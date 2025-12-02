Here’s a clear path through your data forest 🌲—we’ll pluck out the number of GPS referrals that occur after the index referral but before the FIRST CPS referral, then bucket them into:

0, 1, 2, 3+, and No CPS

…and finally give you a tidy table you can graph.


---

✅ Step 1 — Define the logic

For each index referral (where is_index == 'Y'):

1. Identify its referral date (or sequence order—whatever your data uses).


2. Look forward in time at subsequent referrals for the same long_person_id.


3. Count GPS referrals that occur after index and before the first CPS referral.


4. If no CPS ever occurs → bucket = "No CPS".


5. Otherwise, bucket as:

0

1

2

3+





---

✅ Step 2 — Example Pandas code

Assuming your dataframe is named df and referral order is determined by something like referral_id or another chronological field.

df_sorted = df.sort_values(['long_person_id', 'referral_id'])

index_refs = df_sorted[df_sorted['is_index'] == 'Y']

results = []

for idx, row in index_refs.iterrows():
    pid = row['long_person_id']
    idx_referral = row['referral_id']

    # All later referrals for this person
    later = df_sorted[(df_sorted['long_person_id'] == pid) &
                      (df_sorted['referral_id'] > idx_referral)]

    # Find first CPS referral
    first_cps = later[later['referral_type'] == 'CPS']
    if len(first_cps) > 0:
        first_cps_referral_id = first_cps['referral_id'].min()

        gps_between = later[(later['referral_type'] == 'GPS') &
                            (later['referral_id'] < first_cps_referral_id)]
        gps_count = gps_between.shape[0]

        # bucketize
        if gps_count == 0: bucket = "0"
        elif gps_count == 1: bucket = "1"
        elif gps_count == 2: bucket = "2"
        else: bucket = "3+"
    else:
        bucket = "No CPS"

    results.append({
        'long_person_id': pid,
        'index_referral_id': idx_referral,
        'gps_before_cps': gps_count if bucket != "No CPS" else None,
        'bucket': bucket
    })

results_df = pd.DataFrame(results)


---

✅ Step 3 — Get counts & percentages for your bar chart

summary = results_df['bucket'].value_counts().sort_index()

summary_pct = (summary / summary.sum() * 100).round(1)

final_summary = pd.DataFrame({
    '# Index Referrals': summary,
    '% Index Referrals': summary_pct
})

print(final_summary)

This will give you a table like:

bucket	# Index Referrals	% Index Referrals

0	142	58.1%
1	55	22.5%
2	26	10.6%
3+	12	4.9%
No CPS	9	3.7%



---

📊 Step 4 — Bar chart example

import matplotlib.pyplot as plt

final_summary['# Index Referrals'].plot(kind='bar')

plt.title("GPS Referrals Between Index and First CPS")
plt.xlabel("Bucket")
plt.ylabel("# of Index Referrals")
plt.show()


---

If you'd like…

✨ I can generate the graph for you
✨ Or convert this into a function
✨ Or help you apply grouping by year, geography, demographic factors, etc.

Just tell me which direction you'd like the analytic compass to swing.
