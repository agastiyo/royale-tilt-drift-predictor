#%%

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import glob
import os
from datetime import datetime

# %%

# Define functions
def parse_battle_time(x):
    if isinstance(x, datetime):  # already parsed
        return x
    try:
        # try the strict expected format
        return datetime.strptime(x, "%Y%m%dT%H%M%S.%fZ")
    except Exception:
        # fallback to pandas parser
        return pd.to_datetime(x, errors='coerce', utc=True)

#%%

# Define the data paths and collect all raw data CSVs
# Make sure to create these directories if you dont already have them
raw = Path("data/raw")
save = Path("data/processed")
all_files = glob.glob(os.path.join(raw, "*.csv"))
li1 = []
li2 = []

# %%

# Combine all files into one df
for file in all_files:
    df = pd.read_csv(file, index_col=None, header=0)
    # Convert battleTime from string to datetime object
    df['battleTime'] = df['battleTime'].apply(parse_battle_time)
    li1.append(df)


full_battle_log_df = pd.concat(li1, axis=0, ignore_index=True).drop_duplicates().sort_values('battleTime') # Drop duplicates and sort rows by timestamp here to avoid issues with calculating streaks later on

#%%

# Keep only relevant columns for further analysis
battle_log_df = full_battle_log_df[['team_0_tag','team_0_name','battleTime','gameMode_name','gameMode_id','team_0_crowns','opponent_0_crowns','team_0_startingTrophies','team_0_trophyChange']]

# %%

# Create player tag to name dictionary
tag_to_name = battle_log_df.drop_duplicates('team_0_tag').set_index("team_0_tag")['team_0_name'].to_dict()

# %%

# Detect wins and streaks for each player individually and add back to the df
for tag,individual_df in battle_log_df.groupby('team_0_tag'):
    # Determine if the player won the battle
    individual_df['win'] = individual_df['team_0_crowns'] > individual_df['opponent_0_crowns']
    
    # Determine player win and loss streaks from the bottom of the set
    groups = (individual_df["win"] != individual_df["win"].shift()).cumsum()
    streak_up = individual_df.groupby(groups).cumcount() + 1
    group_sizes = individual_df.groupby(groups)["win"].transform("size")
    streak_down = group_sizes - streak_up + 1
    
    individual_df["win_streak"] = streak_down.where(individual_df["win"], 0)
    individual_df["loss_streak"] = streak_down.where(~individual_df["win"], 0)
    
    li2.append(individual_df)

battle_log_df = pd.concat(li2, axis=0, ignore_index=True)

# %%

# Save the processed dataframe to CSV for later use
save.parent.mkdir(parents=True, exist_ok=True)
battle_log_df.to_csv(f"{save}/battle_log.csv")

# %%

# Plot trophy progression over time on the ladder for each player
for tag,temp_df in battle_log_df.where(battle_log_df['gameMode_name'] == 'Ladder').groupby('team_0_tag'):
    name = tag_to_name.get(tag, f"Tag: {tag}")
    plt.plot(temp_df['battleTime'], temp_df['team_0_startingTrophies'].interpolate())
    
    plt.xticks(rotation=45, ha="right")
    plt.title(f"{name} Ladder Trophies")
    plt.show()

# %%

# Plot trophy progression over time on the ladder for all players
for tag,temp_df in battle_log_df.where(battle_log_df['gameMode_name'] == 'Ladder').groupby('team_0_tag'):
    name = tag_to_name.get(tag, f"Tag: {tag}")
    plt.plot(temp_df['battleTime'], temp_df['team_0_startingTrophies'].interpolate(), label=name)
    plt.xticks(rotation=45, ha="right")

plt.legend()
plt.show()
# %%
