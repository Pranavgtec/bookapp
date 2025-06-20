import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import ecommerceapp.routing  # <- this is where WebSocket routes are stored

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

# This line loads normal Django apps (admin, views, forms, etc.)
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,  # 📦 for normal HTTP routes
    "websocket": AuthMiddlewareStack(  # 🔌 for WebSocket routes (chat)
        URLRouter(
            ecommerceapp.routing.websocket_urlpatterns  # ➡️ where to find WebSocket URLs
        )
    ),
})



