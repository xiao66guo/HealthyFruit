from django.urls import path
from order.views import OrderPlaceView, OrderCommitView

urlpatterns = [
    path('place', OrderPlaceView.as_view(), name='place'),          # 提交订单页面的显示
    path('commit', OrderCommitView.as_view(), name='commit'),       # 订单的创建


]