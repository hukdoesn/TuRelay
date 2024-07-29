from django.urls import path
from apps.views import LoginView, UserListView, RolesPermissionsView, CreateUserView, UserUpdateView

urlpatterns = [
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/users/create/', CreateUserView.as_view(), name='user-create'),  # 新增用户创建路径
    path('api/users/', UserListView.as_view(), name='user-list'),  # 配置用户列表的API路径
    path('api/users/<str:username>/lock/', UserListView.as_view(), name='user-lock'),   # 配置锁定用户的API路径
    path('api/users/<str:username>/reset_password/', UserListView.as_view(), name='reset-password'),  # 配置重置密码的API路径
    path('api/users/<str:username>/', UserUpdateView.as_view(), name='user-update'),  # 配置更新用户的API路径
    path('api/roles_permissions/', RolesPermissionsView.as_view(), name='roles-permissions'),  # 配置获取角色和权限数据的API路径
]
