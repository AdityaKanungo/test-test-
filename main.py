# Calculate means
metrics = ['Total Agents on Calls', 'Offered', 'avg_wait_time']
means = df.groupby('weather_event_day')[metrics].mean()
baseline = means.loc[0]
delta_pct = ((means.loc[1] - baseline) / baseline) * 100

# Plot
delta_pct.plot(kind='bar', color=['gray' if v < 0 else 'orange' for v in delta_pct], figsize=(8, 5))
plt.axhline(0, color='black', linewidth=0.8)
plt.title('Percentage Change on Weather Days vs Non-Weather Days')
plt.ylabel('% Change from Baseline')
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()