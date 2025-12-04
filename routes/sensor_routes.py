from fastapi import APIRouter, Depends, Request, Query
from fastapi.security import OAuth2PasswordBearer
from controller.sensors_controller import controller_post_data, controller_get_data_sensor_predict, get_aqi
from pydantic import BaseModel

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
    # Tạo payload đơn giản
    class Payload:
        pass
    p = Payload()
    p.station_id = payload.station_id
    p.timestamp = payload.timestamp

    print(payload)

    return await controller_get_data_sensor_predict(p)

class AQIRequest(BaseModel):
    pm25: float
    pm10: float
    no2: float
    o3: float
    so2: float
    co: float

@router.post("/aqi")
async def predict_aqi(payload: AQIRequest):
    return await get_aqi(payload.model_dump())