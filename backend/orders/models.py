from django.db import models
from django.utils import timezone

class TradeOrder(models.Model):
    ORDER_TYPES = [('LIMIT', 'Limit'), ('MARKET', 'Market'), ('SL', 'Stop Loss')]
    ORDER_MODES = [('BUY', 'Buy'), ('SELL', 'Sell')]
    PRODUCTS = [('INTRADAY', 'Intraday'), ('DELIVERY', 'Delivery'), ('MARGIN', 'Margin')]
    VALIDITY_CHOICES = [('DAY', 'Day'), ('IOC', 'IOC')]

    symbol = models.CharField(max_length=50)
    quantity = models.IntegerField()
    exchange = models.CharField(max_length=10)
    validity = models.CharField(max_length=10, choices=VALIDITY_CHOICES)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPES)
    order_mode = models.CharField(max_length=10, choices=ORDER_MODES)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    trigger_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product = models.CharField(max_length=10, choices=PRODUCTS)
    
    status = models.CharField(max_length=20, default='PENDING')
    fyers_response = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)  # Order date & time
    updated_at = models.DateTimeField(auto_now=True)         # Modified time

    # 🆕 New fields below
    entry_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # LTP at time of entry
    revisit_flag = models.BooleanField(default=False)  # If this order was revisited later
    parent_order_id = models.IntegerField(null=True, blank=True)  # Reference to earlier order if this is a follow-up

    def __str__(self):
        return f"{self.symbol} - {self.order_mode} @ {self.price or 'MKT'}"
