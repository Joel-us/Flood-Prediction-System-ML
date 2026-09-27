import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from sklearn.metrics import (
    silhouette_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report
)

from sklearn.ensemble import RandomForestClassifier


# ============================================================
# FLOODVISION
# MODEL 1
#
# K-MEANS + RANDOM FOREST
# FLOOD / NO FLOOD
# ============================================================


ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = (
    ROOT
    / "data"
    / "processed"
    / "CWC_Flood_NoFlood.csv"
)

MODEL_FILE = (
    ROOT
    / "models"
    / "flood_model.joblib"
)


# ============================================================
# 1. LOAD DATA
# ============================================================

print("=" * 70)
print("       FLOODVISION - MODEL 1")
print("       K-MEANS + RANDOM FOREST")
print("       FLOOD / NO FLOOD")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(
    DATA_FILE
)

df["date_ist"] = pd.to_datetime(
    df["date_ist"]
)

df = df.sort_values(
    "date_ist"
).reset_index(
    drop=True
)

print("\nDataset loaded.")
print("Rows:", len(df))
print(
    "Stations:",
    df["station_code"].nunique()
)


# ============================================================
# 2. FEATURES
# ============================================================

features = [

    # Previous river conditions
    "water_level_prev",
    "water_level_max_prev",

    # Previous rainfall
    "rainfall_prev",
    "rainfall_3d",
    "rainfall_7d",

    # Previous water-level windows
    "water_level_3d_max",
    "water_level_7d_max",

    # Station thresholds
    "warning_level",
    "danger_level",

    # Threshold-relative features
    "water_level_danger_ratio",
    "water_level_warning_ratio",
    "water_level_max_danger_ratio",
    "water_level_3d_danger_ratio",
    "water_level_7d_danger_ratio",
    "danger_margin",
    "warning_margin"
]


target = "Flood"


# ============================================================
# 3. CLEAN DATA
# ============================================================

df = df.dropna(
    subset=features + [target]
).copy()

df[target] = (
    df[target]
    .astype(int)
)

print(
    "Usable rows:",
    len(df)
)


# ============================================================
# 4. CHECK TARGET DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("TARGET DISTRIBUTION")
print("=" * 70)

target_counts = (
    df[target]
    .value_counts()
    .sort_index()
)

print(
    target_counts
)

print("\nTarget percentages:")

print(
    df[target]
    .value_counts(
        normalize=True
    )
    .mul(100)
    .round(2)
)


# ============================================================
# 5. TIME-BASED TRAIN / TEST SPLIT
# ============================================================

split_date = pd.Timestamp(
    "2022-01-01"
)

train = df[
    df["date_ist"] < split_date
].copy()

test = df[
    df["date_ist"] >= split_date
].copy()


X_train = train[
    features
].copy()

y_train = train[
    target
].astype(int)


X_test = test[
    features
].copy()

y_test = test[
    target
].astype(int)


print("\n" + "=" * 70)
print("TIME-BASED SPLIT")
print("=" * 70)

print("\nTraining period:")

print(
    train["date_ist"].min().date(),
    "to",
    train["date_ist"].max().date()
)

print(
    "Training rows:",
    len(train)
)

print(
    "Training floods:",
    int(y_train.sum())
)

print(
    "Training no-flood:",
    int((y_train == 0).sum())
)


print("\nTesting period:")

print(
    test["date_ist"].min().date(),
    "to",
    test["date_ist"].max().date()
)

print(
    "Testing rows:",
    len(test)
)

print(
    "Testing floods:",
    int(y_test.sum())
)

print(
    "Testing no-flood:",
    int((y_test == 0).sum())
)


# ============================================================
# 6. STANDARDIZATION
# ============================================================

print("\n" + "=" * 70)
print("STANDARDIZATION")
print("=" * 70)

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(
    X_train
)

X_test_scaled = scaler.transform(
    X_test
)

print(
    "Scaling complete."
)


# ============================================================
# 7. K-MEANS
# ============================================================

print("\n" + "=" * 70)
print("K-MEANS CLUSTER SELECTION")
print("=" * 70)


# Use a sample to keep silhouette calculation manageable.
sample_size = min(
    50000,
    len(X_train_scaled)
)

rng = np.random.RandomState(
    42
)

sample_indices = rng.choice(
    len(X_train_scaled),
    size=sample_size,
    replace=False
)

X_cluster_sample = (
    X_train_scaled[
        sample_indices
    ]
)


best_k = None
best_score = -1

cluster_scores = {}


for k in range(2, 6):

    print(
        f"\nTesting K={k}..."
    )

    kmeans_test = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    labels = (
        kmeans_test
        .fit_predict(
            X_cluster_sample
        )
    )

    score = silhouette_score(
        X_cluster_sample,
        labels
    )

    cluster_scores[k] = float(
        score
    )

    print(
        f"K={k} -> "
        f"Silhouette Score: "
        f"{score:.4f}"
    )

    if score > best_score:

        best_score = score
        best_k = k


print("\nBest K:")
print(best_k)

print(
    "Best Silhouette Score:",
    round(best_score, 4)
)


