import http.server
import socketserver
import json
import datetime
import os

PORT = int(os.environ.get("PORT", 8080))
PASSWORD = "1234" 
ADMIN_CODE = "1541"
messages = []
online_users = set()
typing_users = set()

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Чат</title>
    <style>
        :root { --bg: #0d1117; --panel: #111; --text: #888; --border: #555; --input-bg: #000; --input-text: #ccc; --name: #ccc; --time: #555; }
        .light-theme { --bg: #f4f4f9; --panel: #fff; --text: #333; --border: #ccc; --input-bg: #fff; --input-text: #000; --name: #000; --time: #888; }
        html, body { margin: 0; padding: 0; width: 100%; height: 100%; background-color: var(--bg); color: var(--text); font-family: 'Courier New', Courier, monospace; overflow: hidden; transition: 0.3s; }
        #login-screen { display: flex; flex-direction: column; gap: 15px; margin: 20px; border: 1px solid var(--border); padding: 20px; border-radius: 5px; background-color: var(--panel); }
        input, textarea, select { padding: 10px; background-color: var(--input-bg); color: var(--input-text); border: 1px solid var(--border); border-radius: 5px; font-family: inherit; font-size: 16px; }
        textarea { resize: none; height: 60px; }
        button { padding: 12px; background-color: var(--border); color: var(--input-text); border: none; border-radius: 5px; font-weight: bold; cursor: pointer; font-size: 16px; }
        #chat-screen { display: none; flex-direction: column; height: 100%; }
        #header { border-bottom: 1px solid var(--border); padding: 10px; background-color: var(--panel); display: flex; justify-content: space-between; align-items: center; font-size: 14px; flex-shrink: 0; }
        #chat-box { flex-grow: 1; overflow-y: scroll; padding: 10px; }
        .msg { margin-bottom: 10px; display: flex; gap: 10px; align-items: flex-start; padding: 5px; border-radius: 5px; }
        .avatar { width: 30px; height: 30px; border-radius: 50%; border: 1px solid var(--border); object-fit: cover; }
        .msg-content { flex-grow: 1; }
        .time { color: var(--time); font-size: 0.8em; }
        .user-name { font-weight: bold; }
        .name-admin { color: #ff3333; text-shadow: 0 0 5px #ff3333; }
        .name-mod { color: #00ff00; }
        .name-user { color: var(--name); }
        .chat-image { max-width: 200px; max-height: 200px; border-radius: 5px; margin-top: 5px; display: block; }
        .bottom-panel { flex-shrink: 0; background-color: var(--panel); border-top: 1px solid var(--border); padding: 5px 10px 10px 10px; }
        .stickers { display: flex; gap: 5px; margin-bottom: 5px; }
        .sticker { font-size: 24px; cursor: pointer; opacity: 0.7; }
        #input-area { display: flex; gap: 5px; align-items: center; }
        #msg-input { flex-grow: 1; background-color: var(--input-bg); color: var(--input-text); border: 1px solid var(--border); }
        #file-input { display: none; }
        .attach-btn { cursor: pointer; font-size: 24px; padding: 5px; background: var(--panel); border-radius: 5px; border: 1px solid var(--border); }
        #typing-indicator { font-size: 12px; color: #00ff00; height: 15px; margin-bottom: 5px; }
        .admin-btn { background-color: #ff3333; color: white; padding: 5px 10px; font-size: 12px; margin-left: 10px; }
    </style>
</head>
<body>
    <div id="login-screen">
        <h2>=== ВХОД ===</h2>
        <input type="text" id="nickname" placeholder="Ваш ник" maxlength="15">
        <input type="number" id="age" placeholder="Возраст (до 100)" min="1" max="100">
        <select id="role">
            <option value="user">Рядовой</option>
            <option value="mod">Модератор</option>
            <option value="admin">АДМИН</option>
        </select>
        <input type="password" id="admin_code" placeholder="Секретный код">
        <input type="password" id="password" placeholder="Пароль (1234)">
        <input type="text" id="avatar" placeholder="Ссылка на аватарку">
        <textarea id="bio" placeholder="О себе"></textarea>
        <button onclick="login()">ВОЙТИ</button>
    </div>

    <div id="chat-screen">
        <div id="header">
            <div style="display:flex; align-items:center; gap:10px;">
                <img id="my-avatar" class="avatar" src="" style="display:none;">
                <span>Пилот: <span id="display-nick"></span></span>
            </div>
            <div style="text-align:right;">
                <div style="color:#00ff00; font-weight:bold;">Онлайн: <span id="online-count">0</span></div>
                <div style="font-size:12px;">Время: <span id="timer">00:00:00</span> 
                    <button onclick="toggleTheme()" style="padding:2px 5px; font-size:10px; margin-left:5px;">Тема</button>
                    <button id="clear-btn" class="admin-btn" style="display:none;" onclick="clearChat()">Очистить</button>
                </div>
            </div>
        </div>
        <div id="chat-box"></div>
        <div class="bottom-panel">
            <div id="typing-indicator"></div>
            <div class="stickers">
                <span class="sticker" onclick="addSticker('🚀')">🚀</span>
                <span class="sticker" onclick="addSticker('🔥')">🔥</span>
                <span class="sticker" onclick="addSticker('😎')">😎</span>
                <span class="sticker" onclick="addSticker('👽')">👽</span>
            </div>
            <div id="input-area">
                <label for="file-input" class="attach-btn">📎</label>
                <input type="file" id="file-input" accept="image/*" onchange="uploadImage(event)">
                <input type="text" id="msg-input" placeholder="Сообщение..." oninput="notifyTyping()">
                <button onclick="sendMsg()">➤</button>
            </div>
        </div>
    </div>

    <script>
        let myNick = "", myAge = "", myBio = "", myAvatar = "", myRole = "user";
        let startTime = 0, lastMessageCount = 0, typingTimeout;

        function playBeep() {
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            if (audioCtx.state === 'suspended') audioCtx.resume();
            const osc = audioCtx.createOscillator(), gain = audioCtx.createGain();
            osc.type = 'sine'; osc.frequency.setValueAtTime(800, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.start(); osc.stop(audioCtx.currentTime + 0.1);
        }

        function toggleTheme() { document.body.classList.toggle('light-theme'); }

        function login() {
            myNick = document.getElementById('nickname').value.trim();
            myAge = document.getElementById('age').value.trim();
            myBio = document.getElementById('bio').value.trim();
            myAvatar = document.getElementById('avatar').value.trim();
            let selectedRole = document.getElementById('role').value;
            const adminCode = document.getElementById('admin_code').value.trim();
            const pass = document.getElementById('password').value.trim();

            if (selectedRole === 'admin' && adminCode !== '1541') { alert("Неверный код!"); return; }
            myRole = selectedRole;

            fetch('/check_pass', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ pass: pass }) })
            .then(r => {
                if(r.ok) {
                    document.getElementById('login-screen').style.display = 'none';
                    document.getElementById('chat-screen').style.display = 'flex';
                    document.getElementById('display-nick').innerText = myNick;
                    if (myRole === 'admin') document.getElementById('clear-btn').style.display = 'inline-block';
                    startTime = Date.now();
                    setInterval(updateTimer, 1000);
                    fetchMessages();
                    setInterval(fetchMessages, 1500);
                } else { alert("Неверный пароль!"); }
            });
        }

        function updateTimer() {
            const diff = Math.floor((Date.now() - startTime) / 1000);
            document.getElementById('timer').innerText = `${String(Math.floor(diff/3600)).padStart(2,'0')}:${String(Math.floor((diff%3600)/60)).padStart(2,'0')}:${String(diff%60).padStart(2,'0')}`;
        }

        function addSticker(emoji) { document.getElementById('msg-input').value += emoji; }

        function notifyTyping() {
            fetch('/typing', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ user: myNick }) });
            clearTimeout(typingTimeout);
            typingTimeout = setTimeout(() => { fetch('/stop_typing', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ user: myNick }) }); }, 2000);
        }

        function fetchMessages() {
            fetch('/get_messages').then(r => r.json()).then(data => {
                document.getElementById('online-count').innerText = data.online;
                let typingList = data.typing.filter(u => u !== myNick);
                document.getElementById('typing-indicator').innerText = typingList.length > 0 ? typingList.join(", ") + " печатает..." : "";
                if (data.messages.length !== lastMessageCount) {
                    if (data.messages.length > lastMessageCount && lastMessageCount !== 0) playBeep();
                    const box = document.getElementById('chat-box');
                    box.innerHTML = '';
                    data.messages.forEach((m) => {
                        let avatarImg = m.avatar ? `<img src="${m.avatar}" class="avatar">` : `<div class="avatar" style="background:#222;"></div>`;
                        let msgBody = m.image ? `<br><img src="${m.image}" class="chat-image">` : m.text;
                        let nameClass = m.role === 'admin' ? 'name-admin' : m.role === 'mod' ? 'name-mod' : 'name-user';
                        box.innerHTML += `<div class="msg"><div>${avatarImg}</div><div class="msg-content"><span class="time">[${m.time}]</span> <span class="user-name ${nameClass}">${m.user}:</span> ${msgBody}</div></div>`;
                    });
                    box.scrollTop = box.scrollHeight;
                    lastMessageCount = data.messages.length;
                }
            });
        }

        function sendMsg() {
            const text = document.getElementById('msg-input').value.trim();
            if (text === '') return;
            fetch('/send_message', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ user: myNick, text: text, avatar: myAvatar, role: myRole }) })
            .then(() => { document.getElementById('msg-input').value = ''; fetchMessages(); });
        }

        function uploadImage(event) {
            const file = event.target.files[0]; if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = new Image();
                img.onload = function() {
                    const canvas = document.createElement('canvas'), MAX_WIDTH = 400, scale = MAX_WIDTH / img.width;
                    canvas.width = MAX_WIDTH; canvas.height = img.height * scale;
                    const ctx = canvas.getContext('2d'); ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                    const base64Image = canvas.toDataURL('image/jpeg', 0.7);
                    fetch('/send_image', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ user: myNick, image: base64Image, role: myRole }) }).then(() => fetchMessages());
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }

        function clearChat() {
            if (confirm("Удалить все сообщения?")) fetch('/clear_chat', { method: 'POST' }).then(() => { lastMessageCount = 0; fetchMessages(); });
        }

        document.getElementById('msg-input').addEventListener('keypress', function (e) { if (e.key === 'Enter') sendMsg(); });
    </script>
