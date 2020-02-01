# _*_coding:utf-8_*_
"""
@ProjectName: Anti2019-nCoV
@Author:  liyong
@File: libs.py
@Software: PyCharm
@Time :    2020/1/28 下午11:38
"""
from logzero import logger

from web.models.databases import User, Company, CompanyUser, CheckInRecordModel, StatusEnum
from web.models.form_validate import validate
from web.apps.base.status import StatusCode, UserCenterStatusCode
from web.utils.date2json import to_json
from web.utils.save_file import save_pic
from datetime import datetime

from operator import itemgetter
from itertools import groupby


def permission_deny():
    """无权访问"""
    return {"status": False, "code": UserCenterStatusCode.access_error.value, "msg": "您无权访问"}


def auth_failed():
    """根据openid判断用户是否存在，从而当作登录校验"""
    return {'status': False, 'msg': '您需要先登录才能签到', "code": UserCenterStatusCode.access_error.value}


def validate_error(keys, **kwargs):
    """校验不合法"""
    state, msg = validate(keys, kwargs)
    if not state:
        return {'status': False, 'msg': '数据入参验证失败', "code": StatusCode.params_error.value}
    return {'status': True, 'msg': msg, "code": StatusCode.success.value}


async def get_user(self, page=1, page_size=10, enterprise_id=None):
    """查询用户"""
    user = self.current_user
    if not user:
        return auth_failed()
    if not enterprise_id:
        rows = user
        rows = [rows] if rows else []
    else:
        role = CompanyUser.by_company_user_id(user.id, enterprise_id)
        if not role or not role.is_admin:
            return permission_deny()
        rows = User.by_enterprise_id(enterprise_id, page=page, page_size=page_size)     # 查询该企业下的所有用户
    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": to_json(rows)}


async def get_company(self, enterprise_id):
    """查询企业"""
    user = self.current_user
    if not user:
        return auth_failed()
    if not enterprise_id:
        rows = Company.by_user_id(user.id)
        if not rows:
            return permission_deny()
    else:
        role = CompanyUser.by_company_user_id(user.id, enterprise_id)
        if not role:
            return permission_deny()
        rows = Company.by_id(enterprise_id)
        rows = [rows] if rows else []

    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": to_json(rows)}


def check_user_exist(user):
    """判断一个用户是否注册了超过3个企业"""
    if not user:
        return {'status': True, 'existed': False}
    query = CompanyUser.by_user_id(user.id)
    if len(query) >= 3:
        return {'status': False, 'msg': '该用户已注册超过3个企业', "code": StatusCode.exist_error.value}
    return {'status': True, 'existed': True}


async def add_user(self, **kwargs):
    """员工注册"""
    keys = ['userName', 'userPhone', 'enterpriseId']
    val = validate_error(keys, **kwargs)
    if not val.get('status'):
        return val
    try:
        company = Company.by_id(kwargs.get('enterpriseId'))
        if not company:
            return {'status': False, 'msg': '该企业不存在', "code": StatusCode.not_found_error.value}
        user = self.current_user
        query = check_user_exist(user)
        if not query.get('status'):
            return query
        if not query.get('existed'):    # 如果当前用户不存在，则注册用户时需要记录openid
            employee_id = kwargs.get('employeeId')
            if employee_id:
                employee_id = employee_id.stirp()
            avatar_pic = kwargs.get('avatarPic')
            if avatar_pic:
                avatar_pic = await save_pic(avatar_pic, 'avatar', f'avatar_{self.openid}')
                if not avatar_pic:
                    return {'status': False, 'msg': '头像保存失败，请重试', "code": StatusCode.file_save_error.value}
            user = User.add(
                userName=kwargs.get('userName'),
                employeeId=employee_id,
                userPhone=kwargs.get('userPhone'),
                avatarPic=avatar_pic,
                openid=self.openid
            )
        company_user = CompanyUser.by_company_user_id(user.id, company.id)
        if company_user:
            return {'status': False, 'msg': '该用户已注册当前企业', "code": StatusCode.exist_error.value}
        else:
            CompanyUser.add(company_id=company.id, user_id=user.id)
        return {'status': True, 'msg': '注册成功', "code": StatusCode.success.value,
                "data": {"userId": user.id, "avatarPic": user.avatarPic}}
    except Exception as e:
        logger.error(f"add user In Error: {str(e)}")
        self.db.rollback()
        return {'status': False, 'msg': '注册失败', "code": StatusCode.db_error.value}


