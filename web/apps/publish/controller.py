# _*_coding:utf-8_*_
"""
@ProjectName: AntiSARI
@Author:  Javen Yan
@File: controller.py
@Software: PyCharm
@Time :    2020/2/2 上午9:52
"""

from web.apps.base.controller import BaseRequestHandler, ABC
from web.apps.publish.libs.publish_libs import add_publish, del_publish, get_publish, update_publish


class EpidemicPublishHandler(BaseRequestHandler, ABC):

    async def get(self):
        city = self.get_argument('city', None)
        classes = self.get_argument('classes', '1')
        response = dict()
        result = await get_publish(self, city, classes=classes)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)

    async def post(self):
        payload = self.get_payload()
        response = dict()
        result = await add_publish(self, **payload)
        response['code'] = result['code']
        response['message'] = result['msg']
        return self.write_json(response)

    async def put(self):
        payload = self.get_payload()
        response = dict()
        result = await update_publish(self, **payload)
        response['code'] = result['code']
        response['message'] = result['msg']
        return self.write_json(response)

    async def delete(self):
        kid = self.get_argument('id')
        response = dict()
        result = await del_publish(self, kid)
        response['code'] = result['code']
        response['message'] = result['msg']
        return self.write_json(response)
