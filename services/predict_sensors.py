
import numpy as np
from typing import List, Tuple, Optional, Dict



# Mức AQI
I_LEVELS = [0, 50, 100, 150, 200, 300, 400, 500]

# PM (µg/m3)
BP_PM25 = [0, 25, 50, 80, 150, 250, 350, 500]
BP_PM10 = [0, 50, 150, 250, 350, 420, 500, 600]

# Khí (µg/m3; CO theo bảng QĐ 1459 dùng 10.000, 30.000...)
BP_NO2  = [0, 100, 200, 700, 1200, 2350, 3100, 3850]
BP_SO2  = [0, 125, 350, 550, 800, 1600, 2100, 2630]
BP_CO   = [0, 10000, 30000, 45000, 60000, 90000, 120000, 150000]
BP_O3_1H = [0, 160, 200, 300, 400, 800, 1000, 1200]
BP_NO = [0, 50, 100, 200, 400, 800, 1200, 2000]

# O3 8h (µg/m3) – bảng quy định đến 400, tương ứng AQI đến 300
BP_O3_8H = [0, 100, 120, 170, 210, 400]
I_O3_8H  = [0, 50, 100, 150, 200, 300]

def build_piecewise(bps: List[float], Is: List[int]) -> List[Tuple[float,float,int,int]]:
    if len(bps) != len(Is):
        raise ValueError("bps và Is phải cùng chiều dài.")
    return [(bps[i], bps[i+1], Is[i], Is[i+1]) for i in range(len(bps)-1)]

PW_PM25  = build_piecewise(BP_PM25,  I_LEVELS)
PW_PM10  = build_piecewise(BP_PM10,  I_LEVELS)
PW_NO2   = build_piecewise(BP_NO2,   I_LEVELS)
PW_SO2   = build_piecewise(BP_SO2,   I_LEVELS)
PW_CO    = build_piecewise(BP_CO,    I_LEVELS)
PW_NO = build_piecewise(BP_NO, I_LEVELS)
PW_O3_1H = build_piecewise(BP_O3_1H, I_LEVELS)
PW_O3_8H = build_piecewise(BP_O3_8H, I_O3_8H)

def linear_aqi(C: float, pw: List[Tuple[float,float,int,int]], cap_hi: float = 500.0) -> float:
    """Nội suy tuyến tính cho AQI thành phần. cap_hi mặc định 500."""
    if C is None or (isinstance(C, float) and np.isnan(C)):
        return np.nan
    if C >= pw[-1][1]:
        return float(cap_hi)
    for BP_lo, BP_hi, I_lo, I_hi in pw:
        if BP_lo <= C <= BP_hi:
            return (I_hi - I_lo)/(BP_hi - BP_lo)*(C - BP_lo) + I_lo
    return np.nan

def linear_aqi_o3_8h(C: float) -> float:
    """O3-8h: bảng chỉ tới AQI=300 khi C>=400."""
    return linear_aqi(C, PW_O3_8H, cap_hi=300.0)



def nowcast_12h(c: List[float]) -> float:
    """
    c = [c1..c12], c1: giờ hiện tại, c12: 12 giờ trước.
    Rule missing (QĐ 1459): có >= 2/3 giá trị c1,c2,c3 mới tính.
    """
    if c is None or len(c) != 12:
        raise ValueError("Cần đúng 12 giá trị theo thứ tự [c1..c12].")

    c = np.array(c, dtype=float)

    if np.sum(~np.isnan(c[:3])) < 2:
        return np.nan

    if np.all(np.isnan(c)):
        return np.nan

    Cmin, Cmax = np.nanmin(c), np.nanmax(c)
    if Cmax <= 0 or np.isnan(Cmin) or np.isnan(Cmax):
        return np.nan

    w = max(0.5, Cmin / Cmax)

    weights = np.power(w, np.arange(12, dtype=float))  # w^(i-1)
    weights[np.isnan(c)] = 0.0

    den = float(np.sum(weights))
    if den == 0.0:
        return np.nan

    return float(np.nansum(c * weights) / den)



def max_8h_mean_o3(o3_extended_31h: List[float]) -> float:
    """
    Tính TB8h lớn nhất của O3 trong ngày.
    Input khuyến nghị: 31 giá trị liên tục = 7 giờ trước 01:00 + 24 giờ của ngày.
    Mặc định: cửa sổ TB8h yêu cầu đủ 8 giá trị (không NaN) để tính.
    """
    arr = np.array(o3_extended_31h, dtype=float)
    if len(arr) < 8:
        return np.nan

    max8 = np.nan
    for end in range(7, len(arr)):
        window = arr[end-7:end+1]
        if np.any(np.isnan(window)):
            continue
        mean8 = float(np.mean(window))
        if np.isnan(max8) or mean8 > max8:
            max8 = mean8
    return float(max8)



