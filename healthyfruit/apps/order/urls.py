from django.urls import path
from order.views import OrderPlaceView, OrderCommitView, OrderPayView, OrderCheckView

urlpatterns = [
    path('place', OrderPlaceView.as_view(), name='place'),          # 提交订单页面的显示
    path('commit', OrderCommitView.as_view(), name='commit'),       # 订单的创建
    path('pay', OrderPayView.as_view(), name='pay'),                # 订单支付
    path('check', OrderCheckView.as_view(), name='check'),          # 订单支付结果查询

]