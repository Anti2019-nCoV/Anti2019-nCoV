# _*_coding:utf-8_*_
"""
@ProjectName: resourceOrder
@Author:  Javen Yan
@File: task.py
@Software: PyCharm
@Time :    2020/2/6 上午11:46
"""
import json
import os
from web.models.databases import Areas
from web.models.dbSession import dbSession


def fetch_data():
    with open(os.path.join(os.getcwd(), 'a.json')) as f:
        result = json.loads(f.read())

    for res in result:
        print(f"save {res.get('RegionName')}")
        try:
            area = Areas(**res)
            dbSession.add(area)
            dbSession.commit()
        except:
            continue


