from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import Token
import jwt
from django.conf import settings

class TokenAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 不需要验证token的路径
        exempt_paths = ['/api/login/', '/api/logout/']
        
        if request.path not in exempt_paths:
            auth_header = request.headers.get('Authorization')
            if auth_header:
                try:
                    # 验证token
                    payload = jwt.decode(
                        auth_header, 
                        settings.SECRET_KEY, 
                        algorithms=['HS256']
                    )
                    
                    # 检查token是否在数据库中且有效
                    token = Token.objects.filter(
                        token=auth_header,
                        is_active=True
                    ).first()
                    
                    if not token:
                        return JsonResponse({
                            'code': 'token_invalid',
                            'message': '登录状态无效'
                        }, status=401)
                    
                    # 检查token是否过期
                    now = timezone.now()
                    token_expiry = token.create_time + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
                    session_timeout = token.last_activity + timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES)
                    
                    if now > token_expiry:
                        token.delete()  # 直接删除过期的token
                        return JsonResponse({
                            'code': 'token_expired',
                            'message': '登录已过期'
                        }, status=401)
                    
                    if now > session_timeout:
                        token.delete()  # 直接删除超时的token
                        return JsonResponse({
                            'code': 'session_timeout',
                            'message': '会话已超时'
                        }, status=401)
                    
                    # 更新最后活动时间
                    token.last_activity = now
                    token.save()
                    
                except jwt.ExpiredSignatureError:
                    # JWT token过期
                    Token.objects.filter(token=auth_header).delete()  # 直接删除
                    return JsonResponse({
                        'code': 'token_expired',
                        'message': '登录已过期'
                    }, status=401)
                except jwt.InvalidTokenError:
                    # JWT token无效
                    Token.objects.filter(token=auth_header).delete()  # 直接删除
                    return JsonResponse({
                        'code': 'token_invalid',
                        'message': '登录状态无效'
                    }, status=401)
            
        response = self.get_response(request)
        return response 