</body>
</html>
"""

class ChatHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        elif self.path == '/get_messages':
            self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
            self.wfile.write(json.dumps({"messages": messages, "online": len(online_users), "typing": list(typing_users)}).encode('utf-8'))
        else: self.send_error(404)
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        if self.path == '/check_pass':
            if json.loads(post_data)['pass'] == PASSWORD: self.send_response(200); self.end_headers()
            else: self.send_response(403); self.end_headers()
        elif self.path == '/send_message':
            data = json.loads(post_data)
            messages.append({"user": data['user'], "text": data['text'], "avatar": data.get('avatar', ''), "time": datetime.datetime.now().strftime("%H:%M"), "image": None, "role": data.get('role', 'user')})
            self.send_response(200); self.end_headers()
        elif self.path == '/send_image':
            data = json.loads(post_data)
            messages.append({"user": data['user'], "text": "Фото", "avatar": "", "time": datetime.datetime.now().strftime("%H:%M"), "image": data['image'], "role": data.get('role', 'user')})
            self.send_response(200); self.end_headers()
        elif self.path == '/join':
            online_users.add(json.loads(post_data)['user']); self.send_response(200); self.end_headers()
        elif self.path == '/leave':
            online_users.discard(json.loads(post_data)['user']); self.send_response(200); self.end_headers()
        elif self.path == '/typing':
            typing_users.add(json.loads(post_data)['user']); self.send_response(200); self.end_headers()
        elif self.path == '/stop_typing':
            typing_users.discard(json.loads(post_data)['user']); self.send_response(200); self.end_headers()
        elif self.path == '/clear_chat':
            messages.clear(); self.send_response(200); self.end_headers()
        else: self.send_error(404)

if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), ChatHandler) as httpd:
        print("Сервер запущен!")
        httpd.serve_forever()
