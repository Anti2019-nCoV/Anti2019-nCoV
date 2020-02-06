# _*_coding:utf-8_*_
"""
@ProjectName: resourceOrder
@Author:  Javen Yan
@File: urls.py
@Software: PyCharm
@Time :    2020/2/6 下午2:06
"""


from web.apps.product.controller import ProductsHandler


urlpatterns = [
    (r'', ProductsHandler)
]