#!/usr/bin/python
# @Time  : 2/1/20
# @Author: liyong
from web.models.form_validate import validate
from web.apps.base.status import StatusCode, UserCenterStatusCode


def permission_deny():
    """无权访问"""
    return {"status": False, "msg": "对不起，您无权访问", "code": UserCenterStatusCode.access_error.value}


def auth_failed():
    """根据openid判断用户是否存在，从而当作登录校验"""
    return {'status': False, 'msg': '您需要先完成登录认证', "code": UserCenterStatusCode.access_error.value}


def validate_error(keys, **kwargs):
    """校验不合法"""
    state, msg = validate(keys, kwargs)
    if not state:
        return {'status': False, 'msg': '数据入参验证失败', "code": StatusCode.params_error.value}
    return {'status': True, 'msg': msg, "code": StatusCode.success.value}


def param_missing(args):
    return {'status': False, 'msg': f'数据入参不完整，缺少{args}', "code": UserCenterStatusCode.miss_params_error.value}


def openid_null():
    return {'status': False, 'msg': f"'openid'为空，无法注册", "code": UserCenterStatusCode.miss_params_error.value}


def not_found():
    return {'status': False, 'msg': f"当前资源不存在", "code": UserCenterStatusCode.not_found_error.value}
