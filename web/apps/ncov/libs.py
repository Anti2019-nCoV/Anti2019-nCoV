# _*_coding:utf-8_*_
"""
@ProjectName: Anti2019-nCoV
@Author:  Javen Yan
@File: common.py
@Software: PyCharm
@Time :    2020/1/28 下午4:38
"""
import time

from logzero import logger
from web.apps.base.status import StatusCode
import httpx as requests
from web.settings import api_url


def format_time(t):
    new_time = int(str(t)[:-3])
    tmp = time.localtime(new_time)
    new_update = time.strftime("%Y-%m-%d %H:%M:%S", tmp)
    return new_update


def parse_single_data(rows, location=None):
    result = dict(confirmedCount=0,
                  suspectedCount=0,
                  curedCount=0,
                  deadCount=0)
    if not location:
        result.setdefault('cities', list())
    for row in rows:
        result['country'] = row.get('country')
        result['provinceName'] = row.get('provinceName')
        result['provinceShortName'] = row.get('provinceShortName')
        result['confirmedCount'] += int(row.get('confirmedCount'))
        result['suspectedCount'] += int(row.get('suspectedCount'))
        result['curedCount'] += int(row.get('curedCount'))
        result['deadCount'] += int(row.get('deadCount'))
        result['comment'] = row.get('comment', '')
        result['updateTime'] = row.get('updateTime')
        if 'cities' in result.keys():
            tmp = dict(cityName=row.get('cityName'),
                       confirmedCount=row.get('confirmedCount'),
                       suspectedCount=row.get('suspectedCount'),
                       curedCount=row.get('curedCount'),
                       deadCount=row.get('deadCount')
                       )
            result['cities'].append(tmp)
    return result


async def records(self, latest=1, province=None):
    result = []
    try:
        params = {"latest": latest}
        if province:
            params["province"] = province
        response = await requests.get(api_url + '/area', params=params)
        if 300 > response.status_code >= 200:
            content = response.json()
            result = content.get('results') if content.get('success') else []
    except Exception as e:
        logger.error(f"news fetch error {e}")

    new_result = []
    for res in result:
        if 'country' in res.keys():
            if res.get('updateTime'):
                res['updateTime'] = format_time(res.get('updateTime'))
            new_result.append(res)
    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": new_result}


async def oversea(self):
    result = []
    try:
        params = {"latest": 1}
        response = await requests.get(api_url + '/area', params=params)
        if 300 > response.status_code >= 200:
            content = response.json()
            result = content.get('results') if content.get('success') else []
    except Exception as e:
        logger.error(f"news fetch error {e}")
    new_result = []
    for res in result:
        if 'country' in res.keys():
            if res['country'] != '中国':
                if res.get('updateTime'):
                    res['updateTime'] = format_time(res.get('updateTime'))
                new_result.append(res)
    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": new_result}


async def news(self, page_size, position):
    result = []
    try:
        params = {"num": page_size}
        if position:
            params["province"] = position
        response = await requests.get(api_url + '/news', params=params)
        if 300 > response.status_code >= 200:
            content = response.json()
            result = content.get('results') if content.get('success') else []
    except Exception as e:
        logger.error(f"news fetch error {e}")

    new_result = []
    for res in result:
        if res.get('pubDate'):
            res['pubDate'] = format_time(res.get('pubDate'))
        new_result.append(res)
    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": result}


async def overalls(self, num=1):
    result = []
    try:
        response = await requests.get(api_url + '/overall', params={"latest": num})
        if 300 > response.status_code >= 200:
            content = response.json()
            result = content.get('results') if content.get('success') else []
    except Exception as e:
        logger.error(f"overall fetch error {e}")

    new_result = []
    for res in result:
        if res.get('updateTime'):
            res['updateTime'] = format_time(res.get('updateTime'))
        new_result.append(res)
    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": new_result}


async def rumors(self, num, rumorType):
    result = []
    try:
        response = await requests.get(api_url + '/rumors', params={"num": num, "rumorType": rumorType})
        if 300 > response.status_code >= 200:
            content = response.json()
            result = content.get('results') if content.get('success') else []
    except Exception as e:
        logger.error(f"overall fetch error {e}")

    new_result = []
    for res in result:
        if res.get('updateTime'):
            res['updateTime'] = format_time(res.get('updateTime'))
        new_result.append(res)
    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": new_result}



