from django.urls import re_path
from orders.consumers import LTPConsumer, OrderUpdateConsumer

websocket_urlpatterns = [
    re_path(r'ws/ltp/$', LTPConsumer.as_asgi()),
    re_path(r'ws/order-updates/$', OrderUpdateConsumer.as_asgi()),
]
