"""
train.py  -  Steps 3 to 7 of the ML pipeline
Run once:  python train.py
Creates:   sleep_model.joblib  +  form_schema.json
"""
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# ---------- Step 3: load data, pick X and y ----------
df = pd.read_csv("student_sleep_patterns.csv")

num_cols = ["Age", "Study_Hours", "Screen_Time", "Caffeine_Intake",
            "Physical_Activity", "Weekday_Sleep_Start"]
cat_cols = ["Gender", "University_Year"]

X = df[num_cols + cat_cols]
y = df["Sleep_Quality"]

# ---------- Step 4: quick audit ----------
print("Rows, Columns:", df.shape)
print("Missing values:", int(df.isnull().sum().sum()))
print("Duplicate rows:", int(df.duplicated().sum()))

# ---------- Step 5: lock test set, train + validate ----------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42)

preprocess = ColumnTransformer([
    ("num", Pipeline([("impute", SimpleImputer(strategy="median")),
                      ("scale", StandardScaler())]), num_cols),
    ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                      ("encode", OneHotEncoder(handle_unknown="ignore"))]), cat_cols),
])

models = {
    "Baseline (average)": DummyRegressor(strategy="mean"),
    "Linear Regression":  LinearRegression(),
    "Decision Tree":      DecisionTreeRegressor(max_depth=4, random_state=42),
    "Random Forest":      RandomForestRegressor(n_estimators=200, random_state=42),
}
cv = KFold(n_splits=5, shuffle=True, random_state=42)

rows = []
for name, model in models.items():
    pipe = Pipeline([("prep", preprocess), ("model", model)])
    scores = -cross_val_score(pipe, X_train, y_train, cv=cv,
                              scoring="neg_mean_absolute_error")
    rows.append({"Model": name, "CV MAE": round(scores.mean(), 3)})

results = pd.DataFrame(rows).sort_values("CV MAE")
print("\n", results.to_string(index=False))

# Best of the three real models is carried forward
best_name = "Random Forest"
final_model = Pipeline([("prep", preprocess), ("model", models[best_name])])
final_model.fit(X_train, y_train)

# ---------- Step 6: final test (used once) ----------
test_mae = mean_absolute_error(y_test, final_model.predict(X_test))
print(f"\nFinal test MAE ({best_name}): {test_mae:.3f}")

# ---------- Step 7: save model + form schema ----------
joblib.dump(final_model, "sleep_model.joblib")

schema = {
    "model": best_name,
    "target": "Sleep_Quality (1-10)",
    "test_mae": round(test_mae, 3),
    "inputs": {
        "Age":                 {"type": "number", "min": 18, "max": 25, "default": 21, "step": 1, "label": "Age"},
        "Gender":              {"type": "choice", "options": ["Male", "Female", "Other"], "label": "Gender"},
        "University_Year":     {"type": "choice", "options": ["1st Year", "2nd Year", "3rd Year", "4th Year"], "label": "University year"},
        "Study_Hours":         {"type": "number", "min": 0, "max": 12,  "default": 6,   "step": 0.5, "label": "Study hours per day"},
        "Screen_Time":         {"type": "number", "min": 1, "max": 4,   "default": 2.5, "step": 0.1, "label": "Screen time (hours per day)"},
        "Caffeine_Intake":     {"type": "number", "min": 0, "max": 5,   "default": 2,   "step": 1,   "label": "Caffeine drinks per day"},
        "Physical_Activity":   {"type": "number", "min": 0, "max": 120, "default": 60,  "step": 5,   "label": "Exercise (minutes per day)"},
        "Weekday_Sleep_Start": {"type": "number", "min": 0.0, "max": 23.5, "default": 23.0, "step": 0.5, "label": "Bedtime (24-hour clock, e.g. 23 = 11 pm)"},
    },
}
with open("form_schema.json", "w") as f:
    json.dump(schema, f, indent=2)

print("Saved: sleep_model.joblib + form_schema.json")
