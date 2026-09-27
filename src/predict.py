import joblib
import pandas as pd
from pathlib import Path


# ============================================================
# FLOODVISION
# PREDICTION MODULE
#
# Model 1:
# K-Means + Random Forest
# Flood / No Flood
#
# Model 2:
# Random Forest
# Flood Severity
# ============================================================


ROOT = Path(__file__).resolve().parents[1]

FLOOD_MODEL_PATH = (
    ROOT
    / "models"
    / "flood_model.joblib"
)

SEVERITY_MODEL_PATH = (
    ROOT
    / "models"
    / "severity_model.joblib"
)


# ============================================================
# LOAD MODELS
# ============================================================

flood_package = joblib.load(
    FLOOD_MODEL_PATH
)

severity_package = joblib.load(
    SEVERITY_MODEL_PATH
)


# ============================================================
# MODEL 1
# ============================================================

flood_model = flood_package["random_forest"]

flood_scaler = flood_package["scaler"]

flood_kmeans = flood_package["kmeans"]

flood_features = flood_package["features"]


# ============================================================
# MODEL 2
# ============================================================

severity_model = severity_package["model"]

severity_features = severity_package["features"]


# ============================================================
# MODEL 1
# FLOOD / NO FLOOD
# ============================================================

def predict_flood(input_data):

    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    X = pd.DataFrame(
        [input_data]
    )

    # Make sure the same features used during training
    # are supplied to the model.
    X = X[flood_features]


    # --------------------------------------------------------
    # K-MEANS
    #
    # K-Means uses standardized features.
    # --------------------------------------------------------

    X_scaled = flood_scaler.transform(X)

    cluster = int(
        flood_kmeans.predict(X_scaled)[0]
    )


    # --------------------------------------------------------
    # RANDOM FOREST
    #
    # Random Forest was trained using RAW feature values
    # + KMeans_Cluster.
    # --------------------------------------------------------

    X_model = X.copy()

    X_model["KMeans_Cluster"] = cluster


    # --------------------------------------------------------
    # FLOOD PREDICTION
    # --------------------------------------------------------

    prediction = int(
        flood_model.predict(X_model)[0]
    )


    # --------------------------------------------------------
    # FLOOD PROBABILITY
    # --------------------------------------------------------

    probabilities = (
        flood_model.predict_proba(X_model)[0]
    )

    # Class 1 = Flood
    flood_probability = float(
        probabilities[1]
    )


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if prediction == 1:
        status = "Flood"
    else:
        status = "No Flood"


    return {
        "prediction": prediction,
        "status": status,
        "probability": flood_probability,
        "probability_percent": flood_probability * 100,
        "cluster": cluster
    }


# ============================================================
# MODEL 2
# FLOOD SEVERITY
# ============================================================

def predict_severity(input_data):

    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    X = pd.DataFrame(
        [input_data]
    )

    X = X[severity_features]


    # --------------------------------------------------------
    # SEVERITY PREDICTION
    # --------------------------------------------------------

    prediction = (
        severity_model.predict(X)[0]
    )


    # --------------------------------------------------------
    # SEVERITY PROBABILITY
    # --------------------------------------------------------

    probabilities = (
        severity_model.predict_proba(X)[0]
    )

    classes = severity_model.classes_


    probability_map = {

        str(label): float(probability)

        for label, probability
        in zip(
            classes,
            probabilities
        )
    }


    max_probability = float(
        max(probabilities)
    )


    return {

        "severity":
            str(prediction),

        "probability":
            max_probability,

        "probabilities":
            probability_map
    }


# ============================================================
# TWO-STAGE PREDICTION
# ============================================================

def predict_two_stage(
    flood_input,
    severity_input=None
):

    # ========================================================
    # STAGE 1
    # FLOOD / NO FLOOD
    # ========================================================

    flood_result = predict_flood(
        flood_input
    )


    # ========================================================
    # NO FLOOD
    #
    # Stop here.
    # Severity is not calculated.
    # ========================================================

    if flood_result["prediction"] == 0:

        return {

            "flood_status":
                flood_result["status"],

            "flood_probability":
                flood_result["probability"],

            "cluster":
                flood_result["cluster"],

            "severity":
                "Not applicable",

            "severity_probability":
                None
        }


    # ========================================================
    # FLOOD DETECTED
    # ========================================================

    if severity_input is None:

        return {

            "flood_status":
                flood_result["status"],

            "flood_probability":
                flood_result["probability"],

            "cluster":
                flood_result["cluster"],

            "severity":
                "Unavailable",

            "severity_probability":
                None
        }


    # ========================================================
    # STAGE 2
    # FLOOD SEVERITY
    # ========================================================

    severity_result = predict_severity(
        severity_input
    )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "flood_status":
            flood_result["status"],

        "flood_probability":
            flood_result["probability"],

        "cluster":
            flood_result["cluster"],

        "severity":
            severity_result["severity"],

        "severity_probability":
            severity_result["probability"]
    }