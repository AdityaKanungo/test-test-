Let’s turn that time_since_index_referral column into a little time-traveler’s compass 🧭 — and compute:


---

✅ Goal

For each long_person_id, compute:

1. Time to first subsequent CPS referral

2. Time to first subsequent GPS referral

(both based on your time_since_index_referral categories: e.g., <=3 months, 3–12 months, >12 months, etc.)

3. Breakdown counts + percent

4. Suggested Seaborn visualizations (sns) to tell the story clearly.


---

🛠️ REFERRAL-LEVEL LOGIC (CRITICAL)

We must deduplicate referrals (because multiple allegation rows exist).

import pandas as pd

df = df.copy()

# Collapse to referral level
ref = df.groupby(
    ['long_person_id', 'referral_id'],
    as_index=False
).agg({
    'referral_type': 'first',
    'referral_sequence_type': 'first',
    'time_since_index_referral': 'first'
})


---

🚀 1. First Subsequent CPS Per Person

# Filter only subsequent CPS referrals
subseq_cps = ref[
    (ref['referral_sequence_type'] == 'Subsequent') &
    (ref['referral_type'] == 'CPS')
]

# For each person, take earliest CPS referral (first one chronologically)
first_cps = subseq_cps.groupby('long_person_id')['time_since_index_referral'].first()

cps_breakdown = first_cps.value_counts().sort_index()
print("Time to FIRST Subsequent CPS Referral:")
print(cps_breakdown)


---

🌟 2. First Subsequent GPS Per Person

subseq_gps = ref[
    (ref['referral_sequence_type'] == 'Subsequent') &
    (ref['referral_type'] == 'GPS')
]

first_gps = subseq_gps.groupby('long_person_id')['time_since_index_referral'].first()

gps_breakdown = first_gps.value_counts().sort_index()
print("Time to FIRST Subsequent GPS Referral:")
print(gps_breakdown)


---

🧮 3. Combine CPS + GPS into ONE Table (Optional)

combined = pd.DataFrame({
    'first_cps': first_cps,
    'first_gps': first_gps
})


---

🎨 4. Recommended Visualizations (Seaborn)

Now let’s paint this universe in colors 🌈 with seaborn.


---

📊 A. Bar Chart — Time to First CPS

import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(8,5))
sns.countplot(
    y=first_cps,
    order=first_cps.value_counts().index
)
plt.title("Time to First Subsequent CPS Referral")
plt.xlabel("Count of Children")
plt.ylabel("Time Since Index Referral")
plt.show()

A horizontal bar chart works beautifully for ordinal buckets (<=3 months, 3–12 months, >12 months).


---

📊 B. Bar Chart — Time to First GPS

plt.figure(figsize=(8,5))
sns.countplot(
    y=first_gps,
    order=first_gps.value_counts().index
)
plt.title("Time to First Subsequent GPS Referral")
plt.xlabel("Count of Children")
plt.ylabel("Time Since Index Referral")
plt.show()


---

📊 C. Side-by-Side Comparison (CPS vs GPS)

Convert counts to a tidy frame:

plot_df = pd.DataFrame({
    'CPS': cps_breakdown,
    'GPS': gps_breakdown
}).reset_index().melt(id_vars='index',
                      var_name='Referral Type',
                      value_name='Count')

plt.figure(figsize=(10,6))
sns.barplot(data=plot_df, x='Count', y='index', hue='Referral Type')
plt.title("Time to First Subsequent CPS vs GPS Referral")
plt.ylabel("Time Since Index Referral")
plt.xlabel("Number of Children")
plt.legend(title="Referral Type")
plt.show()

This is the most executive-friendly view — one axis for time buckets, two colored bars showing CPS and GPS patterns.


---

📈 D. Heatmap (optional but powerful)

This is great when you want to show distribution patterns visually.

heat = plot_df.pivot_table(index='index', columns='Referral Type', values='Count')

plt.figure(figsize=(6,4))
sns.heatmap(heat, annot=True, cmap='Blues')
plt.title("Heatmap: CPS vs GPS Time to First Referral")
plt.xlabel("")
plt.ylabel("Time Since Index")
plt.show()


---

⭐ Interpretation Ideas for Storytelling

Short time windows (≤3 months) indicate rapid re-engagement with the system → possible early warning or escalation patterns.

Longer windows (>12 months) point toward episodic or recurring issues.

Comparing CPS vs GPS tells whether concerns escalate or shift subcategory over time.


This becomes a wonderful narrative for leadership: How quickly do families reappear in the system, and through what door? 🚪✨


---

If you want, I can also compute:

Time to first CPS AFTER a GPS

Escalation curves

CPS->GPS and GPS->CPS transitions

Survival curves (Kaplan-Meier) for risk modeling


Just say the word — happy to build those too.
