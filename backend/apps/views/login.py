from apps.utils import (
    APIView, JsonResponse, jwt, datetime,
    get_object_or_404, timezone, RefreshToken,
    settings, User, UserLock, LoginLog, Token, user_has_view_permission, is_ip_in_list
)
from django.contrib.auth.hashers import check_password
from user_agents import parse
from .mfa_auth import MFAUtil
from apps.models import SystemSettings
from datetime import timedelta

class LoginView(APIView):
    """
    用户登录视图，处理用户的登录请求
    """
    def post(self, request):
        data = request.data  # 获取请求数据
        username = data.get('username')  # 获取请求中的用户名
        password = data.get('password')  # 获取请求中的密码
        otp_code = data.get('otp_code')  # 获取OTP验证码
        client_ip = request.META.get('REMOTE_ADDR')  # 获取客户端 IP 地址

        user_agent_string = request.META.get('HTTP_USER_AGENT')  # 获取浏览器信息
        user_agent = parse(user_agent_string)
        
        browser_info = f"{user_agent.browser.family} {user_agent.browser.version_string}"  # 获取浏览器信息
        os_info = user_agent.os.family  # 获取操作系统信息

        # 获取系统设置
        system_settings = SystemSettings.objects.first()
        if not system_settings:
            system_settings = SystemSettings.objects.create()

        # 先检查白名单
        if system_settings.ip_whitelist:
            # 如果在白名单中，直接允许访问
            if is_ip_in_list(client_ip, system_settings.ip_whitelist):
                pass  # 允许继续登录流程
            else:
                # 不在白名单中，直接拒绝
                LoginLog.objects.create(
                    username=username,
                    client_ip=client_ip,
                    login_status=False,
                    reason="IP不在白名单中",
                    browser_info=browser_info,
                    os_info=os_info
                )
                return JsonResponse({
                    'status': 'ip_not_allowed',
                    'message': 'IP不在白名单中'
                }, status=403)
        # 如果没有设置白名单，则检查黑名单
        elif system_settings.ip_blacklist:
            if is_ip_in_list(client_ip, system_settings.ip_blacklist):
                LoginLog.objects.create(
                    username=username,
                    client_ip=client_ip,
                    login_status=False,
                    reason="IP在黑名单中",
                    browser_info=browser_info,
                    os_info=os_info
                )
                return JsonResponse({
                    'status': 'ip_blocked',
                    'message': 'IP在黑名单中'
                }, status=403)

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
                user.save()     # 保存更新到数据库
                user_lock.lock_count += 1       # 记录锁定次数
                user_lock.save()  # 保存更新到数据库
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

        # 密码验证通过后，检查MFA
        if check_password(password, user.password):
            # 检查是否启用了MFA
            if user.mfa_level == 1:
                # 如果未绑定MFA
                if not user.otp_secret_key:
                    secret_key = MFAUtil.generate_secret()
                    qr_code = MFAUtil.generate_qr_code(username, secret_key)
                    return JsonResponse({
                        'status': 'mfa_required',
                        'require_bind': True,
                        'qr_code': qr_code,
                        'secret_key': secret_key
                    }, status=200)
                
                # 如果已绑定MFA，验证OTP
                if not otp_code:
                    return JsonResponse({
                        'status': 'mfa_required',
                        'require_bind': False
                    }, status=200)
                
                if not MFAUtil.verify_otp(user.otp_secret_key, otp_code):
                    # 记录MFA验证失败日志
                    LoginLog.objects.create(
                        user=user,
                        username=username,
                        client_ip=client_ip,
                        login_status=False,
                        reason="MFA验证失败",
                        browser_info=browser_info,
                        os_info=os_info
                    )
                    return JsonResponse({'status': 'mfa_invalid', 'message': 'MFA验证码错误'}, status=401)

        # 成功登录，重置登录尝试次数
        user_lock.login_count = 0
        user_lock.save()

        # 检查用户是否具有只读权限
        is_read_only = user_has_view_permission(user)

        # 检查是否是允许多人登录的账号
        multi_login_accounts = system_settings.multi_login_account.split(',') if system_settings and system_settings.multi_login_account else []

        if user.username not in multi_login_accounts:
            # 如果不是多人登录账号，删除旧的 Token
            Token.objects.filter(user=user).delete()

        # 生成新的JWT令牌
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        access_token['is_read_only'] = is_read_only

        # 创建新的 Token
        Token.objects.create(
            user=user,
            token=str(access_token),
            create_time=timezone.now(),
            last_activity=timezone.now()
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

        # 获取系统设置
        system_settings = SystemSettings.objects.first()
        if not system_settings:
            system_settings = SystemSettings.objects.create()

        # 在成功登录后,生成过期时间(在返回响应前)
        login_expiry = timezone.now() + timedelta(hours=2)  # 设置2小时后过期
        session_expiry = timezone.now() + timedelta(hours=2)  # 设置会话2小时后过期

        # 返回登录成功响应
        return JsonResponse({
            'status': 'login_successful',
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'name': user.name,
            'is_read_only': is_read_only,
            'watermark_enabled': system_settings.watermark_enabled,     # 添加水印设置
            'login_expiry': login_expiry.isoformat(),  # 添加登录过期时间
            'session_expiry': session_expiry.isoformat(),  # 添加会话过期时间
            'message': '登录成功'
        }, status=200)

# 添加MFA绑定视图
class MFABindView(APIView):
    def post(self, request):
        username = request.data.get('username')
        secret_key = request.data.get('secret_key')
        otp_code = request.data.get('otp_code')
        
        try:
            user = User.objects.get(username=username)
            
            # 验证OTP代码
            if not MFAUtil.verify_otp(secret_key, otp_code):
                return JsonResponse({'status': 'error', 'message': '验证码错误'}, status=400)
            
            # 绑定成功，保存密钥
            user.otp_secret_key = secret_key
            user.save()
            
            return JsonResponse({'status': 'success', 'message': 'MFA绑定成功'}, status=200)
            
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=404)