async def add_company(self, **kwargs):
    """企业注册"""
    keys = ['companyName', 'companyAddr', 'userName', 'userPhone']
    val = validate_error(keys, **kwargs)
    if not val.get('status'):
        return val
    try:
        company = Company.by_name(kwargs.get('companyName'))
        if company:
            return {'status': False, 'msg': '该企业已注册', "code": StatusCode.exist_error.value}
        user = self.current_user
        query = check_user_exist(user)
        if not query.get('status'):
            return query
        if not query.get('existed'):    # 如果当前用户不存在，则注册用户时需要记录openid
            user = User.add(
                userName=kwargs.get('userName'),
                userPhone=kwargs.get('userPhone'),
                openid=self.openid
            )
        company = Company.add(
            companyName=kwargs.get('companyName'),
            companyAddr=kwargs.get('companyAddr')
        )
        logo_pic = kwargs.get('logoPic')
        if logo_pic:
            logo_pic = await save_pic(logo_pic, 'logo', f'logo_{company.id}')
            if not logo_pic:
                if not query.get('existed'):
                    user.delete(user.id)
                company.delete(company.id)
                return {'status': False, 'msg': 'logo保存失败，请重试', "code": StatusCode.file_save_error.value}
            company.update(company.id, {'logoPic': logo_pic})
        company_user = CompanyUser.by_company_user_id(user.id, company.id)
        if company_user:
            return {'status': False, 'msg': '该用户已注册当前企业', "code": StatusCode.exist_error.value}
        else:
            CompanyUser.add(
                company_id=company.id, user_id=user.id, is_admin=True, is_contacts=True
            )
        return {'status': True, 'msg': '注册成功', "code": StatusCode.success.value,
                "data": {"enterpriseId": company.id, "logoPic": company.logoPic}}
    except Exception as e:
        logger.error(f"add Company In Error: {str(e)}")
        self.db.rollback()
        return {'status': False, 'msg': '注册失败', "code": StatusCode.db_error.value}


async def check_in(self, **kwargs):
    """员工签到"""
    keys = ['province', 'city', 'address', 'latitude', 'longitude', 'status']
    val = validate_error(keys, **kwargs)
    if not val.get('status'):
        return val
    user = self.current_user
    if not user:
        return auth_failed()
    try:
        CheckInRecordModel.add(
            userId=user.id,
            province=kwargs.get('province'),
            city=kwargs.get('city'),
            address=kwargs.get('address'),
            latitude=kwargs.get('latitude'),
            longitude=kwargs.get('longitude'),
            status=kwargs.get('status')
        )
        User.update(user.id, {
            'checkedTime': datetime.now(),
            'checkedAddr': kwargs.get('province'),
            'checkedStatus': kwargs.get('status')
        })  # 更新用户表的签到状态
        return {'status': True, 'msg': '签到成功', "code": StatusCode.success.value}
    except Exception as e:
        logger.error(f"Check In Error: {str(e)}")
        self.db.rollback()
        return {'status': False, 'msg': '签到失败', "code": StatusCode.db_error.value}


async def get_check_in_records(self, page=1, page_size=10):
    """查询个人签到轨迹"""
    user = self.current_user
    if not user:
        return auth_failed()
    rows = CheckInRecordModel.by_user_id(user.id, page, page_size)

    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": to_json(rows)}


def get_length(generator):
    """获取迭代器长度"""
    if hasattr(generator, "__len__"):
        return len(generator)
    else:
        return sum(1 for _ in generator)


async def get_statistics_checked(self,  page=1, page_size=10, enterprise_id=None):
    """统计签到数据"""
    if not enterprise_id:
        return permission_deny()
    checked = []
    checked_data = to_json(User.by_enterprise_id_checked_today(enterprise_id))    # 根据企业搜索用户
    if not checked_data:
        return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": checked}

    checked_data.sort(key=itemgetter('checkedAddr'))  # 按省排序
    for checked_address, items in groupby(checked_data, key=itemgetter('checkedAddr')):   # 按省分割
        isolated_count = 0
        suspected_count = 0
        confirmed_count = 0
        items = list(items)
        items.sort(key=itemgetter('checkedStatus'))  # 按健康状态分割
        logger.debug(f'items sort by {checked_address}: {items}')
        for status, sub_items in groupby(items, key=itemgetter('checkedStatus')):
            length = get_length(sub_items)
            if status == StatusEnum.isolated:
                isolated_count = length
            elif status == StatusEnum.suspected:
                suspected_count = length
            elif status == StatusEnum.confirmed:
                confirmed_count = length

        checked_count = get_length(items)  # 打卡数量
        checked.append({
            'checked_address': checked_address, 'checked_count': checked_count, 'isolated_count': isolated_count,
            'suspected_count': suspected_count, 'confirmed_count': confirmed_count
        })

    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": checked}


async def get_statistics_unchecked(self, page=1, page_size=10,  enterprise_id=None):
    """统计未签到数据"""
    user = self.current_user
    if not user:
        return auth_failed()
    if not enterprise_id:
        return permission_deny()
    role = CompanyUser.by_company_user_id(user.id, enterprise_id)
    if not role or not role.is_admin:
        return permission_deny()

    unchecked_data = User.by_enterprise_id_unchecked_today(enterprise_id, page, page_size)    # 根据企业搜索用户

    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": to_json(unchecked_data)}


async def get_statistics_total(self, enterprise_id=None):
    """统计该企业所有用户个数"""
    if not enterprise_id:
        return permission_deny()

    total_count = CompanyUser.count_by_company_id(enterprise_id)

    checked_data = User.by_enterprise_id_checked_today(enterprise_id)  # 根据企业搜索用户
    checked_count = len(checked_data)
    isolated_count = User.count_status_checked_today(enterprise_id, StatusEnum.isolated)
    suspected_count = User.count_status_checked_today(enterprise_id, StatusEnum.suspected)
    confirmed_count = User.count_status_checked_today(enterprise_id, StatusEnum.confirmed)

    reuslt = {
        'total_count': total_count,
        'checked_count': checked_count,
        'unchecked_count': total_count - checked_count,
        'isolated_count': isolated_count,
        'suspected_count': suspected_count,
        'confirmed_count': confirmed_count
    }

    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": reuslt}
