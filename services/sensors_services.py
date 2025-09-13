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

async def service_post_all_data(body):

    device_name = body.get("device_name")
    dataset = body.get("dataset")
    device_token = body.get("device_token")
    longitude = float(body.get("longitude"))
    latitude = float(body.get("latitude"))
    no2 = float(body.get("no2"))
    so2 = float(body.get("so2"))
    o3 = float(body.get("o3"))
    pm25 = float(body.get("pm25"))
    pm10 = float(body.get("pm10"))
    aqi = float(body.get("aqi"))
    no2Aqi = float(body.get("no2Aqi"))
    so2Aqi = float(body.get("so2Aqi"))
    o3Aqi = float(body.get("o3Aqi"))
    pm25Aqi = float(body.get("pm25Aqi"))
    pm10Aqi = float(body.get("pm10Aqi"))
    coAqi = float(body.get("coAqi"))
    timestamp = body.get("timestamp")

    # Tắt warning SSL (do bypass SSL verification)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    url = "https://florus.hpcc.vn/api/external/data"
    headers = {
        "Content-Type": "application/json"
    }
    
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
        "timestamp": timestamp
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, verify=False, timeout=10)
        response.raise_for_status()

        # Parse response JSON để lấy message
        response_json = response.json()
        message = response_json.get("message", "No message returned")

        print("Message nhận được:", message)

        return {"message": message}, 200

    except requests.exceptions.RequestException as e:
        print("Lỗi khi gửi request:", e)
        return {"error": str(e)}, 500
    

def normalize_number(x):
    if x < 100:
        return round(x, 2)
    digits = int(math.log10(x)) + 1   # đếm số chữ số
    divisor = 10 ** (digits - 2)      # ví dụ 1234 → 10^(4-2)=100
    return round(x / divisor, 3)      # làm tròn 3 số sau dấu phẩy


async def service_get_data_sensor_predict():
    # Tắt warning SSL (do bypass SSL verification)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    url = "https://florus.hpcc.vn/api/aqi_server/predict"
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        json_path = os.path.join(os.getcwd(), "predict_data.json")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        response = requests.post(url, headers=headers, json=data, verify=False, timeout=10)
        response.raise_for_status()

        # Parse response JSON để lấy message
        response_json = response.json()
        message = response_json.get("message", "No message returned")
        data = response_json.get("data", "No data returned")
        data_list = data["value_72h"]
        seven_values = [normalize_number(v) for v in data_list[:7]]

        # giá trị thứ 24, 48, 72 (nếu có)
        values_24_48_72 = []
        for idx in [23, 47, 71]:
            if idx < len(data_list):
                values_24_48_72.append(normalize_number(data_list[idx]))

        print("7 giá trị đầu:", seven_values)
        print("Giá trị 24, 48, 72:", values_24_48_72)

        data = {
            "value_7h": seven_values,
            "value_24h": values_24_48_72[0],
            "value_48h": values_24_48_72[1],
            "value_72h": values_24_48_72[2],
        }

        return {"message": message, "data": data}, 200

    except requests.exceptions.RequestException as e:
        print("Lỗi khi gửi request:", e)
        return {"error": str(e)}, 500
