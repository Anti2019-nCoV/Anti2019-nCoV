# _*_coding:utf-8_*_
"""
@ProjectName: Anti2019-nCoV
@Author:  liyong
@File: urls.py
@Software: PyCharm
@Time :    2020/1/28 下午11:58
"""
from web.apps.user.controller import CompanyHandler, UserHandler, UserCheckInHandler, StatisticsCheckInHandler

urlpatterns = [
    (r'/enterprise', CompanyHandler),
    (r'/checkIn', UserCheckInHandler),
    (r'/employee', UserHandler),
    (r'/statistics', StatisticsCheckInHandler),
]
