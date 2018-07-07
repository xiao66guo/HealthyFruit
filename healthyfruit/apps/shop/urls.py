from django.urls import path
from shop.views import ShopAddView, ShopInfoView

urlpatterns = [
    # path('detail/<sku_id>', DetailView.as_view(), name='detail'),
    path('add', ShopAddView.as_view(), name='add'),         # 购物车记录的添加
    path('show', ShopInfoView.as_view(), name='show'),      # 购物车页面显示

]