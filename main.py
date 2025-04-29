import pandas as pd
from scipy.stats import ttest_ind

# Make sure 'Day' is a datetime and 'Hour' is an integer
df['Day'] = pd.to_datetime(df['Day'])
df['Hour'] = df['Hour'].astype(int)

# Define your outage columns
outage_columns = [
    'compass', 'ecis accessibility issues', 'ecis application issues',
    'ecis imaging', 'ecis processing', 'ecis server issues',
    'genesys', 'not_applicable', 'ecis connectivity issues'
]

impact_by_type = []

# Loop over each outage type
for col in outage_columns:
    # Identify outage starts
    outage_starts = df[df[col] == 1][['Day', 'Hour']]

    next_3_hours_data = pd.DataFrame()

    # For each outage event, get next 3 hours
    for idx, row in outage_starts.iterrows():
        day = row['Day']
        hour = row['Hour']

        # Pull next 3 hours data
        three_hours = df[
            ((df['Day'] == day) & (df['Hour'].between(hour+1, hour+3)))
        ]
        next_3_hours_data = pd.concat([next_3_hours_data, three_hours], ignore_index=True)

    # If no post-outage data found, skip
    if next_3_hours_data.empty:
        continue

    # Metrics after outage
    avg_wait_after = next_3_hours_data['Avg_Wait_Time'].mean()
    avg_calls_after = next_3_hours_data['Offered'].mean()

    # Metrics for normal hours (baseline)
    baseline_data = df[~df.index.isin(next_3_hours_data.index)]
    baseline_wait = baseline_data['Avg_Wait_Time'].mean()
    baseline_calls = baseline_data['Offered'].mean()

    # Delta Metrics
    delta_wait = avg_wait_after - baseline_wait
    delta_calls = avg_calls_after - baseline_calls

    # Significance Tests
    wait_stat, wait_p = ttest_ind(next_3_hours_data['Avg_Wait_Time'], baseline_data['Avg_Wait_Time'], equal_var=False)
    call_stat, call_p = ttest_ind(next_3_hours_data['Offered'], baseline_data['Offered'], equal_var=False)

    # Save results
    impact_by_type.append({
        'Outage_Type': col,
        'Avg_Wait_Next3Hours': round(avg_wait_after, 2),
        'Avg_Calls_Next3Hours': round(avg_calls_after, 2),
        'Baseline_Wait': round(baseline_wait, 2),
        'Baseline_Calls': round(baseline_calls, 2),
        'Delta_Wait_Time': round(delta_wait, 2),
        'Delta_Call_Volume': round(delta_calls, 2),
        'Num_Outage_Events': len(outage_starts),
        'Wait_Time_Significant': 'Yes' if wait_p < 0.05 else 'No',
        'Call_Volume_Significant': 'Yes' if call_p < 0.05 else 'No'
    })

# Create DataFrame
impact_df = pd.DataFrame(impact_by_type)

# Composite Score (lower is worse)
impact_df['Score'] = (
    impact_df['Delta_Wait_Time'].rank(ascending=False) +
    impact_df['Delta_Call_Volume'].rank(ascending=False) +
    impact_df['Num_Outage_Events'].rank(ascending=False)
)

impact_df = impact_df.sort_values('Score', ascending=True)

import ace_tools as tools; tools.display_dataframe_to_user(name="Corrected Ranked Outage Types by Next 3 Hours Performance", dataframe=impact_df)