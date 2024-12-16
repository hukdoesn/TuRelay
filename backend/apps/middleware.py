from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import Token
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