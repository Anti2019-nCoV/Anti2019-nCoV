# _*_coding:utf-8_*_
"""
@ProjectName: Anti2019-nCoV
@Author:  Javen Yan
@File: urls.py
@Software: PyCharm
@Time :    2020/1/28 下午1:58
"""
from web.apps.ncov.controller import NonCoVHandler, NonCoVNewsHandler, NonCoVOverallHandler, NonCoVOverSeaHandler

urlpatterns = [
    (r'/news', NonCoVNewsHandler),
    (r'/overall', NonCoVOverallHandler),
    (r'', NonCoVHandler),
    (r'/oversea', NonCoVOverSeaHandler)
]
