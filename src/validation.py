#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import glob
import os
from datetime import datetime
#%%
# Define the data paths and collect all raw data CSVs
raw = Path("data/raw")
save = Path("data/processed")
all_files = glob.glob(os.path.join(raw, "*.csv"))
li = []
# %%
# Loop through each CSV file to process battle logs
for file in all_files:
    df = pd.read_csv(file, index_col=None, header=0)
    
    # Convert battleTime from string to datetime object
    df['battleTime'] = df['battleTime'].apply(lambda x: datetime.strptime(x, "%Y%m%dT%H%M%S.%fZ"))
    
    # Determine if the player won the battle
    df['win'] = df['team_0_crowns'] > df['opponent_0_crowns']
    
    # Create columns for win and loss streaks from the bottom of the set
    groups = (df["win"] != df["win"].shift()).cumsum()
    streak_up = df.groupby(groups).cumcount() + 1
    group_sizes = df.groupby(groups)["win"].transform("size")
    streak_down = group_sizes - streak_up + 1
    
    df["win_streak"] = streak_down.where(df["win"], 0)
    df["loss_streak"] = streak_down.where(~df["win"], 0)
    
    # Add the processed dataframe to the list
    li.append(df)

# Concatenate all individual player dataframes into a single dataframe
full_battle_log_df = pd.concat(li, axis=0, ignore_index=True)

#%%
# Keep only the relevant columns for further analysis
battle_log_df = full_battle_log_df[['team_0_tag','team_0_name','battleTime','gameMode_name','gameMode_id','win','win_streak','loss_streak','team_0_crowns','opponent_0_crowns','team_0_startingTrophies','team_0_trophyChange']]

# Save the processed dataframe to CSV for later use
save.parent.mkdir(parents=True, exist_ok=True)
battle_log_df.to_csv(f"{save}/battle_logs.csv")
# %%
# Identify all unique player tags in the dataframe
tags = battle_log_df['team_0_tag'].unique().tolist()

# Plot trophy progression over time on the ladder for each player
for tag in tags:
    temp_df = battle_log_df.where(battle_log_df['team_0_tag'] == tag).where(battle_log_df['gameMode_name'] == 'Ladder').dropna()
    plt.plot(temp_df['battleTime'], temp_df['team_0_startingTrophies'].interpolate())
    
    plt.xticks(rotation=45, ha="right")
    plt.title(f"{temp_df['team_0_name'].iloc[0]} Ladder Trophies")
    plt.show()
# %%
