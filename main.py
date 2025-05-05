import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency

# 1. Load your dataset (update path and flag column names as needed)
df = pd.read_csv('your_data.csv', parse_dates=['Date'])

# 2. Create a proper datetime index if hour is a separate column
df['datetime'] = df['Date'] + pd.to_timedelta(df['hour'], unit='h')
df = df.set_index('datetime')

# 3. Ensure outage flags are numeric 0/1
df['A'] = df['outage flag A'].astype(int)
df['B'] = df['outage flag B'].astype(int)
df['C'] = df['outage flag C'].astype(int)

# 4. Frequency counts of each outage
freq = df[['A', 'B', 'C']].sum().rename('count')

# 5. Joint occurrence counts
joint = {
    'A&B': int(((df['A'] == 1) & (df['B'] == 1)).sum()),
    'A&C': int(((df['A'] == 1) & (df['C'] == 1)).sum()),
    'B&C': int(((df['B'] == 1) & (df['C'] == 1)).sum()),
}

# 6. Conditional probabilities P(B|A) and P(C|A)
p_b_given_a = joint['A&B'] / freq['A'] if freq['A'] > 0 else np.nan
p_c_given_a = joint['A&C'] / freq['A'] if freq['A'] > 0 else np.nan

# 7. Correlation matrix of the binary flags
corr = df[['A', 'B', 'C']].corr()

# 8. Chi-squared tests for independence between each pair
chi2_results = {}
for x, y in [('A', 'B'), ('A', 'C'), ('B', 'C')]:
    ct = pd.crosstab(df[x], df[y])
    chi2, p, _, _ = chi2_contingency(ct)
    chi2_results[f'{x} vs {y}'] = {'chi2': chi2, 'p-value': p}

# 9. Print out all results
print("Frequency counts:\n", freq)
print("\nJoint occurrences:\n", joint)
print(f"\nP(B|A) = {p_b_given_a:.2f}, P(C|A) = {p_c_given_a:.2f}")
print("\nCorrelation matrix:\n", corr)
print("\nChi-squared test results:\n", chi2_results)

# 10. Plot a heatmap of the correlations
fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(corr, vmin=-1, vmax=1)
ax.set_xticks(range(len(corr.columns)))
ax.set_yticks(range(len(corr.index)))
ax.set_xticklabels(corr.columns)
ax.set_yticklabels(corr.index)
plt.colorbar(im, ax=ax)
plt.title('Outage Flag Correlation Heatmap')
plt.tight_layout()
plt.show()