"""
=========================================
T-Weather
notifier.py
Web Push Notification
=========================================
"""

import json

from pywebpush import webpush, WebPushException

from config import (
    VAPID_PRIVATE_KEY,
    VAPID_CLAIM_EMAIL
)


class Notifier:

    def __init__(self):

        self.vapid_private_key = VAPID_PRIVATE_KEY

        self.vapid_claims = {
            "sub": VAPID_CLAIM_EMAIL
        }

    def send(self, subscription, title, message):

        payload = json.dumps({
            "title": title,
            "body": message
        })

        try:

            webpush(

                subscription_info=subscription,

                data=payload,

                vapid_private_key=self.vapid_private_key,

                vapid_claims=self.vapid_claims

            )

            return True

        except WebPushException as e:

            print("Push Error:", e)

            # Subscription hết hạn hoặc bị thu hồi -> báo hiệu để xoá khỏi DB
            status_code = None

            if e.response is not None:
                status_code = e.response.status_code

            if status_code in (404, 410):
                return "expired"

            return False

    def broadcast(self, subscriptions, warnings):
        """
        subscriptions: list các tuple (endpoint, p256dh, auth) lấy từ db.get_subscriptions()
        warnings: list các dict {"title":..., "message":..., "type":...} từ analyzer
        """

        if not warnings or not subscriptions:
            return

        expired_endpoints = []

        for endpoint, p256dh, auth in subscriptions:

            subscription_info = {
                "endpoint": endpoint,
                "keys": {
                    "p256dh": p256dh,
                    "auth": auth
                }
            }

            for warning in warnings:

                result = self.send(
                    subscription_info,
                    warning["title"],
                    warning["message"]
                )

                if result == "expired":
                    expired_endpoints.append(endpoint)
                    break  # subscription này chết, khỏi gửi tiếp cảnh báo còn lại cho nó

        return expired_endpoints


notifier = Notifier()


if __name__ == "__main__":

    print("Notifier Ready")
