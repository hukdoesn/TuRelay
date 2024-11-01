import paramiko
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404
from apps.models import Host, Credential, Token, User, CommandLog, CommandAlert
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
from apps.alert_utils.command_alert_handler import check_command_alert
import socket

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
        self.in_history_search = False  # 标记是否在历史搜索模式
        self.history_search_buffer = ''  # 历史搜索缓冲区
        self.actual_command = ''  # 存储实际要执行的命令
        self.in_escape_sequence = False  # 标记是否在处理转义序列
        self.escape_buffer = ''  # 存储转义序列
        self.last_activity = None  # 记录最后活动时间
        self.timeout_task = None   # 存储超时检查任务
        self.TIMEOUT_SECONDS = 600  # 设置10分钟超时 (60秒 * 10)

        # 定义一个正则表达式来匹配 shell 提示符
        self.shell_prompt_regex = re.compile(r'[^@]+@[^:]+:[^\$#]*[#$]\s?$')

    async def connect(self):
        # 从 URL 中获取主机 ID
        self.host_id = self.scope['url_route']['kwargs']['host_id']
        logger.debug(f"尝试连接到主机ID: {self.host_id}")

        # 从查询参数中获取 token
        query_string = self.scope['query_string'].decode('utf-8')
        query_params = urllib.parse.parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if not token:
            logger.warning("连接失败: 未提供令牌")
            await self.send_text_data('认证失败：未提供令牌。\n')
            await self.close()
            return

        # 验证令牌并获取用户名
        try:
            token_obj = await sync_to_async(Token.objects.get)(token=token)
            self.user = await sync_to_async(User.objects.get)(id=token_obj.user_id)
            self.username = self.user.username
            logger.debug(f"用户 {self.username} 认证成功")
        except Token.DoesNotExist:
            logger.warning(f"连接失败: 无效的令牌 {token}")
            await self.send_text_data('认证失败：无效的令牌。\n')
            await self.close()
            return
        except User.DoesNotExist:
            logger.warning(f"连接失败: 用户不存在 (令牌: {token})")
            await self.send_text_data('认证失败：用户不存在。\n')
            await self.close()
            return

        # 异步获取主机和凭据信息
        self.host = await sync_to_async(get_object_or_404)(Host, id=self.host_id)
        self.credential_id = await sync_to_async(lambda: self.host.account_type.id)()
        self.credential = await sync_to_async(get_object_or_404)(Credential, id=self.credential_id)
        logger.debug(f"获取到主机信息: {self.host.name}, 凭据ID: {self.credential_id}")

        # 接受 WebSocket 连接
        await self.accept()
        logger.debug(f"WebSocket 连接已接受")

        # 初始化最后活动时间
        self.last_activity = datetime.datetime.now()
        
        # 启动超时检查任务
        self.timeout_task = asyncio.create_task(self.check_timeout())
        
        # 初始化 SSH 连接
        await self.establish_ssh_connection()

    async def disconnect(self, close_code):
        # 取消超时检查任务
        if self.timeout_task:
            self.timeout_task.cancel()
            try:
                await self.timeout_task
            except asyncio.CancelledError:
                pass

        # 关闭 SSH 连接
        if hasattr(self, 'ssh_client'):
            self.ssh_client.close()

        logger.info(f"WebSocket 连接已断开 (close_code={close_code})")

    async def receive(self, text_data):
        # 更新最后活动时间
        self.last_activity = datetime.datetime.now()
        
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
                logger.debug(f"未检测到 shell 提示符,跳过命令记录")
                continue

            if self.in_editor:
                logger.debug(f"在编辑器中,跳过命令记录")
                continue

            # 处理特殊按键
            char_code = ord(char)
            
            # 处理 Ctrl+C (ASCII 0x03)
            if char_code == 3:
                logger.debug("检测到 Ctrl+C，清空命令缓冲区")
                self.command_buffer = ''
                self.actual_command = ''
                self.in_history_search = False
                self.history_search_buffer = ''
                continue

            # 处理 Ctrl+R (ASCII 0x12)
            if char_code == 18:
                logger.debug("检测到 Ctrl+R，进入历史搜索模式")
                self.in_history_search = True
                self.history_search_buffer = ''
                continue

            # 处理方向键和其他转义序列
            if char == '\x1b':  # ESC
                self.in_escape_sequence = True
                self.escape_buffer = char
                continue
                
            if self.in_escape_sequence:
                self.escape_buffer += char
                # 检查是否是完整的转义序列
                if self.escape_buffer == '\x1b[A':  # 上方向键
                    logger.debug("检测到上方向键")
                    self.in_escape_sequence = False
                    self.escape_buffer = ''
                    continue
                elif self.escape_buffer == '\x1b[B':  # 下方向键
                    logger.debug("检测到下方向键")
                    self.in_escape_sequence = False
                    self.escape_buffer = ''
                    continue
                elif len(self.escape_buffer) >= 3:  # 其他转义序列
                    self.in_escape_sequence = False
                    self.escape_buffer = ''
                continue

            # 处理回车键
            if char in ('\r', '\n'):
                if self.actual_command:  # 如果有实际命令（从历史记录或方向键获取），使用它
                    self.command_buffer = self.actual_command
                    self.actual_command = ''  # 重置实际命令
                
                if self.command_buffer.strip():  # 只有当命令不为空时才记录
                    # 清理命令中的提示符和搜索前缀
                    clean_command = re.sub(r'^\[.*?\]#\s*', '', self.command_buffer.strip())
                    clean_command = re.sub(r'^.*\(reverse-i-search\).*?: ', '', clean_command)
                    if clean_command:  # 确保清理后的命令不为空
                        logger.info(f"检测到命令执行: {clean_command}")
                        self.command_buffer = clean_command
                        await self.save_command_log()
                        await self.check_command_alert()
                
                self.command_buffer = ''
                self.in_shell_prompt = False
                self.in_history_search = False
                self.history_search_buffer = ''
                continue

            # 处理退格键
            if char == '\x7f':  # Backspace
                if self.in_history_search:
                    self.history_search_buffer = self.history_search_buffer[:-1]
                else:
                    self.command_buffer = self.command_buffer[:-1]
                continue

            # 处理Tab键
            if char_code == 9:
                logger.debug("检测到 Tab 键,等待自动补全")
                continue

            # 处理普通字符输入
            if self.in_history_search:
                self.history_search_buffer += char
            else:
                self.command_buffer += char

    async def save_command_log(self):
        """
        保存执行的命令到 CommandLog 表中。
        """
        command = self.command_buffer.strip()
        if command:
            if command.startswith('vi ') or command.startswith('vim '):
                self.in_editor = True
                command_to_save = command
                logger.info(f"进入编辑器模式: {command_to_save}")
            else:
                command_to_save = command

            await sync_to_async(CommandLog.objects.create)(
                username=self.username,
                command=command_to_save,
                hosts=self.host.name,
                network=self.host.network,
                credential=self.credential.account,
                create_time=datetime.datetime.now()
            )
            logger.info(f'命令已记录: 用户={self.username}, 主机={self.host.name}, 命令={command_to_save}')

    async def check_command_alert(self):
        command = self.command_buffer.strip()
        if command:
            logger.debug(f"开始检查命令告警: 用户={self.username}, 主机={self.host.name}, 命令={command}")
            alert_result = await check_command_alert(self.host.id, command, self.username)
            if alert_result:
                logger.warning(f'命令告警触发: 用户={self.username}, 主机={self.host.name}, 命令={command}')
                # 告警通知已经在 check_command_alert 函数中发送
            else:
                logger.debug(f'命令未触发告警: 用户={self.username}, 主机={self.host.name}, 命令={command}')

    async def establish_ssh_connection(self):
        """
        使用主机凭据建立 SSH 连接。
        """
        logger.debug(f"开始建立 SSH 连接到主机: {self.host.name}")
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # 设置传输层参数
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.host.network, self.host.port))
            
            transport = paramiko.Transport(sock)
            transport.set_keepalive(30)  # 30秒发送一次心跳
            transport.window_size = 2147483647  # 设置最大窗口大小
            transport.packetizer.REKEY_BYTES = pow(2, 40)  # 重新生成密钥的字节数
            transport.packetizer.REKEY_PACKETS = pow(2, 40)  # 重新生成密钥的包数量

            if self.credential.type == '密码':
                logger.debug(f"使用密码认证连接到主机: {self.host.network}")
                transport.connect(username=self.credential.account, password=self.credential.password)
            elif self.credential.type == '密钥':
                logger.debug(f"使用密钥认证接到主机: {self.host.network}")
                key_file = io.StringIO(self.credential.key)
                pkey = paramiko.RSAKey.from_private_key(key_file, password=self.credential.key_password)
                transport.connect(username=self.credential.account, pkey=pkey)
            else:
                logger.error(f"不支持的凭据类型: {self.credential.type}")
                await self.send_text_data('不支持的凭据类型。\n')
                await self.close()
                return

            self.ssh_client._transport = transport
            logger.debug(f"SSH 连接成功建立")

            # 使用更大的终端大小启动 shell
            self.ssh_channel = self.ssh_client.invoke_shell(
                term='xterm-256color',
                width=500,
                height=2000,
                width_pixels=0,
                height_pixels=0
            )
            self.ssh_channel.settimeout(0)
            self.ssh_channel.set_combine_stderr(True)  # 合并标准错误到标准输出

            # 开始从 SSH 服务器读取数据
            asyncio.create_task(self.receive_ssh_data())

        except paramiko.AuthenticationException:
            logger.error(f'SSH 认证失败: 主机ID={self.host_id}')
            await self.send_text_data('认证失败。\n')
            await self.close()
        except paramiko.SSHException as e:
            logger.error(f'SSH 错误: {str(e)} (主机ID={self.host_id})')
            await self.send_text_data(f'SSH 错误: {str(e)}\n')
            await self.close()
        except Exception as e:
            logger.error(f'意外错误: {str(e)} (主机ID={self.host_id})')
            await self.send_text_data(f'意外错误: {str(e)}\n')
            await self.close()

    async def receive_ssh_data(self):
        """
        持续从 SSH 通道读取数据并将其发送到 WebSocket。
        同时检测 shell 提示符和处理自动补全的内容。
        """
        try:
            buffer = ''
            BUFFER_SIZE = 1024 * 1024  # 增加到 1MB
            
            while True:
                # 检查是否有数据可读
                if self.ssh_channel.recv_ready():
                    try:
                        data = self.ssh_channel.recv(BUFFER_SIZE)
                        if not data:
                            # 连接已关闭
                            break
                            
                        # 解码并发送数据
                        text = data.decode('utf-8', errors='replace')
                        await self.send(text_data=text)
                        
                        # 更新buffer用于检测提示符
                        buffer += text
                        if len(buffer) > 4096:
                            buffer = buffer[-4096:]
                            
                        # 检测 shell 提示符
                        if self.shell_prompt_regex.search(buffer):
                            self.in_shell_prompt = True
                            buffer = ''
                            if self.in_editor:
                                self.in_editor = False
                                
                        # 更新命令缓冲区
                        await self.update_command_buffer_from_ssh(text)
                            
                    except UnicodeDecodeError:
                        logger.warning("解码 SSH 数据时出错，跳过此部分数")
                        continue
                else:
                    # 没有数据时短暂休眠
                    await asyncio.sleep(0.001)
                
        except Exception as e:
            await self.send_text_data(f'连接错误: {str(e)}\n')
            logger.error('SSH 数据接收错误: %s (主机ID=%s)', str(e), self.host_id)
            await self.close()

    async def update_command_buffer_from_ssh(self, data):
        """
        从 SSH 服务器返回的数据中更新命令缓冲区，处理自动补全的内容。
        """
        if not data or self.in_editor:
            return

        # 如果之前检测到命令已执行，则置标志
        if self.is_command_executed:
            self.is_command_executed = False
            return

        # 移除 ANSI 转义序列
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        clean_data = ansi_escape.sub('', data)

        # 检查是否包含历史命令的完整输出
        if self.in_history_search:
            # 尝试从输出中提取完整的命令
            # 使用正则表达式匹配 reverse-i-search 后的实际命令
            search_pattern = r'\(reverse-i-search\).*?: (.+?)(?=\r|\n|$)'
            matches = re.findall(search_pattern, clean_data)
            if matches:
                # 取最后一个匹配的命令
                self.actual_command = matches[-1].strip()
                logger.debug(f"从历史搜索中获取到完整命令: {self.actual_command}")
                return
        
        # 检查是否是方向键历史命令
        elif '\x1b[A' in data or '\x1b[B' in data:  # 上下方向键
            lines = clean_data.splitlines()
            for line in lines:
                if line.strip():
                    # 清理命令中的提示符
                    clean_line = re.sub(r'^\[.*?\]#\s*', '', line.strip())
                    if clean_line:
                        self.actual_command = clean_line
                        logger.debug(f"从方向键历史中获取到完整命令: {self.actual_command}")
                    break

        # 处理自动补全的情况
        elif self.last_input_char and ord(self.last_input_char) == 9:  # Tab 键
            # 只保留可打印字符
            printable_data = ''.join(filter(lambda x: x.isprintable(), clean_data))
            self.command_buffer += printable_data

    async def send_text_data(self, message):
        """
        辅助函数，用于向 WebSocket 发送消息。
        """
        await self.send(text_data=message)
        logger.debug('发送到 WebSocket 的消息: %s', message.strip())

    async def check_timeout(self):
        """
        定期检查连接是否超时
        """
        try:
            while True:
                await asyncio.sleep(30)  # 每30秒检查一次
                
                if self.last_activity is None:
                    continue
                    
                elapsed = datetime.datetime.now() - self.last_activity
                if elapsed.total_seconds() > self.TIMEOUT_SECONDS:
                    logger.info(f"SSH 连接超时 ({self.TIMEOUT_SECONDS}秒无活动)")
                    # 发送超时消息给客户端
                    await self.send(text_data=json.dumps({
                        'type': 'timeout',
                        'message': f'连接已超时 ({self.TIMEOUT_SECONDS//60}分钟无活动)'
                    }))
                    # 关闭连接
                    await self.close(code=4000)  # 使用自定义关闭代码4000表示超时
                    break
                    
        except asyncio.CancelledError:
            # 任务被取消时正常退出
            pass
        except Exception as e:
            logger.error(f"超时检查任务出错: {str(e)}")

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

            # 定义式化文件大小的函数
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

            # 创建 UID 到用户名的映
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
                # 获取用的home目录
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
                # 如果是目录，使用 rmdir 删除（仅删除空目录）
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
