from apps.utils import (
    APIView, JsonResponse, jwt, datetime,
    get_object_or_404, timezone, RefreshToken,
    settings, User, UserLock, Token
)
from django.contrib.auth.hashers import make_password, check_password


class LoginView(APIView):
    def post(self, request):
        data = request.data  # 获取请求数据
        # 获取请求中的用户名和密码
        username = data.get('username')
        password = data.get('password')
        
        # 调试信息
        print(f"Username: {username}, Password: {password}")
        
        # 尝试获取用户对象，如果不存在返回用户不存在状态码
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'status': 'user_not_found', 'message': '用户不存在'}, status=404)
        
        # 获取或创建用户锁定记录
        user_lock, created = UserLock.objects.get_or_create(user=user)
        
        # 检查用户是否被锁定
        if user.status == 1:
            return JsonResponse({'status': 'account_locked', 'message': '账号已被锁定'}, status=403)
        
        # 比较输入的密码与数据库中的密码
        if not check_password(password, user.password):
            # 密码不匹配，增加登录尝试次数
            user_lock.login_count += 1
            user_lock.last_attempt_time = timezone.now()
            user_lock.save()
            
            # 如果尝试次数达到5次，将用户锁定
            if user_lock.login_count >= 5:
                user.status = 1
                user.save()
                return JsonResponse({'status': 'account_locked', 'message': '账号已被锁定'}, status=403)
            
            return JsonResponse({'status': 'password_incorrect', 'message': '密码错误'}, status=401)
        
        # 成功登录，重置登录尝试次数
        user_lock.login_count = 0
        user_lock.save()
        
        # 生成新的JWT令牌
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # 保存新的令牌到数据库，并更新create_time字段
        Token.objects.update_or_create(
            user=user,
            defaults={'token': access_token, 'create_time': timezone.now()}
        )
        
        # 更新用户的最后登录时间
        user.login_time = timezone.now()
        user.save()
        
        # 返回登录成功和令牌信息
        return JsonResponse({
            'status': 'login_successful',
            'access_token': access_token,
            'refresh_token': str(refresh),
            'name': user.name,
            'message': '登录成功'
        }, status=200)
