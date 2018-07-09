from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
from django.template import loader
import os
# 设置 Django 配置依赖的环境变量
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthyfruit.settings")
django.setup()
# 创建一个 Celery 对象
app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/11')

# 定义任务函数
@app.task
def send_register_active_email(to_email, username, token):
    # 发送激活邮件
    subject = '健康水果欢迎您'
    message = ''
    html_message = '''<h1>%s, 欢迎您成为健康水果的注册会员，请点击以下链接激活您的账户：</h1><br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>''' % (username, token, token)
    sender_user = settings.EMAIL_FROM
    receiver = [to_email]
    send_mail(subject, message, sender_user, receiver, html_message=html_message)


from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
# 生成商品首页静态页面
@app.task
def generate_static_index():
    # 获取商品分类信息
    types = GoodsType.objects.all()
    # 获取首页轮播商品信息
    scroll_banner = IndexGoodsBanner.objects.all().order_by('index')
    # 获取首页促销活动信息
    promotion_banner = IndexPromotionBanner.objects.all().order_by('index')
    # 获取首页分类商品展示信息
    for type in types:
        # 查询type种类首页展示的文字商品
        title_banner = IndexTypeGoodsBanner.objects.filter( type=type, display_type=0 ).order_by('index')
        # 查询type种类首页展示的图片image善品信息
        image_banner = IndexTypeGoodsBanner.objects.filter( type=type, display_type=1 ).order_by('index')
        type.title_banner = title_banner
        type.image_banner = image_banner
    # 获取登录用户的购物车信息
    shop_count = 0

    # 使用模板，渲染生成静态首页的内容
    # 1.加载模板文件，获取模板对象
    temp = loader.get_template('static_index.html')
    # 2.模板上下文
    context = {'types': types,
               'scroll_banner': scroll_banner,
               'promotion_banner': promotion_banner,
               'shop_count': shop_count}
    # 3.模板渲染，生成HTML文件
    static_index = temp.render(context)

    # 保存一个首页静态文件
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    with open(save_path, 'w') as f:
        f.write(static_index)

