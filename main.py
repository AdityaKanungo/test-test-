import pandas as pd

df = df.copy()

# ------------------------------------------------------------
# STEP 1 — Identify all index referrals
# ------------------------------------------------------------
index_rows = df[df['is_index'] == 'Y'][[
    'long_person_id', 
    'subcategory_of_abuse'
]].rename(columns={'subcategory_of_abuse': 'index_subcategory'})

# Attach index subcategory to all rows
df = df.merge(index_rows, on='long_person_id', how='left')

# ------------------------------------------------------------
# STEP 2 — Filter subsequent GPS referrals
# ------------------------------------------------------------
subseq_gps = df[
    (df['referral_sequence_type'] == 'Subsequent') &
    (df['referral_type'] == 'GPS')
]

# ------------------------------------------------------------
# STEP 3 — Flag whether each index referral has ANY subsequent GPS referral
# ------------------------------------------------------------
has_subseq_gps = subseq_gps.groupby('long_person_id').size().reindex(
    index_rows['long_person_id'],
    fill_value=0
)

# Percentage of index referrals with ≥1 subsequent GPS referral
pct_index_with_subseq_gps = (has_subseq_gps > 0).mean() * 100

print("Percentage of INDEX referrals with subsequent GPS referrals:")
print(round(pct_index_with_subseq_gps, 2), "%")

# ------------------------------------------------------------
# STEP 4 — Breakdown: same vs different subcategory
# ------------------------------------------------------------
breakdown = subseq_gps.groupby('same_gps_subcategory_as_index').size()

print("\nBreakdown of subsequent GPS referrals:")
print(breakdown)
