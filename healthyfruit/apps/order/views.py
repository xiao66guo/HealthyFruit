from django.shortcuts import render, redirect
from django.views.generic import View
from django.urls import reverse
from user.models import Address
from utils.mini import LoginRequiredView
from goods.models import GoodsSKU
from django_redis import get_redis_connection


# 提交订单页面
class OrderPlaceView(LoginRequiredView, View):
    def post(self, request):
        # 获取登录的用户
        user = request.user

        # 获取用户购买商品的id
        sku_ids = request.POST.getlist('sku_ids')

        # 对参数进行判断
        if not all(sku_ids):
            # 如果数据不完整，跳转到购物车页面
            redirect(reverse('shop:show'))

        # 获取用户的收货地址
        adss = Address.objects.filter(user=user)
        print(adss)

        # 获取redis连接对象
        conn = get_redis_connection('default')
        shop_key = 'shop_%d' % user.id

        skus = []
        total_count = 0
        total_amount = 0
        # 获取用户所购买的商品信息
        for sku_id in sku_ids:
            # 根据商品的id查询对应商品的信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 从redis数据库中获取用户要购买的商品数量
            count = conn.hget(shop_key, sku_id)
            # 计算商品的小计
            amount = sku.price * int(count)
            # 给sku对象添加属性
            sku.count = int(count)
            sku.amount = amount

            # 追加商品
            skus.append(sku)
            # 计算总数量和总价格
            total_count += int(count)
            total_amount += amount

        # 运费
        trans_price = 10
        # 实付款
        total_pay = total_amount + trans_price

        context = {'adss': adss,
                   'skus': skus,
                   'total_count': total_count,
                   'total_amount': total_amount,
                   'total_pay': total_pay,
                   'trans_price': trans_price}

        return render(request, 'place_order.html', context)



