import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind
import statsmodels.formula.api as smf

# -----------------------------
# 1. Simulated Daily Dataset
# -----------------------------
np.random.seed(42)
date_range = pd.date_range(start='2022-01-01', end='2024-12-31', freq='D')
df = pd.DataFrame({
    'Date': date_range,
    'Holiday_Flag': np.random.choice([0, 1], size=len(date_range), p=[0.9, 0.1]),
    'Avg Accept Time': np.random.normal(loc=6, scale=1.5, size=len(date_range)),
    'Answer Rate': np.random.normal(loc=0.85, scale=0.05, size=len(date_range)),
    'Offered': np.random.poisson(lam=1500, size=len(date_range))
})

# Clean and clip data
df['Avg Accept Time'] = df['Avg Accept Time'].clip(lower=2, upper=15)
df['Answer Rate'] = df['Answer Rate'].clip(lower=0.5, upper=1.0)
df['Holiday_Flag'] = df['Holiday_Flag'].astype(int)
df['DayOfWeek'] = df['Date'].dt.day_name()
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month_name()

# -----------------------------
# 2. Line Charts: Compare Holiday vs Non-Holiday
# -----------------------------
df_grouped = df.groupby(['Date', 'Holiday_Flag']).agg({
    'Avg Accept Time': 'mean',
    'Answer Rate': 'mean',
    'Offered': 'mean'
}).reset_index()

# Line Chart: Avg Accept Time
plt.figure(figsize=(12, 5))
sns.lineplot(data=df_grouped, x='Date', y='Avg Accept Time', hue='Holiday_Flag')
plt.title("Avg Accept Time Over Time (Holiday vs Non-Holiday)")
plt.xlabel("Date")
plt.ylabel("Avg Accept Time (min)")
plt.legend(title='Holiday', labels=['Non-Holiday', 'Holiday'])
plt.tight_layout()
plt.show()

# Line Chart: Answer Rate
plt.figure(figsize=(12, 5))
sns.lineplot(data=df_grouped, x='Date', y='Answer Rate', hue='Holiday_Flag')
plt.title("Answer Rate Over Time (Holiday vs Non-Holiday)")
plt.xlabel("Date")
plt.ylabel("Answer Rate")
plt.legend(title='Holiday', labels=['Non-Holiday', 'Holiday'])
plt.tight_layout()
plt.show()

# Line Chart: Offered
plt.figure(figsize=(12, 5))
sns.lineplot(data=df_grouped, x='Date', y='Offered', hue='Holiday_Flag')
plt.title("Call Volume (Offered) Over Time (Holiday vs Non-Holiday)")
plt.xlabel("Date")
plt.ylabel("Offered Calls")
plt.legend(title='Holiday', labels=['Non-Holiday', 'Holiday'])
plt.tight_layout()
plt.show()

# Line Chart: Avg Accept Time by Day of Week
plt.figure(figsize=(10, 5))
sns.lineplot(data=df.groupby(['DayOfWeek', 'Holiday_Flag'])['Avg Accept Time'].mean().reset_index(),
             x='DayOfWeek', y='Avg Accept Time', hue='Holiday_Flag', marker='o')
plt.title("Avg Accept Time by Day of Week")
plt.ylabel("Avg Accept Time (min)")
plt.xlabel("Day of Week")
plt.xticks(rotation=45)
plt.legend(title="Holiday", labels=['Non-Holiday', 'Holiday'])
plt.tight_layout()
plt.show()

# Line Chart: Answer Rate by Day of Week
plt.figure(figsize=(10, 5))
sns.lineplot(data=df.groupby(['DayOfWeek', 'Holiday_Flag'])['Answer Rate'].mean().reset_index(),
             x='DayOfWeek', y='Answer Rate', hue='Holiday_Flag', marker='o')
plt.title("Answer Rate by Day of Week")
plt.ylabel("Answer Rate")
plt.xlabel("Day of Week")
plt.xticks(rotation=45)
plt.legend(title="Holiday", labels=['Non-Holiday', 'Holiday'])
plt.tight_layout()
plt.show()

# -----------------------------
# 3. T-Tests: Holiday vs Non-Holiday
# -----------------------------
metrics = ['Avg Accept Time', 'Answer Rate', 'Offered']
t_test_results = []

for metric in metrics:
    group1 = df[df['Holiday_Flag'] == 1][metric]
    group0 = df[df['Holiday_Flag'] == 0][metric]
    t_stat, p_val = ttest_ind(group1, group0, nan_policy='omit')
    t_test_results.append({
        'Metric': metric,
        'T-Statistic': round(t_stat, 4),
        'P-Value': round(p_val, 4),
        'Significant (p < 0.05)': p_val < 0.05
    })

t_test_df = pd.DataFrame(t_test_results)
print("\nT-Test Results:")
print(t_test_df)

# -----------------------------
# 4. OLS Regression
# -----------------------------
print("\nOLS Regression: Avg Accept Time ~ Holiday + DayOfWeek")
model1 = smf.ols('Q("Avg Accept Time") ~ Holiday_Flag + C(DayOfWeek)', data=df).fit()
print(model1.summary())

print("\nOLS Regression: Answer Rate ~ Holiday + DayOfWeek")
model2 = smf.ols('Q("Answer Rate") ~ Holiday_Flag + C(DayOfWeek)', data=df).fit()
print(model2.summary())

print("\nOLS Regression: Offered ~ Holiday + DayOfWeek")
model3 = smf.ols('Offered ~ Holiday_Flag + C(DayOfWeek)', data=df).fit()
print(model3.summary())

