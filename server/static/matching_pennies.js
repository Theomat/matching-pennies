var rounds = []
var startTime = getMillis()
var started = false
var tuto_number_two = false
var dataSent = false
var trial_end = 0
var alertShown = false
var true_start_time = getMillis()
function getMillis(){
    const d = new Date();
    return d.getTime();
}

function sendData(){
    if (dataSent)
        return
    dataSent = true
    $.post("save", { rounds: rounds , room_no: room_no, mail: mail}, function (result) {});
}

function press(choice, played_with_keys = false){
    if (dataSent || !started || alertShown)
        return
    let time = getMillis() - startTime
    let round = [choice, time, played_with_keys, tuto_number_two]
    rounds.push(round)
    startTime = getMillis()
}

function round(f, decimals=2){
    let multiplier = Math.pow(10, decimals)
    let x = Math.round(f * multiplier)
    return x / multiplier
}

// MAIN
$(document).ready(function () {
    let real = document.getElementById("real")
    real.style.display = "none";
    let tuto = document.getElementById("tuto")


    setTimeout(() => {
        real.style.display = "block"
        tuto.style.display = "none"
        started = true
        startTime = getMillis()
        tuto_number_two = true
        mail = document.getElementById("mail").value
        setTimeout(() => {
            alertShown = true
            trial_end = rounds.length > 0 ? rounds.length - 1 : 0
            tuto_number_two = false
            let bit_per_second = round(rounds.length / test_time, 2)
            let s = ""
            for(var i = 0; i < rounds.length;i++){
                s += "" + rounds[i][0]
            }
            alert("You generated " + rounds.length + " elements.\nThat is " + bit_per_second + " bits/sec, you should have at least 2 bits/sec.\nThis was the true end of the tutorial, now the real experiment will start.\nHere is what your sequence looks like:\n"+s)
            startTime = getMillis()
            true_start_time = getMillis()
            setTimeout(() => {
                sendData()
                alert("Thank you the experiment is over!")
                $(location).attr("href", "");
            }, play_time * 60 * 1000)
            alertShown = false
        }, test_time * 1000)

        let speed = document.getElementById("speed")
        setInterval(() => {
            let total_time = getMillis() - true_start_time
            let remaining_time = play_time * 60 * 1000 - total_time
            let bits_generated = rounds.length - trial_end
            let bit_per_second = round(bits_generated / total_time * 1000, 2)
            if(bit_per_second < 1){
                speed.innerHTML = "You should go faster: " + bit_per_second + " bits/sec"
            } else if (!tuto_number_two && bit_per_second * remaining_time / 1000 + bits_generated < play_time * 60 * 2){
                speed.innerHTML = "You will not generate enough data at this speed: " + bit_per_second + " bits/sec"
            } else {
                speed.innerHTML = ""
            }

        }, 100)
    }, read_time * 60 * 1000)



});

document.onkeyup = function (e) {
    var e = e || window.event; // for IE to cover IEs window event-object
    if (e.key == 'ArrowLeft') {
        press(0, true)
        return false;
    } else if (e.key == 'ArrowRight') {
        press(1, true)
        return false;
    }
}

$(window).bind('beforeunload', function () {
    sendData(false);
});