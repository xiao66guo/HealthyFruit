from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
import os
# 设置 Django 配置依赖的环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthyfruit.settings")

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
