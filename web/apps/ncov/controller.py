# _*_coding:utf-8_*_
"""
@ProjectName: Anti2019-nCoV
@Author:  Javen Yan
@File: controller.py
@Software: PyCharm
@Time :    2019/12/5 上午11:50
"""
from abc import ABC
from web.apps.base.controller import BaseRequestHandler
from web.apps.base.status import StatusCode
from web.apps.ncov.libs import records, news, overalls, rumors, oversea


class NonCoVHandler(BaseRequestHandler, ABC):

    async def get(self):
        response = dict(code=StatusCode.success.value)
        province = self.get_argument('province', None)
        latest = int(self.get_argument('latest', '1'))
        result = await records(self, latest, province)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)


class NonCoVOverSeaHandler(BaseRequestHandler, ABC):

    async def get(self):
        response = dict(code=StatusCode.success.value)
        result = await oversea(self)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)


class NonCoVNewsHandler(BaseRequestHandler, ABC):

    async def get(self):
        response = dict()
        page_size = int(self.get_argument('page_size', '10'))
        position = self.get_argument('province', None)
        result = await news(self, page_size, position)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)


class NonCoVOverallHandler(BaseRequestHandler, ABC):

    async def get(self):
        response = dict()
        num = int(self.get_argument('num', '1'))
        result = await overalls(self, num)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)


class NonCoVSariRumorsHandler(BaseRequestHandler, ABC):

    async def get(self):
        response = dict()
        num = self.get_argument('num', '10')
        rumorType = self.get_argument('rumorType', '0')
        result = await rumors(self, num, rumorType)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)
