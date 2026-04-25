import requests
import time
import os

# ====== ENV ======
TOKEN = os.getenv("8595778284:AAGficu4j0aYs9cKwCyD9Xser4rNLjdFuIY")
CHAT_ID = os.getenv("1121598543")

# ====== TELEGRAM ======
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        print("Lỗi gửi Telegram")

# ====== SHOPEE PRODUCTS ======
SHOPEE_PRODUCTS = [
    {
        "name": "HTDTM2",
        "item_id": "56708833366",
        "shop_id": "374899645",
        "link": "https://shopee.vn/product/374899645/56708833366"
    },
    {
        "name": "GOKURAKUGAI (Shopee)",
        "item_id": "47708411931",
        "shop_id": "374899645",
        "link": "https://shopee.vn/product/374899645/47708411931"
    }
]

# ====== WEBSITE PRODUCTS ======
WEBSITES = [
    {
        "name": "GOKURAKUGAI (IPM)",
        "url": "https://ipm.vn/products/gokurakugai-1-ban-gioi-han"
    },
    {
        "name": "Hành Trình Đi Tìm Mẹ 2 (IPM)",
        "url": "https://ipm.vn/products/hanh-trinh-di-tim-me-2-ban-suu-tam"
    }
]
# ====== SHOPEE CHECK ======
def get_shopee_stock(item_id, shop_id):
    url = f"https://shopee.vn/api/v4/item/get?itemid={item_id}&shopid={shop_id}"

    headers = {
        "user-agent": "Mozilla/5.0",
        "accept": "application/json"
    }

    r = requests.get(url, headers=headers, timeout=10)

    if r.status_code != 200:
        return 0

    data = r.json()
    stock = 0

    models = data.get("data", {}).get("models", [])
    for m in models:
        stock += m.get("stock", 0)

    return stock

# ====== WEBSITE CHECK (IPM) ======
def check_ipm_stock_v2(url):
    try:
        headers = {"user-agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        html = r.text.lower()

        if "thêm vào giỏ" in html and "disabled" not in html:
            return 1  # có hàng
        elif "sắp có hàng" in html:
            return -1
        else:
            return 0  # hết hàng

    except:
        return 0

# ====== TRẠNG THÁI ======
status_shopee = {p["name"]: 0 for p in SHOPEE_PRODUCTS}
status_web = {w["name"]: 0 for w in WEBSITES}

last_alert = {}
COOLDOWN = 60  # chống spam

# ====== START ======
print("🚀 Bot started")
send_telegram("🚀 Bot Shopee + Website đang chạy 24/7...")

while True:
    print("Đang check...")

    now = time.time()

    # ====== SHOPEE ======
    for p in SHOPEE_PRODUCTS:
        try:
            stock = get_shopee_stock(p["item_id"], p["shop_id"])

            if stock > 0:
                if status_shopee[p["name"]] == 0 or (now - last_alert.get(p["name"], 0) > COOLDOWN):
                    msg = f"🔥 {p['name']} CÓ HÀNG!\nSố lượng: {stock}\n👉 {p['link']}"
                    send_telegram(msg)
                    last_alert[p["name"]] = now

            if stock == 0 and status_shopee[p["name"]] > 0:
                send_telegram(f"❌ {p['name']} đã hết hàng")

            status_shopee[p["name"]] = stock

        except Exception as e:
            print("Shopee lỗi:", e)

    # ====== WEBSITE ======
    for w in WEBSITES:
        try:
            stock = check_ipm_stock_v2(w["url"])

            if stock == 1:
                if status_web[w["name"]] == 0:
                    send_telegram(f"🔥 {w['name']} CÓ HÀNG!\n👉 {w['url']}")

            elif stock == -1:
                if status_web[w["name"]] != -1:
                    send_telegram(f"⏳ {w['name']} SẮP MỞ BÁN!\n👉 {w['url']}")

            elif stock == 0:
                if status_web[w["name"]] > 0:
                    send_telegram(f"❌ {w['name']} HẾT HÀNG")

            status_web[w["name"]] = stock

        except Exception as e:
            print("Web lỗi:", e)

    time.sleep(3)