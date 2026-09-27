import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  CloudRain,
  Droplets,
  Gauge,
  Map,
  MapPin,
  Navigation,
  Radio,
  Share2,
  ShieldAlert,
  Waves,
} from "lucide-react";

import { Button } from "@/components/ui/button";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

import type {
  FloodRiskResponse,
  LocationResult,
} from "@/services/api";

/* =========================================================
   TYPES
========================================================= */

type FloodCardProps = {
  flood: FloodRiskResponse;
  location?: LocationResult;
  onShare?: () => void;
};

type WeatherData = {
  T1d: number;
  T3d: number;
  T5d: number;
  T7d: number;
  T10d: number;

  Temperature: number;
  FeelsLike: number | null;
  Humidity: number;
  WindSpeed: number | null;
  WindDirection: number | null;
  CloudCover: number | null;
  Precipitation: number | null;
  ObservationTime: string | null;
};

/* =========================================================
   HELPERS
========================================================= */

function formatDate(value: string | null | undefined) {
  if (!value) {
    return "Date unavailable";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function formatDateTime(
  value: string | null | undefined,
) {
  if (!value) {
    return "Time unavailable";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatNumber(
  value: number | null | undefined,
  decimals = 2,
) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(value)
  ) {
    return "—";
  }

  return value.toFixed(decimals);
}

/* =========================================================
   SECTION TITLE
========================================================= */

function SectionTitle({
  eyebrow,
  title,
  description,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
}) {
  return (
    <div className="mb-5">
      {eyebrow && (
        <p className="text-xs font-bold uppercase text-brand">
          {eyebrow}
        </p>
      )}

      <h2 className="mt-1 text-2xl font-bold tracking-tight">
        {title}
      </h2>

      {description && (
        <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
          {description}
        </p>
      )}
    </div>
  );
}

/* =========================================================
   LOCATION
========================================================= */

export function LocationMap({
  location,
}: {
  location: LocationResult;
}) {
  const region = [
    location.admin1,
    location.admin2,
  ]
    .filter(Boolean)
    .join(", ");

  const isRepresentative =
    location.is_state_representative === true;

  return (
    <section
      className="grid overflow-hidden rounded-lg border border-border bg-card shadow-card lg:grid-cols-[0.8fr_1.2fr]"
      aria-labelledby="location-heading"
    >
      <div className="flex flex-col justify-between p-6 lg:p-8">
        <div>
          <p className="text-xs font-bold uppercase text-brand">
            Location being checked
          </p>

          <div className="mt-4 flex items-start gap-3">
            <span className="grid size-10 shrink-0 place-items-center rounded-md bg-brand-soft text-brand">
              <MapPin />
            </span>

            <div className="min-w-0">
              <h2
                id="location-heading"
                className="text-2xl font-bold"
              >
                {location.name}
              </h2>

              <p className="text-muted-foreground">
                {region}
                {region && location.country ? ", " : ""}
                {location.country}
              </p>

              {isRepresentative && (
                <div className="mt-3 inline-flex rounded-full bg-warning-soft px-3 py-1 text-xs font-semibold text-warning">
                  Representative location
                </div>
              )}
            </div>
          </div>

          {isRepresentative && (
            <p className="mt-4 max-w-md text-xs leading-5 text-muted-foreground">
              This location represents the selected state or
              territory for assessment purposes. It does not
              represent monitoring data from every part of the
              state.
            </p>
          )}
        </div>

        <div className="mt-8 flex gap-6 text-xs text-muted-foreground">
          <p>
            Latitude
            <strong className="block text-sm text-foreground">
              {location.latitude.toFixed(5)}
            </strong>
          </p>

          <p>
            Longitude
            <strong className="block text-sm text-foreground">
              {location.longitude.toFixed(5)}
            </strong>
          </p>
        </div>
      </div>

      <div
        className="map-surface relative min-h-72 overflow-hidden border-t border-border lg:border-l lg:border-t-0"
        aria-label={`Map preview centered on ${location.name}`}
      >
        <div className="map-grid absolute inset-0" />

        <div className="absolute inset-0 flex items-center justify-center">
          <div className="relative">
            <span className="absolute inset-0 animate-map-pulse rounded-full bg-brand/20" />

            <span className="relative grid size-14 place-items-center rounded-full border-4 border-card bg-brand text-primary-foreground shadow-lg">
              <Navigation
                className="size-6"
                fill="currentColor"
              />
            </span>
          </div>
        </div>

        <div className="absolute bottom-4 left-4 flex items-center gap-2 rounded-md border border-border bg-card/90 px-3 py-2 text-xs font-medium shadow-sm backdrop-blur">
          <Map className="size-4 text-brand" />
          Selected area preview
        </div>
      </div>
    </section>
  );
}

/* =========================================================
   FLOOD RISK
========================================================= */

export function FloodRiskCard({
  flood,
  onShare,
}: FloodCardProps) {
  const isFlood =
    flood.prediction.flood_status === "Flood";

  const probability = Math.max(
    0,
    Math.min(
      100,
      flood.prediction.flood_probability_percent,
    ),
  );

  const circumference = 2 * Math.PI * 52;

  const offset =
    circumference *
    (1 - probability / 100);

  const RiskIcon = isFlood
    ? ShieldAlert
    : CheckCircle2;

  const statusLabel = isFlood
    ? "FLOOD"
    : "NO FLOOD";

  return (
    <section
      id="risk"
      className={`scroll-mt-24 rounded-lg border p-6 shadow-card sm:p-8 ${
        isFlood
          ? "risk-flood"
          : "risk-safe"
      }`}
      aria-labelledby="risk-heading"
    >
      <div className="grid items-center gap-8 lg:grid-cols-[1fr_auto]">
        {/* STATUS */}

        <div>
          <p className="text-xs font-bold uppercase">
            Flood assessment
          </p>

          <div className="mt-4 flex items-center gap-3">
            <RiskIcon className="size-10 shrink-0" />

            <h2
              id="risk-heading"
              className="text-4xl font-extrabold uppercase sm:text-5xl"
            >
              {statusLabel}
            </h2>
          </div>

          <p className="mt-5 max-w-2xl text-base leading-7 opacity-85">
            {isFlood
              ? "The FloodVision model classified this location as Flood based on the available input data."
              : "The FloodVision model classified this location as No Flood based on the available input data."}
          </p>

          <div className="mt-6 flex flex-wrap gap-3">
            <Button
              variant="risk"
              onClick={() =>
                document
                  .getElementById("details")
                  ?.scrollIntoView({
                    behavior: "smooth",
                  })
              }
            >
              View details
            </Button>

            {onShare && (
              <Button
                variant="riskGhost"
                onClick={onShare}
              >
                <Share2 />
                Share result
              </Button>
            )}
          </div>
        </div>

        {/* PROBABILITY */}

        <div
          className="relative mx-auto size-40 shrink-0"
          aria-label={`Model-estimated flood probability ${probability.toFixed(
            2,
          )} percent`}
        >
          <svg
            className="size-full -rotate-90"
            viewBox="0 0 120 120"
            role="img"
            aria-hidden="true"
          >
            <circle
              cx="60"
              cy="60"
              r="52"
              fill="none"
              stroke="currentColor"
              strokeOpacity=".15"
              strokeWidth="8"
            />

            <circle
              className="confidence-ring"
              cx="60"
              cy="60"
              r="52"
              fill="none"
              stroke="currentColor"
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
            />
          </svg>

          <div className="absolute inset-0 grid place-content-center text-center">
            <strong className="text-3xl font-extrabold">
              {probability.toFixed(2)}%
            </strong>

            <span className="text-xs font-medium opacity-75">
              Model-estimated
              <br />
              flood probability
            </span>
          </div>
        </div>
      </div>

      {/* MODEL EXPLANATION */}

      <div className="mt-7 border-t border-current/15 pt-5">
        <p className="text-xs uppercase opacity-70">
          Model-estimated probability
        </p>

        <p className="mt-1 text-xl font-bold">
          {probability.toFixed(2)}%
        </p>

        <div className="mt-5 flex items-start gap-3">
          <AlertTriangle className="mt-0.5 size-5 shrink-0" />

          <div>
            <p className="font-semibold">
              Model estimate only
            </p>

            <p className="mt-1 text-sm leading-6 opacity-75">
              This percentage is produced by the FloodVision
              machine-learning system using the available input
              data. It is not an official flood warning, a
              guaranteed prediction, or a calibrated real-world
              probability. Follow official emergency alerts and
              local authority guidance.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

/* =========================================================
   WEATHER
========================================================= */

export function WeatherPanel({
  weather,
  fahrenheit,
  onUnits,
}: {
  weather: WeatherData;
  fahrenheit: boolean;
  onUnits: () => void;
}) {
  const temp = (
    value: number | null | undefined,
  ) => {
    if (
      value === null ||
      value === undefined
    ) {
      return "—";
    }

    return fahrenheit
      ? Math.round((value * 9) / 5 + 32)
      : Math.round(value);
  };

  const unit = fahrenheit
    ? "°F"
    : "°C";

  const windDirection = (
    degrees: number | null | undefined,
  ) => {
    if (
      degrees === null ||
      degrees === undefined
    ) {
      return "—";
    }

    const directions = [
      "N",
      "NE",
      "E",
      "SE",
      "S",
      "SW",
      "W",
      "NW",
    ];

    const index =
      Math.round(degrees / 45) % 8;

    return `${directions[index]} (${Math.round(
      degrees,
    )}°)`;
  };

  return (
    <section
      id="weather"
      className="scroll-mt-24 rounded-lg border border-border bg-card p-6 shadow-card sm:p-8"
      aria-labelledby="weather-heading"
    >
      <div className="flex items-start justify-between gap-4">
        <SectionTitle
          eyebrow="Weather information"
          title="Current weather"
          description="Recent weather conditions for the selected location."
        />

        <Button
          variant="outline"
          size="sm"
          onClick={onUnits}
          aria-label="Change temperature unit"
        >
          {fahrenheit ? "°F" : "°C"}
        </Button>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        {/* TEMPERATURE */}

        <div className="rounded-lg border border-border bg-muted/30 p-6">
          <div className="flex items-center gap-5">
            <span className="grid size-16 shrink-0 place-items-center rounded-lg bg-weather text-weather-foreground">
              <Gauge className="size-9" />
            </span>

            <div>
              <p className="text-5xl font-extrabold">
                {temp(weather.Temperature)}
                {unit}
              </p>

              <p className="mt-1 font-semibold">
                Current temperature
              </p>

              <p className="mt-1 text-sm text-muted-foreground">
                Feels like{" "}
                {temp(weather.FeelsLike)}
                {weather.FeelsLike !== null &&
                weather.FeelsLike !== undefined
                  ? unit
                  : ""}
              </p>
            </div>
          </div>

          {weather.ObservationTime && (
            <p className="mt-5 border-t border-border pt-4 text-xs text-muted-foreground">
              Updated{" "}
              {formatDateTime(
                weather.ObservationTime,
              )}
            </p>
          )}
        </div>

        {/* WEATHER METRICS */}

        <div className="grid grid-cols-2 gap-px overflow-hidden rounded-lg border border-border bg-border sm:grid-cols-3">
          <div className="bg-card p-4">
            <Droplets className="mb-2 size-5 text-brand" />

            <p className="text-xs text-muted-foreground">
              Humidity
            </p>

            <p className="font-bold">
              {weather.Humidity}%
            </p>
          </div>

          <div className="bg-card p-4">
            <Navigation className="mb-2 size-5 text-brand" />

            <p className="text-xs text-muted-foreground">
              Wind
            </p>

            <p className="font-bold">
              {weather.WindSpeed !== null &&
              weather.WindSpeed !== undefined
                ? `${weather.WindSpeed} km/h`
                : "—"}
            </p>

            <p className="mt-1 text-xs text-muted-foreground">
              {windDirection(
                weather.WindDirection,
              )}
            </p>
          </div>

          <div className="bg-card p-4">
            <CloudRain className="mb-2 size-5 text-brand" />

            <p className="text-xs text-muted-foreground">
              Cloud cover
            </p>

            <p className="font-bold">
              {weather.CloudCover !== null &&
              weather.CloudCover !== undefined
                ? `${weather.CloudCover}%`
                : "—"}
            </p>
          </div>

          <div className="bg-card p-4">
            <CloudRain className="mb-2 size-5 text-brand" />

            <p className="text-xs text-muted-foreground">
              Current precipitation
            </p>

            <p className="font-bold">
              {weather.Precipitation !== null &&
              weather.Precipitation !== undefined
                ? `${weather.Precipitation} mm`
                : "—"}
            </p>
          </div>
        </div>
      </div>

      {/* RAINFALL */}

      <div className="mt-8">
        <div className="mb-4">
          <p className="text-sm font-semibold">
            Recent rainfall
          </p>

          <p className="text-sm text-muted-foreground">
            Accumulated rainfall over recent periods.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
          {[
            ["Last 24 hours", weather.T1d],
            ["Last 3 days", weather.T3d],
            ["Last 5 days", weather.T5d],
            ["Last 7 days", weather.T7d],
            ["Last 10 days", weather.T10d],
          ].map(([label, value]) => (
            <div
              key={String(label)}
              className="rounded-lg border border-border bg-card p-4"
            >
              <CloudRain className="mb-2 size-5 text-brand" />

              <p className="text-xs text-muted-foreground">
                {label}
              </p>

              <p className="mt-1 text-lg font-bold">
                {value} mm
              </p>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6 rounded-lg border border-border bg-muted/30 p-4">
        <p className="text-sm text-muted-foreground">
          Weather information is provided as supporting
          environmental information. It is separate from the
          flood assessment shown above.
        </p>
      </div>
    </section>
  );
}

/* =========================================================
   FORECAST
========================================================= */

export function ForecastPanel() {
  return (
    <section className="rounded-lg border border-border bg-card p-6 shadow-card">
      <SectionTitle
        title="Weather information"
        description="The connected weather service currently supplies recent weather and rainfall measurements rather than a multi-day forecast."
      />

      <div className="rounded-md bg-surface-strong p-4 text-sm text-muted-foreground">
        Multi-day forecast information is not currently
        supplied by the connected flood-risk service.
      </div>
    </section>
  );
}

/* =========================================================
   RAINFALL
========================================================= */

export function RainfallPanel({
  flood,
}: {
  flood: FloodRiskResponse;
}) {
  const rainfall = [
    {
      period: "1 day",
      millimeters: flood.rainfall.T1d,
    },
    {
      period: "3 days",
      millimeters: flood.rainfall.T3d,
    },
    {
      period: "5 days",
      millimeters: flood.rainfall.T5d,
    },
    {
      period: "7 days",
      millimeters: flood.rainfall.T7d,
    },
    {
      period: "10 days",
      millimeters: flood.rainfall.T10d,
    },
  ];

  const max = Math.max(
    ...rainfall.map(
      (item) => item.millimeters,
    ),
    1,
  );

  return (
    <section
      className="rounded-lg border border-border bg-card p-6 shadow-card"
      aria-labelledby="rain-heading"
    >
      <SectionTitle
        eyebrow="Rainfall"
        title="Recent rainfall"
        description="Cumulative rainfall values available for the selected location."
      />

      <div className="flex h-64 items-end justify-between gap-3 border-b border-border px-1 pt-8 sm:gap-6">
        {rainfall.map((item) => (
          <div
            key={item.period}
            className="flex h-full min-w-0 flex-1 flex-col justify-end text-center"
          >
            <span className="mb-2 text-xs font-bold">
              {item.millimeters} mm
            </span>

            <div
              className="rain-bar mx-auto w-full max-w-14 rounded-t-md bg-brand"
              style={{
                height: `${Math.max(
                  (item.millimeters / max) * 82,
                  3,
                )}%`,
              }}
            />

            <span className="mt-3 text-[11px] text-muted-foreground sm:text-xs">
              {item.period}
            </span>
          </div>
        ))}
      </div>

      <p className="mt-4 text-xs leading-5 text-muted-foreground">
        Rainfall displayed here is supporting environmental
        information. The flood model uses its own CWC-derived
        rainfall features.
      </p>
    </section>
  );
}

/* =========================================================
   CWC MONITORING
========================================================= */

export function CWCMonitoringPanel({
  flood,
}: {
  flood: FloodRiskResponse;
}) {
  const cwc = flood.cwc;

  return (
    <section
      className="rounded-lg border border-border bg-card p-6 shadow-card sm:p-8"
      aria-labelledby="cwc-heading"
    >
      <div className="flex items-start gap-4">
        <span className="grid size-11 shrink-0 place-items-center rounded-md bg-brand-soft text-brand">
          <Waves className="size-6" />
        </span>

        <div className="min-w-0">
          <p className="text-xs font-bold uppercase text-brand">
            River monitoring
          </p>

          <h2
            id="cwc-heading"
            className="mt-1 text-2xl font-bold"
          >
            Latest available river monitoring
          </h2>

          <p className="mt-1 text-sm text-muted-foreground">
            Latest available Central Water Commission observation
            from the usable monitoring station associated with this
            location.
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          icon={<Radio />}
          label="Monitoring station"
          value={cwc.station}
        />

        <MetricCard
          icon={<Gauge />}
          label="Latest water level"
          value={`${formatNumber(
            cwc.latest_water_level,
          )} m`}
        />

        <MetricCard
          icon={<AlertTriangle />}
          label="Warning level"
          value={`${formatNumber(
            cwc.warning_level,
          )} m`}
        />

        <MetricCard
          icon={<ShieldAlert />}
          label="Danger level"
          value={`${formatNumber(
            cwc.danger_level,
          )} m`}
        />
      </div>

      <div className="mt-5 rounded-md bg-surface-strong p-4 text-sm">
        <p className="font-semibold">
          Latest available observation
        </p>

        <p className="mt-1 text-muted-foreground">
          {formatDate(cwc.latest_date)}
          {" · "}
          Monitoring station distance:{" "}
          {formatNumber(cwc.distance_km)} km
        </p>
      </div>

      <div className="mt-4 rounded-md border border-warning/30 bg-warning-soft p-4">
        <p className="text-xs leading-5 text-muted-foreground">
          This is the latest available CWC observation in the
          connected data source. It may not represent a real-time
          measurement for the selected location.
        </p>
      </div>
    </section>
  );
}

/* =========================================================
   CWC FEATURES
========================================================= */

export function CWCFeaturesPanel({
  flood,
}: {
  flood: FloodRiskResponse;
}) {
  const values = [
    [
      "Previous water level",
      `${formatNumber(
        flood.cwc_features.water_level_prev,
      )} m`,
    ],
    [
      "Previous maximum level",
      `${formatNumber(
        flood.cwc_features.water_level_max_prev,
      )} m`,
    ],
    [
      "3-day maximum level",
      `${formatNumber(
        flood.cwc_features.water_level_3d_max,
      )} m`,
    ],
    [
      "7-day maximum level",
      `${formatNumber(
        flood.cwc_features.water_level_7d_max,
      )} m`,
    ],
    [
      "Previous rainfall",
      `${formatNumber(
        flood.cwc_features.rainfall_prev,
        1,
      )} mm`,
    ],
    [
      "3-day rainfall",
      `${formatNumber(
        flood.cwc_features.rainfall_3d,
        1,
      )} mm`,
    ],
    [
      "7-day rainfall",
      `${formatNumber(
        flood.cwc_features.rainfall_7d,
        1,
      )} mm`,
    ],
  ];

  return (
    <section className="rounded-lg border border-border bg-card p-6 shadow-card">
      <SectionTitle
        eyebrow="Recent measurements"
        title="Recent monitoring data"
        description="Recent river-level and rainfall measurements associated with the selected location."
      />

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {values.map(([label, value]) => (
          <div
            key={label}
            className="rounded-md bg-surface-strong p-4"
          >
            <p className="text-xs text-muted-foreground">
              {label}
            </p>

            <p className="mt-1 font-bold">
              {value}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

/* =========================================================
   HISTORICAL REFERENCE
========================================================= */

export function ConditionsPanel({
  flood,
}: {
  flood: FloodRiskResponse;
}) {
  const reference =
    flood.historical_reference;

  const conditions = [
    {
      label: "Historical reference gauge",
      value: reference.station,
      description:
        "Nearest available INDOFLOODS historical reference gauge.",
    },
    {
      label: "Distance from selected location",
      value: `${formatNumber(
        reference.distance_km,
      )} km`,
      description:
        "Geographic distance to the historical reference gauge.",
    },
    {
      label: "Reference gauge state",
      value: reference.state,
      description:
        "State associated with the historical reference gauge.",
    },
    {
      label: "Basin",
      value: reference.basin,
      description:
        "River basin associated with the reference gauge.",
    },
  ];

  return (
    <section
      id="details"
      className="scroll-mt-24"
      aria-labelledby="conditions-heading"
    >
      <SectionTitle
        eyebrow="Historical reference"
        title="Historical reference data"
        description="Historical INDOFLOODS catchment information used as supporting environmental context."
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {conditions.map((condition) => (
          <article
            key={condition.label}
            className="rounded-lg border border-border bg-card p-5 shadow-card"
          >
            <span className="grid size-10 place-items-center rounded-md bg-brand-soft text-brand">
              <MapPin className="size-5" />
            </span>

            <h3 className="mt-4 font-bold">
              {condition.label}
            </h3>

            <p className="mt-1 break-words text-sm font-semibold text-brand">
              {condition.value}
            </p>

            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              {condition.description}
            </p>
          </article>
        ))}
      </div>

      <div className="mt-5 rounded-md border border-border bg-muted/30 p-4">
        <p className="text-xs leading-5 text-muted-foreground">
          The INDOFLOODS reference gauge is a historical
          environmental reference. It should not be interpreted as
          the selected location's current local river-monitoring
          station.
        </p>
      </div>
    </section>
  );
}

/* =========================================================
   DATA SOURCES AND COVERAGE
========================================================= */

export function CoveragePanel({
  flood,
}: {
  flood: FloodRiskResponse;
}) {
  const reference =
    flood.historical_reference;

  const cwc = flood.cwc;

  const historicalFar =
    reference.distance_km > 100;

  return (
    <section
      className={`rounded-lg border p-6 sm:p-8 ${
        historicalFar
          ? "border-warning/40 bg-warning-soft"
          : "border-border bg-card"
      }`}
      aria-labelledby="coverage-heading"
    >
      <div className="flex items-start gap-4">
        <span className="grid size-11 shrink-0 place-items-center rounded-md bg-card text-warning">
          <Radio />
        </span>

        <div className="min-w-0">
          <p className="text-xs font-bold uppercase text-muted-foreground">
            Data sources
          </p>

          <h2
            id="coverage-heading"
            className="mt-1 text-xl font-bold"
          >
            Data sources and coverage
          </h2>

          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            FloodVision uses separate sources for current river
            monitoring and historical environmental reference data.
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <SourceCard
          title="Selected location"
          value={
            flood.location
              ? `${flood.location.latitude.toFixed(
                  4,
                )}, ${flood.location.longitude.toFixed(4)}`
              : "Selected location"
          }
          description="Coordinates used for the assessment."
        />

        <SourceCard
          title="Historical INDOFLOODS reference"
          value={reference.station}
          description={`${formatNumber(
            reference.distance_km,
          )} km from selected location`}
        />

        <SourceCard
          title="CWC monitoring station"
          value={cwc.station}
          description={`${formatNumber(
            cwc.distance_km,
          )} km from selected location`}
        />
      </div>

      <div className="mt-6 rounded-md border border-border bg-card/70 p-5">
        <p className="font-semibold">
          How to interpret these sources
        </p>

        <p className="mt-2 text-sm leading-6 text-muted-foreground">
          Current river monitoring and historical catchment
          information come from separate data sources. The distances
          shown above indicate how far the available monitoring or
          reference station is from the selected location.
        </p>
      </div>

      {historicalFar && (
        <div className="mt-4 rounded-md border border-warning/30 bg-warning-soft p-4">
          <p className="text-sm font-semibold">
            Historical reference is relatively distant
          </p>

          <p className="mt-1 text-xs leading-5 text-muted-foreground">
            The nearest available INDOFLOODS historical reference
            gauge is more than 100 km from the selected location.
            This gauge is therefore presented as supporting
            environmental context rather than local current
            monitoring.
          </p>
        </div>
      )}
    </section>
  );
}

/* =========================================================
   SEVERITY
========================================================= */

export function SeverityPanel({
  flood,
}: {
  flood: FloodRiskResponse;
}) {
  const isFlood =
    flood.prediction.flood_status === "Flood";

  if (!isFlood) {
    return (
      <section className="rounded-lg border border-border bg-card p-6 shadow-card sm:p-8">
        <SectionTitle
          eyebrow="Second-stage model"
          title="Flood severity"
          description="Severity is evaluated only when a flood is detected."
        />

        <div className="rounded-md bg-surface-strong p-5">
          <p className="font-bold">
            Severity assessment not required
          </p>

          <p className="mt-1 text-sm text-muted-foreground">
            The flood model classified this location as No Flood,
            so the severity model was not applied.
          </p>
        </div>
      </section>
    );
  }

  const severity =
    flood.severity.severity ??
    "Flood";

  const probability =
    flood.severity
      .severity_probability_percent;

  return (
    <section className="rounded-lg border border-warning/40 bg-warning-soft p-6 shadow-card sm:p-8">
      <div className="flex items-start gap-4">
        <span className="grid size-11 shrink-0 place-items-center rounded-md bg-card text-warning">
          <ShieldAlert className="size-6" />
        </span>

        <div>
          <p className="text-xs font-bold uppercase text-warning">
            Second-stage model
          </p>

          <h2 className="mt-1 text-2xl font-bold">
            Flood severity
          </h2>

          <p className="mt-2 text-lg font-semibold">
            {severity}
          </p>

          {probability !== null &&
            probability !== undefined && (
              <p className="mt-2 text-sm text-muted-foreground">
                Model-estimated severity probability:{" "}
                <strong>
                  {probability.toFixed(2)}%
                </strong>
              </p>
            )}
        </div>
      </div>

      <p className="mt-5 text-sm leading-6 text-muted-foreground">
        The severity model was applied because the first-stage
        flood model classified this location as Flood.
      </p>
    </section>
  );
}

/* =========================================================
   SAFETY + TECHNICAL DETAILS
========================================================= */

export function PreparednessAndTechnical({
  flood,
}: {
  flood: FloodRiskResponse;
}) {
  const tips = [
    "Keep important documents protected.",
    "Avoid walking or driving through floodwater.",
    "Monitor official alerts and local authorities.",
    "Keep emergency supplies ready.",
  ];

  const isFlood =
    flood.prediction.flood_status === "Flood";

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* SAFETY */}

      <section
        className="rounded-lg bg-hero p-6 text-hero-foreground sm:p-8"
        aria-labelledby="prepared-heading"
      >
        <ShieldAlert className="size-8 text-brand-bright" />

        <h2
          id="prepared-heading"
          className="mt-4 text-2xl font-bold"
        >
          Safety guidance
        </h2>

        <p className="mt-2 text-sm leading-6 text-hero-muted">
          General safety guidance during periods of heavy rainfall
          or possible flooding.
        </p>

        <div className="mt-5 grid gap-3">
          {tips.map((tip) => (
            <p
              key={tip}
              className="flex items-start gap-2 text-sm text-hero-muted"
            >
              <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-brand-bright" />

              {tip}
            </p>
          ))}
        </div>
      </section>

      {/* TECHNICAL DETAILS */}

      <section className="rounded-lg border border-border bg-card px-6 shadow-card">
        <Accordion type="single" collapsible>
          <AccordionItem
            value="technical"
            className="border-0"
          >
            <AccordionTrigger className="py-6 text-base hover:no-underline">
              <span className="flex items-center gap-3">
                <BarChart3 className="size-5 text-muted-foreground" />
                Assessment details
              </span>
            </AccordionTrigger>

            <AccordionContent>
              <div className="space-y-4 text-sm leading-6 text-muted-foreground">
                <p>
                  FloodVision provides a machine-learning estimate
                  based on the input data available to the system for
                  the selected location.
                </p>

                <p>
                  The system uses a two-stage assessment. The first
                  model classifies the location as{" "}
                  <strong>Flood</strong> or{" "}
                  <strong>No Flood</strong>. The severity model is
                  evaluated only when the first model predicts Flood.
                </p>

                <p>
                  The displayed probability is a{" "}
                  <strong>model-estimated probability</strong>. It
                  should not be interpreted as an official flood
                  warning, a guaranteed prediction, or a calibrated
                  real-world probability.
                </p>

                <dl className="grid gap-3 sm:grid-cols-2">
                  <TechnicalItem
                    label="Flood status"
                    value={
                      flood.prediction
                        .flood_status
                    }
                  />

                  <TechnicalItem
                    label="Model-estimated probability"
                    value={`${flood.prediction.flood_probability_percent.toFixed(
                      2,
                    )}%`}
                  />

                  <TechnicalItem
                    label="CWC monitoring station"
                    value={flood.cwc.station}
                  />

                  <TechnicalItem
                    label="Latest water level"
                    value={`${formatNumber(
                      flood.cwc.latest_water_level,
                    )} m`}
                  />

                  <TechnicalItem
                    label="Warning level"
                    value={`${formatNumber(
                      flood.cwc.warning_level,
                    )} m`}
                  />

                  <TechnicalItem
                    label="Danger level"
                    value={`${formatNumber(
                      flood.cwc.danger_level,
                    )} m`}
                  />

                  <TechnicalItem
                    label="Flood severity"
                    value={
                      isFlood
                        ? flood.severity
                            .severity ??
                          "Not available"
                        : "Not applicable"
                    }
                  />

                  <TechnicalItem
                    label="CWC station distance"
                    value={`${formatNumber(
                      flood.cwc.distance_km,
                    )} km`}
                  />
                </dl>

                <div className="rounded-md border border-warning/30 bg-warning-soft p-4 text-xs">
                  For emergencies and official warnings, always
                  follow information issued by the appropriate
                  government authorities.
                </div>

                <p className="text-xs">
                  Internal clustering information is used by the
                  model but is not presented as a user-facing risk
                  classification.
                </p>
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </section>
    </div>
  );
}

/* =========================================================
   SMALL COMPONENTS
========================================================= */

function MetricCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-md bg-surface-strong p-4">
      <div className="mb-2 text-brand">
        {icon}
      </div>

      <p className="text-xs text-muted-foreground">
        {label}
      </p>

      <p className="mt-1 break-words font-bold">
        {value}
      </p>
    </div>
  );
}

function SourceCard({
  title,
  value,
  description,
}: {
  title: string;
  value: string;
  description: string;
}) {
  return (
    <div className="rounded-md border border-border bg-card p-5">
      <p className="text-xs font-bold uppercase text-muted-foreground">
        {title}
      </p>

      <p className="mt-2 break-words font-bold">
        {value}
      </p>

      <p className="mt-1 text-xs leading-5 text-muted-foreground">
        {description}
      </p>
    </div>
  );
}

function TechnicalItem({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-md bg-surface-strong p-3">
      <dt className="text-muted-foreground">
        {label}
      </dt>

      <dd className="mt-1 font-medium text-foreground">
        {value}
      </dd>
    </div>
  );
}