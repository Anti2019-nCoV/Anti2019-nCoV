# _*_coding:utf-8_*_
"""
@ProjectName: AntiSARI
@Author:  Javen Yan
@File: publish_libs.py
@Software: PyCharm
@Time :    2020/2/2 上午10:29
"""
from logzero import logger
from web.apps.base.status import StatusCode
from web.models.form_validate import validate
from web.models.databases import EpidemicPublishModel
from web.utils.date2json import to_json


async def add_publish(self, **kwargs):
    keys = ['cityName', 'regionName', 'isolatedCount', 'suspectedCount', 'confirmedCount', 'comment', 'curedCount']
    state, msg = validate(keys, kwargs)
    if not state:
        return {'status': False, 'msg': '数据入参验证失败', "code": StatusCode.params_error.value}
    try:
        EpidemicPublishModel.update_by_city(**kwargs)
        return {'status': True, 'msg': '业务操作成功', "code": StatusCode.success.value}
    except Exception as e:
        logger.error(f"EpidemicPublishModel Add Error {str(e)}")
        self.db.rollback()
        return {'status': False, 'msg': '业务操作失败', "code": StatusCode.db_error.value}


async def update_publish(self, **kwargs):
    keys = ['cityName', 'regionName']
    state, msg = validate(keys, kwargs)
    if not state:
        return {'status': False, 'msg': '数据入参验证失败', "code": StatusCode.params_error.value}
    try:
        EpidemicPublishModel.update_by_city(**kwargs)
        return {'status': True, 'msg': '业务操作成功', "code": StatusCode.success.value}
    except Exception as e:
        logger.error(f"EpidemicPublishModel Update Error {str(e)}")
        self.db.rollback()
        return {'status': False, 'msg': '业务操作失败', "code": StatusCode.db_error.value}


async def get_publish(self, cityName, classes=1):
    result = None
    if not cityName:
        return {'status': False, 'msg': '请选择城市', "code": StatusCode.error.value}
    if classes == 1 or classes == '1':
        row = EpidemicPublishModel.by_city(cityName)
        if row:
            result = parser(row)
        return {'status': True, 'msg': '业务操作成功', "code": StatusCode.success.value, 'data': result}
    else:
        row = EpidemicPublishModel.by_city(cityName)
        if row:
            result = to_json(row)
        return {'status': True, 'msg': '业务操作成功', "code": StatusCode.success.value, 'data': result}


def parser(results):
    new_res = {
        "cityName": "",
        "isolatedCount": 0,
        "suspectedCount": 0,
        "confirmedCount": 0,
        "curedCount": 0,
        "regions": []
    }
    new_region = []
    for result in results:
        res = result.to_dict()
        new_res['cityName'] = res.get('cityName')
        new_res['isolatedCount'] += int(res.get('isolatedCount'))
        new_res['suspectedCount'] += int(res.get('suspectedCount'))
        new_res['confirmedCount'] += int(res.get('confirmedCount'))
        new_res['curedCount'] += int(res.get('curedCount'))
        tmp = {"regionName": res.get('regionName'),
               "isolatedCount": res.get('isolatedCount'),
               "curedCount": res.get('curedCount'),
               "suspectedCount": res.get('suspectedCount'),
               "confirmedCount": res.get('confirmedCount')}
        new_region.append(tmp)
    new_res['regions'] = new_region
    return new_res


async def del_publish(self, kid):
    try:
        EpidemicPublishModel.delete(kid)
        return {'status': True, 'msg': '业务操作成功', "code": StatusCode.success.value}
    except Exception as e:
        logger.error(f"EpidemicPublishModel Delete Error {str(e)}")
        self.db.rollback()
        return {'status': False, 'msg': '业务操作失败', "code": StatusCode.db_error.value}
