from fyers_apiv3.FyersWebsocket import data_ws

# ✅ Format: APP_ID:ACCESS_TOKEN
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsiZDoxIiwiZDoyIiwieDowIiwieDoxIiwieDoyIl0sImF0X2hhc2giOiJnQUFBQUFCb1hPaEk3c0p0U2xmOUd4dFlfNEJ6b2R1NEVFT3JNbHl1MGlJWjJwZVBQVFJOYlRpZGJhZVBUVzFHdmRxQkh2THYteWttVGVIZnExY3djUG53bnFFU1VWT0NIYWgtU1JTdkMydUpUVEI1Tm4wVHR5UT0iLCJkaXNwbGF5X25hbWUiOiIiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiIzOTBiZjFiODdiOGJlYWY1ZWQ5MTZlYmZiZGMwNGJkNDg4NmNjODAyOWUxNTFjZTE4YmEzMjE0YiIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImZ5X2lkIjoiWVM2MTk2NCIsImFwcFR5cGUiOjEwMCwiZXhwIjoxNzUwOTg0MjAwLCJpYXQiOjE3NTA5MTkyNDAsImlzcyI6ImFwaS5meWVycy5pbiIsIm5iZiI6MTc1MDkxOTI0MCwic3ViIjoiYWNjZXNzX3Rva2VuIn0.aALLKLOo_qqa5vh4UQ4HJ9M--HjbXfzMckz-E_wPDWU"

# ✅ Symbols to fetch LTP
symbols = ['NSE:RELIANCE-EQ', 'NSE:TATAMOTORS-EQ', 'NSE:SBIN-EQ']

def onmessage(message):
    """
    Callback to print only LTP (Last Traded Price) from incoming WebSocket messages.
    """
    if isinstance(message, dict) and message.get("symbol") and message.get("ltp") is not None:
        print(f"{message['symbol']} → LTP: ₹{message['ltp']}")
    else:
        print("🟡 Ignored:", message)

def onerror(message):
    print("❌ Error:", message)

def onclose(message):
    print("🔌 Disconnected:", message)

def onopen():
    print("✅ WebSocket Connected.")
    fyers.subscribe(symbols=symbols, data_type="SymbolUpdate")
    fyers.keep_running()

# ✅ WebSocket client
fyers = data_ws.FyersDataSocket(
    access_token=access_token,       # Must be in APP_ID:ACCESS_TOKEN format
    log_path="",                     
    litemode=False,                  # ❗️ Set to False to receive full market data
    write_to_file=False,            
    reconnect=True,                 
    on_connect=onopen,
    on_close=onclose,
    on_error=onerror,
    on_message=onmessage
)

# ✅ Start connection
fyers.connect()