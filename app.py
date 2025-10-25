from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import os
import ast
from datetime import datetime

app = Flask(__name__, template_folder = 'templates', static_folder = 'static')
df  = pd.read_csv('final_player_df.csv')
df.set_index('id', inplace = True)

# Create player name to ID dictionary
player_dict = {row['full_name']: idx for idx, row in df.iterrows()}

@app.route("/")
def home():
    return render_template('index.html', player_names = list(player_dict.keys()))

@app.route('/player/<int:player_id>')
def get_player(player_id):
    if player_id not in df.index:
        return jsonify({'error': 'Player not found'}), 404
    row = df.loc[player_id].drop('top_knn_ids').to_dict()
    row['density_plot_url']         = f"/static/density_plots/{player_id}.png"
    row['contract_expiration_date'] = datetime.strptime(row['contract_expiration_date'],'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
    row['market_value_in_eur']      = "€{:,.0f}".format(row['market_value_in_eur'])
    return jsonify(row)

@app.route('/similar_players/<int:player_id>')
def get_similar(player_id):
    if player_id not in df.index:
        return jsonify({'error': 'Player not found'}), 404

    top_ids = pd.unique(df.loc[player_id]['top_knn_ids'])

    players = []
    for sid in top_ids:
        if sid in df.index:
            row = df.loc[sid]
            if isinstance(row, pd.DataFrame): # If df.loc[sid] returns multiple rows, take the first one
                row = row.iloc[0]

            players.append({
                'id': int(sid),
                'full_name': str(row['full_name']),
                'club': str(row['club']),
                'role': str(row['role']),
                'image_url': str(row['image_url'])
            })

    return jsonify({'similar_players': players})

@app.route('/get_player_id', methods=['POST'])
def get_player_id():
    name = request.json.get("name")
    player_id = player_dict.get(name)
    return jsonify({"player_id": player_id})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
