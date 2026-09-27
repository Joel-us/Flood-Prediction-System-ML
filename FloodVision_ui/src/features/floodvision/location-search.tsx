import {
  Check,
  LocateFixed,
  MapPin,
  Search,
} from "lucide-react";
import {
  useEffect,
  useRef,
  useState,
} from "react";

import { Button } from "@/components/ui/button";
import { api } from "@/services/api";

import type { LocationResult } from "@/services/api";

type Props = {
  selected?: LocationResult;
  busy: boolean;
  onCheck: (location: LocationResult) => void;
};

export function LocationSearch({
  selected,
  busy,
  onCheck,
}: Props) {
  const [query, setQuery] = useState(
    selected?.name ?? "",
  );

  const [choice, setChoice] =
    useState<LocationResult | undefined>(
      selected,
    );

  const [suggestions, setSuggestions] =
    useState<LocationResult[]>([]);

  const [focused, setFocused] =
    useState(false);

  const [searching, setSearching] =
    useState(false);

  const searchId = useRef(0);

  /* =======================================================
     SEARCH LOCATIONS
     ======================================================= */

  useEffect(() => {
    const trimmedQuery = query.trim();

    if (!trimmedQuery) {
      setSuggestions([]);
      setSearching(false);
      return;
    }

    /*
     * If the currently selected location is already
     * exactly what the user typed, don't search again.
     */
    if (
      choice?.name.toLowerCase() ===
      trimmedQuery.toLowerCase()
    ) {
      setSuggestions([choice]);
      setSearching(false);
      return;
    }

    const currentSearchId =
      ++searchId.current;

    const timer = window.setTimeout(
      async () => {
        try {
          setSearching(true);

          const response =
            await api.searchLocations(
              trimmedQuery,
            );

          /*
           * Ignore old requests if the user has
           * already typed something new.
           */
          if (
            currentSearchId !==
            searchId.current
          ) {
            return;
          }

          setSuggestions(
            response.results ?? [],
          );
        } catch (error) {
          console.error(
            "Location search failed:",
            error,
          );

          if (
            currentSearchId ===
            searchId.current
          ) {
            setSuggestions([]);
          }
        } finally {
          if (
            currentSearchId ===
            searchId.current
          ) {
            setSearching(false);
          }
        }
      },
      350,
    );

    return () => {
      window.clearTimeout(timer);
    };
  }, [query, choice]);

  /* =======================================================
     SYNC SELECTED LOCATION
     ======================================================= */

  useEffect(() => {
    if (!selected) {
      return;
    }

    setQuery(selected.name);
    setChoice(selected);
    setSuggestions([selected]);
  }, [selected]);

  /* =======================================================
     SHOW SUGGESTIONS
     ======================================================= */

  const showSuggestions =
    focused &&
    query.trim().length > 0 &&
    choice?.name.toLowerCase() !==
      query.trim().toLowerCase();

  /* =======================================================
     SELECT LOCATION
     ======================================================= */

  const handleSelect = (
    location: LocationResult,
  ) => {
    setChoice(location);
    setQuery(location.name);
    setSuggestions([location]);
    setFocused(false);
  };

  /* =======================================================
     RUN FLOOD CHECK
     ======================================================= */

  const handleCheck = () => {
    const next =
      choice ?? suggestions[0];

    if (!next) {
      return;
    }

    onCheck(next);
  };

  /* =======================================================
     LOCATION LABEL
     ======================================================= */

  const getLocationDetails = (
    location: LocationResult,
  ) => {
    const parts = [
      location.admin1,
      location.admin2,
      location.country,
    ].filter(Boolean);

    return parts.join(", ");
  };

  /* =======================================================
     UI
     ======================================================= */

  return (
    <div className="relative z-20 mx-auto w-full max-w-3xl rounded-lg border border-hero-border bg-search p-2 shadow-search sm:flex sm:items-center">

      {/* =================================================
          SEARCH INPUT
          ================================================= */}

      <div className="relative min-w-0 flex-1">

        <label
          htmlFor="location-search"
          className="sr-only"
        >
          Search for a city or location
        </label>

        <Search className="pointer-events-none absolute left-4 top-1/2 size-5 -translate-y-1/2 text-muted-foreground" />

        <input
          id="location-search"
          value={query}
          onFocus={() =>
            setFocused(true)
          }
          onBlur={() =>
            window.setTimeout(
              () =>
                setFocused(false),
              180,
            )
          }
          onChange={(event) => {
            setQuery(
              event.target.value,
            );

            /*
             * The old selection is no longer
             * valid once the user starts typing.
             */
            setChoice(undefined);
          }}
          onKeyDown={(event) => {
            if (
              event.key === "Enter"
            ) {
              event.preventDefault();

              const first =
                suggestions[0];

              if (first) {
                handleSelect(first);
                onCheck(first);
              }
            }
          }}
          placeholder="Search for a city or location..."
          autoComplete="off"
          className="h-14 w-full bg-transparent pl-12 pr-4 text-base text-search-foreground outline-none placeholder:text-muted-foreground"
        />

        {/* =================================================
            SUGGESTIONS
            ================================================= */}

        {showSuggestions && (
          <div className="absolute left-0 right-0 top-[calc(100%+0.75rem)] overflow-hidden rounded-lg border border-border bg-popover p-1 text-popover-foreground shadow-xl">

            {/* SEARCHING */}

            {searching ? (

              <div className="px-3 py-4 text-sm text-muted-foreground">
                Searching locations...
              </div>

            ) : suggestions.length > 0 ? (

              /* =============================================
                 RESULTS
                 ============================================= */

              suggestions.map(
                (location, index) => (
                  <button
                    key={`${location.latitude}-${location.longitude}-${index}`}
                    type="button"
                    className="flex w-full items-center gap-3 rounded-md px-3 py-3 text-left hover:bg-accent"
                    onMouseDown={(event) => {
                      event.preventDefault();

                      handleSelect(
                        location,
                      );
                    }}
                  >

                    <MapPin className="size-4 shrink-0 text-brand" />

                    <span className="min-w-0">

                      <span className="block font-medium">
                        {location.name}
                      </span>

                      <span className="block truncate text-xs text-muted-foreground">
                        {getLocationDetails(
                          location,
                        )}
                      </span>

                    </span>

                  </button>
                ),
              )

            ) : (

              /* =============================================
                 NO RESULTS
                 ============================================= */

              <p className="px-3 py-4 text-sm text-muted-foreground">
                Location not found. Try searching
                for another city.
              </p>

            )}

          </div>
        )}

      </div>

      {/* =================================================
          CHECK FLOOD RISK BUTTON
          ================================================= */}

      <Button
        variant="hero"
        size="lg"
        className="mt-2 h-12 w-full sm:mt-0 sm:w-auto"
        disabled={
          busy ||
          searching ||
          (!choice &&
            !suggestions[0])
        }
        onClick={handleCheck}
      >

        {busy ? (

          <LocateFixed className="animate-spin" />

        ) : choice ? (

          <Check />

        ) : (

          <LocateFixed />

        )}

        {busy
          ? "Checking..."
          : "Check Flood Risk"}

      </Button>

    </div>
  );
}