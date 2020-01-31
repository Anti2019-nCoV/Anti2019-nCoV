# _*_coding:utf-8_*_
"""
@ProjectName: AntiSARI
@Author:  Javen Yan
@File: auth_lib.py
@Software: PyCharm
@Time :    2020/1/29 下午9:58
"""
import httpx as requests
from logzero import logger
from web.apps.base.status import StatusCode
from web.settings import wx_app_id, wx_app_secret


async def code2token(self, code):
    url = " https://api.weixin.qq.com/sns/oauth2/access_token?appid={}&secret={}&code={}&grant_type=authorization_code" \
        .format(wx_app_id, wx_app_secret, code)
    try:
        result = await requests.get(url)
        if 300 > result.status_code >= 200:
            content = result.json()
            if not content.get('errmsg'):
                return {'status': True, 'msg': '获取成功', 'code': StatusCode.success.value, "data": content}
            else:
                return {'status': False, 'msg': f'删除菜单失败 {content.get("errmsg")}', 'code': StatusCode.error.value}
        else:
            return {'status': False, 'msg': '删除菜单失败', 'code': StatusCode.third_api_error.value}
    except Exception as e:
        logger.error(f"Code 2 AccessToken Request Error : {e}")
        return {'status': False, 'msg': '删除菜单失败, 请求异常', 'code': StatusCode.third_api_error.value}


async def get_user_info(self, access_token, openid, auth=False):
    source_url = 'https://api.weixin.qq.com/sns/userinfo?access_token={ACCESS_TOKEN}&openid={OPENID}&lang=zh_CN'
    use_info_url = source_url.format(ACCESS_TOKEN=access_token, OPENID=openid)
    try:
        result = await requests.get(use_info_url)
        if 300 > result.status_code >= 200:
            content = result.json()
            if not content.get('errmsg'):
                if not auth:
                    userInfo = {
                        'nickname': content['nickname'],
                        'sex': content['sex'],
                        'province': content['province'],
                        'city': content['city'],
                        'country': content['country'],
                        'avatarPic': content['headimgurl'],
                        'openid': content['openid']
                    }
                else:
                    userInfo = {
                        'avatarPic': content['headimgurl'],
                        'openid': content['openid'],
                    }
                return {'status': True, 'msg': '获取信息成功', 'code': StatusCode.success.value, "data": userInfo}
            else:
                return {'status': False, 'msg': f'获取信息失败 {content.get("errmsg")}', 'code': StatusCode.error.value}
        else:
            return {'status': False, 'msg': '获取信息失败', 'code': StatusCode.third_api_error.value}
    except Exception as e:
        logger.error(f"Get User Info Request Error : {e}")
        return {'status': False, 'msg': '获取信息失败, 请求异常', 'code': StatusCode.third_api_error.value}
