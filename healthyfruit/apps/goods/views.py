from django.shortcuts import render
from django.views.generic import View
from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner

# Create your views here.

# 首页
class IndexView(View):
    def get(self, request):
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
        content = {'types': types,
                   'scroll_banner': scroll_banner,
                   'promotion_banner': promotion_banner,
                   'shop_count': shop_count}

        return render(request, 'index.html', content)