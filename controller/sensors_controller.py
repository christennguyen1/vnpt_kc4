
from getDataCoreIot import get_pm_aqi_arrays
from services.sensors_services import service_get_predicted_aqi, service_post_all_data
from fastapi.responses import JSONResponse
import numpy as np
from typing import List, Tuple, Optional
from fastapi import HTTPException
from typing import Dict

from services.predict_sensors import service_calculate_hourly_aqi


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
    
def build_pm_12h(
    pm_hist: List[float],
    pm_future: List[float],
    future_hours: int
) -> List[float]:
    """
    future_hours: 1 | 2 | 3
    """
    past_count = 12 - future_hours
    return pm_hist[-past_count:] + pm_future[:future_hours]


# async def controller_get_data_sensor_predict(payload):
#     try:
#         station_id = payload.station_id
#         timestamp = payload.timestamp

#         data = await service_get_predicted_aqi(
#             station_id=station_id,
#             timestamp=timestamp
#         )

#         # data = {
#         #     "pm25_12h": [55, 58, 60, 62, 65, 63, 61, 59, 57, 56, 54, 52],
#         #     "pm10_12h": [80, 85, 90, 88, 92, 95, 93, 90, 87, 85, 83, 82],
#         #     "no2_1h": 180,
#         #     "so2_1h": 200,
#         #     "o3_1h": 250,
#         #     "co_1h": 8000
#         # }

#         # ví dụ data["predictions"] chứa:
#         # pm25_12h, pm10_12h, no2_1h, so2_1h, o3_1h, co_1h

#         print("Prediction Data: ", data)

#         aqi_result = await service_calculate_hourly_aqi(data)

#         print("AQI Result: ", aqi_result)

#         response = {
#             "message": "OK",
#             "data": {
#                 "prediction": data,
#                 "aqi": aqi_result
#             },
#             "status": 200,
#             "errCode": 0
#         }

#         return JSONResponse(content=response, status_code=200)

#     except Exception as e:
#         return JSONResponse(
#             content={
#                 "status": 500,
#                 "message": str(e),
#                 "error": 1
#             },
#             status_code=500
#         )

async def controller_get_data_sensor_predict(payload):
    try:
        station_id = payload.station_id
        timestamp = payload.timestamp

        # 1️⃣ Lấy PM quá khứ
        pm10_hist, pm25_hist = get_pm_aqi_arrays("[KC] Air Quality 4A")

        # 2️⃣ Lấy future prediction
        future = await service_get_predicted_aqi(
            station_id=station_id,
            timestamp=timestamp
        )

        result = {}

        for i, hour in enumerate([1, 2, 3]):
            pm25_12h = build_pm_12h(
                pm25_hist,
                [f["pm25"] for f in future],
                hour
            )

            pm10_12h = build_pm_12h(
                pm10_hist,
                [f["pm10"] for f in future],
                hour
            )

            data_input = {
                "pm25_12h": pm25_12h,
                "pm10_12h": pm10_12h,
                "no2_1h": future[i]["no2"],
                "so2_1h": future[i]["so2"],
                "o3_1h": future[i]["o3"],
                "co_1h": future[i]["co"],
                "no_1h": future[i]["no"],
            }

            aqi = await service_calculate_hourly_aqi(data_input)

            result[f"{hour}h"] = {
                **aqi,
                "timestamp": future[i]["timestamp"],
                "station_id": station_id
            }

        return JSONResponse(
            content={
                "status": 200,
                "message": "OK",
                "data": result,
                "errCode": 0
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": str(e), "error": 1}
        )
