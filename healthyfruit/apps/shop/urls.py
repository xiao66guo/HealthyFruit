from django.urls import path
from shop.views import ShopAddView, ShopInfoView, ShopUpdateView, ShopDeleteView

urlpatterns = [
    # path('detail/<sku_id>', DetailView.as_view(), name='detail'),
    path('add', ShopAddView.as_view(), name='add'),             # 购物车记录的添加
    path('show', ShopInfoView.as_view(), name='show'),          # 购物车页面显示
    path('update', ShopUpdateView.as_view(), name='update'),    # 购物车数据更新
    path('delete', ShopDeleteView.as_view(), name='delete'),    # 删除购物车中商品记录

]