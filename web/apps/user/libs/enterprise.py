#!/usr/bin/python
# @Time  : 2/1/20
# @Author: liyong
from logzero import logger
from web.models.databases import User, Company, CompanyUser, RoleTypeEnum
from web.apps.base.status import StatusCode
from web.utils.date2json import to_json
from web.apps.user.libs.utils import save_pic, check_user_exist
from web.apps.user.libs.response import auth_failed, permission_deny, validate_error, param_missing, openid_null


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
        company_user = CompanyUser.by_company_user_id(user.id, enterprise_id)
        if not company_user:    # 该企业下的所有用户均可查看
            return permission_deny()
        rows = Company.by_id(enterprise_id)
        rows = [rows] if rows else []

    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": to_json(rows)}


async def add_company(self, **kwargs):
    """企业注册"""
    keys = ['companyName', 'companyAddr', 'userName', 'userPhone']
    val = validate_error(keys, **kwargs)
    if not val.get('status'):
        return val
    if not self.openid:
        return openid_null()
    try:
        company = Company.by_name(kwargs.get('companyName'))
        if company:
            return {'status': False, 'msg': '该企业已注册', "code": StatusCode.exist_error.value}
        user = self.current_user
        query = check_user_exist(user)
        if not query.get('status'):
            return query
        user_flag = False
        if not query.get('existed'):    # 如果当前用户不存在，则注册用户时需要记录openid
            name = kwargs.get('userName').strip()
            phone = kwargs.get('userPhone').strip()
            user = User.by_name_phone(name, phone)
            if not user:
                user_flag = True
                user = User.add(
                    userName=name,
                    userPhone=phone,
                    openid=self.openid,
                    is_admin=True
                )
        company = Company.add(
            companyName=kwargs.get('companyName').strip(),
            companyAddr=kwargs.get('companyAddr').strip()
        )
        logo_pic = kwargs.get('logoPic')
        if logo_pic:
            logo_pic = await save_pic(logo_pic.strip(), 'logo', f'logo_{company.id}')
            if not logo_pic:
                if user_flag:
                    user.delete(user.id)
                company.delete(company.id)
                return {'status': False, 'msg': 'logo保存失败，请重试', "code": StatusCode.file_save_error.value}
            company.update(company.id, logoPic=logo_pic)
        company_user = CompanyUser.by_company_user_id(user.id, company.id)
        if not company_user:
            CompanyUser.add(
                company_id=company.id, user_id=user.id, role_type=RoleTypeEnum.admin_rw
            )
        return {'status': True, 'msg': '注册成功', "code": StatusCode.success.value,
                "data": {"enterpriseId": company.id, "logoPic": company.logoPic}}
    except Exception as e:
        logger.error(f"add Company In Error: {str(e)}")
        self.db.rollback()
        return {'status': False, 'msg': '注册失败', "code": StatusCode.db_error.value}


async def update_company(self, enterprise_id=None, **kwargs):
    """编辑企业信息"""
    user = self.current_user
    if not user:
        return auth_failed()
    if not enterprise_id:
        return param_missing('enterpriseId')
    company_user = CompanyUser.by_company_user_id(user.id, enterprise_id)
    if not company_user or company_user.role_type != RoleTypeEnum.admin_rw:  # 该企业下的所有用户均可查看
        return permission_deny()
    try:
        keys = ['id', 'user', 'createTime', 'updateTime']
        for key in keys:
            kwargs.pop(key)  # 排除这些key
        company = Company.update(enterprise_id, **kwargs)
        return {'status': True, 'msg': '更新企业成功', "code": StatusCode.success.value,
                "data": {"enterpriseId": company.id, "logoPic": company.logoPic}}
    except Exception as e:
        logger.error(f"update company In Error: {str(e)}")
        self.db.rollback()
        return {'status': False, 'msg': '更新企业失败', "code": StatusCode.db_error.value}
