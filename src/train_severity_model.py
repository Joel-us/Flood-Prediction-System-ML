import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# FLOODVISION - MODEL 2
# FLOOD SEVERITY
# FLOOD vs SEVERE FLOOD
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = (
    ROOT
    / "data"
    / "processed"
    / "INDOFLOODS_Master.csv"
)

MODEL_FILE = (
    ROOT
    / "models"
    / "severity_model.joblib"
)


print("=" * 65)
print("       FLOODVISION - MODEL 2")
print("       FLOOD SEVERITY PREDICTION")
print("       FLOOD vs SEVERE FLOOD")
print("=" * 65)


# ============================================================
# 1. LOAD DATA
# ============================================================

df = pd.read_csv(DATA_FILE)

print("\nDataset loaded")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# ============================================================
# 2. TARGET
# ============================================================

target = "Flood Type"

# Keep only the two documented severity classes
df = df[
    df[target].isin([
        "Flood",
        "Severe Flood"
    ])
].copy()

print("\nTarget distribution:")
print(df[target].value_counts())


# ============================================================
# 3. FEATURES
# ============================================================

numeric_features = [
    "T1d",
    "T3d",
    "T5d",
    "T7d",
    "T10d",

    "Annual Mean Temperature",
    "Annual Precipitation",

    "Stream Order",
    "Drainage Area",
    "Catchment Relief",
    "Drainage Density",
    "Ruggedness Number",
    "Population Density"
]

categorical_features = [
    "KoppenGeiger Climate Type",
    "Land cover",
    "Soil type",
    "lithology type"
]

features = (
    numeric_features
    + categorical_features
)


# ============================================================
# 4. CHECK FEATURES
# ============================================================

missing_features = [
    col
    for col in features
    if col not in df.columns
]

if missing_features:
    raise ValueError(
        "Missing required features:\n"
        + "\n".join(missing_features)
    )

print("\nFeatures:")
for feature in features:
    print(" -", feature)


# ============================================================
# 5. TARGET ENCODING
# ============================================================

# Flood = 0
# Severe Flood = 1

df["Severity"] = (
    df[target]
    .map({
        "Flood": 0,
        "Severe Flood": 1
    })
)

X = df[features].copy()
y = df["Severity"].astype(int)


# ============================================================
# 6. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\n" + "=" * 65)
print("TRAIN / TEST SPLIT")
print("=" * 65)

print("Training rows:", len(X_train))
print("Testing rows :", len(X_test))

print("\nTraining target:")
print(y_train.value_counts())

print("\nTesting target:")
print(y_test.value_counts())


# ============================================================
# 7. PREPROCESSING
# ============================================================

numeric_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="median")
    ),
    (
        "scaler",
        StandardScaler()
    )
])


categorical_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="most_frequent")
    ),
    (
        "encoder",
        OneHotEncoder(
            handle_unknown="ignore",
            sparse_output=False
        )
    )
])


preprocessor = ColumnTransformer([
    (
        "numeric",
        numeric_pipeline,
        numeric_features
    ),
    (
        "categorical",
        categorical_pipeline,
        categorical_features
    )
])


# ============================================================
# 8. RANDOM FOREST
# ============================================================

random_forest = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)


model = Pipeline([
    (
        "preprocessor",
        preprocessor
    ),
    (
        "random_forest",
        random_forest
    )
])


# ============================================================
# 9. TRAIN
# ============================================================

print("\n" + "=" * 65)
print("TRAINING MODEL 2")
print("=" * 65)

print("Training Random Forest...")

model.fit(
    X_train,
    y_train
)

print("Training complete.")


# ============================================================
# 10. PREDICTION
# ============================================================

y_pred = model.predict(X_test)

y_prob = model.predict_proba(
    X_test
)[:, 1]


# ============================================================
# 11. EVALUATION
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

cm = confusion_matrix(
    y_test,
    y_pred
)


print("\n" + "=" * 65)
print("MODEL 2 RESULTS")
print("=" * 65)

print(f"\nAccuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")
print(f"ROC-AUC  : {roc_auc:.4f}")


# ============================================================
# 12. CONFUSION MATRIX
# ============================================================

print("\nConfusion Matrix:")
print(cm)


# ============================================================
# 13. CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Flood",
            "Severe Flood"
        ],
        zero_division=0
    )
)


# ============================================================
# 14. FEATURE IMPORTANCE
# ============================================================

rf = model.named_steps["random_forest"]

preprocessor_fitted = (
    model.named_steps["preprocessor"]
)

feature_names = (
    preprocessor_fitted
    .get_feature_names_out()
)

importance = pd.DataFrame({
    "Feature": feature_names,
    "Importance": rf.feature_importances_
})

importance = importance.sort_values(
    "Importance",
    ascending=False
)

print("\n" + "=" * 65)
print("TOP 20 FEATURE IMPORTANCES")
print("=" * 65)

print(
    importance
    .head(20)
    .to_string(index=False)
)


# ============================================================
# 15. SAVE MODEL
# ============================================================

MODEL_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

model_package = {
    "model": model,
    "features": features,
    "numeric_features": numeric_features,
    "categorical_features": categorical_features,

    "target_mapping": {
        0: "Flood",
        1: "Severe Flood"
    }
}


joblib.dump(
    model_package,
    MODEL_FILE
)


print("\n" + "=" * 65)
print("MODEL 2 SAVED")
print("=" * 65)

print(MODEL_FILE)

print("\nModel 2 training complete.")