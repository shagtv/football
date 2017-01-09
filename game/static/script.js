$(function () {
    var speed = 3;
    var moveX = 0;
    var moveY = 0;

    var players = [];
    var ws = new WebSocket("ws://shagtv.net:8000/ws");
    var mode;
    var gameId;

    setInterval(function() {
        if (mode === 'list') {
            ws.send(JSON.stringify({
            'command': 'game-list'
        }));
        }
    }, 1000);

    setInterval(function() {
        if (mode === 'game') {
            ws.send(JSON.stringify({
            'command': 'game-info',
            'id': gameId
        }));
        }
    }, 50);

    ws.onmessage = function (evt) {
        var data = JSON.parse(evt.data);
        if (data['command'] == 'draw') {
            pitch.draw();

            data['players'].forEach(function(data) {
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
            $('#result-home').html(data['result']['home']);
            $('#result-guest').html(data['result']['guest']);
            $('#ccu').html(data['ccu']);
        } else if (data['command'] == 'msg') {
            var html = '<p><strong>' + data['author'] + '</strong> (' + data['dt'] + '): ';
            html += data['msg'] + '</p>';
            console.log(data);
            console.log(html);
            $('#msgs').html(html + $('#msgs').html())
        } else if (data['command'] == 'game-list') {
            var html = '';
            data['games'].forEach(function (game) {
                html += '<p>';
                html += game[0] + ' (created: ' + game[1] + ') ';
                html += '' + game[2]['home'] + ':' + game[2]['guest'] + ' ';
                html += '<button class="game-open" data-id="' + game[0] + '">Open</button>';
                html += '</p>';
            });
            $('#games-block').html(html);
        }
    };

    ws.onopen = function () {
        console.log('open');
        var name = '' + parseInt(Math.random() * 100) + '*';
        $('#name').val(name);
        ws.send(JSON.stringify({
            'command': 'save-name',
            'name': name,
            'first': true
        }));

        mode = 'list'
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
                'command': 'pass',
                'id': gameId
            }))
        }

        if (e.keyCode == 87) {
            ws.send(JSON.stringify({
                'command': 'goal',
                'id': gameId
            }))
        }

        if (e.keyCode == 13) {
            $('#msg-btn').click();
        }

        if (send) {
            ws.send(JSON.stringify({
                'command': 'move',
                'moveX': moveX,
                'moveY': moveY,
                'id': gameId
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
            $('#msg').focus();
        }

        if (send) {
            ws.send(JSON.stringify({
                'command': 'move',
                'moveX': moveX,
                'moveY': moveY,
                'id': gameId
            }))
        }
    };

    $('#msg-btn').on('click', function () {
        var msg = document.getElementById('msg').value;
        if (msg) {
            ws.send(JSON.stringify({
                'command': 'msg',
                'msg': msg
            }));
            $('#msg').val('');
        }
    });

    $('#game-list').on('click', function () {
        gameId = undefined;
        mode = 'list';
        $('#pitch').hide();
        $('#result-block').hide();
        $('#games-block').show();
        $('#game-list').hide();
        $('#game-buttons').hide();
    });

   $('#games-block').on('click', '.game-open', function () {
        gameId = $(this).data('id');
        mode = 'game';
        $('#pitch').show();
        $('#result-block').show();
        $('#game-list').show();
        $('#games-block').hide();
        $('#game-buttons').show();
    });

   $('.game-command').on('click', function () {
        ws.send(JSON.stringify({
            'command': $(this).data('command'),
            'id': gameId
        }))
    });

   $('#game-create').on('click', function () {
        ws.send(JSON.stringify({
            'command': 'create'
        }))
    });

    $('#save-name').on('click', function () {
        ws.send(JSON.stringify({
            'command': 'save-name',
            'name': $('#name').val()
        }))
    });
});
