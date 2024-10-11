# routing.py
from django.urls import path
from django.urls import re_path
from apps.views.consumers import SSHConsumer
from apps.views.rdp_consumers import RDPConnectView

websocket_urlpatterns = [
    path('ws/ssh/<str:host_id>/', SSHConsumer.as_asgi()),  # SSH 连接的 WebSocket 路由
    path('guacamole/<str:host_id>/', RDPConnectView.as_asgi()),  # RDP WebSocket route
]