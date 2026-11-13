import http.server
import socketserver
import json
import datetime
import os

PORT = int(os.environ.get("PORT", 8080))
messages = []
online_users = {}
ADMIN_CODE = "1541"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Чат</title>
    <style>
        :root { --bg: #0d1117; --panel: #161b22; --text: #c9d1d9; --border: #30363d; --accent: #58a6ff; --green: #238636; }
        html, body { margin: 0; padding: 0; width: 100%; height: 100%; background: var(--bg); color: var(--text); font-family: sans-serif; overflow: hidden; }
        #auth-screen { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 20px; }
        .box { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 25px; width: 100%; max-width: 350px; }
        h2 { margin-top: 0; color: #fff; text-align: center; }
        input { width: 100%; padding: 12px; margin-bottom: 10px; background: var(--bg); color: var(--text); border: 1px solid var(--border); border-radius: 6px; box-sizing: border-box; outline: none; }
        button { width: 100%; padding: 12px; background: var(--green); color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; }
        .toggle-link { text-align: center; margin-top: 15px; font-size: 14px; color: var(--accent); cursor: pointer; }
        
        #main-screen { display: none; flex-direction: column; height: 100%; }
        #top-bar { background: var(--panel); border-bottom: 1px solid var(--border); padding: 10px 15px; display: flex; justify-content: space-between; align-items: center; }
        .my-profile { display: flex; align-items: center; gap: 10px; }
        .my-profile img { width: 40px; height: 40px; border-radius: 50%; border: 2px solid var(--accent); object-fit: cover; }
        
        #chat-box { flex-grow: 1; overflow-y: scroll; padding: 15px; display: flex; flex-direction: column; gap: 10px; }
        .msg { display: flex; gap: 10px; max-width: 85%; }
        .msg.mine { align-self: flex-end; flex-direction: row-reverse; }
        .msg img { width: 35px; height: 35px; border-radius: 50%; object-fit: cover; }
        .msg-content { background: var(--panel); padding: 10px 15px; border-radius: 12px; border: 1px solid var(--border); cursor: pointer; }
        .msg.mine .msg-content { background: #1f6feb; border-color: #1f6feb; color: white; }
        .msg-name { font-size: 12px; color: var(--accent); margin-bottom: 4px; font-weight: bold; }
        .msg.mine .msg-name { color: #c9d1d9; text-align: right; }
        .msg-text { font-size: 15px; word-wrap: break-word; }
        .msg-img { max-width: 200px; border-radius: 8px; margin-top: 5px; display: block; }
        .msg-actions { display: flex; gap: 5px; margin-top: 5px; justify-content: flex-end; }
        .action-btn { background: none; border: none; cursor: pointer; font-size: 16px; padding: 2px; }
        
        #bottom-bar { background: var(--panel); padding: 10px; border-top: 1px solid var(--border); display: flex; gap: 10px; align-items: center; }
        #msg-input { margin-bottom: 0; flex-grow: 1; border-radius: 20px; padding: 10px 15px; }
        .icon-btn { background: none; border: none; color: var(--accent); font-size: 24px; cursor: pointer; }
        .send-btn { background: var(--accent); border: none; color: white; border-radius: 50%; width: 40px; height: 40px; cursor: pointer; }
        #toast { position: fixed; bottom: 80px; left: 50%; transform: translateX(-50%); background: #238636; color: white; padding: 10px 20px; border-radius: 20px; display: none; }
    </style>
</head>
<body>
    <div id="auth-screen">
        <div class="box">
            <h2 id="auth-title">Вход</h2>
            <img id="avatar-preview" style="width: 80px; height: 80px; border-radius: 50%; display: none; margin: 0 auto 10px; border: 2px solid var(--border);">
            <label for="avatar-file" id="avatar-label" style="display:none; cursor:pointer; text-align:center; color:var(--accent); margin-bottom:10px;">📷 Выбрать аватарку</label>
            <input type="file" id="avatar-file" accept="image/*" style="display:none;" onchange="previewAvatar(event)">
            
            <input type="text" id="auth-nick" placeholder="Ваш ник">
            <input type="number" id="auth-age" placeholder="Возраст" style="display:none;">
            <input type="password" id="auth-pass" placeholder="Пароль">
            <input type="password" id="auth-admin-code" placeholder="Секретный код (только для админа)" style="display:none;">
            <button onclick="doAuth()" id="auth-btn">Войти</button>
            <div class="toggle-link" onclick="toggleAuthMode()" id="toggle-text">Нет аккаунта? Зарегистрироваться</div>
        </div>
    </div>

    <div id="main-screen">
        <div id="top-bar">
            <div class="my-profile">
                <img id="my-avatar-img" src="">
                <div>
                    <div style="font-weight: bold; color: #fff;" id="my-nick-display"></div>
                    <div style="font-size: 12px; color: var(--green);" id="my-status">В сети</div>
                </div>
            </div>
            <button onclick="logout()" style="width: auto; padding: 5px 10px; background: var(--border); color: white; border-radius: 5px;">Выйти</button>
        </div>
        <div id="chat-box"></div>
        <div id="bottom-bar">
            <label for="file-input" class="icon-btn">📎</label>
            <input type="file" id="file-input" accept="image/*" style="display: none;" onchange="uploadImage(event)">
            <input type="text" id="msg-input" placeholder="Сообщение..." onkeypress="if(event.key === 'Enter') sendMsg()">
            <button class="send-btn" onclick="sendMsg()">➤</button>
        </div>
    </div>
    <div id="toast"></div>

    <script>
        let isLoginMode = true;
        let myData = null;
        let lastMessageCount = 0;
        let currentAvatarBase64 = "";

        window.onload = function() {
            let saved = localStorage.getItem('chatUser');
            if (saved) { myData = JSON.parse(saved); enterChat(); }
        }

        function toggleAuthMode() {
            isLoginMode = !isLoginMode;
            document.getElementById('auth-title').innerText = isLoginMode ? "Вход" : "Регистрация";
            document.getElementById('auth-btn').innerText = isLoginMode ? "Войти" : "Зарегистрироваться";
            document.getElementById('toggle-text').innerText = isLoginMode ? "Нет аккаунта? Зарегистрироваться" : "Уже есть аккаунт? Войти";
            let display = isLoginMode ? "none" : "block";
            document.getElementById('auth-age').style.display = display;
            document.getElementById('auth-admin-code').style.display = display;
            document.getElementById('avatar-label').style.display = display;
        }

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
                    currentAvatarBase64 = canvas.toDataURL('image/jpeg', 0.8);
                    let preview = document.getElementById('avatar-preview');
                    preview.src = currentAvatarBase64; preview.style.display = 'block';
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }

        function doAuth() {
            const nick = document.getElementById('auth-nick').value.trim();
            const pass = document.getElementById('auth-pass').value.trim();
            if (!nick || !pass) { alert("Введите ник и пароль!"); return; }

            if (isLoginMode) {
                myData = { nick: nick, avatar: `https://ui-avatars.com/api/?name=${nick}&background=random&color=fff`, role: 'user', age: '' };
            } else {
                const age = document.getElementById('auth-age').value.trim();
                const adminCode = document.getElementById('auth-admin-code').value.trim();
                let avatar = currentAvatarBase64 || `https://ui-avatars.com/api/?name=${nick}&background=random&color=fff`;
                let role = (adminCode === '1541') ? 'admin' : 'user';
                myData = { nick: nick, avatar: avatar, role: role, age: age };
            }
            localStorage.setItem('chatUser', JSON.stringify(myData));
            enterChat();
        }

        function logout() { localStorage.removeItem('chatUser'); location.reload(); }

        function enterChat() {
            document.getElementById('auth-screen').style.display = 'none';
            document.getElementById('main-screen').style.display = 'flex';
            document.getElementById('my-nick-display').innerText = myData.nick;
            document.getElementById('my-avatar-img').src = myData.avatar;
            if (myData.role === 'admin') {
                document.getElementById('my-status').innerText = "👑 Админ";
                document.getElementById('my-status').style.color = "#ff3333";
            }
            fetch('/join', { method: 'POST', body: JSON.stringify(myData) });
            setInterval(fetchData, 1000);
        }

        function showToast(text) {
            let t = document.getElementById('toast'); t.innerText = text;
            t.style.display = 'block'; setTimeout(() => { t.style.display = 'none'; }, 2000);
        }

        function copyText(text) { navigator.clipboard.writeText(text).then(() => showToast("Скопировано!")); }
        function reactToMsg(idx) { fetch('/react', { method: 'POST', body: JSON.stringify({ index: idx, reaction: '❤️' }) }); }
        function deleteMsg(idx) { if(confirm("Удалить?")) fetch('/delete', { method: 'POST', body: JSON.stringify({ index: idx }) }); }

        function fetchData() {
            fetch('/data').then(r => r.json()).then(data => {
                if (data.messages.length !== lastMessageCount) {
                    const box = document.getElementById('chat-box');
                    box.innerHTML = '';
                    data.messages.forEach((m, index) => {
                        let isMine = m.nick === myData.nick;
                        let deleteBtn = (myData.role === 'admin') ? `<button class="action-btn" onclick="event.stopPropagation(); deleteMsg(${index})">🗑️</button>` : '';
                        let reactionHtml = m.reaction ? `<div style="font-size:14px;">${m.reaction}</div>` : '';
                        let imgHtml = m.image ? `<img src="${m.image}" class="msg-img">` : '';

                        box.innerHTML += `
                            <div class="msg ${isMine ? 'mine' : ''}">
                                <img src="${m.avatar}">
                                <div class="msg-content" onclick="copyText('${m.text.replace(/'/g, "\\'")}')">
                                    <div class="msg-name">${m.nick} (${m.time})</div>
                                    <div class="msg-text">${m.text}${imgHtml}</div>
                                    ${reactionHtml}
                                    <div class="msg-actions">
                                        <button class="action-btn" onclick="event.stopPropagation(); reactToMsg(${index})">❤️</button>
                                        ${deleteBtn}
                                    </div>
                                </div>
                            </div>`;
                    });
                    box.scrollTop = box.scrollHeight;
                    lastMessageCount = data.messages.length;
                }
            });
        }

        function sendMsg() {
            const text = document.getElementById('msg-input').value.trim();
            if (!text) return;
            fetch('/send', { method: 'POST', body: JSON.stringify({ ...myData, text: text }) })
            .then(() => { document.getElementById('msg-input').value = ''; });
        }

        function uploadImage(event) {
            const file = event.target.files[0]; if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = new Image();
                img.onload = function() {
                    const canvas = document.createElement('canvas');
                    canvas.width = 400; canvas.height = img.height * (400/img.width);
                    const ctx = canvas.getContext('2d'); ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                    fetch('/send', { method: 'POST', body: JSON.stringify({ ...myData, text: "Фото", image: canvas.toDataURL('image/jpeg', 0.7) }) });
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    </script>
</body>
</html>
"""

class ChatHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        elif self.path == '/data':
            self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
            self.wfile.write(json.dumps({"messages": messages}).encode('utf-8'))
        else: self.send_error(404)

    def do_POST(self):
        l = int(self.headers['Content-Length'])
        d = json.loads(self.rfile.read(l).decode())
        if self.path == '/join': online_users[d['nick']] = d
        elif self.path == '/send': messages.append({"nick": d['nick'], "avatar": d['avatar'], "text": d.get('text',''), "image": d.get('image'), "time": datetime.datetime.now().strftime("%H:%M"), "reaction": ""})
        elif self.path == '/react' and 0 <= d['index'] < len(messages): messages[d['index']]['reaction'] = d['reaction']
        elif self.path == '/delete' and 0 <= d['index'] < len(messages): messages.pop(d['index'])
        self.send_response(200); self.end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), ChatHandler) as httpd:
        print("Server started")
        httpd.serve_forever()
