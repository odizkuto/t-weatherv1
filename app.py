"""
=========================================
T-Weather
app.py
=========================================
"""

from flask import Flask
from flask import jsonify
from flask import render_template
from flask import send_from_directory
from flask import request

from flask_cors import CORS

from weather import weather
from analyzer import analyzer
from database import db
from scheduler import start
from notifier import notifier

from config import (
    HOST,
    PORT,
    DEBUG,
    VAPID_PUBLIC_KEY
)

app = Flask(__name__)

CORS(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/service-worker.js")
def service_worker():
    return send_from_directory(".", "service-worker.js")


@app.route("/api/weather")
def api_weather():

    latitude = request.args.get("lat", type=float)
    longitude = request.args.get("lon", type=float)

    current = weather.current(latitude, longitude)

    if current is None:
        return jsonify({
            "status": "offline"
        })

    result = analyzer.analyze(current, latitude, longitude)

    return jsonify(result)


@app.route("/api/history")
def history():

    rows = db.history()

    data = []

    for row in rows:
        data.append({
            "id": row[0],
            "time": row[1],
            "temperature": row[2],
            "humidity": row[3],
            "rain": row[4],
            "rain_probability": row[5],
            "cloud": row[6],
            "uv": row[7],
            "wind": row[8],
            "status": row[9],
            "created_at": row[10]
        })

    return jsonify(data)


@app.route("/api/latest")
def latest():

    row = db.latest()

    if row is None:
        return jsonify({})

    return jsonify({
        "id": row[0],
        "time": row[1],
        "temperature": row[2],
        "humidity": row[3],
        "rain": row[4],
        "rain_probability": row[5],
        "cloud": row[6],
        "uv": row[7],
        "wind": row[8],
        "status": row[9],
        "created_at": row[10]
    })


@app.route("/api/vapid-public-key")
def vapid_public_key():

    return jsonify({
        "publicKey": VAPID_PUBLIC_KEY
    })


@app.route("/api/subscribe", methods=["POST"])
def subscribe():

    sub = request.get_json()

    if not sub or "endpoint" not in sub:
        return jsonify({"status": "error", "message": "invalid subscription"}), 400

    endpoint = sub.get("endpoint")
    keys = sub.get("keys", {})

    # Toạ độ điện thoại tại thời điểm đăng ký (có thể không có nếu
    # người dùng chưa cấp quyền định vị -> sẽ dùng vị trí mặc định
    # trong config.py cho tới khi có toạ độ thật).
    latitude = sub.get("latitude")
    longitude = sub.get("longitude")

    db.add_subscription(
        endpoint,
        keys.get("p256dh"),
        keys.get("auth"),
        latitude,
        longitude
    )

    return jsonify({"status": "ok"})


@app.route("/api/update-location", methods=["POST"])
def update_location():
    """
    Điện thoại di chuyển sang vị trí mới -> cập nhật lại toạ độ cho
    subscription đã đăng ký, để lần quét cảnh báo nền tiếp theo dùng
    đúng vị trí hiện tại thay vì vị trí cũ.
    """

    body = request.get_json()

    if not body or "endpoint" not in body:
        return jsonify({"status": "error", "message": "missing endpoint"}), 400

    endpoint = body.get("endpoint")
    latitude = body.get("latitude")
    longitude = body.get("longitude")

    if latitude is None or longitude is None:
        return jsonify({"status": "error", "message": "missing coordinates"}), 400

    updated = db.update_subscription_location(endpoint, latitude, longitude)

    if not updated:
        return jsonify({
            "status": "error",
            "message": "subscription chưa tồn tại, hãy đăng ký lại"
        }), 404

    return jsonify({"status": "ok"})


@app.route("/api/test-push")
def test_push():
    """
    Gửi thử 1 tin nhắn push đến tất cả thiết bị đã đăng ký,
    không cần chờ có cảnh báo thời tiết thật xảy ra.
    Dùng để kiểm tra tính năng thông báo trên điện thoại.
    """

    subscriptions = db.get_subscriptions()

    if not subscriptions:
        return jsonify({
            "status": "error",
            "message": "Chưa có thiết bị nào đăng ký nhận thông báo. "
                       "Mở trang trên điện thoại và cho phép thông báo trước."
        }), 400

    test_warning = [{
        "title": "🔔 Test thông báo T-Weather",
        "message": "Nếu bạn thấy tin nhắn này, tính năng push đã hoạt động!",
        "type": "test"
    }]

    expired = notifier.broadcast(subscriptions, test_warning)

    if expired:
        for endpoint in expired:
            db.remove_subscription(endpoint)

    sent = len(subscriptions) - (len(expired) if expired else 0)

    return jsonify({
        "status": "ok",
        "total_subscriptions": len(subscriptions),
        "sent": sent,
        "expired_removed": len(expired) if expired else 0
    })


if __name__ == "__main__":

    start()

    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG
    )
