# tests_basic.py
# Automated checks for the Transit Delays assignment (runs without importing main.py)

import os, pandas as pd

CAPACITY = 60  # <-- needed for the Q2 check

print("cwd:", os.getcwd())
print("files here:", os.listdir())

candidates = ["test_small.csv", os.path.join("data", "test_small.csv")]
path = next((p for p in candidates if os.path.exists(p)), None)
if not path:
    raise FileNotFoundError("Could not find test_small.csv in . or ./data. Put it there and retry.")

print("Using:", path)
df = pd.read_csv(path, dtype=str)

# normalise columns (same logic as program)
df['passenger_count'] = pd.to_numeric(df['passenger_count'], errors='coerce').fillna(0).astype(int)
df['expected_departure'] = pd.to_datetime(df['expected_departure'], errors='coerce')
df['actual_departure'] = pd.to_datetime(df['actual_departure'], errors='coerce')
df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date

# labels
df['delta_minutes'] = (df['actual_departure'] - df['expected_departure']).dt.total_seconds() / 60.0
df['cancelled'] = df['actual_departure'].isna()
df['early'] = (~df['cancelled']) & (df['delta_minutes'] <= -2)
df['late'] = (~df['cancelled']) & (df['delta_minutes'] >= 5)
df['on_time'] = (~df['cancelled']) & (~df['early']) & (~df['late'])

# ----- Q1 -----
b_brad = df[df['stop_name'] == "Bradshaw Street"]
b_ocean = df[df['stop_name'] == "Ocean Avenue"]
assert b_brad['early'].sum() == 1
assert b_brad['on_time'].sum() == 1
assert b_brad['late'].sum() == 0
assert b_brad['cancelled'].sum() == 1
assert b_ocean['early'].sum() == 0
assert b_ocean['on_time'].sum() == 1
assert b_ocean['late'].sum() == 1
assert b_ocean['cancelled'].sum() == 0

# ----- Q2 -----
below_half = df[(~df['cancelled']) & (df['passenger_count'] < (CAPACITY / 2))]
assert len(below_half) == 3

# ----- Q3 -----
def simple_trend(sub):
    daily = sub.groupby('date').agg(avg=('passenger_count','mean')).reset_index().sort_values('date')
    if len(daily) < 2:
        return "not enough data"
    first = daily['avg'].iloc[0]
    last = daily['avg'].iloc[-1]
    if last >= first * 1.05:
        return "going up"
    elif last <= first * 0.95:
        return "going down"
    else:
        return "staying about the same"

assert simple_trend(b_brad) == "going down"
assert simple_trend(b_ocean) == "going down"

# ----- Q4 -----
start = pd.to_datetime("2025-03-01").date()
end = pd.to_datetime("2025-03-02").date()
subset = df[(df['date'] >= start) & (df['date'] <= end)]
affected = subset[(subset['cancelled']) | (subset['late'])]
assert affected['passenger_count'].sum() == 40

print("All automated tests passed.")

