import paramiko
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404
from apps.models import Host, Credential, Token, User, CommandLog  # Import your models
from asgiref.sync import sync_to_async
import io
import logging
import json
from django.http import JsonResponse, FileResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import stat
import datetime
import os
import urllib.parse  # For parsing query parameters
import re  # For regular expressions

# 获取日志记录器实例
logger = logging.getLogger('log')

class SSHConsumer(AsyncWebsocketConsumer):
    """
    SSHConsumer 处理 WebSocket 连接，以使用 Paramiko 根据存储在数据库中的主机凭据建立 SSH 会话。
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 初始化属性
        self.last_input_char = None  # 记录上一次输入的字符
        self.command_buffer = ''
        self.is_command_executed = False  # 标记是否执行了命令
        self.in_shell_prompt = False  # 标记是否在 shell 提示符
        self.in_editor = False  # 标记是否在编辑器中

        # 定义一个正则表达式来匹配 shell 提示符
        self.shell_prompt_regex = re.compile(r'[^@]+@[^:]+:[^\$#]*[#$]\s?$')

    async def connect(self):
        # 从 URL 中获取主机 ID
        self.host_id = self.scope['url_route']['kwargs']['host_id']

        # 从查询参数中获取 token
        query_string = self.scope['query_string'].decode('utf-8')
        query_params = urllib.parse.parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if not token:
            await self.send_text_data('认证失败：未提供令牌。\n')
            await self.close()
            return

        # 验证令牌并获取用户名
        try:
            # 假设 Token 表有字段 'token' 和 'user_id'
            token_obj = await sync_to_async(Token.objects.get)(token=token)
            self.user = await sync_to_async(User.objects.get)(id=token_obj.user_id)
            self.username = self.user.username
        except Token.DoesNotExist:
            await self.send_text_data('认证失败：无效的令牌。\n')
            await self.close()
            return
        except User.DoesNotExist:
            await self.send_text_data('认证失败：用户不存在。\n')
            await self.close()
            return

        # 异步获取主机和凭据信息
        self.host = await sync_to_async(get_object_or_404)(Host, id=self.host_id)
        self.credential_id = await sync_to_async(lambda: self.host.account_type.id)()
        self.credential = await sync_to_async(get_object_or_404)(Credential, id=self.credential_id)

        # 接受 WebSocket 连接
        await self.accept()

        # 初始化 SSH 连接
        await self.establish_ssh_connection()

    async def disconnect(self, close_code):
        # 处理 WebSocket 连接断开
        if hasattr(self, 'ssh_client'):
            self.ssh_client.close()  # 关闭 SSH 连接

    async def receive(self, text_data):
        # 处理从 WebSocket 接收到的数据
        try:
            data = json.loads(text_data)
            if isinstance(data, dict) and 'cols' in data and 'rows' in data:
                # 调整终端大小
                self.ssh_channel.resize_pty(width=data['cols'], height=data['rows'])
            elif hasattr(self, 'ssh_channel'):
                # 将客户端输入的数据发送到 SSH 通道
                self.ssh_channel.send(text_data)

                # 更新命令缓冲区
                await self.update_command_buffer(text_data)

                # 记录最后一个输入的字符
                if text_data:
                    self.last_input_char = text_data[-1]
        except (json.JSONDecodeError, TypeError):
            # 如果数据不是 JSON 或不能迭代，则视为普通的命令输入
            if hasattr(self, 'ssh_channel'):
                self.ssh_channel.send(text_data)

                # 更新命令缓冲区
                await self.update_command_buffer(text_data)

                # 记录最后一个输入的字符
                if text_data:
                    self.last_input_char = text_data[-1]

    async def update_command_buffer(self, data):
        """
        更新命令缓冲区，处理用户输入的数据，包括特殊键。
        """
        for char in data:
            if not self.in_shell_prompt:
                # 未检测到 shell 提示符，不记录输入
                continue

            if self.in_editor:
                # 在编辑器中，不记录输入
                continue

            if char == '\r' or char == '\n':
                # 用户按下回车键，标记命令已执行
                self.is_command_executed = True
                # 保存当前命令缓冲区
                await self.save_command_log()
                # 重置命令缓冲区
                self.command_buffer = ''
                self.in_shell_prompt = False  # 等待下一个提示符
            elif char == '\x7f':
                # 处理退格键
                self.command_buffer = self.command_buffer[:-1]
            elif ord(char) == 9:
                # Tab 键，等待服务器返回自动补全内容
                pass
            else:
                # 添加输入的字符到命令缓冲区
                self.command_buffer += char

    async def save_command_log(self):
        """
        保存执行的命令到 CommandLog 表中。
        """
        command = self.command_buffer.strip()
        if command:
            # 检测是否进入编辑器，如 vi、vim
            if command.startswith('vi ') or command.startswith('vim '):
                self.in_editor = True  # 进入编辑器
                # 只记录进入编辑器的命令，不记录后续内容
                command_to_save = command
            else:
                command_to_save = command

            # 创建命令日志记录
            await sync_to_async(CommandLog.objects.create)(
                username=self.username,
                command=command_to_save,
                # hosts拼接network
                # hosts=f"{self.host.name} ({self.host.network})",
                hosts=self.host.name,
                network=self.host.network,
                credential=self.credential.account,
                create_time=datetime.datetime.now()
            )
            logger.info('命令已记录: 用户=%s, 命令=%s', self.username, command_to_save)

    async def establish_ssh_connection(self):
        """
        使用主机凭据建立 SSH 连接。
        """
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            if self.credential.type == '密码':
                # 使用密码认证连接
                await sync_to_async(self.ssh_client.connect)(
                    self.host.network,
                    port=self.host.port,
                    username=self.credential.account,
                    password=self.credential.password,
                    timeout=10
                )
            elif self.credential.type == '密钥':
                # 使用密钥认证连接
                key_file = io.StringIO(self.credential.key)
                pkey = paramiko.RSAKey.from_private_key(key_file, password=self.credential.key_password)
                await sync_to_async(self.ssh_client.connect)(
                    self.host.network,
                    port=self.host.port,
                    username=self.credential.account,
                    pkey=pkey,
                    timeout=10
                )
            else:
                await self.send_text_data('不支持的凭据类型。\n')
                await self.close()
                return

            # 使用指定终端大小启动 shell
            self.ssh_channel = self.ssh_client.invoke_shell(term='xterm', width=80, height=24)
            self.ssh_channel.settimeout(0.0)

            # 开始从 SSH 服务器读取数据
            asyncio.create_task(self.receive_ssh_data())

        except paramiko.AuthenticationException:
            await self.send_text_data('认证失败。\n')
            logger.error('SSH 认证失败: 主机ID=%s', self.host_id)
            await self.close()
        except paramiko.SSHException as e:
            await self.send_text_data(f'SSH 错误: {str(e)}\n')
            logger.error('SSH 错误: %s (主机ID=%s)', str(e), self.host_id)
            await self.close()
        except Exception as e:
            await self.send_text_data(f'意外错误: {str(e)}\n')
            logger.error('意外错误: %s (主机ID=%s)', str(e), self.host_id)
            await self.close()

    async def receive_ssh_data(self):
        """
        持续从 SSH 通道读取数据并将其发送到 WebSocket。
        同时检测 shell 提示符和处理自动补全的内容。
        """
        try:
            buffer = ''
            while True:
                if self.ssh_channel.recv_ready():
                    # 接收数据
                    data = self.ssh_channel.recv(1024).decode('utf-8', errors='replace')
                    await self.send(text_data=data)

                    # 累积缓冲区数据
                    buffer += data

                    # 检测 shell 提示符
                    if self.shell_prompt_regex.search(buffer):
                        self.in_shell_prompt = True
                        buffer = ''  # 重置缓冲区

                        # 如果之前在编辑器中，现在退出了编辑器
                        if self.in_editor:
                            self.in_editor = False
                    else:
                        # 继续累积缓冲区
                        pass

                    # 更新命令缓冲区
                    await self.update_command_buffer_from_ssh(data)
                await asyncio.sleep(0.1)
        except Exception as e:
            await self.send_text_data(f'连接错误: {str(e)}\n')
            logger.error('SSH 数据接收错误: %s (主机ID=%s)', str(e), self.host_id)
            await self.close()

    async def update_command_buffer_from_ssh(self, data):
        """
        从 SSH 服务器返回的数据中更新命令缓冲区，处理自动补全的内容。
        """
        if not data:
            return

        if self.in_editor:
            # 在编辑器中，不记录任何输出
            return

        # 如果之前检测到命令已执行，则重置标志
        if self.is_command_executed:
            self.is_command_executed = False
            return

        # 处理自动补全的情况
        # 检查是否有自动补全的内容
        # 这里假设自动补全的内容紧跟在用户输入后返回
        if self.last_input_char and ord(self.last_input_char) == 9:  # 上一次输入是 Tab 键
            # 移除 ANSI 转义序列
            ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
            clean_data = ansi_escape.sub('', data)

            # 只保留可打印字符
            printable_data = ''.join(filter(lambda x: x.isprintable(), clean_data))

            # 添加到命令缓冲区
            self.command_buffer += printable_data

    async def send_text_data(self, message):
        """
        辅助函数，用于向 WebSocket 发送消息。
        """
        await self.send(text_data=message)
        logger.debug('发送到 WebSocket 的消息: %s', message.strip())



# 文件管理相关的视图
class FileListView(APIView):
    """
    获取服务器上的文件列表，包括文件的所有者和所属组信息，以及格式化的文件大小。
    """

    def get(self, request, host_id):
        # 获取主机和凭据
        host = get_object_or_404(Host, id=host_id)
        credential = get_object_or_404(Credential, id=host.account_type.id)
        try:
            # 获取路径参数，默认为根目录 '/'
            path = request.GET.get('path', '/')
            # 可以添加安全检查，防止目录遍历攻击
            # if not is_safe_path(path):
            #     return Response({'error': '非法路径'}, status=status.HTTP_400_BAD_REQUEST)

            # 建立 SSH 和 SFTP 连接
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 根据凭据类型进行连接
            if credential.type == '密码':
                ssh_client.connect(
                    host.network,
                    port=host.port,
                    username=credential.account,
                    password=credential.password,
                    timeout=10
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
                    timeout=10
                )
            else:
                return Response({'error': '不支持的凭据类型'}, status=status.HTTP_400_BAD_REQUEST)

            # 打开 SFTP 客户端
            sftp_client = ssh_client.open_sftp()

            # 确定当前路径，规范化路径
            if not os.path.isabs(path):
                # 如果路径不是绝对路径，则获取用户的 home 目录
                home_path = sftp_client.normalize('.')
                path = os.path.join(home_path, path)
            else:
                # 规范化绝对路径
                path = sftp_client.normalize(path)

            # 获取指定路径下的文件列表
            file_list = sftp_client.listdir_attr(path)

            # 定义格式化文件大小的函数
            def format_size(size):
                units = ['B', 'KB', 'MB', 'GB', 'TB']
                index = 0
                while size >= 1024 and index < len(units) - 1:
                    size /= 1024
                    index += 1
                return f"{size:.2f} {units[index]}"

            # 初始化集合，用于存储所有的用户 ID（UID）和组 ID（GID）
            uids = set()
            gids = set()

            # 从文件属性中提取所有的 UID 和 GID
            for file_attr in file_list:
                uids.add(file_attr.st_uid)
                gids.add(file_attr.st_gid)

            # 创建 UID 到用户名的映射
            uid_to_user = {}
            if uids:
                # 构建命令，使用 getent passwd 获取用户名
                uid_str = ' '.join(str(uid) for uid in uids)
                passwd_cmd = f'getent passwd {uid_str}'
                # 执行命令
                stdin, stdout, stderr = ssh_client.exec_command(passwd_cmd)
                passwd_output = stdout.read().decode('utf-8')
                # 解析命令输出，建立 UID 到用户名的映射
                for line in passwd_output.strip().split('\n'):
                    if line:
                        parts = line.split(':')
                        if len(parts) >= 3:
                            username = parts[0]  # 用户名
                            uid = int(parts[2])   # UID
                            uid_to_user[uid] = username

            # 创建 GID 到组名的映射
            gid_to_group = {}
            if gids:
                # 构建命令，使用 getent group 获取组名
                gid_str = ' '.join(str(gid) for gid in gids)
                group_cmd = f'getent group {gid_str}'
                # 执行命令
                stdin, stdout, stderr = ssh_client.exec_command(group_cmd)
                group_output = stdout.read().decode('utf-8')
                # 解析命令输出，建立 GID 到组名的映射
                for line in group_output.strip().split('\n'):
                    if line:
                        parts = line.split(':')
                        if len(parts) >= 3:
                            groupname = parts[0]  # 组名
                            gid = int(parts[2])    # GID
                            gid_to_group[gid] = groupname

            # 构建文件信息列表
            files = []
            for file_attr in file_list:
                permissions = stat.filemode(file_attr.st_mode)
                modify_time = datetime.datetime.fromtimestamp(
                    file_attr.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                is_directory = stat.S_ISDIR(file_attr.st_mode)

                # 获取文件的所有者和所属组名称
                uid = file_attr.st_uid
                gid = file_attr.st_gid
                owner = uid_to_user.get(uid, str(uid))  # 如果用户名未找到，使用 UID 的字符串形式
                group = gid_to_group.get(gid, str(gid))  # 如果组名未找到，使用 GID 的字符串形式

                # 格式化文件大小
                size = format_size(file_attr.st_size)

                files.append({
                    'filename': file_attr.filename,
                    'size': size,
                    'permissions': permissions,
                    'modify_time': modify_time,
                    'is_directory': is_directory,
                    'owner': owner,
                    'group': group,
                })

            # 关闭连接
            sftp_client.close()
            ssh_client.close()

            # 返回文件列表和当前路径
            return Response({'files': files, 'current_path': path})
        except Exception as e:
            logger.error('获取文件列表错误: %s (主机ID=%s)', str(e), host_id)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FileUploadView(APIView):
    """
    上传文件到服务器。
    """

    def post(self, request, host_id):
        # 获取上传的文件
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': '未找到文件'}, status=status.HTTP_400_BAD_REQUEST)
        # 获取路径参数
        path = request.POST.get('path', '.')
        # 获取主机和凭据
        host = get_object_or_404(Host, id=host_id)
        credential = get_object_or_404(Credential, id=host.account_type.id)
        try:
            # 建立 SSH 和 SFTP 连接
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if credential.type == '密码':
                ssh_client.connect(
                    host.network,
                    port=host.port,
                    username=credential.account,
                    password=credential.password,
                    timeout=10
                )
            elif credential.type == '密钥':
                key_file = io.StringIO(credential.key)
                pkey = paramiko.RSAKey.from_private_key(key_file, password=credential.key_password)
                ssh_client.connect(
                    host.network,
                    port=host.port,
                    username=credential.account,
                    pkey=pkey,
                    timeout=10
                )
            else:
                return Response({'error': '不支持的凭据类型'}, status=status.HTTP_400_BAD_REQUEST)

            sftp_client = ssh_client.open_sftp()

            # 确定上传路径
            if path == '~':
                # 获取用户的home目录
                path = sftp_client.normalize('.')

            # 上传文件到指定目录
            remote_file_path = os.path.join(path, uploaded_file.name)
            sftp_client.putfo(uploaded_file.file, remote_file_path)

            sftp_client.close()
            ssh_client.close()
            return Response({'message': '文件上传成功'})
        except Exception as e:
            logger.error('文件上传错误: %s (主机ID=%s)', str(e), host_id)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FileDownloadView(APIView):
    """
    从服务器下载文件。
    """

    def get(self, request, host_id):
        filename = request.GET.get('filename')
        if not filename:
            return Response({'error': '未指定文件名'}, status=status.HTTP_400_BAD_REQUEST)
        # 获取路径参数
        path = request.GET.get('path', '.')
        # 获取主机和凭据
        host = get_object_or_404(Host, id=host_id)
        credential = get_object_or_404(Credential, id=host.account_type.id)
        try:
            # 建立 SSH 和 SFTP 连接
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if credential.type == '密码':
                ssh_client.connect(
                    host.network,
                    port=host.port,
                    username=credential.account,
                    password=credential.password,
                    timeout=10
                )
            elif credential.type == '密钥':
                key_file = io.StringIO(credential.key)
                pkey = paramiko.RSAKey.from_private_key(key_file, password=credential.key_password)
                ssh_client.connect(
                    host.network,
                    port=host.port,
                    username=credential.account,
                    pkey=pkey,
                    timeout=10
                )
            else:
                return Response({'error': '不支持的凭据类型'}, status=status.HTTP_400_BAD_REQUEST)

            sftp_client = ssh_client.open_sftp()

            # 确定文件路径
            if path == '~':
                # 获取用户的home目录
                path = sftp_client.normalize('.')

            remote_file_path = os.path.join(path, filename)

            # 下载文件
            file_obj = io.BytesIO()
            sftp_client.getfo(remote_file_path, file_obj)
            file_obj.seek(0)

            sftp_client.close()
            ssh_client.close()

            response = FileResponse(file_obj, filename=filename)
            return response
        except Exception as e:
            logger.error('文件下载错误: %s (主机ID=%s)', str(e), host_id)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FileDeleteView(APIView):
    """
    删除服务器上的文件。
    """

    def delete(self, request, host_id):
        filename = request.GET.get('filename')
        if not filename:
            return Response({'error': '未指定文件名'}, status=status.HTTP_400_BAD_REQUEST)
        # 获取路径参数
        path = request.GET.get('path', '.')
        # 获取主机和凭据
        host = get_object_or_404(Host, id=host_id)
        credential = get_object_or_404(Credential, id=host.account_type.id)
        try:
            # 建立 SSH 和 SFTP 连接
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if credential.type == '密码':
                ssh_client.connect(
                    host.network,
                    port=host.port,
                    username=credential.account,
                    password=credential.password,
                    timeout=10
                )
            elif credential.type == '密钥':
                key_file = io.StringIO(credential.key)
                pkey = paramiko.RSAKey.from_private_key(key_file, password=credential.key_password)
                ssh_client.connect(
                    host.network,
                    port=host.port,
                    username=credential.account,
                    pkey=pkey,
                    timeout=10
                )
            else:
                return Response({'error': '不支持的凭据类型'}, status=status.HTTP_400_BAD_REQUEST)

            sftp_client = ssh_client.open_sftp()

            # 确定文件路径
            if path == '~':
                # 获取用户的home目录
                path = sftp_client.normalize('.')

            remote_file_path = os.path.join(path, filename)

            # 判断是文件还是目录
            file_attr = sftp_client.lstat(remote_file_path)
            if stat.S_ISDIR(file_attr.st_mode):
                # 如果是目录，使用 rmdir 删除（仅能删除空目录）
                sftp_client.rmdir(remote_file_path)
            else:
                # 如果是文件，删除文件
                sftp_client.remove(remote_file_path)

            sftp_client.close()
            ssh_client.close()
            return Response({'message': '文件删除成功'})
        except Exception as e:
            logger.error('文件删除错误: %s (主机ID=%s)', str(e), host_id)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
