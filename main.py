Yep, the idea makes sense—you just need to restrict the whole universe first to kids whose index referral is “Child Sexually Acting Out”, then run the GPS→future CPS logic inside that cohort only.

Something like this:

import pandas as pd

# Make sure date is datetime
df['referral_received_date'] = pd.to_datetime(df['referral_received_date'])

# --------------------------------------------------------
# 0. Restrict to children whose INDEX referral is CSAO
# --------------------------------------------------------
csao_df = df[df['index_subcategory_of_abuse'] == 'Child Sexually Acting Out'].copy()

# (Optional) if you ONLY want GPS referrals that match the index subcategory:
# csao_df = csao_df[csao_df['same_gps_subcategory_as_index'] == 'Y']

# --------------------------------------------------------
# 1. Build GPS & CPS referral-level tables *within this cohort*
# --------------------------------------------------------
gps = (
    csao_df[csao_df['referral_type'] == 'GPS']
    [['long_person_id', 'referral_id', 'referral_received_date']]
    .drop_duplicates()
)

cps = (
    csao_df[csao_df['referral_type'] == 'CPS']
    [['long_person_id', 'referral_id', 'referral_received_date',
      'category_of_abuse', 'allegation_outcome']]
    .drop_duplicates(['long_person_id', 'referral_id'])
)

# --------------------------------------------------------
# 2. For each GPS, find future CPS referrals for same person
# --------------------------------------------------------
pairs = gps.merge(
    cps,
    on='long_person_id',
    suffixes=('_gps', '_cps')
)

# keep only CPS after the GPS referral
pairs = pairs[pairs['referral_received_date_cps'] > pairs['referral_received_date_gps']]

# for each GPS, keep the first CPS that follows it
pairs = (
    pairs
    .sort_values(['long_person_id', 'referral_id_gps', 'referral_received_date_cps'])
    .groupby(['long_person_id', 'referral_id_gps'], as_index=False)
    .first()
)

# --------------------------------------------------------
# 3. Percent of GPS (in CSAO index cohort) with future CPS
# --------------------------------------------------------
total_gps = gps['referral_id'].nunique()
gps_with_future_cps = pairs['referral_id_gps'].nunique()

pct_gps_with_future_cps = round(100 * gps_with_future_cps / total_gps, 2)
print(f"{pct_gps_with_future_cps}% of GPS referrals (where index referral is CSAO) "
      f"have at least one future CPS referral")

# --------------------------------------------------------
# 4. Breakdown by CPS category & outcome
# --------------------------------------------------------
by_cat = (
    pairs.groupby('category_of_abuse')['referral_id_gps']
    .nunique()
    .rename('num_gps_with_future_cps')
    .to_frame()
)
by_cat['pct_of_all_gps'] = 100 * by_cat['num_gps_with_future_cps'] / total_gps

by_outcome = (
    pairs.groupby('allegation_outcome')['referral_id_gps']
    .nunique()
    .rename('num_gps_with_future_cps')
    .to_frame()
)
by_outcome['pct_of_all_gps'] = 100 * by_outcome['num_gps_with_future_cps'] / total_gps

print("\nBreakdown by CPS category_of_abuse (within CSAO index cohort):")
print(by_cat.reset_index())

print("\nBreakdown by CPS allegation_outcome (within CSAO index cohort):")
print(by_outcome.reset_index())

So logically:

1. Filter cohort: only records where index_subcategory_of_abuse == "Child Sexually Acting Out".


2. Within that cohort, take all GPS referrals as the denominator.


3. For each GPS, see if there is any later CPS for the same long_person_id.


4. Compute the overall %, then break down by CPS category and outcome.



If your current code is doing those four things (just with slightly different variable names), then you’re on the right track.
