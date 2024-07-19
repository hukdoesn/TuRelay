from django.urls import path
from apps.views import LoginView, UserListView        # 统一从views包中导入视图类

urlpatterns = [
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/users/', UserListView.as_view(), name='user-list'),  # 配置用户列表的API路径
    # path('api/users', UserListView.as_view(), name='user-list'),
]