import pandas as pd

# --- Make sure date is datetime ---
df['referral_received_date'] = pd.to_datetime(df['referral_received_date'])

# --- Split GPS and CPS referrals (referral-level, not allegation-level) ---
gps = (
    df[df['referral_type'] == 'GPS']
    [['long_person_id', 'referral_id', 'referral_received_date']]
    .drop_duplicates()
)

cps = (
    df[df['referral_type'] == 'CPS']
    [['long_person_id', 'referral_id', 'referral_received_date',
      'category_of_abuse', 'allegation_outcome']]
    # if multiple allegation rows per CPS referral, keep one row per referral
    .drop_duplicates(['long_person_id', 'referral_id'])
)

# --- Pair each GPS with CPS referrals for the same person that occur later ---
pairs = gps.merge(
    cps,
    on='long_person_id',
    suffixes=('_gps', '_cps')
)

# keep only CPS that occur AFTER the GPS referral
pairs = pairs[
    pairs['referral_received_date_cps'] > pairs['referral_received_date_gps']
]

# for each GPS referral, keep the FIRST CPS that follows it
pairs = (
    pairs
    .sort_values(['long_person_id', 'referral_id_gps', 'referral_received_date_cps'])
    .groupby(['long_person_id', 'referral_id_gps'], as_index=False)
    .first()
)

# ------------------------------------------------------------------
# 1. Overall % of GPS referrals that have at least one future CPS
# ------------------------------------------------------------------
total_gps = gps['referral_id'].nunique()
gps_with_future_cps = pairs['referral_id_gps'].nunique()

pct_gps_with_future_cps = 100 * gps_with_future_cps / total_gps
print(f"Overall % of GPS with future CPS referrals: {pct_gps_with_future_cps:.1f}%")

# ------------------------------------------------------------------
# 1a. Breakdown by CPS CATEGORY (using the first CPS after each GPS)
#     Denominator = all GPS referrals
# ------------------------------------------------------------------
by_cat = (
    pairs
    .groupby('category_of_abuse')['referral_id_gps']
    .nunique()
    .rename('num_gps_with_future_cps')
    .to_frame()
)
by_cat['pct_of_all_gps'] = 100 * by_cat['num_gps_with_future_cps'] / total_gps
print("\nBreakdown by CPS category_of_abuse:")
print(by_cat.reset_index())

# ------------------------------------------------------------------
# 1b. Breakdown by CPS OUTCOME
# ------------------------------------------------------------------
by_outcome = (
    pairs
    .groupby('allegation_outcome')['referral_id_gps']
    .nunique()
    .rename('num_gps_with_future_cps')
    .to_frame()
)
by_outcome['pct_of_all_gps'] = 100 * by_outcome['num_gps_with_future_cps'] / total_gps
print("\nBreakdown by CPS allegation_outcome:")
print(by_outcome.reset_index())

# ------------------------------------------------------------------
# 1c. (Optional) Breakdown by BOTH CPS category & outcome together
# ------------------------------------------------------------------
by_cat_outcome = (
    pairs
    .groupby(['category_of_abuse', 'allegation_outcome'])['referral_id_gps']
    .nunique()
    .rename('num_gps_with_future_cps')
    .to_frame()
)
by_cat_outcome['pct_of_all_gps'] = (
    100 * by_cat_outcome['num_gps_with_future_cps'] / total_gps
)
print("\nBreakdown by CPS category_of_abuse x allegation_outcome:")
print(by_cat_outcome.reset_index())
