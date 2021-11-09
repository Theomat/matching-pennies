# Matching Pennies


## Game server

We offer a ready to use game server to collect data from players.

### Start the server

```bash
# Make sure games folder exist
mkdir -p games 
# Launch server
python server/server.py -r <number_of_rounds>
```

The games played will appear in the `games` folder with one file per game.

### Game File structure

A game file is a CSV file with three colunms. 
There is one line per round player.
The first column is `0|1` and represents the human choice.
The second column is `0|1` and represents the CPU choice.
The last column is a positive integer that represents the number of milliseconds elapsed between their last decision and the current decision.
Note that for the first decision the timer starts ticking when the user lands on the play page.

### CPU Strategy

Currently the CPU plays purely randomly.
