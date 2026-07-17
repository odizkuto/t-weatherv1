"""
=========================================
T-Weather
scheduler.py
=========================================
"""

from apscheduler.schedulers.background import BackgroundScheduler

from weather import weather
from analyzer import analyzer
from database import db
from notifier import notifier

from config import CHECK_INTERVAL


scheduler = BackgroundScheduler()


def update_home_dashboard():
    """
    Cập nhật thời tiết cho vị trí mặc định trong config.py (GPS cố
    định) -> lưu vào bảng weather_history để trang dashboard/history
    có dữ liệu xem lại. Không liên quan đến vị trí điện thoại từng
    người dùng.
    """

    current = weather.current()

    if current is None:
        return

    result = analyzer.analyze(current)

    db.save(
        current,
        result["status"]
    )

    return result


def check_subscription(endpoint, p256dh, auth, latitude, longitude):
    """
    Quét thời tiết theo ĐÚNG toạ độ hiện tại của 1 thiết bị đã đăng
    ký nhận thông báo, rồi gửi cảnh báo riêng cho thiết bị đó (mỗi
    người 1 vị trí khác nhau -> cảnh báo khác nhau, không dùng
    broadcast chung 1 nội dung cho tất cả nữa).

    Trả về True nếu subscription này đã hết hạn (cần xoá khỏi DB).
    """

    current = weather.current(latitude, longitude)

    if current is None:
        return False

    result = analyzer.analyze(current, latitude, longitude)

    if result["status"] != "warning":
        return False

    subscription_info = {
        "endpoint": endpoint,
        "keys": {
            "p256dh": p256dh,
            "auth": auth
        }
    }

    for warning in result["warnings"]:

        print(
            "[T-Weather]",
            endpoint[:40] + "...",
            warning["title"],
            warning["message"]
        )

        send_result = notifier.send(
            subscription_info,
            warning["title"],
            warning["message"]
        )

        if send_result == "expired":
            return True

    return False


def update_weather():

    try:

        update_home_dashboard()

        subscriptions = db.get_subscriptions()

        expired_endpoints = []

        for endpoint, p256dh, auth, latitude, longitude in subscriptions:

            try:

                is_expired = check_subscription(
                    endpoint,
                    p256dh,
                    auth,
                    latitude,
                    longitude
                )

                if is_expired:
                    expired_endpoints.append(endpoint)

            except Exception as e:

                print("Subscription Check Error:", endpoint[:40], e)

        for endpoint in expired_endpoints:
            db.remove_subscription(endpoint)

    except Exception as e:

        print("Scheduler Error:", e)


def start():

    scheduler.add_job(
        update_weather,
        "interval",
        minutes=CHECK_INTERVAL,
        id="weather_job",
        replace_existing=True
    )

    scheduler.start()

    update_weather()
