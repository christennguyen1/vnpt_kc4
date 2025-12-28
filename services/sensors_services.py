from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder 
import asyncio
from datetime import datetime, timedelta, timezone
import pandas as pd
from dateutil.relativedelta import relativedelta
import pytz
import requests
import urllib3
import json
import os
import sys
import math

import requests
import pandas as pd
import urllib3
from datetime import datetime

import httpx
import urllib3
from datetime import timedelta
import email.utils

import random
from datetime import datetime, timedelta

async def service_post_all_data(body):

    try:
        device_name = body["device_name"]
        dataset = body["dataset"]
        device_token = body["device_token"]
        longitude = float(body["longitude"])
        latitude = float(body["latitude"])
        no2 = float(body["no2"])
        so2 = float(body["so2"])
        o3 = float(body["o3"])
        pm25 = float(body["pm25"])
        pm10 = float(body["pm10"])
        aqi = float(body["aqi"])
        no2Aqi = float(body["no2Aqi"])
        so2Aqi = float(body["so2Aqi"])
        o3Aqi = float(body["o3Aqi"])
        pm25Aqi = float(body["pm25Aqi"])
        pm10Aqi = float(body["pm10Aqi"])
        coAqi = float(body["coAqi"])
        timestamp = body["timestamp"]
    except Exception as e:
        return {"error": f"Missing or invalid fields: {e}"}, 400

    # ---- Lấy dữ liệu thời tiết ----
    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m",
        "forecast_days": 2,
        "timezone": "Asia/Bangkok"
    }

    try:
        r = requests.get(weather_url, params=params, timeout=5).json()

        df = pd.DataFrame({
            "time": r["hourly"]["time"],
            "temperature": r["hourly"]["temperature_2m"],
            "humidity": r["hourly"]["relative_humidity_2m"]
        })

        df["time"] = pd.to_datetime(df["time"])
        now = datetime.now()

        df["time_diff"] = abs(df["time"] - now)
        nearest_row = df.loc[df["time_diff"].idxmin()]

        print("⏱ Thời điểm gần nhất:", nearest_row["time"])
        print("🌡 Temperature:", nearest_row["temperature"])
        print("💧 Humidity:", nearest_row["humidity"])

    except Exception as e:
        return {"error": f"Weather API error: {e}"}, 500

    # ---- Gửi dữ liệu lên server ----
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    url = "https://florus.hpcc.vn/api/external/data"
    headers = {"Content-Type": "application/json"}

    data = {
        "device_name": device_name,
        "dataset": dataset,
        "device_token": device_token,
        "longitude": longitude,
        "latitude": latitude,
        "no2": no2,
        "so2": so2,
        "o3": o3,
        "pm25": pm25,
        "pm10": pm10,
        "aqi": aqi,
        "no2Aqi": no2Aqi,
        "so2Aqi": so2Aqi,
        "o3Aqi": o3Aqi,
        "pm25Aqi": pm25Aqi,
        "pm10Aqi": pm10Aqi,
        "coAqi": coAqi,
        "temperature": float(nearest_row["temperature"]),
        "humidity": float(nearest_row["humidity"]),
        "timestamp": timestamp
    }

    try:
        response = requests.post(url, headers=headers, json=data, verify=False, timeout=10)
        response.raise_for_status()

        msg = response.json().get("message", "No message")
        print("Server message:", msg)

        return {"message": msg, "data": data}, 200

    except requests.exceptions.RequestException as e:
        print("❌ Lỗi gọi API:", e)
        return {"error": str(e)}, 500


def normalize_number(x):
    if x < 100:
        return round(x, 2)
    digits = int(math.log10(x)) + 1   # đếm số chữ số
    divisor = 10 ** (digits - 2)      # ví dụ 1234 → 10^(4-2)=100
    return round(x / divisor, 3)      # làm tròn 3 số sau dấu phẩy


def find_prediction_for_hour(predictions, target_time):
    for item in predictions:
        item_time = email.utils.parsedate_to_datetime(item["timestamp"])
        if item_time >= target_time:
            return item
    return None


import requests
from typing import Dict, Any, List


PREDICT_API_URL = "https://florus.hpcc.vn/api/aqi_server/prediction"


# async def service_get_predicted_aqi(
#     station_id: str,
#     timestamp: str,
#     limit: int = 20
# ) -> Dict[str, Any]:

#     payload = {
#         "station_id": station_id,
#         "timestamp": timestamp,
#         "limit": limit,
#         "offset": 0,
#         "flag": True
#     }

#     res = requests.get(PREDICT_API_URL, json=payload, timeout=10, verify=False)
#     res.raise_for_status()

#     data = res.json()
#     predictions = data.get("prediction", [])

#     if len(predictions) < 12:
#         raise ValueError("Not enough prediction data")

#     # sort theo thời gian (cũ -> mới)
#     predictions.sort(key=lambda x: x["timestamp"])

#     # 12 mốc thời gian gần nhất
#     latest_12 = predictions[-12:]

#     latest = latest_12[-1]

#     return {
#         "pm25_12h": [p["pm25_predicted"] for p in latest_12],
#         "pm10_12h": [p["pm10_predicted"] for p in latest_12],
#         "no2_1h": latest.get("no2_predicted"),
#         "so2_1h": latest.get("so2_predicted"),
#         "o3_1h": latest.get("o3_predicted"),
#         "co_1h": latest.get("co_predicted"),
#     }

async def service_get_predicted_aqi(
    station_id: str,
    timestamp: str,
    limit: int = 20
) -> List[Dict[str, Any]]:

    payload = {
        "station_id": station_id,
        "timestamp": timestamp,
        "limit": limit,
        "offset": 0,
        "flag": False
    }

    res = requests.get(PREDICT_API_URL, json=payload, timeout=10, verify=False)
    res.raise_for_status()

    predictions = res.json().get("prediction", [])

    if len(predictions) < 3:
        raise ValueError("Not enough future prediction data")

    # sort theo thời gian tăng dần
    predictions.sort(key=lambda x: x["timestamp"])

    # lấy 3 giờ tương lai gần nhất
    future_3h = predictions[:3]

    return [
        {
            "timestamp": p["timestamp"],
            "pm25": p["pm25_predicted"],
            "pm10": p["pm10_predicted"],
            "no2": p["no2_predicted"],
            "so2": p["so2_predicted"],
            "o3": p["o3_predicted"],
            "co": p["co_predicted"],
            "no": p["no_predicted"],
        }
        for p in future_3h
    ]


