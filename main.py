Here comes a small analytical lantern to illuminate your subcategory constellations ✨—we’ll map how GPS subcategories co-occur with the index referral’s subcategory.

You’ll get:

1. A co-occurrence table (index subcategory × GPS subcategory)


2. Python code to compute it


3. sns heatmap & bar visuals to display the pattern




---

🌟 Goal

For each index referral (is_index == 'Y'):

Look at the same person’s subsequent GPS referrals

Gather their subcategory_of_abuse values

Count how often each GPS subcategory appears for each index subcategory


This yields a co-occurrence matrix like:

Index Subcat →   Child Behavior | Neglect | Trauma | ...
GPS Subcat


---

🧠 Step 1 — Prepare & filter

import pandas as pd

df_sorted = df.sort_values(['long_person_id', 'referral_id'])

# Only index referrals
index_df = df_sorted[df_sorted['is_index'] == 'Y']


---

🧪 Step 2 — Build co-occurrence pairs

For each index referral, collect GPS subcategories after that index.

cooc = []

for idx, row in index_df.iterrows():
    pid = row['long_person_id']
    idx_ref = row['referral_id']
    idx_subcat = row['subcategory_of_abuse']
    
    # all later referrals for this person
    later = df_sorted[(df_sorted['long_person_id'] == pid) &
                      (df_sorted['referral_id'] > idx_ref)]
    
    gps = later[later['referral_type'] == 'GPS']
    
    for gps_subcat in gps['subcategory_of_abuse']:
        cooc.append([idx_subcat, gps_subcat])
        
cooc_df = pd.DataFrame(cooc, columns=['index_subcat', 'gps_subcat'])


---

🧮 Step 3 — Create a co-occurrence matrix

cooc_matrix = pd.crosstab(cooc_df['index_subcat'], cooc_df['gps_subcat'])
cooc_matrix

If you want percentages row-wise:

cooc_matrix_pct = cooc_matrix.div(cooc_matrix.sum(axis=1), axis=0)


---

🎨 Step 4 — Visualize (Seaborn Heatmap)

import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(14,8))
sns.heatmap(cooc_matrix, annot=True, fmt='d', cmap='viridis')
plt.title("GPS Subcategory Co-Occurrence with Index Subcategory")
plt.xlabel("GPS Subcategory")
plt.ylabel("Index Subcategory")
plt.tight_layout()
plt.show()

Or the percentage version:

plt.figure(figsize=(14,8))
sns.heatmap(cooc_matrix_pct, annot=True, fmt='.2f', cmap='magma')
plt.title("GPS Subcategory Co-Occurrence (% of Index Subcategory)")
plt.xlabel("GPS Subcategory")
plt.ylabel("Index Subcategory")
plt.tight_layout()
plt.show()


---

📊 Optional: barplots for each index subcategory

A small flurry of bars—each index subcategory gets a barplot of GPS companion subcategories.

index_values = cooc_df['index_subcat'].unique()

for sub in index_values:
    subset = cooc_df[cooc_df['index_subcat'] == sub]
    counts = subset['gps_subcat'].value_counts()
    
    plt.figure(figsize=(10,4))
    sns.barplot(x=counts.index, y=counts.values)
    plt.xticks(rotation=45, ha='right')
    plt.title(f"GPS Subcategories Co-Occurring with Index Subcategory: {sub}")
    plt.ylabel("Count")
    plt.xlabel("GPS Subcategory")
    plt.tight_layout()
    plt.show()


---

🌈 If you'd like…

I can enhance this with:

filtering by year

demographic slices

co-occurrence networks (graph visualization)

grouping subcategories into broader themes


Just nudge me in a direction and I’ll spin up the next analytic tapestry.
