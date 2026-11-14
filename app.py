import http.server
import socketserver
import json
import datetime
import os
import time

PORT = int(os.environ.get("PORT", 8080))
messages = []
users = {}

HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Мессенджер v26.0</title>
<style>
:root { --bg: #0d1117; --panel: #161b22; --text: #c9d1d9; --border: #30363d; --accent: #58a6ff; --green: #238636; }
.light-theme { --bg: #f0f2f5; --panel: #ffffff; --text: #000000; --border: #ccc; --accent: #007bff; }
html, body { margin: 0; padding: 0; width: 100%; height: 100%; background: var(--bg); color: var(--text); font-family: sans-serif; overflow: hidden; display: flex; flex-direction: column; transition: 0.3s; }
#auth-screen { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 20px; box-sizing: border-box; overflow-y: auto; }
.auth-box { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 25px; width: 100%; max-width: 350px; }
input { width: 100%; padding: 12px; margin-bottom: 12px; background: var(--bg); color: var(--text); border: 1px solid var(--border); border-radius: 6px; box-sizing: border-box; outline: none; }
button { width: 100%; padding: 12px; background: var(--green); color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; }
.avatar-upload { text-align: center; margin-bottom: 15px; }
.avatar-preview { width: 80px; height: 80px; border-radius: 50%; border: 2px solid var(--border); object-fit: cover; margin-bottom: 10px; display: none; background: #000; }
.upload-btn { background: var(--border); color: white; padding: 8px; border-radius: 6px; cursor: pointer; display: inline-block; font-size: 14px; margin-bottom: 10px; }
#main-screen { display: none; flex-direction: column; height: 100%; position: relative; }
.tab-content { flex-grow: 1; overflow-y: auto; display: none; padding-bottom: 60px; }
.tab-content.active { display: block; }
.contact { padding: 15px; border-bottom: 1px solid var(--border); cursor: pointer; display: flex; align-items: center; gap: 15px; }
.contact img { width: 45px; height: 45px; border-radius: 50%; }
.contact-info { display: flex; flex-direction: column; flex-grow: 1; }
.contact-name { font-weight: bold; font-size: 16px; }
.contact-sub { font-size: 12px; color: #888; }
.profile-view { text-align: center; padding: 40px 20px; }
.profile-view img { width: 120px; height: 120px; border-radius: 50%; border: 3px solid var(--accent); object-fit: cover; margin-bottom: 20px; }
#bottom-nav { position: absolute; bottom: 0; left: 0; width: 100%; background: var(--panel); border-top: 1px solid var(--border); display: flex; justify-content: space-around; padding: 10px 0; z-index: 20; }
.nav-item { display: flex; flex-direction: column; align-items: center; color: #888; cursor: pointer; font-size: 12px; }
.nav-item.active { color: var(--accent); }
.nav-item span { font-size: 20px; margin-bottom: 2px; }
#chat-screen { display: none; flex-direction: column; height: 100%; position: absolute; top: 0; left: 0; width: 100%; background: var(--bg); z-index: 30; }
#chat-header { padding: 10px 15px; border-bottom: 1px solid var(--border); background: var(--panel); display: flex; align-items: center; gap: 15px; }
#chat-box { flex-grow: 1; overflow-y: scroll; padding: 15px; display: flex; flex-direction: column; gap: 10px; }
.msg { display: flex; gap: 10px; max-width: 90%; }
.msg.mine { align-self: flex-end; flex-direction: row-reverse; }
.msg img { width: 30px; height: 30px; border-radius: 50%; }
.msg-content { background: var(--panel); padding: 8px 12px; border-radius: 10px; border: 1px solid var(--border); }
.msg.mine .msg-content { background: #1f6feb; color: white; }
.msg-name { font-size: 11px; color: var(--accent); font-weight: bold; }
#bottom-bar { background: var(--panel); padding: 10px; border-top: 1px solid var(--border); display: flex; gap: 10px; }
#msg-input { margin-bottom: 0; flex-grow: 1; }
.settings-section { background: var(--panel); margin: 15px; border-radius: 10px; overflow: hidden; }
.settings-item { padding: 15px; display: flex; align-items: center; gap: 15px; border-bottom: 1px solid var(--border); cursor: pointer; }
.settings-icon { width: 35px; height: 35px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.settings-text { display: flex; flex-direction: column; flex-grow: 1; }
.settings-title { font-size: 16px; }
.settings-desc { font-size: 12px; color: #888; }
</style>
</head>
<body>
<div id="auth-screen">
<div class="auth-box">
<h2 style="text-align:center;">Вход в чат</h2>
<div class="avatar-upload">
<img id="avatar-preview" class="avatar-preview" src="">
<label for="avatar-file" class="upload-btn">📷 Выбрать фото</label>
<input type="file" id="avatar-file" accept="image/*" style="display:none;" onchange="previewAvatar(event)">
</div>
<input type="text" id="auth-nick" placeholder="Ваш Ник">
<input type="number" id="auth-age" placeholder="Ваш Возраст">
<button onclick="doAuth()">Войти</button>
</div>
</div>

<div id="main-screen">
<div id="tab-chats" class="tab-content active">
<div style="padding:15px; font-weight:bold; font-size:18px;">Чаты</div>
<div id="contact-list">
<div class="contact" onclick="openChat('GENERAL')">
<div style="width:45px;height:45px;background:#5865F2;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px;">🌐</div>
<div class="contact-info"><div class="contact-name">Общий чат</div><div class="contact-sub">Писать всем</div></div>
</div>
</div>
</div>
<div id="tab-account" class="tab-content">
<div class="profile-view">
<img id="account-avatar" src="">
<h1 id="account-nick"></h1>
<p id="account-age"></p>
</div>
</div>
<div id="tab-settings" class="tab-content">
<div style="padding:15px; font-weight:bold; font-size:22px;">Настройки</div>
<div class="settings-section">
<div class="settings-item" onclick="toggleTheme()">
<div class="settings-icon" style="background:#e0a000;">🎨</div>
<div class="settings-text"><div class="settings-title">Сменить тему</div><div class="settings-desc">Тёмная / Светлая</div></div>
</div>
</div>
<div class="settings-section">
<div class="settings-item" onclick="logout()">
<div class="settings-icon" style="background:#888;">🚪</div>
<div class="settings-text"><div class="settings-title" style="color:#f85149;">Выйти</div></div>
</div>
</div>
</div>
<div id="bottom-nav">
<div class="nav-item active" onclick="switchTab('chats', this)"><span>💬</span>Чаты</div>
<div class="nav-item" onclick="switchTab('account', this)"><span>👤</span>Аккаунт</div>
<div class="nav-item" onclick="switchTab('settings', this)"><span>⚙️</span>Настройки</div>
</div>
</div>

<div id="chat-screen">
<div id="chat-header">
<button onclick="closeChat()" style="width:auto; padding:5px 10px; background:var(--border); color:white;">←</button>
<div id="chat-title" style="font-weight:bold;">Общий чат</div>
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
let currentAvatarBase64 = "";

window.onload = function() {
    let saved = localStorage.getItem('chatUser');
    if (saved) { myData = JSON.parse(saved); enterChat(); }
    if(localStorage.getItem('theme') === 'light') document.body.classList.add('light-theme');
};

function previewAvatar(event) {
    const file = event.target.files[0]; if (!file) return;
    const reader = new FileReader();
    reader.onload = function(e) {
        const img = new Image();
        img.onload = function() {
            const canvas = document.createElement('canvas');
            canvas.width = 150; canvas.height = 150;
            const ctx = canvas.getContext('2d');
            const minSize = Math.min(img.width, img.height);
            ctx.drawImage(img, (img.width-minSize)/2, (img.height-minSize)/2, minSize, minSize, 0, 0, 150, 150);
            currentAvatarBase64 = canvas.toDataURL('image/jpeg', 0.7);
            let preview = document.getElementById('avatar-preview');
            preview.src = currentAvatarBase64; preview.style.display = 'block';
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

function doAuth() {
    const nick = document.getElementById('auth-nick').value.trim();
    const age = document.getElementById('auth-age').value.trim();
    if (!nick || !age) return alert("Заполните ник и возраст!");
    let avatar = currentAvatarBase64 || `https://ui-avatars.com/api/?name=${nick}&background=random&color=fff`;
    myData = { nick, age, avatar };
    localStorage.setItem('chatUser', JSON.stringify(myData));
    enterChat();
}

function enterChat() {
    document.getElementById('auth-screen').style.display = 'none';
    document.getElementById('main-screen').style.display = 'flex';
    document.getElementById('account-avatar').src = myData.avatar;
    document.getElementById('account-nick').innerText = myData.nick;
    document.getElementById('account-age').innerText = "Возраст: " + myData.age;
    fetch('/join', { method: 'POST', body: JSON.stringify(myData) });
    setInterval(fetchMsgs, 1000);
}

function logout() { localStorage.removeItem('chatUser'); location.reload(); }

function toggleTheme() {
    document.body.classList.toggle('light-theme');
    localStorage.setItem('theme', document.body.classList.contains('light-theme') ? 'light' : 'dark');
}

function switchTab(tabId, element) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.getElementById('tab-' + tabId).classList.add('active');
    element.classList.add('active');
}

function openChat(username) {
    document.getElementById('main-screen').style.display = 'none';
    document.getElementById('chat-screen').style.display = 'flex';
    lastMsgCount = 0;
}

function closeChat() {
    document.getElementById('chat-screen').style.display = 'none';
    document.getElementById('main-screen').style.display = 'flex';
}

function fetchMsgs() {
    fetch('/data').then(r => r.json()).then(data => {
        if (data.msgs.length !== lastMsgCount) {
            const box = document.getElementById('chat-box');
            box.innerHTML = '';
            data.msgs.forEach(m => {
                const isMine = m.nick === myData.nick && m.age === myData.age;
                box.innerHTML += `<div class="msg ${isMine ? 'mine' : ''}"><img src="${m.avatar}"><div class="msg-content"><div class="msg-name">${m.nick} (${m.age})</div><div>${m.text}</div></div></div>`;
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
            messages.append({"nick": d['nick'], "age": d['age'], "avatar": d['avatar'], "text": d['text']})
        self.send_response(200); self.end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print("Сервер v26.0 запущен")
        httpd.serve_forever()
