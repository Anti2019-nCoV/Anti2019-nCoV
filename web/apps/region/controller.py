# _*_coding:utf-8_*_
"""
@ProjectName: resourceOrder
@Author:  Javen Yan
@File: controller.py
@Software: PyCharm
@Time :    2020/2/6 下午12:45
"""
from web.apps.base.controller import BaseRequestHandler,ABC
from web.apps.region.libs import get_area


class RegionHandler(BaseRequestHandler,ABC):

    async def get(self):
        response = dict()
        parent_code = self.get_argument('parent', None)
        region_code = self.get_argument('regionCode', None)
        result = await get_area(self, parent_code, region_code)
        response['code'] = result['code']
        response['message'] = result['msg']
        if result['status']:
            response['data'] = result['data']
        return self.write_json(response)