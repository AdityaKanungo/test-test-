import pandas as pd

# Load the CSV file (update filename if needed)
df = pd.read_csv("your_file.csv")

# Define metrics to evaluate
metrics = ['Offered', 'Avg_Wait_Time', 'Avg_Handle_Time']

# Step 1: Compute baseline values on normal (non-outage) days
normal_days = df[
    (df['Outage_Flag_Outage_ecis'] != 1) &
    (df['Outage_Flag_compass'] != 1) &
    (df['Outage_Flag_ecis down'] != 1) &
    (df['Outage_Flag_genesys'] != 1)
]
baselines = {metric: normal_days[metric].mean() for metric in metrics}

# Step 2: Identify outage types and hour columns
hour_cols = [col for col in df.columns if 'Hour_' in col and '_After_Outage_' in col]
outage_types = sorted({col.split('_After_Outage_')[1] for col in hour_cols})

# Step 3: Compute metrics increase over baseline
results = []
for outage in outage_types:
    row = {'Outage_Type': outage}
    for hour in ['Hour_1', 'Hour_2', 'Hour_3']:
        flag_col = f"{hour}_After_Outage_{outage}"
        if flag_col in df.columns:
            subset = df[df[flag_col] == 1]
            for metric in metrics:
                avg_val = subset[metric].mean()
                row[f"{hour}_{metric}_Increase"] = avg_val - baselines[metric]
        else:
            for metric in metrics:
                row[f"{hour}_{metric}_Increase"] = None
    results.append(row)

# Step 4: Create output DataFrame
summary_df = pd.DataFrame(results)
print(summary_df)