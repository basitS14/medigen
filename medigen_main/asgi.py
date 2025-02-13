import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from meds.routing import websocket_urlpatterns  # Import your WebSocket routes

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medigen_main.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Regular HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)  # WebSocket routes
    ),
})
