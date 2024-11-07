# middleware_log.py

from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from django.forms.models import model_to_dict
from .models import OperationLog, User, Credential, DomainMonitor, Host
from .utils import CustomTokenAuthentication
import json
from datetime import datetime
from uuid import UUID

class OperationLogMiddleware(MiddlewareMixin):
    """
    操作日志中间件，记录用户的增、删、改操作日志。
    """

    # URL和breadcrumbName映射
    BREADCRUMB_MAP = {
        '/api/users/': '用户列表',
        '/api/credentials/': '凭据管理',
        '/api/asset-management/hosts/': '主机管理',
        '/api/asset-management/databases/': '数据库管理',
        '/api/monitor_domains/': '站点监控',
        '/api/hosts/': '主机列表',
        # 其他API接口映射
    }

    # 添加白名单路径
    WHITELIST_PATHS = [
        '/api/login/',
        '/api/mfa/bind/',  # 添加MFA绑定路径到白名单
    ]

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        在视图处理请求之前执行，记录操作前的数据。
        """
        # 检查请求路径是否在白名单中
        if request.path in self.WHITELIST_PATHS:
            return None

        # 仅处理认证后的请求
        self.user = self.get_authenticated_user(request)
        if not self.user:
            return None

        # 获取breadcrumbName
        breadcrumb_name = self.get_breadcrumb_name(request.path)

        # 获取变更前的数据
        before_change_data = self.get_before_data(request, view_func, view_kwargs)

        # 初始化操作日志数据
        self.operation_data = {
            'user': self.user,
            'module': breadcrumb_name,
            'request_interface': request.path,
            'request_method': request.method,
            'ip_address': self.get_client_ip(request),
            'before_change': json.dumps(self.clean_data(before_change_data), ensure_ascii=False) if before_change_data else '{}',
            'create_time': now(),
        }

        # 将operation_data保存在request对象中以便在process_response中使用
        request.operation_data = self.operation_data

    def process_response(self, request, response):
        """
        在视图处理响应之后执行，记录操作后的数据。
        """
        # 如果请求没有被捕获或者用户未认证，直接返回响应
        if not hasattr(request, 'operation_data') or not self.user:
            return response

        # 仅记录成功的增、删、改操作日志 (状态码2xx表示成功)
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and response.status_code // 100 == 2:
            if request.method == 'DELETE':
                # 不记录after_change数据
                request.operation_data['after_change'] = '{}'
            else:
                after_change_data = self.get_after_data(request, response)
                # 在这里转换 UUID 类型为字符串
                request.operation_data['after_change'] = json.dumps(self.clean_data(after_change_data), ensure_ascii=False)
            
            # 创建操作日志
            OperationLog.objects.create(**request.operation_data)

        return response

    def get_authenticated_user(self, request):
        """
        获取经过认证的用户，使用自定义的认证类。
        """
        user, _ = CustomTokenAuthentication().authenticate(request)
        return user

    def get_breadcrumb_name(self, path):
        """
        根据请求路径获取breadcrumbName，使用预定义的映射。
        """
        for url, name in self.BREADCRUMB_MAP.items():
            if path.startswith(url):
                return name
        return '未定义模块'

    def get_client_ip(self, request):
        """
        获取请求的IP地址。
        """
        return request.META.get('REMOTE_ADDR')

    def get_before_data(self, request, view_func, view_kwargs):
        """
        获取操作前的数据，对于DELETE、PUT、PATCH以及某些POST操作，从数据库中获取当前数据。
        """
        if request.method in ['DELETE', 'PUT', 'PATCH', 'POST']:
            # 针对特定的POST请求也获取before_change数据
            if request.method == 'POST' and 'reset_password' not in request.path:
                return None

            if 'username' in view_kwargs:
                try:
                    user = User.objects.get(username=view_kwargs['username'])
                    user_dict = model_to_dict(user)
                    # 将日期时间字段转换为字符串
                    for key, value in user_dict.items():
                        if isinstance(value, datetime):
                            user_dict[key] = value.isoformat()
                    # 过滤掉password字段
                    if 'password' in user_dict:
                        user_dict['password'] = '***'
                    return user_dict
                except User.DoesNotExist:
                    return None

            if 'pk' in view_kwargs:
                # 通过检查view_func名称或请求路径来确定我们正在处理的模型
                if 'credential' in request.path:
                    try:
                        credential = Credential.objects.get(pk=view_kwargs['pk'])
                        credential_dict = model_to_dict(credential)
                        # 将日期时间字段转换为字符串
                        for key, value in credential_dict.items():
                            if isinstance(value, datetime):
                                credential_dict[key] = value.isoformat()
                        # 过滤掉敏感字段
                        credential_dict = self.clean_sensitive_data(credential_dict)
                        return credential_dict
                    except Credential.DoesNotExist:
                        return None

                elif 'monitor_domain' in request.path:
                    try:
                        monitor = DomainMonitor.objects.get(pk=view_kwargs['pk'])
                        monitor_dict = model_to_dict(monitor)
                        # 将日期时间字段转换为字符串
                        for key, value in monitor_dict.items():
                            if isinstance(value, datetime):
                                monitor_dict[key] = value.isoformat()
                        return monitor_dict
                    except DomainMonitor.DoesNotExist:
                        return None
                    
                elif 'host' in request.path:
                    try:
                        host = Host.objects.get(pk=view_kwargs['pk'])
                        host_dict = model_to_dict(host)
                        # 将日期时间字段转换为字符串
                        for key, value in host_dict.items():
                            if isinstance(value, datetime):
                                host_dict[key] = value.isoformat()
                        return host_dict
                    except Host.DoesNotExist:
                        return None

        return None

    def get_after_data(self, request, response):
        """
        获取操作后的数据，如果返回的是JSON响应体，则直接返回，如果不是，则返回状态码和文本。
        """
        try:
            if 'application/json' in response['Content-Type']:
                after_data = response.data
                # 转换日期时间字段为字符串
                if isinstance(after_data, dict):
                    after_data = self.clean_data(after_data)
                return after_data
            else:
                return f"响应状态码: {response.status_code}, 响应内容: {response.content.decode('utf-8')}"
        except Exception as e:
            return f"获取变更后数据失败: {str(e)}"

    def clean_data(self, data):
        """
        清理数据，处理不能序列化的数据类型（例如UUID和datetime）。
        """
        if isinstance(data, dict):
            cleaned_data = {}
            for key, value in data.items():
                if isinstance(value, UUID):
                    cleaned_data[key] = str(value)  # 转换UUID为字符串
                elif isinstance(value, datetime):
                    cleaned_data[key] = value.isoformat()  # 转换datetime为ISO格式字符串
                else:
                    cleaned_data[key] = self.clean_data(value)  # 递归处理嵌套的数据
            return cleaned_data
        elif isinstance(data, (list, tuple)):
            return [self.clean_data(item) for item in data]  # 处理列表或元组
        elif isinstance(data, datetime):
            return data.isoformat()  # 处理单个datetime对象
        elif isinstance(data, UUID):
            return str(data)  # 处理单个UUID对象
        return data

    def clean_sensitive_data(self, data):
        """
        清理敏感信息，如密码、密钥等。
        """
        sensitive_fields = ['password', 'key', 'key_password', 'KeySecret']
        for field in sensitive_fields:
            if field in data:
                data[field] = '****'  # 掩盖敏感信息
        return data