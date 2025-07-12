import json
import traceback
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from fyers_apiv3 import fyersModel
from .models import TradeOrder


access_token = settings.FYERS_ACCESS_TOKEN


@method_decorator(csrf_exempt, name='dispatch')
class PlaceOrderView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)

        product_mapping = {
            "DELIVERY": "CNC",
            "INTRADAY": "INTRADAY",
            "MARGIN": "MARGIN"
        }
        fyers_product = product_mapping.get(data['product'].upper(), "CNC")

        order = TradeOrder.objects.create(
            symbol=data['symbol'],
            quantity=data['quantity'],
            exchange=data['exchange'],
            validity=data['validity'],
            order_type=data['orderType'],
            order_mode=data['orderMode'],
            price=data.get('price'),
            trigger_price=data.get('triggerPrice'),
            product=fyers_product,
            status='PENDING'
        )

        fyers = fyersModel.FyersModel(
            client_id=settings.FYERS_CLIENT_ID,
            token=access_token,
            log_path="/tmp/"
        )

        if order.order_mode.upper() == "SELL" and fyers_product == "CNC":
            try:
                holdings_response = fyers.get_holdings()
                holdings = holdings_response.get("holdings", [])
                symbol_key = f"{order.exchange}:{order.symbol}"
                held_qty = 0
                for holding in holdings:
                    if holding["symbol"] == symbol_key:
                        held_qty = holding["qty"]
                        break

                if held_qty < order.quantity:
                    order.status = "REJECTED"
                    order.fyers_response = {
                        "error": f"Insufficient holdings. You have {held_qty} shares of {order.symbol}."
                    }
                    order.save()
                    return JsonResponse({
                        "error": f"Insufficient holdings. You have {held_qty} shares of {order.symbol}."
                    }, status=400)

            except Exception as e:
                order.status = "ERROR"
                order.fyers_response = {"error": f"Holdings check failed: {str(e)}"}
                order.save()
                return JsonResponse({"error": f"Holdings check failed: {str(e)}"}, status=500)

        order_payload = {
            "symbol": f"{order.exchange}:{order.symbol}",
            "qty": order.quantity,
            "type": self.get_type_code(order.order_type),
            "side": 1 if order.order_mode.upper() == "BUY" else -1,
            "productType": fyers_product,
            "limitPrice": float(order.price) if order.price else 0,
            "stopPrice": float(order.trigger_price) if order.trigger_price else 0,
            "validity": order.validity,
            "disclosedQty": 0,
            "offlineOrder": False,
            "exchange": order.exchange
        }

        try:
            print("🔼 ORDER PAYLOAD:", json.dumps(order_payload, indent=2))
            fyers_response = fyers.place_order(order_payload)
            print("✅ FYERS RESPONSE:", json.dumps(fyers_response, indent=2))

            if fyers_response.get("s") == "ok" and fyers_response.get("code") in [1101, 200]:
                order.status = "SUCCESS"
            else:
                order.status = "FAILED"

            order.fyers_response = fyers_response
            order.save()

            return JsonResponse({
                "message": "Order Placed",
                "fyers_response": fyers_response
            })

        except Exception as e:
            traceback.print_exc()
            order.status = "ERROR"
            order.fyers_response = {"error": str(e)}
            order.save()
            return JsonResponse({"error": str(e)}, status=500)

    def get_type_code(self, order_type):
        return {
            "LIMIT": 1,
            "MARKET": 2,
            "SL": 3
        }.get(order_type.upper(), 2)


class OrderListView(View):
    def get(self, request):
        orders = list(TradeOrder.objects.all().order_by('-id').values())
        return JsonResponse({"orders": orders})


class GetLTPView(View):
    def get(self, request):
        symbol = request.GET.get("symbol")
        if not symbol:
            return JsonResponse({"error": "Symbol is required"}, status=400)

        fyers = fyersModel.FyersModel(
            client_id=settings.FYERS_CLIENT_ID,
            token=settings.FYERS_ACCESS_TOKEN,
            log_path="/tmp/"
        )

        try:
            response = fyers.quotes({"symbols": symbol})
            ltp = response.get("d", [{}])[0].get("v", {}).get("lp")

            if ltp is not None:
                # ✅ Broadcast LTP to WebSocket group
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "ltp_group",
                    {
                        "type": "ltp_update",
                        "message": {
                            "symbol": symbol,
                            "ltp": ltp
                        }
                    }
                )
                return JsonResponse({"symbol": symbol, "ltp": ltp})
            else:
                return JsonResponse({
                    "error": "LTP not found",
                    "response": response
                }, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class DeleteOrderView(View):
    def delete(self, request, order_id):
        try:
            order = TradeOrder.objects.get(id=order_id)
            order.delete()
            return JsonResponse({"message": f"Order {order_id} deleted successfully."})
        except TradeOrder.DoesNotExist:
            return JsonResponse({"error": "Order not found."}, status=404)
