from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from goods.models import GoodsSKU, GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
from django_redis import get_redis_connection
from django.core.cache import cache
from order.models import OrderGoods

# 首页
class IndexView(View):
    def get(self, request):
        # 先从缓存中获取数据
        context = cache.get('index_page_data')
        if context is None: # 如果缓存中没有数据
            print('设置首页缓存')
            # 获取商品分类信息
            types = GoodsType.objects.all()
            # 获取首页轮播商品信息
            scroll_banner = IndexGoodsBanner.objects.all().order_by('index')
            # 获取首页促销活动信息
            promotion_banner = IndexPromotionBanner.objects.all().order_by('index')
            # 获取首页分类商品展示信息
            for type in types:
                # 查询type种类首页展示的文字商品
                title_banner = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')
                # 查询type种类首页展示的图片image善品信息
                image_banner = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
                type.title_banner = title_banner
                type.image_banner = image_banner
            # 获取登录用户的购物车信息
            shop_count = 0
            # 上下文
            context = {'types': types,
                       'scroll_banner': scroll_banner,
                       'promotion_banner': promotion_banner,
                       'shop_count': shop_count}

            # 设置缓存 cache.set(缓存的名称，缓存的数据，缓存的有效时间)
            cache.set('index_page_data', context, 3600)

        # 获取user
        user = request.user
        # 对用户的登录状态进行判断
        if user.is_authenticated:
            # 用户已登录
            con = get_redis_connection('default')   # StrictRedis
            shop_key = 'cart_%s'%user.id
            shop_count = con.hlen(shop_key)
            context.update(shop_count=shop_count)

        return render(request, 'index.html', context)


# 详情页面
class DetailView(View):
    def get(self, request, sku_id):
        # 获取商品的分类信息
        types = GoodsType.objects.all()
        # 获取商品的详情信息
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:index'))
        # 获取商品的评论信息
        order_skus = OrderGoods.objects.filter(sku=sku).exclude(comment='').order_by('-update_time')
        # 获取和商品同一种类的2个新品信息
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('create_time')[:2]
        # 获取和商品同一个SPU的其他规格商品
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=sku_id)

        # 获取登录用户购物车信息
        shop_count = 0
        # 获取user
        user = request.user
        # 对用户的登录状态进行判断
        if user.is_authenticated:
            # 用户已登录
            con = get_redis_connection('default')  # StrictRedis
            shop_key = 'cart_%s' % user.id
            shop_count = con.hlen(shop_key)

        context = {'types': types,
                   'sku': sku,
                   'order_skus': order_skus,
                   'new_skus': new_skus,
                   'same_spu_skus': same_spu_skus,
                   'shop_count': shop_count}
        return render(request, 'detail.html', context)