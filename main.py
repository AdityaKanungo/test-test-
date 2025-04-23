from scipy.stats import ttest_ind

results = []
for col in ['Call Volume', 'Wait Time', 'Answer Rate']:
    post  = df.loc[df['post_holiday_flag']==1, col]
    base  = df.loc[(df['holiday_Flag']==0) & (df['post_holiday_flag']==0), col]
    t, p  = ttest_ind(post, base, equal_var=False)  # Welch
    results.append((col, post.mean(), base.mean(), t, p))

print(pd.DataFrame(results, columns=[
        'Metric', 'Mean (Post-hol)', 'Mean (Normal)', 't-stat', 'p-value']))
