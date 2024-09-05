from apps.utils import APIView, Response, status, Paginator, EmptyPage, PageNotAnInteger, CustomTokenAuthentication, IsAuthenticated, Credential, Host, Node
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from rest_framework import serializers
import json
import paramiko
import io

# 节点序列化器，用于验证和序列化 Node 模型的数据
class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = '__all__'


# 主机序列化器，用于验证和序列化 Host 模型的数据
class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = '__all__'

class HostView(APIView):
    """
    HostView 类处理 Host 模型的 CRUD 操作，
    并按主机名称、操作系统和协议进行过滤。
    """
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        处理GET请求，返回主机列表，支持按主机名称、操作系统和协议进行筛选，并提供分页功能。
        """
        
        # 获取筛选参数
        name = request.GET.get('name', '')  # 获取主机名称的筛选参数，默认为空字符串
        operating_system = request.GET.get('operating_system', '')  # 获取操作系统的筛选参数，默认为空字符串
        protocol = request.GET.get('protocol', '')  # 获取协议的筛选参数，默认为空字符串

        # 获取所有主机并按创建时间升序排序
        hosts = Host.objects.all().order_by('create_time')

        # 根据筛选参数过滤主机
        if name:
            hosts = hosts.filter(name__icontains=name)
        if operating_system:
            hosts = hosts.filter(operating_system__icontains=operating_system)
        if protocol:
            hosts = hosts.filter(protocol__icontains=protocol)

        # 获取分页参数
        page = request.GET.get('page', 1)  # 获取当前页码，默认为第1页
        page_size = request.GET.get('page_size', 10)  # 获取每页显示的记录数，默认为10

        # 实例化分页器
        paginator = Paginator(hosts, page_size)

        # 获取当前页的数据
        current_page_data = paginator.get_page(page)

        # 构建响应数据
        data = []
        for host in current_page_data:
            data.append({
                'id': host.id,
                'name': host.name,
                'status': host.status,
                'node': host.node.name,  # 返回节点名称
                'operating_system': host.operating_system,
                'network': host.network,
                'protocol': host.protocol,
                'port': host.port,
                'account_type': host.account_type.name if host.account_type else None,  # 关联凭据的名称
                'remarks': host.remarks,
                'create_time': host.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        # 构建分页信息
        pagination = {
            'current_page': current_page_data.number,  # 当前页码
            'total_pages': paginator.num_pages,  # 总页数
            'total_items': paginator.count,  # 总记录数
            'page_size': page_size,  # 每页显示的记录数
        }

        # 返回分页后的响应数据
        return Response({
            'result': data,
            'pagination': pagination
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """
        处理POST请求，用于创建新的主机
        """
        # 自动设置操作系统字段
        protocol = request.data.get('protocol', '')
        if protocol == 'SSH':
            request.data['operating_system'] = 'Linux'
        elif protocol == 'RDP':
            request.data['operating_system'] = 'Windows'
        
        serializer = HostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """
        处理PUT请求，更新现有主机
        """
        # 根据主键获取主机对象，如果不存在则返回404
        host = get_object_or_404(Host, pk=pk)
        
        # 自动设置操作系统字段
        protocol = request.data.get('protocol', '')
        if protocol == 'SSH':
            request.data['operating_system'] = 'Linux'
        elif protocol == 'RDP':
            request.data['operating_system'] = 'Windows'

        # 使用model_to_dict记录更新前的数据
        before_data = model_to_dict(host)

        # 序列化并验证更新的数据
        serializer = HostSerializer(host, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # 使用model_to_dict记录更新后的数据
            after_data = model_to_dict(host)

            # 返回更新后的主机数据
            return Response(after_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        处理DELETE请求，删除现有主机
        """
        # 根据主键获取主机对象，如果不存在则返回404
        host = get_object_or_404(Host, pk=pk)

        # 使用model_to_dict记录删除前的数据
        host_data = model_to_dict(host)

        # 删除主机
        host.delete()

        # 返回删除前的主机数据
        return Response(host_data, status=status.HTTP_204_NO_CONTENT)


# 凭据简要信息序列化器，用于仅返回凭据的 id, name 和 type
class CredentialSelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credential
        fields = ['id', 'name', 'type']

class CredentialSelectionView(APIView):
    """
    CredentialSelectionView 类返回简要的凭据信息，
    包括 id, name 和 type。
    """
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        处理GET请求，返回凭据的简要信息列表。
        """
        # 获取所有凭据
        credentials = Credential.objects.all()

        # 序列化数据
        serializer = CredentialSelectionSerializer(credentials, many=True)

        # 返回序列化后的数据
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class TestConnectionView(APIView):
    """
    测试主机连接的视图类，并更新主机的连接状态
    """
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        处理POST请求，测试主机连接并更新连接状态
        """
        host_id = request.data.get('host_id')
        ip_address = request.data.get('ip_address')
        port = (request.data.get('port'))
        credential_id = request.data.get('credential_id')

        # 获取主机对象和凭据信息
        host = get_object_or_404(Host, pk=host_id)
        credential = get_object_or_404(Credential, pk=credential_id)

        # 测试连接
        if credential.type == '密码':
            result, error = self.test_ssh_connection(ip_address, port, credential.account, credential.password)
        elif credential.type == '密钥':
            result, error = self.test_ssh_key_connection(ip_address, port, credential.account, credential.key, credential.key_password)
        else:
            return Response({'status': 1, 'error': '不支持的凭据类型'}, status=status.HTTP_400_BAD_REQUEST)

        # 更新主机状态字段
        host.status = result
        host.save()

        # 根据结果返回响应
        if result:
            return Response({'status': 0}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 1, 'error': error}, status=status.HTTP_200_OK)

    def test_ssh_connection(self, ip, port, username, password):
        """
        使用密码测试SSH连接
        """
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, port=port, username=username, password=password)
            ssh.close()
            return True, None
        except paramiko.AuthenticationException as auth_error:
            return False, f"Authentication failed: {auth_error}"
        except paramiko.SSHException as ssh_error:
            return False, f"SSH error occurred: {ssh_error}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def test_ssh_key_connection(self, ip, port, username, key, key_password=None):
            """
            使用密钥测试SSH连接
            """
            try:
                # 使用StringIO将字符串键转换为类似文件的对象
                key_file = io.StringIO(key)
                # 加载私钥，处理可能提供或不提供密钥密码的情况
                pkey = paramiko.RSAKey.from_private_key(key_file, password=key_password)
                
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, port=port, username=username, pkey=pkey)
                ssh.close()
                return True, None
            except paramiko.AuthenticationException as auth_error:
                return False, f"Authentication failed: {auth_error}"
            except paramiko.SSHException as ssh_error:
                return False, f"SSH error occurred: {ssh_error}"
            except Exception as e:
                return False, f"Unexpected error: {str(e)}"
            
# 新增节点信息的API
class NodeSelectionView(APIView):
    """
    NodeSelectionView 类返回简要的节点信息，
    包括 id 和 name。
    """
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        处理GET请求，返回节点的简要信息列表。
        """
        nodes = Node.objects.all()
        serializer = NodeSerializer(nodes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
