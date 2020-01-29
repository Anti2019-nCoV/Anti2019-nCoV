# _*_coding:utf-8_*_
"""
@ProjectName: Anti2019-nCoV
@Author:  Javen Yan
@File: test.py
@Software: PyCharm
@Time :    2020/1/28 下午3:52
"""

from tasks.collector import SariDataCollector
from web.settings import api_url

SariDataCollector(api=api_url).run()