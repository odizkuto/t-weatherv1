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

    current = weather.current()

    if current is None:
        return jsonify({
            "status": "offline"
        })

    result = analyzer.analyze(current)

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

    db.add_subscription(
        endpoint,
        keys.get("p256dh"),
        keys.get("auth")
    )

    return jsonify({"status": "ok"})


if __name__ == "__main__":

    start()

    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG
    )
