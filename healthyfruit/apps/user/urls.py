from django.urls import path
from user.views import RegisterView, ActiveView, LoginView, LogoutView, UserInfoView, UserOrderView, UserAddressView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # path('register', views.register, name='register'),     # 注册页面
    # path('register_handle', views.register_handle, name='register_handle'),  # 注册处理

    path('register', RegisterView.as_view(), name='register'),      # 注册页面
    path('active/<token>', ActiveView.as_view(), name='active'),    # 激活邮件路径
    path('login', LoginView.as_view(), name='login'),               # 登录界面
    path('logout', LogoutView.as_view(), name='logout'),            # 退出页面

    path('info', UserInfoView.as_view(), name='info'),              # 用户中心信息页面
    path('order', UserOrderView.as_view(), name='order'),           # 用户中心订单页面
    path('address', UserAddressView.as_view(), name='address'),     # 用户中心地址页面

]

'''
    path('info', login_required(UserInfoView.as_view()), name='info'),               # 用户中心信息页面
    path('order', login_required(UserOrderView.as_view()), name='order'),           # 用户中心订单页面
    path('address', login_required(UserAddressView.as_view()), name='address'),     # 用户中心地址页面
'''