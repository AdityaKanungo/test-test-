Crystal clear now — thank you for slowing the carousel so we can step off at the right horse 🎠.

You want the clean, simple escalation sequence:

🎯 “How many GPS referrals happened after the INDEX and before the FIRST CPS?”

Categories should be:

0 GPS before CPS

1 GPS before CPS

2 GPS before CPS

3 GPS before CPS

4+ GPS before CPS

No CPS (child never escalated)


No need for time buckets here.
Just pure counts between index → CPS.

Let’s build that neatly, correctly, and referral-level.


---

✅ STEP 1 — Collapse to referral-level

ref = df.groupby(
    ['long_person_id','referral_id'],
    as_index=False
).agg({
    'referral_type':'first',
    'referral_sequence_type':'first'
})


---

✅ STEP 2 — Identify the FIRST CPS referral

# Filter to CPS only and take earliest by referral_sequence_type ordering
first_cps = ref[ref['referral_type']=="CPS"] \
    .sort_values(['long_person_id','referral_sequence_type']) \
    .groupby('long_person_id') \
    .first()[['referral_id']]

first_cps.rename(columns={'referral_id':'first_cps_id'}, inplace=True)

If you have a better chronological field (like actual referral date), we can replace this ordering — for now we rely on referral_sequence_type or the natural sort order you provide.


---

✅ STEP 3 — Count GPS referrals AFTER index but BEFORE first CPS

We assume you already know the index referral for each long_person_id via is_index == 'Y'.

index_ref = ref[ref['referral_sequence_type']=="Index"] \
    .groupby('long_person_id') \
    .first()[['referral_id']]

index_ref.rename(columns={'referral_id':'index_id'}, inplace=True)


---

Merge everything:

merged = ref.merge(index_ref, on='long_person_id', how='left')
merged = merged.merge(first_cps, on='long_person_id', how='left')


---

Logic for counting GPS between index and first CPS

We need a sequencing variable to know what comes between what.

You have referral_sequence_type but it is categorical (Index, Subsequent).

Better approach:
Create a numeric sequence order per long_person_id.

merged = merged.sort_values(['long_person_id','referral_sequence_type'])  
merged['seq'] = merged.groupby('long_person_id').cumcount()

Now sequences look like:

seq	referral_type	meaning

0	Index	first referral
1	GPS	after index
2	GPS	after index
3	CPS	first CPS
4	GPS/CPS	after CPS


Perfect for "between index and CPS".


---

Compute counts:

def count_gps_between(group):
    idx_seq = group[group['referral_id']==group['index_id'].iloc[0]]['seq'].iloc[0]
    
    # Case 1: HAS CPS
    if pd.notna(group['first_cps_id'].iloc[0]):
        cps_seq = group[group['referral_id']==group['first_cps_id'].iloc[0]]['seq'].iloc[0]
        
        gps_between = group[
            (group['seq'] > idx_seq) &
            (group['seq'] < cps_seq) &
            (group['referral_type']=="GPS")
        ]
        return len(gps_between)
    
    # Case 2: NO CPS → count all GPS after index
    else:
        gps_after = group[
            (group['seq'] > idx_seq) &
            (group['referral_type']=="GPS")
        ]
        return f"No CPS ({len(gps_after)})"

result = merged.groupby('long_person_id').apply(count_gps_between)


---

✨ Now categorize into 1,2,3,4+, No CPS

def categorize(x):
    if isinstance(x, str):
        return "No CPS"
    if x >= 4:
        return "4+"
    return str(x)

result_cat = result.apply(categorize)
print(result_cat.value_counts())

This produces:

Category	Meaning

0	No GPS before CPS
1	1 GPS before CPS
2	2 GPS before CPS
3	3 GPS before CPS
4+	4 or more GPS before CPS
No CPS	never escalated



---

📊 Recommended Visuals (Seaborn)

These visuals will pop in a dashboard or slide deck.


---

1️⃣ Bar Chart — Distribution of GPS Counts Before CPS

sns.countplot(x=result_cat, order=["0","1","2","3","4+","No CPS"])
plt.title("GPS Referrals Between Index and First CPS")
plt.xlabel("# GPS referrals before CPS")
plt.ylabel("# Children")
plt.show()


---

2️⃣ Stacked Bar — Escalation vs No Escalation

df_vis = pd.DataFrame({'category': result_cat})
df_vis['type'] = df_vis['category'].apply(lambda x: "No CPS" if x=="No CPS" else "Has CPS")

sns.countplot(x='type', data=df_vis)
plt.title("Children With vs Without CPS Escalation")
plt.xlabel("")
plt.ylabel("# Children")
plt.show()


---

3️⃣ Optional Heatmap — GPS Count vs Subcategory

If you want to see escalation risk by abuse type.

heat = df_vis.join(df[['long_person_id','subcategory_of_abuse']].drop_duplicates()
).pivot_table(index='subcategory_of_abuse', columns='category', aggfunc='size', fill_value=0)

sns.heatmap(heat, annot=True, cmap="Blues")
plt.title("GPS Before CPS by Subcategory of Abuse")
plt.show()


---

🎁 If you want …

I can also build:

Time-based escalation curves

Transition matrices (GPS → CPS → GPS)

Family-level escalation summaries

Cohort tracking panels


Just say the word 🌙
