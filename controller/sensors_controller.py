
from services.sensors_services import service_post_all_data, service_get_predicted_aqi
from fastapi.responses import JSONResponse
import numpy as np
from typing import List, Tuple, Optional
from fastapi import HTTPException
from typing import Dict

def linear_aqi(C: float, bp: List[Tuple[float, float, int, int]]) -> Optional[int]:
    for BP_lo, BP_hi, I_lo, I_hi in bp:
        if BP_lo <= C <= BP_hi:
            val = (I_hi - I_lo) / (BP_hi - BP_lo) * (C - BP_lo) + I_lo
            return int(round(val))
    return np.nan

def build_piecewise(bps: List[float], Is: List[int]) -> List[Tuple[float, float, int, int]]:
    out = []
    for i in range(len(bps)-1):
        out.append((bps[i], bps[i+1], Is[i], Is[i+1]))
    return out

I_levels = [0, 50, 100, 150, 200, 300, 400, 500]

BP_PM25   = [0, 25, 50, 80, 150, 250, 350, 500]
BP_PM10   = [0, 50, 150, 250, 350, 420, 500, 600]
BP_NO2    = [0, 100, 200, 700, 1200, 2350, 3100, 3850]
BP_SO2    = [0, 125, 350, 550, 800, 1600, 2100, 2630]
BP_CO     = [0, 10000, 30000, 45000, 60000, 90000, 120000, 150000]
BP_O3     = [0, 160, 200, 300, 400, 800, 1000, 1200]

PW_PM25  = build_piecewise(BP_PM25,  I_levels)
PW_PM10  = build_piecewise(BP_PM10,  I_levels)
PW_NO2   = build_piecewise(BP_NO2,   I_levels)
PW_SO2   = build_piecewise(BP_SO2,   I_levels)
PW_CO    = build_piecewise(BP_CO,    I_levels)
PW_O3    = build_piecewise(BP_O3,    I_levels)

def aqi_hourly(pm25_1h: Optional[float],
               pm10_1h: Optional[float],
               no2_1h: Optional[float],
               o3_1h: Optional[float],
               so2_1h: Optional[float],
               co_1h: Optional[float] = None):
   
    aqi_pm25 = linear_aqi(pm25_1h, PW_PM25)
    aqi_pm10 = linear_aqi(pm10_1h, PW_PM10) 
    aqi_no2  = linear_aqi(no2_1h, PW_NO2) 
    aqi_o3   = linear_aqi(o3_1h, PW_O3)
    aqi_so2  = linear_aqi(so2_1h, PW_SO2) 
    aqi_co2  = linear_aqi(co_1h, PW_CO) 

    return int(np.nanmax([aqi_pm25, aqi_pm10, aqi_no2, aqi_o3, aqi_so2, aqi_co2]))

async def controller_post_data(body):
    try:
        data, status = await service_post_all_data(body)
        response = {
            "message": data.get('message'),
            "data": data.get('data'),
            "status": status,
            "errCode": 0
        }
        return JSONResponse(content=response, status_code=status)
    except Exception as e:
        return {
            "status": 500,
            "message": str(e),
            "error": 1
        }, 500
    

async def controller_get_data_sensor_predict(payload):
    try:
        data = await service_get_predicted_aqi(payload)
        response = {
            "message": data.get('message'),
            "data": data.get('predictions'),
            "status": 200,
            "errCode": 0
        }
        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={
            "status": 500,
            "message": str(e),
            "error": 1
        }, status_code=500)

async def get_aqi(data: Dict):
    """
    data: dict có keys pm25_1h, pm10_1h, no2_1h, o3_1h, so2_1h, co_1h
    """
    try:
        pm25 = float(data.get("pm25"))
        pm10 = float(data.get("pm10"))
        no2  = float(data.get("no2"))
        o3   = float(data.get("o3"))
        so2  = float(data.get("so2"))
        co   = float(data.get("co"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input data: {e}")

    aqi = aqi_hourly(pm25, pm10, no2, o3, so2, co)

    return {
        "pm25Aqi": pm25,
        "pm10Aqi": pm10,
        "no2Aqi": no2,
        "o3Aqi": o3,
        "so2Aqi": so2,
        "coAqi": co,
        "aqi": aqi
    }