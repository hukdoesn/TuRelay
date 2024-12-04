# routing.py
from django.urls import path

from apps.views.consumers import SSHConsumer

from apps.views.rdp_consumers import GuacamoleConsumer

from apps.views.file_transfer_consumer import FileTransferConsumer

websocket_urlpatterns = [
    path('ws/ssh/<str:host_id>/', SSHConsumer.as_asgi()),  # SSH 连接的 WebSocket 路由
    path('ws/guacamole/<str:host_id>/', GuacamoleConsumer.as_asgi()),
    path('ws/file_transfer/<str:transfer_id>/', FileTransferConsumer.as_asgi()),
]