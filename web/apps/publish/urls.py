# _*_coding:utf-8_*_
"""
@ProjectName: AntiSARI
@Author:  Javen Yan
@File: urls.py
@Software: PyCharm
@Time :    2020/2/2 上午9:53
"""

from web.apps.publish.controller import EpidemicPublishHandler

urlpatterns = [
    (r'', EpidemicPublishHandler)
]
