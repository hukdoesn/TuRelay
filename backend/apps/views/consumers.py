import paramiko
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404
from apps.models import Host, Credential
from asgiref.sync import sync_to_async
import io
import logging
import json

# 获取日志记录器实例
logger = logging.getLogger('log')

class SSHConsumer(AsyncWebsocketConsumer):
    """
    SSHConsumer 处理 WebSocket 连接，以使用 Paramiko 根据存储在数据库中的主机凭据建立 SSH 会话。
    """

    async def connect(self):
        self.host_id = self.scope['url_route']['kwargs']['host_id']  # 从 URL 中获取主机 ID

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
                self.ssh_channel.send(text_data)  # 通过 SSH 通道发送数据到服务器
        except (json.JSONDecodeError, TypeError):
            # 如果数据不是 JSON 或不能迭代，则视为普通的命令输入
            if hasattr(self, 'ssh_channel'):
                self.ssh_channel.send(text_data)

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
        """
        try:
            while True:
                if self.ssh_channel.recv_ready():
                    # 处理接收到的数据，使用 'replace' 以确保不会因无法解码的字符导致崩溃
                    data = self.ssh_channel.recv(1024).decode('utf-8', errors='replace')
                    await self.send(text_data=data)
                await asyncio.sleep(0.1)
        except Exception as e:
            await self.send_text_data(f'连接错误: {str(e)}\n')
            logger.error('SSH 数据接收错误: %s (主机ID=%s)', str(e), self.host_id)
            await self.close()

    async def send_text_data(self, message):
        """
        辅助函数，用于向 WebSocket 发送消息。
        """
        await self.send(text_data=message)
        logger.debug('发送到 WebSocket 的消息: %s', message.strip())
        
