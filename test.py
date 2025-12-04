from typing import Dict, List, Tuple, Optional
import math
import numpy as np

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
BP_O3  = [0, 160, 200, 300, 400, 800, 1000, 1200]

PW_PM25  = build_piecewise(BP_PM25,  I_levels)
PW_PM10  = build_piecewise(BP_PM10,  I_levels)
PW_NO2   = build_piecewise(BP_NO2,   I_levels)
PW_SO2   = build_piecewise(BP_SO2,   I_levels)
PW_CO    = build_piecewise(BP_CO,    I_levels)
PW_O3 = build_piecewise(BP_O3, I_levels)

def nowcast_12h(values_12h):
    count_nan = 0
    for i in [values_12h[-1], values_12h[-2], values_12h[-3]]:
        if np.isnan(i):
            count_nan += 1
    if count_nan < 2:
        return np.nan
    
    w_asterisk = np.nanmin(np.array(values_12h))/np.nanmax(np.array(values_12h))
    if np.isnan(w_asterisk):
        return np.nan

    if w_asterisk <= 0.5:
        w = 0.5
    else:
        w = w_asterisk

    if w == 0.5:
        ans = 0.0
        for i, v in enumerate(values_12h):
            if np.isnan(i):
                continue
            wi = w**i
            ans += wi&v
        return ans
    else:
        num = 0.0
        den = 0.0
        
        for i, v in enumerate(values_12h):
            if np.isnan(i):
                continue
            wi = w**i
            num += v * wi
            den += wi

        return num/den

def aqi_hourly(pm25_1h: Optional[float],
               pm10_1h: Optional[float],
               no2_1h: Optional[float],
               o3_1h: Optional[float],
               so2_1h: Optional[float],
               co_1h: Optional[float] = None):
   
    aqi_pm25 = linear_aqi(pm25_1h, PW_PM25)
    aqi_pm10  = linear_aqi(pm10_1h, PW_PM10) 
    aqi_no2 = linear_aqi(no2_1h, PW_NO2) 
    aqi_o3  = linear_aqi(o3_1h,  PW_O3)
    aqi_so2 = linear_aqi(so2_1h, PW_SO2) 
    aqi_co2 = linear_aqi(co_1h, PW_CO) 

    return np.nanmax(np.array([aqi_pm25, aqi_pm10, aqi_no2, aqi_o3, aqi_so2, aqi_co2]))

if __name__ == "__main__":
    print(    aqi_hourly(
        pm25_1h=25,
        pm10_1h=25,
        no2_1h=180,     # µg/m3
        o3_1h=250,      # µg/m3
        so2_1h=200,     # µg/m3
        co_1h=8000   
    ))

