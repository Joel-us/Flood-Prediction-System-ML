from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# PATH SETUP
# ============================================================

SRC_DIR = Path(__file__).resolve().parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ============================================================
# FLOODVISION MODULES
# ============================================================

from location_data import search_location
from weather_data import get_weather

from gauge_data import (
    find_nearest_gauge,
    get_catchment_data
)

from cwc_data import (
    find_nearest_cwc_station,
    build_cwc_flood_features
)

from predict import predict_two_stage


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="FloodVision API",
    description="FloodVision two-stage flood prediction API",
    version="2.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "ok",
        "message": "FloodVision API is running",
        "version": "2.0.0"
    }


# ============================================================
# LOCATION SEARCH
# ============================================================

@app.get("/locations")
def locations(
    query: str = Query(..., min_length=1)
):

    try:

        results = search_location(query)

        return {
            "query": query,
            "results": results
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Location search failed: {str(e)}"
        )


# ============================================================
# LIVE WEATHER
# ============================================================

@app.get("/weather")
def weather(
    latitude: float,
    longitude: float
):

    try:

        weather_data = get_weather(
            latitude,
            longitude
        )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "weather": weather_data
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Weather request failed: {str(e)}"
        )


# ============================================================
# FLOOD RISK ASSESSMENT
# ============================================================

