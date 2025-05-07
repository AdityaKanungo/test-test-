import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind

# --- Load and prepare data ---
weather_df = pd.read_csv('weather_events.csv')  # ['day', 'event_type']
calls_df = pd.read_csv('call_data.csv')         # ['day', 'agents_on_call', 'offered', 'avg_wait_time']

weather_df['day'] = pd.to_datetime(weather_df['day'])
calls_df['day'] = pd.to_datetime(calls_df['day'])

# Merge on date
df = pd.merge(calls_df, weather_df, on='day', how='left')

# Add weather indicator
df['weather_event_day'] = df['event_type'].notnull().astype(int)

# --- EDA Visualizations ---
plt.figure(figsize=(12, 4))
sns.boxplot(x='weather_event_day', y='agents_on_call', data=df)
plt.title('Agents on Call: Weather vs Non-Weather Days')
plt.show()

plt.figure(figsize=(12, 4))
sns.boxplot(x='weather_event_day', y='offered', data=df)
plt.title('Call Volume: Weather vs Non-Weather Days')
plt.show()

plt.figure(figsize=(12, 4))
sns.boxplot(x='weather_event_day', y='avg_wait_time', data=df)
plt.title('Wait Time: Weather vs Non-Weather Days')
plt.show()

# --- Statistical Testing ---
def t_test(metric):
    group1 = df[df['weather_event_day'] == 1][metric]
    group2 = df[df['weather_event_day'] == 0][metric]
    stat, pval = ttest_ind(group1, group2, equal_var=False, nan_policy='omit')
    return stat, pval

print("\nT-Test Results:")
for col in ['agents_on_call', 'offered', 'avg_wait_time']:
    stat, pval = t_test(col)
    print(f"{col}: t-stat = {stat:.2f}, p-value = {pval:.4f}")

# --- Impact by Weather Event Type ---
impact_by_event = (
    df[df['weather_event_day'] == 1]
    .groupby('event_type')[['agents_on_call', 'offered', 'avg_wait_time']]
    .mean()
    .sort_values(by='avg_wait_time', ascending=False)
)

print("\nAverage Metrics by Weather Event Type:")
print(impact_by_event)

# --- Optional: Rolling trends ---
df.set_index('day', inplace=True)
df[['agents_on_call', 'offered', 'avg_wait_time']].rolling(window=7).mean().plot(
    title='7-Day Rolling Average of Call Center Metrics', figsize=(12, 5))
plt.ylabel("Metric Value")
plt.show()