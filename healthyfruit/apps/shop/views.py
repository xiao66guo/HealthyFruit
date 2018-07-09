from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django_redis import get_redis_connection
from goods.models import GoodsSKU
from utils.mini import LoginRequiredView

# 采用ajax post请求（商品ID<sku_id> 和 更新数量<count>）
# 购物车记录的添加
class ShopAddView(View):
    def post(self, request):
        # 获取登录的用户
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 1, 'msg': '用户为登录'})

        # 接收参数
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 对接收到的参数进行校验
        if not all([sku_id, count]):
            print(sku_id, count)
            return JsonResponse({'res': 1, 'msg': '数据不完整'})

        # 对商品的id进行判断
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 2, 'msg': '数据不存在'})

        # 对商品的数量进行判断
        try:
            count = int(count)
        except Exception as Error:
            return JsonResponse({'res': 3, 'msg': '商品数目非法'})
        if count <= 0:
            return JsonResponse({'res': 3, 'msg': '商品数目非法'})

        # 添加用户购物车记录的信息
        from django_redis import get_redis_connection
        conn = get_redis_connection('default')
        shop_key = 'shop_%d' % user.id
        shop_count = conn.hget(shop_key, sku_id)

        if shop_count:
            count += int(shop_count)

        # 对商品的库存进行判断
        if count > sku.stock:
            return JsonResponse({'res': 4, 'msg': '商品库存不足'})

        # 设置购物记录中s ku_id 的值
        conn.hset(shop_key, sku_id, count)

        # 获取用户购物车中的数量
        shop_count = conn.hlen(shop_key)

        return JsonResponse({'res': 5, 'shop_count': shop_count, 'msg': '添加成功'})


# 采用ajax post请求（商品ID<sku_id> 和 更新数量<count>）
# 购物车页面的信息
class ShopInfoView(LoginRequiredView, View):
    def get(self, request):
        # 获取登录的用户
        user = request.user
        # 获取redis链接
        conn = get_redis_connection('default')
        shop_key = 'shop_%d' % user.id
        # 从redis中获取用户购物车记录
        shop_dict = conn.hgetall(shop_key)

        skus = []
        total_count = 0
        total_amount = 0
        # 查询购物车中商品ID对应的商品信息
        for sku_id, count in shop_dict.items():
            # 根据sku_id获取商品的信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 计算单个商品的总价
            amount = sku.price * int(count)

            sku.count = int(count)
            sku.amount = amount
            skus.append(sku)

            # 计算商品的总件数和总价格
            total_count += int(count)
            total_amount += amount

        context = {'skus': skus,
                   'total_count': total_count,
                   'total_amount': total_amount}

        return render(request, 'cart.html', context)


# 采用ajax post请求（商品ID<sku_id> 和 更新数量<count>）
# 购物车页面信息更新
class ShopUpdateView(View):
    def post(self, request):
        # 获取登录的用户
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 1, 'msg': '用户为登录'})

        # 接收参数
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 对接收到的参数进行校验
        if not all([sku_id, count]):

            return JsonResponse({'res': 1, 'msg': '数据不完整'})

        # 对商品的id进行判断
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 2, 'msg': '数据不存在'})

        # 对商品的数量进行判断
        try:
            count = int(count)
        except Exception as Error:
            return JsonResponse({'res': 3, 'msg': '商品数目非法'})
        if count <= 0:
            return JsonResponse({'res': 3, 'msg': '商品数目非法'})

        # 更新用户购物车记录信息
        # 获取链接
        conn = get_redis_connection('default')
        # 拼接key
        shop_key = 'shop_%d' % user.id
        # 对商品的库存进行判断
        if count > sku.stock:
            return JsonResponse({'res': 4, 'msg': '商品库存不足'})

        # 更新购物车中商品的数目
        conn.hset(shop_key, sku_id, count)

        # 计算购物车中商品的总件数
        shop_count = 0
        shop_vals = conn.hvals(shop_key)
        for val in shop_vals:
            shop_count += int(val)

        return JsonResponse({'res': 5, 'shop_count': shop_count, 'msg': '更新成功'})


# 采用ajax post请求（商品ID<sku_id>)
# 删除购物车中的商品
class ShopDeleteView(View):
    def post(self, request):
        # 获取登录的用户
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 1, 'msg': '用户为登录'})

        # 接收参数
        sku_id = request.POST.get('sku_id')

        # 对接收到的参数进行校验
        if not all([sku_id]):
            return JsonResponse({'res': 1, 'msg': '数据不完整'})

        # 对商品的id进行判断
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 2, 'msg': '数据不存在'})

        # 删除用户的购物车记录
        # 获取链接的对象
        conn = get_redis_connection('default')
        shop_key = 'shop_%d' % user.id
        # 删除redis中用户购物车的记录
        conn.hdel(shop_key, sku_id)

        # 计算购物车中商品的总件数
        shop_count = 0
        shop_vals = conn.hvals(shop_key)
        for val in shop_vals:
            shop_count += int(val)

        return JsonResponse({'res': 3, 'shop_count': shop_count, 'msg': '删除成功'})


