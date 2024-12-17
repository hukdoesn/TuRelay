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
    SSH WebSocket 消费者类
    
    主要功能:
    1. 建立和管理 SSH 连接
    2. 处理 WebSocket 消息
    3. 记录命令执行日志
    4. 检测命令告警
    5. 管理会话超时
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 命令处理相关组件
        self.command_handler = CommandHandler()      # 命令处理器
        self.shell_detector = ShellPromptDetector()  # Shell提示符检测器
        
        # 命令状态标记
        self.last_input_char = None        # 最后输入的字符
        self.command_buffer = ''           # 命令缓冲区
        self.is_command_executed = False   # 命令是否已执行
        self.in_shell_prompt = False       # 是否在shell提示符状态
        self.in_editor = False             # 是否在编辑器模式
        self.in_history_search = False     # 是否在历史搜索模式
        self.history_search_buffer = ''    # 历史搜索缓冲区
        self.actual_command = ''           # 实际要执行的命令
        
        # 转义序列处理
        self.in_escape_sequence = False    # 是否在处理转义序列
        self.escape_buffer = ''            # 转义序列缓冲区
        
        # 会话管理
        self.last_activity = None          # 最后活动时间
        self.timeout_task = None           # 超时检查任务
        self.TIMEOUT_SECONDS = 3600        # 超时时间(1小时)

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
        """
        处理接收到的WebSocket消息
        
        1. 命令记录消息
        2. 终端大小调整消息
        3. 普通文本输入
        
        Args:
            text_data: WebSocket消息内容
        """
        # 更新最后活动时间
        self.last_activity = datetime.datetime.now()
        
        try:
            # 尝试解析JSON数据
            try:
                data = json.loads(text_data)
                if isinstance(data, dict):
                    if 'type' in data and data['type'] == 'command':
                        # 处理命令记录
                        await self.handle_command_record(data['command'])
                        return
                    elif 'cols' in data and 'rows' in data:
                        # 处理终端大小调整
                        self.ssh_channel.resize_pty(width=data['cols'], height=data['rows'])
                        return
            except json.JSONDecodeError:
                pass

            # 处理普通文本输入
            if hasattr(self, 'ssh_channel'):
                self.ssh_channel.send(text_data)

        except Exception as e:
            logger.error(f"处理WebSocket数据时出错: {str(e)}")
            await self.close()

    async def handle_command_record(self, command):
        """
        处理命令记录
        
        1. 清理命令文本
        2. 记录到数据库
        3. 检查命令告警
        4. 处理编辑器模式
        
        Args:
            command: 原始命令文本
        """
        try:
            # 检查是否在编辑器中
            if self.in_editor:
                return

            # 清理命令
            clean_command = self.command_handler.clean_command(command)
            if clean_command:
                # 记录命令到数据库
                await self.save_command_log(clean_command)
                # 检查命令告警
                await self.check_command_alert(clean_command)

                # 检查是否进入编辑器
                if clean_command.startswith(('vi ', 'vim ')):
                    self.in_editor = True
                    logger.debug(f"进入编辑器模式: {clean_command}")

        except Exception as e:
            logger.error(f"记录命令时出错: {str(e)}")

    async def process_input(self, data):
        """处理输入数据"""
        if self.in_editor:
            return

        for char in data:
            # 处理特殊按键
            char_code = ord(char)
            
            # 处理 Ctrl+C
            if char_code == 3:
                self.command_buffer = ''
                self.actual_command = ''
                self.in_history_search = False
                self.history_search_buffer = ''
                continue

            # 处理回车键
            if char in ('\r', '\n'):
                if self.actual_command:
                    self.command_buffer = self.actual_command
                    self.actual_command = ''

                if self.command_buffer.strip():
                    clean_command = self.command_handler.clean_command(self.command_buffer)
                    if clean_command:
                        await self.save_command_log(clean_command)
                        await self.check_command_alert(clean_command)

                self.command_buffer = ''
                self.in_shell_prompt = False
                self.in_history_search = False
                self.history_search_buffer = ''
                continue

            # 处理其他输入
            if not self.in_shell_prompt:
                continue

            # 更新命令缓冲区
            if char == '\x7f':  # Backspace
                if self.in_history_search:
                    self.history_search_buffer = self.history_search_buffer[:-1]
                else:
                    self.command_buffer = self.command_buffer[:-1]
            else:
                if self.in_history_search:
                    self.history_search_buffer += char
                else:
                    self.command_buffer += char

    async def save_command_log(self, command):
        """
        保存执行的命令到 CommandLog 表中。
        """
        await sync_to_async(CommandLog.objects.create)(
            username=self.username,
            command=command,
            hosts=self.host.name,
            network=self.host.network,
            credential=self.credential.name,
            create_time=datetime.datetime.now()
        )
        logger.info(f'命令已记录: 用户={self.username}, 主机={self.host.name}, 命令={command}')

    async def check_command_alert(self, command):
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
                        if self.shell_detector.detect_prompt(text):
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

class CommandHandler:
    """
    命令处理器类
    1. 清理命令文本
    2. 移除ANSI转义序列
    3. 移除shell提示符
    """
    
    def __init__(self):
        # Shell提示符正则表达式
        self.shell_prompt_regex = re.compile(r'[^@]+@[^:]+:[^\$#]*[#$]\s?$')

    def clean_command(self, command):
        """
        清理命令文本
        1. 移除ANSI转义序列
        2. 移除各种shell提示符
        3. 移除前后空白字符
        
        Args:
            command: 原始命令文本
            
        Returns:
            清理后的命令文本
        """
        # 移除ANSI转义序列
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        clean_cmd = ansi_escape.sub('', command)
        
        # 移除shell提示符
        clean_cmd = re.sub(r'^\[.*?\]#\s*', '', clean_cmd)                # 移除方括号类型提示符
        clean_cmd = re.sub(r'^.*\(reverse-i-search\).*?: ', '', clean_cmd) # 移除历史搜索提示符
        clean_cmd = re.sub(r'^.*?[@:].*?[#$]\s*', '', clean_cmd)          # 移除常见的shell提示符格式
        
        # 移除前后空白字符
        clean_cmd = clean_cmd.strip()
        
        return clean_cmd

class ShellPromptDetector:
    """
    Shell提示符检测器类
    1. 检测shell提示符
    2. 管理检测缓冲区
    """
    
    def __init__(self):
        # Shell提示符匹配模式
        self.prompt_pattern = re.compile(r'[^@]+@[^:]+:[^\$#]*[#$]\s?$')
        self.buffer = ''  # 检测缓冲区

    def detect_prompt(self, data):
        """
        检测shell提示符
        
        Args:
            data: 要检测的文本数据
            
        Returns:
            bool: 是否检测到提示符
        """
        # 更新缓冲区
        self.buffer += data
        # 保持缓冲区大小在合理范围
        if len(self.buffer) > 4096:
            self.buffer = self.buffer[-4096:]
        
        # 检查是否匹配提示符模式
        return bool(self.prompt_pattern.search(self.buffer))

    def reset(self):
        """重置检测缓冲区"""
        self.buffer = ''
