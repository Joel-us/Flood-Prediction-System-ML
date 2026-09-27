# FloodVision – Flood Prediction System Using Machine Learning

FloodVision is a machine-learning-based flood prediction system designed to analyze environmental, hydrological, rainfall, and catchment-related information to estimate flood risk for a selected location.

The system follows a two-stage prediction approach:

1. **Flood Prediction** – predicts whether the current conditions indicate **Flood** or **No Flood**.
2. **Flood Severity Prediction** – runs only when a flood is predicted and estimates the corresponding flood type/severity.

The project combines machine learning with real flood, precipitation, catchment, weather, and river-level data to provide an interactive flood-risk dashboard.

---

## Project Objectives

The main objectives of FloodVision are:

- Predict flood occurrence using machine learning.
- Estimate the model's flood probability.
- Predict flood severity when a flood is detected.
- Use rainfall and water-level observations as current-condition inputs.
- Use catchment characteristics and historical flood information as supporting data.
- Provide a location-based flood prediction interface.
- Present prediction results through a modern web dashboard.

---

# System Architecture

```text
                         User
                           |
                           v
                  FloodVision Web UI
                React + TanStack + Vite
                           |
                           v
                    FastAPI Backend
                           |
            +--------------+--------------+
            |                             |
            v                             v
      Location / Weather            CWC Data
            |                             |
            +--------------+--------------+
                           |
                           v
                  Current Flood Features
                           |
                           v
               Model 1 – Flood Prediction
                  K-Means + Random Forest
                           |
                    +------+------+
                    |             |
                 No Flood        Flood
                    |             |
                    |             v
                    |       Model 2 – Severity
                    |         Random Forest
                    |             |
                    +------+------+
                           |
                           v
                    FloodVision Dashboard