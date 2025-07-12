from django.urls import path
from .views import PlaceOrderView, OrderListView, GetLTPView, DeleteOrderView

urlpatterns = [
    path('place-order/', PlaceOrderView.as_view(), name='place_order'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('get-ltp/', GetLTPView.as_view(), name='get_ltp'),
    path('delete-order/<int:order_id>/', DeleteOrderView.as_view(), name='delete_order'),  # ✅ Add this
]
