import os
import pandas as pd
import numpy as np


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

METADATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "metadata_indofloods.csv"
)

CATCHMENT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "Catchment.csv"
)


# ============================================================
# LOAD GAUGE METADATA
# ============================================================

def load_gauge_metadata():
    """
    Load official INDOFLOODS gauge metadata.

    Only gauges that also exist in Catchment.csv
    are retained because these are the gauges used
    by the trained FloodVision model.
    """

    metadata = pd.read_csv(METADATA_FILE)
    catchment = pd.read_csv(CATCHMENT_FILE)

    required = [
        "GaugeID",
        "Latitude",
        "Longitude",
        "Station",
        "State"
    ]

    missing = [
        col for col in required
        if col not in metadata.columns
    ]

    if missing:
        raise ValueError(
            f"Missing metadata columns: {missing}"
        )

    # Only gauges available to the trained model
    valid_gauges = set(
        catchment["GaugeID"]
        .astype(str)
        .str.strip()
    )

    metadata["GaugeID"] = (
        metadata["GaugeID"]
        .astype(str)
        .str.strip()
    )

    metadata = metadata[
        metadata["GaugeID"].isin(valid_gauges)
    ].copy()

    metadata["Latitude"] = pd.to_numeric(
        metadata["Latitude"],
        errors="coerce"
    )

    metadata["Longitude"] = pd.to_numeric(
        metadata["Longitude"],
        errors="coerce"
    )

    metadata = metadata.dropna(
        subset=["Latitude", "Longitude"]
    )

    return metadata


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def haversine_distance(
    latitude1,
    longitude1,
    latitude2,
    longitude2
):
    """
    Calculate distance between two coordinates
    using the Haversine formula.

    Returns distance in kilometres.
    """

    earth_radius = 6371.0

    lat1 = np.radians(latitude1)
    lat2 = np.radians(latitude2)

    delta_lat = np.radians(
        latitude2 - latitude1
    )

    delta_lon = np.radians(
        longitude2 - longitude1
    )

    a = (
        np.sin(delta_lat / 2) ** 2
        +
        np.cos(lat1)
        *
        np.cos(lat2)
        *
        np.sin(delta_lon / 2) ** 2
    )

    c = 2 * np.arcsin(
        np.sqrt(a)
    )

    return earth_radius * c


# ============================================================
# FIND NEAREST GAUGE
# ============================================================

def find_nearest_gauge(latitude, longitude):
    """
    Find the nearest valid INDOFLOODS gauge.

    Returns gauge information including the distance
    in kilometres.
    """

    gauges = load_gauge_metadata().copy()

    if gauges.empty:
        return None

    # Calculate distance from selected location
    gauges["distance_km"] = haversine_distance(
        latitude,
        longitude,
        gauges["Latitude"].values,
        gauges["Longitude"].values
    )

    # Find nearest gauge
    nearest = gauges.loc[
        gauges["distance_km"].idxmin()
    ]

    distance_km = float(
        nearest["distance_km"]
    )

    return {
        "GaugeID": str(nearest["GaugeID"]),
        "Station": str(nearest["Station"]),
        "Latitude": float(nearest["Latitude"]),
        "Longitude": float(nearest["Longitude"]),
        "State": str(nearest["State"]),
        "Basin": str(
            nearest.get("Basin", "Unknown")
        ),

        # Used by FastAPI
        "distance_km": distance_km,

        # Kept for existing CLI compatibility
        "Distance": distance_km
    }


# ============================================================
# GET CATCHMENT DATA
# ============================================================

def get_catchment_data(gauge_id):
    """
    Get catchment information for a GaugeID.
    """

    catchment = pd.read_csv(
        CATCHMENT_FILE
    )

    catchment["GaugeID"] = (
        catchment["GaugeID"]
        .astype(str)
        .str.strip()
    )

    result = catchment[
        catchment["GaugeID"] == str(gauge_id).strip()
    ]

    if result.empty:
        raise ValueError(
            f"No catchment data found for {gauge_id}"
        )

    return result.iloc[0]


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("INDOFLOODS GAUGE LOCATION TEST")
    print("=" * 60)

    latitude = float(
        input("Enter latitude: ")
    )

    longitude = float(
        input("Enter longitude: ")
    )

    gauge = find_nearest_gauge(
        latitude,
        longitude
    )

    if gauge is None:
        print("\nNo suitable INDOFLOODS gauge found.")
        exit()

    print("\nNearest INDOFLOODS Gauge")
    print("-" * 40)

    print(
        "Gauge ID :",
        gauge["GaugeID"]
    )

    print(
        "Station  :",
        gauge["Station"]
    )

    print(
        "State    :",
        gauge["State"]
    )

    print(
        "Basin    :",
        gauge["Basin"]
    )

    print(
        "Latitude :",
        gauge["Latitude"]
    )

    print(
        "Longitude:",
        gauge["Longitude"]
    )

    print(
        "Distance :",
        round(gauge["distance_km"], 2),
        "km"
    )

    catchment = get_catchment_data(
        gauge["GaugeID"]
    )

    print("\nCatchment Data Found")
    print("-" * 40)

    print(
        "Annual Mean Temperature :",
        catchment["Annual Mean Temperature"]
    )

    print(
        "Annual Precipitation    :",
        catchment["Annual Precipitation"]
    )

    print(
        "Stream Order            :",
        catchment["Stream Order"]
    )

    print(
        "Drainage Area           :",
        catchment["Drainage Area"]
    )

    print(
        "Catchment Relief        :",
        catchment["Catchment Relief"]
    )

    print(
        "Drainage Density        :",
        catchment["Drainage Density"]
    )

    print(
        "Ruggedness Number       :",
        catchment["Ruggedness Number"]
    )

    print(
        "Population Density      :",
        catchment["Population Density"]
    )

    print(
        "Climate Type            :",
        catchment["KoppenGeiger Climate Type"]
    )

    print(
        "Land Cover              :",
        catchment["Land cover"]
    )

    print(
        "Soil Type               :",
        catchment["Soil type"]
    )

    print(
        "Lithology               :",
        catchment["lithology type"]
    )