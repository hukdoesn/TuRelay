import paramiko
import io
import logging
import json
import stat
import datetime
import os
import tempfile
import hashlib
import uuid
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.models import Host, Credential, OperationLog
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings
from concurrent.futures import ThreadPoolExecutor
from apps.utils import CustomTokenAuthentication, IsAuthenticated
import time

# 获取日志记录器实例
logger = logging.getLogger('log')

# 创建线程池
file_transfer_executor = ThreadPoolExecutor(max_workers=5)  # 限制最大并发数为5

class FileListView(APIView):
    """获取服务器上的文件列表，包括文件的所有者和所属组信息，以及格式化的文件大小。"""
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, host_id):
        # 获取主机和凭据
        host = get_object_or_404(Host, id=host_id)
        credential = get_object_or_404(Credential, id=host.account_type.id)
        try:
            path = request.GET.get('path', '/')
            show_hidden = request.GET.get('show_hidden', 'false').lower() == 'true'

            # 建立 SSH 和 SFTP 连接
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 设置更长的超时时间和更大的窗口大小
            transport_timeout = settings.FILE_TRANSFER.get('TIMEOUT', 3600)

            if credential.type == '密码':
                ssh_client.connect(
                    host.network,
                    port=host.port,
                    username=credential.account,
                    password=credential.password,
                    timeout=transport_timeout
                )
            elif credential.type == '密钥':
                key_file = io.StringIO(credential.key)
                pkey = paramiko.RSAKey.from_private_key(
                    key_file, password=credential.key_password)
                ssh_client.connect(
                    host.network,
                    port=host.port,
                    username=credential.account,
                    pkey=pkey,
                    timeout=transport_timeout
                )
            else:
                return Response({'error': '不支持的凭据类型'}, status=status.HTTP_400_BAD_REQUEST)

            # 打开 SFTP 客户端并设置参数
            sftp_client = ssh_client.open_sftp()
            sftp_client.get_channel().settimeout(transport_timeout)
            sftp_client.get_channel().window_size = 67108864  # 64MB 窗口大小

            # 确定当前路径
            if not os.path.isabs(path):
                home_path = sftp_client.normalize('.')
                path = os.path.join(home_path, path)
            else:
                path = sftp_client.normalize(path)

            # 获取文件列表
            file_list = sftp_client.listdir_attr(path)

            # 过滤隐藏文件
            if not show_hidden:
                file_list = [f for f in file_list if not f.filename.startswith('.')]

            # 收集所有的 UID 和 GID
            uids = {f.st_uid for f in file_list}
            gids = {f.st_gid for f in file_list}

            # 批量获取用户和组信息
            uid_to_user = {}
            gid_to_group = {}

            if uids:
                # 使用单个命令获取所有用户信息
                uid_str = ' '.join(str(uid) for uid in uids)
                _, stdout, _ = ssh_client.exec_command(f'getent passwd {uid_str}')
                passwd_output = stdout.read().decode('utf-8')
                
                for line in passwd_output.strip().split('\n'):
                    if line:
                        parts = line.split(':')
                        if len(parts) >= 3:
                            uid_to_user[int(parts[2])] = parts[0]

            if gids:
                # 使用单个命令获取所有组信息
                gid_str = ' '.join(str(gid) for gid in gids)
                _, stdout, _ = ssh_client.exec_command(f'getent group {gid_str}')
                group_output = stdout.read().decode('utf-8')
                
                for line in group_output.strip().split('\n'):
                    if line:
                        parts = line.split(':')
                        if len(parts) >= 3:
                            gid_to_group[int(parts[2])] = parts[0]

            # 格式化文件信息
            files = []
            for file_attr in file_list:
                # 格式化文件大小
                size = self.format_size(file_attr.st_size)
                
                # 获取权限和时间
                permissions = stat.filemode(file_attr.st_mode)
                modify_time = datetime.datetime.fromtimestamp(
                    file_attr.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                
                # 获取所有者和组信息
                owner = uid_to_user.get(file_attr.st_uid, str(file_attr.st_uid))
                group = gid_to_group.get(file_attr.st_gid, str(file_attr.st_gid))

                files.append({
                    'filename': file_attr.filename,
                    'size': size,
                    'permissions': permissions,
                    'modify_time': modify_time,
                    'is_directory': stat.S_ISDIR(file_attr.st_mode),
                    'owner': owner,
                    'group': group,
                })

            # 关闭连接
            sftp_client.close()
            ssh_client.close()

            return Response({
                'files': files,
                'current_path': path
            })

        except Exception as e:
            logger.error('获取文件列表错误: %s (主机ID=%s)', str(e), host_id)
            if 'sftp_client' in locals():
                sftp_client.close()
            if 'ssh_client' in locals():
                ssh_client.close()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def format_size(size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

class FileUploadView(APIView):
    """上传文件到服务器。"""
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, host_id):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': '未找到文件'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 检查文件大小
        if uploaded_file.size > settings.FILE_TRANSFER['MAX_UPLOAD_SIZE']:
            return Response({'error': '文件大小超过限制'}, status=status.HTTP_400_BAD_REQUEST)

        path = request.POST.get('path', '.')
        transfer_id = str(uuid.uuid4())

        try:
            host = get_object_or_404(Host, id=host_id)
            credential = get_object_or_404(Credential, id=host.account_type.id)
            
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_file.close()
            
            # 使用线程池提交任务
            file_transfer_executor.submit(
                self.upload_task,
                host,
                credential,
                temp_file.name,
                path,
                uploaded_file.name,
                transfer_id
            )

            # 记录操作日志
            OperationLog.objects.create(
                user=request.user,  # 已通过认证的用户
                module='文件管理',
                request_interface=request.path,
                request_method=request.method,
                ip_address=request.META.get('REMOTE_ADDR'),
                before_change='{}',
                after_change=json.dumps({
                    'message': '文件上传',
                    'filename': uploaded_file.name,
                    'path': path,
                    'host_ip': host.network,
                    'host_name': host.name
                }, ensure_ascii=False)
            )

            return Response({
                'message': '开始上传',
                'path': path,
                'uploaded_file': uploaded_file.name,
                'transfer_id': transfer_id,
                'host_name': host.name,
                'host_ip': host.network
            })

        except Exception as e:
            logger.error('文件上传错误: %s', str(e))
            try:
                if 'temp_file' in locals():
                    os.unlink(temp_file.name)
            except Exception as e:
                logger.error('删除临时文件错误: %s', str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def upload_task(self, host, credential, temp_file_path, path, filename, transfer_id):
        channel_layer = get_channel_layer()
        ssh_client = None
        sftp_client = None

        try:
            # 建立SSH连接
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 设置更长的超时时间
            transport_timeout = settings.FILE_TRANSFER.get('TIMEOUT', 3600)
            banner_timeout = 60
            auth_timeout = 60

            if credential.type == '密码':
                ssh_client.connect(
                    host.network,
                    port=host.port,
                    username=credential.account,
                    password=credential.password,
                    timeout=transport_timeout,
                    banner_timeout=banner_timeout,
                    auth_timeout=auth_timeout
                )
            else:
                key_file = io.StringIO(credential.key)
                pkey = paramiko.RSAKey.from_private_key(
                    key_file,
                    password=credential.key_password
                )
                ssh_client.connect(
                    host.network,
                    port=host.port,
                    username=credential.account,
                    pkey=pkey,
                    timeout=transport_timeout,
                    banner_timeout=banner_timeout,
                    auth_timeout=auth_timeout
                )

            # 设置SFTP客户端
            sftp_client = ssh_client.open_sftp()
            sftp_client.get_channel().settimeout(transport_timeout)
            
            # 设置更大的窗口大小
            sftp_client.get_channel().window_size = 67108864  # 64MB

            remote_path = os.path.join(path, filename)

            # 获取文件总大小
            total_size = os.path.getsize(temp_file_path)
            
            # 初始化传输状态变量
            start_time = time.time()
            last_update_time = start_time
            last_transferred = 0

            def upload_callback(transferred, total):
                nonlocal last_update_time, last_transferred
                current_time = time.time()
                time_diff = current_time - last_update_time
                
                # 每0.5秒更新一次进度
                if time_diff >= 0.5:
                    progress = (transferred / total_size) * 100
                    bytes_since_last = transferred - last_transferred
                    speed = bytes_since_last / time_diff  # 字节/秒

                    async_to_sync(channel_layer.group_send)(
                        f"file_transfer_{transfer_id}",
                        {
                            'type': 'transfer_progress',
                            'filename': filename,
                            'progress': round(progress, 2),
                            'status': '进行中',
                            'transferred': transferred,
                            'total': total_size,
                            'speed': round(speed, 2)
                        }
                    )
                    
                    last_update_time = current_time
                    last_transferred = transferred
                
                return transferred

            # 计算本地文件MD5
            md5_hash = hashlib.md5()
            with open(temp_file_path, 'rb') as f:
                while True:
                    chunk = f.read(settings.FILE_TRANSFER['CHUNK_SIZE'])
                    if not chunk:
                        break
                    md5_hash.update(chunk)
            local_md5 = md5_hash.hexdigest()

            # 缓冲区上传文件
            sftp_client.put(
                temp_file_path,  # 临时文件路径
                remote_path,
                callback=upload_callback,
                confirm=True
            )

            # 发送校验状态
            async_to_sync(channel_layer.group_send)(
                f"file_transfer_{transfer_id}",
                {
                    'type': 'transfer_progress',
                    'filename': filename,
                    'progress': 100,
                    'status': '校验中',
                    'transferred': total_size,
                    'total': total_size,
                    'speed': 0
                }
            )

            # 计算远程文件MD5
            _, stdout, _ = ssh_client.exec_command(f'md5sum {remote_path}')
            remote_md5 = stdout.read().decode().split()[0]

            if remote_md5 == local_md5:
                async_to_sync(channel_layer.group_send)(
                    f"file_transfer_{transfer_id}",
                    {
                        'type': 'transfer_progress',
                        'filename': filename,
                        'progress': 100,
                        'status': '完成',
                        'transferred': total_size,
                        'total': total_size,
                        'speed': 0
                    }
                )
            else:
                # 如果MD5不匹配，删除远程文件并报错
                sftp_client.remove(remote_path)
                raise Exception('文件校验失败')

        except Exception as e:
            logger.error('文件上传错误: %s', str(e))
            async_to_sync(channel_layer.group_send)(
                f"file_transfer_{transfer_id}",
                {
                    'type': 'transfer_progress',
                    'filename': filename,
                    'progress': 0,
                    'status': '失败',
                    'transferred': 0,
                    'total': total_size if 'total_size' in locals() else 0,
                    'speed': 0
                }
            )
        finally:
            # 清理资源
            if sftp_client:
                sftp_client.close()
            if ssh_client:
                ssh_client.close()
            try:
                os.unlink(temp_file_path)
            except:
                pass

class FileDownloadView(APIView):
    """从服务器下载文件。"""
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, host_id):
        filename = request.GET.get('filename')
        if not filename:
            return Response({'error': '未指定文件名'}, status=status.HTTP_400_BAD_REQUEST)

        path = request.GET.get('path', '.')
        transfer_id = str(uuid.uuid4())

        try:
            host = get_object_or_404(Host, id=host_id)
            credential = get_object_or_404(Credential, id=host.account_type.id)

            # 使用线程池提交下载任务
            file_transfer_executor.submit(
                self.download_task,
                host,
                credential,
                filename,
                path,
                transfer_id
            )

            # 记录操作日志
            OperationLog.objects.create(
                user=request.user,  # 已通过认证的用户
                module='文件管理',
                request_interface=request.path,
                request_method=request.method,
                ip_address=request.META.get('REMOTE_ADDR'),
                before_change='{}',
                after_change=json.dumps({
                    'message': '文件下载',
                    'filename': filename,
                    'path': path,
                    'host_ip': host.network,
                    'host_name': host.name
                }, ensure_ascii=False)
            )

            return Response({
                'message': '开始下载',
                'transfer_id': transfer_id,
                'host_name': host.name,
                'host_ip': host.network,
                'filename': filename,
                'path': path
            })

        except Exception as e:
            logger.error('文件下载错误: %s', str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def download_task(self, host, credential, filename, path, transfer_id):
        channel_layer = get_channel_layer()
        ssh_client = None
        sftp_client = None

        try:
            # 建立SSH连接
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            transport_timeout = settings.FILE_TRANSFER.get('TIMEOUT', 3600)
            banner_timeout = 60
            auth_timeout = 60

            if credential.type == '密码':
                ssh_client.connect(
                    host.network,
                    port=host.port,
                    username=credential.account,
                    password=credential.password,
                    timeout=transport_timeout,
                    banner_timeout=banner_timeout,
                    auth_timeout=auth_timeout
                )
            else:
                key_file = io.StringIO(credential.key)
                pkey = paramiko.RSAKey.from_private_key(
                    key_file,
                    password=credential.key_password
                )
                ssh_client.connect(
                    host.network,
                    port=host.port,
                    username=credential.account,
                    pkey=pkey,
                    timeout=transport_timeout,
                    banner_timeout=banner_timeout,
                    auth_timeout=auth_timeout
                )

            # 设置SFTP客户端
            sftp_client = ssh_client.open_sftp()
            sftp_client.get_channel().settimeout(transport_timeout)
            
            # 设置更大的窗口大小
            sftp_client.get_channel().window_size = 67108864  # 64MB

            remote_path = os.path.join(path, filename)
            
            # 获取文件大小
            file_size = sftp_client.stat(remote_path).st_size
            
            # 初始化传输状态变量
            start_time = time.time()
            last_update_time = start_time
            last_transferred = 0

            def download_callback(transferred, total):
                nonlocal last_update_time, last_transferred
                current_time = time.time()
                time_diff = current_time - last_update_time
                
                # 每0.5秒更新一次进度
                if time_diff >= 0.5:
                    progress = (transferred / file_size) * 100
                    bytes_since_last = transferred - last_transferred
                    speed = bytes_since_last / time_diff  # 字节/秒

                    async_to_sync(channel_layer.group_send)(
                        f"file_transfer_{transfer_id}",
                        {
                            'type': 'transfer_progress',
                            'filename': filename,
                            'progress': round(progress, 2),
                            'status': '进行中',
                            'transferred': transferred,
                            'total': file_size,
                            'speed': round(speed, 2)
                        }
                    )
                    
                    last_update_time = current_time
                    last_transferred = transferred
                
                return transferred

            # 创建临时文件
            temp_file_path = f'/tmp/download_{transfer_id}'
            sftp_client.get(
                remote_path,
                temp_file_path,
                callback=download_callback
            )

            # 发送完成消息
            async_to_sync(channel_layer.group_send)(
                f"file_transfer_{transfer_id}",
                {
                    'type': 'transfer_progress',
                    'filename': filename,
                    'progress': 100,
                    'status': '完成',
                    'transferred': file_size,
                    'total': file_size,
                    'speed': 0
                }
            )

        except Exception as e:
            logger.error('文件下载错误: %s', str(e))
            async_to_sync(channel_layer.group_send)(
                f"file_transfer_{transfer_id}",
                {
                    'type': 'transfer_progress',
                    'filename': filename,
                    'progress': 0,
                    'status': '失败',
                    'transferred': 0,
                    'total': file_size,
                    'speed': 0
                }
            )
        finally:
            if sftp_client:
                sftp_client.close()
            if ssh_client:
                ssh_client.close()

# 添加新的视图函数来处理文件下载
class FileDownloadContentView(APIView):
    """处理文件下载内容的视图"""
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, transfer_id):
        try:
            # 获取临时文件路径
            temp_file_path = f'/tmp/download_{transfer_id}'  # 使用 transfer_id 作为临时文件名
            
            if not os.path.exists(temp_file_path):
                return Response({'error': '文件不存在或已过期'}, status=status.HTTP_404_NOT_FOUND)
            
            # 读取文件并返回
            response = FileResponse(
                open(temp_file_path, 'rb'),
                as_attachment=True,
                filename=os.path.basename(temp_file_path)
            )
            
            # 设置响应头
            response['Content-Type'] = 'application/octet-stream'
            
            return response
            
        except Exception as e:
            logger.error('文件下载错误: %s', str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file_path)
            except:
                pass 