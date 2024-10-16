import json
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.models import Host, Credential
from .guacamole import GuacamoleClient
from asgiref.sync import sync_to_async
import asyncio

class GuacamoleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.host_id = self.scope['url_route']['kwargs']['host_id']
        
        # 使用异步方式获取主机信息和凭据
        host = await self.get_host(self.host_id)
        credential = await self.get_credential(host)

        # 实例化 GuacamoleClient 并连接
        self.guac_client = GuacamoleClient()
        self.connection_id = self.guac_client.connect(
            protocol='rdp',
            hostname=host.network,
            username=credential.account, 
            password=credential.password,
            port=host.port,
        )

        await self.accept()

        # 启动任务来转发 guacd 到 WebSocket 的数据
        self.guac_to_web_task = asyncio.create_task(self.guac_to_web())

    async def disconnect(self, close_code):
        if self.guac_client:
            self.guac_client.disconnect()
        if hasattr(self, 'guac_to_web_task'):
            self.guac_to_web_task.cancel()

    async def receive(self, text_data):
        # 将前端发送的数据转发给 guacd
        if self.guac_client and self.guac_client.connected:
            self.guac_client.send(text_data.encode('utf-8'))

    async def guac_to_web(self):
        # 持续从 guacd 读取数据并发送给前端
        while True:
            data = await asyncio.get_event_loop().run_in_executor(None, self.guac_client.receive)
            if data:
                await self.send(text_data=data.decode('utf-8'))
            else:
                break

    @sync_to_async
    def get_host(self, host_id):
        return Host.objects.get(id=host_id)

    @sync_to_async
    def get_credential(self, host):
        return Credential.objects.get(id=host.account_type_id)
