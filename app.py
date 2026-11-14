import http.server
import socketserver
import json
import datetime
import os

PORT = int(os.environ.get("PORT", 8080))
messages = []

HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Мессенджер v24.0</title>
<style>
body { margin:0; padding:0; background:#0d1117; color:#c9d1d9; font-family:sans-serif; height:100vh; display:flex; flex-direction:column; overflow:hidden; }
#auth-screen { display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; padding:20px; box-sizing:border-box; }
.auth-box { background:#161b22; border:1px solid #30363d; border-radius:12px; padding:25px; width:100%; max-width:350px; }
input { width:100%; padding:12px; margin-bottom:12px; background:#0d1117; color:#fff; border:1px solid #30363d; border-radius:6px; box-sizing:border-box; outline:none; }
button { width:100%; padding:12px; background:#238636; color:white; border:none; border-radius:6px; font-size:16px; font-weight:bold; cursor:pointer; }
#main-screen { display:none; flex-direction:column; height:100%; }
#top-bar { background:#161b22; padding:15px; display:flex; justify-content:space-between; border-bottom:1px solid #30363d; }
#chat-box { flex-grow:1; overflow-y:scroll; padding:15px; display:flex; flex-direction:column; gap:10px; }
.msg { display:flex; gap:10px; max-width:90%; }
.msg.mine { align-self:flex-end; flex-direction:row-reverse; }
.msg img { width:35px; height:35px; border-radius:50%; }
.msg-content { background:#161b22; padding:8px 12px; border-radius:10px; border:1px solid #30363d; }
.msg.mine .msg-content { background:#1f6feb; color:white; }
.msg-name { font-size:11px; color:#58a6ff; font-weight:bold; margin-bottom:3px; }
.msg.mine .msg-name { color:#c9d1d9; text-align:right; }
#bottom-bar { background:#161b22; padding:10px; display:flex; gap:10px; border-top:1px solid #30363d; }
#msg-input { flex-grow:1; margin-bottom:0; }
</style>
</head>
<body>
<div id="auth-screen">
<div class="auth-box">
<h2 style="text-align:center;">Вход в чат</h2>
<input type="text" id="auth-nick" placeholder="Ваше Имя (отображается)">
<input type="text" id="auth-username" placeholder="Ваш @username (без @)">
<button onclick="doAuth()">Войти</button>
</div>
</div>

<div id="main-screen">
<div id="top-bar">
<div style="font-weight:bold;" id="my-nick"></div>
<button onclick="logout()" style="width:auto; padding:5px 10px; background:#30363d;">Выйти</button>
</div>
<div id="chat-box"></div>
<div id="bottom-bar">
<input type="text" id="msg-input" placeholder="Сообщение..." onkeypress="if(event.key === 'Enter') sendMsg()">
<button onclick="sendMsg()" style="width:auto; padding:0 15px;">➤</button>
</div>
</div>

<script>
let myData = null;
let lastMsgCount = 0;

window.onload = function() {
    let saved = localStorage.getItem('chatUser');
    if (saved) { myData = JSON.parse(saved); enterChat(); }
};

function doAuth() {
    const nick = document.getElementById('auth-nick').value.trim();
    const username = document.getElementById('auth-username').value.trim().toLowerCase().replace('@', '');
    if (!nick || !username) return alert("Заполните имя и @username!");
    const avatar = `https://ui-avatars.com/api/?name=${nick}&background=random&color=fff`;
    myData = { nick, username, avatar };
    localStorage.setItem('chatUser', JSON.stringify(myData));
    enterChat();
}

function enterChat() {
    document.getElementById('auth-screen').style.display = 'none';
    document.getElementById('main-screen').style.display = 'flex';
    document.getElementById('my-nick').innerText = myData.nick;
    fetch('/join', { method: 'POST', body: JSON.stringify(myData) });
    setInterval(fetchMsgs, 1000);
}

function logout() { localStorage.removeItem('chatUser'); location.reload(); }

function fetchMsgs() {
    fetch('/data').then(r => r.json()).then(data => {
        if (data.msgs.length !== lastMsgCount) {
            const box = document.getElementById('chat-box');
            box.innerHTML = '';
            data.msgs.forEach(m => {
                const isMine = m.username === myData.username;
                box.innerHTML += `<div class="msg ${isMine ? 'mine' : ''}"><img src="${m.avatar}"><div class="msg-content"><div class="msg-name">@${m.username} (${m.nick})</div><div>${m.text}</div></div></div>`;
            });
            box.scrollTop = box.scrollHeight;
            lastMsgCount = data.msgs.length;
        }
    });
}

function sendMsg() {
    const text = document.getElementById('msg-input').value.trim();
    if (!text) return;
    fetch('/send', { method: 'POST', body: JSON.stringify({ ...myData, text }) }).then(() => {
        document.getElementById('msg-input').value = '';
    });
}
</script>
</body>
</html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        elif self.path == '/data':
            self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
            self.wfile.write(json.dumps({"msgs": messages}).encode('utf-8'))
        else: self.send_error(404)

    def do_POST(self):
        l = int(self.headers['Content-Length'])
        d = json.loads(self.rfile.read(l).decode())
        if self.path == '/join':
            pass
        elif self.path == '/send':
            messages.append({"nick": d['nick'], "username": d['username'], "avatar": d['avatar'], "text": d['text']})
        self.send_response(200); self.end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print("Сервер v24.0 запущен")
        httpd.serve_forever()
