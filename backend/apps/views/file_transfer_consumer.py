import json
import urllib.parse
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
import asyncio
from channels.db import database_sync_to_async
from apps.models import Token, User
import logging

logger = logging.getLogger('log')

class FileTransferConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 从URL获取传输ID
        self.transfer_id = self.scope['url_route']['kwargs']['transfer_id']
        
        # 验证token
        query_string = self.scope['query_string'].decode('utf-8')
        query_params = urllib.parse.parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if not token:
            await self.close()
            return

        try:
            token_obj = await database_sync_to_async(Token.objects.get)(token=token)
            self.user = await database_sync_to_async(User.objects.get)(id=token_obj.user_id)
        except (Token.DoesNotExist, User.DoesNotExist):
            await self.close()
            return

        await self.accept()
        
        # 设置group name
        self.group_name = f"file_transfer_{self.transfer_id}"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def transfer_progress(self, event):
        """发送传输进度信息到WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'progress',
            'filename': event['filename'],
            'progress': event['progress'],
            'status': event['status']
        })) 