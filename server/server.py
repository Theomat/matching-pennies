import argparse
import os
import random
import csv
from types import SimpleNamespace
from typing import Dict, List, Tuple
import time

from flask import Flask, render_template, request

GAME_FOLDER = "./games"
GAME_FOLDER = "/home/mpennies/matching-pennies/games"
# -----------------------------------------------------------
## Globals
# -----------------------------------------------------------
refresh_time: int = 3 # seconds
play_time: int = 1 # minutes
read_time: float = .5 # minute
test_time: int = 30 # seconds
# -----------------------------------------------------------
## Parse arguments
# -----------------------------------------------------------
def parse_args() -> SimpleNamespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Flask server to run an online matching penny game server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="(default: \"0.0.0.0\") the server host")
    parser.add_argument("-p", "--port", type=int, default=5000, help="(default: 5000) the server port")
    parser.add_argument("-d", "--debug", action="store_true", help="(default: False) debug mode")
    parser.add_argument("-o", "--output", type=str, default=GAME_FOLDER, help=f"(default: '{GAME_FOLDER}') folder in which games are saved")

    return parser.parse_args()

# -----------------------------------------------------------
## Flask routes
# -----------------------------------------------------------
app: Flask = Flask(__name__)

rooms: Dict[int, Tuple[float, List[float]]] = {}
ongoing: Dict[int, int] = {}



def get_new_room_id() -> int:
    id = random.randrange(1000, 9999)
    if id in ongoing or id in rooms:
        return get_new_room_id()
    if os.path.exists(f"{GAME_FOLDER}/{id}_1.csv"):
        return get_new_room_id()
    return id

def update_players(room_id: int) -> int:
    time_now = now()
    object = [t for t in rooms.get(room_id)[1] if time_now - t <= refresh_time]
    rooms[room_id] = (rooms[room_id][0], object)
    return len(object)

def now() -> float:
    return time.perf_counter()

@app.route('/')
def index() -> str:
    return render_template("index.html")

@app.route('/create')
def create_room() -> str:
    room_id = get_new_room_id()
    t = now()
    rooms[room_id] = (t, [])
    return render_template("admin.html", room_no=room_id, timestamp=t)

@app.route('/<int:room_id>')
def join_room(room_id: int) -> str:
    if room_id in ongoing:
        return render_template("play.html", room_no=room_id, play_time=play_time, read_time=read_time, test_time=test_time)

    if room_id not in rooms:
        return render_template("fail_join.html", room_no=room_id)
    rooms[room_id][1].append(now())
    return render_template("wait.html", room_no=room_id, refresh_time=refresh_time)


@app.route('/<int:room_id>/info')
def room_info(room_id: int) -> str:
    if room_id not in rooms:
        return "-1"
    return f"{update_players(room_id)}"

@app.route('/<int:room_id>/start', methods=["POST"])
def room_start(room_id: int) -> str:
    if room_id not in rooms:
        return "That room does not exist!"
    t = float(request.form.getlist("timestamp")[0])
    if abs(t - rooms.get(room_id)[0]) > 1e-3:
        return "Invalid timestamp"
    ongoing[room_id] = update_players(room_id)
    del rooms[room_id]
    return "true"

@app.route('/<int:room_id>/started')
def thanks(room_id: int) -> str:
    return render_template("thanks.html", room_no=room_id)


@app.route('/save', methods=["POST"])
def save_game():
    try:
        room_id = int(request.form.getlist("room_no")[0])
        mail = request.form.getlist("mail")[0]
    except:
        return
    if room_id not in ongoing:
        return ""
    game_no = ongoing[room_id]
    ongoing[room_id] -= 1
    if ongoing[room_id] <= 0:
        del ongoing[room_id]
    try:
        # Parse data
        rounds = [["room_no", str(room_id), "mail", mail]]
        i = 0
        success = True
        while success:
            round = request.form.getlist(f"rounds[{i}][]")
            success = len(round) > 0
            if success:
                rounds.append(round)
            i += 1
        # Write data to disk
        with open(f"{GAME_FOLDER}/{room_id}_{game_no}.csv", "w") as fd:
            csv.writer(fd).writerows(rounds)
        
        return "Yes"
    except:
        print("An error occured when saving file!")
        return "No"

# -----------------------------------------------------------
## Main
# -----------------------------------------------------------
if __name__ == "__main__":
    parameters: SimpleNamespace = parse_args()
    GAME_FOLDER = parameters.output
    app.run(debug=parameters.debug, host=parameters.host, port=parameters.port)