from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from django.forms.models import model_to_dict
from .models import OperationLog, User
from .utils import CustomTokenAuthentication
import json

class OperationLogMiddleware(MiddlewareMixin):
    """
    操作日志中间件，记录用户的增、删、改操作日志。
    """

    # URL和breadcrumbName映射
    BREADCRUMB_MAP = {
        '/api/users/': '用户管理',
        '/api/asset-management/hosts/': '主机管理',
        '/api/asset-management/databases/': '数据库管理',
        # 其他API接口映射
    }

    def process_view(self, request, view_func, view_args, view_kwargs):
        # 跳过不需要Token认证的请求，例如登录请求
        if request.path == '/api/login/':
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
            'before_change': json.dumps(before_change_data, ensure_ascii=False) if before_change_data else '{}',
            'create_time': now(),
        }

        # 将operation_data保存在request对象中以便在process_response中使用
        request.operation_data = self.operation_data

    def process_response(self, request, response):
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
                request.operation_data['after_change'] = json.dumps(after_change_data, ensure_ascii=False)
            
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
                    return model_to_dict(user)
                except User.DoesNotExist:
                    return None
            # 可以添加其他模型的处理逻辑
        return None

    def get_after_data(self, request, response):
        """
        获取操作后的数据，如果返回的是JSON响应体，则直接返回，如果不是，则返回状态码和文本。
        """
        try:
            if 'application/json' in response['Content-Type']:
                return response.data
            else:
                return f"响应状态码: {response.status_code}, 响应内容: {response.content.decode('utf-8')}"
        except Exception as e:
            return f"获取变更后数据失败: {str(e)}"
