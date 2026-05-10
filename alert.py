import requests, smtplib, os, json
from email.mime.text import MIMEText

# ── YOUR ALERTS ─────────────────────────────────────
ALERTS = [

    # ── BTC ALERTS ──
    {"coin": "bitcoin", "symbol": "BTC", "target": 75525.00, "direction": "below", "note": "BTC Level 1"},
    {"coin": "bitcoin", "symbol": "BTC", "target": 71171.00, "direction": "below", "note": "BTC Level 2"},
    {"coin": "bitcoin", "symbol": "BTC", "target": 67195.00, "direction": "below", "note": "BTC Level 3"},
    {"coin": "bitcoin", "symbol": "BTC", "target": 63971.00, "direction": "below", "note": "BTC Level 4"},

    # ── MOVR ALERTS ──
    {"coin": "moonriver", "symbol": "MOVR", "target": 2.34,  "direction": "below", "note": "MOVR Level 1"},
    {"coin": "moonriver", "symbol": "MOVR", "target": 1.65,  "direction": "below", "note": "MOVR Level 2"},
    {"coin": "moonriver", "symbol": "MOVR", "target": 1.39,  "direction": "below", "note": "MOVR Level 3"},
    {"coin": "moonriver", "symbol": "MOVR", "target": 1.30,  "direction": "below", "note": "MOVR Level 4"},
    {"coin": "moonriver", "symbol": "MOVR", "target": 1.23,  "direction": "below", "note": "MOVR Level 5"},
    {"coin": "moonriver", "symbol": "MOVR", "target": 1.16,  "direction": "below", "note": "MOVR Level 6 — Deep Buy"},

    # ── PLUME ALERTS ──
    {"coin": "plume-network", "symbol": "PLUME", "target": 0.01351, "direction": "below", "note": "PLUME Level 1"},
    {"coin": "plume-network", "symbol": "PLUME", "target": 0.01140, "direction": "below", "note": "PLUME Level 2"},
    {"coin": "plume-network", "symbol": "PLUME", "target": 0.01028, "direction": "below", "note": "PLUME Level 3"},
    {"coin": "plume-network", "symbol": "PLUME", "target": 0.01000, "direction": "below", "note": "PLUME Level 4 — Target Entry"},

]
# ─────────────────────────────────────────────────────

TG_TOKEN       = os.environ["TG_TOKEN"]
TG_CHAT_ID     = os.environ["TG_CHAT_ID"]
EMAIL_FROM     = os.environ["EMAIL_FROM"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO       = os.environ["EMAIL_TO"]

def get_prices(coin_ids):
    ids = ",".join(set(coin_ids))
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    r = requests.get(url, timeout=10)
    return r.json()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TG_CHAT_ID, "text": msg})

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"]    = EMAIL_FROM
    msg["To"]      = EMAIL_TO
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(EMAIL_FROM, EMAIL_PASSWORD)
        s.send_message(msg)

def check_alerts():
    coin_ids = [a["coin"] for a in ALERTS]
    prices   = get_prices(coin_ids)

    for alert in ALERTS:
        price = prices.get(alert["coin"], {}).get("usd")
        if price is None:
            print(f"Could not fetch {alert['symbol']}")
            continue

        triggered = (
            (alert["direction"] == "below" and price <= alert["target"]) or
            (alert["direction"] == "above" and price >= alert["target"])
        )

        if triggered:
            msg = (
                f"PRICE ALERT TRIGGERED\n"
                f"Coin   : {alert['symbol']}\n"
                f"Price  : ${price:,.5f}\n"
                f"Target : {alert['direction']} ${alert['target']}\n"
                f"Action : {alert['note']}\n"
                f"Check KuCoin NOW!"
            )
            send_telegram(msg)
            send_email(f"{alert['symbol']} Alert — {alert['note']}", msg)
            print(f"Alert sent for {alert['symbol']}")
        else:
            print(f"{alert['symbol']}: ${price} | waiting for {alert['direction']} ${alert['target']}")

check_alerts()
