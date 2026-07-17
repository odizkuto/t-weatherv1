"""
=========================================
T-Weather Configuration
=========================================
"""

# ==========================
# GPS (ĐỔI THÀNH GPS CỦA BẠN)
# ==========================

LATITUDE = 10.658639
LONGITUDE = 105.334861

# Bán kính theo dõi (km)
RADIUS_KM = 5

# ==========================
# Open-Meteo
# ==========================

BASE_URL = "https://api.open-meteo.com/v1/forecast"

# ==========================
# Scheduler
# ==========================

CHECK_INTERVAL = 5   # phút

# ==========================
# Cảnh báo mưa
# ==========================

RAIN_MM = 0.1
RAIN_PROBABILITY = 60

# ==========================
# Cảnh báo nắng
# ==========================

UV_WARNING = 6

HIGH_TEMP = 33

LOW_CLOUD = 10

# ==========================
# Database
# ==========================

DATABASE = "database/weather.db"

# ==========================
# Cache
# ==========================

CACHE_FILE = "cache/weather.json"

# ==========================
# Flask
# ==========================

HOST = "0.0.0.0"

PORT = 5000

DEBUG = True

# ==========================
# Web Push (VAPID)
# ==========================
# Key này mình đã tạo sẵn cho bạn - dùng luôn được.
# Nếu muốn tự tạo cặp key khác, chạy: python generate_vapid_keys.py

VAPID_PUBLIC_KEY = "BJy4UfeLNgwaIqAoaKQ4oYWGP-H9lmW-MEA2XQH7zMLtDkQXsPFGLcF78_6D9DxQaNMxxn2XY9qqYcqBnIKOaL0"
VAPID_PRIVATE_KEY = "IALJANw11PxxJwmy7iicdBVAOkrNRr0A48QwJR-FMnI"
VAPID_CLAIM_EMAIL = "mailto:admin@tweather.local"
