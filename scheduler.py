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


scheduler = BackgroundScheduler()


def update_weather():

    try:

        current = weather.current()

        if current is None:
            return

        result = analyzer.analyze(current)

        db.save(
            current,
            result["status"]
        )

        print(
            "[T-Weather]",
            result["status"]
        )

        if result["status"] == "warning":

            for warning in result["warnings"]:

                print(
                    warning["title"],
                    warning["message"]
                )

    except Exception as e:

        print("Scheduler Error:", e)


def start():

    scheduler.add_job(
        update_weather,
        "interval",
        minutes=10,
        id="weather_job",
        replace_existing=True
    )

    scheduler.start()

    update_weather()