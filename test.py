import requests
import pandas as pd
from datetime import datetime, timedelta

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 10.8231,
    "longitude": 106.6297,
    "hourly": "temperature_2m,relative_humidity_2m",
    "forecast_days": 2,
    "timezone": "Asia/Bangkok"
}

r = requests.get(url, params=params).json()

df = pd.DataFrame({
    "time": r["hourly"]["time"],
    "temperature": r["hourly"]["temperature_2m"],
    "humidity": r["hourly"]["relative_humidity_2m"]
})

# Chuyển cột time sang datetime
df["time"] = pd.to_datetime(df["time"])

# Lấy thời gian hiện tại
now = datetime.now()

# Tìm dòng có thời gian gần nhất
df["time_diff"] = abs(df["time"] - now)
nearest_row = df.loc[df["time_diff"].idxmin()]

print("⏱ Thời điểm gần nhất:", nearest_row["time"])
print("🌡 Temperature:", nearest_row["temperature"])
print("💧 Humidity:", nearest_row["humidity"])
