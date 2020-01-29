# _*_coding:utf-8_*_
"""
@ProjectName: Anti2019-nCoV
@Author:  liyong
@File: libs.py
@Software: PyCharm
@Time :    2020/1/28 下午11:38
"""
from logzero import logger

from web.models.databases import User, Company, CheckInRecordModel
from web.models.form_validate import validate
from web.apps.base.status import StatusCode, UserCenterStatusCode
from web.utils.date2json import to_json
from datetime import datetime


async def get_user(self, enterprise_id, user_id=None):
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
        user = User(
            userName=kwargs.get('userName').strip(),
            employeeId=employee_id,
            userPhone=kwargs.get('userPhone').strip(),
            createTime=datetime.now()
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
            is_admin=True,
            createTime=datetime.now()
        )
        company = Company(
            companyName=kwargs.get('companyName').strip(),
            companyAddr=kwargs.get('companyAddr').strip(),
            createTime=datetime.now()
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
    keys = ['province', 'city', 'address', 'latitude', 'longitude', 'status']
    state, msg = validate(keys, kwargs)
    if not state:
        return {'status': False, 'msg': '数据入参验证失败', "code": StatusCode.params_error.value}
    user = self.current_user
    if not user:
        return {'status': False, 'msg': '您需要先登录才能签到', "code": UserCenterStatusCode.access_error.value}
    try:
        ch = CheckInRecordModel(
            userId=user.id,
            province=kwargs.get('province'),
            city=kwargs.get('city'),
            address=kwargs.get('address'),
            latitude=kwargs.get('latitude'),
            longitude=kwargs.get('longitude'),
            status=kwargs.get('status')
        )
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
