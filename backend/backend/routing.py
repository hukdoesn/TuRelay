# routing.py
from django.urls import path, re_path

from apps.views.consumers import SSHConsumer

from apps.views.rdp_consumers import RDPConsumer

websocket_urlpatterns = [
    path('ws/ssh/<str:host_id>/', SSHConsumer.as_asgi()),  # SSH 连接的 WebSocket 路由
    path('ws/rdp/<str:host_id>/', RDPConsumer.as_asgi()),  # RDP 连接的 WebSocket 路由
]