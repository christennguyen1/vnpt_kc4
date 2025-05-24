from datetime import datetime
import requests
import pytz

async def service_post_all_data(body):
    data = body
    
    device_name = str(data.get('device_name', ""))
    aqi = float(data.get('aqi', 0))
    no2Aqi = float(data.get('no2Aqi', 0))
    so2Aqi = float(data.get('so2Aqi', 0))
    o3Aqi = float(data.get('o3Aqi', 0))
    pm25Aqi = float(data.get('pm25Aqi', 0))
    pm10Aqi = float(data.get('pm10Aqi', 0))
    coAqi = float(data.get('coAqi', 0))
    
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    vietnam_time = datetime.now(vietnam_tz)
    
    formatted_time = vietnam_time.strftime("%Y-%m-%dT%H:%M:%S")
    print(f"Thời gian nhận dữ liệu: {formatted_time}")

    
    # URL và timeout chung
    login_url = "http://123.25.190.46:8081/v1/login"
    air_quality_url = "http://123.25.190.46:8081/v1/air-quality"
    timeout = 60

    # Login để lấy token
    try:
        login_headers = {"Content-Type": "application/json"}
        login_payload = {"username": "user", "password": "password123"}
        login_response = requests.post(login_url, json=login_payload, headers=login_headers, timeout=timeout)
        login_response.raise_for_status()
        token = login_response.json()["token"]
        print("Login thành công")
    except Exception as e:
        print(f"Lỗi login: {e}")
        return

    # Gửi air quality
    air_quality_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    air_quality_payload = {
        "device_name": device_name,
        "aqi": aqi,
        "no2Aqi": no2Aqi,
        "so2Aqi": so2Aqi,
        "o3Aqi": o3Aqi,
        "pm25Aqi": pm25Aqi,
        "pm10Aqi": pm10Aqi,
        "coAqi": coAqi,
        "timestamp": str(formatted_time)
    }

    try:
        air_quality_response = requests.post(air_quality_url, json=air_quality_payload, headers=air_quality_headers, timeout=timeout)
        air_quality_response.raise_for_status()
        print("Gửi air quality thành công:", air_quality_response.json())
    except requests.exceptions.HTTPError as e:
        if air_quality_response.status_code in (401, 403):  # Lỗi xác thực
            print(f"Lỗi xác thực: {e}, thử login lại")
            try:
                # Login lại để lấy token mới
                login_response = requests.post(login_url, json=login_payload, headers=login_headers, timeout=timeout)
                login_response.raise_for_status()
                token = login_response.json()["token"]
                print("Login lại thành công")
                
                # Gửi lại air quality với token mới
                air_quality_headers["Authorization"] = f"Bearer {token}"
                air_quality_response = requests.post(air_quality_url, json=air_quality_payload, headers=air_quality_headers, timeout=timeout)
                air_quality_response.raise_for_status()
                print("Gửi air quality thành công:", air_quality_response.json())
            except Exception as retry_e:
                print(f"Lỗi khi thử lại: {retry_e}")
        else:
            print(f"Lỗi HTTP: {e}")
    except Exception as e:
        print(f"Lỗi gửi air quality: {e}")
    
    # Trả về thông tin sau khi xử lý
    response = {
        'message': 'Data sensors post successfully',
        'data': air_quality_payload
    }
    
    return response, 201

