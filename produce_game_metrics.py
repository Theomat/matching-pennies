import glob
import json
import csv

MAX_ROUNDS = 20
metrics = {
    "payoff": {
        "type": "distribution",
        "bins": list(range(-MAX_ROUNDS, MAX_ROUNDS + 2)),
        "data": [],
    },
    "choice": {
        "type": "distribution",
        "bins": [0, 1, 2],
        "data": [],
    },
    "changed_choice_after_lost": {
        "type": "distribution",
        "bins": [0, 1, 2],
        "labels": ["False", "True"],
        "data": [],
    },
    "time": {
        "type": "distribution",
        "data": [],
    },
    "time_after_lost": {
        "type": "distribution",
        "data": [],
    },
}

for file in glob.glob("./games/*.csv"):
    with open(file) as fd:
        rows = [row for row in csv.reader(fd)]

    last_round = None
    payoff: int = 0
    for round in rows:
        win = round[0] != round[1]
        metrics["choice"]["data"].append(int(round[0]))
        payoff += 1 if win else -1
        time = int(round[2])
        metrics["time"]["data"].append(time)
        changed_choice_after_lost = last_round is not None and last_round != round[0]
        metrics["changed_choice_after_lost"]["data"].append(int(changed_choice_after_lost))
        if last_round is not None:
            metrics["time_after_lost"]["data"].append(time)

        last_round = None if win else round[0]

    metrics["payoff"]["data"].append(payoff)

with open("metrics.json", "w") as fd:
    json.dump(metrics, fd)