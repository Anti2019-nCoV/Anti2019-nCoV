# _*_coding:utf-8_*_
"""
@ProjectName: Anti2019-nCoV
@Author:  liyong
@File: libs.py
@Software: PyCharm
@Time :    2020/1/28 下午11:38
"""
from logzero import logger

from web.models.databases import User, Company, CheckInRecordModel, StatusEnum
from web.models.form_validate import validate
from web.apps.base.status import StatusCode, UserCenterStatusCode
from web.utils.date2json import to_json
from datetime import datetime

from operator import itemgetter
from itertools import groupby


async def get_user(self, enterprise_id=None, user_id=None):
    if user_id:
        rows = [User.by_id(user_id)]
    elif enterprise_id:
        rows = User.by_enterprise_id(enterprise_id)     # 查询该企业下的所有用户
    else:
        rows = User.all()
    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": to_json(rows)}


async def get_company(self, enterprise_id=None):
    if enterprise_id:
        rows = [Company.by_id(enterprise_id)]
    else:
        rows = Company.all()
    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": to_json(rows)}


def check_user_exist(self):
    """判断一个用户是否注册了超过3个企业"""
    if not self.current_user:
        return True, {}
    query = Company.by_user_id(self.current_user.id)
    if len(query) >= 3:
        return False, {'status': False, 'msg': '该用户已注册超过3个企业', "code": StatusCode.exist_error.value}
    return True, {}


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
        passed, query = check_user_exist(self)
        if not passed:
            return query
        employee_id = kwargs.get('employeeId')
        if employee_id:
            employee_id = employee_id.stirp()
        avatar_pic = kwargs.get('avatarPic')
        if avatar_pic:
            avatar_pic = avatar_pic.strip()
        user = User(
            userName=kwargs.get('userName').strip(),
            employeeId=employee_id,
            userPhone=kwargs.get('userPhone').strip(),
            avatarPic=avatar_pic
        )
        company.user += [user]
        self.db.add(user)
        self.db.add(company)
        self.db.commit()
        return {'status': True, 'msg': '注册成功', "code": StatusCode.success.value,
                "data": {"userId": user.id}}
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
        passed, query = check_user_exist(self)
        if not passed:
            return query
        user = User(
            userName=kwargs.get('userName').strip(),
            userPhone=kwargs.get('userPhone').strip(),
            is_admin=True
        )
        company = Company(
            companyName=kwargs.get('companyName').strip(),
            companyAddr=kwargs.get('companyAddr').strip()
        )
        company.user = [user]
        self.db.add(user)
        self.db.add(company)
        self.db.commit()
        return {'status': True, 'msg': '注册成功', "code": StatusCode.success.value,
                "data": {"enterpriseId": company.id}}
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
        ch = CheckInRecordModel(
            userId=user_info.id,
            province=kwargs.get('province'),
            city=kwargs.get('city'),
            address=kwargs.get('address'),
            latitude=kwargs.get('latitude'),
            longitude=kwargs.get('longitude'),
            status=kwargs.get('status')
        )
        self.db.query(User).filter_by(id=user_info.id).update({
            'checkedTime': datetime.now(),
            'checkedAddr': kwargs.get('province'),
            'checkedStatus': kwargs.get('status')
        })      # 更新用户表的签到状态
        self.db.add(ch)
        self.db.commit()
        return {'status': True, 'msg': '签到成功', "code": StatusCode.success.value}
    except Exception as e:
        logger.error(f"Check In Error: {str(e)}")
        self.db.rollback()
        return {'status': False, 'msg': '签到失败', "code": StatusCode.db_error.value}


async def get_check_in_records(self, page=1, page_size=10, userId=None):
    if userId:
        rows = CheckInRecordModel.by_user_id(userId, page, page_size)
    else:
        rows = CheckInRecordModel.paginate(userId, page, page_size)
    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": to_json(rows)}


def get_length(generator):
    if hasattr(generator, "__len__"):
        return len(generator)
    else:
        return sum(1 for _ in generator)


async def get_statistics_checked(self, enterprise_id=None):
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
        print(enterprise_id)
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

