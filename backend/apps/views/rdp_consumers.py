# rdp_consumers.py

import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import logging
import json
import traceback
import time
from apps.views.guacd_client import GuacdClient
from django.shortcuts import get_object_or_404
from apps.models import Host, Credential
from asgiref.sync import sync_to_async

logger = logging.getLogger('log')

class RDPConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.host_id = self.scope['url_route']['kwargs']['host_id'].replace('-', '')
        try:
            self.host = await sync_to_async(get_object_or_404)(Host, id=self.host_id)
            self.credential = await self.get_credential(self.host)
            await self.accept()
            await self.establish_rdp_connection()
        except Exception as e:
            logger.error(f"连接错误: {str(e)}")
            logger.error(traceback.format_exc())
            await self.close()

    @sync_to_async
    def get_credential(self, host):
        return get_object_or_404(Credential, id=host.account_type.id)

    async def disconnect(self, close_code):
        logger.info(f"WebSocket 连接关闭，代码: {close_code}")
        if hasattr(self, 'guacd_client'):
            self.guacd_client.close()

    async def receive(self, text_data=None, bytes_data=None):
        if hasattr(self, 'guacd_client') and self.guacd_client.connected:
            try:
                if text_data:
                    logger.debug(f"Sending text data to guacd: {text_data}")
                    await sync_to_async(self.guacd_client.send_instruction)(text_data)
                if bytes_data:
                    logger.debug(f"Sending binary data to guacd: {len(bytes_data)} bytes")
                    await sync_to_async(self.guacd_client.sock.sendall)(bytes_data)
            except Exception as e:
                logger.error(f"Error sending data to guacd: {str(e)}")
                logger.error(traceback.format_exc())
                await self.close()
        else:
            logger.error("Attempted to send data, but guacd_client is not connected")

    async def establish_rdp_connection(self):
        try:
            self.guacd_client = GuacdClient(hostname='localhost', port=4822)
            self.guacd_client.connect()

            connection_parameters = {
                'hostname': self.host.network,
                'port': str(self.host.port or 3389),
                'username': self.credential.account,
                'password': self.credential.password,
                'width': '1024',
                'height': '768',
                'dpi': '96',
                'color-depth': '24',
                'disable-audio': 'true',
                'enable-printing': 'false',
                'enable-drive': 'false',
                'security': 'nla',
                'ignore-cert': 'true',
                'disable-auth': 'false',
                'console': 'false',
                'server-layout': 'en-us-qwerty',
                'enable-wallpaper': 'false',
                'enable-theming': 'false',
                'enable-font-smoothing': 'true',
                'enable-full-window-drag': 'false',
                'enable-desktop-composition': 'false',
                'enable-menu-animations': 'false',
                'disable-bitmap-caching': 'false',
                'disable-offscreen-caching': 'false',
                'disable-glyph-caching': 'false',
            }

            logger.info(f"开始与 guacd 握手，参数: {connection_parameters}")
            await sync_to_async(self.guacd_client.handshake)('rdp', connection_parameters)
            logger.info("握手成功，开始转发数据")

            await self.forward_guacd_data()

        except Exception as e:
            error_message = f'建立 RDP 连接失败: {str(e)}'
            logger.error(error_message)
            logger.error(traceback.format_exc())
            await self.send(json.dumps({'error': error_message}))
            await self.close()

    async def forward_guacd_data(self):
        try:
            start_time = time.time()
            last_activity = time.time()
            while self.guacd_client.connected:
                try:
                    data = await sync_to_async(self.guacd_client.receive)()
                    if data is None:
                        if time.time() - last_activity > 30:  # 30秒无活动
                            logger.warning("No activity for 30 seconds, closing connection")
                            break
                        await asyncio.sleep(1)
                        continue
                    last_activity = time.time()
                    await self.send(text_data=data)
                except Exception as e:
                    logger.error(f'Error receiving data from guacd: {str(e)}')
                    if "Bad file descriptor" in str(e):
                        break
                    await asyncio.sleep(1)
                    continue

                if time.time() - start_time > 10:
                    logger.info(f"RDP connection has been active for {time.time() - start_time:.2f} seconds")
                    start_time = time.time()

        except Exception as e:
            logger.error(f'Error in data streaming for host {self.host_id}: {str(e)}')
            logger.error(traceback.format_exc())
            error_message = f'RDP connection error: {str(e)}'
            await self.send(json.dumps({'error': error_message}))
        finally:
            logger.info(f"RDP connection lasted for a total of {time.time() - start_time:.2f} seconds")
            if hasattr(self, 'guacd_client'):
                self.guacd_client.close()
            await self.close()
