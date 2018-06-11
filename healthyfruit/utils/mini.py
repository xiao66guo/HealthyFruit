from django.views import View
from django.contrib.auth.decorators import login_required


class LoginRequiredView(View):
    @classmethod
    def as_view(cls, **initkwargs):
        # 调用 View 类中的 as_view() 方法
        view = super(LoginRequiredView, cls).as_view(**initkwargs)
        return login_required(view)