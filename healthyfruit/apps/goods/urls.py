from django.urls import path
from goods.views import IndexView, DetailView, ListView

urlpatterns = [

    path('index', IndexView.as_view(), name='index'),                   # 首页
    path('detail/<sku_id>', DetailView.as_view(), name='detail'),       # 详情页面
    path('list/<type_id>/<page>', ListView.as_view(), name='list'),     # 商品列表页
]