from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from user.models import User
import re

# Create your views here.


# 注册视图
def register(request):
    return render(request, 'register.html')


# 注册提交响应的视图
def register_handle(request):
    # 接收数据
    username = request.POST.get('user_name')
    password = request.POST.get('pwd')
    email = request.POST.get('email')

    # 进行校验(校验数据的完整性)
    if not all([username, password, email]):
        return render(request, 'register.html', {'error': '对不起，您输入的内容不完整！😭😭😭'})

    # 校验邮箱的正确性
    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        return render( request, 'register.html', {'error': '对不起，您输入的邮箱不正确！😭😭😭'} )

    # 业务处理:进行注册操作
    # User.objects.create(username=username, password=password, email=email)
    user_info = User.objects.create_user(username, password, email)
    user_info.is_active = 0
    user_info.save()

    # 注册成功后跳转页面
    return redirect(reverse('goods:index'))

