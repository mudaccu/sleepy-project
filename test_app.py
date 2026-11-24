"""
test_app.py  -  Step 8 '-> test'
Run:  python test_app.py
Checks the saved model gives valid predictions for a few students.
"""
import joblib
import pandas as pd

model = joblib.load("sleep_model.joblib")

students = [
    {"Age": 21, "Gender": "Male", "University_Year": "2nd Year", "Study_Hours": 6,
     "Screen_Time": 3.5, "Caffeine_Intake": 4, "Physical_Activity": 15, "Weekday_Sleep_Start": 2},
    {"Age": 20, "Gender": "Female", "University_Year": "1st Year", "Study_Hours": 4,
     "Screen_Time": 1.0, "Caffeine_Intake": 0, "Physical_Activity": 90, "Weekday_Sleep_Start": 22},
    {"Age": 24, "Gender": "Other", "University_Year": "4th Year", "Study_Hours": 10,
     "Screen_Time": 2.5, "Caffeine_Intake": 2, "Physical_Activity": 45, "Weekday_Sleep_Start": 23},
]

preds = model.predict(pd.DataFrame(students))
for i, p in enumerate(preds, 1):
    assert 1 <= p <= 10, f"Student {i}: score {p} is outside 1-10"
    print(f"Student {i}: {p:.1f} / 10  ✅")
print("All tests passed ✅")
