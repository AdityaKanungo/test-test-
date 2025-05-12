import pandas as pd
from scipy.stats import ttest_ind

# Ensure proper types
df['Day'] = pd.to_datetime(df['Day'])
df['Hour'] = df['Hour'].astype(int)

# Define outage columns
outage_columns = [
    'compass', 'ecis accessibility issues', 'ecis application issues',
    'ecis imaging', 'ecis processing', 'ecis server issues',
    'genesys', 'not_applicable', 'ecis connectivity issues'
]

impact_by_type = []

# Loop over each outage column
for col in outage_columns:
    # Get records during the outage
    during_outage = df[df[col] == 1]
    baseline_data = df[df[col] == 0]

    # Skip if no data during outage
    if during_outage.empty or baseline_data.empty:
        continue

    # Calculate averages
    avg_wait_outage = during_outage['Avg_Wait_Time'].mean()
    avg_calls_outage = during_outage['Offered'].mean()
    avg_wait_baseline = baseline_data['Avg_Wait_Time'].mean()
    avg_calls_baseline = baseline_data['Offered'].mean()

    # Deltas
    delta_wait = avg_wait_outage - avg_wait_baseline
    delta_calls = avg_calls_outage - avg_calls_baseline

    # T-tests
    wait_stat, wait_p = ttest_ind(during_outage['Avg_Wait_Time'], baseline_data['Avg_Wait_Time'], equal_var=False)
    call_stat, call_p = ttest_ind(during_outage['Offered'], baseline_data['Offered'], equal_var=False)

    # Count number of discrete outage events (Day + Hour)
    outage_events = during_outage[['Day', 'Hour']].drop_duplicates().shape[0]

    # Append result
    impact_by_type.append({
        'Outage_Type': col,
        'Avg_Wait_During_Outage': round(avg_wait_outage, 2),
        'Avg_Calls_During_Outage': round(avg_calls_outage, 2),
        'Baseline_Wait': round(avg_wait_baseline, 2),
        'Baseline_Calls': round(avg_calls_baseline, 2),
        'Delta_Wait_Time': round(delta_wait, 2),
        'Delta_Call_Volume': round(delta_calls, 2),
        'Num_Outage_Events': outage_events,
        'Wait_Time_Significant': 'Yes' if wait_p < 0.05 else 'No',
        'Call_Volume_Significant': 'Yes' if call_p < 0.05 else 'No'
    })

# Convert to DataFrame
impact_df = pd.DataFrame(impact_by_type)

# Composite score
impact_df['Score'] = (
    impact_df['Delta_Wait_Time'].rank(ascending=False) +
    impact_df['Delta_Call_Volume'].rank(ascending=False) +
    impact_df['Num_Outage_Events'].rank(ascending=False)
)

impact_df = impact_df.sort_values('Score', ascending=True)

# Show result
import ace_tools as tools; tools.display_dataframe_to_user(name="Ranked Outage Types by DURING Outage Performance", dataframe=impact_df)