import paramiko
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404
from apps.models import Host, Credential, Token, User, CommandLog, CommandAlert
from asgiref.sync import sync_to_async
import io
import logging
import json
import re
from apps.alert_utils.command_alert_handler import check_command_alert
import socket
import datetime
import urllib

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
                    # 清命令中的提示符和搜索前缀
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
            logger.error(f'意外错误: {str(e)} (机ID={self.host_id})')
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

        # 检否包含历史命令的完整输出
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
                    # 清理命令中的示符
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
