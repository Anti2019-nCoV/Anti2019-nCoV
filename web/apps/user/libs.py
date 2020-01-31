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


async def get_user(self, page=1, page_size=10, enterprise_id=None, user_id=None):
    if user_id:
        rows = User.by_id(user_id)
        rows = [rows] if rows else []
    elif enterprise_id:
        rows = User.by_enterprise_id(enterprise_id, page=page, page_size=page_size)     # 查询该企业下的所有用户
    else:
        rows = User.paginate(page=page, page_size=page_size)
    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": to_json(rows)}


async def get_company(self, page=1, page_size=10, enterprise_id=None):
    if enterprise_id:
        rows = Company.by_id(enterprise_id)
        rows = [rows] if rows else []
    else:
        rows = Company.paginate(page=page, page_size=page_size)
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
    state, msg = validate(keys, kwargs)
    if not state:
        return {'status': False, 'msg': '数据入参验证失败', "code": StatusCode.params_error.value}
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
                avatar_pic = await save_pic(avatar_pic.strip(), 'avatar', f'avatar_{self.openid}')
                if not avatar_pic:
                    return {'status': False, 'msg': '头像保存失败，请重试', "code": StatusCode.file_save_error.value}
            user = User.add(
                userName=kwargs.get('userName').strip(),
                employeeId=employee_id,
                userPhone=kwargs.get('userPhone').strip(),
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
    state, msg = validate(keys, kwargs)
    if not state:
        return {'status': False, 'msg': '数据入参验证失败', "code": StatusCode.params_error.value}
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
                userName=kwargs.get('userName').strip(),
                userPhone=kwargs.get('userPhone').strip(),
                openid=self.openid
            )
        company = Company.add(
            companyName=kwargs.get('companyName').strip(),
            companyAddr=kwargs.get('companyAddr').strip()
        )
        logo_pic = kwargs.get('logoPic')
        if logo_pic:
            logo_pic = await save_pic(logo_pic.strip(), 'logo', f'logo_{company.id}')
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
    state, msg = validate(keys, kwargs)
    if not state:
        return {'status': False, 'msg': '数据入参验证失败', "code": StatusCode.params_error.value}
    user_info = self.current_user
    if not user_info:
        return {'status': False, 'msg': '您需要先登录才能签到', "code": UserCenterStatusCode.access_error.value}
    try:
        CheckInRecordModel.add(
            userId=user_info.id,
            province=kwargs.get('province'),
            city=kwargs.get('city'),
            address=kwargs.get('address'),
            latitude=kwargs.get('latitude'),
            longitude=kwargs.get('longitude'),
            status=kwargs.get('status')
        )
        User.update(user_info.id, {
            'checkedTime': datetime.now(),
            'checkedAddr': kwargs.get('province'),
            'checkedStatus': kwargs.get('status')
        })  # 更新用户表的签到状态
        return {'status': True, 'msg': '签到成功', "code": StatusCode.success.value}
    except Exception as e:
        logger.error(f"Check In Error: {str(e)}")
        self.db.rollback()
        return {'status': False, 'msg': '签到失败', "code": StatusCode.db_error.value}


async def get_check_in_records(self, page=1, page_size=10, userId=None):
    if userId:
        rows = CheckInRecordModel.by_user_id(userId, page, page_size)
    else:
        rows = CheckInRecordModel.paginate(page, page_size)
    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": to_json(rows)}


def get_length(generator):
    """获取迭代器长度"""
    if hasattr(generator, "__len__"):
        return len(generator)
    else:
        return sum(1 for _ in generator)


async def get_statistics_checked(self,  page=1, page_size=10, enterprise_id=None):
    """统计签到数据"""
    if enterprise_id:
        users = User.by_enterprise_id(enterprise_id)    # 根据企业搜索用户
    else:
        users = User.all()
    checked_data = []
    for user in users:
        checked_models = User.by_id_checked_today(user.id)
        if checked_models:
            checked_data.extend(to_json([checked_models]))
    checked_data.sort(key=itemgetter('checkedAddr'))   # 按省排序
    checked = []
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


async def get_statistics_unchecked(self, enterprise_id=None):
    """统计未签到数据"""
    if enterprise_id:
        users = User.by_enterprise_id(enterprise_id)    # 根据企业搜索用户
    else:
        users = User.all()
    logger.debug(f'unchecked users: {users} count: {len(users)}')
    unchecked_data = []
    for user in users:
        unchecked_models = User.by_id_unchecked_today(user.id)
        if unchecked_models:
            logger.debug(f'unchecked_models userid: {user.id}')
            unchecked_data.extend(to_json([unchecked_models]))

    unchecked = []
    for uncheck_ in unchecked_data:
        unchecked.append({
            'userName': uncheck_.get('userName'),
            'employeeId': uncheck_.get('employeeId'),
            'userPhone': uncheck_.get('userPhone')
        })

    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": unchecked}

