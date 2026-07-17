"""
=========================================
T-Weather
analyzer.py
=========================================
"""

from weather import weather
from config import (
    UV_WARNING,
    RAIN_MM,
    RAIN_PROBABILITY,
    HIGH_TEMP,
    LOW_CLOUD,
    WIND_WARNING
)


class WeatherAnalyzer:

    def analyze(self, current, latitude=None, longitude=None):

        warnings = []

        next_hour = weather.next_one_hour(latitude, longitude)

        # ==========================
        # MƯA
        # ==========================

        if (
            next_hour["rain"] >= RAIN_MM
            or
            next_hour["rain_probability"] >= RAIN_PROBABILITY
        ):

            warnings.append({

                "type": "rain",

                "title": "🌧 Có mưa trong khoảng 1 giờ tới",

                "message":
                    f"Lượng mưa {next_hour['rain']} mm\n"
                    f"Xác suất {next_hour['rain_probability']}%"

            })

        # ==========================
        # UV
        # ==========================

        if next_hour["uv"] >= UV_WARNING:

            warnings.append({

                "type": "uv",

                "title": "☀ UV cao",

                "message":
                    f"Chỉ số UV dự báo {next_hour['uv']}"

            })

        # ==========================
        # NẮNG GẮT
        # ==========================

        if (
            next_hour["temperature"] >= HIGH_TEMP
            and
            next_hour["cloud"] <= LOW_CLOUD
        ):

            warnings.append({

                "type": "heat",

                "title": "🔥 Nắng gắt",

                "message":
                    f"Nhiệt độ {next_hour['temperature']}°C"

            })

        # ==========================
        # GIÓ
        # ==========================

        if next_hour["wind"] >= WIND_WARNING:

            warnings.append({

                "type": "wind",

                "title": "💨 Gió mạnh",

                "message":
                    f"Tốc độ gió {next_hour['wind']} km/h"

            })

        return {

            "status":
                "warning"
                if warnings
                else
                "normal",

            "current": current,

            "forecast": next_hour,

            "warnings": warnings

        }


analyzer = WeatherAnalyzer()


if __name__ == "__main__":

    data = weather.current()

    result = analyzer.analyze(data)

    print(result)
