#!/usr/bin/python
# @Time  : 2/1/20
# @Author: liyong
import os
import base64
import re
from logzero import logger
from web.models.databases import CompanyUser
from web.apps.base.status import StatusCode


async def save_pic(source, target, filename):

    try:
        # 使用正则source中抽取base64格式的图片信息
        result = re.match(r"data:image/(\w+);base64,(.*)", source)
        pic_ext = result.group(1)
        bs64_str = result.group(2)
        target_dir = os.path.join('uploads', target)
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir,  f'{filename}.{pic_ext}')
        # 将base64格式的数据装换为二进制数据
        imgdata = base64.b64decode(bs64_str)
        # 将二进制数据装换为图片
        with open(target_path, "wb") as f:
            f.write(imgdata)

        url = ''.join([
            target_path.replace("\\", "/")
        ])
    except Exception as er:
        logger.error(f"save {target} pic error: {er}")

        url = None

    logger.debug(f'url is {url}')

    return url


def check_user_exist(user):
    """判断一个用户是否注册了超过3个企业"""
    if not user:
        return {'status': True, 'existed': False}
    query = CompanyUser.by_user_id(user.id)
    if len(query) >= 3:
        return {'status': False, 'msg': '您已注册超过3个企业', "code": StatusCode.exist_error.value}
    return {'status': True, 'existed': True}


def get_length(generator):
    """获取迭代器长度"""
    if hasattr(generator, "__len__"):
        return len(generator)
    else:
        return sum(1 for _ in generator)
