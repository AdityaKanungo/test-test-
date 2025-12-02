import pandas as pd

df = df.copy()

# ------------------------------------------------------------
# Collapse to referral-level (unique referral rows)
# ------------------------------------------------------------
ref = df.groupby(
    ['long_person_id', 'referral_id'], 
    as_index=False
).agg({
    'referral_type': 'first',
    'is_index': 'first',
    'referral_sequence_type': 'first',
    'subcategory_of_abuse': 'first',
    'same_gps_subcategory_as_index': 'first'
})

# ------------------------------------------------------------
# Identify index referrals (one per long_person_id ideally)
# ------------------------------------------------------------
index_ref = ref[ref['is_index'] == 'Y'][[
    'long_person_id',
    'referral_id',
    'subcategory_of_abuse'
]].rename(columns={'subcategory_of_abuse': 'index_subcategory'})

# ------------------------------------------------------------
# Attach index subcategory to all referral-level rows
# ------------------------------------------------------------
ref = ref.merge(index_ref[['long_person_id', 'index_subcategory']],
                on='long_person_id', how='left')

# ------------------------------------------------------------
# Filter only subsequent GPS referrals at referral-level
# ------------------------------------------------------------
subseq_gps = ref[
    (ref['referral_sequence_type'] == 'Subsequent') &
    (ref['referral_type'] == 'GPS')
]

# ------------------------------------------------------------
# Percentage of index referrals that have ≥1 subsequent GPS referral
# ------------------------------------------------------------
has_subseq = subseq_gps.groupby('long_person_id').size().reindex(
    index_ref['long_person_id'], fill_value=0
)

pct_index_with_subseq_gps = (has_subseq > 0).mean() * 100
print("Percentage of INDEX referrals with ≥1 subsequent GPS referral:")
print(round(pct_index_with_subseq_gps, 2), "%")

# ------------------------------------------------------------
# Breakdown of same vs different subcategory (referral-level)
# ------------------------------------------------------------
breakdown = subseq_gps['same_gps_subcategory_as_index'].value_counts()
print("\nBreakdown of subsequent GPS referrals by subcategory match:")
print(breakdown)
