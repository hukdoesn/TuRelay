from functools import wraps
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import AuthenticationFailed

def check_permission(permission_code):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                raise AuthenticationFailed('用户未认证')

            permissions = RolePermission.objects.filter(user_id=user.id).values_list('permission__code', flat=True)
            if permission_code not in permissions:
                raise PermissionDenied('无权限执行此操作')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
