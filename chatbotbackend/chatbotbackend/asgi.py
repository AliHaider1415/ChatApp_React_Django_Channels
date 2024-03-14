
import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from api.consumers import *

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbotbackend.settings')

application = get_asgi_application()

ws_patterns = [
    # path('ws/test/',TestConsumer.as_asgi()),
    path('ws/async/',AsyncConsumer.as_asgi())
]
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(ws_patterns)
    )
})