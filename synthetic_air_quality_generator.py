
# Synthetic Air Quality Data Generator
# -----------------------------------
# Generate hourly pollutant data for each station based on
# hourly × quarterly statistics (avg/min/max).

# Input:
# - hourly_quarter_stats_by_station.csv

# Output:
# - Functions to generate synthetic values and time series



import pandas as pd
import numpy as np

# ===============================
# Load statistics
# ===============================
def load_stats(csv_path):
    """
    Load hourly-quarterly statistics file.
    """
    return pd.read_csv(csv_path)


# ===============================
# Core sampling utilities
# ===============================
def generate_value_from_stats(avg, vmin, vmax, rng=None):
    """
    Generate a random value within [vmin, vmax]
    centered around avg using truncated normal sampling.
    """
    if rng is None:
        rng = np.random.default_rng()

    if pd.isna(avg) or pd.isna(vmin) or pd.isna(vmax) or vmax <= vmin:
        return np.nan

    sigma = (vmax - vmin) / 6.0  # ~99.7% within bounds

    for _ in range(10):
        x = rng.normal(avg, sigma)
        if vmin <= x <= vmax:
            return x

    return np.clip(avg, vmin, vmax)


def generate_pollutant_value(
    station_id,
    pollutant,
    timestamp,
    stats_df,
    rng=None
):
    """
    Generate one pollutant value for a station at a given timestamp.
    """
    if rng is None:
        rng = np.random.default_rng()

    ts = pd.to_datetime(timestamp)
    hour = ts.hour
    quarter = ts.quarter

    row = stats_df[
        (stats_df.station_id == station_id) &
        (stats_df.quarter == quarter) &
        (stats_df.hour == hour)
    ]

    if row.empty:
        return np.nan

    avg = row[f"{pollutant}_avg"].values[0]
    vmin = row[f"{pollutant}_min"].values[0]
    vmax = row[f"{pollutant}_max"].values[0]

    return generate_value_from_stats(avg, vmin, vmax, rng)


# ===============================
# High-level generators
# ===============================
POLLUTANTS = ["PM25", "NO2", "O3", "CO", "SO2", "TSP"]


def generate_station_record(
    station_id,
    timestamp,
    stats_df,
    rng=None
):
    """
    Generate a full pollutant record for one station at one timestamp.
    """
    record = {
        "station_id": station_id,
        "timestamp": pd.to_datetime(timestamp)
    }

    for pol in POLLUTANTS:
        record[pol] = generate_pollutant_value(
            station_id,
            pol,
            timestamp,
            stats_df,
            rng
        )

    return record


def generate_time_series(
    station_id,
    start_time,
    end_time,
    freq="1H",
    stats_df=None,
    seed=42
):
    """
    Generate a synthetic hourly time series for one station.
    """
    rng = np.random.default_rng(seed)
    times = pd.date_range(start=start_time, end=end_time, freq=freq)

    records = [
        generate_station_record(station_id, t, stats_df, rng)
        for t in times
    ]

    return pd.DataFrame(records)


# ===============================
# Example usage
# ===============================
if __name__ == "__main__":
    stats = load_stats("hourly_quarter_stats_by_station.csv")

    df_sim = generate_time_series(
        station_id=211,
        start_time="2025-12-20 00:00",
        end_time="2025-12-30 23:00",
        stats_df=stats
    )

    df_sim.to_csv("synthetic_station_211.csv", index=False)
    print("Synthetic data generated: synthetic_station_211.csv")
