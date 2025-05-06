import pandas as pd

# Step 1: Load the Excel file
df = pd.read_excel("your_file.xlsx", engine="openpyxl")

# Step 2: Define metrics to analyze
metrics = ['Offered', 'Avg_Wait_Time', 'Avg_Handle_Time']

# Step 3: Compute baseline values on non-outage days
normal_days = df[
    (df['Outage_Flag_Outage_ecis'] != 1) &
    (df['Outage_Flag_compass'] != 1) &
    (df['Outage_Flag_ecis down'] != 1) &
    (df['Outage_Flag_genesys'] != 1)
]
baselines = {metric: normal_days[metric].mean() for metric in metrics}

# Step 4: Identify outage types
hour_cols = [col for col in df.columns if 'Hour_' in col and '_After_Outage_' in col]
outage_types = sorted({col.split('_After_Outage_')[1] for col in hour_cols})

# Step 5: Prepare results in pivoted structure
reshaped_results = []

for outage in outage_types:
    for hour in ['Hour_1', 'Hour_2', 'Hour_3']:
        flag_col = f"{hour}_After_Outage_{outage}"
        if flag_col in df.columns:
            filtered = df[df[flag_col] == 1]
            row = {
                "Outage Type": outage.upper(),
                "Hour": hour.replace("_", " ")
            }
            for metric in metrics:
                avg_val = filtered[metric].mean()
                row[f"{metric} Avg"] = avg_val
                row[f"{metric} Increase"] = avg_val - baselines[metric]
            reshaped_results.append(row)

# Step 6: Create final DataFrame
final_df = pd.DataFrame(reshaped_results)

# Optional: Format column order
cols = ['Outage Type', 'Hour'] + \
       [f"{m} Increase" for m in metrics] + \
       [f"{m} Avg" for m in metrics]
final_df = final_df[cols]

# View the result
print(final_df)