#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import glob
import os
from datetime import datetime
#%%
# Find data path
raw = Path("data/raw")
save = Path("data/interim")
all_files = glob.glob(os.path.join(raw, "*.csv"))
li = []
# %%
# Set up structured data frame with only needed data
# Create structured data frame for each player
for file in all_files:
  df = pd.read_csv(file, index_col=None,header=0)
  
  df['battleTime'] = df['battleTime'].apply(lambda x: datetime.strptime(x, "%Y%m%dT%H%M%S.%fZ"))
  
  # decide if battle is won
  df['win'] = df['team_0_crowns'] > df['opponent_0_crowns']

  # create win/loss streaks
  groups = (df["win"] != df["win"].shift()).cumsum()

  streak_up = df.groupby(groups).cumcount() + 1
  group_sizes = df.groupby(groups)["win"].transform("size")
  streak_down = group_sizes - streak_up + 1
  # assign win/loss streaks (backward counting)
  df["win_streak"] = streak_down.where(df["win"], 0)
  df["loss_streak"] = streak_down.where(~df["win"], 0)
  li.append(df)

# Concat al individual dfs into one
full_battle_log_df = pd.concat(li, axis=0, ignore_index=True)
battle_log_df = full_battle_log_df[['team_0_tag','team_0_name','battleTime','gameMode_name','gameMode_id','win','win_streak','loss_streak','team_0_crowns','opponent_0_crowns','team_0_startingTrophies','team_0_trophyChange']]
# %%
print(battle_log_df)
battle_log_df.to_csv(f"{save}/test.csv")
# %%
# Identify all unique players in df
tags = battle_log_df['team_0_tag'].unique().tolist()
print(tags)
# %%
# Plot the trophy change in ladder for each player
for tag in tags:
  temp_df = battle_log_df.where(battle_log_df['team_0_tag'] == tag).where(battle_log_df['gameMode_name'] == 'Ladder').dropna()
  plt.plot(temp_df['battleTime'],temp_df['team_0_startingTrophies'].interpolate())
  plt.xticks(rotation=45, ha="right")
  plt.title(f"{temp_df['team_0_name'].iloc[0]} Ladder Trophies")
  plt.show()
# %%
