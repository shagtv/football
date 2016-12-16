(function () {
    var speed = 3;
    var moveX = 0;
    var moveY = 0;

    var players = [];
    var ws = new WebSocket("ws://shagtv.net:8000/ws");

    ws.onmessage = function (evt) {
        var data = JSON.parse(evt.data);
        if (data['command'] == 'draw') {
            pitch.draw();

            data['players'].each(function(data) {
                var player = new Player(
                    data[0],
                    data[1],
                    data[2],
                    data[3]
                );
                player.draw();
            });
            ball.x = data['ball'][0];
            ball.y = data['ball'][1];
            ball.draw();
            document.getElementById('result-home').innerHTML = data['result']['home'];
            document.getElementById('result-guest').innerHTML = data['result']['guest'];
            document.getElementById('ccu').innerHTML = data['ccu'];
        } else if (data['command'] == 'msg') {
            var html = '<p><strong>' + data['author'] + '</strong> (' + data['dt'] + '): ';
            html += data['msg'] + '</p>';
            console.log(data);
            console.log(html);
            document.getElementById('msgs').innerHTML = html + document.getElementById('msgs').innerHTML
        } else if (data['command'] == 'game-list') {
            var html = '';
            data['games'].forEach(function (game) {
                html += '<p id="game-' + game[0] + '">';
                html += game[0] + ' (created: ' + game[1] + ') ';
                html += '<button>Open</button>';
                html += '</p>';
            });
            document.getElementById('games-block').innerHTML = html;
        }
    };

    ws.onopen = function () {
        console.log('open');
        var name = '' + parseInt(Math.random() * 100) + '*';
        document.getElementById('name').value = name;
        ws.send(JSON.stringify({
            'command': 'save-name',
            'name': name,
            'first': true
        }));

        ws.send(JSON.stringify({
            'command': 'game-list',
            'name': name,
            'first': true
        }));
    };

    ws.onerror = function (evt) {
        console.log('error:' + evt)
    };

    var canvas = document.getElementById('pitch');
    var ctx = canvas.getContext('2d');

    var pitch = {
        draw: function () {

            // Outer lines
            ctx.beginPath();
            ctx.rect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "#060";
            ctx.fill();
            ctx.lineWidth = 1;
            ctx.strokeStyle = "#FFF";
            ctx.stroke();
            ctx.closePath();

            ctx.fillStyle = "#FFF";

            // Mid line
            ctx.beginPath();
            ctx.moveTo(canvas.width / 2, 0);
            ctx.lineTo(canvas.width / 2, canvas.height);
            ctx.stroke();
            ctx.closePath();

            //Mid circle
            ctx.beginPath();
            ctx.arc(canvas.width / 2, canvas.height / 2, 73, 0, 2 * Math.PI, false);
            ctx.stroke();
            ctx.closePath();
            //Mid point
            ctx.beginPath();
            ctx.arc(canvas.width / 2, canvas.height / 2, 2, 0, 2 * Math.PI, false);
            ctx.fill();
            ctx.closePath();

            //Home penalty box
            ctx.beginPath();
            ctx.rect(0, (canvas.height - 322) / 2, 132, 322);
            ctx.stroke();
            ctx.closePath();
            //Home goal box
            ctx.beginPath();
            ctx.rect(0, (canvas.height - 146) / 2, 44, 146);
            ctx.stroke();
            ctx.closePath();
            //Home goal
            ctx.beginPath();
            ctx.moveTo(1, (canvas.height / 2) - 22);
            ctx.lineTo(1, (canvas.height / 2) + 22);
            ctx.lineWidth = 2;
            ctx.stroke();
            ctx.closePath();
            ctx.lineWidth = 1;

            //Home penalty point
            ctx.beginPath();
            ctx.arc(88, canvas.height / 2, 1, 0, 2 * Math.PI, true);
            ctx.fill();
            ctx.closePath();
            //Home half circle
            ctx.beginPath();
            ctx.arc(88, canvas.height / 2, 73, 0.29 * Math.PI, 1.71 * Math.PI, true);
            ctx.stroke();
            ctx.closePath();

            //Away penalty box
            ctx.beginPath();
            ctx.rect(canvas.width - 132, (canvas.height - 322) / 2, 132, 322);
            ctx.stroke();
            ctx.closePath();
            //Away goal box
            ctx.beginPath();
            ctx.rect(canvas.width - 44, (canvas.height - 146) / 2, 44, 146);
            ctx.stroke();
            ctx.closePath();
            //Away goal
            ctx.beginPath();
            ctx.moveTo(canvas.width - 1, (canvas.height / 2) - 22);
            ctx.lineTo(canvas.width - 1, (canvas.height / 2) + 22);
            ctx.lineWidth = 2;
            ctx.stroke();
            ctx.closePath();
            ctx.lineWidth = 1;
            //Away penalty point
            ctx.beginPath();
            ctx.arc(canvas.width - 88, canvas.height / 2, 1, 0, 2 * Math.PI, true);
            ctx.fill();
            ctx.closePath();
            //Away half circle
            ctx.beginPath();
            ctx.arc(canvas.width - 88, canvas.height / 2, 73, 0.71 * Math.PI, 1.29 * Math.PI, false);
            ctx.stroke();
            ctx.closePath();

            //Home L corner
            ctx.beginPath();
            ctx.arc(0, 0, 8, 0, 0.5 * Math.PI, false);
            ctx.stroke();
            ctx.closePath();
            //Home R corner
            ctx.beginPath();
            ctx.arc(0, canvas.height, 8, 0, 2 * Math.PI, true);
            ctx.stroke();
            ctx.closePath();
            //Away R corner
            ctx.beginPath();
            ctx.arc(canvas.width, 0, 8, 0.5 * Math.PI, Math.PI, false);
            ctx.stroke();
            ctx.closePath();
            //Away L corner
            ctx.beginPath();
            ctx.arc(canvas.width, canvas.height, 8, Math.PI, 1.5 * Math.PI, false);
            ctx.stroke();
            ctx.closePath();
        }
    };

    var ball = {
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        draw: function () {
            ctx.beginPath();
            ctx.arc(this.x, this.y, 3, 0, 2 * Math.PI, false);
            ctx.fillStyle = "#FF0";
            ctx.fill();
            ctx.strokeStyle = "#000";
            ctx.stroke();
            ctx.closePath();
        }
    };

    var Player = function (x, y, team, name) {
        this.x = x;
        this.y = y;
        this.team = team || "home";
        this.name = name || "noname";
    };

    Player.prototype.draw = function () {
        ctx.beginPath();
        ctx.arc(this.x, this.y, 5, 0, 2 * Math.PI, false);
        ctx.fillStyle = ((this.team === "home") ? "#00F" : "#F00");
        ctx.fill();
        ctx.strokeStyle = "#000";
        ctx.stroke();
        ctx.fillStyle = "#FFF";
        ctx.fillText(this.name, this.x + 5, this.y - 5);
        ctx.closePath();
    };

    window.onkeydown = function (e) {
        var send = false;
        if (e.keyCode == 37 && moveX == 0) {
            moveX = -speed;
            send = true;
        }

        if (e.keyCode == 38 && moveY == 0) {
            moveY = -speed;
            send = true;
        }

        if (e.keyCode == 39 && moveX == 0) {
            moveX = speed;
            send = true;
        }

        if (e.keyCode == 40 && moveY == 0) {
            moveY = speed;
            send = true;
        }

        if (e.keyCode == 81) {
            ws.send(JSON.stringify({
                'command': 'pass'
            }))
        }

        if (e.keyCode == 87) {
            ws.send(JSON.stringify({
                'command': 'goal'
            }))
        }

        if (e.keyCode == 13) {
            document.getElementById('msg-btn').onclick();
        }

        if (send) {
            ws.send(JSON.stringify({
                'command': 'move',
                'moveX': moveX,
                'moveY': moveY
            }))
        }
    };

    window.onkeyup = function (e) {
        var send = false;
        if (e.keyCode == 37) {
            moveX = 0;
            send = true;
        }

        if (e.keyCode == 38) {
            moveY = 0;
            send = true;
        }

        if (e.keyCode == 39) {
            moveX = 0;
            send = true;
        }

        if (e.keyCode == 40) {
            moveY = 0;
            send = true;
        }

        if (e.keyCode == 192) {
            document.getElementById('msg').focus();
        }

        if (send) {
            ws.send(JSON.stringify({
                'command': 'move',
                'moveX': moveX,
                'moveY': moveY
            }))
        }
    };

    document.getElementById('msg-btn').onclick = function () {
        var msg = document.getElementById('msg').value;
        if (msg) {
            ws.send(JSON.stringify({
                'command': 'msg',
                'msg': msg
            }));
            document.getElementById('msg').value = '';
        }
    };

    document.getElementById('create-game').onclick = function () {
        ws.send(JSON.stringify({
            'command': 'create'
        }))
    };

    document.getElementById('start-game').onclick = function () {
        ws.send(JSON.stringify({
            'command': 'start'
        }))
    };

    document.getElementById('pause-game').onclick = function () {
        ws.send(JSON.stringify({
            'command': 'pause'
        }))
    };

    document.getElementById('stop-game').onclick = function () {
        ws.send(JSON.stringify({
            'command': 'stop'
        }))
    };

    document.getElementById('join-game').onclick = function () {
        ws.send(JSON.stringify({
            'command': 'join'
        }))
    };

    document.getElementById('leave-game').onclick = function () {
        ws.send(JSON.stringify({
            'command': 'leave'
        }))
    };

    document.getElementById('save-name').onclick = function () {
        ws.send(JSON.stringify({
            'command': 'save-name',
            'name': document.getElementById('name').value
        }))
    };
})();