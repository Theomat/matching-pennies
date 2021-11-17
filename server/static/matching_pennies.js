var rounds = []
var score = [0, 0]
var startTime = getMillis()

var timeCircleBar;
var scoreBar, WIDTH, HEIGHT;
var dataSent = false

const TARGET_TIME = 10000
const RATIO_FLUC = .0125
const TRIES = 5
const MAX_PARTICLES = 1000
const HIST_SIZE = 10


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

function sendData(try_redirect = true){
    if (dataSent)
        return
    window.alert("Score: You: " + score[0] + " | CPU: " + score[1] + "\nWin rate: " + Math.round(score[0] / rounds.length * 100) + "%\nPayoff: " + (score[0] -score[1]));
    dataSent = true
    $.post("save", { rounds: rounds }, function (result) {
        if (result == "Yes" && try_redirect){
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

    let history = document.getElementById("history")
    let array = []
    let startRound = Math.max(0, rounds.length - HIST_SIZE)
    for (var i = 0; i < 2; i++){
        let line = []
        for (var j = 0; j < HIST_SIZE - rounds.length; j++) {
            line.push("")
        }
        for (var j = startRound; j < rounds.length; j++) {
            let color = rounds[j][i] == 1 ? "danger" : "primary"
            let content = "<a class=\"btn-" + color + " btn-lg fw-bold\"> </a>"
            line.push(content)
        }
        
        array.push(line)
    }
    let col_names = []
    for (var j = 0; j < HIST_SIZE - rounds.length; j++) {
        col_names.push("")
    }
    for (var i = startRound; i < rounds.length; i++){
        let c = rounds[i][0] != rounds[i][1] ? "W" : "L"
        col_names.push("R" + (i + 1) +": " + c)
    }
    history.innerHTML = produceTable(array, "", col_names, ["You", "CPU"])
    timeCircleBar.renderProgress(100)
    // Reset startTime
    startTime = getMillis()
}

function humanChoice(choice){
    if(dataSent)
        return
    let time = getMillis() - startTime
    let round = [choice, getCPUPlay(), time]
    rounds.push(round)
    nextRound()
}

function toRad(degrees){
    return degrees / 180 * Math.PI
}

function roundRect(ctx, x, y, w, h, bl, br){
    ctx.beginPath()
    ctx.moveTo(x + bl, y)

    ctx.lineTo(x + w - br, y)
    ctx.arc(x + w - br, y + br, br, toRad(90), 0, false)

    ctx.lineTo(x + w, y + h - br)
    ctx.arc(x + w - br, y + h - br, br, 0, toRad(270), false)
    ctx.lineTo(x + w - br, y + h)

    ctx.lineTo(x + bl, y + h) 
    ctx.arc(x + bl, y + h - bl, bl, toRad(270), toRad(180), false)

    ctx.lineTo(x, y + bl)
    ctx.arc(x + bl, y + bl, bl, toRad(180), toRad(90), false)
    ctx.closePath()
}

let lastRender = 0
let hu_particles = []
let cpu_particles = []
function renderScoreBar(){
    let t = getMillis()
    let dt = t - lastRender;
    let w = WIDTH
    let h = HEIGHT

    let ctx = scoreBar

    let barWidth = Math.round(0.6 * w)
    let barHeight = Math.round(0.6 * h)
    let tx = (w - barWidth) / 2
    let ty = (h - barHeight) / 2

    ctx.clearRect(0, 0, w, h)
    ctx.save()
    ctx.translate(tx, ty)

    let ratio = rounds.length == 0 ? .5 : score[0] / rounds.length
    let b = h * 0.1

    
    ratio += Math.sin(t / 100) * RATIO_FLUC
    ratio += Math.sin(t / 327) * RATIO_FLUC / 2
    ratio += Math.sin(t / 1143) * RATIO_FLUC / 4
    ratio = Math.min(1, Math.max(0, ratio))

    ctx.save()
    roundRect(ctx, 0, 0, barWidth, barHeight, b, b)
    ctx.fill()
    ctx.clip()

    ctx.fillStyle = '#27ae60';
    ctx.fillRect(0, 0, barWidth * ratio, barHeight)

    ctx.fillStyle = '#f39c12';
    ctx.fillRect(barWidth * ratio, 0, barWidth * (1 - ratio), barHeight)
    ctx.restore()

    // let pradius = b  / 4

    // ctx.fillStyle = '#2ecc71';
    // hu_particles = doParticles(ctx, hu_particles, ratio, -1, ratio, tx, ty, pradius, barWidth, barHeight, dt)
    // ctx.fillStyle = '#f1c40f';
    // cpu_particles = doParticles(ctx, cpu_particles, 1 - ratio, 1, ratio, tx, ty, pradius, barWidth, barHeight, dt)
    ctx.restore()

    let text_height = Math.round(barHeight / 2)
    ctx.font = text_height+ "px Arial"
    let m = ctx.measureText("You")
    ctx.fillStyle = '#2ecc71';
    ctx.fillText("You", tx / 2 - m.width / 2, ty + barHeight / 2 + m.actualBoundingBoxAscent / 2)
    ctx.fillStyle = '#f1c40f';
    m = ctx.measureText("CPU")
    ctx.fillText("CPU", w - tx / 2 - m .width / 2, ty + barHeight / 2 + m.actualBoundingBoxAscent / 2)



    lastRender = getMillis();
}

function doParticles(ctx, particles, chance, direction, ratio, tx, ty, pradius, barWidth, barHeight, dt){
    let next_particles = []
    for (var i = 0; i < particles.length; i++) {
        let part = particles[i];
        let x = part[0]
        let y = part[1]
        let vx = part[2]
        let vy = part[3]
        let ticks = part[4]
        ctx.beginPath()
        ctx.arc(x, y, pradius, 0, 50, false)
        ctx.fill()
        ticks -= dt
        if (ticks > 0 && x - pradius >= -tx && y - pradius >= -ty && x + pradius <= barWidth + tx && y + pradius <= barHeight + ty) {
            x += vx * dt / 1000 * pradius
            y += vy * dt / 1000 * pradius
            next_particles.push([x, y, vx, vy, ticks])
        }
    }
    for (var i = 0; i < TRIES && next_particles.length < MAX_PARTICLES; ++i) {
        if (Math.random() < chance) {
            next_particles.push([barWidth * ratio + direction * pradius, Math.random() * barHeight,
            direction * (.1 + Math.random()) * barWidth / 2, (2 * Math.random() - 1) * barHeight / 2,
            Math.round(Math.random() * 800 + 200)])
        }
    }
    return next_particles
}


function blink(duration){
    if (dataSent)
        return
    let overlay = document.getElementById("overlay")
    overlay.classList.add("blink")
    setTimeout(() => {
        overlay.classList.remove("blink")
    },
    duration)
}

// MAIN
$(document).ready(function () {

    let canvas = document.getElementById("score")
    
    canvas.width = canvas.clientWidth
    canvas.height = canvas.clientHeight
    
    scoreBar = canvas.getContext("2d");

    WIDTH = canvas.width;
    HEIGHT = canvas.height;

    
    timeCircleBar = new Circlebar({
        element: ".time-bar",
        skin: "fire",
        type: "manual",
        maxValue: 100,
    });
    nextRound()

    let lastBlink = 0
    setInterval(() => {
        let x = (getMillis() - startTime) / 1000;
        let value = 1/20 * Math.log((x *x) / 0.11 + 1) / Math.log(1.7);
        let progress = Math.round(100 * (1 - value));
        timeCircleBar.renderProgress(Math.max(0, progress));
        if (progress < 50){
            let nextDuration = Math.max(100, (1 - progress / 50) * 1000)
            if(getMillis() - lastBlink > 1000 - nextDuration){
                lastBlink = getMillis() + nextDuration
                blink(nextDuration)
            }
        }
    }, 100)

    setInterval(renderScoreBar, 20)
});

$(window).bind('beforeunload', function () {
    sendData(false);
});