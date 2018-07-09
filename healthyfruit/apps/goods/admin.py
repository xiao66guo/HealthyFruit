from django.contrib import admin
from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
from django.core.cache import cache

class BaseAdmin(admin.ModelAdmin):
    # 增加数据或者更新数据是被调用
    def save_model(self, request, obj, form, change):
        # 执行增加或者更新操作
        super().save_model(request, obj, form, change)

        # 启动celery
        from celery_tasks.task import generate_static_index
        print('更新 generate_static_index.delay')
        generate_static_index.delay()

        # 清楚首页缓存数据
        cache.delete('index_page_data')

    # 删除数据时调用
    def delete_model(self, request, obj):
        super().delete_model(request, obj)

        # 启动celery
        from celery_tasks.task import generate_static_index
        generate_static_index.delay()
        # 清除首页缓存
        cache.delete('index_page_data')


class GoodsTypeAdmin(BaseAdmin):
    pass


class IndexGoodsBannerAdmin(BaseAdmin):
    pass


class IndexPromotionBannerAdmin(BaseAdmin):
    pass


class IndexTypeGoodsBannerAdmin(BaseAdmin):
    pass


admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
