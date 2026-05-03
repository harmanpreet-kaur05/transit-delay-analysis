# ITECH1400 Assignment 2 - Transit Delays
# Simple CLI program to analyse transit data from CSV

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

CAPACITY = 60

def load_data(file_name):
    df = pd.read_csv(file_name)
    df['actual_departure'] = df['actual_departure'].replace('none', np.nan)
    df['expected_departure'] = pd.to_datetime(df['expected_departure'], errors='coerce')
    df['actual_departure'] = pd.to_datetime(df['actual_departure'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['delay'] = (df['actual_departure'] - df['expected_departure']).dt.total_seconds() / 60
    df.loc[df['actual_departure'].isna(), 'delay'] = np.nan
    return df

def classify(row):
    if pd.isna(row['actual_departure']):
        return 'cancelled'
    if row['delay'] <= -2:
        return 'early'
    elif row['delay'] < 5:
        return 'on-time'
    else:
        return 'late'

def q1_status_percentages(df):
    df['status'] = df.apply(classify, axis=1)
    result = df.groupby(['stop_name', 'status']).size().unstack(fill_value=0)
    result = result[['early', 'on-time', 'late', 'cancelled']]
    percent = result.div(result.sum(axis=1), axis=0) * 100
    print("\nQ1: Percentage of departures by status at each stop\n")
    print(percent.round(2))
    percent.plot(kind='bar', stacked=True, figsize=(10,5))
    plt.title('Departure Status by Stop (%)')
    plt.ylabel('Percentage')
    plt.tight_layout()
    plt.savefig('q1_chart.png')
    plt.close()

def q2_low_capacity(df):
    count = (df['passenger_count'] < CAPACITY / 2).sum()
    print("\nQ2: Buses with less than half capacity:", count)

def q3_trend(df):
    print("\nQ3: Demand trend per stop\n")
    trends = []
    for stop, group in df.groupby('stop_name'):
        daily = group.groupby('date')['passenger_count'].sum().reset_index()
        if len(daily) < 2:
            trends.append((stop, 'same'))
            continue
        x = np.arange(len(daily))
        y = daily['passenger_count'].values
        slope = np.polyfit(x, y, 1)[0]
        if slope > 0.1:
            trends.append((stop, 'up'))
        elif slope < -0.1:
            trends.append((stop, 'down'))
        else:
            trends.append((stop, 'same'))
    for stop, t in trends:
        print(f"{stop}: {t}")

def q4_passengers_affected(df, start_date, end_date):
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    df_range = df[(df['date'] >= start) & (df['date'] <= end)]
    late = df_range[(df_range['delay'] >= 5) & df_range['actual_departure'].notna()]
    cancelled = df_range[df_range['actual_departure'].isna()]
    total = late['passenger_count'].sum() + cancelled['passenger_count'].sum()
    print(f"\nQ4: Passengers affected by late or cancelled ({start_date} to {end_date}): {int(total)}")

def q5_more_buses(df):
    df['status'] = df.apply(classify, axis=1)
    late_rate = df.groupby('stop_name').apply(lambda x: (x['status'] == 'late').mean())
    crowded_rate = df.groupby('stop_name').apply(lambda x: (x['passenger_count'] >= 0.8 * CAPACITY).mean())
    score = late_rate + crowded_rate
    result = pd.DataFrame({'late_rate': late_rate, 'crowded_rate': crowded_rate, 'score': score})
    result = result.sort_values('score', ascending=False)
    print("\nQ5: Stops that may need more buses\n")
    print(result.head(5))

def main():
    file_name = "transit_data_mar-jun_2025-30471465 (1).csv"
    df = load_data(file_name)
    q1_status_percentages(df)
    q2_low_capacity(df)
    q3_trend(df)
    q4_passengers_affected(df, "2025-03-01", "2025-06-30")
    q5_more_buses(df)
    print("\nAnalysis complete. Chart saved as q1_chart.png")

if __name__ == "__main__":
    main()

