from fastapi import APIRouter, Depends, Request, Query
from fastapi.security import OAuth2PasswordBearer
from controller.sensors_controller import controller_post_data, controller_get_data_sensor_predict
from pydantic import BaseModel
from services.predict_sensors import aqi_overall_hourly_pm_only

router = APIRouter()


@router.post("/create")
async def create_sensor_data(request: Request):
    body = await request.json()
    return await controller_post_data(body)

class AQIPredictRequest(BaseModel):
    station_id: str
    timestamp: str  # "2025-11-28T00:00:00" ví dụ

@router.post("/predict")
async def get_data_sensor_predict(payload: AQIPredictRequest):
    return await controller_get_data_sensor_predict(payload)


class AQIRequest(BaseModel):
    pm25: float
    pm10: float
    no2: float
    o3: float
    so2: float
    co: float

@router.post("/aqi")
async def predict_aqi(payload: AQIRequest):
    data = payload.model_dump()

    # ---- AQI thành phần (đã là AQI, không tính lại) ----
    components = {
        "pm25": round(data["pm25"]),
        "pm10": round(data["pm10"]),
        "no2":  round(data["no2"]),
        "o3":   round(data["o3"]),
        "so2":  round(data["so2"]),
        "co":   round(data["co"]),
    }

    # ---- AQI tổng (PM only) ----
    aqi = aqi_overall_hourly_pm_only(components)

    # ---- Response đúng format bạn yêu cầu ----
    return {
        "pm25Aqi": data["pm25"],
        "pm10Aqi": data["pm10"],
        "no2Aqi":  data["no2"],
        "o3Aqi":   data["o3"],
        "so2Aqi":  data["so2"],
        "coAqi":   data["co"],
        "aqi": aqi
    }
