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
from web.apps.user.libs.employee import get_user, add_user, update_user, check_user_admin
from web.apps.user.libs.enterprise import get_company, add_company, update_company
from web.apps.user.libs.checkedin import check_in, get_check_in_records, get_statistics_checked,\
    get_statistics_unchecked, get_statistics_total


class CompanyHandler(BaseRequestHandler, ABC):
    """企业"""
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

    async def put(self):
        response = dict()
        enterprise_id = self.get_argument('enterpriseId', None)
        payload = self.get_payload()
        result = await update_company(self, enterprise_id, **payload)
        response['code'] = result['code']
        response['msg'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)


class UserHandler(BaseRequestHandler, ABC):
    """员工"""
    middleware_list = ['web.middleware.middleware.WxMiddleware']

    async def get(self):
        response = dict(code=StatusCode.success.value)
        page = int(self.get_argument('page', '1'))
        page_size = int(self.get_argument('page_size', '10'))
        enterprise_id = self.get_argument('enterpriseId', None)
        result = await get_user(self, page, page_size, enterprise_id)
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

    async def put(self):
        response = dict()
        enterprise_id = self.get_argument('enterpriseId', None)
        user_id = self.get_argument('userId', None)
        payload = self.get_payload()
        result = await update_user(self, enterprise_id, user_id, **payload)
        response['code'] = result['code']
        response['msg'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)


class UserAdminHandler(BaseRequestHandler, ABC):
    """判断是否企业联系人"""
    middleware_list = ['web.middleware.middleware.WxMiddleware']

    async def get(self):
        response = dict(code=StatusCode.success.value)
        result = await check_user_admin(self)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)


class UserCheckInHandler(BaseRequestHandler, ABC):
    """签到"""
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
        page = int(self.get_argument('page', '1'))
        page_size = int(self.get_argument('page_size', '10'))
        result = await get_check_in_records(self, page=page, page_size=page_size)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)


class StatisticsCheckInHandler(BaseRequestHandler, ABC):

    middleware_list = ['web.middleware.middleware.WxMiddleware']

    async def get(self):
        response = dict()
        enterprise_id = self.get_argument('enterpriseId', None)
        result = await get_statistics_checked(self, enterprise_id=enterprise_id)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)


class StatisticsUncheckInHandler(BaseRequestHandler, ABC):

    middleware_list = ['web.middleware.middleware.WxMiddleware']

    async def get(self):
        response = dict()
        enterprise_id = self.get_argument('enterpriseId', None)
        page = int(self.get_argument('page', '1'))
        page_size = int(self.get_argument('page_size', '10'))
        result = await get_statistics_unchecked(self, page=page, page_size=page_size, enterprise_id=enterprise_id)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)


class StatisticsTotalHandler(BaseRequestHandler, ABC):

    middleware_list = ['web.middleware.middleware.WxMiddleware']

    async def get(self):
        response = dict()
        enterprise_id = self.get_argument('enterpriseId', None)
        result = await get_statistics_total(self, enterprise_id=enterprise_id)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)
