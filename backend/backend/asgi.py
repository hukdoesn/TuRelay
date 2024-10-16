import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import backend.routing
from apps.utils import TokenAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

django_application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_application,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            backend.routing.websocket_urlpatterns
        )
    ),
})
