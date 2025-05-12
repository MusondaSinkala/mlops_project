import pandas as pd
import json
import numpy as np
import ast
from functools import reduce

def process_data():
    
    # Columns to convert
    columns_to_convert = [
        "type", "possession_team", "play_pattern", "team", "tactics", "related_events", 
        "player", "position", "pass", "carry", "ball_receipt", "under_pressure", 
        "duel", "dribble", "interception", "clearance", "shot", "block", 
        "ball_recovery", "50_50", "goalkeeper"
    ]

    # Safe evaluation function
    def safe_eval(x):
        if isinstance(x, str) and x.strip() == '':
            return None
        try:
            return ast.literal_eval(x) if isinstance(x, str) else x
        except (ValueError, SyntaxError) as e:
            print(f"Error evaluating: {x} ({e})")
            return None


    # Define converter dict
    converters = {col: safe_eval for col in columns_to_convert}

    # Load the CSV with the converters
    df = pd.read_csv("/mnt/block/data/final_datasets/streamed_data.csv", converters=converters)
    
    columns = ['Id', 'Matches Played',
               'Total Shots', 'Accurate Shots', 'Shot Accuracy', 'Goals', 'Shot Conversion', 'Penalties Taken', 'Penalties Scored', 'Penalty Conversion', 'Free Kick Shots',
               'Total Passes', 'Accurate Passes', 'Pass Accuracy', 'Key Passes', 'Assists', 'Crosses', 'Free Kick Crosses', 
               'Run Attempts With Ball', 'Successful Runs With Ball', 'Perc Successful Runs With Ball', 'Dribbles',
               'Aerial Duels', 'Aerial Duels Won', 'Perc Aerial Duels Won', 'Ground Defensive duels Won', 'Loose Ball Duels', 'Loose Balls Won', 'Perc Loose Balls Won',
               'Sliding Tackles', 'Interceptions', 'Clearances', 'Blocks', 'Possession Regained', 'Own Goals',
               'GK Balls Attacked', 'GK Save Attempts', 'GK Successful Save Attempts', 'Perc GK Save Success'
              ]
    
    # Ensure player name is accessible
    df['Id'] = df['player'].apply(lambda x: x['id'] if pd.notnull(x) else None)



    # Replace None with np.nan to avoid issues in aggregations
    df = df.replace({None: np.nan})

    # Matches Played – since all events are from a single match, we set it as 1 for all
    matches_played         = df.groupby('Id')['match_id'].nunique().reset_index()
    matches_played.columns = ['Id', 'Matches Played']

    # Shots
    shots                           = df[df['type'].apply(lambda x: x.get('name') == 'Shot')].copy()
    shots['Accurate Shot']          = shots['shot'].apply(lambda x: x.get('outcome', {}).get('name') == 'Goal' or x.get('outcome', {}).get('name') in ['On Target', 'Saved'])
    shots['Goal']                   = shots['shot'].apply(lambda x: x.get('outcome', {}).get('name') == 'Goal')
    shots_agg                       = shots.groupby('Id').agg(Total_Shots      = ('Id', 'count'),
                                                              Accurate_Shots   = ('Accurate Shot', 'sum'),
                                                              Goals            = ('Goal', 'sum'),
                                                              Penalties_Taken  = ('shot', lambda x: sum(1 for s in x if s.get('type', {}).get('name') == 'Penalty')),
                                                              Penalties_Scored = ('shot', lambda x: sum(1 for s in x if s.get('type', {}).get('name') == 'Penalty' and s.get('outcome', {}).get('name') == 'Goal')),
                                                              Free_Kick_Shots  = ('shot', lambda x: sum(1 for s in x if s.get('type', {}).get('name') == 'Free Kick'))
                                                             ).reset_index()

    shots_agg['Shot Accuracy']      = shots_agg['Accurate_Shots'] / shots_agg['Total_Shots']
    shots_agg['Shot Conversion']    = shots_agg['Goals'] / shots_agg['Total_Shots']
    shots_agg['Penalty Conversion'] = shots_agg['Penalties_Scored'] / shots_agg['Penalties_Taken'].replace({0: np.nan})

    # Passes
    passes             = df[df['type'].apply(lambda x: x.get('name') == 'Pass')].copy()
    passes['accurate'] = passes['pass'].apply(lambda x: x.get('outcome') is None)
    passes['key_pass'] = passes['pass'].apply(lambda x: x.get('type', {}).get('name') == 'Key Pass')

    passes_agg         = passes.groupby('Id').agg(Total_Passes      = ('Id', 'count'),
                                                  Accurate_Passes   = ('accurate', 'sum'),
                                                  Key_Passes        = ('key_pass', 'sum'),
                                                  Crosses           = ('pass', lambda x: sum(1 for s in x if s.get('height', {}).get('name') == 'High Pass')),
                                                  Free_Kick_Crosses = ('pass', lambda x: sum(1 for s in x if s.get('type', {}).get('name') == 'Free Kick' and s.get('height', {}).get('name') == 'High Pass'))
                                                 ).reset_index()

    passes_agg['Pass Accuracy'] = passes_agg['Accurate_Passes'] / passes_agg['Total_Passes']

    # Assists
    goals           = shots[shots['Goal']]
    goals['Assist'] = goals['pass'].apply(lambda x: x.get('recipient', {}).get('name') if isinstance(x, dict) else np.nan)
    assists_agg     = goals.groupby('Assist').agg(Assists=('Assist', 'count')).rename_axis('Id').reset_index()

    # Carries / Runs With Ball
    carries     = df[df['type'].apply(lambda x: x.get('name') == 'Carry')].copy()
    carries_agg = carries.groupby('Id').agg(Run_Attempts_With_Ball=('Id', 'count'),
                                            Successful_Runs_With_Ball=('Id', 'count')
                                           ).reset_index()

    # Dribbles
    dribbles             = df[df['type'].apply(lambda x: x.get('name') == 'Dribble')].copy()
    dribbles['Dribbles'] = dribbles['dribble'].apply(lambda x: x.get('outcome', {}).get('name') == 'Complete')
    dribbles_agg         = dribbles.groupby('Id').agg(Dribbles = ('Dribbles', 'sum')).reset_index()

    # Defensive duels, aerials, and other duels
    duels           = df[df['type'].apply(lambda x: x.get('name') == 'Duel')].copy()
    duels['aerial'] = duels['duel'].apply(lambda x: x.get('type', {}).get('name') == 'Aerial Duel')
    duels['won']    = duels['duel'].apply(lambda x: x.get('outcome', {}).get('name') == 'Won')
    aerials         = duels[duels['aerial']]
    aerials_agg     = aerials.groupby('Id').agg(Aerial_Duels = ('Id', 'count'),
                                                Aerial_Duels_Won=('won', 'sum')
                                               ).reset_index()
    aerials_agg['Perc Aerial Duels Won'] = aerials_agg['Aerial_Duels_Won'] / aerials_agg['Aerial_Duels']

    ground_def_duels = df[df['type'].apply(lambda x: x.get('name') == 'Duel')].copy()
    ground_def_duels = ground_def_duels[ground_def_duels['duel'].apply(lambda x: x.get('type', {}).get('name') == 'Ground defending duel')]

    ground_def_duels['won'] = ground_def_duels['duel'].apply(lambda x: x.get('outcome', {}).get('name') == 'Won')

    ground_def_duels_agg = ground_def_duels.groupby('Id').agg(Ground_Defensive_Duels = ('Id', 'count'),
                                                              Ground_Defensive_Duels_Won=('won', 'sum')
                                                             ).reset_index()

    ground_def_duels_agg['Perc Ground Defensive Duels Won'] = (
        ground_def_duels_agg['Ground_Defensive_Duels_Won'] / ground_def_duels_agg['Ground_Defensive_Duels'].replace(0, np.nan)
                                                              )

    loose_ball_duels = df[df['type'].apply(lambda x: x.get('name') == 'Duel')].copy()
    loose_ball_duels = loose_ball_duels[loose_ball_duels['duel'].apply(lambda x: x.get('type', {}).get('name') == 'Loose Ball')]

    loose_ball_duels['won'] = loose_ball_duels['duel'].apply(lambda x: x.get('outcome', {}).get('name') == 'Won')

    loose_ball_duels_agg    = loose_ball_duels.groupby('Id').agg(Loose_Ball_Duels = ('Id', 'count'),
                                                                 Loose_Balls_Won = ('won', 'sum')
                                                                ).reset_index()

    loose_ball_duels_agg['Perc Loose Balls Won'] = (
        loose_ball_duels_agg['Loose_Balls_Won'] / loose_ball_duels_agg['Loose_Ball_Duels'].replace(0, np.nan)
                                                   )

    # Sliding tackles, interceptions, clearances, blocks, possession regain
    interceptions     = df[df['type'].apply(lambda x: x.get('name') == 'Interception')].copy()
    interceptions_agg = interceptions.groupby('Id').agg(Interceptions = ('Id', 'count')).reset_index()

    tackles     = df[df['type'].apply(lambda x: x.get('name') == 'Block')].copy()
    tackles_agg = tackles.groupby('Id').agg(Sliding_Tackles = ('Id', 'count')).reset_index()

    # Clearances
    clearances     = df[df['type'].apply(lambda x: x.get('name') == 'Clearance')]
    clearances_agg = clearances.groupby('Id').agg(Clearances = ('Id', 'count')).reset_index()

    # Ball recoveries
    recoveries     = df[df['type'].apply(lambda x: x.get('name') == 'Ball Recovery')]
    recoveries_agg = recoveries.groupby('Id').agg(Possession_Regained = ('Id', 'count')).reset_index()

    blocks         = df[df['type'].apply(lambda x: x.get('name') == 'Block')].copy()

    blocks_agg = blocks.groupby('Id').agg(Blocks = ('Id', 'count')).reset_index()

    shots     = df[df['type'].apply(lambda x: x.get('name') == 'Shot')].copy()
    own_goals = shots[shots['shot'].apply(lambda x: x.get('outcome', {}).get('name') == 'Own Goal')]

    own_goals_agg = own_goals.groupby('Id').agg(Own_Goals = ('Id', 'count')).reset_index()

    # Goalkeeper
    gk            = df[df['type'].apply(lambda x: x.get('name') == 'Goal Keeper')].copy()
    gk['save']    = gk['goalkeeper'].apply(lambda x: x.get('type', {}).get('name') == 'Shot Saved')
    gk['success'] = gk['goalkeeper'].apply(lambda x: x.get('outcome', {}).get('name') == 'Success')
    gk_agg        = gk.groupby('Id').agg(GK_Balls_Attacked           = ('Id', 'count'),
                                         GK_Save_Attempts            = ('save', 'sum'),
                                         GK_Successful_Save_Attempts = ('success', 'sum')
                                        ).reset_index()
    gk_agg['Perc GK Save Success'] = gk_agg['GK_Successful_Save_Attempts'] / gk_agg['GK_Save_Attempts'].replace(0, np.nan)

    # Combine all
    dfs = [matches_played, shots_agg, passes_agg, assists_agg, carries_agg, dribbles_agg,
           aerials_agg, ground_def_duels_agg, loose_ball_duels_agg,
           interceptions_agg, tackles_agg, clearances_agg, recoveries_agg, blocks_agg, own_goals_agg,
           gk_agg]

    final_df = reduce(lambda left, right: pd.merge(left, right, on = 'Id', how = 'outer'), dfs)
    final_df = final_df.fillna(0)

    # Add percentage of successful runs
    final_df['Perc Successful Runs With Ball'] = final_df['Successful_Runs_With_Ball'] / final_df['Run_Attempts_With_Ball'].replace(0, np.nan)

    # Rename for final output
    final_df = final_df.rename(columns = {'Total_Shots': 'Total Shots',
                                          'Accurate_Shots': 'Accurate Shots',
                                          'Goals': 'Goals',
                                          'Shot Accuracy': 'Shot Accuracy',
                                          'Shot Conversion': 'Shot Conversion',
                                          'Penalties_Taken': 'Penalties Taken',
                                          'Penalties_Scored': 'Penalties Scored',
                                          'Penalty Conversion': 'Penalty Conversion',
                                          'Free_Kick_Shots': 'Free Kick Shots',
                                          'Total_Passes': 'Total Passes',
                                          'Accurate_Passes': 'Accurate Passes',
                                          'Pass Accuracy': 'Pass Accuracy',
                                          'Key_Passes': 'Key Passes',
                                          'Crosses': 'Crosses',
                                          'Free_Kick_Crosses': 'Free Kick Crosses',
                                          'Run_Attempts_With_Ball': 'Run Attempts With Ball',
                                          'Successful_Runs_With_Ball': 'Successful Runs With Ball',
                                          'Dribbles': 'Dribbles',
                                          'Aerial_Duels': 'Aerial Duels',
                                          'Aerial_Duels_Won': 'Aerial Duels Won',
                                          'Perc Aerial Duels Won': 'Perc Aerial Duels Won',
                                          'Ground_Defensive_Duels_Won': 'Ground Defensive duels Won',
                                          'Loose_Ball_Duels': 'Loose Ball Duels',
                                          'Loose_Balls_Won': 'Loose Balls Won',
                                          'Possession_Regained': 'Possession Regained',
                                          'Sliding_Tackles': 'Sliding Tackles',
                                          'Own_Goals': 'Own Goals',
                                          'GK_Balls_Attacked': 'GK Balls Attacked',
                                          'GK_Save_Attempts': 'GK Save Attempts',
                                          'GK_Successful_Save_Attempts': 'GK Successful Save Attempts',
                                          'Perc GK Save Success': 'Perc GK Save Success'
                                         })
    final_df = final_df[columns]
    
    return final_df

if __name__ == "__main__":
    process_data()