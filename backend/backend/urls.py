from django.urls import path
from apps.views import LoginView        # 统一从views包中导入视图类

urlpatterns = [
    path('api/login/', LoginView.as_view(), name='login'),
]