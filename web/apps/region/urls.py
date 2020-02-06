# _*_coding:utf-8_*_
"""
@ProjectName: resourceOrder
@Author:  Javen Yan
@File: urls.py
@Software: PyCharm
@Time :    2020/2/6 下午12:45
"""

from web.apps.region.controller import RegionHandler


urlpatterns = [
    (r'/region', RegionHandler)
]