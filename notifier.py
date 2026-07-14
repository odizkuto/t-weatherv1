"""
=========================================
T-Weather
notifier.py
Web Push Notification
=========================================
"""

from pywebpush import webpush, WebPushException


class Notifier:

    def __init__(self):

        self.vapid_private_key = ""
        self.vapid_claims = {
            "sub": "mailto:admin@tweather.local"
        }

    def send(self, subscription, title, message):

        payload = f"""{{
            "title":"{title}",
            "body":"{message}"
        }}"""

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

            return False

    def broadcast(self, subscriptions, warnings):

        if not warnings:

            return

        title = warnings[0]["title"]

        message = warnings[0]["message"]

        for sub in subscriptions:

            self.send(
                sub,
                title,
                message
            )


notifier = Notifier()


if __name__ == "__main__":

    print("Notifier Ready")