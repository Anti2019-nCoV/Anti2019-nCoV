# _*_coding:utf-8_*_
"""
@ProjectName: resourceOrder
@Author:  Javen Yan
@File: libs.py
@Software: PyCharm
@Time :    2020/2/6 下午12:47
"""

from web.models.databases import Areas
from web.utils.date2json import to_json
from web.apps.base.status import StatusCode


async def get_area(self, parent_code, region_code):
    results = []
    rows = Areas.filter(parent_code, region_code)
    if rows:
        results = to_json(rows)
    return {'status': True, 'msg': "获取成功", "data": results, "code": StatusCode.success.value}