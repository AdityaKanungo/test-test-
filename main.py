"""
daily_holiday_impact.py
-----------------------
Quantifies how call-centre KPIs behave in the days *after* a holiday,
using only **daily** data (no Hour column).

Columns required
    • Day                – date (YYYY-MM-DD)
    • Call Volume        – int
    • Wait Time          – float / int
    • Agents on call     – int
    • Answer Rate        – float (0-1 or %)
    • holiday_Flag       – 1 = holiday, 0 = non-holiday
    • Calls per agent    – float
"""

# ─────────────────────────────────────────────────────
# Imports & settings
# ─────────────────────────────────────────────────────
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.formula.api as smf
from pathlib import Path

plt.rcParams["figure.figsize"] = (11, 6)
sns.set_style("whitegrid")

METRICS = ["Call Volume", "Wait Time", "Answer Rate", "Calls per agent"]


# ─────────────────────────────────────────────────────
# 0  Load & clean
# ─────────────────────────────────────────────────────
def load_data(path: str | Path) -> pd.DataFrame:
    df = (pd.read_csv(path, parse_dates=["Day"])
            .sort_values("Day")
            .reset_index(drop=True))
    # Basic sanity checks
    assert {"holiday_Flag"}.issubset(df.columns), "holiday_Flag missing"
    return df


# ─────────────────────────────────────────────────────
# 1  Feature engineering
# ─────────────────────────────────────────────────────
def add_holiday_features(df: pd.DataFrame) -> pd.DataFrame:
    df["is_holiday"] = df["holiday_Flag"].astype(int)

    # Group every holiday (or non-holiday stretch) and count days since
    df["holiday_group"] = df["is_holiday"].cumsum()
    df["days_since_holiday"] = df.groupby("holiday_group").cumcount()

    # Smooth buckets
    df["post_holiday_bucket"] = pd.cut(
        df["days_since_holiday"],
        bins=[-1, 0, 1, 2, 5, np.inf],
        labels=["Holiday", "Day 1", "Day 2", "Day 3-5", "Day 6+"],
        right=True,
    )

    # Weekday factor (controls for normal weekly seasonality)
    df["weekday"] = df["Day"].dt.day_name()

    return df


# ─────────────────────────────────────────────────────
# 2  Exploratory event-study plots
# ─────────────────────────────────────────────────────
def event_study_plot(df: pd.DataFrame, metric: str) -> None:
    mean_df = (df.groupby("days_since_holiday")[metric]
                 .mean()
                 .reset_index())
    ax = sns.lineplot(data=mean_df, x="days_since_holiday",
                      y=metric, marker="o")
    ax.axhline(df[metric].mean(), ls="--", lw=1, label="Overall mean")
    ax.set_title(f"{metric} vs. Days Since Holiday")
    ax.set_xlabel("Days Since Holiday (0 = Holiday)")
    ax.legend()
    plt.show()


# ─────────────────────────────────────────────────────
# 3  Regression models
# ─────────────────────────────────────────────────────
def run_models(df: pd.DataFrame) -> dict:
    res = {}

    # OLS for Wait Time
    ols_formula = ("Q('Wait Time') ~ C(post_holiday_bucket)"
                   " + C(weekday) + Q('Agents on call')"
                   " + C(post_holiday_bucket):Q('Agents on call')")
    res["wait_time_ols"] = smf.ols(ols_formula, data=df).fit(cov_type="HC3")

    # Poisson for Call Volume (count)
    poi_formula = ("Q('Call Volume') ~ C(post_holiday_bucket)"
                   " + C(weekday) + Q('Agents on call')")
    res["call_volume_poi"] = smf.glm(
        poi_formula, data=df,
        family=smf.families.Poisson()).fit(cov_type="HC3")

    return res


def print_summaries(res_dict: dict) -> None:
    for name, model in res_dict.items():
        print("\n", "="*80, f"\n{name.upper()}\n", "="*80)
        print(model.summary())


# ─────────────────────────────────────────────────────
# 4  Driver
# ─────────────────────────────────────────────────────
def main(path: str | Path = "calls_daily.csv",
         make_plots: bool = True,
         run_reg: bool = True) -> None:

    df = load_data(path)
    df = add_holiday_features(df)

    if make_plots:
        for m in METRICS:
            event_study_plot(df, m)

    if run_reg:
        results = run_models(df)
        print_summaries(results)


if __name__ == "__main__":
    main("calls_daily.csv")
