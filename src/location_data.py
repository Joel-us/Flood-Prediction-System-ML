from __future__ import annotations

from typing import Any

import requests


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


# ============================================================
# INDIAN STATES AND UNION TERRITORIES
# Representative location = capital / major administrative city
#
# These coordinates are used ONLY when the user searches for
# the state/UT itself.
#
# They do not mean that the whole state is represented by
# one flood-monitoring station.
# ============================================================

INDIA_STATES_UTS: dict[str, dict[str, Any]] = {
    # -------------------------
    # STATES
    # -------------------------

    "andhra pradesh": {
        "name": "Amaravati",
        "state": "Andhra Pradesh",
        "latitude": 16.5062,
        "longitude": 80.6480,
    },
    "arunachal pradesh": {
        "name": "Itanagar",
        "state": "Arunachal Pradesh",
        "latitude": 27.0844,
        "longitude": 93.6053,
    },
    "assam": {
        "name": "Dispur",
        "state": "Assam",
        "latitude": 26.1433,
        "longitude": 91.7898,
    },
    "bihar": {
        "name": "Patna",
        "state": "Bihar",
        "latitude": 25.5941,
        "longitude": 85.1376,
    },
    "chhattisgarh": {
        "name": "Raipur",
        "state": "Chhattisgarh",
        "latitude": 21.2514,
        "longitude": 81.6296,
    },
    "goa": {
        "name": "Panaji",
        "state": "Goa",
        "latitude": 15.4909,
        "longitude": 73.8278,
    },
    "gujarat": {
        "name": "Gandhinagar",
        "state": "Gujarat",
        "latitude": 23.2156,
        "longitude": 72.6369,
    },
    "haryana": {
        "name": "Chandigarh",
        "state": "Haryana",
        "latitude": 30.7333,
        "longitude": 76.7794,
    },
    "himachal pradesh": {
        "name": "Shimla",
        "state": "Himachal Pradesh",
        "latitude": 31.1048,
        "longitude": 77.1734,
    },
    "jharkhand": {
        "name": "Ranchi",
        "state": "Jharkhand",
        "latitude": 23.3441,
        "longitude": 85.3096,
    },
    "karnataka": {
        "name": "Bengaluru",
        "state": "Karnataka",
        "latitude": 12.9716,
        "longitude": 77.5946,
    },
    "kerala": {
        "name": "Thiruvananthapuram",
        "state": "Kerala",
        "latitude": 8.5241,
        "longitude": 76.9366,
    },
    "madhya pradesh": {
        "name": "Bhopal",
        "state": "Madhya Pradesh",
        "latitude": 23.2599,
        "longitude": 77.4126,
    },
    "maharashtra": {
        "name": "Mumbai",
        "state": "Maharashtra",
        "latitude": 19.0760,
        "longitude": 72.8777,
    },
    "manipur": {
        "name": "Imphal",
        "state": "Manipur",
        "latitude": 24.8170,
        "longitude": 93.9368,
    },
    "meghalaya": {
        "name": "Shillong",
        "state": "Meghalaya",
        "latitude": 25.5788,
        "longitude": 91.8933,
    },
    "mizoram": {
        "name": "Aizawl",
        "state": "Mizoram",
        "latitude": 23.7271,
        "longitude": 92.7176,
    },
    "nagaland": {
        "name": "Kohima",
        "state": "Nagaland",
        "latitude": 25.6751,
        "longitude": 94.1086,
    },
    "odisha": {
        "name": "Bhubaneswar",
        "state": "Odisha",
        "latitude": 20.2961,
        "longitude": 85.8245,
    },
    "punjab": {
        "name": "Chandigarh",
        "state": "Punjab",
        "latitude": 30.7333,
        "longitude": 76.7794,
    },
    "rajasthan": {
        "name": "Jaipur",
        "state": "Rajasthan",
        "latitude": 26.9124,
        "longitude": 75.7873,
    },
    "sikkim": {
        "name": "Gangtok",
        "state": "Sikkim",
        "latitude": 27.3389,
        "longitude": 88.6065,
    },
    "tamil nadu": {
        "name": "Chennai",
        "state": "Tamil Nadu",
        "latitude": 13.0827,
        "longitude": 80.2707,
    },
    "telangana": {
        "name": "Hyderabad",
        "state": "Telangana",
        "latitude": 17.3850,
        "longitude": 78.4867,
    },
    "tripura": {
        "name": "Agartala",
        "state": "Tripura",
        "latitude": 23.8315,
        "longitude": 91.2868,
    },
    "uttar pradesh": {
        "name": "Lucknow",
        "state": "Uttar Pradesh",
        "latitude": 26.8467,
        "longitude": 80.9462,
    },
    "uttarakhand": {
        "name": "Dehradun",
        "state": "Uttarakhand",
        "latitude": 30.3165,
        "longitude": 78.0322,
    },
    "west bengal": {
        "name": "Kolkata",
        "state": "West Bengal",
        "latitude": 22.5726,
        "longitude": 88.3639,
    },

    # -------------------------
    # UNION TERRITORIES
    # -------------------------

    "andaman and nicobar islands": {
        "name": "Port Blair",
        "state": "Andaman and Nicobar Islands",
        "latitude": 11.6234,
        "longitude": 92.7265,
    },
    "andaman & nicobar islands": {
        "name": "Port Blair",
        "state": "Andaman and Nicobar Islands",
        "latitude": 11.6234,
        "longitude": 92.7265,
    },
    "chandigarh": {
        "name": "Chandigarh",
        "state": "Chandigarh",
        "latitude": 30.7333,
        "longitude": 76.7794,
    },
    "dadra and nagar haveli and daman and diu": {
        "name": "Daman",
        "state": "Dadra and Nagar Haveli and Daman and Diu",
        "latitude": 20.3974,
        "longitude": 72.8328,
    },
    "delhi": {
        "name": "New Delhi",
        "state": "Delhi",
        "latitude": 28.6139,
        "longitude": 77.2090,
    },
    "jammu and kashmir": {
        "name": "Srinagar",
        "state": "Jammu and Kashmir",
        "latitude": 34.0837,
        "longitude": 74.7973,
    },
    "ladakh": {
        "name": "Leh",
        "state": "Ladakh",
        "latitude": 34.1526,
        "longitude": 77.5771,
    },
    "lakshadweep": {
        "name": "Kavaratti",
        "state": "Lakshadweep",
        "latitude": 10.5669,
        "longitude": 72.6420,
    },
    "puducherry": {
        "name": "Puducherry",
        "state": "Puducherry",
        "latitude": 11.9416,
        "longitude": 79.8083,
    },
}


