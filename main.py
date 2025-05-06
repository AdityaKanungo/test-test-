import pandas as pd

# Load the Excel file
df = pd.read_excel("your_file.xlsx", engine="openpyxl")

# Define metrics to calculate
metrics = ['Offered', 'Avg_Wait_Time']

# Identify all hour-related outage flag columns
hour_cols = [col for col in df.columns if 'Hour_' in col and '_After_Outage_' in col]
outage_types = sorted({col.split('_After_Outage_')[1] for col in hour_cols})

# Prepare results
results = []

for outage in outage_types:
    row = {'Outage_Type': outage}
    for hour in ['Hour_1', 'Hour_2', 'Hour_3']:
        flag_col = f"{hour}_After_Outage_{outage}"
        if flag_col in df.columns:
            filtered_df = df[df[flag_col] == 1]
            for metric in metrics:
                row[f"{hour}_{metric}"] = filtered_df[metric].mean()
        else:
            for metric in metrics:
                row[f"{hour}_{metric}"] = None
    results.append(row)

# Create summary DataFrame
summary_df = pd.DataFrame(results)
print(summary_df)