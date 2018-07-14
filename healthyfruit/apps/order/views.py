from django.shortcuts import render, redirect
from django.views.generic import View
from django.urls import reverse
from django_redis import get_redis_connection
from django.http import JsonResponse
from django.db import transaction

from user.models import Address
from utils.mini import LoginRequiredView
from goods.models import GoodsSKU
from order.models import OrderInfo, OrderGoods
from datetime import datetime


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
        adss = Address.objs.filter(user=user)

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

        sku_ids = ','.join(sku_ids)
        context = {'adss': adss,
                   'skus': skus,
                   'total_count': total_count,
                   'total_amount': total_amount,
                   'total_pay': total_pay,
                   'trans_price': trans_price,
                   'sku_ids': sku_ids}

        return render(request, 'place_order.html', context)


# 创建订单
class OrderCommitView(View):
    @transaction.atomic()
    def post(self, request):
        # 对登录用户进行判断
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'msg': '用户未登录'})

        # 接收参数
        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids')

        # 对接收的参数进行校验
        if not all([addr_id, pay_method, sku_ids]):
            return JsonResponse({'res': 1, 'msg': '数据不完整'})

        # 对地址信息进行校验
        try:
            addr = Address.objs.get(id=addr_id)
        except Address.DoesNotExist:
            return JsonResponse({'res': 2, 'msg': '地址不存在'})

        # 对支付方式进行校验
        if pay_method not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({'res': 3, 'msg': '支付方式非法'})

        # 生成订单（当前时间+用户id)
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)

        # 运费
        trans_price = 0
        # 订单中商品的总数量和总价格
        total_count = 0
        total_price = 0

        # 设置mysql事务的保存点
        sid = transaction.savepoint()
        try:
            '''向 df_order_info 中添加一条记录'''
            order = OrderInfo.objects.create(order_id=order_id,
                                             user=user,
                                             addr=addr,
                                             pay_method=pay_method,
                                             total_count=total_count,
                                             total_price=total_price,
                                             transit_price=trans_price)

            # 获取redis的链接对象
            conn = get_redis_connection('default')
            shop_key = 'shop_%d' % user.id

            sku_ids = sku_ids.split(',')
            # 遍历获取用户所要购买的商品信息
            for sku_id in sku_ids:
                for i in range(3):
                    # 根据id查询商品的信息
                    try:
                        sku = GoodsSKU.objects.get(id=sku_id)

                        # sku = GoodsSKU.objects.select_for_update.get(id=sku_id)
                    except GoodsSKU.DoesNotExist:
                        # 将事务回滚到保存点之前
                        transaction.savepoint_rollback(sid)
                        return JsonResponse({'res': 4, 'msg': '商品信息错误'})

                    # 从redis中获取用户要购买的商品数量
                    count = conn.hget(shop_key, sku_id)

                    # 判断商品的库存
                    if sku.stock < int(count):
                        transaction.savepoint_rollback(sid)
                        return JsonResponse({'res': 6, 'msg': '商品库存不足'})

                    '''对商品的库存减少，销量增加'''
                    origin_stock = sku.stock
                    new_stock = origin_stock - int(count)
                    new_sales = sku.sales + int(count)
                    res = GoodsSKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
                    if res == 0:
                        if i == 2:
                            transaction.savepoint_rollback(sid)
                            return JsonResponse({'res': 7, 'msg': '下单失败2'})
                        continue

                    '''向 df_order_goods 中添加一条记录'''
                    OrderGoods.objects.create(order=order,
                                              sku=sku,
                                              count=int(count),
                                              price=sku.price)
                    # '''对商品的库存减少，销量增加'''
                    # sku.stock -= int(count)
                    # sku.sales += int(count)
                    '''对用户购买的商品的总数量和总价格进行累计'''
                    total_count += int(count)
                    total_price += sku.price * int(count)

                    break

            # TODO:更新订单信息记录中购买的商品的总数目和总金额
            order.total_count = total_count
            order.total_price = total_price
            order.save()
        except Exception as e:
            transaction.savepoint_rollback(sid)
            return JsonResponse({'res': 7, 'msg': '下单失败'})

        # TODO:删除购物车中的记录
        conn.hdel(shop_key, *sku_ids)

        return JsonResponse({'res': 5, 'msg': '订单创建成功'})



