# _*_coding:utf-8_*_
"""
@ProjectName: resourceOrder
@Author:  Javen Yan
@File: order_lib.py
@Software: PyCharm
@Time :    2020/2/6 下午12:12
"""
from logzero import logger
from web.apps.base.status import StatusCode
from web.models.databases import OrderUser, Orders
from web.utils.date2json import to_json
import hashlib
from datetime import datetime
from web.models.form_validate import validate


def get_str_sha1_secret_str(res):
    sha = hashlib.sha1(res.encode('utf-8'))
    encrypts = sha.hexdigest()
    return encrypts


async def get_orders(self, residentId):
    result = []
    if not residentId:
        return {'status': False, 'msg': "缺少参数", "code": StatusCode.miss_params_error.value}
    user = OrderUser.by_id_card(residentId)
    if user:
        rows = Orders.by_user_id(user.id)
        if rows:
            result = to_json(rows)
    return {'status': True, 'msg': "获取成功", "code": StatusCode.success.value, "data": result}


async def add_orders(self, payload):
    keys = ["user", "phamacy", "item", "smsCode"]
    state, msg = validate(keys, payload)
    if not state:
        return {'status': False, "msg": "参数校验失败", "code": StatusCode.miss_params_error.value}
    user = OrderUser.by_id_card(payload['user']['residentId'])
    userInfo = dict(userName=payload['user']['name'],
                    userIdCard=payload['user']['residentId'],
                    userPhone=payload['user']['telephone'],
                    communityName=payload['user']['communityName'],
                    communityDistrict=payload['user']['communityDistrict'],
                    communityAddress=payload['user']['communityAddress'])
    if not user:
        try:
            user = OrderUser(**userInfo)
            self.db.add(user)
            self.db.commit()
        except Exception as e:
            logger.error(f"Save user Error {e}")
            return {'status': False, 'msg': "数据库操作失败", "code": StatusCode.db_error.value}
    else:
        user.update(**userInfo)
    orderInfo = dict(
        userId=user.id,
        productName=payload.get('item').get('name'),
        productQty=payload.get('item').get('quantity'),
        pharmacyName=payload.get('phamacy').get('name'),
        pharmacyDistrict=payload.get('phamacy').get('district'),
        pharmacyAddress=payload.get('phamacy').get('address'),
    )
    try:
        order = Orders(**orderInfo)
        self.db.add(order)
        self.db.commit()
    except Exception as e:
        logger.error(f"Save user Error {e}")
        return {'status': False, 'msg': "数据库操作失败", "code": StatusCode.db_error.value}
    return {'status': True, 'msg': '预约成功', 'code': StatusCode.success.value, "data": order.to_dict()}


async def update_status(self, order_id):
    if order_id:
        row = Orders.by_uuid(order_id)
        if row:
            if row.Status == Orders.SUCCESS:
                return {'status': True, 'msg': "订单已经验证", "code": StatusCode.success.value}
            row.Status = Orders.SUCCESS
            row.updatedTime = datetime.now()
            self.db.commit()
            return {'status': True, 'msg': "订单验证成功", "code": StatusCode.success.value}
        else:
            return {'status': True, 'msg': "未找到改订单", "code": StatusCode.error.value}
    else:
        return {'status': True, 'msg': "未找到改订单", "code": StatusCode.error.value}


async def get_users(self, residentId, phone):
    results = None
    rows, t = OrderUser.filter(residentId, phone)
    if rows:
        if t == 'dict':
            results = rows.to_dict()
        elif t == 'list':
            results = to_json(rows)
    return {'status': True, 'msg': "获取成功", "data": results, "code": StatusCode.success.value}