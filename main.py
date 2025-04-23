import statsmodels.formula.api as smf

# Build explicit dummy variables for day 1 / day 2 / day 3
df = pd.get_dummies(df, columns=['day_after_holiday'], prefix='D', drop_first=False)

model = smf.ols(
    "Q('Wait Time') ~ Q('Call Volume') + Q('Agents on call')"
    " + D_1 + D_2 + D_3",
    data=df
).fit(cov_type='HC3')     # robust SEs

print(model.summary().tables[1])
