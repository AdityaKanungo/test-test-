import pandas as pd
import numpy as np

# ---- 1.1  Load & basic cleaning ---------------------------------------------
df = pd.read_csv("call_center_daily.csv")        # adapt as needed
df['Day'] = pd.to_datetime(df['Day'])           # ensure true datetimes
df = df.sort_values('Day').reset_index(drop=True)

# ---- 1.2  Forward-fill 3-day post-holiday window ----------------------------
# Identify index positions where the current row is a holiday
holiday_idx = df.index[df['holiday_Flag'] == 1]

# Make helper columns
df['post_holiday_flag']  = 0          # 1 if in 3-day window
df['day_after_holiday']  = 0          # 1, 2, 3 for relative day

for idx in holiday_idx:
    for offset in range(1, 4):        # 1, 2, 3
        target = idx + offset
        if target < len(df):
            df.loc[target, 'post_holiday_flag'] = 1
            df.loc[target, 'day_after_holiday'] = offset
