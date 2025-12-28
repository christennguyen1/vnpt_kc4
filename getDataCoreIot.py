import requests
from datetime import datetime, timezone, timedelta

DEVICE_MAP = {
    "[KC] Air Quality 4C": "b2bebec0-cdc2-11f0-b529-c7574d2602e9",
    "[KC] Air Quality 4B": "dcd92db0-4c5f-11f0-8f88-735b2578d56c",
    "[KC] Air Quality 4A": "d51f0770-4c5f-11f0-8f88-735b2578d56c",

    "[KC] Air Quality 3A": "ad07a990-4c5f-11f0-8f88-735b2578d56c",
    "[KC] Air Quality 3C": "bed52850-4c5f-11f0-8f88-735b2578d56c",

    "[KC] Air Quality 2A": "81e57cb0-4c5f-11f0-8f88-735b2578d56c",
    "[KC] Air Quality 2B": "4103fd70-4c5f-11f0-8f88-735b2578d56c",
    "[KC] Air Quality 2C": "49bb2150-4c5f-11f0-8f88-735b2578d56c",

    "[KC] Air Quality 1A": "90b5ca50-1754-11f0-b943-e12b9c63441a",
    "[KC] Air Quality 1B": "58980540-4c5e-11f0-8f88-735b2578d56c",
}

def get_device_id(device_name: str) -> str:
    try:
        return DEVICE_MAP[device_name]
    except KeyError:
        raise ValueError(f"❌ Device name không tồn tại: {device_name}")


# ===============================
# 1. Login ThingsBoard
# ===============================
def login_thingsboard():
    url = "https://app.coreiot.io/api/auth/login"
    payload = {
        "username": "doquangkhanh15@gmail.com",
        "password": "Khanh1512200215!"
    }

    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()["token"]


# ===============================
# 2. Lấy epoch giờ tròn hiện tại & 12h trước (VN)
# ===============================
def current_and_12h_before_epoch_round_vn():
    vn_tz = timezone(timedelta(hours=7))

    now = datetime.now(vn_tz)
    rounded = now.replace(minute=0, second=0, microsecond=0)

    end_ts = int(rounded.timestamp() * 1000)
    start_ts = end_ts - 12 * 60 * 60 * 1000

    return start_ts, end_ts


# ===============================
# 3. Convert telemetry -> arrays value[]
# ===============================
def telemetry_to_value_arrays(telemetry_json):
    result = {}

    for key, items in telemetry_json.items():
        # sort theo timestamp cho chắc
        items_sorted = sorted(items, key=lambda x: x["ts"])
        result[key] = [float(item["value"]) for item in items_sorted]

    return result


# ===============================
# 4. Gọi API telemetry
# ===============================
def get_pm_aqi_arrays(device_name: str):
    device_id = get_device_id(device_name)

    token = login_thingsboard()
    start_ts, end_ts = current_and_12h_before_epoch_round_vn()

    url = (
        f"https://app.coreiot.io/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries"
        f"?keys=pm10Aqi,pm25Aqi"
        f"&startTs={start_ts}"
        f"&endTs={end_ts}"
        f"&interval=3600000"
        f"&agg=AVG"
        f"&limit=1000"
        f"&useStrictDataTypes=false"
    )

    headers = {
        "X-Authorization": f"Bearer {token}"
    }

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    data = telemetry_to_value_arrays(resp.json())

    return data['pm10Aqi'], data['pm25Aqi']


# ===============================
# 5. Run
# ===============================
if __name__ == "__main__":
    DEVICE_NAME = "[KC] Air Quality 4A"

    pm10_aqi, pm25_aqi = get_pm_aqi_arrays(DEVICE_NAME)
    print(pm10_aqi)
    print(pm25_aqi)
