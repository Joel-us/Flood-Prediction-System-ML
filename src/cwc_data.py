import duckdb
import pandas as pd
import numpy as np
from datetime import timedelta


# ============================================================
# CWC DATA SOURCES
# ============================================================

CWC_STATIONS_URL = (
    "https://diagram-chasing.github.io/cwc-flood-forecasts/stations.parquet"
)

CWC_DAILY_URL = (
    "https://diagram-chasing.github.io/cwc-flood-forecasts/daily.parquet"
)


# ============================================================
# LOAD CWC STATIONS
# ============================================================

def load_cwc_stations():
    """
    Load CWC station information.

    Returns:
        pandas.DataFrame
    """

    query = f"""
        SELECT
            station_code,
            name,
            lat,
            lon,
            nearest_town,
            warning_level,
            danger_level
        FROM read_parquet('{CWC_STATIONS_URL}')
        WHERE lat IS NOT NULL
          AND lon IS NOT NULL
    """

    stations = duckdb.sql(query).df()

    stations["lat"] = pd.to_numeric(
        stations["lat"],
        errors="coerce"
    )

    stations["lon"] = pd.to_numeric(
        stations["lon"],
        errors="coerce"
    )

    stations["warning_level"] = pd.to_numeric(
        stations["warning_level"],
        errors="coerce"
    )

    stations["danger_level"] = pd.to_numeric(
        stations["danger_level"],
        errors="coerce"
    )

    stations = stations[
        stations["lat"].notna()
        & stations["lon"].notna()
    ].copy()

    return stations


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate great-circle distance in kilometers.
    """

    R = 6371.0

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)

    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    a = np.clip(a, 0, 1)

    return 2 * R * np.arcsin(
        np.sqrt(a)
    )


# ============================================================
# GET LATEST AVAILABLE CWC WATER-LEVEL DATE
# ============================================================

def get_latest_cwc_date():
    """
    Find the latest date actually available in the CWC HHS
    water-level dataset.

    We do NOT use CURRENT_DATE because the CWC parquet may
    be several days behind the current calendar date.
    """

    query = f"""
        SELECT MAX(date_ist) AS latest_date
        FROM read_parquet('{CWC_DAILY_URL}')
        WHERE datatype_code = 'HHS'
          AND mean IS NOT NULL
    """

    result = duckdb.sql(query).df()

    latest_date = result.iloc[0]["latest_date"]

    if pd.isna(latest_date):
        raise ValueError(
            "Could not determine the latest CWC water-level date."
        )

    return pd.Timestamp(latest_date).date()


# ============================================================
# GET STATIONS WITH RECENT WATER-LEVEL DATA
# ============================================================

def get_stations_with_recent_water_data(
    latest_date,
    days=14,
    min_observations=2
):
    """
    Find all stations having enough valid HHS observations
    during the latest available CWC period.

    Example:

        Latest CWC date = 2026-09-11
        days = 14

        Window:
            2026-08-28 -> 2026-09-11
    """

    start_date = (
        pd.Timestamp(latest_date)
        - pd.Timedelta(days=days)
    ).date()

    query = f"""
        SELECT
            station_code,
            COUNT(*) AS observation_count
        FROM read_parquet('{CWC_DAILY_URL}')
        WHERE datatype_code = 'HHS'
          AND date_ist BETWEEN ? AND ?
          AND mean IS NOT NULL
          AND max IS NOT NULL
          AND mean > -100
        GROUP BY station_code
        HAVING COUNT(*) >= ?
    """

    result = duckdb.execute(
        query,
        [
            start_date,
            latest_date,
            min_observations
        ]
    ).df()

    return set(
        result["station_code"].astype(str)
    )


# ============================================================
# FIND NEAREST USABLE CWC STATION
# ============================================================

def find_nearest_cwc_station(
    latitude,
    longitude
):
    """
    Find the nearest CWC station that:

    1. Has valid coordinates.
    2. Has Warning Level.
    3. Has Danger Level.
    4. Has enough recent HHS observations.

    Recent means relative to the latest date actually
    available in the CWC dataset.
    """

    latitude = float(latitude)
    longitude = float(longitude)

    if not -90 <= latitude <= 90:
        raise ValueError(
            f"Invalid latitude: {latitude}"
        )

    if not -180 <= longitude <= 180:
        raise ValueError(
            f"Invalid longitude: {longitude}"
        )

    print(
        "\nChecking latest available CWC data..."
    )

    # --------------------------------------------------------
    # Latest date in CWC dataset
    # --------------------------------------------------------

    latest_date = get_latest_cwc_date()

    print(
        f"Latest CWC water-level date: {latest_date}"
    )

    # --------------------------------------------------------
    # Stations with enough recent HHS data
    # --------------------------------------------------------

    available_station_codes = (
        get_stations_with_recent_water_data(
            latest_date,
            days=14,
            min_observations=2
        )
    )

    if not available_station_codes:
        raise ValueError(
            "No CWC stations have sufficient recent "
            "water-level observations."
        )

    print(
        f"Stations with recent water-level data: "
        f"{len(available_station_codes)}"
    )

    # --------------------------------------------------------
    # Load station metadata
    # --------------------------------------------------------

    stations = load_cwc_stations()

    if stations.empty:
        raise ValueError(
            "No CWC stations could be loaded."
        )

    # --------------------------------------------------------
    # Keep stations with both thresholds
    # --------------------------------------------------------

    stations = stations[
        stations["warning_level"].notna()
        & stations["danger_level"].notna()
    ].copy()

    # --------------------------------------------------------
    # Keep stations having recent HHS data
    # --------------------------------------------------------

    stations["station_code"] = (
        stations["station_code"]
        .astype(str)
    )

    stations = stations[
        stations["station_code"].isin(
            available_station_codes
        )
    ].copy()

    if stations.empty:
        raise ValueError(
            "No CWC station has both Warning/Danger levels "
            "and recent HHS water-level data."
        )

    # --------------------------------------------------------
    # Calculate geographic distance
    # --------------------------------------------------------

    stations["distance_km"] = haversine_distance(
        latitude,
        longitude,
        stations["lat"].astype(float),
        stations["lon"].astype(float)
    )

    # --------------------------------------------------------
    # Sort nearest first
    # --------------------------------------------------------

    stations = stations.sort_values(
        "distance_km"
    ).reset_index(drop=True)

    station = stations.iloc[0]

    return {
        "station_code": station["station_code"],

        "name": station["name"],

        "latitude": float(
            station["lat"]
        ),

        "longitude": float(
            station["lon"]
        ),

        "nearest_town": station["nearest_town"],

        "warning_level": float(
            station["warning_level"]
        ),

        "danger_level": float(
            station["danger_level"]
        ),

        "distance_km": float(
            station["distance_km"]
        ),

        "latest_cwc_date": str(
            latest_date
        )
    }


# ============================================================
# READ WATER-LEVEL DATA
# ============================================================

def get_cwc_water_level_data(
    station_code,
    start_date,
    end_date
):
    """
    Read HHS water-level data for a station.
    """

    query = f"""
        SELECT
            date_ist,
            min,
            mean,
            max,
            sum,
            n_obs
        FROM read_parquet('{CWC_DAILY_URL}')
        WHERE station_code = ?
          AND datatype_code = 'HHS'
          AND date_ist BETWEEN ? AND ?
        ORDER BY date_ist
    """

    return duckdb.execute(
        query,
        [
            station_code,
            start_date,
            end_date
        ]
    ).df()


# ============================================================
# READ RAINFALL DATA
# ============================================================

def get_cwc_rainfall_data(
    station_code,
    start_date,
    end_date
):
    """
    Read MPS rainfall data for a station.
    """

    query = f"""
        SELECT
            date_ist,
            min,
            mean,
            max,
            sum,
            n_obs
        FROM read_parquet('{CWC_DAILY_URL}')
        WHERE station_code = ?
          AND datatype_code = 'MPS'
          AND date_ist BETWEEN ? AND ?
        ORDER BY date_ist
    """

    return duckdb.execute(
        query,
        [
            station_code,
            start_date,
            end_date
        ]
    ).df()


# ============================================================
# GET RECENT CWC DATA
# ============================================================

def get_cwc_recent_data(
    station_code,
    days=14,
    latest_date=None
):
    """
    Get recent CWC water-level and rainfall data.

    The window is based on the latest date available in the
    CWC dataset, NOT the computer's current date.
    """

    if latest_date is None:
        latest_date = get_latest_cwc_date()

    latest_date = pd.Timestamp(
        latest_date
    ).date()

    start_date = (
        latest_date
        - timedelta(days=days)
    )

    # --------------------------------------------------------
    # Water level
    # --------------------------------------------------------

    water = get_cwc_water_level_data(
        station_code,
        start_date,
        latest_date
    )

    # --------------------------------------------------------
    # Rainfall
    # --------------------------------------------------------

    rainfall = get_cwc_rainfall_data(
        station_code,
        start_date,
        latest_date
    )

    water["datatype_code"] = "HHS"

    rainfall["datatype_code"] = "MPS"

    return pd.concat(
        [
            water,
            rainfall
        ],
        ignore_index=True
    )


# ============================================================
# BUILD MODEL 1 CWC FEATURES
# ============================================================

def build_cwc_flood_features(
    station_code,
    warning_level,
    danger_level,
    latest_date=None
):
    """
    Build the nine base features required by Model 1.

    Features:

        water_level_prev
        water_level_max_prev
        rainfall_prev
        rainfall_3d
        rainfall_7d
        water_level_3d_max
        water_level_7d_max
        warning_level
        danger_level

    Derived threshold-ratio features are added later by
    api_server.py because they belong to Model 1 preprocessing.
    """

    # --------------------------------------------------------
    # Determine latest available date
    # --------------------------------------------------------

    if latest_date is None:
        latest_date = get_latest_cwc_date()

    latest_date = pd.Timestamp(
        latest_date
    ).date()

    # --------------------------------------------------------
    # Get recent data
    # --------------------------------------------------------

    df = get_cwc_recent_data(
        station_code,
        days=14,
        latest_date=latest_date
    )

    # ========================================================
    # WATER LEVEL
    # ========================================================

    water = df[
        df["datatype_code"] == "HHS"
    ].copy()

    if water.empty:
        raise ValueError(
            "Not enough historical CWC water-level data."
        )

    # --------------------------------------------------------
    # Convert numeric columns
    # --------------------------------------------------------

    water["mean"] = pd.to_numeric(
        water["mean"],
        errors="coerce"
    )

    water["max"] = pd.to_numeric(
        water["max"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Remove invalid values
    # --------------------------------------------------------

    water = water[
        water["mean"].notna()
        & water["max"].notna()
        & (water["mean"] > -100)
    ].copy()

    if len(water) < 2:
        raise ValueError(
            "Not enough historical CWC water-level data."
        )

    # ========================================================
    # DAILY WATER LEVEL
    # ========================================================

    water_daily = (
        water
        .groupby("date_ist")
        .agg(
            water_level_mean=(
                "mean",
                "mean"
            ),
            water_level_max=(
                "max",
                "max"
            )
        )
        .sort_index()
    )

    if len(water_daily) < 2:
        raise ValueError(
            "Not enough historical CWC water-level days."
        )

    # ========================================================
    # LATEST OBSERVATION
    # ========================================================

    latest_observation_date = (
        water_daily.index.max()
    )

    # --------------------------------------------------------
    # Previous observations
    #
    # The model uses previous conditions, so exclude the
    # latest available observation.
    # --------------------------------------------------------

    previous_water = water_daily[
        water_daily.index
        < latest_observation_date
    ].copy()

    if previous_water.empty:
        raise ValueError(
            "Not enough previous CWC water-level observations."
        )

    # ========================================================
    # WATER LEVEL PREVIOUS DAY
    # ========================================================

    water_level_prev = float(
        previous_water.iloc[-1][
            "water_level_mean"
        ]
    )

    # ========================================================
    # PREVIOUS MAXIMUM WATER LEVEL
    # ========================================================

    water_level_max_prev = float(
        previous_water.iloc[-1][
            "water_level_max"
        ]
    )

    # ========================================================
    # PREVIOUS 3-DAY MAXIMUM
    # ========================================================

    water_level_3d_max = float(
        previous_water[
            "water_level_max"
        ]
        .tail(3)
        .max()
    )

    # ========================================================
    # PREVIOUS 7-DAY MAXIMUM
    # ========================================================

    water_level_7d_max = float(
        previous_water[
            "water_level_max"
        ]
        .tail(7)
        .max()
    )

    # ========================================================
    # RAINFALL
    # ========================================================

    rainfall = df[
        df["datatype_code"] == "MPS"
    ].copy()

    rainfall["sum"] = pd.to_numeric(
        rainfall["sum"],
        errors="coerce"
    )

    rainfall = rainfall[
        rainfall["sum"].notna()
        & (rainfall["sum"] >= 0)
        & (rainfall["sum"] <= 2000)
    ].copy()

    # ========================================================
    # RAINFALL FEATURES
    # ========================================================

    if rainfall.empty:

        rainfall_prev = 0.0
        rainfall_3d = 0.0
        rainfall_7d = 0.0

    else:

        rainfall_daily = (
            rainfall
            .groupby("date_ist")["sum"]
            .sum()
            .sort_index()
        )

        previous_rainfall = rainfall_daily[
            rainfall_daily.index
            < latest_observation_date
        ]

        if previous_rainfall.empty:

            rainfall_prev = 0.0
            rainfall_3d = 0.0
            rainfall_7d = 0.0

        else:

            rainfall_prev = float(
                previous_rainfall.iloc[-1]
            )

            rainfall_3d = float(
                previous_rainfall
                .tail(3)
                .sum()
            )

            rainfall_7d = float(
                previous_rainfall
                .tail(7)
                .sum()
            )

    # ========================================================
    # MODEL 1 BASE FEATURES
    # ========================================================

    features = {

        "water_level_prev":
            water_level_prev,

        "water_level_max_prev":
            water_level_max_prev,

        "rainfall_prev":
            rainfall_prev,

        "rainfall_3d":
            rainfall_3d,

        "rainfall_7d":
            rainfall_7d,

        "water_level_3d_max":
            water_level_3d_max,

        "water_level_7d_max":
            water_level_7d_max,

        "warning_level":
            float(warning_level),

        "danger_level":
            float(danger_level)
    }

    # ========================================================
    # RETURN
    # ========================================================

    return {

        "features":
            features,

        "latest_date":
            str(
                latest_observation_date
            ),

        "latest_water_level":
            float(
                water_daily.loc[
                    latest_observation_date,
                    "water_level_mean"
                ]
            ),

        "latest_water_level_max":
            float(
                water_daily.loc[
                    latest_observation_date,
                    "water_level_max"
                ]
            ),

        "warning_level":
            float(warning_level),

        "danger_level":
            float(danger_level)
    }


# ============================================================
# COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("FLOODVISION - CWC DATA TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # Input location
    # --------------------------------------------------------

    latitude = float(
        input("\nEnter latitude: ")
    )

    longitude = float(
        input("Enter longitude: ")
    )

    print(
        "\nFinding nearest usable CWC station..."
    )

    try:

        # ====================================================
        # FIND STATION
        # ====================================================

        station = find_nearest_cwc_station(
            latitude,
            longitude
        )

        print()
        print("Nearest Usable CWC Station")
        print("-" * 50)

        print(
            f"Station      : "
            f"{station['name']}"
        )

        print(
            f"Station Code : "
            f"{station['station_code']}"
        )

        print(
            f"Latitude     : "
            f"{station['latitude']:.6f}"
        )

        print(
            f"Longitude    : "
            f"{station['longitude']:.6f}"
        )

        print(
            f"Distance     : "
            f"{station['distance_km']:.2f} km"
        )

        print(
            f"Warning Level: "
            f"{station['warning_level']}"
        )

        print(
            f"Danger Level : "
            f"{station['danger_level']}"
        )

        print(
            f"CWC Data Date: "
            f"{station['latest_cwc_date']}"
        )

        # ====================================================
        # BUILD FEATURES
        # ====================================================

        print(
            "\nBuilding CWC flood features..."
        )

        result = build_cwc_flood_features(
            station["station_code"],
            station["warning_level"],
            station["danger_level"],
            station["latest_cwc_date"]
        )

        # ====================================================
        # DISPLAY FEATURES
        # ====================================================

        print()
        print("CWC FLOOD FEATURES")
        print("-" * 50)

        for key, value in result["features"].items():

            print(
                f"{key:<30}: "
                f"{value:.4f}"
            )

        print()

        print(
            f"Latest Observation Date : "
            f"{result['latest_date']}"
        )

        print(
            f"Latest Water Level      : "
            f"{result['latest_water_level']:.3f}"
        )

        print(
            f"Latest Maximum Level    : "
            f"{result['latest_water_level_max']:.3f}"
        )

        print()
        print(
            "CWC DATA TEST SUCCESSFUL"
        )
        print("=" * 70)

    except Exception as e:

        print()
        print("CWC DATA ERROR:")
        print(
            f"{type(e).__name__}: {e}"
        )
        print("=" * 70)