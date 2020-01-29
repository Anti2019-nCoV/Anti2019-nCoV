# _*_coding:utf-8_*_
"""
@ProjectName: Anti2019-nCoV
@Author:  Javen Yan
@File: urls.py
@Software: PyCharm
@Time :    2020/1/29 上午8:44
"""
from web.apps.gateway.auth_controller import Code2AccessTokenHandler, GetUserInfo
from web.apps.gateway.controller import WxGatewayHandler, JsApiHandler
from web.apps.gateway.wx_controller import WxMenuHandler, WxNewsHandler, ConstHandler, AutoReplyHandler

urlpatterns = [
    (r'/gateway', WxGatewayHandler),
    (r'/code2token', Code2AccessTokenHandler),
    (r'/getUserInfo', GetUserInfo),
    (r'/JsApi/(.*?)', JsApiHandler),
    (r'/menus', WxMenuHandler),
    (r'/news', WxNewsHandler),
    (r'/constant', ConstHandler),
    (r'/autoReply', AutoReplyHandler)
]