from django.urls import path
from order.views import OrderPlaceView

urlpatterns = [
    path('place', OrderPlaceView.as_view(), name='place'),          # 提交订单页面的显示



]