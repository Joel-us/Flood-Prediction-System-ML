import type { FloodRiskResponse, LocationResult } from "@/services/api";

export type FloodStatus = "Flood" | "No Flood";

export interface SelectedLocation {
  name: string;
  region: string;
  country: string;
  latitude: number;
  longitude: number;
}

export interface AssessmentBundle {
  location: SelectedLocation;
  result: FloodRiskResponse;
}

export type { FloodRiskResponse, LocationResult };