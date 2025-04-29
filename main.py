import pandas as pd
from scipy.stats import ttest_ind

# Define your outage columns (update this list as per your dataset)
outage_columns = [
    'compass', 'ecis accessibility issues', 'ecis application issues',
    'ecis imaging', 'ecis processing', 'ecis server issues',
    'genesys', 'not_applicable', 'ecis connectivity issues'
]

# Initialize list to store results
impact_by_type = []

# Loop through each outage type
for col in outage_columns:
    group_on = df[df[col] == 1]
    group_off = df[df[col] == 0]

    if group_on.empty:
        continue  # Skip if no outage of this type

    # Average Metrics
    avg_wait_on = group_on['Avg_Wait_Time'].mean()
    avg_wait_off = group_off['Avg_Wait_Time'].mean()
    delta_wait = avg_wait_on - avg_wait_off

    avg_calls_on = group_on['Offered'].mean()
    avg_calls_off = group_off['Offered'].mean()
    delta_calls = avg_calls_on - avg_calls_off

    # T-tests for significance
    wait_stat, wait_p = ttest_ind(group_on['Avg_Wait_Time'], group_off['Avg_Wait_Time'], equal_var=False)
    call_stat, call_p = ttest_ind(group_on['Offered'], group_off['Offered'], equal_var=False)

    # Number of outage events (approximated using Day + Hour combo)
    num_outage_events = group_on[['Day', 'Hour']].drop_duplicates().shape[0]

    # Save results
    impact_by_type.append({
        'Outage_Type': col,
        'Delta_Wait_Time': round(delta_wait, 2),
        'Delta_Call_Volume': round(delta_calls, 2),
        'Avg_Wait_During': round(avg_wait_on, 2),
        'Avg_Calls_During': round(avg_calls_on, 2),
        'Num_Hours': len(group_on),
        'Num_Outage_Events': num_outage_events,
        'Wait_Time_Significant': 'Yes' if wait_p < 0.05 else 'No',
        'Call_Volume_Significant': 'Yes' if call_p < 0.05 else 'No'
    })

# Create DataFrame
impact_df = pd.DataFrame(impact_by_type)

# Calculate Composite Score (lower is worse)
impact_df['Score'] = (
    impact_df['Delta_Wait_Time'].rank(ascending=False) +
    impact_df['Delta_Call_Volume'].rank(ascending=False) +
    impact_df['Num_Hours'].rank(ascending=False) +
    impact_df['Num_Outage_Events'].rank(ascending=False)
)

# Sort by Score
impact_df = impact_df.sort_values('Score', ascending=True)

# Display the final result
import ace_tools as tools; tools.display_dataframe_to_user(name="Ranked Outage Types by Full Impact Analysis", dataframe=impact_df)