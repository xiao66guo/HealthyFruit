from django.shortcuts import render

# Create your views here.

# 首页
def index(request):
    return render(request, 'index.html')