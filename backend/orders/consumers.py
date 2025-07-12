import json
import asyncio
import threading
import os
import django
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from fyers_apiv3.FyersWebsocket import data_ws

# ✅ Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trade_backend.settings")
django.setup()

from django.conf import settings

# 🔁 Global Variables
active_clients = {}  # Format: {consumer_instance: [symbols]}
fyers = None         # Global Fyers socket instance

# ✅ Global asyncio loop (used across threads)
main_event_loop = asyncio.new_event_loop()
asyncio.set_event_loop(main_event_loop)

# -----------------------------
# 🔹 LTPConsumer: for live price updates
# -----------------------------
class LTPConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.symbols = []
        active_clients[self] = self.symbols
        print(f"🟢 LTP WebSocket Connected from: {self.scope.get('client')}")

    async def disconnect(self, close_code):
        if self in active_clients:
            del active_clients[self]
        print(f"🔴 LTP WebSocket Disconnected.")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            if data.get("type") == "subscribe" and "symbol" in data:
                symbol = data["symbol"]

                if symbol not in self.symbols:
                    self.symbols.append(symbol)
                    await self.subscribe_to_fyers(symbol)
                    print(f"✅ Subscribed to {symbol}")

            elif data.get("type") == "unsubscribe" and "symbol" in data:
                symbol = data["symbol"]
                if symbol in self.symbols:
                    self.symbols.remove(symbol)
                    print(f"🛑 Unsubscribed from {symbol}")

        except Exception as e:
            print("❌ Error in WebSocket message:", str(e))

    @sync_to_async
    def subscribe_to_fyers(self, symbol):
        if fyers:
            print(f"➡️ Subscribing to Fyers: {symbol}")
            fyers.subscribe(symbols=[symbol], data_type="SymbolUpdate")

    async def send_ltp_to_client(self, symbol, ltp):
        try:
            print(f"📤 Sending LTP to frontend: {symbol} = {ltp}")
            await self.send(text_data=json.dumps({
                "symbol": symbol,
                "ltp": ltp,
                "precision": 2
            }))
        except Exception as e:
            print("❌ Failed to send LTP to client:", str(e))

# -----------------------------
# 🔸 OrderUpdateConsumer
# -----------------------------
class OrderUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("🟢 OrderUpdate WebSocket Connected")

    async def disconnect(self, close_code):
        print("🔴 OrderUpdate WebSocket Disconnected")

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"📨 OrderUpdate Received: {data}")
        await self.send(text_data=json.dumps({
            "type": "ack",
            "message": "Order update received successfully."
        }))

# -----------------------------
# 📨 Callback from Fyers
# -----------------------------
def on_fyers_message(msg):
    print("📩 Fyers sent:", msg)

    if msg.get("type") == "symbolUpdate":
        for item in msg.get("data", []):
            symbol = item.get("symbol")
            ltp = item.get("ltp")

            print(f"📊 LTP → {symbol}: {ltp}")

            for client, subscribed_symbols in list(active_clients.items()):
                if symbol in subscribed_symbols:
                    try:
                        asyncio.run_coroutine_threadsafe(
                            client.send_ltp_to_client(symbol, ltp),
                            main_event_loop
                        )
                        print(f"📤 LTP pushed to frontend for {symbol}")
                    except Exception as e:
                        print("⚠️ Failed to push LTP update:", str(e))

# -----------------------------
# 🔌 Fyers WebSocket Starter
# -----------------------------
def start_fyers_socket():
    global fyers
    try:
        formatted_token = f"{settings.FYERS_CLIENT_ID.split('-')[0]}:{settings.FYERS_ACCESS_TOKEN}"
        fyers = data_ws.FyersDataSocket(
            access_token=formatted_token,
            log_path="",
            litemode=True,
            write_to_file=False,
            reconnect=True,
            on_connect=lambda: print("✅ Fyers Socket Connected"),
            on_close=lambda msg: print("❌ Fyers Socket Closed:", msg),
            on_error=lambda msg: print("⚠️ Fyers Socket Error:", msg),
            on_message=on_fyers_message,
        )
        fyers.connect()
    except Exception as e:
        print("🚨 Failed to start Fyers socket:", str(e))

# 🧵 Start the event loop and Fyers WebSocket
threading.Thread(target=main_event_loop.run_forever, daemon=True).start()
threading.Thread(target=start_fyers_socket, daemon=True).start()
