import requests
from typing import Dict, Any, List


PREDICT_API_URL = "https://florus.hpcc.vn/api/aqi_server/prediction"


async def service_get_predicted_aqi(
    station_id: str,
    timestamp: str,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Call prediction API → build AQI input
    """

    print(timestamp)

    payload = {
        "station_id": station_id,
        "timestamp": timestamp,
        "limit": limit,
        "offset": 0,
        "flag": False
    }

    res = requests.get(PREDICT_API_URL, json=payload, timeout=10, verify=False)

    res.raise_for_status()

    data = res.json()
    predictions = data.get("prediction", [])

    if not predictions:
        raise ValueError("No prediction data returned")

    # sort theo thời gian tăng dần
    predictions = sorted(
        predictions,
        key=lambda x: x["timestamp"]
    )

    # lấy 12 giờ gần nhất
    pm25_12h: List[float] = [
        p.get("pm25_predicted") for p in predictions[:12]
    ]

    pm10_12h: List[float] = [
        p.get("pm10_predicted") for p in predictions[:12]
    ]

    # lấy giá trị 1h gần nhất
    latest = predictions[-1]

    aqi_input = {
        "pm25_12h": pm25_12h,
        "pm10_12h": pm10_12h,
        "no2_1h": latest.get("no2_predicted"),
        "so2_1h": latest.get("so2_predicted"),
        "o3_1h": latest.get("o3_predicted"),
        "co_1h": latest.get("co_predicted"),
    }

    return aqi_input

import asyncio

station_id = "215"
timestamp = "2025-12-27T00:00:00"

async def main():
    result = await service_get_predicted_aqi(
        station_id=station_id,
        timestamp=timestamp
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())