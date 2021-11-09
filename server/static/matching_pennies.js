var rounds = []
var score = [0, 0]
var startTime = getMillis()


function produceTable(array, caption, col_names, line_names) {
    var caption = "<caption>" + caption + "</caption>"

    var head = "<thead>" + (line_names === undefined ? "" : "<tr><th scope=\"col\">#</th>")
    for (var i = 0; i < col_names.length; i++) {
        head += "<th scope=\"col\">" + col_names[i] + "</th>"
    }
    head += "</tr></thead>"

    var body = "<tbody>"
    for (var j = 0; j < array.length; j++) {
        var row = "<tr>" + (line_names === undefined ? "" : "<th scope=\"row\">" + line_names[j] + " </th>")
        var line = array[j]
        for (var i = 0; i < line.length; i++) {
            row += "<td>" + line[i] + "</td>"
        }
        row += "</tr>"
        body += row
    }
    body += "</tbody>"
    return "<table class=\"table caption-top\">" + caption + head + body + "</table>"
}

function getCPUPlay(){
    return Math.floor(Math.random() * 2);
}

function getMillis(){
    const d = new Date();
    return d.getTime();
}

function sendData(){
    $.post("save", { rounds: rounds }, function (result) {
        if(result == "Yes"){
            $(location).attr("href", window.location.origin);
        }
    });
}

function nextRound(){
    let numRound = rounds.length


    if(numRound >= 1){
        // Update score
        let last_round = rounds[rounds.length - 1]
        score[0] += last_round[0] != last_round[1]
        score[1] += last_round[0] == last_round[1]
    }

    // Update visual elements
    let hu_score = document.getElementById("score-you")
    hu_score.innerHTML = score[0]
    let cpu_score = document.getElementById("score-cpu")
    cpu_score.innerHTML = score[1]


    
    let history = document.getElementById("history")
    let array = []
    for (var i = 0; i < 2; i++){
        let line = []
        for (var j = 0; j < rounds.length; j++) {
            let color = rounds[j][i] == 1 ? "danger" : "primary"
            let content = "<a class=\"btn btn-lg fw-bold label label-" + color + "\"> </a>"
            line.push(content)
        }
        array.push(line)
    }
    let col_names = []
    for (var i = 0; i < rounds.length; i++){
        let c = rounds[i][0] != rounds[i][1] ? "W" : "L"
        col_names.push("R" + (i + 1) +": " + c)
    }
    if(numRound <= MAX_ROUNDS){
        history.innerHTML = produceTable(array, "", col_names, ["You", "CPU"])
    }

    let round = document.getElementById("round")
    if (numRound >= MAX_ROUNDS) {
        round.innerHTML = "Finished"
        sendData()
    } else {
        round.innerHTML = "Round " + (numRound + 1) + "/" + MAX_ROUNDS
    }
    // Reset startTime
    startTime = getMillis()
}

function humanChoice(choice){
    let numRound = rounds.length
    if (numRound >= MAX_ROUNDS)
        return
    let time = getMillis() - startTime
    let round = [choice, getCPUPlay(), time]
    rounds.push(round)
    nextRound()
}


// MAIN
$(document).ready(function () {
    nextRound()
});