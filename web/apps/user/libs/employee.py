#!/usr/bin/python
# @Time  : 2/1/20
# @Author: liyong
from logzero import logger
from web.models.databases import User, Company, CompanyUser, RoleTypeEnum
from web.apps.base.status import StatusCode
from web.utils.date2json import to_json
from web.apps.user.libs.utils import save_pic, check_user_exist
from web.apps.user.libs.response import auth_failed, permission_deny, validate_error, param_missing, openid_null


async def get_user(self, page=1, page_size=10, enterprise_id=None):
    """查询用户"""
    user = self.current_user
    if not user:
        return auth_failed()
    if not enterprise_id:
        rows = user
        rows = [rows] if rows else []
    else:
        company_user = CompanyUser.by_company_user_id(user.id, enterprise_id)
        if not company_user or company_user.role_type == RoleTypeEnum.member:   # 该企业下的管理员可查看
            return permission_deny()
        rows = User.by_enterprise_id(enterprise_id, page=page, page_size=page_size)     # 查询该企业下的所有用户
    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": to_json(rows)}


async def check_user_admin(self):
    """查询用户是否是企业联系人"""
    user = self.current_user
    if not user:
        return auth_failed()

    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": {'is_admin': user.is_admin}}


async def add_user(self, **kwargs):
    """员工注册"""
    keys = ['userName', 'userPhone', 'enterpriseId']
    val = validate_error(keys, **kwargs)
    if not val.get('status'):
        return val
    if not self.openid:
        return openid_null()
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
                employee_id = employee_id.strip()
            avatar_pic = kwargs.get('avatarPic')
            if avatar_pic:
                avatar_pic = await save_pic(avatar_pic.strip(), 'avatar', f'avatar_{self.openid}')
                if not avatar_pic:
                    return {'status': False, 'msg': '头像保存失败，请重试', "code": StatusCode.file_save_error.value}
            name = kwargs.get('userName').strip()
            phone = kwargs.get('userPhone').strip()
            user = User.by_name_phone(name, phone)
            if not user:
                user = User.add(
                    userName=name,
                    employeeId=employee_id,
                    userPhone=phone,
                    avatarPic=avatar_pic,
                    openid=self.openid
                )
        company_user = CompanyUser.by_company_user_id(user.id, company.id)
        if not company_user:
            CompanyUser.add(company_id=company.id, user_id=user.id)
        return {'status': True, 'msg': '注册成功', "code": StatusCode.success.value,
                "data": {"userId": user.id, "avatarPic": user.avatarPic, 'openid': user.openid}}
    except Exception as e:
        logger.error(f"add user In Error: {str(e)}")
        self.db.rollback()
        return {'status': False, 'msg': '注册失败', "code": StatusCode.db_error.value}


async def update_user(self, enterprise_id=None, user_id=None, **kwargs):
    """编辑用户信息"""
    user = self.current_user
    if not user:
        return auth_failed()
    if not enterprise_id:
        return param_missing('enterpriseId')
    company_user = CompanyUser.by_company_user_id(user.id, enterprise_id)
    if not company_user or company_user.role_type != RoleTypeEnum.admin_rw:  # 该企业下的所有用户均可查看
        return permission_deny()
    userid = user.id
    if user_id:
        company_user = CompanyUser.by_company_user_id(user_id, enterprise_id)
        if not company_user:        # 判断该用户是否属于该企业
            return permission_deny()
        userid = user_id
    try:
        keys = ['id', 'openid', 'is_admin', 'company', 'createTime', 'updateTime']
        for key in keys:
            kwargs.pop(key)     # 排除这些key
        name = kwargs.get('userName').strip()
        phone = kwargs.get('userPhone').strip()
        instance = User.by_name_phone(name, phone)
        if instance.id != userid:
            return {'status': False, 'msg': '当前姓名和手机号已占用', "code": StatusCode.exist_error.value}
        user = User.update(userid, **kwargs)
        return {'status': True, 'msg': '更新用户成功', "code": StatusCode.success.value,
                "data": {"userId": user.id, "avatarPic": user.avatarPic, 'openid': user.openid}}
    except Exception as e:
        logger.error(f"update user In Error: {str(e)}")
        self.db.rollback()
        return {'status': False, 'msg': '更新用户失败', "code": StatusCode.db_error.value}
