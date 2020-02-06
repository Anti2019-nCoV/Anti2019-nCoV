# _*_coding:utf-8_*_
"""
@ProjectName: resourceOrder
@Author:  Javen Yan
@File: controller.py
@Software: PyCharm
@Time :    2020/2/6 下午2:06
"""
from web.apps.base.controller import BaseRequestHandler, ABC
from web.apps.product.libs import get_product, add_product, delete_product, update_product


class ProductsHandler(BaseRequestHandler, ABC):

    async def get(self):
        response = dict()
        _type = self.get_argument('type', None)
        result = await get_product(self, _type)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)

    async def post(self):
        response = dict()
        payloads = self.get_payload()
        result = await add_product(self, payloads)
        response['code'] = result['code']
        response['message'] = result['msg']
        return self.write_json(response)

    async def put(self):
        response = dict()
        payloads = self.get_payload()
        result = await update_product(self, payloads)
        response['code'] = result['code']
        response['message'] = result['msg']
        return self.write_json(response)

    async def delete(self):
        response = dict()
        _id = self.get_argument('id')
        result = await delete_product(self, _id)
        response['code'] = result['code']
        response['message'] = result['msg']
        return self.write_json(response)
