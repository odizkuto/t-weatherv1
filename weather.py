"""
=========================================
T-Weather
weather.py
=========================================
"""

import json
from datetime import datetime

import requests

from config import (
    LATITUDE,
    LONGITUDE,
    BASE_URL,
    CACHE_FILE
)


class WeatherService:

    def __init__(self):

        self.url = (
            f"{BASE_URL}"
            f"?latitude={LATITUDE}"
            f"&longitude={LONGITUDE}"
            "&hourly="
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "precipitation_probability,"
            "cloud_cover,"
            "uv_index,"
            "wind_speed_10m"
            "&forecast_days=2"
            "&timezone=auto"
        )

    def fetch(self):

        try:

            response = requests.get(
                self.url,
                timeout=20
            )

            response.raise_for_status()

            data = response.json()

            self.save_cache(data)

            return data

        except Exception as e:

            print("Weather Error:", e)

            return self.load_cache()

    def save_cache(self, data):

        try:

            with open(
                CACHE_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    data,
                    f,
                    ensure_ascii=False,
                    indent=4
                )

        except Exception as e:

            print("Save Cache Error:", e)

    def load_cache(self):

        try:

            with open(
                CACHE_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except:

            return None

    def _current_index(self, times):

        now = datetime.now()

        current = now.strftime("%Y-%m-%dT%H:00")

        if current in times:
            return times.index(current)

        return 0

    def current(self):

        data = self.fetch()

        if not data:
            return None

        hourly = data["hourly"]

        i = self._current_index(hourly["time"])

        return {

            "time": hourly["time"][i],

            "temperature": hourly["temperature_2m"][i],

            "humidity": hourly["relative_humidity_2m"][i],

            "rain": hourly["precipitation"][i],

            "rain_probability":
                hourly["precipitation_probability"][i],

            "cloud": hourly["cloud_cover"][i],

            "uv": hourly["uv_index"][i],

            "wind": hourly["wind_speed_10m"][i]

        }

    def next_one_hour(self):

        data = self.fetch()

        if not data:
            return None

        hourly = data["hourly"]

        i = self._current_index(hourly["time"])

        j = min(i + 1, len(hourly["time"]) - 1)

        return {

            "time": hourly["time"][j],

            "temperature": hourly["temperature_2m"][j],

            "humidity": hourly["relative_humidity_2m"][j],

            "rain": hourly["precipitation"][j],

            "rain_probability":
                hourly["precipitation_probability"][j],

            "cloud": hourly["cloud_cover"][j],

            "uv": hourly["uv_index"][j],

            "wind": hourly["wind_speed_10m"][j]

        }


weather = WeatherService()


if __name__ == "__main__":

    print(weather.current())

    print()

    print(weather.next_one_hour())