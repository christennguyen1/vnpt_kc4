from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder 
from schemas import SensorData, SensorDataWeek, SensorDataDay, SensorDataMonth
import asyncio
from datetime import datetime, timedelta, timezone
import pandas as pd
from dateutil.relativedelta import relativedelta
import pytz
import requests
import urllib3

async def service_post_all_data(body):
    # Tắt warning SSL (do bypass SSL verification)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # URL API
    url = "https://florus.hpcc.vn/api/external/data"
    
    # Header
    headers = {
        "Content-Type": "application/json"
    }
    
    # Dữ liệu gửi lên
    data = {
        "device_name": "Sensor HCM",
        "dataset": "aqi_index_mr_nhan",
        "device_token": "cvcvxcv",
        "longitude": 232.3123,
        "latitude": 32.4324,
        "no2": 123.1,
        "so2": 321.1,
        "o3": 123.1,
        "pm25": 123.1,
        "pm10": 123.1,
        "aqi": 112,
        "no2Aqi": 18,
        "so2Aqi": 10,
        "o3Aqi": 25,
        "pm25Aqi": 55,
        "pm10Aqi": 70,
        "coAqi": 8,
        "timestamp": "2025-08-21T08:15:55.726+00:00"
    }
    
    # Gửi request POST với verify=False (bỏ qua kiểm tra SSL)
    try:
        response = requests.post(url, headers=headers, json=data, verify=False, timeout=10)
        response.raise_for_status()  # Nếu HTTP trả lỗi sẽ raise exception
        print("Gửi thành công. Phản hồi từ server:")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print("Lỗi khi gửi request:", e)

    return response,200

