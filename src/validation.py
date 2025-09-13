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
p = Path("data/raw")
all_files = glob.glob(os.path.join(p, "*.csv"))
li = []
# %%
# Set up structured data frame with only needed data
for file in all_files:
  df = pd.read_csv(file, index_col=None,header=0)
  df['battleTime'] = df['battleTime'].apply(lambda x: datetime.strptime(x, "%Y%m%dT%H%M%S.%fZ"))
  li.append(df)

full_battle_log_df = pd.concat(li, axis=0, ignore_index=True)
battle_log_df = full_battle_log_df[['team_0_tag','battleTime','gameMode_name','gameMode_id','team_0_crowns','opponent_0_crowns','team_0_startingTrophies','team_0_trophyChange']]
battle_log_df['win'] = df['team_0_crowns'] > df['opponent_0_crowns']
# %%
print(battle_log_df)
# %%
# Identify all unique players in df
tags = battle_log_df['team_0_tag'].unique().tolist()
print(tags)
# %%
# Plot the trophy change in ladder for each player
for tag in tags:
  temp_df = battle_log_df.mask(battle_log_df['team_0_tag'] == tag).mask(battle_log_df['gameMode_name'] == 'Ladder')
  print(temp_df)
  #plt.plot(temp_df['battleTime'],temp_df['team_0_startingTrophies'])
  #plt.title(f"{tag} Ladder Trophies")
  #plt.show()
# %%
