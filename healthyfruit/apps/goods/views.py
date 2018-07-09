from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from goods.models import GoodsSKU, GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
from django_redis import get_redis_connection
from django.core.cache import cache
from order.models import OrderGoods

# 商品首页
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


# 商品详情页面
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

            # 添加用户浏览记录(如果用户浏览过商品，可以先从redis对应的list元素中移除商品ID,在将商品ID添加到列表左侧)
            # 拼接key
            history_key = 'history_%d'%user.id
            con.lrem(history_key, 0, sku_id)
            con.lpush(history_key, sku_id)
            con.ltrim(history_key, 0, 4)


        context = {'types': types,
                   'sku': sku,
                   'order_skus': order_skus,
                   'new_skus': new_skus,
                   'same_spu_skus': same_spu_skus,
                   'shop_count': shop_count}
        return render(request, 'detail.html', context)


# 商品列表页
class ListView(View):
    def get(self, request, type_id, page):
        # 获取商品的分类信息
        types = GoodsType.objects.all()

        # 获取type_id对应的分类信息type
        try:
            type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            return redirect(reverse('goods:index'))

        # 获取商品排序的方式
        sort = request.GET.get('sort')
        # 获取type分类的商品列表信息
        if sort == 'price':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:   # 默认排序
            sort = 'default'
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')

        # 分页处理
        from django.core.paginator import Paginator
        paginator = Paginator(skus, 2)
        # 对页码进行处理
        page = int(page)
        if paginator.num_pages < page:
            page = 1
        # 获取对应页码的内容，返回page对象
        skus_page = paginator.page(page)

        # 对页码过多时进行处理
        # 不足5页，显示全部
        # 当前是前3页，显示1-5页
        # 当前是后3页，显示后5页
        # 大于5时，显示当前页的前2页、当前页、当前页的后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages+1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages-4, num_pages+1)
        else:
            pages = range(page-2, page+3)


        # 获取type种类的2个新品信息
        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]
        # 获取登录用的购物车信息
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
                   'type': type,
                   'skus_page': skus_page,
                   'new_skus': new_skus,
                   'sort': sort,
                   'pages': pages,
                   'shop_count': shop_count}

        return render(request, 'list.html', context)