@app.get("/flood-risk")
def flood_risk(
    latitude: float,
    longitude: float
):

    try:

        # ====================================================
        # 1. FIND INDOFLOODS HISTORICAL REFERENCE GAUGE
        # ====================================================

        gauge = find_nearest_gauge(
            latitude,
            longitude
        )

        if gauge is None:

            raise HTTPException(
                status_code=404,
                detail="No suitable INDOFLOODS reference gauge found."
            )


        # ====================================================
        # 2. GET CATCHMENT DATA
        #
        # Used by the severity model.
        # This is historical/catchment reference data,
        # not the current monitoring station.
        # ====================================================

        catchment = get_catchment_data(
            gauge["GaugeID"]
        )

        if catchment is None:

            raise HTTPException(
                status_code=404,
                detail="Catchment information not found."
            )


        # ====================================================
        # 3. GET RECENT WEATHER
        # ====================================================

        recent_weather = get_weather(
            latitude,
            longitude
        )


        # ====================================================
        # 4. FIND CURRENT CWC MONITORING STATION
        # ====================================================

        cwc_station = find_nearest_cwc_station(
            latitude,
            longitude
        )

        if cwc_station is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    "No usable CWC station with recent "
                    "water-level data found."
                )
            )


        # ====================================================
        # 5. BUILD CWC FLOOD FEATURES
        # ====================================================

        cwc_result = build_cwc_flood_features(
            cwc_station["station_code"],
            cwc_station["warning_level"],
            cwc_station["danger_level"]
        )

        cwc_features = cwc_result["features"]


        # ====================================================
        # 6. MODEL 1 INPUT
        #
        # Flood / No Flood
        # ====================================================

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


        # ====================================================
        # 7. DERIVED MODEL 1 FEATURES
        # ====================================================

        danger_level = flood_input["danger_level"]
        warning_level = flood_input["warning_level"]

        water_level_prev = flood_input["water_level_prev"]

        if danger_level <= 0:

            raise HTTPException(
                status_code=500,
                detail="Invalid CWC danger level."
            )

        if warning_level <= 0:

            raise HTTPException(
                status_code=500,
                detail="Invalid CWC warning level."
            )


        flood_input["water_level_danger_ratio"] = (
            water_level_prev / danger_level
        )

        flood_input["water_level_warning_ratio"] = (
            water_level_prev / warning_level
        )

        flood_input["water_level_max_danger_ratio"] = (
            flood_input["water_level_max_prev"]
            / danger_level
        )

        flood_input["water_level_3d_danger_ratio"] = (
            flood_input["water_level_3d_max"]
            / danger_level
        )

        flood_input["water_level_7d_danger_ratio"] = (
            flood_input["water_level_7d_max"]
            / danger_level
        )

        flood_input["danger_margin"] = (
            danger_level - water_level_prev
        )

        flood_input["warning_margin"] = (
            warning_level - water_level_prev
        )


        # ====================================================
        # 8. MODEL 2 INPUT
        #
        # Flood Severity
        # ====================================================

        severity_input = {

            "T1d":
                recent_weather["T1d"],

            "T3d":
                recent_weather["T3d"],

            "T5d":
                recent_weather["T5d"],

            "T7d":
                recent_weather["T7d"],

            "T10d":
                recent_weather["T10d"],

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


        # ====================================================
        # 9. TWO-STAGE PREDICTION
        # ====================================================

        result = predict_two_stage(
            flood_input,
            severity_input
        )


        # ====================================================
        # 10. RETURN API RESPONSE
        # ====================================================

        response = {

            # ------------------------------------------------
            # LOCATION
            # ------------------------------------------------

            "location": {

                "latitude":
                    latitude,

                "longitude":
                    longitude
            },


            # ------------------------------------------------
            # FLOOD PREDICTION
            # ------------------------------------------------

            "prediction": {

                "flood_status":
                    result["flood_status"],

                "flood_probability":
                    round(
                        result["flood_probability"],
                        4
                    ),

                "flood_probability_percent":
                    round(
                        result["flood_probability"] * 100,
                        2
                    ),

                # Internal model information.
                # Can be hidden from the frontend later.
                "cluster":
                    result["cluster"]
            },


            # ------------------------------------------------
            # SEVERITY
            # ------------------------------------------------

            "severity": {

                "severity":
                    result["severity"],

                "severity_probability":
                    (
                        round(
                            result["severity_probability"],
                            4
                        )
                        if result["severity_probability"] is not None
                        else None
                    ),

                "severity_probability_percent":
                    (
                        round(
                            result["severity_probability"] * 100,
                            2
                        )
                        if result["severity_probability"] is not None
                        else None
                    )
            },


            # ------------------------------------------------
            # HISTORICAL INDOFLOODS REFERENCE
            #
            # This is NOT presented as the current
            # monitoring station.
            # ------------------------------------------------

            "historical_reference": {

                "gauge_id":
                    gauge["GaugeID"],

                "station":
                    gauge["Station"],

                "state":
                    gauge["State"],

                "basin":
                    gauge["Basin"],

                "latitude":
                    gauge["Latitude"],

                "longitude":
                    gauge["Longitude"],

                "distance_km":
                    round(
                        gauge["distance_km"],
                        2
                    )
            },


            # ------------------------------------------------
            # CURRENT CWC MONITORING
            # ------------------------------------------------

            "cwc": {

                "station":
                    cwc_station["name"],

                "station_code":
                    cwc_station["station_code"],

                "distance_km":
                    round(
                        cwc_station["distance_km"],
                        2
                    ),

                "warning_level":
                    cwc_station["warning_level"],

                "danger_level":
                    cwc_station["danger_level"],

                "latest_date":
                    cwc_result["latest_date"],

                "latest_water_level":
                    cwc_result["latest_water_level"],

                "latest_water_level_max":
                    cwc_result["latest_water_level_max"]
            },


            # ------------------------------------------------
            # CWC FLOOD FEATURES
            # ------------------------------------------------

            "cwc_features": {

                "water_level_prev":
                    cwc_features["water_level_prev"],

                "water_level_max_prev":
                    cwc_features["water_level_max_prev"],

                "water_level_3d_max":
                    cwc_features["water_level_3d_max"],

                "water_level_7d_max":
                    cwc_features["water_level_7d_max"],

                "rainfall_prev":
                    cwc_features["rainfall_prev"],

                "rainfall_3d":
                    cwc_features["rainfall_3d"],

                "rainfall_7d":
                    cwc_features["rainfall_7d"],

                "warning_level":
                    cwc_features["warning_level"],

                "danger_level":
                    cwc_features["danger_level"]
            },


            # ------------------------------------------------
            # WEATHER / RAINFALL
            # ------------------------------------------------

            "rainfall": {

                "T1d":
                    recent_weather["T1d"],

                "T3d":
                    recent_weather["T3d"],

                "T5d":
                    recent_weather["T5d"],

                "T7d":
                    recent_weather["T7d"],

                "T10d":
                    recent_weather["T10d"]
            }
        }


        return response


    # ========================================================
    # HTTP EXCEPTION
    # ========================================================

    except HTTPException:

        raise


    # ========================================================
    # GENERAL ERROR
    # ========================================================

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(
                "Flood risk assessment failed: "
                f"{type(e).__name__}: {str(e)}"
            )
        )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {

        "name":
            "FloodVision API",

        "status":
            "running",

        "version":
            "2.0.0",

        "message":
            "FloodVision two-stage backend is ready"
    }