def aqi_components_hourly(
    pm25_c1_to_c12: Optional[List[float]] = None,
    pm10_c1_to_c12: Optional[List[float]] = None,
    no2_1h: Optional[float] = None,
    so2_1h: Optional[float] = None,
    o3_1h: Optional[float] = None,
    co_1h: Optional[float] = None,
    no_1h: Optional[float] = None,
) -> Dict[str, Optional[int]]:
    out: Dict[str, Optional[int]] = {}

    # PM: Nowcast -> AQI
    if pm25_c1_to_c12 is not None:
        v = linear_aqi(nowcast_12h(pm25_c1_to_c12), PW_PM25)
        out["pm25"] = None if np.isnan(v) else int(round(v))
    else:
        out["pm25"] = None

    if pm10_c1_to_c12 is not None:
        v = linear_aqi(nowcast_12h(pm10_c1_to_c12), PW_PM10)
        out["pm10"] = None if np.isnan(v) else int(round(v))
    else:
        out["pm10"] = None

    # Khí: TB1h -> AQI
    v = linear_aqi(no2_1h, PW_NO2)
    out["no2"] = None if np.isnan(v) else int(round(v))

    v = linear_aqi(so2_1h, PW_SO2)
    out["so2"] = None if np.isnan(v) else int(round(v))

    v = linear_aqi(o3_1h, PW_O3_1H)
    out["o3"] = None if np.isnan(v) else int(round(v))

    v = linear_aqi(co_1h, PW_CO)
    out["co"] = None if np.isnan(v) else int(round(v))

    v = linear_aqi(no_1h, PW_NO)
    out["no"] = None if np.isnan(v) else int(round(v))

    return out

def aqi_overall_hourly_pm_only(components: Dict[str, Optional[int]]) -> Optional[int]:
    pm = [components.get("pm25"), components.get("pm10")]
    pm = [v for v in pm if v is not None]
    return None if len(pm) == 0 else int(max(pm))



def aqi_components_daily(
    pm25_24h: Optional[List[float]] = None,   # 24 giá trị TB1h (01:00..00:00)
    pm10_24h: Optional[List[float]] = None,
    no2_24h: Optional[List[float]] = None,    # 24 giá trị TB1h
    so2_24h: Optional[List[float]] = None,
    co_24h: Optional[List[float]] = None,
    o3_24h: Optional[List[float]] = None,     # 24 giá trị TB1h
    o3_extended_31h: Optional[List[float]] = None,  # 31 giá trị để tính TB8h
) -> Dict[str, Optional[int]]:
    out: Dict[str, Optional[int]] = {}

    # PM: TB24h
    if pm25_24h is not None:
        v = linear_aqi(float(np.nanmean(pm25_24h)), PW_PM25)
        out["pm25"] = None if np.isnan(v) else int(round(v))
    else:
        out["pm25"] = None

    if pm10_24h is not None:
        v = linear_aqi(float(np.nanmean(pm10_24h)), PW_PM10)
        out["pm10"] = None if np.isnan(v) else int(round(v))
    else:
        out["pm10"] = None

    # NO2/SO2/CO: max TB1h trong ngày
    v = linear_aqi(float(np.nanmax(no2_24h)) if no2_24h is not None else None, PW_NO2)
    out["no2"] = None if np.isnan(v) else int(round(v))

    v = linear_aqi(float(np.nanmax(so2_24h)) if so2_24h is not None else None, PW_SO2)
    out["so2"] = None if np.isnan(v) else int(round(v))

    v = linear_aqi(float(np.nanmax(co_24h)) if co_24h is not None else None, PW_CO)
    out["co"] = None if np.isnan(v) else int(round(v))

    # O3: xét max TB1h và max TB8h; nếu max8h > 400 => chỉ dùng 1h
    aqi_o3 = np.nan
    if o3_24h is not None:
        max1h = float(np.nanmax(o3_24h))
        aqi_1h = linear_aqi(max1h, PW_O3_1H)

        max8h = np.nan
        if o3_extended_31h is not None:
            max8h = max_8h_mean_o3(o3_extended_31h)

        if not np.isnan(max8h) and max8h <= 400:
            aqi_8h = linear_aqi_o3_8h(max8h)
            aqi_o3 = max(aqi_1h, aqi_8h)
        else:
            aqi_o3 = aqi_1h

    out["o3"] = None if (aqi_o3 is None or np.isnan(aqi_o3)) else int(round(aqi_o3))

    return out

def aqi_overall_daily_pm_only(components_daily: Dict[str, Optional[int]]) -> Optional[int]:
    pm = [components_daily.get("pm25"), components_daily.get("pm10")]
    pm = [v for v in pm if v is not None]
    return None if len(pm) == 0 else int(max(pm))



