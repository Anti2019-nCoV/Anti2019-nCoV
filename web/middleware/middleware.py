# _*_coding:utf-8_*_
"""
@ProjectName: Anti2019-nCoV
@Author:  Javen Yan
@File: middleware.py
@Software: PyCharm
@Time :    2019/12/9 上午9:50
"""
from logzero import logger
from web.apps.gateway.libs.auth_lib import get_user_info
from web.middleware.base import Middleware
from web.models.databases import User


class WxMiddleware(Middleware):
    """
        微信用户认证中间件
    """

    async def process_request(self):
        logger.debug("用户认证中间件， 正在认证")
        access_token = self.request.headers.get('access_token', None)
        openid = self.get_argument('openid', None)
        if not access_token and not openid:
            kw = {"code": 10006, "message": "用户认证数据缺失"}
            return self.finish(kw)
        if access_token and openid:
            res = await get_user(self, access_token, openid)
            if res['status']:
                self.current_user = res['data']
            else:
                kw = {"code": res['code'], "message": res['msg']}
                return self.finish(kw)

    def process_response(self):
        logger.debug("用户认证中间件， 认证完成")


async def get_user(self, token, openid):
    user = User.by_openid(openid)
    if user:
        return {'status': True, 'data': user.to_dict()}
    else:
        return await get_user_info(self, access_token=token, openid=openid, auth=True)
