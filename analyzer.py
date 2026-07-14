"""
=========================================
T-Weather
analyzer.py
=========================================
"""

from weather import weather


class WeatherAnalyzer:

    def analyze(self, current):

        warnings = []

        next_hour = weather.next_one_hour()

        # ==========================
        # MƯA
        # ==========================

        if (
            next_hour["rain"] >= 0.1
            or
            next_hour["rain_probability"] >= 60
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

        if next_hour["uv"] >= 6:

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
            next_hour["temperature"] >= 35
            and
            next_hour["cloud"] <= 10
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

        if next_hour["wind"] >= 40:

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