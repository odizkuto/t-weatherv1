"""
=========================================
T-Weather
weather.py
=========================================
"""

import json
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

# Múi giờ của khu vực theo dõi (Open-Meteo trả timezone=auto theo GPS này)
LOCATION_TZ = ZoneInfo("Asia/Ho_Chi_Minh")

from config import (
    LATITUDE,
    LONGITUDE,
    BASE_URL,
    CACHE_FILE,
    CHECK_INTERVAL
)


class WeatherService:

    def __init__(self):

        # Cache trong RAM cho các toạ độ ĐỘNG (điện thoại di chuyển).
        # key: (lat làm tròn 3 số, lon làm tròn 3 số)
        # value: (thời điểm lấy dữ liệu, data trả về từ Open-Meteo)
        self._mem_cache = {}

        # Số giây dữ liệu 1 toạ độ được coi là còn "mới" -> chưa cần
        # gọi lại API. Lấy theo đúng chu kỳ quét để không gọi API
        # thừa khi nhiều request đến cùng lúc cho cùng 1 vị trí.
        self._cache_ttl = CHECK_INTERVAL * 60

    def _build_url(self, latitude, longitude):

        return (
            f"{BASE_URL}"
            f"?latitude={latitude}"
            f"&longitude={longitude}"
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

    def _resolve_coords(self, latitude, longitude):
        """
        Không có toạ độ truyền vào (vd. trình duyệt chưa cấp quyền
        định vị) -> dùng toạ độ mặc định trong config.py làm phương
        án dự phòng.
        """

        if latitude is None or longitude is None:
            return LATITUDE, LONGITUDE

        return latitude, longitude

    def fetch(self, latitude=None, longitude=None):

        latitude, longitude = self._resolve_coords(latitude, longitude)

        is_default_location = (
            latitude == LATITUDE
            and
            longitude == LONGITUDE
        )

        cache_key = (round(latitude, 3), round(longitude, 3))

        cached = self._mem_cache.get(cache_key)

        if cached and (time.time() - cached[0]) < self._cache_ttl:
            return cached[1]

        try:

            response = requests.get(
                self._build_url(latitude, longitude),
                timeout=20
            )

            response.raise_for_status()

            data = response.json()

            self._mem_cache[cache_key] = (time.time(), data)

            # Chỉ ghi file cache cho vị trí mặc định (dùng khi mất
            # mạng và không có toạ độ điện thoại nào gửi lên).
            if is_default_location:
                self.save_cache(data)

            return data

        except Exception as e:

            print("Weather Error:", e)

            # Còn cache RAM cũ (dù hết hạn) cho đúng toạ độ này thì
            # dùng tạm, còn hơn không có gì.
            if cached:
                return cached[1]

            if is_default_location:
                return self.load_cache()

            return None

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

        # Luôn tính giờ hiện tại theo múi giờ của khu vực GPS
        # (LOCATION_TZ), KHÔNG dùng datetime.now() trần vì nó phụ
        # thuộc múi giờ hệ điều hành của server (có thể là UTC hoặc
        # bất kỳ múi giờ nào khác nơi đặt server), gây lệch giờ so
        # với nhãn thời gian "timezone=auto" mà Open-Meteo trả về.
        now = datetime.now(LOCATION_TZ)

        current = now.strftime("%Y-%m-%dT%H:00")

        if current in times:
            return times.index(current)

        # Không khớp chính xác (vd. cache cũ) -> lấy mốc giờ gần nhất
        # đã qua thay vì mặc định về index 0 (00:00 của ngày đầu tiên
        # trong danh sách), để tránh hiển thị dữ liệu sai lệch hoàn toàn.
        past = [t for t in times if t <= current]

        if past:
            return times.index(past[-1])

        return 0

    def current(self, latitude=None, longitude=None):

        data = self.fetch(latitude, longitude)

        if not data:
            return None

        hourly = data["hourly"]

        i = self._current_index(hourly["time"])

        return {

            "time": hourly["time"][i],

            # Giờ thực tại thời điểm quét (đổi mỗi lần scan, không bị
            # kẹt nguyên 1 tiếng như "time" - vốn chỉ là mốc giờ tròn
            # của bản ghi dự báo).
            "updated_at":
                datetime.now(LOCATION_TZ).strftime("%H:%M %d/%m/%Y"),

            "temperature": hourly["temperature_2m"][i],

            "humidity": hourly["relative_humidity_2m"][i],

            "rain": hourly["precipitation"][i],

            "rain_probability":
                hourly["precipitation_probability"][i],

            "cloud": hourly["cloud_cover"][i],

            "uv": hourly["uv_index"][i],

            "wind": hourly["wind_speed_10m"][i]

        }

    def next_one_hour(self, latitude=None, longitude=None):

        data = self.fetch(latitude, longitude)

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
