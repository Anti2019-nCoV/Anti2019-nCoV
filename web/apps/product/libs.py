# _*_coding:utf-8_*_
"""
@ProjectName: resourceOrder
@Author:  Javen Yan
@File: libs.py
@Software: PyCharm
@Time :    2020/2/6 下午2:06
"""
from logzero import logger

from web.apps.base.status import StatusCode
from web.models.databases import Products
from web.models.form_validate import validate
from web.utils.date2json import to_json


async def get_product(self, _type):
    result = []
    if _type == 'all':
        rows = Products.all()
    else:
        rows = Products.hot_product()
    if rows:
        result = to_json(rows)
    return {'status': True, 'msg': "获取成功", "data": result, "code": StatusCode.success.value}


async def add_product(self, payload):
    keys = ["productName", "productMaxPrice", "productMinPrice", "productDesc"]
    state, msg = validate(keys, payload)
    if not state:
        return {'status': False, "msg": "参数校验失败", "code": StatusCode.miss_params_error.value}
    tmp = payload.get('isHot')
    if tmp == 1 or tmp == '1':
        status = True
    else:
        status = False
    productInfo = dict(
        productName=payload.get('productName'),
        productMaxPrice=payload.get('productMaxPrice'),
        productMinPrice=payload.get('productMinPrice'),
        productDesc=payload.get('productDesc'),
        isHot=status
    )
    try:
        product = Products(**productInfo)
        self.db.add(product)
        self.db.commit()
    except Exception as e:
        logger.error(f"Save Product Error {e}")
        return {'status': False, 'msg': "数据库操作失败", "code": StatusCode.db_error.value}
    return {'status': True, 'msg': '添加成功', 'code': StatusCode.success.value}


async def delete_product(self, _id):
    row = Products.by_id(_id)
    if row:
        try:
            self.db.delete(row)
            self.db.commit()
            return {'status': True, 'msg': '删除成功', 'code': StatusCode.success.value}
        except Exception as e:
            logger.error(f"Delete Product Error {e}")
            return {'status': False, 'msg': "数据库操作失败", "code": StatusCode.db_error.value}
    return {'status': False, 'msg': '未找到商品', 'code': StatusCode.not_found_error.value}


async def update_product(self, payload):
    _id = payload.get('id')
    if not _id:
        return {'status': False, 'msg': "缺少商品检索参数", "code": StatusCode.miss_params_error.value}
    row = Products.by_id(_id)
    if row:
        try:
            for k, v in payload.items():
                if k == 'priceRange':
                    continue
                setattr(row, k, v)
            self.db.commit()
            return {'status': True, 'msg': '更新成功', 'code': StatusCode.success.value}
        except Exception as e:
            logger.error(f"Update Product Error {e}")
            return {'status': False, 'msg': "数据库操作失败", "code": StatusCode.db_error.value}
    else:
        return {'status': False, 'msg': '未找到产品', 'code': StatusCode.error.value}