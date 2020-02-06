# _*_coding:utf-8_*_
"""
@ProjectName: resourceOrder
@Author:  Javen Yan
@File: urls.py
@Software: PyCharm
@Time :    2020/2/6 下午12:08
"""

from web.apps.orders.controller import OrderHandler, OrderVerifyHandler, OrderUserHandler


urlpatterns = [
    (r'', OrderHandler),
    (r'/verify', OrderVerifyHandler),
    (r'/user', OrderUserHandler)
]