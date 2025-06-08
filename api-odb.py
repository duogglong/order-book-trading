from flask import Flask, jsonify, abort
import requests
import os

app = Flask(__name__)

# Binance API chỉ chấp nhận những limit này cho endpoint depth
VALID_LIMITS = [5, 10, 20, 50, 100, 500, 1000]
    
def fetch_order_book(symbol, limit):
    if limit not in VALID_LIMITS:
        abort(400, description=f"Limit không hợp lệ. Chỉ chấp nhận {VALID_LIMITS}")
    url = f'https://api.binance.com/api/v3/depth?symbol={symbol.upper()}&limit={limit}'
    response = requests.get(url)
    if response.status_code != 200:
        abort(response.status_code, description=f"Lỗi khi lấy dữ liệu từ Binance: {response.text}")
    data = response.json()
    return data

def fetch_last_price(symbol):
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}'
    response = requests.get(url)
    if response.status_code != 200:
        abort(response.status_code, description=f"Lỗi khi lấy giá hiện tại từ Binance: {response.text}")
    data = response.json()
    return float(data['price'])

def analyze_order_book(data, symbol):
    bids = data.get('bids', [])
    asks = data.get('asks', [])

    total_bid_qty = sum(float(qty) for _, qty in bids)
    total_ask_qty = sum(float(qty) for _, qty in asks)

    highest_bid = float(bids[0][0]) if bids else 0
    lowest_ask = float(asks[0][0]) if asks else 0
    spread = lowest_ask - highest_bid if bids and asks else 0

    if total_bid_qty > total_ask_qty:
        taller = "BUY*"
        diff = total_bid_qty - total_ask_qty
    elif total_ask_qty > total_bid_qty:
        taller = "SELL*"
        diff = total_ask_qty - total_bid_qty
    else:
        taller = "BALANCED"
        diff = 0

    last_price = fetch_last_price(symbol)

    return {
        "symbol": symbol.upper(),
        "last_price": round(last_price, 6),
        "spread": round(spread, 6),
        "total_bid_qty": round(total_bid_qty, 4),
        "total_ask_qty": round(total_ask_qty, 4),
        "taller": taller,
        "difference": round(diff, 4),
    }

@app.route('/orderbook/<symbol>/<int:limit>')
def orderbook(symbol, limit):
    data = fetch_order_book(symbol, limit)
    result = analyze_order_book(data, symbol)
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
