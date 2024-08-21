from django.urls import path
from apps.views import LoginView, UserListView, RolesPermissionsView, CreateUserView, UserUpdateView, LoginLogView, UserDetailView, OperationLogView, LockRecordView, CredentialView, DomainMonitorView

urlpatterns = [
    path('api/login/', LoginView.as_view(), name='login'),
    # path('api/check_permission/', check_permission, name='check-permission'),  # 配置检查权限的API路径
    path('api/users/create/', CreateUserView.as_view(), name='user-create'),  # 新增用户创建路径
    path('api/users/', UserListView.as_view(), name='user-list'),  # 配置用户列表的API路径
    path('api/users/<str:username>/lock/', UserDetailView.as_view(), name='user-lock'),  # 配置锁定用户的API路径
    path('api/users/<str:username>/reset_password/', UserDetailView.as_view(), name='reset-password'),  # 配置重置密码的API路径
    path('api/users/<str:username>/delete/', UserDetailView.as_view(), name='user-detail'),  # 配置删除用户和获取用户详细信息的API路径
    path('api/users/<str:username>/update/', UserUpdateView.as_view(), name='user-update'),  # 配置更新用户信息的API路径
    path('api/roles_permissions/', RolesPermissionsView.as_view(), name='roles-permissions'),  # 配置获取角色和权限数据的API路径
    path('api/login_logs/', LoginLogView.as_view(), name='login-log'),  # 配置获取登录日志数据的API路径
    path('api/operation_logs/', OperationLogView.as_view(), name='operation-log'),  # 配置获取操作日志数据的API路径
    path('api/lock_record/', LockRecordView.as_view(), name='lock-record'),  # 配置获取锁定记录的API路径
    path('api/credentials/', CredentialView.as_view(), name='credentials-list'),  # 配置凭据列表的API路径
    path('api/credentials/create/', CredentialView.as_view(), name='credentials-create'),  # 配置新建凭据的API路径
    path('api/credentials/<int:pk>/delete/', CredentialView.as_view(), name='credentials-delete'),  # 配置删除凭据的API路径
    path('api/credentials/<int:pk>/update/', CredentialView.as_view(), name='credentials-update'),  # 配置更新凭据的API路径
    path('api/monitor_domains/', DomainMonitorView.as_view(), name='domain-monitor'),  # 配置域名监控列表的API路径
    path('api/monitor_domains/create/', DomainMonitorView.as_view(), name='domain-monitor-create'),  # 配置新建域名监控的API路径
    path('api/monitor_domains/<int:pk>/update/', DomainMonitorView.as_view(), name='domain-monitor-update'),  # 配置更新域名监控的API路径
    path('api/monitor_domains/<int:pk>/delete/', DomainMonitorView.as_view(), name='domain-monitor-delete'),  # 配置删除域名监控的API路径
]