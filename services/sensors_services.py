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
