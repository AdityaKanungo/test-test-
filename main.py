import seaborn as sns
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
sns.set_style("whitegrid")

for i, metric in enumerate(metrics):
    # Prepare a small DataFrame for sns.barplot
    plot_df = df[['weather_event_day', metric]].copy()
    plot_df['weather_event_day'] = plot_df['weather_event_day'].map({0: 'Non-Weather', 1: 'Weather'})

    sns.barplot(x='weather_event_day', y=metric, data=plot_df, ax=axes[i], palette=['gray', 'orange'], ci='sd')
    
    # Calculate and show delta
    delta = means[metric][1] - means[metric][0]
    axes[i].set_title(f'{metric}\nChange: {delta:.2f}')
    axes[i].set_ylabel(metric)
    axes[i].set_xlabel('')

plt.suptitle('Metric Comparison (Mean ± SD): Weather vs Non-Weather Days', fontsize=14)
plt.tight_layout()
plt.show()