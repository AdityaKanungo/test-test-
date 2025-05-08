metrics = ['Total Agents on Calls', 'Offered', 'avg_wait_time']
means = df.groupby('weather_event_day')[metrics].mean()
baseline = means.loc[0]
delta = means.loc[1] - baseline

delta.plot(kind='bar', color=['gray' if v < 0 else 'orange' for v in delta], figsize=(8, 5))
plt.axhline(0, color='black', linewidth=0.8)
plt.title('Change in Metrics on Weather Days vs Baseline')
plt.ylabel('Difference from Non-Weather Days')
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()