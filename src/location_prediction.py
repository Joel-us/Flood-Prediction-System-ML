import sys
import os

# Allow imports from src/
sys.path.append(
    os.path.dirname(os.path.abspath(__file__))
)

from location_data import search_location
from weather_data import get_weather
from gauge_data import find_nearest_gauge, get_catchment_data
from cwc_data import (
    find_nearest_cwc_station,
    build_cwc_flood_features
)
from predict import predict_two_stage


# ============================================================
# BUILD SEVERITY INPUT
# ============================================================

def build_severity_input(weather, catchment):

    return {
        "T1d": weather["T1d"],
        "T3d": weather["T3d"],
        "T5d": weather["T5d"],
        "T7d": weather["T7d"],
        "T10d": weather["T10d"],

        "Annual Mean Temperature":
            catchment["Annual Mean Temperature"],

        "Annual Precipitation":
            catchment["Annual Precipitation"],

        "Stream Order":
            catchment["Stream Order"],

        "Drainage Area":
            catchment["Drainage Area"],

        "Catchment Relief":
            catchment["Catchment Relief"],

        "Drainage Density":
            catchment["Drainage Density"],

        "Ruggedness Number":
            catchment["Ruggedness Number"],

        "Population Density":
            catchment["Population Density"],

        "KoppenGeiger Climate Type":
            catchment["KoppenGeiger Climate Type"],

        "Land cover":
            catchment["Land cover"],

        "Soil type":
            catchment["Soil type"],

        "lithology type":
            catchment["lithology type"],
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("FLOODVISION - LOCATION FLOOD PREDICTION")
    print("=" * 70)

    location_name = input("\nEnter location: ").strip()

    # --------------------------------------------------------
    # 1. LOCATION
    # --------------------------------------------------------

    print()
    print("[1] Searching location...")

    locations = search_location(location_name)

    if not locations:
        print("Location not found.")
        return

    location = locations[0]

    latitude = float(location["latitude"])
    longitude = float(location["longitude"])

    print(
        f"Location   : {location['name']}"
    )

    print(
        f"Latitude   : {latitude}"
    )

    print(
        f"Longitude  : {longitude}"
    )

    print(
        f"Country    : {location['country']}"
    )

    # --------------------------------------------------------
    # 2. INDOFLOODS GAUGE
    # --------------------------------------------------------

    print()
    print("[2] Finding nearest INDOFLOODS gauge...")

    gauge = find_nearest_gauge(
        latitude,
        longitude
    )

    print(
        f"Gauge      : {gauge['GaugeID']}"
    )

    print(
        f"Station    : {gauge['Station']}"
    )

    print(
        f"Distance   : {gauge['Distance']:.2f} km"
    )

    # --------------------------------------------------------
    # 3. CATCHMENT
    # --------------------------------------------------------

    print()
    print("[3] Loading catchment data...")

    catchment = get_catchment_data(
        gauge["GaugeID"]
    )

    if catchment is None:
        print("Catchment data not found.")
        return

    print("Catchment data loaded.")

    # --------------------------------------------------------
    # 4. WEATHER
    # --------------------------------------------------------

    print()
    print("[4] Getting recent weather data...")

    weather = get_weather(
        latitude,
        longitude
    )

    print(
        f"T1d   : {weather['T1d']:.1f} mm"
    )

    print(
        f"T3d   : {weather['T3d']:.1f} mm"
    )

    print(
        f"T5d   : {weather['T5d']:.1f} mm"
    )

    print(
        f"T7d   : {weather['T7d']:.1f} mm"
    )

    print(
        f"T10d  : {weather['T10d']:.1f} mm"
    )

    # --------------------------------------------------------
    # 5. CWC LIVE DATA
    # --------------------------------------------------------

    print()
    print("[5] Finding usable CWC station...")

    try:

        cwc_station = find_nearest_cwc_station(
            latitude,
            longitude
        )

        print(
            f"CWC Station : "
            f"{cwc_station['name']}"
        )

        print(
            f"CWC Code    : "
            f"{cwc_station['station_code']}"
        )

        print(
            f"CWC Distance: "
            f"{cwc_station['distance_km']:.2f} km"
        )

        print(
            f"Warning     : "
            f"{cwc_station['warning_level']:.2f} m"
        )

        print(
            f"Danger      : "
            f"{cwc_station['danger_level']:.2f} m"
        )

        cwc_result = build_cwc_flood_features(
            cwc_station["station_code"],
            cwc_station["warning_level"],
            cwc_station["danger_level"]
        )

    except Exception as e:

        print()
        print("CWC DATA ERROR")
        print(
            f"{type(e).__name__}: {e}"
        )
        return

    cwc_features = cwc_result["features"]

    print()
    print("CWC Flood Features")
    print("-" * 50)

    for key, value in cwc_features.items():

        print(
            f"{key:<25}: {value:.4f}"
        )

    print(
        f"{'Latest Water Level':<25}: "
        f"{cwc_result['latest_water_level']:.3f} m"
    )

    # --------------------------------------------------------
    # 6. BUILD MODEL INPUTS
    # --------------------------------------------------------

    print()
    print("[6] Building model inputs...")

    # Model 1
    flood_input = {
        "water_level_prev":
            cwc_features["water_level_prev"],

        "water_level_max_prev":
            cwc_features["water_level_max_prev"],

        "rainfall_prev":
            cwc_features["rainfall_prev"],

        "rainfall_3d":
            cwc_features["rainfall_3d"],

        "rainfall_7d":
            cwc_features["rainfall_7d"],

        "water_level_3d_max":
            cwc_features["water_level_3d_max"],

        "water_level_7d_max":
            cwc_features["water_level_7d_max"],

        "warning_level":
            cwc_features["warning_level"],

        "danger_level":
            cwc_features["danger_level"],
    }

    # Model 2
    severity_input = build_severity_input(
        weather,
        catchment
    )

    # --------------------------------------------------------
    # 7. TWO-STAGE MODEL
    # --------------------------------------------------------

    print()
    print("[7] Running FloodVision two-stage model...")

    result = predict_two_stage(
        flood_input,
        severity_input
    )

    # --------------------------------------------------------
    # 8. FINAL RESULT
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("FINAL FLOODVISION PREDICTION")
    print("=" * 70)

    print(
        f"\nFlood Status       : "
        f"{result['flood_status']}"
    )

    print(
        f"Flood Probability : "
        f"{result['flood_probability'] * 100:.2f}%"
    )

    print(
        f"K-Means Cluster   : "
        f"{result['cluster']}"
    )

    if result["severity"] is not None:

        print(
            f"Severity           : "
            f"{result['severity']}"
        )

        print(
            f"Severity Probability: "
            f"{result['severity_probability'] * 100:.2f}%"
        )

    else:

        print(
            "Severity           : "
            "Not applicable"
        )

    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()