# Useful alternative names / abbreviations.
STATE_ALIASES = {
    "up": "uttar pradesh",
    "u.p.": "uttar pradesh",
    "mp": "madhya pradesh",
    "m.p.": "madhya pradesh",
    "hp": "himachal pradesh",
    "h.p.": "himachal pradesh",
    "uk": "uttarakhand",
    "wb": "west bengal",
    "tn": "tamil nadu",
    "t.n.": "tamil nadu",
    "ap": "andhra pradesh",
    "a.p.": "andhra pradesh",
    "ts": "telangana",
    "kl": "kerala",
    "ka": "karnataka",
    "mh": "maharashtra",
    "odisha": "odisha",
    "orissa": "odisha",
    "j&k": "jammu and kashmir",
    "jammu & kashmir": "jammu and kashmir",
    "pondicherry": "puducherry",
    "nct delhi": "delhi",
    "delhi ncr": "delhi",
}


def normalize_query(query: str) -> str:
    """Normalize user input for matching."""
    return " ".join(
        query.strip().lower().replace(",", " ").split()
    )


def get_state_result(
    query: str,
) -> dict[str, Any] | None:
    """
    Return a representative location when the user searches
    for an Indian state or Union Territory.
    """

    normalized = normalize_query(query)

    # Direct state/UT match.
    key = STATE_ALIASES.get(
        normalized,
        normalized,
    )

    location = INDIA_STATES_UTS.get(key)

    if location is None:
        return None

    return {
        "name": location["name"],
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "country": "India",
        "country_code": "IN",
        "admin1": location["state"],
        "admin2": None,
        "elevation": None,
        "timezone": "Asia/Kolkata",
        "population": None,

        # Extra fields used by FloodVision UI.
        "is_state_representative": True,
        "state_name": location["state"],
        "representative_location": location["name"],
    }


