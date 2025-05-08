fig, axes = plt.subplots(1, 3, figsize=(15, 4))

for i, metric in enumerate(metrics):
    values = means[metric]
    delta = values[1] - values[0]
    axes[i].bar(['Non-Weather', 'Weather'], values, color=['gray', 'orange'])
    axes[i].set_title(f'{metric}\nChange: {delta:.2f}')
    axes[i].set_ylabel(metric)

plt.suptitle('Metric Comparison: Weather vs Non-Weather Days')
plt.tight_layout()
plt.show()