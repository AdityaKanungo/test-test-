# Assuming df is your main DataFrame
# Step 1: Classify each day
df['post_holiday_day_type'] = 'Normal'
df.loc[df['D_1'] == 1, 'post_holiday_day_type'] = 'Day 1 After Holiday'
df.loc[df['D_2'] == 1, 'post_holiday_day_type'] = 'Day 2 After Holiday'
df.loc[df['D_3'] == 1, 'post_holiday_day_type'] = 'Day 3 After Holiday'

# Step 2: Group and calculate average Offered Volume
volume_summary = df.groupby('post_holiday_day_type')['Offered'].agg(['mean', 'count']).reset_index()

# Step 3: Calculate % increase compared to normal days
normal_avg = volume_summary.loc[volume_summary['post_holiday_day_type'] == 'Normal', 'mean'].values[0]
volume_summary['percent_increase_vs_normal'] = (volume_summary['mean'] - normal_avg) / normal_avg * 100

import ace_tools as tools; tools.display_dataframe_to_user(name="Volume Summary", dataframe=volume_summary)

volume_summary



import matplotlib.pyplot as plt

plt.figure(figsize=(8,5))
plt.bar(volume_summary['post_holiday_day_type'], volume_summary['mean'], color='skyblue')
plt.ylabel('Average Call Volume (Offered)')
plt.title('Average Call Volume After Holidays')
plt.xticks(rotation=15)
for i, v in enumerate(volume_summary['mean']):
    plt.text(i, v + 50, f"{v:.0f}", ha='center', va='bottom', fontweight='bold')
plt.show()


# Create interaction terms
df['Monday_D1'] = df['Monday'] * df['D_1']
df['Tuesday_D1'] = df['Tuesday'] * df['D_1']
df['Wednesday_D1'] = df['Wednesday'] * df['D_1']
df['Thursday_D1'] = df['Thursday'] * df['D_1']
df['Friday_D1'] = df['Friday'] * df['D_1']

# Run interaction model
import statsmodels.formula.api as smf

interaction_model = smf.ols(
    formula="""Q("Offered") ~ Monday + Tuesday + Wednesday + Thursday + Friday
               + D_1 + D_2 + D_3
               + Monday_D1 + Tuesday_D1 + Wednesday_D1 + Thursday_D1 + Friday_D1
            """,
    data=df
).fit()

print(interaction_model.summary())