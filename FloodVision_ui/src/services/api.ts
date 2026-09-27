const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

/* =========================================================
   LOCATION
   ========================================================= */

export interface LocationResult {
  name: string;
  latitude: number;
  longitude: number;
  country: string;
  country_code?: string;
  admin1?: string;
  admin2?: string;
  elevation?: number;
  timezone?: string;
  population?: number;

  /* State / UT representative location */
  is_state_representative?: boolean;
  state_name?: string;
  representative_location?: string | null;
}

export interface LocationSearchResponse {
  query: string;
  results: LocationResult[];
}

/* =========================================================
   WEATHER
   ========================================================= */

export interface WeatherResponse {
  latitude: number;
  longitude: number;

  weather: {
    /* Recent rainfall */
    T1d: number;
    T3d: number;
    T5d: number;
    T7d: number;
    T10d: number;

    /* Current weather */
    Temperature: number;
    FeelsLike: number | null;
    Humidity: number;
    WindSpeed: number | null;
    WindDirection: number | null;
    CloudCover: number | null;
    Precipitation: number | null;
    ObservationTime: string | null;
  };
}

/* =========================================================
   FLOOD RISK
   ========================================================= */

export type FloodStatus = "Flood" | "No Flood";

export type SeverityStatus =
  | "Flood"
  | "Severe Flood"
  | null;

export interface FloodRiskResponse {
  location: {
    latitude: number;
    longitude: number;
  };

  /* -------------------------------------------------------
     MODEL 1: FLOOD / NO FLOOD
     ------------------------------------------------------- */

  prediction: {
    flood_status: FloodStatus;

    /*
      Probability produced by the Random Forest model.

      This is a model-estimated probability.
      It is NOT an official flood warning and should not
      be interpreted as a guaranteed real-world probability.
    */

    flood_probability: number;

    flood_probability_percent: number;

    /*
      Internal K-Means cluster.
      Normally hidden from non-technical users.
    */

    cluster: number;
  };

  /* -------------------------------------------------------
     MODEL 2: SEVERITY
     ------------------------------------------------------- */

  severity: {
    severity: SeverityStatus;

    severity_probability: number | null;

    severity_probability_percent: number | null;
  };

  /* -------------------------------------------------------
     HISTORICAL INDOFLOODS REFERENCE
     ------------------------------------------------------- */

  historical_reference: {
    gauge_id: string;

    station: string;

    state: string;

    basin: string;

    latitude: number;

    longitude: number;

    distance_km: number;
  };

  /* -------------------------------------------------------
     CWC CURRENT MONITORING STATION
     ------------------------------------------------------- */

  cwc: {
    station: string;

    station_code: string;

    distance_km: number;

    warning_level: number;

    danger_level: number;

    latest_date: string;

    latest_water_level: number;

    latest_water_level_max: number;
  };

  /* -------------------------------------------------------
     CWC FEATURES USED BY FLOOD MODEL
     ------------------------------------------------------- */

  cwc_features: {
    water_level_prev: number;

    water_level_max_prev: number;

    water_level_3d_max: number;

    water_level_7d_max: number;

    rainfall_prev: number;

    rainfall_3d: number;

    rainfall_7d: number;

    /*
      These additional threshold-related features are used
      internally by Model 1.
    */

    water_level_danger_ratio?: number;

    water_level_warning_ratio?: number;

    water_level_max_danger_ratio?: number;

    water_level_3d_danger_ratio?: number;

    water_level_7d_danger_ratio?: number;

    danger_margin?: number;

    warning_margin?: number;
  };

  /* -------------------------------------------------------
     OPEN-METEO RECENT RAINFALL
     ------------------------------------------------------- */

  rainfall: {
    T1d: number;

    T3d: number;

    T5d: number;

    T7d: number;

    T10d: number;
  };
}

/* =========================================================
   GENERIC FETCH FUNCTION
   ========================================================= */

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url);

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    try {
      const error = await response.json();

      if (error?.detail) {
        message = error.detail;
      } else if (error?.message) {
        message = error.message;
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(message);
  }

  return response.json();
}

/* =========================================================
   SEARCH LOCATIONS
   ========================================================= */

export async function searchLocations(
  query: string,
): Promise<LocationSearchResponse> {
  if (!query.trim()) {
    return {
      query,
      results: [],
    };
  }

  const url =
    `${API_BASE_URL}/locations` +
    `?query=${encodeURIComponent(query.trim())}`;

  return fetchJson<LocationSearchResponse>(url);
}

/* =========================================================
   GET WEATHER
   ========================================================= */

export async function getWeather(
  latitude: number,
  longitude: number,
): Promise<WeatherResponse> {
  const url =
    `${API_BASE_URL}/weather` +
    `?latitude=${encodeURIComponent(latitude)}` +
    `&longitude=${encodeURIComponent(longitude)}`;

  return fetchJson<WeatherResponse>(url);
}

/* =========================================================
   GET FLOOD RISK
   ========================================================= */

export async function getFloodRisk(
  latitude: number,
  longitude: number,
): Promise<FloodRiskResponse> {
  const url =
    `${API_BASE_URL}/flood-risk` +
    `?latitude=${encodeURIComponent(latitude)}` +
    `&longitude=${encodeURIComponent(longitude)}`;

  return fetchJson<FloodRiskResponse>(url);
}

/* =========================================================
   CHECK BACKEND HEALTH
   ========================================================= */

export async function checkApiHealth(): Promise<boolean> {
  try {
    const result = await fetchJson<{ status: string }>(
      `${API_BASE_URL}/health`,
    );

    return result.status === "ok";
  } catch {
    return false;
  }
}

/* =========================================================
   API OBJECT
   ========================================================= */

export const api = {
  searchLocations,
  getWeather,
  getFloodRisk,
  checkApiHealth,
};