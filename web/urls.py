# _*_coding:utf-8_*_
"""
@ProjectName: Anti2019-nCoV
@Author:  Javen Yan
@File: urls.py
@Software: PyCharm
@Time :    2019/12/5 上午10:41
"""
from web.utils.app_route import merge_route
from web.apps.public.urls import urlpatterns as common
from web.apps.position.urls import urlpatterns as position
from web.apps.ncov.urls import urlpatterns as no_sari
from web.apps.gateway.urls import urlpatterns as wxGateway
from web.apps.user.urls import urlpatterns as user
from web.apps.publish.urls import urlpatterns as publish
from web.apps.region.urls import urlpatterns as region
from web.apps.orders.urls import urlpatterns as orders
from web.apps.product.urls import urlpatterns as products
urlpatterns = list()

urlpatterns += merge_route(common, '')
urlpatterns += merge_route(position, '/area')
urlpatterns += merge_route(no_sari, '/nCoV')
urlpatterns += merge_route(wxGateway, '/wx')
urlpatterns += merge_route(user, '/user')
urlpatterns += merge_route(publish, '/epidemic')
urlpatterns += merge_route(region, '/address')
urlpatterns += merge_route(orders, '/orders')
urlpatterns += merge_route(products, '/items')