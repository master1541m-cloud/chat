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
    <title>Мой Мессенджер</title>
    <style>
        :root { --bg: #0d1117; --panel: #161b22; --text: #c9d1d9; --border: #30363d; --accent: #58a6ff; --green: #238636; }
        html, body { margin: 0; padding: 0; width: 100%; height: 100%; background-color: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; overflow: hidden; }
        
        #auth-screen { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 20px; box-sizing: border-box; overflow-y: auto; }
        .auth-box { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 25px; width: 100%; max-width: 350px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); }
        .auth-box h2 { margin-top: 0; color: #fff; text-align: center; }
        input, select { width: 100%; padding: 12px; margin-bottom: 12px; background: var(--bg); color: var(--text); border: 1px solid var(--border); border-radius: 6px; font-size: 16px; box-sizing: border-box; outline: none; }
        input:focus { border-color: var(--accent); }
        button { width: 100%; padding: 12px; background: var(--green); color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; }
        button:hover { background: #2ea043; }
        .toggle-link { text-align: center; margin-top: 15px; font-size: 14px; color: var(--accent); cursor: pointer; }

        /* Стили для загрузки аватарки */
        .avatar-upload { text-align: center; margin-bottom: 15px; }
        .avatar-preview { width: 80px; height: 80px; border-radius: 50%; border: 2px solid var(--border); object-fit: cover; margin-bottom: 10px; display: none; background: #000; }
        .upload-btn { background: var(--border); color: white; padding: 8px; border-radius: 6px; cursor: pointer; display: inline-block; font-size: 14px; margin-bottom: 10px; }

        #main-screen { display: none; flex-direction: column; height: 100%; }
        #top-bar { background: var(--panel); border-bottom: 1px solid var(--border); padding: 10px 15px; display: flex; justify-content: space-between; align-items: center; }
        .my-profile { display: flex; align-items: center; gap: 10px; }
        .my-profile img { width: 40px; height: 40px; border-radius: 50%; border: 2px solid var(--accent); object-fit: cover; }
        
        #online-list { background: var(--panel); padding: 10px 15px; border-bottom: 1px solid var(--border); display: flex; gap: 15px; overflow-x: auto; white-space: nowrap; }
        .user-circle { display: flex; flex-direction: column; align-items: center; font-size: 11px; gap: 4px; }
        .user-circle img { width: 45px; height: 45px; border-radius: 50%; border: 2px solid var(--border); object-fit: cover; }
        .user-circle.admin img { border-color: #f85149; }

        #chat-box { flex-grow: 1; overflow-y: scroll; padding: 15px; display: flex; flex-direction: column; gap: 10px; }
        .msg { display: flex; gap: 10px; max-width: 85%; }
        .msg.mine { align-self: flex-end; flex-direction: row-reverse; }
        .msg img.avatar { width: 35px; height: 35px; border-radius: 50%; object-fit: cover; }
        .msg-content { background: var(--panel); padding: 10px 15px; border-radius: 12px; border: 1px solid var(--border); position: relative; }
        .msg.mine .msg-content { background: #1f6feb; border-color: #1f6feb; color: white; }
        .msg-name { font-size: 12px; color: var(--accent); margin-bottom: 4px; font-weight: bold; }
        .msg.mine .msg-name { color: #c9d1d9; text-align: right; }
        .msg-text { font-size: 15px; line-height: 1.4; word-wrap: break-word; }
        .msg-img { max-width: 200px; border-radius: 8px; margin-top: 5px; display: block; }

        #bottom-bar { background: var(--panel); padding: 10px; border-top: 1px solid var(--border); display: flex; gap: 10px; align-items: center; }
        #msg-input { margin-bottom: 0; flex-grow: 1; border-radius: 20px; padding: 10px 15px; }
        .icon-btn { background: none; border: none; color: var(--accent); font-size: 24px; cursor: pointer; padding: 5px; display: flex; align-items: center; justify-content: center; }
        .send-btn { background: var(--accent); border: none; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-size: 20px; cursor: pointer; }
    </style>
</head>
<body>
    <div id="auth-screen">
        <div class="auth-box">
            <h2 id="auth-title">Вход</h2>
            
            <!-- Блок загрузки аватарки (только при регистрации) -->
            <div id="avatar-block" class="avatar-upload" style="display:none;">
                <img id="avatar-preview" class="avatar-preview" src="">
                <label for="avatar-file" class="upload-btn">📷 Выбрать фото</label>
                <input type="file" id="avatar-file" accept="image/*" style="display:none;" onchange="previewAvatar(event)">
            </div>

            <input type="text" id="auth-nick" placeholder="Ваш ник">
            <input type="number" id="auth-age" placeholder="Возраст" style="display:none;">
            <input type="password" id="auth-pass" placeholder="Пароль">
            <input type="password" id="auth-admin-code" placeholder="Код админа (если есть)" style="display:none;">
            
            <button onclick="doAuth()" id="auth-btn">Войти</button>
            <div class="toggle-link" onclick="toggleAuthMode()" id="toggle-text">Нет аккаунта? Зарегистрироваться</div>
        </div>
    </div>

    <div id="main-screen">
        <div id="top-bar">
            <div class="my-profile">
                <img id="my-avatar-img" src="" alt="Avatar">
                <div>
                    <div style="font-weight: bold; color: #fff;" id="my-nick-display"></div>
                    <div style="font-size: 12px; color: var(--green);">В сети</div>
                </div>
            </div>
            <button onclick="logout()" style="width: auto; padding: 5px 10px; background: var(--border);">Выйти</button>
        </div>
        <div id="online-list"></div>
        <div id="chat-box"></div>
        <div id="bottom-bar">
            <label for="file-input" class="icon-btn">📎</label>
            <input type="file" id="file-input" accept="image/*" style="display: none;" onchange="uploadImage(event)">
            <input type="text" id="msg-input" placeholder="Сообщение..." onkeypress="if(event.key === 'Enter') sendMsg()">
            <button class="send-btn" onclick="sendMsg()">➤</button>
        </div>
    </div>

    <script>
        let isLoginMode = true;
        let myData = null;
        let lastMessageCount = 0;
        let currentAvatarBase64 = ""; // Сюда сохраняем выбранную аватарку

        window.onload = function() {
            let saved = localStorage.getItem('chatUser');
            if (saved) {
                myData = JSON.parse(saved);
                enterChat();
            }
        }

        function toggleAuthMode() {
            isLoginMode = !isLoginMode;
            document.getElementById('auth-title').innerText = isLoginMode ? "Вход" : "Регистрация";
            document.getElementById('auth-btn').innerText = isLoginMode ? "Войти" : "Зарегистрироваться";
            document.getElementById('toggle-text').innerText = isLoginMode ? "Нет аккаунта? Зарегистрироваться" : "Уже есть аккаунт? Войти";
            
            let display = isLoginMode ? "none" : "block";
            document.getElementById('auth-age').style.display = display;
            document.getElementById('auth-admin-code').style.display = display;
            document.getElementById('avatar-block').style.display = display;
        }

        // Функция предпросмотра и сжатия аватарки
        function previewAvatar(event) {
            const file = event.target.files[0]; if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = new Image();
                img.onload = function() {
                    const canvas = document.createElement('canvas');
                    const SIZE = 150; // Размер аватарки
                    canvas.width = SIZE; canvas.height = SIZE;
                    const ctx = canvas.getContext('2d');
                    
                    // Обрезаем в квадрат
                    const minSize = Math.min(img.width, img.height);
                    const startX = (img.width - minSize) / 2;
                    const startY = (img.height - minSize) / 2;
                    
                    ctx.drawImage(img, startX, startY, minSize, minSize, 0, 0, SIZE, SIZE);
                    
                    currentAvatarBase64 = canvas.toDataURL('image/jpeg', 0.8);
                    
                    let preview = document.getElementById('avatar-preview');
                    preview.src = currentAvatarBase64;
                    preview.style.display = 'inline-block';
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
                myData = { nick: nick, avatar: `https://ui-avatars.com/api/?name=${nick}&background=random&color=fff&size=128`, role: 'user', age: '' };
            } else {
                const age = document.getElementById('auth-age').value.trim();
                const adminCode = document.getElementById('auth-admin-code').value.trim();
                
                // Если выбрал фото - берем его, если нет - генерируем букву
                let avatar = currentAvatarBase64;
                if (!avatar) avatar = `https://ui-avatars.com/api/?name=${nick}&background=random&color=fff&size=128`;
                
                let role = 'user';
                if (adminCode === '1541') { role = 'admin'; }

                myData = { nick: nick, avatar: avatar, role: role, age: age };
            }
            localStorage.setItem('chatUser', JSON.stringify(myData));
            enterChat();
        }

        function logout() {
            localStorage.removeItem('chatUser');
            location.reload();
        }

        function enterChat() {
            document.getElementById('auth-screen').style.display = 'none';
            document.getElementById('main-screen').style.display = 'flex';
            document.getElementById('my-nick-display').innerText = myData.nick + (myData.age ? `, ${myData.age}` : '');
            document.getElementById('my-avatar-img').src = myData.avatar;
            fetch('/join', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(myData) });
            setInterval(fetchData, 1000);
        }

        function fetchData() {
            fetch('/data').then(r => r.json()).then(data => {
                const list = document.getElementById('online-list');
                list.innerHTML = '';
                data.users.forEach(u => {
                    let adminClass = u.role === 'admin' ? 'admin' : '';
                    list.innerHTML += `<div class="user-circle ${adminClass}"><img src="${u.avatar}"><span>${u.nick}</span></div>`;
                });

                if (data.messages.length !== lastMessageCount) {
                    const box = document.getElementById('chat-box');
                    box.innerHTML = '';
                    data.messages.forEach(m => {
                        let isMine = m.nick === myData.nick;
                        let msgClass = isMine ? 'mine' : '';
                        let imgHtml = m.image ? `<img src="${m.image}" class="msg-img">` : '';
                        box.innerHTML += `
                            <div class="msg ${msgClass}">
                                <img src="${m.avatar}" class="avatar">
                                <div class="msg-content">
                                    <div class="msg-name">${m.nick} (${m.time})</div>
                                    <div class="msg-text">${m.text}${imgHtml}</div>
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
            fetch('/send', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...myData, text: text, image: null }) })
            .then(() => { document.getElementById('msg-input').value = ''; });
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
                    fetch('/send', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...myData, text: "Фото", image: base64Image }) });
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
            self.wfile.write(json.dumps({"messages": messages, "users": list(online_users.values())}).encode('utf-8'))
        else: self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        if self.path == '/join':
            online_users[data['nick']] = {"nick": data['nick'], "avatar": data['avatar'], "role": data.get('role', 'user')}
            self.send_response(200); self.end_headers()
        elif self.path == '/send':
            messages.append({
                "nick": data['nick'], "avatar": data['avatar'], "text": data.get('text', ''), 
                "image": data.get('image'), "time": datetime.datetime.now().strftime("%H:%M")
            })
            self.send_response(200); self.end_headers()
        else: self.send_error(404)

if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), ChatHandler) as httpd:
        print("Сервер запущен на порту", PORT)
        httpd.serve_forever()
