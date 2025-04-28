import pandas as pd

# Sample structure of your dataframe
# df = pd.read_csv('your_data.csv')

# Step 1: Filter only days after holidays
day1_df = df[df['day1_after_holiday'] == 1]
day2_df = df[df['day2_after_holiday'] == 1]
day3_df = df[df['day3_after_holiday'] == 1]

# Step 2: Group by holiday_name and take average call volume
day1_avg = day1_df.groupby('holiday_name')['call_volume'].mean().reset_index()
day1_avg.rename(columns={'call_volume': 'day1_avg_call_volume'}, inplace=True)

day2_avg = day2_df.groupby('holiday_name')['call_volume'].mean().reset_index()
day2_avg.rename(columns={'call_volume': 'day2_avg_call_volume'}, inplace=True)

day3_avg = day3_df.groupby('holiday_name')['call_volume'].mean().reset_index()
day3_avg.rename(columns={'call_volume': 'day3_avg_call_volume'}, inplace=True)

# Step 3: Merge all into a single table
holiday_impact = day1_avg.merge(day2_avg, on='holiday_name', how='outer')\
                         .merge(day3_avg, on='holiday_name', how='outer')

# Step 4: Sort by highest Day 1 impact
holiday_impact = holiday_impact.sort_values(by='day1_avg_call_volume', ascending=False)

# Display
print(holiday_impact)


# Filter "normal" days (not holiday or after holiday)
normal_days = df[(df['holiday_flag'] == 0) & 
                 (df['day1_after_holiday'] == 0) &
                 (df['day2_after_holiday'] == 0) &
                 (df['day3_after_holiday'] == 0)]

baseline_call_volume = normal_days['call_volume'].mean()

# Add comparison columns
holiday_impact['day1_increase_vs_baseline'] = holiday_impact['day1_avg_call_volume'] - baseline_call_volume
holiday_impact['day2_increase_vs_baseline'] = holiday_impact['day2_avg_call_volume'] - baseline_call_volume
holiday_impact['day3_increase_vs_baseline'] = holiday_impact['day3_avg_call_volume'] - baseline_call_volume