def search_location(
    query: str,
    count: int = 10,
) -> list[dict[str, Any]]:
    """
    Search for a location.

    Search order:

    1. Indian state / UT exact match
    2. Open-Meteo India geocoding search
    3. Broader Open-Meteo fallback search

    This allows searches such as:

        Meghalaya
        Uttar Pradesh
        Tamil Nadu
        Chennai
        Shillong
        Lucknow
    """

    query = query.strip()

    if not query:
        return []

    # ========================================================
    # 1. STATE / UT
    # ========================================================

    state_result = get_state_result(query)

    if state_result:
        return [state_result]

    # ========================================================
    # 2. INDIA-FIRST OPEN-METEO SEARCH
    # ========================================================

    try:
        params = {
            "name": query,
            "count": min(max(count, 1), 100),
            "language": "en",
            "format": "json",
            "countryCode": "IN",
        }

        response = requests.get(
            GEOCODING_URL,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results", [])

        if results:
            return [
                format_geocoding_result(
                    result
                )
                for result in results
            ]

    except requests.RequestException as exc:
        print(
            f"India geocoding request failed: {exc}"
        )

    # ========================================================
    # 3. GLOBAL FALLBACK
    # ========================================================

    try:
        params = {
            "name": query,
            "count": min(max(count, 1), 100),
            "language": "en",
            "format": "json",
        }

        response = requests.get(
            GEOCODING_URL,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results", [])

        return [
            format_geocoding_result(
                result
            )
            for result in results
        ]

    except requests.RequestException as exc:
        print(
            f"Global geocoding request failed: {exc}"
        )
        return []


def format_geocoding_result(
    result: dict[str, Any],
) -> dict[str, Any]:
    """Convert Open-Meteo result into FloodVision format."""

    return {
        "name": result.get(
            "name",
            "Unknown location",
        ),
        "latitude": result.get(
            "latitude"
        ),
        "longitude": result.get(
            "longitude"
        ),
        "country": result.get(
            "country",
            "",
        ),
        "country_code": result.get(
            "country_code"
        ),
        "admin1": result.get(
            "admin1"
        ),
        "admin2": result.get(
            "admin2"
        ),
        "elevation": result.get(
            "elevation"
        ),
        "timezone": result.get(
            "timezone"
        ),
        "population": result.get(
            "population"
        ),

        # Normal city/place result.
        "is_state_representative": False,
        "state_name": result.get(
            "admin1"
        ),
        "representative_location": None,
    }


# ============================================================
# COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("FLOODVISION LOCATION SEARCH TEST")
    print("=" * 60)

    test_queries = [
        "Meghalaya",
        "Uttar Pradesh",
        "Tamil Nadu",
        "Chennai",
        "Shillong",
        "Lucknow",
    ]

    for query in test_queries:
        print(f"\nSearch: {query}")
        print("-" * 60)

        results = search_location(query)

        if not results:
            print("No results found.")
            continue

        for index, result in enumerate(
            results[:5],
            start=1,
        ):
            representative = result.get(
                "is_state_representative",
                False,
            )

            label = ""

            if representative:
                label = (
                    " [STATE/UT REPRESENTATIVE]"
                )

            print(
                f"[{index}] "
                f"{result['name']}, "
                f"{result.get('admin1')}, "
                f"{result['country']}"
                f"{label}"
            )

            print(
                f"    Latitude : "
                f"{result['latitude']}"
            )

            print(
                f"    Longitude: "
                f"{result['longitude']}"
            )
