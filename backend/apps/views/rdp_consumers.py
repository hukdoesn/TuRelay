import json
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.models import Host, Credential
from django.shortcuts import get_object_or_404
from guacamole import GuacamoleClient  # Replace with actual library for guacd interaction
import logging

logger = logging.getLogger('log')

class RDPConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.host_id = self.scope['url_route']['kwargs']['host_id']
        self.host = await sync_to_async(get_object_or_404)(Host, id=self.host_id)
        self.credential = await sync_to_async(get_object_or_404)(Credential, id=self.host.account_type.id)

        # Strip symbols from host ID
        self.host_id_cleaned = self.host_id.replace('-', '')

        # Establish the connection to guacd
        try:
            self.guac_client = GuacamoleClient('172.17.102.69', 4822)
            self.guac_client.connect(
                protocol='rdp',
                hostname=self.host.network,
                port=self.host.port,
                username=self.credential.account,
                password=self.credential.password
            )
            await self.accept()

            # Start listening for messages
            await self.receive_rdp_data()

        except Exception as e:
            logger.error(f'RDP 连接失败: {str(e)}')
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'guac_client'):
            self.guac_client.disconnect()

    async def receive(self, text_data):
        # Relay data from WebSocket to guacd
        if hasattr(self, 'guac_client'):
            self.guac_client.send(text_data)

    async def receive_rdp_data(self):
        while True:
            if hasattr(self, 'guac_client'):
                data = self.guac_client.receive()
                await self.send(data)
