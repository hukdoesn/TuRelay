from django.urls import path
from apps.views.consumers import SSHConsumer

websocket_urlpatterns = [
    path('ws/ssh/<int:host_id>/', SSHConsumer.as_asgi()),  # WebSocket route for SSH connection
]
