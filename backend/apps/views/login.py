from apps.utils import (
    APIView, JsonResponse, jwt, datetime,
    get_object_or_404, timezone, RefreshToken,
    settings, User, UserLock, LoginLog, Token, user_has_view_permission
)
from django.contrib.auth.hashers import check_password
from user_agents import parse

class LoginView(APIView):
    """
    用户登录视图，处理用户的登录请求
    """
    def post(self, request):
        data = request.data  # 获取请求数据
        username = data.get('username')  # 获取请求中的用户名
        password = data.get('password')  # 获取请求中的密码
        client_ip = request.META.get('REMOTE_ADDR')  # 获取客户端 IP 地址

        user_agent_string = request.META.get('HTTP_USER_AGENT')  # 获取浏览器信息
        user_agent = parse(user_agent_string)
        
        browser_info = f"{user_agent.browser.family} {user_agent.browser.version_string}"  # 获取浏览器信息
        os_info = user_agent.os.family  # 获取操作系统信息

        # 尝试获取用户对象，如果不存在返回用户不存在状态码
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户不存在时记录日志
            LoginLog.objects.create(
                username=username,
                client_ip=client_ip,
                login_status=False,
                reason="用户不存在",
                browser_info=browser_info,
                os_info=os_info
            )
            return JsonResponse({'status': 'user_not_found', 'message': '用户不存在'}, status=404)

        # 获取或创建用户锁定记录
        user_lock, created = UserLock.objects.get_or_create(user=user)

        # 检查用户是否被锁定
        if user.status == 1:
            # 用户被锁定时记录日志
            LoginLog.objects.create(
                user=user,
                username=username,
                client_ip=client_ip,
                login_status=False,
                reason="账号已被锁定",
                browser_info=browser_info,
                os_info=os_info
            )
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
                # 记录锁定日志
                LoginLog.objects.create(
                    user=user,
                    username=username,
                    client_ip=client_ip,
                    login_status=False,
                    reason="账号已被锁定",
                    browser_info=browser_info,
                    os_info=os_info
                )
                return JsonResponse({'status': 'account_locked', 'message': '账号已被锁定'}, status=403)

            # 记录密码错误日志
            LoginLog.objects.create(
                user=user,
                username=username,
                client_ip=client_ip,
                login_status=False,
                reason="密码错误",
                browser_info=browser_info,
                os_info=os_info
            )
            return JsonResponse({'status': 'password_incorrect', 'message': '密码错误'}, status=401)

        # 成功登录，重置登录尝试次数
        user_lock.login_count = 0
        user_lock.save()

        # 检查用户是否具有只读权限
        is_read_only = user_has_view_permission(user)

        # 生成新的JWT令牌并将只读权限信息包含在负载中
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        access_token['is_read_only'] = is_read_only  # 将权限信息加入到JWT负载中

        # 更新或创建用户 Token
        Token.objects.update_or_create(
            user=user,
            defaults={'token': str(access_token), 'create_time': timezone.now()}
        )

        # 更新用户登录时间
        user.login_time = timezone.now()
        user.save()

        # 记录成功登录日志
        LoginLog.objects.create(
            user=user,
            username=username,
            client_ip=client_ip,
            login_status=True,
            browser_info=browser_info,
            os_info=os_info
        )

        # 返回登录成功响应
        return JsonResponse({
            'status': 'login_successful',
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'name': user.name,
            'is_read_only': is_read_only,  # 返回权限信息
            'message': '登录成功'
        }, status=200)
