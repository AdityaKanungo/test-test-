import matplotlib.pyplot as plt
import seaborn as sns

fig, axes = plt.subplots(1, 2, figsize=(14, 5))  # 1 row, 2 columns

# Boxplot for Agents on Call
sns.boxplot(ax=axes[0], x='weather_event_day', y='Total Agents on Calls', data=df)
axes[0].set_title('Agents on Call: Weather vs Non-Weather Days')

# Boxplot for Call Volume
sns.boxplot(ax=axes[1], x='weather_event_day', y='Offered', data=df)
axes[1].set_title('Call Volume: Weather vs Non-Weather Days')

plt.tight_layout()
plt.show()