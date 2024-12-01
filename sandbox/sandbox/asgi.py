import os
from django.conf import settings
from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler  # Import ASGIStaticFilesHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from posts.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sandbox.settings')

print("The WebSocket routes are:", websocket_urlpatterns)

# Use ASGIStaticFilesHandler when DEBUG is True
if settings.DEBUG:
    django_asgi_app = ASGIStaticFilesHandler(get_asgi_application())
else:
    django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,  # Updated to use django_asgi_app
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
