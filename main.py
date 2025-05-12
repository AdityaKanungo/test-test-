# Define your metrics
metrics = ['Total Agents on Calls', 'Offered', 'avg_wait_time']

# Group by weather_event_day and calculate mean and std
summary_data = df.groupby('weather_event_day')[metrics].agg(['mean', 'std']).round(2)

# Rename the index for readability
summary_data.index = ['Non-Weather', 'Weather']

# Flatten the column MultiIndex
summary_data.columns = [f'{col[0]} ({col[1]})' for col in summary_data.columns]

# Display the resulting DataFrame
print(summary_data)