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

CHECK_INTERVAL = 10   # phút

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