# # ---- dữ liệu demo ----
# pm25_24h = [
#     55, 56, 58, 60, 62, 63,
#     65, 67, 68, 70, 72, 73,
#     74, 73, 72, 70, 68, 66,
#     64, 62, 60, 58, 56, 55
# ]

# pm10_24h = [
#     80, 82, 85, 88, 90, 92,
#     95, 97, 98, 100, 102, 103,
#     105, 103, 102, 100, 98, 96,
#     94, 92, 90, 88, 85, 82
# ]

# no2_24h = [180]*24
# so2_24h = [200]*24
# co_24h  = [8000]*24
# o3_24h  = [250]*24

# # 31h cho O3 TB8h: 7h trước + 24h trong ngày
# o3_ext_31h = [240, 242, 245, 247, 248, 249, 250] + o3_24h

# components_d = aqi_components_daily(
#     pm25_24h=pm25_24h,
#     pm10_24h=pm10_24h,
#     no2_24h=no2_24h,
#     so2_24h=so2_24h,
#     co_24h=co_24h,
#     o3_24h=o3_24h,
#     o3_extended_31h=o3_ext_31h
# )

# aqi_daily_pm = aqi_overall_daily_pm_only(components_d)

# print("AQI ngày theo chất:")
# for pol, aqi in components_d.items():
#     print(f"  - {pol}: {aqi}")
# print("AQI ngày (PM-only):", aqi_daily_pm)


# #VD cho AQI giờ
# pm25_12h = [55, 58, 60, 62, 65, 63, 61, 59, 57, 56, 54, 52]
# pm10_12h = [80, 85, 90, 88, 92, 95, 93, 90, 87, 85, 83, 82]

# components = aqi_components_hourly(
#     pm25_c1_to_c12=pm25_12h,
#     pm10_c1_to_c12=pm10_12h,
#     no2_1h=180,
#     so2_1h=200,
#     o3_1h=250,
#     co_1h=8000,
# )

# aqi_overall_pm = aqi_overall_hourly_pm_only(components)

# components, aqi_overall_pm
# for pollutant, aqi in components.items():
#     print(f"AQI {pollutant}: {aqi}")

# aqi_overall_pm = aqi_overall_hourly_pm_only(components)
# print("AQI giờ (PM-only):", aqi_overall_pm)

# async def service_calculate_hourly_aqi() -> Dict:
#     """
#     data input ví dụ:
#     {
#       "pm25_12h": [...],
#       "pm10_12h": [...],
#       "no2_1h": 180,
#       "so2_1h": 200,
#       "o3_1h": 250,
#       "co_1h": 8000
#     }
#     """

#     data = {
#         "pm25_12h": [55, 58, 60, 62, 65, 63, 61, 59, 57, 56, 54, 52],
#         "pm10_12h": [80, 85, 90, 88, 92, 95, 93, 90, 87, 85, 83, 82],
#         "no2_1h": 180,
#         "so2_1h": 200,
#         "o3_1h": 250,
#         "co_1h": 8000
#     }

#     components = aqi_components_hourly(
#         pm25_c1_to_c12=data.get("pm25_12h"),
#         pm10_c1_to_c12=data.get("pm10_12h"),
#         no2_1h=data.get("no2_1h"),
#         so2_1h=data.get("so2_1h"),
#         o3_1h=data.get("o3_1h"),
#         co_1h=data.get("co_1h"),
#     )

#     aqi_pm_only = aqi_overall_hourly_pm_only(components)

#     return {
#         "components": components,
#         "aqi_pm_only": aqi_pm_only
#     }

from typing import Dict

def convert_no_ppm_to_ugm3(no_ppm: float) -> float:
    """
    Convert NO from ppm to µg/m³
    Công thức chuẩn ở 25°C, 1 atm
    """
    if no_ppm is None or np.isnan(no_ppm):
        return np.nan

    MOLAR_MASS_NO = 30.01  # g/mol
    return no_ppm * MOLAR_MASS_NO * 1000 / 24.45

async def service_calculate_hourly_aqi(data: Dict) -> Dict:
    components = aqi_components_hourly(
        pm25_c1_to_c12=data.get("pm25_12h"),
        pm10_c1_to_c12=data.get("pm10_12h"),
        no2_1h=data.get("no2_1h"),
        so2_1h=data.get("so2_1h"),
        o3_1h=data.get("o3_1h"),
        co_1h=data.get("co_1h"),
        no_1h=convert_no_ppm_to_ugm3(data.get("no_1h")),
    )

    aqi_pm_only = aqi_overall_hourly_pm_only(components)

    components["aqi"] = aqi_pm_only

    print("AQI PM Only:", aqi_pm_only)

    # return {
    #     "components": components,
    #     "aqi_pm_only": aqi_pm_only
    # }
    return components

