#%%

# Make sure you have ran validation.py before running this!

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

#%%

# Read processed csv to get battle data
p = Path("data/processed/battle_log.csv")
battle_log_df = pd.read_csv(p)

# %%

# Determine a statistical picture of trophy deltas above and below 10k

# One error that I am seeing here is that sometime when you lose and you would fall below the trophy gate if you got a regular loss in trophies, the loss delta is only as much as it takes to drop you to the minimum amount. This leads to a lot of outliers in the sub 10k loss deltas. These outliers must be removed to determine the exact theoretical distribution of the Clash Royale win and loss deltas. Do this the next time you see this.

ladder_df = battle_log_df[battle_log_df['gameMode_name'] == 'Ladder'].copy()
ladder_df['is_sub10k'] = ladder_df['team_0_startingTrophies'] < 10000

delta_stats = ladder_df.groupby(['is_sub10k', 'win'])['team_0_trophyChange'].agg(['mean','std','count'])

print("Mean trophy deltas")
for (is_sub10k, win), row in delta_stats.iterrows():
    group = "0-9999" if is_sub10k else "10000+"
    result = "Win" if win else "Loss"
    mean_val = row['mean']
    std_val = row['std']
    n = row['count']
    print(f"{group} trophies | {result:4s}: {mean_val:.2f} ± {std_val:.2f} with {n} samples")

fig, axs = plt.subplots(3, 2, figsize=(6, 9))
x = [0.3,0.7]
labels = ['Loss','Win']

sub10k = delta_stats.loc[True]
post10k = delta_stats.loc[False]

axs[0,0].errorbar(x,abs(sub10k['mean']),yerr=sub10k['std'],fmt='o')
axs[0,0].set_xticks(x)
axs[0,0].set_xlim(0, 1)
axs[0,0].set_xticklabels(labels)
axs[0,0].set_title("Sub 10k Trophies")
axs[0,0].set_ylabel("Absolute Mean Trophy Change")
axs[0,0].grid(True,linestyle="--")

axs[0,1].errorbar(x,abs(post10k['mean']),yerr=post10k['std'],fmt='o')
axs[0,1].set_xticks(x)
axs[0,1].set_xlim(0, 1)
axs[0,1].set_xticklabels(labels)
axs[0,1].set_title("10k+ Trophies")
axs[0,1].grid(True,linestyle="--")

axs[1,0].hist(ladder_df.loc[(ladder_df['is_sub10k']) & (ladder_df['win']), 'team_0_trophyChange'], bins=20)
axs[1,0].set_title("Sub 10k Win Deltas")

axs[1,1].hist(ladder_df.loc[(~ladder_df['is_sub10k']) & (ladder_df['win']), 'team_0_trophyChange'], bins=20)
axs[1,1].set_title("10k+ Win Deltas")

axs[2,0].hist(ladder_df.loc[(ladder_df['is_sub10k']) & (~ladder_df['win']), 'team_0_trophyChange'], bins=20)
axs[2,0].set_title("Sub 10k Loss Deltas")

axs[2,1].hist(ladder_df.loc[(~ladder_df['is_sub10k']) & (~ladder_df['win']), 'team_0_trophyChange'], bins=20)
axs[2,1].set_title("10k+ Loss Deltas")

plt.tight_layout()
plt.show()
# %%
