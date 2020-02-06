# _*_coding:utf-8_*_
"""
@ProjectName: resourceOrder
@Author:  Javen Yan
@File: controller.py
@Software: PyCharm
@Time :    2020/2/6 下午12:07
"""
from web.apps.base.controller import BaseRequestHandler,ABC
from web.apps.orders.libs.order_lib import get_orders, add_orders, update_status, get_users


class OrderHandler(BaseRequestHandler, ABC):

    async def get(self):
        response = dict()
        residentId = self.get_argument('residentId', None)
        result = await get_orders(self, residentId)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)

    async def post(self):
        response = dict()
        payloads = self.get_payload()
        result = await add_orders(self, payloads)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)


class OrderVerifyHandler(BaseRequestHandler, ABC):

    async def get(self):
        order = self.get_argument('order', None)
        response = dict()
        result = await update_status(self, order)
        response['code'] = result['code']
        response['message'] = result['msg']
        return self.write_json(response)


class OrderUserHandler(BaseRequestHandler, ABC):

    async def get(self):
        user_id = self.get_argument('residentId', None)
        phone = self.get_argument('phone', None)
        response = dict()
        result = await get_users(self, user_id, phone)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)
