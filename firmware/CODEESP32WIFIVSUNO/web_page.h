#pragma once
// Separate HTML avoids Arduino generating C++ prototypes from JavaScript.
static const char YEAR2_WEB_PAGE[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Robot IK XYZ Control</title>

  <style>
    body {
      font-family: Arial;
      text-align: center;
      background: #f2f2f2;
      user-select: none;
      margin: 0;
      padding: 10px;
    }

    h2 {
      margin-top: 15px;
    }

    input {
      width: 80px;
      height: 35px;
      font-size: 18px;
      margin: 5px;
      text-align: center;
    }

    button {
      width: 110px;
      height: 50px;
      margin: 6px;
      font-size: 18px;
      border-radius: 10px;
      border: none;
      background: #1976d2;
      color: white;
    }

    .stop {
      background: #d32f2f;
      width: 230px;
    }

    .home {
      background: #388e3c;
    }

    .statusBox {
      background: white;
      border-radius: 12px;
      padding: 12px;
      margin: 12px auto;
      max-width: 680px;
      box-shadow: 0 0 8px #ccc;
      text-align: left;
      font-size: 16px;
    }

    .value {
      font-weight: bold;
      color: #d32f2f;
    }

    .small {
      font-size: 13px;
      color: #555;
      word-break: break-word;
    }

    .axisBox {
      display: inline-block;
      background: #eeeeee;
      border-radius: 10px;
      padding: 10px;
      margin: 5px;
      min-width: 130px;
    }
  </style>
</head>

<body>
  <h2>Robot Arm IK XYZ Control</h2>

  <div class="statusBox">
    <h3>AS5600 Encoder</h3>

    <div class="axisBox">
      BASE<br>
      <span id="baseAngle" class="value">---</span>
    </div>

    <div class="axisBox">
      LOW joint<br>
      <span id="lowJoint" class="value">---</span>
    </div>

    <div class="axisBox">
      HIGH joint<br>
      <span id="highJoint" class="value">---</span>
    </div>

    <p class="small">
      Angle line:<br>
      <span id="angleLine">---</span>
    </p>

    <p class="small">
      Raw encoder line:<br>
      <span id="encRaw">---</span>
    </p>

    <p class="small">
      Last Uno line:<br>
      <span id="unoLine">---</span>
    </p>

    <p class="small">
      Last command sent:
      <span id="lastCmd">---</span>
    </p>

    <p class="small">
      Data age:
      <span id="ageMs">---</span> ms
    </p>
  </div>

  <button class="home" onclick="sendLine('G28')">G28 HOME</button>
  <button class="home" onclick="sendLine('G90')">G90 ABS</button>
  <button class="home" onclick="sendLine('M114')">SHOW STATUS</button>

  <hr>

  <h3>Move XYZ</h3>

  X: <input id="x" value="0"><br>
  Y: <input id="y" value="174"><br>
  Z: <input id="z" value="120"><br>
  F: <input id="f" value="20"><br>

  <button onclick="moveXYZ()">MOVE XYZ</button>

  <hr>

  <h3>Quick positions</h3>

  <button onclick="sendLine('G1 X0 Y174 Z120 F20')">HOME POS</button>
  <button onclick="sendLine('G1 X40 Y160 Z100 F20')">P1</button>
  <button onclick="sendLine('G1 X-40 Y160 Z100 F20')">P2</button>
  <button onclick="sendLine('G1 X0 Y200 Z80 F20')">P3</button>

  <hr>

  <h3>Manual Jog</h3>

  <button
    onmousedown="sendKey('q')" onmouseup="sendKey('x')"
    ontouchstart="touchSend(event,'q')" ontouchend="touchSend(event,'x')">Y+</button><br>

  <button
    onmousedown="sendKey('a')" onmouseup="sendKey('x')"
    ontouchstart="touchSend(event,'a')" ontouchend="touchSend(event,'x')">Z+</button>

  <button
    onmousedown="sendKey('w')" onmouseup="sendKey('x')"
    ontouchstart="touchSend(event,'w')" ontouchend="touchSend(event,'x')">X+</button>

  <button
    onmousedown="sendKey('d')" onmouseup="sendKey('x')"
    ontouchstart="touchSend(event,'d')" ontouchend="touchSend(event,'x')">Z-</button><br>

  <button
    onmousedown="sendKey('e')" onmouseup="sendKey('x')"
    ontouchstart="touchSend(event,'e')" ontouchend="touchSend(event,'x')">Y-</button><br>

  <button
    onmousedown="sendKey('s')" onmouseup="sendKey('x')"
    ontouchstart="touchSend(event,'s')" ontouchend="touchSend(event,'x')">X-</button><br>

  <button class="stop" onclick="sendKey('x')">STOP</button>

<script>
function sendLine(line) {
  fetch('/gcode?line=' + encodeURIComponent(line), {method: 'POST'})
    .catch(err => console.log(err));
}

function sendKey(key) {
  fetch('/key?val=' + encodeURIComponent(key), {method: 'POST'})
    .catch(err => console.log(err));
}

function touchSend(event, key) {
  event.preventDefault();
  sendKey(key);
}

function moveXYZ() {
  let x = document.getElementById('x').value;
  let y = document.getElementById('y').value;
  let z = document.getElementById('z').value;
  let f = document.getElementById('f').value;

  let line = 'G1 X' + x + ' Y' + y + ' Z' + z + ' F' + f;
  sendLine(line);
}

function updateStatus() {
  fetch('/status')
    .then(response => response.json())
    .then(data => {
      document.getElementById('encRaw').innerText = data.encoder;
      document.getElementById('angleLine').innerText = data.angle;
      document.getElementById('unoLine').innerText = data.uno;
      document.getElementById('lastCmd').innerText = data.cmd;
      document.getElementById('ageMs').innerText = data.age_ms;

      let angle = data.angle;

      if (angle && angle.startsWith('A,')) {
        let p = angle.split(',');

        if (p.length >= 4) {
          document.getElementById('baseAngle').innerText = p[1];
          document.getElementById('lowJoint').innerText = p[2];
          document.getElementById('highJoint').innerText = p[3];
        }
      }
    })
    .catch(err => {
      console.log(err);
    });
}

setInterval(updateStatus, 200);
updateStatus();
</script>

</body>
</html>
)rawliteral";
