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
        # 用户管理
        '/api/users/': '用户列表',
        '/api/users/create/': '创建用户',
        '/api/users/<str:username>/detail/': '用户详情',
        '/api/users/<str:username>/update/': '更新用户',
        '/api/users/<str:username>/reset_password/': '重置密码',
        
        # 权限管理
        '/api/roles_permissions/': '角色权限管理',
        
        # 日志管理
        '/api/login_logs/': '登录日志',
        '/api/operation_logs/': '操作日志',
        '/api/command_logs/': '命令日志',
        '/api/lock_record/': '锁定记录',
        
        # 凭据管理
        '/api/credentials/': '凭据管理',
        '/api/credentials/create/': '创建凭据',
        '/api/credentials/<int:pk>/update/': '更新凭据',
        
        # 站点监控
        '/api/monitor_domains/': '站点监控',
        '/api/monitor_domains/create/': '创建监控',
        '/api/monitor_domains/<int:pk>/update/': '更新监控',
        
        # 主机管理
        '/api/hosts/': '主机管理',
        '/api/hosts/create/': '创建主机',
        '/api/hosts/<str:pk>/update/': '更新主机',
        '/api/hosts/test_connection/': '测试连接',
        
        # 终端管理
        '/api/terminal/get_tree_structure/': '终端树结构',
        '/api/terminal/files/': '文件管理',
        '/api/terminal/upload/': '文件上传',
        '/api/terminal/download/': '文件下载',
        
        # 告警管理
        '/api/alert_contacts/': '告警联系人',
        '/api/alert_contacts/create/': '创建联系人',
        '/api/command_alerts/': '命令告警',
        '/api/command_alerts/create/': '创建告警',
        
        # 资产管理
        '/api/asset_nodes/': '资产节点',
        
        # 系统设置
        '/api/settings/system/': '系统设置',
        
        # 仪表盘
        '/api/dashboard/statistics/': '仪表盘统计',
        '/api/dashboard/login_statistics/': '登录统计',
    }

    # 添加白名单路径
    WHITELIST_PATHS = [
        '/api/login/',
        '/api/mfa/bind/', 
        '/api/logout/'
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
                    # 对敏感数据进行脱敏处理
                    user_dict = self.clean_sensitive_data(user_dict)
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
                        # 对敏感数据进行脱敏处理
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
                        # 对敏感数据进行脱敏处理
                        monitor_dict = self.clean_sensitive_data(monitor_dict)
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
                        # 对敏感数据进行脱敏处理
                        host_dict = self.clean_sensitive_data(host_dict)
                        return host_dict
                    except Host.DoesNotExist:
                        return None

                elif 'asset_nodes' in request.path:
                    try:
                        from .models import Node  # 导入Node模型
                        node = Node.objects.get(pk=view_kwargs['pk'])
                        node_dict = model_to_dict(node)
                        # 添加父节点名称信息
                        if node.parent:
                            node_dict['parent_name'] = node.parent.name
                        # 添加主机数量信息
                        node_dict['host_count'] = node.hosts.count()
                        # 添加子节点数量信息
                        node_dict['child_nodes_count'] = node.children.count()
                        # 将日期时间字段转换为字符串
                        for key, value in node_dict.items():
                            if isinstance(value, datetime):
                                node_dict[key] = value.isoformat()
                        return node_dict
                    except Node.DoesNotExist:
                        return None

        return None

    def get_after_data(self, request, response):
        """
        获取操作后的数据，如果返回的是JSON响应体，则直接返回，如果不是，则返回状态码和文本。
        """
        try:
            if 'application/json' in response['Content-Type']:
                after_data = response.data
                # 转换日期时间字段为字符串并清理敏感数据
                if isinstance(after_data, dict):
                    after_data = self.clean_data(after_data)
                    after_data = self.clean_sensitive_data(after_data)
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
        if isinstance(data, dict):
            sensitive_fields = [
                'password', 
                'key', 
                'key_password', 
                'KeySecret',
                'secret_key',
                'access_key',
                'private_key',
                'public_key',
                'token',
                'api_key',
                'ssh_key',
                'ssh_password'
            ]
            
            cleaned_data = data.copy()
            for field in sensitive_fields:
                if field in cleaned_data:
                    cleaned_data[field] = '***'  # 使用统一的掩码替换敏感信息
            return cleaned_data
        return data