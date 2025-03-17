import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DTest.settings")

# ВАЖНО: сначала настроить Django
import django
django.setup()

# Теперь можно импортировать остальное
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from DTest.routing import websocket_urlpatterns
from notifications.middleware import JWTAuthMiddleware  # путь к middleware

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})