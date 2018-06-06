from django.urls import path
from user.views import RegisterView

urlpatterns = [
    # path('register', views.register, name='register'),     # 注册页面
    # path('register_handle', views.register_handle, name='register_handle'),  # 注册处理

    path('register', RegisterView.as_view(), name='register'),     # 注册页面
]