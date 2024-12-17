from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import Token, RolePermission
from apps.utils import session_manager
import jwt
from django.conf import settings

class TokenAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        exempt_paths = ['/api/login/', '/api/logout/', '/api/mfa/bind/']
        
        if request.path not in exempt_paths:
            auth_header = request.headers.get('Authorization')
            if auth_header:
                try:
                    # 验证JWT token
                    payload = jwt.decode(
                        auth_header, 
                        settings.SECRET_KEY, 
                        algorithms=['HS256']
                    )
                    
                    # 从Redis检查会话状态
                    user_id = session_manager.get_session(auth_header)
                    if not user_id:
                        return JsonResponse({
                            'code': 'token_invalid',
                            'message': '登录状态无效'
                        }, status=401)
                    
                    # 更新会话过期时间
                    if not session_manager.update_session(auth_header):
                        return JsonResponse({
                            'code': 'token_invalid',
                            'message': '登录状态无效'
                        }, status=401)
                    
                    # 将用户ID添加到request中，供后续中间件使用
                    request.user_id = user_id
                    
                except jwt.ExpiredSignatureError:
                    session_manager.remove_session(auth_header)
                    return JsonResponse({
                        'code': 'token_expired',
                        'message': '登录已过期'
                    }, status=401)
                except jwt.InvalidTokenError:
                    session_manager.remove_session(auth_header)
                    return JsonResponse({
                        'code': 'token_invalid',
                        'message': '登录状态无效'
                    }, status=401)
            else:
                return JsonResponse({
                    'code': 'no_token',
                    'message': '未提供认证令牌'
                }, status=401)
            
        response = self.get_response(request)
        return response 

class PermissionMiddleware:
    """
    权限中间件，用于处理请求的权限控制
    - 对于只读用户，只允许GET请求
    - 对于完全访问用户，允许所有请求方法
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # 定义不需要权限检查的路径
        self.exempt_paths = [
            '/api/login/',
            '/api/logout/',
            '/api/mfa/bind/',
        ]
        # 定义允许只读用户访问的POST接口
        self.allowed_readonly_posts = [
            '/api/logout/',  # 允许登出
        ]

    def __call__(self, request):
        # 如果是豁免路径，直接放行
        if request.path in self.exempt_paths:
            return self.get_response(request)

        # 获取用户ID（由TokenAuthenticationMiddleware设置）
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return self.get_response(request)

        # 检查用户权限
        try:
            role_permission = RolePermission.objects.filter(user_id=user_id).first()
            if role_permission and role_permission.permission.code == 'view':
                # 只读用户只能进行GET请求和特定的POST请求
                if request.method != 'GET' and request.path not in self.allowed_readonly_posts:
                    return JsonResponse({
                        'status': 'permission_denied',
                        'message': '只读用户禁止增加、删除、修改等操作'
                    }, status=403)
        except Exception as e:
            # 如果出现异常，记录错误并返回权限错误
            print(f"Permission check error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '权限检查失败'
            }, status=500)

        return self.get_response(request) 