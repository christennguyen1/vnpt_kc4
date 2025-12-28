from typing import Optional
from fastapi import APIRouter, Depends, Request, Query
from fastapi.security import OAuth2PasswordBearer
from controller.sensors_controller import controller_post_data, controller_get_data_sensor_predict
from getDataCoreIot import get_pm_aqi_arrays
from pydantic import BaseModel
from services.predict_sensors import aqi_overall_hourly_pm_only, service_calculate_hourly_aqi

router = APIRouter()


@router.post("/create")
async def create_sensor_data(request: Request):
    body = await request.json()
    return await controller_post_data(body)

class AQIPredictRequest(BaseModel):
    station_id: str
    timestamp: str  # "2025-11-28T00:00:00" ví dụ
    device_name: Optional[str] = None  # không bắt buộc

@router.post("/predict")
async def get_data_sensor_predict(payload: AQIPredictRequest):
    return await controller_get_data_sensor_predict(payload)


def convert_no2_ppm_to_ugm3(no2_ppm: float) -> Optional[float]:
    if no2_ppm is None:
        return None
    MOLAR_MASS_NO2 = 46.0055
    return no2_ppm * MOLAR_MASS_NO2 * 1000 / 24.45

def convert_so2_ppm_to_ugm3(so2_ppm: float) -> Optional[float]:
    if so2_ppm is None:
        return None
    MOLAR_MASS_SO2 = 64.066
    return so2_ppm * MOLAR_MASS_SO2 * 1000 / 24.45

def convert_o3_ppm_to_ugm3(o3_ppm: float) -> Optional[float]:
    if o3_ppm is None:
        return None
    MOLAR_MASS_O3 = 48.00
    return o3_ppm * MOLAR_MASS_O3 * 1000 / 24.45

def convert_co_ppm_to_ugm3(co_ppm: float) -> Optional[float]:
    if co_ppm is None:
        return None
    MOLAR_MASS_CO = 28.01
    return co_ppm * MOLAR_MASS_CO * 1000 / 24.45

class AQIRequest(BaseModel):
    device_name: str           # Lấy pm25/pm10 từ ThingsBoard
    pm10: Optional[float] = None
    pm25: Optional[float] = None
    no2: Optional[float] = None
    so2: Optional[float] = None
    o3: Optional[float] = None
    co: Optional[float] = None
    no: Optional[float] = None  # ppm

@router.post("/aqi")
async def predict_aqi(payload: AQIRequest):
    data = payload.model_dump()

    # Lấy PM từ ThingsBoard
    pm10_list, pm25_list = get_pm_aqi_arrays(data["device_name"])
    # Lấy 12 giờ gần nhất (last 12 elements)
    pm10_12h = pm10_list[-12:] if pm10_list else None
    pm25_12h = pm25_list[-12:] if pm25_list else None

    # Chuẩn bị dict cho service
    service_data = {
        "pm10_12h": pm10_12h,
        "pm25_12h": pm25_12h,
        "no2_1h": convert_no2_ppm_to_ugm3(data.get("no2")),
        "so2_1h": convert_so2_ppm_to_ugm3(data.get("so2")),
        "o3_1h": convert_o3_ppm_to_ugm3(data.get("o3")),
        "co_1h": convert_co_ppm_to_ugm3(data.get("co")),
        "no_1h": data.get("no"),
    }

    # Tính AQI
    components = await service_calculate_hourly_aqi(service_data)

    # Trả response đúng format
    return {
        "pm10": data.get("pm10"),
        "pm25": data.get("pm25"),
        "no2": data.get("no2"),
        "so2": data.get("so2"),
        "o3": data.get("o3"),
        "co": data.get("co"),
        "pm25Aqi": components.get("pm25"),
        "pm10Aqi": components.get("pm10"),
        "no2Aqi":  components.get("no2"),
        "o3Aqi":   components.get("o3"),
        "so2Aqi":  components.get("so2"),
        "coAqi":   components.get("co"),
        "noAqi":   components.get("no"),
        "aqi": components.get("aqi"),
    }
