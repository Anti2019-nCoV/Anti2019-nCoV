# _*_coding:utf-8_*_
"""
@ProjectName: Anti2019-nCoV
@Author:  liyong
@File: urls.py
@Software: PyCharm
@Time :    2020/1/28 下午11:58
"""
from web.apps.user import controller

urlpatterns = [
    (r'/enterprise', controller.CompanyHandler),
    (r'/checkIn', controller.UserCheckInHandler),
    (r'/employee', controller.UserHandler),
    (r'/statistics/checked', controller.StatisticsCheckInHandler),
    (r'/statistics/unchecked', controller.StatisticsUncheckInHandler),
    (r'/statistics/total', controller.StatisticsTotalHandler),
    (r'/admin', controller.UserAdminHandler)
]
