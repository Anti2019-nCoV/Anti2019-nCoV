# _*_coding:utf-8_*_
"""
@ProjectName: Anti2019-nCoV
@Author:  Javen Yan
@File: urls.py
@Software: PyCharm
@Time :    2020/1/28 下午1:59
"""
from web.apps.position.controller import PositionHandler

urlpatterns = [
    (r'', PositionHandler)
]
