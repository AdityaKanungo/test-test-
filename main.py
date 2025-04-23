import matplotlib.pyplot as plt

# Add calendar week & weekday labels for plotting convenience
df['Week']     = df['Day'].dt.isocalendar().week
df['Weekday']  = df['Day'].dt.day_name()

metrics = {
    'Call Volume': 'Offered',
    'Wait Time'  : 'Avg Wait',
    'Answer Rate': 'Answer Rate'
}

for col, title in metrics.items():
    plt.figure(figsize=(10,4))
    for label, g in df.groupby('post_holiday_flag'):
        # 0 = “normal”, 1 = “post-holiday”
        avg = g.groupby('Weekday')[col].mean().reindex(
              ['Monday','Tuesday','Wednesday','Thursday','Friday'])
        style = '-' if label == 0 else '--'
        plt.plot(avg.values, style, marker='o',
                 label='Post-holiday' if label else 'Normal')
    plt.title(f'{title}: Normal vs Post-holiday')
    plt.ylabel(col)
    plt.xticks(range(5), ['Mon','Tue','Wed','Thu','Fri'])
    plt.legend()
    plt.tight_layout()
    plt.show()
