from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from celery_tasks.task import send_register_active_email
from django.contrib.auth import authenticate, login, logout
from goods.models import GoodsSKU
from user.models import User, Address
from django_redis import get_redis_connection
from order.models import OrderInfo, OrderGoods
from redis import StrictRedis
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
        user_info = User.objects.create_user(username, email, password)
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

        # 使用 celery 发出发送邮件任务
        send_register_active_email.delay(email, username, result_token)

        # 注册成功后跳转页面
        return redirect(reverse('goods:index'))


# 创建激活邮件的视图
class ActiveView(View):
    # 激活处理
    def get(self, request, token):
        # 对加密后的 token 进行解密处理
        seria = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = seria.loads(token)
            # 获取激活的用户ID
            user_id = info['confirm']
            # 激活用户
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 激活后的应答
            return redirect(reverse('user:login'))
        except SignatureExpired as error:
            # 激活链接已失效（提示用户链接已失效，再次点击重新发送激活链接）
            return HttpResponse('<h1>激活链接已失效</h1>')


# 登录页面
class LoginView(View):
    def get(self, request):
        # 从 cookie 中加载用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES['username']
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'login.html', {'username': username, 'checked': checked})

    # 登录校验
    def post(self, request):
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('pwd')

        # 参数校验
        if not all([username, password]):
            return render(request, 'login.html', {'error': '用户名和密码输入不完整'})

        # 业务处理
        # 根据用户名和密码查找用户的信息
        user = authenticate(username=username, password=password)
        if user is not None:
            # 用户名和密码正确
            if user.is_active:  # 说明账户已激活
                # 对用户的登录状态进行处理
                login(request, user)
                # 获取 next 参数
                next_url = request.GET.get('next', reverse('goods:index'))

                response = redirect(next_url)

                # 判断是否需要记住用户名
                remember = request.POST.get('remember')
                if 'on' == remember: # 记住用户名
                    response.set_cookie('username', username, max_age=7*24*3600)
                else:   # 清除用户名
                    response.delete_cookie('username')

                return response
            else:   # 说明账户未激活
                return render(request, 'login.html', {'error': '对不起，您的账户未激活哦'})
        else:# 用户名和密码错误
            return render(request, 'login.html', {'error': '用户名或密码错误'})


# 退出页面
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('user:login'))


from utils.mini import LoginRequiredView
# 用户中心——信息页面
# class UserInfoView(View):
class UserInfoView(LoginRequiredView):
    def get(self, request):
        # 获取登录的用户
        user = request.user
        # 获取用户的收货地址信息
        address = Address.objs.get_default_address(user=user)

        # 获取用户最近浏览的商品信息
        # conn = StrictRedis(host='localhost', port=6379, db=12)
        conn = get_redis_connection('default')
        # 拼接list的key
        history_key = 'history_%d' % user.id
        # 获取用户最新浏览的5个商品的ID
        sku_ids = conn.lrange(history_key, 0, 4)
        # 根据ID获取商品的信息
        '''
        # 只需查一次数据库(但是查完之后需要调整顺序）
        skus = GoodSKU.objects.filter(id_in=sku_ids)
        # 调整商品信息的顺序
        sku_li = []
        for sku_id in sku_ids:
            for sku in skus:
                if int(sku_id) == sku.id:
                    sku_li.append(sku)
        '''

        # 效率低，需要查5次数据库(但是查完之后的顺序和用户浏览的顺序一致)
        skus = []
        for sku_id in sku_ids:
            # 根据 sku_id 获取商品信息
            sku = GoodsSKU.objects.get(id=sku_id)
            skus.append(sku)

        info_content = {'page': 'info',
                        'address': address,
                        'skus': skus}
        return render(request, 'user_center_info.html', info_content)


# 用户中心——订单页面
# class UserOrderView(View):
class UserOrderView(LoginRequiredView, View):
    def get(self, request, page):
        # 获取登录的用户
        user = request.user
        # 获取用户的订单信息
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')
        # 获取用户购买的每个商品订单的信息
        for order in orders:
            # 获取order订单商品的信息
            order_skus = OrderGoods.objects.filter(order=order)
            # 遍历取出每个商品的小计
            for order_sku in order_skus:
                # 计算商品小计
                amount = order_sku.count * order_sku.price
                # 保存订单商品的小计
                order_sku.amount = amount

            # 获取订单状态的标题
            order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
            # 计算订单的实付款
            order.total_pay = order.total_price + order.transit_price
            # 保存订单商品的信息
            order.order_skus = order_skus

        # 分页显示处理
        from django.core.paginator import Paginator
        paginator = Paginator(orders, 1)
        # 对页码进行校验
        page = int(page)
        if page > paginator.num_pages:
            page = 1
        # 获取第page也的内容
        order_page = paginator.page(page)

        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        context = {'order_page': order_page,
                   'pages': pages,
                   'page': 'order'}

        return render(request, 'user_center_order.html', context)


# 用户中心——地址页面
# class UserAddressView(View):
class UserAddressView(LoginRequiredView):
    def get(self, request):
        # 获取用户的默认收货地址
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 用户不存在默认的收货地址
        #     address = None
        address = Address.objs.get_default_address(user)
        context = {'page': 'address',
                   'address': address}
        return render(request, 'user_center_site.html', context)

    # 地址的添加
    def post(self, request):
        # 接收提交的参数
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        # 对接受的参数进行判断
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'error': '数据不完整，请重新输入'})
        # 对是否为默认地址进行判断
        # 1.如果有默认地址，新添加的地址为非默认地址
        # 2.如果没有默认地址，新添加的地址为默认地址
        # 获取登录用户的对象
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 用户不存在默认的收货地址
        #     address = None
        address = Address.objs.get_default_address(user)

        is_default = True
        if address:
            is_default = False

        # 添加收获地址
        Address.objs.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)
        # 对新添加的地址进行刷新
        return redirect(reverse('user:address'))






