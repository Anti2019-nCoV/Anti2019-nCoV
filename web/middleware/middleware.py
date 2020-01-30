# _*_coding:utf-8_*_
"""
@ProjectName: Anti2019-nCoV
@Author:  Javen Yan
@File: middleware.py
@Software: PyCharm
@Time :    2019/12/9 上午9:50
"""
from logzero import logger
from web.middleware.base import Middleware
from web.models.databases import User


class WxMiddleware(Middleware):
    """
        微信用户认证中间件
    """

    async def process_request(self):
        logger.debug("用户认证中间件， 正在认证")
        access_token = self.request.headers.get('access_token', None)
        openid = self.request.headers.get('openid', None)
        if access_token is None or openid is None:
            kw = {"code": 10006, "message": "用户认证数据缺失"}
            return self.finish(kw)
        self.openid = openid    # 传入openid
        self.current_user = await get_user(self, openid)

    def process_response(self):
        logger.debug("用户认证中间件， 认证完成")


async def get_user(self, openid):
    return User.by_openid(openid)