# ============================================================
# 8. FINAL K-MEANS
# ============================================================

print("\n" + "=" * 70)
print("TRAINING FINAL K-MEANS")
print("=" * 70)

kmeans = KMeans(
    n_clusters=best_k,
    random_state=42,
    n_init=10
)

train_clusters = (
    kmeans
    .fit_predict(
        X_train_scaled
    )
)

test_clusters = (
    kmeans
    .predict(
        X_test_scaled
    )
)


print(
    "K-Means training complete."
)


# ============================================================
# 9. CLUSTER DISTRIBUTION
# ============================================================

print("\nTraining cluster distribution:")

unique, counts = np.unique(
    train_clusters,
    return_counts=True
)

for cluster, count in zip(
    unique,
    counts
):

    print(
        f"Cluster {cluster}: "
        f"{count:,} rows"
    )


# ============================================================
# 10. ADD K-MEANS CLUSTER
# ============================================================

X_train_rf = (
    X_train
    .copy()
)

X_test_rf = (
    X_test
    .copy()
)

X_train_rf[
    "KMeans_Cluster"
] = train_clusters

X_test_rf[
    "KMeans_Cluster"
] = test_clusters


# ============================================================
# 11. RANDOM FOREST
# ============================================================

print("\n" + "=" * 70)
print("RANDOM FOREST")
print("=" * 70)

rf = RandomForestClassifier(

    n_estimators=300,

    max_depth=18,

    min_samples_leaf=5,

    class_weight="balanced",

    random_state=42,

    n_jobs=-1
)


print(
    "Training Random Forest..."
)

rf.fit(
    X_train_rf,
    y_train
)

print(
    "Random Forest training complete."
)


# ============================================================
# 12. PREDICTION
# ============================================================

print("\nGenerating test predictions...")

y_pred = rf.predict(
    X_test_rf
)

y_prob = rf.predict_proba(
    X_test_rf
)[:, 1]


# ============================================================
# 13. EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    y_prob
)

pr_auc = average_precision_score(
    y_test,
    y_prob
)

cm = confusion_matrix(
    y_test,
    y_pred
)


# ============================================================
# 14. RESULTS
# ============================================================

print("\n" + "=" * 70)
print("MODEL 1 RESULTS")
print("=" * 70)

print(
    f"\nAccuracy : {accuracy:.4f}"
)

print(
    f"Precision: {precision:.4f}"
)

print(
    f"Recall   : {recall:.4f}"
)

print(
    f"F1 Score : {f1:.4f}"
)

print(
    f"ROC-AUC  : {roc_auc:.4f}"
)

print(
    f"PR-AUC   : {pr_auc:.4f}"
)


print("\nConfusion Matrix:")

print(cm)


print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "No Flood",
            "Flood"
        ],
        zero_division=0
    )
)


# ============================================================
# 15. FEATURE IMPORTANCE
# ============================================================

feature_names = (
    features
    + ["KMeans_Cluster"]
)

importance = pd.DataFrame({

    "Feature":
        feature_names,

    "Importance":
        rf.feature_importances_
})


importance = (
    importance
    .sort_values(
        "Importance",
        ascending=False
    )
)


print("\n" + "=" * 70)
print("FEATURE IMPORTANCE")
print("=" * 70)

print(
    importance.to_string(
        index=False
    )
)


# ============================================================
# 16. CLUSTER FLOOD ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("CLUSTER FLOOD ANALYSIS")
print("=" * 70)

cluster_analysis = pd.DataFrame({

    "Cluster":
        train_clusters,

    "Flood":
        y_train.values
})


cluster_summary = (
    cluster_analysis
    .groupby("Cluster")
    .agg(

        Records=(
            "Flood",
            "size"
        ),

        Floods=(
            "Flood",
            "sum"
        ),

        Flood_Rate=(
            "Flood",
            "mean"
        )
    )
    .reset_index()
)


cluster_summary[
    "Flood_Rate"
] *= 100


print(
    cluster_summary.to_string(
        index=False
    )
)


# ============================================================
# 17. CHECK PROBABILITY VARIATION
# ============================================================

print("\n" + "=" * 70)
print("PROBABILITY CHECK")
print("=" * 70)

print(
    "Minimum probability:",
    round(float(y_prob.min()), 6)
)

print(
    "Maximum probability:",
    round(float(y_prob.max()), 6)
)

print(
    "Mean probability:",
    round(float(y_prob.mean()), 6)
)

print(
    "Unique probability values:",
    len(np.unique(y_prob))
)


# ============================================================
# 18. SAVE MODEL
# ============================================================

MODEL_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


model_package = {

    "scaler":
        scaler,

    "kmeans":
        kmeans,

    "random_forest":
        rf,

    "features":
        features,

    "best_k":
        best_k,

    "silhouette_score":
        float(best_score),

    "split_date":
        str(split_date),

    "cluster_scores":
        cluster_scores
}


joblib.dump(
    model_package,
    MODEL_FILE
)


print("\n" + "=" * 70)
print("MODEL SAVED")
print("=" * 70)

print(
    MODEL_FILE
)

print(
    "\nK-Means + Random Forest "
    "Model 1 complete."
)