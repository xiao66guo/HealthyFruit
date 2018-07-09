from django.urls import path
from shop.views import ShopAddView, ShopInfoView, ShopUpdateView

urlpatterns = [
    # path('detail/<sku_id>', DetailView.as_view(), name='detail'),
    path('add', ShopAddView.as_view(), name='add'),             # 购物车记录的添加
    path('show', ShopInfoView.as_view(), name='show'),          # 购物车页面显示
    path('update', ShopUpdateView.as_view(), name='update'),    # 购物车数据更新

]