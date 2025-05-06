import pandas as pd

# Load the Excel file (update filename if needed)
df = pd.read_excel("your_file.xlsx", engine="openpyxl")

# Find all relevant columns
hour_cols = [col for col in df.columns if 'Hour_' in col and '_After_Outage_' in col]

# Extract outage types
outage_types = sorted({col.split('_After_Outage_')[1] for col in hour_cols})

# Compute means
results = []
for outage in outage_types:
    row = {'Outage_Type': outage}
    for hour in ['Hour_1', 'Hour_2', 'Hour_3']:
        col = f"{hour}_After_Outage_{outage}"
        if col in df.columns:
            row[hour] = df[df[col] == 1]['Offered'].mean()
        else:
            row[hour] = None
    results.append(row)

# Convert to DataFrame
result_df = pd.DataFrame(results)
print(result_df)