Yep – we should collapse to referral level first, then do all the logic on that.
Below is end-to-end code that only uses these columns:

cols = [
    "long_person_id", "referral_id", "referral_type", "allegation_id",
    "is_index", "subcategory_of_abuse", "same_gps_subcategory_as_index",
    "referral_sequence_type", "time_since_index_referral"
]

df = df[cols].copy()


---

0. Go from allegation-level → referral-level

Multiple allegation rows per referral → we want one row per (person, referral).

# helper: collapse multiple allegation rows into one referral-level row
def any_Y(s):
    if (s == "Y").any():  # any Y → Y
        return "Y"
    if (s == "N").any():  # otherwise if any N → N
        return "N"
    return None           # all None / NA

referrals = (
    df
    .groupby(
        ["long_person_id", "referral_id", "referral_type",
         "referral_sequence_type", "time_since_index_referral"],
        as_index=False
    )
    .agg({
        "is_index": any_Y,                       # index if any allegation flagged Y
        "subcategory_of_abuse": lambda s: ", ".join(sorted(s.dropna().unique())),
        "same_gps_subcategory_as_index": any_Y   # any Y → Y (same as index)
    })
)

# this `referrals` df is now **referral-level** (what we want)


---

1️⃣ Time to first subsequent CPS and GPS (using time_since_index_referral)

First, make time_since_index_referral ordered so we can pick the earliest bucket:

import pandas as pd

# adjust this list to match YOUR buckets exactly & in order
time_order = ["0-3 months", "3-6 months", "6-12 months", ">12 months"]

referrals["time_since_index_referral"] = pd.Categorical(
    referrals["time_since_index_referral"],
    categories=time_order,
    ordered=True
)

subseq = referrals[referrals["referral_sequence_type"] == "Subsequent"].copy()

# first subsequent CPS/GPS per child
first_subseq = (
    subseq
    .dropna(subset=["time_since_index_referral"])
    .sort_values(["long_person_id", "referral_type", "time_since_index_referral"])
    .groupby(["long_person_id", "referral_type"], as_index=False)
    .first()[["long_person_id", "referral_type", "time_since_index_referral"]]
)

# breakdown (counts & percent) by type and time bucket
time_breakdown = (
    first_subseq
    .groupby(["referral_type", "time_since_index_referral"])["long_person_id"]
    .nunique()
    .reset_index(name="n_children")
)

time_breakdown["pct_within_type"] = (
    time_breakdown["n_children"]
    / time_breakdown.groupby("referral_type")["n_children"].transform("sum")
    * 100
)

Suggested visuals (seaborn)

import seaborn as sns
import matplotlib.pyplot as plt

# Bar chart: time to first subsequent CPS vs GPS
plt.figure(figsize=(8, 5))
sns.barplot(
    data=time_breakdown,
    x="time_since_index_referral",
    y="n_children",
    hue="referral_type"
)
plt.xlabel("Time since index referral")
plt.ylabel("Number of children")
plt.title("Time to first subsequent CPS / GPS referral")
plt.xticks(rotation=30)
plt.tight_layout()
plt.show()

You can also plot pct_within_type instead of counts if you want a percentage comparison.


---

2️⃣ Number of GPS referrals between index and first CPS

We want: 1, 2, 3, 4+ GPS, and No CPS.

2.1 First CPS after index (per child)

# first CPS subsequent to index for each child
cps_subseq = referrals[
    (referrals["referral_type"] == "CPS") &
    (referrals["referral_sequence_type"] == "Subsequent")
].copy()

first_cps = (
    cps_subseq
    .dropna(subset=["time_since_index_referral"])
    .sort_values(["long_person_id", "time_since_index_referral"])
    .groupby("long_person_id", as_index=False)
    .first()[["long_person_id", "referral_id", "time_since_index_referral"]]
)
first_cps = first_cps.rename(columns={"referral_id": "first_cps_referral_id",
                                      "time_since_index_referral": "first_cps_time"})

2.2 Count GPS subsequents before that CPS

# all subsequent GPS referrals
gps_subseq = referrals[
    (referrals["referral_type"] == "GPS") &
    (referrals["referral_sequence_type"] == "Subsequent")
].copy()

# attach first CPS bucket to each GPS record (if any) for that child
gps_with_cps = gps_subseq.merge(
    first_cps[["long_person_id", "first_cps_time"]],
    on="long_person_id",
    how="left"
)

# only keep GPS that occur before (or in same time bucket as) first CPS
gps_before_cps = gps_with_cps[
    gps_with_cps["first_cps_time"].notna() &
    (gps_with_cps["time_since_index_referral"] <= gps_with_cps["first_cps_time"])
]

# count distinct GPS referrals before first CPS per child
gps_counts = (
    gps_before_cps
    .groupby("long_person_id")["referral_id"]
    .nunique()
    .reset_index(name="n_gps_before_first_cps")
)

2.3 Create categories including “No CPS”

import numpy as np

# all children with an index referral
children_with_index = referrals[referrals["is_index"] == "Y"]["long_person_id"].unique()

# build base frame with one row per child who has an index
gps_summary = pd.DataFrame({"long_person_id": children_with_index})

# attach counts of GPS before first CPS (NaN => 0)
gps_summary = gps_summary.merge(gps_counts, on="long_person_id", how="left")
gps_summary["n_gps_before_first_cps"] = gps_summary["n_gps_before_first_cps"].fillna(0).astype(int)

# flag whether child ever had a post-index CPS
gps_summary = gps_summary.merge(
    first_cps[["long_person_id"]],
    on="long_person_id",
    how="left",
    indicator="has_cps_ind"
)
gps_summary["has_cps"] = gps_summary["has_cps_ind"].eq("both")

def band(row):
    if not row["has_cps"]:
        return "No CPS"
    n = row["n_gps_before_first_cps"]
    if n == 0:
        return "0 GPS"
    elif n == 1:
        return "1 GPS"
    elif n == 2:
        return "2 GPS"
    elif n == 3:
        return "3 GPS"
    else:
        return "4+ GPS"

gps_summary["gps_band"] = gps_summary.apply(band, axis=1)

band_order = ["0 GPS", "1 GPS", "2 GPS", "3 GPS", "4+ GPS", "No CPS"]

gps_band_counts = (
    gps_summary
    .groupby("gps_band")["long_person_id"]
    .nunique()
    .reindex(band_order)
    .reset_index(name="n_children")
)

gps_band_counts["pct_children"] = (
    gps_band_counts["n_children"] /
    gps_band_counts["n_children"].sum() * 100
)

Suggested visual

plt.figure(figsize=(7, 5))
sns.barplot(
    data=gps_band_counts,
    x="gps_band",
    y="n_children",
    order=band_order
)
plt.xlabel("Number of GPS referrals before first CPS")
plt.ylabel("Number of children")
plt.title("GPS referrals between index and first CPS")
plt.tight_layout()
plt.show()

You can switch y="pct_children" for a percentage plot.


---

If you paste this in and still see a “single positional indexer out of bounds” error anywhere, send me that exact traceback + the few lines around it and I’ll debug the specific spot.
