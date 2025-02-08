import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from ws.routing import websocket_urlpatterns  # Import WebSocket routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'j&k.settings')
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(websocket_urlpatterns)
})