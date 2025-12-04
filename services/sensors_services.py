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


import httpx
import json
import email.utils
from datetime import timedelta

async def service_get_predicted_aqi(payload):
    """
    payload: object có thuộc tính station_id và timestamp (str)
    """
    url = "https://florus.hpcc.vn/api/aqi_server/prediction"
    headers = {"Content-Type": "application/json"}

    data = {
        "timestamp": "2025-11-28 00:00:00",
        "station_id": "216",
        "latitude": "10.780482",
        "longitude": "106.659511",
        "limit": 20,
        "offset": 0,
        "flag": True
    }

    # async with httpx.AsyncClient(verify=False, timeout=10) as client:
    #     response = await client.request("GET", url, headers=headers, json=data)
    #     try:
    #         response.raise_for_status()
    #         response_json = response.json()  # dict
    #         print(json.dumps(response_json, indent=4))  # chỉ để debug
    #     except httpx.HTTPStatusError as e:
    #         print(f"HTTP error: {e.response.status_code} - {e.response.text}")
    #         return {"message": str(e), "predictions": []}
    #     except Exception as e:
    #         print(f"Other error: {str(e)}")
    #         return {"message": str(e), "predictions": []}

    # predictions = response_json.get("prediction", [])
    # if not predictions:
    #     return {"message": response_json.get("message", "No data"), "predictions": []}

    # # timestamp gốc
    # ts_dt = email.utils.parsedate_to_datetime(predictions[0]["timestamp"])

    # result = {}
    # for h in [1, 2, 3]:
    #     target = ts_dt + timedelta(hours=h)
    #     pred = find_prediction_for_hour(predictions, target)
    #     if pred:
    #         result[f"{h}h"] = {
    #             "pm25": pred["pm25_predicted"],
    #             "pm10": pred["pm10_predicted"],
    #             "no2": pred["no2_predicted"],
    #             "co": pred["co_predicted"],
    #             "so2": pred["so2_predicted"],
    #             "o3": pred["o3_predicted"],
    #             "timestamp": pred["timestamp"]
    #         }

    ts_dt = datetime.fromisoformat(payload.timestamp)

    result = {}
    for h in [1, 2, 3]:
        target_time = ts_dt + timedelta(hours=h)
        # Sinh random các thông số trong khoảng hợp lý
        pred = {
            "pm25": round(random.uniform(20, 40), 2),
            "pm10": round(random.uniform(20, 50), 2),
            "no2": round(random.uniform(0.01, 0.4), 2),
            "co": round(random.uniform(0.01, 0.4), 2),
            "so2": round(random.uniform(0.01, 0.4), 2),
            "o3": round(random.uniform(0.01, 0.4), 3),
            "timestamp": target_time.isoformat(),
            "station_id": payload.station_id
        }
        result[f"{h}h"] = pred

    return {
        "message": "Mocked prediction data",
        "predictions": result
    }

    return {"message": response_json.get("message", "Success"), "predictions": result}

    # return {}