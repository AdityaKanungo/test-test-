import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# --- Simulate a daily dataset ---
np.random.seed(42)
date_range = pd.date_range(start='2022-01-01', end='2024-12-31', freq='D')
df = pd.DataFrame({
    'Date': date_range,
    'Holiday_Flag': np.random.choice([0, 1], size=len(date_range), p=[0.9, 0.1]),
    'Avg Accept Time': np.random.normal(loc=6, scale=1.5, size=len(date_range)),
    'Answer Rate': np.random.normal(loc=0.85, scale=0.05, size=len(date_range)),
    'Offered': np.random.poisson(lam=1500, size=len(date_range))
})

# Clip outliers and preprocess
df['Avg Accept Time'] = df['Avg Accept Time'].clip(2, 15)
df['Answer Rate'] = df['Answer Rate'].clip(0.5, 1.0)
df['Holiday_Flag'] = df['Holiday_Flag'].astype(int)
df['DayOfWeek'] = df['Date'].dt.dayofweek  # Monday=0, Sunday=6

# --- Remove weekends ---
df = df[df['DayOfWeek'] < 5].copy()

# --- Flag 3 days after each holiday (excluding weekends) ---
df['Post_Holiday_1'] = 0
df['Post_Holiday_2'] = 0
df['Post_Holiday_3'] = 0

holiday_dates = df[df['Holiday_Flag'] == 1]['Date']
for holiday in holiday_dates:
    post_days = df[df['Date'] > holiday].head(3).index
    if len(post_days) >= 1:
        df.loc[post_days[0], 'Post_Holiday_1'] = 1
    if len(post_days) >= 2:
        df.loc[post_days[1], 'Post_Holiday_2'] = 1
    if len(post_days) >= 3:
        df.loc[post_days[2], 'Post_Holiday_3'] = 1

# --- Year-wise visualization ---
years = [2022, 2023, 2024]
for year in years:
    yearly_df = df[df['Date'].dt.year == year]
    yearly_melted = yearly_df.melt(
        id_vars='Date',
        value_vars=['Avg Accept Time', 'Answer Rate', 'Offered'],
        var_name='Metric',
        value_name='Value'
    )
    holiday_dates_year = yearly_df[yearly_df['Holiday_Flag'] == 1]['Date']
    
    unique_metrics = yearly_melted['Metric'].unique()
    fig, axes = plt.subplots(len(unique_metrics), 1, figsize=(15, 10), sharex=True)

    for i, metric in enumerate(unique_metrics):
        ax = axes[i]
        metric_df = yearly_melted[yearly_melted['Metric'] == metric]
        sns.lineplot(data=metric_df, x='Date', y='Value', ax=ax, label=metric)

        # Mark holidays
        for h in holiday_dates_year:
            ax.axvline(x=h, color='red', linestyle='--', linewidth=0.8)

        # Highlight post-holiday points
        for day_flag in ['Post_Holiday_1', 'Post_Holiday_2', 'Post_Holiday_3']:
            post_days = yearly_df[yearly_df[day_flag] == 1]['Date']
            for pd in post_days:
                ax.axvline(x=pd, color='orange', linestyle=':', linewidth=0.6)

        ax.set_title(f"{metric} in {year} with Holidays (red) and 3 Post-Holiday Days (orange)")
        ax.set_ylabel(metric)
        ax.grid(True)

    axes[-1].xaxis.set_major_locator(mdates.MonthLocator())
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
