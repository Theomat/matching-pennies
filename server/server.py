import argparse
import os
import csv
from types import SimpleNamespace

from flask import Flask, render_template, request

# -----------------------------------------------------------
## Globals
# -----------------------------------------------------------
min_rounds_to_save: int = 5
game_no: int = 0
# Compute first free game number
while os.path.exists(f"./games/{game_no}.csv"):
    game_no += 1
# -----------------------------------------------------------
## Parse arguments
# -----------------------------------------------------------
def parse_args() -> SimpleNamespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Flask server to run an online matching penny game server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="(default: \"0.0.0.0\") the server host")
    parser.add_argument("-d", "--debug", action="store_true", help="(default: False) debug mode")
    parser.add_argument("-m", "--min", action="store", type="int", default=min_rounds_to_save, help=f"(default: {min_rounds_to_save}) minimum number of rounds to be played for the game to be saved")

    return parser.parse_args()

# -----------------------------------------------------------
## Flask routes
# -----------------------------------------------------------
app: Flask = Flask(__name__)

@app.route('/')
def index() -> str:
    return render_template("index.html", games_played=game_no)

@app.route('/play')
def play() -> str:
    return render_template("play.html")

@app.route('/save', methods=["POST"])
def save_game():
    global game_no
    try:
        # Parse data
        rounds = []
        i = 0
        success = True
        while success:
            round = request.form.getlist(f"rounds[{i}][]")
            success = len(round) > 0
            if success:
                rounds.append(round)
            i += 1
        if len(rounds) < min_rounds_to_save:
            return "Yes"
        # Write data to disk
        with open(f"./games/{game_no}.csv", "w") as fd:
            csv.writer(fd).writerows(rounds)
        
        game_no += 1
        return "Yes"
    except:
        return "No"

# -----------------------------------------------------------
## Main
# -----------------------------------------------------------
if __name__ == "__main__":
    parameters: SimpleNamespace = parse_args()
    min_rounds_to_save = parameters.min
    app.run(debug=parameters.debug, host=parameters.host)