# _*_coding:utf-8_*_
"""
@ProjectName: AntiSARI
@Author:  Javen Yan
@File: auth_controller.py
@Software: PyCharm
@Time :    2020/1/29 下午9:45
"""
from abc import ABC
from web.apps.base.controller import BaseRequestHandler
from web.apps.base.status import StatusCode
from web.apps.gateway.libs.auth_lib import code2token, get_user_info


class Code2AccessTokenHandler(BaseRequestHandler, ABC):

    async def get(self):
        response = dict()
        code = self.get_argument('code', None)
        if not code:
            response['code'] = StatusCode.miss_params_error.value
            response['message'] = "Code参数缺失"
            return self.write_json(response)
        result = await code2token(self, code)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)


class GetUserInfo(BaseRequestHandler, ABC):

    async def get(self):
        response = dict()
        access_token = self.request.headers.get('access_token', None)
        open_id = self.request.headers.get('openid', None)
        if not access_token:
            response['code'] = StatusCode.miss_params_error.value
            response['message'] = "access_token参数缺失"
            return self.write_json(response)
        if not open_id:
            response['code'] = StatusCode.miss_params_error.value
            response['message'] = "open_id参数缺失"
            return self.write_json(response)
        result = await get_user_info(self, access_token, open_id)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)