# _*_coding:utf-8_*_
"""
@ProjectName: Anti2019-nCoV
@Author:  liyong
@File: controller.py
@Software: PyCharm
@Time :    2020/1/28 下午11:50
"""
from abc import ABC
from web.apps.base.controller import BaseRequestHandler
from web.apps.base.status import StatusCode
from web.apps.user.libs import get_user, get_company, add_user, add_company, check_in, get_check_in_records


class CompanyHandler(BaseRequestHandler, ABC):

    middleware_list = ['web.middleware.middleware.WxMiddleware']

    async def get(self):
        response = dict(code=StatusCode.success.value)
        enterprise_id = self.get_argument('enterpriseId', None)
        result = await get_company(self, enterprise_id)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)

    async def post(self):
        response = dict()
        payload = self.get_payload()
        result = await add_company(self, **payload)
        response['code'] = result['code']
        response['msg'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)


class UserHandler(BaseRequestHandler, ABC):

    middleware_list = ['web.middleware.middleware.WxMiddleware']

    async def get(self):
        response = dict(code=StatusCode.success.value)
        enterprise_id = self.get_argument('enterpriseId', None)
        user_id = self.get_argument('userId', None)
        result = await get_user(self, enterprise_id, user_id)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)

    async def post(self):
        response = dict()
        payload = self.get_payload()
        result = await add_user(self, **payload)
        response['code'] = result['code']
        response['msg'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)


class UserCheckInHandler(BaseRequestHandler, ABC):

    middleware_list = ['web.middleware.middleware.WxMiddleware']

    async def post(self):
        response = dict()
        payload = self.get_payload()
        result = await check_in(self, **payload)
        response['code'] = result['code']
        response['msg'] = result['msg']
        return self.write_json(response)

    async def get(self):
        response = dict()
        _id = self.get_argument('userId', None)
        page = int(self.get_argument('page', '1'))
        page_size = int(self.get_argument('page_size', '10'))
        if _id:
            result = await get_check_in_records(self, page=page, page_size=page_size, userId=_id)
        else:
            result = await get_check_in_records(self, page=page, page_size=page_size)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)
