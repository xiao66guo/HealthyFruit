from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


# 注册视图
def register(request):
    return render(request, 'register.html')


