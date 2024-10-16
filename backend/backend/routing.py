# routing.py
from django.urls import path, re_path

from apps.views.consumers import SSHConsumer

from apps.views.rdp_consumers import GuacamoleConsumer

websocket_urlpatterns = [
    path('ws/ssh/<str:host_id>/', SSHConsumer.as_asgi()),  # SSH 连接的 WebSocket 路由
    re_path(r'ws/guacamole/(?P<host_id>\w+)/$', GuacamoleConsumer.as_asgi()),
]