from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from user.models import User
import re

# Create your views here.


# 注册视图
def register(request):
    if request.method == 'GET':
        # 如果发起的请求是 GET 请求，就显示注册页面
        return render(request, 'register.html')
    elif request.method == 'POST':
        # 如果发起的请求是 POST 请求，就显示注册处理页面
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')

        # 进行校验(校验数据的完整性)
        if not all([username, password, email]):
            return render(request, 'register.html', {'error': '对不起，您输入的内容不完整！😭😭😭'})

        # 校验邮箱的正确性
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'error': '对不起，您输入的邮箱不正确！😭😭😭'})

        # 对注册的用户名进行判断是否已经存在
        try:
            user_info = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user_info = None

        if user_info:
            # 用户名已存在
            return render(request, 'register.html', {'error': '对不起，您输入的用户名已存在！😭😭😭'})

        # 业务处理:进行注册操作
        # User.objects.create(username=username, password=password, email=email)
        user_info = User.objects.create_user(username, password, email)
        user_info.is_active = 0
        user_info.save()

        # 注册成功后跳转页面
        return redirect(reverse('goods:index'))


# 创建类视图
class RegisterView(View):
    # 显示注册页面
    def get(self, request):
        return render(request, 'register.html')

    # 注册处理
    def post(self, request):
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')

        # 进行校验(校验数据的完整性)
        if not all([username, password, email]):
            return render(request, 'register.html', {'error': '对不起，您输入的内容不完整！😭😭😭'})

        # 校验邮箱的正确性
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'error': '对不起，您输入的邮箱不正确！😭😭😭'})

        # 对注册的用户名进行判断是否已经存在
        try:
            user_info = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user_info = None

        if user_info:
            # 用户名已存在
            return render(request, 'register.html', {'error': '对不起，您输入的用户名已存在！😭😭😭'})

        # 业务处理:进行注册操作
        # User.objects.create(username=username, password=password, email=email)
        user_info = User.objects.create_user(username, password, email)
        user_info.is_active = 0
        user_info.save()

        # 在用户注册成功后，发送激活邮件（链接）/user/active/token信息
            # 创建一个加密类对象（使用 itsdangerous 生成激活的 token 信息
        seria = Serializer(settings.SECRET_KEY, 3600)
        user_id = {'confirm': user_info.id}
            # 进行加密并返回一个 bytes 类型
        result_token = seria.dumps(user_id)
            # 转换 str 类型
        result_token = result_token.decode()



        # 注册成功后跳转页面
        return redirect(reverse('goods:index'))

