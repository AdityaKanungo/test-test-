import pandas as pd

# ------------------------------------------------------------------
# 0. Ensure referral_received_date is datetime
# ------------------------------------------------------------------
df['referral_received_date'] = pd.to_datetime(df['referral_received_date'])

# ------------------------------------------------------------------
# 1. INDEX GPS referrals = any referral where is_index == "Y"
#    Dedup at referral level (one referral_id per person per date)
# ------------------------------------------------------------------
index_gps = (
    df[df['is_index'] == 'Y']
    [['long_person_id', 'referral_id', 'referral_received_date']]
    .drop_duplicates()
    .rename(columns={
        'referral_id': 'index_referral_id',
        'referral_received_date': 'index_referral_date'
    })
)

total_index_gps = index_gps['index_referral_id'].nunique()

# ------------------------------------------------------------------
# 2. CPS referrals (dedup at referral level)
# ------------------------------------------------------------------
cps = (
    df[df['referral_type'] == 'CPS']
    [['long_person_id', 'referral_id', 'referral_received_date',
      'category_of_abuse', 'allegation_outcome']]
    .drop_duplicates(['long_person_id', 'referral_id'])
    .rename(columns={
        'referral_id': 'cps_referral_id',
        'referral_received_date': 'cps_referral_date'
    })
)

# ------------------------------------------------------------------
# 3. Pair each index GPS referral with future CPS referrals
# ------------------------------------------------------------------
pairs = index_gps.merge(cps, on='long_person_id', how='left')

# Only CPS referrals strictly after the index GPS
pairs = pairs[pairs['cps_referral_date'] > pairs['index_referral_date']]

# For each index GPS, keep the earliest CPS escalation
pairs = (
    pairs
    .sort_values(['long_person_id', 'index_referral_id', 'cps_referral_date'])
    .groupby(['long_person_id', 'index_referral_id'], as_index=False)
    .first()
)

# ------------------------------------------------------------------
# 4. Overall % of index GPS with future CPS referrals
# ------------------------------------------------------------------
index_with_future_cps = pairs['index_referral_id'].nunique()

pct_index_with_future_cps = round(
    100 * index_with_future_cps / total_index_gps, 1
)

print(f"% of Child Sexually Acting Out (index) GPS with future CPS: "
      f"{pct_index_with_future_cps}%")

# ------------------------------------------------------------------
# 5a. Breakdown by CPS category_of_abuse
# ------------------------------------------------------------------
by_cat = (
    pairs
    .groupby('category_of_abuse')['index_referral_id']
    .nunique()
    .rename('num_index_gps_with_future_cps')
    .to_frame()
)

by_cat['pct_of_all_index_gps'] = (
    100 * by_cat['num_index_gps_with_future_cps'] / total_index_gps
)

print("\nBreakdown by CPS category_of_abuse:")
print(by_cat.reset_index())

# ------------------------------------------------------------------
# 5b. Breakdown by CPS allegation_outcome
# ------------------------------------------------------------------
by_outcome = (
    pairs
    .groupby('allegation_outcome')['index_referral_id']
    .nunique()
    .rename('num_index_gps_with_future_cps')
    .to_frame()
)

by_outcome['pct_of_all_index_gps'] = (
    100 * by_outcome['num_index_gps_with_future_cps'] / total_index_gps
)

print("\nBreakdown by CPS allegation_outcome:")
print(by_outcome.reset_index())

# ------------------------------------------------------------------
# 5c. Category × Outcome breakdown
# ------------------------------------------------------------------
by_cat_outcome = (
    pairs
    .groupby(['category_of_abuse', 'allegation_outcome'])['index_referral_id']
    .nunique()
    .rename('num_index_gps_with_future_cps')
    .to_frame()
)

by_cat_outcome['pct_of_all_index_gps'] = (
    100 * by_cat_outcome['num_index_gps_with_future_cps'] / total_index_gps
)

print("\nBreakdown by CPS category × allegation_outcome:")
print(by_cat_outcome.reset_index())
