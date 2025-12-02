Ah—now we shift the lens.
Instead of subsequent GPS referrals, you want co-occurring allegations within the SAME referral as the index referral.

In other words:

> For every referral where is_index == 'Y' and the index subcategory is Child Sexually Acting Out,
look at all the other allegations attached to that same referral_id.
Count which other subcategories appear alongside it across the entire dataset.



This matches the style of the graphic you shared.
(Think of the index subcategory as the main note, and we’re listening for harmonies 🎶.)


---

✅ Step 1 — Filter to index referrals with target subcategory

TARGET = "Child Sexually Acting Out"

index_refs = df[
    (df['is_index'] == 'Y') &
    (df['subcategory_of_abuse'] == TARGET)
][['long_person_id', 'referral_id']]


---

✅ Step 2 — Get all allegations linked to those same referrals

We join back to the full dataframe but exclude the target subcategory.

# Referrals of interest
ref_ids = index_refs['referral_id'].unique()

# All allegations on these referrals
cooc = df[df['referral_id'].isin(ref_ids)]

# Remove the target subcategory
cooc = cooc[cooc['subcategory_of_abuse'] != TARGET]


---

✅ Step 3 — Count co-occurring subcategories

cooc_counts = cooc['subcategory_of_abuse'].value_counts()

print(cooc_counts)

If you want percentages relative to all index referrals in this category:

total_index_referrals = len(index_refs)
cooc_pct = (cooc_counts / total_index_referrals * 100).round(1)

print(cooc_pct)


---

📊 Step 4 — Create a seaborn bar chart (horizontal, like your example)

import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(10,6))
sns.barplot(x=cooc_pct.values, y=cooc_pct.index)

plt.xlabel("Percent of Index Referrals (Child Sexually Acting Out)")
plt.ylabel("Co-occurring Allegation Subcategory")
plt.title("Most Likely Co-Occurring Subcategories\n(Index = Child Sexually Acting Out)")

plt.xlim(0, cooc_pct.max() * 1.15)
plt.tight_layout()
plt.show()


---

🎯 What this yields

You’ll get a ranked table like:

Inappropriate Discipline                       14.2%
Behavioral Health Concerns – Child             12.7%
Domestic Violence                                9.8%
Substance Use by Parent/Caregiver               8.1%
Conduct by Parent/Caregiver that Places Child…  7.4%
...

Which matches the structure of the chart in your screenshot.
Each percentage means:

> “Among all index referrals where the subcategory = Child Sexually Acting Out,
what proportion also had allegation X on the same referral?”




---

Want me to wrap this into a reusable function?

I can deliver a clean get_cooccurring_subcategories(df, target_subcat) utility that returns counts, percentages, plots, etc.
