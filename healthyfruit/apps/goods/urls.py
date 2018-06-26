from django.urls import path
from goods.views import IndexView, DetailView

urlpatterns = [

    path('index', IndexView.as_view(), name='index'),           # 首页
    path('detail/<sku_id>', DetailView.as_view(), name='detail'),   # 详情页面
]