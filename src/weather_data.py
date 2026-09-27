import requests
from datetime import datetime, timedelta


WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(latitude, longitude):
    """
    Get recent weather data for a selected location.

    Returns:
        Dictionary containing:
        - T1d
        - T3d
        - T5d
        - T7d
        - T10d
        - Temperature
        - FeelsLike
        - Humidity
        - WindSpeed
        - WindDirection
        - CloudCover
        - Precipitation
        - ObservationTime
    """

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "hourly": (
            "temperature_2m,"
            "apparent_temperature,"
            "relative_humidity_2m,"
            "precipitation,"
            "wind_speed_10m,"
            "wind_direction_10m,"
            "cloud_cover"
        ),

        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),

        "timezone": "auto"
    }

    response = requests.get(
        WEATHER_URL,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    if "hourly" not in data:
        raise ValueError("Weather data not available.")

    hourly = data["hourly"]

    # -----------------------------------------
    # Extract hourly data
    # -----------------------------------------

    precipitation = hourly.get("precipitation", [])
    temperature = hourly.get("temperature_2m", [])
    feels_like = hourly.get("apparent_temperature", [])
    humidity = hourly.get("relative_humidity_2m", [])
    wind_speed = hourly.get("wind_speed_10m", [])
    wind_direction = hourly.get("wind_direction_10m", [])
    cloud_cover = hourly.get("cloud_cover", [])
    times = hourly.get("time", [])

    # -----------------------------------------
    # Remove missing precipitation values
    # -----------------------------------------

    valid_precipitation = [
        value for value in precipitation
        if value is not None
    ]

    if not valid_precipitation:
        raise ValueError("No precipitation data available.")

    # -----------------------------------------
    # Recent cumulative precipitation
    # -----------------------------------------

    T1d = sum(valid_precipitation[-24:])
    T3d = sum(valid_precipitation[-72:])
    T5d = sum(valid_precipitation[-120:])
    T7d = sum(valid_precipitation[-168:])
    T10d = sum(valid_precipitation[-240:])

    # -----------------------------------------
    # Helper function
    # -----------------------------------------

    def latest_value(values):
        return next(
            (value for value in reversed(values) if value is not None),
            None
        )

    # -----------------------------------------
    # Latest weather conditions
    # -----------------------------------------

    latest_temperature = latest_value(temperature)
    latest_feels_like = latest_value(feels_like)
    latest_humidity = latest_value(humidity)
    latest_wind_speed = latest_value(wind_speed)
    latest_wind_direction = latest_value(wind_direction)
    latest_cloud_cover = latest_value(cloud_cover)
    latest_precipitation = latest_value(precipitation)
    latest_time = latest_value(times)

    # -----------------------------------------
    # Return weather information
    # -----------------------------------------

    return {
        # Existing rainfall values
        "T1d": round(T1d, 2),
        "T3d": round(T3d, 2),
        "T5d": round(T5d, 2),
        "T7d": round(T7d, 2),
        "T10d": round(T10d, 2),

        # Current weather
        "Temperature": latest_temperature,
        "FeelsLike": latest_feels_like,
        "Humidity": latest_humidity,
        "WindSpeed": latest_wind_speed,
        "WindDirection": latest_wind_direction,
        "CloudCover": latest_cloud_cover,
        "Precipitation": latest_precipitation,
        "ObservationTime": latest_time,
    }


def display_weather(weather):
    print("\n" + "=" * 60)
    print("FLOODVISION - WEATHER DATA")
    print("=" * 60)

    print("\nRECENT RAINFALL")
    print("-" * 60)

    print(f"Last 24 hours : {weather['T1d']} mm")
    print(f"Last 3 days   : {weather['T3d']} mm")
    print(f"Last 5 days   : {weather['T5d']} mm")
    print(f"Last 7 days   : {weather['T7d']} mm")
    print(f"Last 10 days  : {weather['T10d']} mm")

    print("\nCURRENT CONDITIONS")
    print("-" * 60)

    print(f"Temperature   : {weather['Temperature']} °C")
    print(f"Feels like    : {weather['FeelsLike']} °C")
    print(f"Humidity      : {weather['Humidity']} %")
    print(f"Wind speed    : {weather['WindSpeed']} km/h")
    print(f"Wind direction: {weather['WindDirection']}°")
    print(f"Cloud cover   : {weather['CloudCover']} %")
    print(f"Precipitation : {weather['Precipitation']} mm")
    print(f"Updated       : {weather['ObservationTime']}")

    print("=" * 60)


def main():

    print("\n" + "=" * 60)
    print("FLOODVISION - WEATHER DATA")
    print("=" * 60)

    latitude = float(input("\nEnter latitude: "))
    longitude = float(input("Enter longitude: "))

    try:
        weather = get_weather(latitude, longitude)
        display_weather(weather)

    except requests.exceptions.RequestException as error:
        print("\n❌ Could not connect to weather service.")
        print(f"Error: {error}")

    except Exception as error:
        print("\n❌ Error:")
        print(error)


if __name__ == "__main__":
    main()