import pandas as pd
from pathlib import Path


# ============================================================
# FLOODVISION
# BUILD / UPDATE FLOOD DATASET
#
# This version uses the existing CWC_Flood_NoFlood.csv
# and adds threshold-relative features.
#
# It DOES NOT download the large CWC parquet again.
# ============================================================


ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT
    / "data"
    / "processed"
    / "CWC_Flood_NoFlood.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "processed"
    / "CWC_Flood_NoFlood.csv"
)


# ============================================================
# 1. START
# ============================================================

print("=" * 70)
print("       FLOODVISION - UPDATE FLOOD DATASET")
print("=" * 70)


# ============================================================
# 2. LOAD EXISTING DATASET
# ============================================================

print("\nLoading existing dataset...")

df = pd.read_csv(
    INPUT_FILE
)

print(
    f"Rows loaded: {len(df):,}"
)

print(
    f"Columns loaded: {len(df.columns)}"
)


# ============================================================
# 3. CHECK REQUIRED ORIGINAL COLUMNS
# ============================================================

required_columns = [

    "water_level_prev",
    "water_level_max_prev",

    "rainfall_prev",
    "rainfall_3d",
    "rainfall_7d",

    "water_level_3d_max",
    "water_level_7d_max",

    "warning_level",
    "danger_level",

    "Flood"
]


missing = [
    col
    for col in required_columns
    if col not in df.columns
]


if missing:

    print("\nERROR:")
    print("The following required columns are missing:")

    for col in missing:
        print(
            " -",
            col
        )

    raise SystemExit(
        "\nDataset structure is not compatible."
    )


# ============================================================
# 4. CONVERT NUMERIC COLUMNS
# ============================================================

numeric_columns = [

    "water_level_prev",
    "water_level_max_prev",

    "rainfall_prev",
    "rainfall_3d",
    "rainfall_7d",

    "water_level_3d_max",
    "water_level_7d_max",

    "warning_level",
    "danger_level"
]


for col in numeric_columns:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )


# ============================================================
# 5. CREATE THRESHOLD-RELATIVE FEATURES
# ============================================================

print("\nCreating threshold-relative features...")


# ------------------------------------------------------------
# Previous water level / danger level
# ------------------------------------------------------------

df["water_level_danger_ratio"] = (
    df["water_level_prev"]
    / df["danger_level"]
)


# ------------------------------------------------------------
# Previous water level / warning level
# ------------------------------------------------------------

df["water_level_warning_ratio"] = (
    df["water_level_prev"]
    / df["warning_level"]
)


# ------------------------------------------------------------
# Previous maximum water level / danger level
# ------------------------------------------------------------

df["water_level_max_danger_ratio"] = (
    df["water_level_max_prev"]
    / df["danger_level"]
)


# ------------------------------------------------------------
# Previous 3-day maximum / danger level
# ------------------------------------------------------------

df["water_level_3d_danger_ratio"] = (
    df["water_level_3d_max"]
    / df["danger_level"]
)


# ------------------------------------------------------------
# Previous 7-day maximum / danger level
# ------------------------------------------------------------

df["water_level_7d_danger_ratio"] = (
    df["water_level_7d_max"]
    / df["danger_level"]
)


# ------------------------------------------------------------
# Distance from danger level
# ------------------------------------------------------------

df["danger_margin"] = (
    df["danger_level"]
    - df["water_level_prev"]
)


# ------------------------------------------------------------
# Distance from warning level
# ------------------------------------------------------------

df["warning_margin"] = (
    df["warning_level"]
    - df["water_level_prev"]
)


# ============================================================
# 6. CLEAN INVALID VALUES
# ============================================================

new_features = [

    "water_level_danger_ratio",
    "water_level_warning_ratio",
    "water_level_max_danger_ratio",
    "water_level_3d_danger_ratio",
    "water_level_7d_danger_ratio",
    "danger_margin",
    "warning_margin"
]


df = df.replace(
    [float("inf"), float("-inf")],
    pd.NA
)


before = len(df)


df = df.dropna(
    subset=required_columns + new_features
).copy()


after = len(df)


print(
    f"\nRows before cleaning: {before:,}"
)

print(
    f"Rows after cleaning : {after:,}"
)

print(
    f"Rows removed        : {before - after:,}"
)


# ============================================================
# 7. DISPLAY NEW FEATURES
# ============================================================

print("\nNew features:")

for col in new_features:

    print(
        f" - {col}"
    )


# ============================================================
# 8. SHOW SAMPLE
# ============================================================

print("\nSample threshold-relative values:")

sample_columns = [

    "water_level_prev",
    "warning_level",
    "danger_level",

    "water_level_danger_ratio",
    "water_level_warning_ratio",

    "danger_margin",
    "warning_margin"
]


print(
    df[
        sample_columns
    ].head(10).to_string(
        index=False
    )
)


# ============================================================
# 9. FLOOD DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("FLOOD DISTRIBUTION")
print("=" * 70)


print(
    df["Flood"]
    .value_counts()
    .sort_index()
)


print("\nPercentage:")


print(
    df["Flood"]
    .value_counts(
        normalize=True
    )
    .mul(100)
    .round(2)
)


# ============================================================
# 10. SAVE
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 11. FINISH
# ============================================================

print("\n" + "=" * 70)
print("DATASET UPDATED SUCCESSFULLY")
print("=" * 70)

print(
    "\nSaved to:"
)

print(
    OUTPUT_FILE
)

print(
    "\nRows:",
    len(df)
)

print(
    "Columns:",
    len(df.columns)
)

print("\nDone.")