import { createFileRoute } from "@tanstack/react-router";
import {
  ArrowDown,
  CloudRain,
  LocateFixed,
  MapPin,
  ShieldCheck,
  Waves,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";

import floodLandscape from "@/assets/floodvision-landscape.jpg";
import { Button } from "@/components/ui/button";

import { Navbar, Footer } from "@/features/floodvision/brand-shell";
import { LoadingState } from "@/features/floodvision/loading-state";
import { LocationSearch } from "@/features/floodvision/location-search";

import {
  LocationMap,
  FloodRiskCard,
  SeverityPanel,
  WeatherPanel,
  RainfallPanel,
  CWCMonitoringPanel,
  CWCFeaturesPanel,
  ConditionsPanel,
  CoveragePanel,
  PreparednessAndTechnical,
} from "@/features/floodvision/result-cards";

import {
  api,
  type FloodRiskResponse,
  type LocationResult,
  type WeatherResponse,
} from "@/services/api";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      {
        title: "FloodVision",
      },
      {
        name: "description",
        content:
          "Flood prediction using location, rainfall, river water-level and machine learning data.",
      },
    ],
  }),

  component: Index,
});

/* =========================================================
   PAGE
========================================================= */

function Index() {
  const [dark, setDark] = useState(false);

  const [location, setLocation] =
    useState<LocationResult | null>(null);

  const [weather, setWeather] =
    useState<WeatherResponse | null>(null);

  const [floodResult, setFloodResult] =
    useState<FloodRiskResponse | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [stage, setStage] =
    useState(0);

  const [error, setError] =
    useState<string | null>(null);

  const [fahrenheit, setFahrenheit] =
    useState(false);

  const resultsRef =
    useRef<HTMLDivElement>(null);

  /* =======================================================
     DARK MODE
  ======================================================= */

  useEffect(() => {
    document.documentElement.classList.toggle(
      "dark",
      dark,
    );

    return () => {
      document.documentElement.classList.remove(
        "dark",
      );
    };
  }, [dark]);

  /* =======================================================
     NAVIGATION
  ======================================================= */

  const navigate = (id: string) => {
    const target = document.getElementById(id);

    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  };

  /* =======================================================
     FLOODVISION ASSESSMENT
  ======================================================= */

  const checkLocation = async (
    selectedLocation: LocationResult,
  ) => {
    setLoading(true);
    setError(null);

    setLocation(selectedLocation);
    setWeather(null);
    setFloodResult(null);
    setStage(1);

    try {
      /* ---------------------------------------------------
         STEP 1 — LOCATION
      --------------------------------------------------- */

      setStage(1);

      /* ---------------------------------------------------
         STEP 2 — WEATHER + FLOOD PREDICTION
      --------------------------------------------------- */

      setStage(2);

      const [
        weatherResponse,
        floodResponse,
      ] = await Promise.all([
        api.getWeather(
          selectedLocation.latitude,
          selectedLocation.longitude,
        ),

        api.getFloodRisk(
          selectedLocation.latitude,
          selectedLocation.longitude,
        ),
      ]);

      setWeather(weatherResponse);
      setFloodResult(floodResponse);

      /* ---------------------------------------------------
         STEP 3 — SEVERITY
         Backend handles the second-stage model.
      --------------------------------------------------- */

      if (
        floodResponse.prediction.flood_status ===
        "Flood"
      ) {
        setStage(3);
      }

      setLoading(false);

      window.setTimeout(() => {
        resultsRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }, 100);
    } catch (err) {
      console.error(
        "FloodVision assessment failed:",
        err,
      );

      setLoading(false);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to calculate flood risk for this location.",
      );
    }
  };

  /* =======================================================
     SHARE RESULT
  ======================================================= */

  const shareResult = async () => {
    if (!location || !floodResult) {
      return;
    }

    const status =
      floodResult.prediction.flood_status;

    const probability =
      floodResult.prediction
        .flood_probability_percent;

    let text =
      `FloodVision assessment for ${location.name}: ` +
      `${status}. ` +
      `Model-estimated probability: ${probability.toFixed(
        2,
      )}%.`;

    if (floodResult.severity.severity) {
      text +=
        ` Severity: ${floodResult.severity.severity}.`;
    }

    try {
      if (navigator.share) {
        await navigator.share({
          title: "FloodVision Result",
          text,
          url: window.location.href,
        });
      } else if (navigator.clipboard) {
        await navigator.clipboard.writeText(
          `${text} ${window.location.href}`,
        );
      }
    } catch {
      // User cancelled sharing.
    }
  };

  /* =======================================================
     RENDER
  ======================================================= */

  return (
    <div className="min-h-screen bg-background text-foreground">

      {/* =================================================
          NAVBAR
      ================================================= */}

      <Navbar
        dark={dark}
        onThemeChange={() =>
          setDark((value) => !value)
        }
        onNavigate={navigate}
      />

      <main>

        {/* =================================================
            HERO
        ================================================= */}

        <section
          id="home"
          className="hero relative isolate flex min-h-[720px] scroll-mt-16 items-center pt-16 text-hero-foreground"
        >
          <div
            aria-hidden="true"
            className="absolute inset-0 -z-10 overflow-hidden"
          >
            <img
              src={floodLandscape}
              alt=""
              width={1920}
              height={1080}
              className="absolute inset-0 size-full object-cover"
            />

            <div className="hero-overlay absolute inset-0" />
          </div>

          <div className="relative mx-auto w-full max-w-7xl px-4 py-20 sm:px-6 lg:px-8">

            <div className="max-w-3xl">

              {/* Badge */}

              <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-hero-border bg-hero-soft px-3 py-1.5 text-xs font-semibold uppercase">
                <ShieldCheck className="size-4 text-brand-bright" />
                Machine Learning Flood Prediction
              </div>

              {/* Heading */}

              <h1 className="text-5xl font-extrabold leading-[1.05] sm:text-6xl lg:text-7xl">
                Flood prediction{" "}
                <span className="text-brand-bright">
                  before it becomes a problem.
                </span>
              </h1>

              {/* Description */}

              <p className="mt-6 max-w-2xl text-lg leading-8 text-hero-muted sm:text-xl">
                FloodVision combines rainfall,
                river water-level observations,
                location data and machine learning
                to estimate flood conditions.
              </p>

              {/* Hero Buttons */}

              <div className="mt-8 flex flex-wrap gap-3">

                <Button
                  variant="hero"
                  size="lg"
                  onClick={() =>
                    navigate("search")
                  }
                >
                  <LocateFixed />
                  Check Flood Risk
                </Button>

                <Button
                  variant="riskGhost"
                  size="lg"
                  onClick={() =>
                    navigate("dashboard")
                  }
                >
                  <Waves />
                  View Dashboard
                </Button>

              </div>
            </div>

            {/* =================================================
                LOCATION SEARCH
            ================================================= */}

            <div
              id="search"
              className="mt-12 scroll-mt-24"
            >
              <LocationSearch
                {...(
                  location
                    ? { selected: location }
                    : {}
                )}
                busy={loading}
                onCheck={checkLocation}
              />

              <p className="mt-3 text-center text-xs text-hero-muted">
                Search for a location to run the
                FloodVision machine-learning assessment.
              </p>
            </div>

          </div>

          {/* Scroll Down */}

          <button
            onClick={() =>
              navigate("dashboard")
            }
            className="absolute bottom-5 left-1/2 hidden -translate-x-1/2 text-hero-muted lg:block"
            aria-label="Scroll to dashboard"
          >
            <ArrowDown className="animate-bounce" />
          </button>

        </section>

        {/* =================================================
            DASHBOARD
        ================================================= */}

        <div
          id="dashboard"
          ref={resultsRef}
          className="scroll-mt-20"
        >

          {/* =================================================
              LOADING / ERROR / RESULTS / EMPTY
          ================================================= */}

          {loading ? (

            <LoadingState stage={stage} />

          ) : error ? (

            /* =================================================
               ERROR
            ================================================= */

            <section className="mx-auto max-w-3xl px-4 py-16 sm:px-6 lg:px-8">

              <div className="rounded-2xl border border-destructive/30 bg-destructive/5 p-6">

                <h2 className="text-xl font-bold">
                  Unable to complete the assessment
                </h2>

                <p className="mt-2 text-sm text-muted-foreground">
                  {error}
                </p>

                <Button
                  variant="outline"
                  className="mt-5"
                  onClick={() =>
                    setError(null)
                  }
                >
                  Try again
                </Button>

              </div>

            </section>

          ) : floodResult && location ? (

            /* =================================================
               RESULTS
            ================================================= */

            <div className="mx-auto max-w-7xl space-y-8 px-4 py-10 sm:px-6 sm:py-14 lg:px-8">

              {/* Assessment Header */}

              <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">

                <div>

                  <p className="text-xs font-bold uppercase tracking-wider text-brand">
                    FloodVision Assessment
                  </p>

                  <h2 className="mt-1 flex items-center gap-2 text-2xl font-bold">
                    <MapPin className="size-6 text-brand" />
                    {location.name}
                  </h2>

                  <p className="mt-1 text-sm text-muted-foreground">
                    {location.latitude.toFixed(4)}
                    {", "}
                    {location.longitude.toFixed(4)}
                  </p>

                </div>

                <Button
                  variant="outline"
                  onClick={shareResult}
                >
                  Share Result
                </Button>

              </div>

              {/* Location */}

              <LocationMap
                location={location}
              />

              {/* Flood Result */}

              <FloodRiskCard
                flood={floodResult}
                location={location}
                onShare={shareResult}
              />

              {/* Severity */}

              <SeverityPanel
                flood={floodResult}
              />

              {/* Weather */}

              {weather && (
                <WeatherPanel
                  weather={weather.weather}
                  fahrenheit={fahrenheit}
                  onUnits={() =>
                    setFahrenheit(
                      (value) => !value,
                    )
                  }
                />
              )}

              {/* Rainfall */}

              <RainfallPanel
                flood={floodResult}
              />

              {/* CWC Monitoring */}

              <CWCMonitoringPanel
                flood={floodResult}
              />

              {/* CWC Features */}

              <CWCFeaturesPanel
                flood={floodResult}
              />

              {/* Historical / Catchment Reference */}

              <ConditionsPanel
                flood={floodResult}
              />

              {/* Coverage */}

              <CoveragePanel
                flood={floodResult}
              />

              {/* Preparedness + Technical */}

              <PreparednessAndTechnical
                flood={floodResult}
              />

              {/* =================================================
                  DISCLAIMER
              ================================================= */}

              <section className="rounded-2xl border border-border bg-muted/30 p-6">

                <h3 className="font-bold">
                  Important information
                </h3>

                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                  FloodVision provides a
                  machine-learning estimate based
                  on available rainfall, weather and
                  river monitoring data. The displayed
                  probability is a model-estimated
                  probability and should not be
                  interpreted as an official flood
                  warning.
                </p>

                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                  For emergencies and official
                  warnings, always follow information
                  issued by the appropriate
                  government authorities.
                </p>

              </section>

            </div>

          ) : (

            /* =================================================
               EMPTY STATE
            ================================================= */

            <section
              className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8"
              aria-labelledby="empty-heading"
            >

              <div className="grid items-center gap-10 lg:grid-cols-2">

                <div>

                  <span className="grid size-14 place-items-center rounded-xl bg-brand-soft text-brand">
                    <Waves className="size-7" />
                  </span>

                  <h2
                    id="empty-heading"
                    className="mt-6 text-3xl font-bold"
                  >
                    Check flood conditions for
                    any location.
                  </h2>

                  <p className="mt-3 max-w-xl text-muted-foreground">
                    Search for a city or location
                    to receive a flood prediction
                    based on rainfall and river
                    monitoring data.
                  </p>

                  <Button
                    variant="hero"
                    size="lg"
                    className="mt-6"
                    onClick={() =>
                      navigate("search")
                    }
                  >
                    <LocateFixed />
                    Choose a location
                  </Button>

                </div>

                <div className="grid gap-3 sm:grid-cols-3">

                  <Feature
                    icon={<LocateFixed />}
                    title="Choose a place"
                    text="Search for a city or area."
                  />

                  <Feature
                    icon={<CloudRain />}
                    title="Get conditions"
                    text="View rainfall and river data."
                  />

                  <Feature
                    icon={<ShieldCheck />}
                    title="Predict flood"
                    text="Run the machine-learning models."
                  />

                </div>

              </div>

            </section>

          )}

        </div>

        {/* =================================================
            ABOUT
        ================================================= */}

        <section
          id="about"
          className="scroll-mt-20 border-t border-border bg-surface-strong py-16"
        >

          <div className="mx-auto grid max-w-7xl gap-10 px-4 sm:px-6 lg:grid-cols-3 lg:px-8">

            <div>

              <p className="text-xs font-bold uppercase text-brand">
                About FloodVision
              </p>

              <h2 className="mt-2 text-3xl font-bold">
                Machine learning for flood
                prediction.
              </h2>

            </div>

            <p className="text-sm leading-7 text-muted-foreground lg:col-span-2">
              FloodVision uses location information,
              recent rainfall, river water-level
              observations and machine-learning models
              to provide a two-stage assessment:
              first Flood or No Flood, followed by
              severity when a flood is predicted.
            </p>

          </div>

        </section>

        {/* =================================================
            PRIVACY + DISCLAIMER
        ================================================= */}

        <section className="border-t border-border bg-background py-10">

          <div className="mx-auto grid max-w-7xl gap-4 px-4 sm:grid-cols-2 sm:px-6 lg:px-8">

            <article
              id="privacy"
              className="scroll-mt-20 p-4"
            >

              <h2 className="font-bold">
                Privacy
              </h2>

              <p className="mt-2 text-sm text-muted-foreground">
                This frontend does not store searches
                or personal information.
              </p>

            </article>

            <article
              id="disclaimer"
              className="scroll-mt-20 p-4"
            >

              <h2 className="font-bold">
                Important disclaimer
              </h2>

              <p className="mt-2 text-sm text-muted-foreground">
                Model estimates do not replace
                official warnings or emergency
                services.
              </p>

            </article>

          </div>

        </section>

      </main>

      <Footer onNavigate={navigate} />

    </div>
  );
}

/* =========================================================
   FEATURE CARD
========================================================= */

function Feature({
  icon,
  title,
  text,
}: {
  icon: ReactNode;
  title: string;
  text: string;
}) {
  return (
    <article className="rounded-xl border border-border bg-card p-5 shadow-card">

      <div className="text-brand">
        {icon}
      </div>

      <h3 className="mt-8 font-bold">
        {title}
      </h3>

      <p className="mt-1 text-sm text-muted-foreground">
        {text}
      </p>

    </article>
  );
}