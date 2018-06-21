from django.urls import path
from goods.views import IndexView

urlpatterns = [

    path('index', IndexView.as_view(), name='index'),           # 首页

]