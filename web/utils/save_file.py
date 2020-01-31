#!/usr/bin/python
# @Time  : 1/31/20
# @Author: liyong
import os
import base64
import re
from logzero import logger


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

