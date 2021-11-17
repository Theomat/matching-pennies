import glob
import csv

from metrics_tracker import Metrics, DataType


metrics = Metrics()
metrics.new_data("payoff", DataType.DISTRIBUTION)
metrics.new_data("choice", DataType.DISTRIBUTION, labels=["Blue", "Red"])
metrics.new_data("rounds", DataType.DISTRIBUTION)
metrics.new_data("choice.after.lost.changed", DataType.DISTRIBUTION, labels= ["False", "True"]), 
metrics.new_data("win.rate", DataType.DISTRIBUTION)
metrics.new_data("time", DataType.DISTRIBUTION)
metrics.new_data("time.after.lost", DataType.DISTRIBUTION)

for file in glob.glob("./games/*.csv"):
    with open(file) as fd:
        rows = [row for row in csv.reader(fd) if len(row) >= 3]

    if len(rows) <= 1:
        continue
    last_round = None
    payoff: int = 0
    metrics.add("rounds", len(rows))
    wins: int = 0
    for round in rows:
        win = round[0] != round[1]
        metrics.add("choice", int(round[0]))
        payoff += 1 if win else -1
        wins += win
        time = int(round[2])
        metrics.add("time", time)
        changed_choice_after_lost = last_round is not None and last_round != round[0]
        if last_round is not None:
            metrics.add("choice.after.lost.changed", int(changed_choice_after_lost))
            metrics.add("time.after.lost", time)

        last_round = None if win else round[0]

    metrics.add("win.rate", wins / len(rows))
    metrics.add("payoff", payoff)

metrics.auto_bins("payoff")
metrics.auto_bins("rounds")
metrics.auto_bins("choice")
metrics.auto_bins("choice.after.lost.changed")
metrics.save()