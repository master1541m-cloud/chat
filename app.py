import http.server
import socketserver
import json
import datetime
import os
import time

PORT = int(os.environ.get("PORT", 8080))
messages = []
private_msgs = {}
users = {} 
typing_status = {}

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Мессенджер v13.0</title>
    <style>
        :root { --bg: #0d1117; --panel: #161b22; --text: #c9d1d9; --border: #30363d; --accent: #58a6ff; --green: #238636; }
        .light-theme { --bg: #f0f2f5; --panel: #ffffff; --text: #000000; --border: #ccc; --accent: #007bff; }
        
        html, body { margin: 0; padding: 0; width: 100%; height: 100%; background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; overflow: hidden; display: flex; flex-direction: column; transition: 0.3s; }
        
        /* Экран входа */
        #auth-screen { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 20px; box-sizing: border-box; overflow-y: auto; }
        .auth-box { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 25px; width: 100%; max-width: 350px; }
        input, textarea { width: 100%; padding: 12px; margin-bottom: 12px; background: var(--bg); color: var(--text); border: 1px solid var(--border); border-radius: 6px; box-sizing: border-box; outline: none; font-family: inherit; }
        button { width: 100%; padding: 12px; background: var(--green); color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; }
        .error { color: #f85149; font-size: 12px; text-align: center; margin-bottom: 10px; display: none; }
        
        .avatar-upload { text-align: center; margin-bottom: 15px; }
        .avatar-preview { width: 80px; height: 80px; border-radius: 50%; border: 2px solid var(--border); object-fit: cover; margin-bottom: 10px; display: none; background: #000; }
        .upload-btn { background: var(--border); color: white; padding: 8px; border-radius: 6px; cursor: pointer; display: inline-block; font-size: 14px; margin-bottom: 10px; }

        /* Основной экран */
        #main-screen { display: none; flex-direction: column; height: 100%; position: relative; }
        .tab-content { flex-grow: 1; overflow-y: auto; display: none; padding-bottom: 60px; }
        .tab-content.active { display: block; }
        
        /* Списки */
        .contact { padding: 15px; border-bottom: 1px solid var(--border); cursor: pointer; display: flex; align-items: center; gap: 15px; }
        .contact:hover { background: var(--panel); }
        .contact img { width: 45px; height: 45px; border-radius: 50%; }
        .contact-info { display: flex; flex-direction: column; flex-grow: 1; }
        .contact-name { font-weight: bold; font-size: 16px; }
        .contact-sub { font-size: 12px; color: #888; }
        .online-dot { width: 10px; height: 10px; background: #2ea043; border-radius: 50%; display: inline-block; margin-right: 5px; }

        /* Аккаунт */
        .profile-view { text-align: center; padding: 40px 20px; }
        .profile-view img { width: 120px; height: 120px; border-radius: 50%; border: 3px solid var(--accent); object-fit: cover; margin-bottom: 20px; }
        .profile-view h1 { margin: 0; color: var(--text); }
        .profile-view p { color: #888; margin-top: 5px; font-style: italic; }

        /* НАСТРОЙКИ (Как в Telegram) */
        .settings-section { background: var(--panel); margin: 15px; border-radius: 10px; overflow: hidden; }
        .settings-item { padding: 15px; display: flex; align-items: center; gap: 15px; border-bottom: 1px solid var(--border); cursor: pointer; }
        .settings-item:last-child { border-bottom: none; }
        .settings-icon { width: 35px; height: 35px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        .settings-text { display: flex; flex-direction: column; flex-grow: 1; }
        .settings-title { font-size: 16px; color: var(--text); }
        .settings-desc { font-size: 12px; color: #888; }
        .settings-arrow { color: #888; font-size: 20px; }

        /* Нижняя панель */
        #bottom-nav { position: absolute; bottom: 0; left: 0; width: 100%; background: var(--panel); border-top: 1px solid var(--border); display: flex; justify-content: space-around; padding: 10px 0; z-index: 20; }
        .nav-item { display: flex; flex-direction: column; align-items: center; color: #888; cursor: pointer; font-size: 12px; }
        .nav-item.active { color: var(--accent); }
        .nav-item span { font-size: 20px; margin-bottom: 2px; }
        
        /* Чат */
        #chat-screen { display: none; flex-direction: column; height: 100%; position: absolute; top: 0; left: 0; width: 100%; background: var(--bg); z-index: 30; }
        #chat-header { padding: 10px 15px; border-bottom: 1px solid var(--border); background: var(--panel); display: flex; align-items: center; gap: 15px; }
        #chat-header button { width: auto; padding: 5px 10px; background: var(--border); color: var(--text); }
        .chat-header-info { display: flex; align-items: center; gap: 10px; flex-grow: 1; cursor: pointer; }
        .chat-header-info img { width: 35px; height: 35px; border-radius: 50%; }
        .chat-header-name { font-weight: bold; font-size: 15px; }
        .chat-header-status { font-size: 12px; color: #888; }
        
        #chat-box { flex-grow: 1; overflow-y: scroll; padding: 15px; display: flex; flex-direction: column; gap: 10px; }
        .msg { display: flex; gap: 10px; max-width: 90%; }
        .msg.mine { align-self: flex-end; flex-direction: row-reverse; }
        .msg img { width: 30px; height: 30px; border-radius: 50%; }
        .msg-content { background: var(--panel); padding: 8px 12px; border-radius: 10px; border: 1px solid var(--border); }
        .msg.mine .msg-content { background: #1f6feb; color: white; }
        .msg-name { font-size: 11px; color: var(--accent); font-weight: bold; margin-bottom: 3px; }
        .msg.mine .msg-name { color: #c9d1d9; text-align: right; }
        
        #bottom-bar { background: var(--panel); padding: 10px; border-top: 1px solid var(--border); display: flex; gap: 10px; }
        #msg-input { margin-bottom: 0; flex-grow: 1; }
        
        #search-bar { display: none; padding: 10px; background: var(--panel); border-bottom: 1px solid var(--border); }
        
        /* Модалки */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 100; justify-content: center; align-items: center; }
        .modal-content { background: var(--panel); border-radius: 15px; padding: 20px; width: 80%; max-width: 300px; text-align: center; position: relative; }
        .close-modal { position: absolute; top: 10px; right: 15px; font-size: 24px; cursor: pointer; color: #888; }
    </style>
</head>
<body>
    <div id="auth-screen">
        <div class="auth-box">
            <h2 style="text-align:center;">Регистрация</h2>
            <div id="error-msg" class="error"></div>
            <div class="avatar-upload">
                <img id="avatar-preview" class="avatar-preview" src="">
                <label for="avatar-file" class="upload-btn">📷 Выбрать аватарку</label>
                <input type="file" id="avatar-file" accept="image/*" style="display:none;" onchange="previewAvatar(event)">
            </div>
            <input type="text" id="reg-nick" placeholder="Ваше Имя">
            <input type="text" id="reg-username" placeholder="Уникальный @username">
            <input type="password" id="reg-pass" placeholder="Пароль">
            <textarea id="reg-bio" placeholder="О себе" rows="2"></textarea>
            <button onclick="doRegister()">Зарегистрироваться</button>
        </div>
    </div>

    <div id="main-screen">
        <div id="tab-chats" class="tab-content active">
            <div style="display:flex; justify-content:space-between; padding:15px; align-items:center;">
                <div style="font-weight:bold; font-size:18px;">Чаты</div>
                <div onclick="toggleSearch()" style="cursor:pointer; font-size:20px;">🔍</div>
            </div>
            <div id="search-bar">
                <input type="text" id="search-input" placeholder="Введите @username..." onkeypress="if(event.key === 'Enter') searchUser()">
            </div>
            <div id="contact-list">
                <div class="contact" onclick="openChat('GENERAL')">
                    <div style="width:45px;height:45px;background:#5865F2;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px;">🌐</div>
                    <div class="contact-info">
                        <div class="contact-name">Общий чат</div>
                        <div class="contact-sub">Писать всем</div>
                    </div>
                </div>
            </div>
        </div>

        <div id="tab-contacts" class="tab-content">
            <div style="padding:15px; font-weight:bold; font-size:18px;">Все пользователи</div>
            <div id="all-users-list"></div>
        </div>

        <div id="tab-account" class="tab-content">
            <div class="profile-view">
                <img id="account-avatar" src="">
                <h1 id="account-nick"></h1>
                <div style="color:var(--accent); font-size:16px; margin-bottom:10px;" id="account-username"></div>
                <p id="account-bio"></p>
            </div>
        </div>

        <!-- НОВЫЕ НАСТРОЙКИ -->
        <div id="tab-settings" class="tab-content">
            <div style="padding:15px; font-weight:bold; font-size:22px;">Настройки</div>
            
            <!-- Аккаунт -->
            <div class="settings-section">
                <div class="settings-item" onclick="switchTab('account', document.querySelectorAll('.nav-item')[2])">
                    <div class="settings-icon" style="background:#3390ec;">👤</div>
                    <div class="settings-text">
                        <div class="settings-title">Аккаунт</div>
                        <div class="settings-desc">Имя, @username, описание</div>
                    </div>
                    <div class="settings-arrow">›</div>
                </div>
            </div>

            <!-- Настройки чатов -->
            <div class="settings-section">
                <div class="settings-item" onclick="toggleTheme()">
                    <div class="settings-icon" style="background:#e0a000;">🎨</div>
                    <div class="settings-text">
                        <div class="settings-title">Настройки чатов</div>
                        <div class="settings-desc">Сменить тему (Тёмная/Светлая)</div>
                    </div>
                    <div class="settings-arrow">›</div>
                </div>
            </div>

            <!-- Приватность -->
            <div class="settings-section">
                <div class="settings-item" onclick="alert('Это заглушка. Приватность в разработке!')">
                    <div class="settings-icon" style="background:#2ea043;">🔐</div>
                    <div class="settings-text">
                        <div class="settings-title">Приватность и безопасность</div>
                        <div class="settings-desc">Блокировка, пароли</div>
                    </div>
                    <div class="settings-arrow">›</div>
                </div>
            </div>

            <!-- Уведомления -->
            <div class="settings-section">
                <div class="settings-item" onclick="toggleSound()">
                    <div class="settings-icon" style="background:#e64a4a;">🔔</div>
                    <div class="settings-text">
                        <div class="settings-title">Уведомления и звуки</div>
                        <div class="settings-desc" id="sound-status">Звук включен</div>
                    </div>
                    <div class="settings-arrow">›</div>
                </div>
            </div>

            <!-- Выход -->
            <div class="settings-section">
                <div class="settings-item" onclick="logout()">
                    <div class="settings-icon" style="background:#888;">🚪</div>
                    <div class="settings-text">
                        <div class="settings-title" style="color:#f85149;">Выйти</div>
                    </div>
                </div>
            </div>
            
            <div style="text-align:center; color:#555; font-size:12px; margin-top:20px;">Мессенджер v13.0</div>
        </div>

        <div id="bottom-nav">
            <div class="nav-item active" onclick="switchTab('chats', this)"><span>💬</span>Чаты</div>
            <div class="nav-item" onclick="switchTab('contacts', this)"><span>👥</span>Контакты</div>
            <div class="nav-item" onclick="switchTab('account', this)"><span>👤</span>Аккаунт</div>
            <div class="nav-item" onclick="switchTab('settings', this)"><span>⚙️</span>Настройки</div>
        </div>
    </div>

    <div id="chat-screen">
        <div id="chat-header">
            <button onclick="closeChat()">←</button>
            <div class="chat-header-info" onclick="openProfile(currentChat)">
                <img id="chat-avatar" src="" style="display:none;">
                <div>
                    <div class="chat-header-name" id="chat-title">Чат</div>
                    <div class="chat-header-status" id="chat-status"></div>
                </div>
            </div>
        </div>
        <div id="chat-box"></div>
        <div id="bottom-bar">
            <input type="text" id="msg-input" placeholder="Сообщение..." oninput="notifyTyping()" onkeypress="if(event.key === 'Enter') sendMsg()">
            <button onclick="sendMsg()" style="width:auto; padding:0 15px;">➤</button>
        </div>
    </div>

    <div id="profile-modal" class="modal" onclick="closeModal(event)">
        <div class="modal-content" onclick="event.stopPropagation()">
            <span class="close-modal" onclick="closeModal(event)">×</span>
            <img id="profile-avatar" style="width:100px;height:100px;border-radius:50%;margin-bottom:15px;">
            <h2 id="profile-nick"></h2>
            <div style="color:var(--accent); margin-bottom:10px;" id="profile-username"></div>
            <p id="profile-bio" style="font-style:italic; color:#888;"></p>
            <p id="profile-status"></p>
        </div>
    </div>

    <script>
        let myData = null;
        let currentChat = 'GENERAL';
        let lastMsgCount = 0;
        let currentAvatarBase64 = "";
        let soundEnabled = true;

        window.onload = function() {
            let saved = localStorage.getItem('chatUser');
            if (saved) { myData = JSON.parse(saved); enterChat(); }
            // Загружаем настройки темы
            if(localStorage.getItem('theme') === 'light') document.body.classList.add('light-theme');
        }

        function toggleTheme() {
            document.body.classList.toggle('light-theme');
            localStorage.setItem('theme', document.body.classList.contains('light-theme') ? 'light' : 'dark');
        }

        function toggleSound() {
            soundEnabled = !soundEnabled;
            document.getElementById('sound-status').innerText = soundEnabled ? "Звук включен" : "Звук выключен";
        }

        function previewAvatar(event) {
            const file = event.target.files[0]; if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = new Image();
                img.onload = function() {
                    const canvas = document.createElement('canvas');
                    const SIZE = 150;
                    canvas.width = SIZE; canvas.height = SIZE;
                    const ctx = canvas.getContext('2d');
                    const minSize = Math.min(img.width, img.height);
                    const startX = (img.width - minSize) / 2;
                    const startY = (img.height - minSize) / 2;
                    ctx.drawImage(img, startX, startY, minSize, minSize, 0, 0, SIZE, SIZE);
                    currentAvatarBase64 = canvas.toDataURL('image/jpeg', 0.7);
                    let preview = document.getElementById('avatar-preview');
                    preview.src = currentAvatarBase64;
                    preview.style.display = 'block';
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }

        function doRegister() {
            const nick = document.getElementById('reg-nick').value.trim();
            const username = document.getElementById('reg-username').value.trim().toLowerCase();
            const pass = document.getElementById('reg-pass').value.trim();
            const bio = document.getElementById('reg-bio').value.trim();
            const errorMsg = document.getElementById('error-msg');

            if (!/^[a-z0-9_]{3,15}$/.test(username)) {
                errorMsg.innerText = "Юзернейм: 3-15 символов, только a-z, 0-9, _";
                errorMsg.style.display = 'block';
                return;
            }
            if (!nick || !pass) {
                errorMsg.innerText = "Заполните имя и пароль!";
                errorMsg.style.display = 'block';
                return;
            }

            let avatar = currentAvatarBase64 || `https://ui-avatars.com/api/?name=${nick}&background=random&color=fff`;

            fetch('/register', { method: 'POST', body: JSON.stringify({ nick: nick, username: username, pass: pass, avatar: avatar, bio: bio }) })
            .then(r => r.json())
            .then(res => {
                if (res.error) {
                    errorMsg.innerText = res.error;
                    errorMsg.style.display = 'block';
                } else {
                    myData = res.user;
                    localStorage.setItem('chatUser', JSON.stringify(myData));
                    enterChat();
                }
            });
        }

        function enterChat() {
            document.getElementById('auth-screen').style.display = 'none';
            document.getElementById('main-screen').style.display = 'flex';
            document.getElementById('account-avatar').src = myData.avatar;
            document.getElementById('account-nick').innerText = myData.nick;
            document.getElementById('account-username').innerText = '@' + myData.username;
            document.getElementById('account-bio').innerText = myData.bio || "Без описания";
            fetch('/join', { method: 'POST', body: JSON.stringify(myData) });
            setInterval(fetchData, 1000);
        }

        function logout() { localStorage.removeItem('chatUser'); location.reload(); }

        function switchTab(tabId, element) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById('tab-' + tabId).classList.add('active');
            element.classList.add('active');
        }

        function toggleSearch() {
            let bar = document.getElementById('search-bar');
            bar.style.display = bar.style.display === 'block' ? 'none' : 'block';
            if (bar.style.display === 'block') document.getElementById('search-input').focus();
        }

        function searchUser() {
            const query = document.getElementById('search-input').value.trim().replace('@', '');
            if (!query || query === myData.username) return;
            if (!document.getElementById('contact-' + query)) {
                let html = `<div class="contact" id="contact-${query}" onclick="openChat('${query}')">
                    <img src="https://ui-avatars.com/api/?name=${query}&background=random&color=fff">
                    <div class="contact-info"><div class="contact-name">@${query}</div><div class="contact-sub">Нажмите, чтобы написать</div></div>
                </div>`;
                document.getElementById('contact-list').insertAdjacentHTML('beforeend', html);
            }
            document.getElementById('search-input').value = '';
            toggleSearch();
            openChat(query);
        }

        function openChat(username) {
            currentChat = username;
            lastMsgCount = 0;
            document.getElementById('main-screen').style.display = 'none';
            document.getElementById('chat-screen').style.display = 'flex';
            if (username === 'GENERAL') {
                document.getElementById('chat-title').innerText = 'Общий чат';
                document.getElementById('chat-avatar').style.display = 'none';
                document.getElementById('chat-status').innerText = '';
            } else {
                document.getElementById('chat-title').innerText = '@' + username;
                document.getElementById('chat-avatar').src = `https://ui-avatars.com/api/?name=${username}&background=random&color=fff`;
                document.getElementById('chat-avatar').style.display = 'block';
                document.getElementById('chat-status').innerText = '...';
            }
        }

        function closeChat() {
            document.getElementById('chat-screen').style.display = 'none';
            document.getElementById('main-screen').style.display = 'flex';
        }

        function openProfile(username) {
            if (username === 'GENERAL' || username === myData.username) return;
            fetch('/get_user/' + username).then(r => r.json()).then(u => {
                if (u) {
                    document.getElementById('profile-avatar').src = u.avatar;
                    document.getElementById('profile-nick').innerText = u.nick;
                    document.getElementById('profile-username').innerText = '@' + u.username;
                    document.getElementById('profile-bio').innerText = u.bio || "Без описания";
                    document.getElementById('profile-status').innerText = u.online ? "В сети" : "Не в сети";
                    document.getElementById('profile-modal').style.display = 'flex';
                }
            });
        }

        function closeModal(e) {
            if(e) e.stopPropagation();
            document.getElementById('profile-modal').style.display = 'none';
        }

        function notifyTyping() {
            if (currentChat === 'GENERAL') return;
            fetch('/typing', { method: 'POST', body: JSON.stringify({ username: myData.username, target: currentChat }) });
        }

        function fetchData() {
            fetch('/data').then(r => r.json()).then(data => {
                const list = document.getElementById('contact-list');
                const allList = document.getElementById('all-users-list');
                Object.keys(data.users).forEach(u => {
                    let userObj = data.users[u];
                    if (u !== myData.username) {
                        if (!document.getElementById('contact-' + u)) {
                            let isOnline = userObj.online ? '<span class="online-dot"></span>' : '';
                            let html = `<div class="contact" id="contact-${u}" onclick="openChat('${u}')">
                                <img src="${userObj.avatar}">
                                <div class="contact-info"><div class="contact-name">${userObj.nick}</div><div class="contact-sub">@${u} | ${isOnline} ${userObj.online ? 'В сети' : 'Не в сети'}</div></div>
                            </div>`;
                            list.insertAdjacentHTML('beforeend', html);
                        }
                        if (!document.getElementById('all-user-' + u)) {
                            let isOnline = userObj.online ? '<span class="online-dot"></span>' : '';
                            let html = `<div class="contact" id="all-user-${u}" onclick="openChat('${u}')">
                                <img src="${userObj.avatar}">
                                <div class="contact-info"><div class="contact-name">${userObj.nick}</div><div class="contact-sub">@${u} | ${isOnline} ${userObj.online ? 'В сети' : 'Не в сети'}</div></div>
                            </div>`;
                            allList.insertAdjacentHTML('beforeend', html);
                        }
                    }
                });
                if (currentChat !== 'GENERAL' && data.users[currentChat]) {
                    let u = data.users[currentChat];
                    let status = u.online ? 'В сети' : 'Не в сети';
                    if (data.typing && data.typing[currentChat]) status = 'печатает...';
                    document.getElementById('chat-status').innerText = status;
                }
                if (document.getElementById('chat-screen').style.display === 'flex') {
                    let currentMessages = [];
                    if (currentChat === 'GENERAL') {
                        currentMessages = data.general;
                    } else {
                        let key = [myData.username, currentChat].sort().join('|');
                        currentMessages = data.private[key] || [];
                    }
                    if (currentMessages.length !== lastMsgCount) {
                        const box = document.getElementById('chat-box');
                        box.innerHTML = '';
                        currentMessages.forEach(m => {
                            let isMine = m.username === myData.username;
                            box.innerHTML += `<div class="msg ${isMine ? 'mine' : ''}"><img src="${m.avatar}"><div class="msg-content"><div class="msg-name">@${m.username} (${m.time})</div><div>${m.text}</div></div></div>`;
                        });
                        box.scrollTop = box.scrollHeight;
                        lastMsgCount = currentMessages.length;
                    }
                }
            });
        }

        function sendMsg() {
            const text = document.getElementById('msg-input').value.trim();
            if (!text) return;
            let payload = { ...myData, text: text, target: currentChat };
            fetch('/send', { method: 'POST', body: JSON.stringify(payload) }).then(() => { document.getElementById('msg-input').value = ''; });
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
        elif self.path.startswith('/get_user/'):
            username = self.path.split('/')[-1]
            if username in users:
                self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
                self.wfile.write(json.dumps(users[username]).encode('utf-8'))
            else:
                self.send_response(404); self.end_headers()
        elif self.path == '/data':
            self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
            now = time.time()
            for u in users: users[u]['online'] = (now - users[u].get('last_seen', 0)) < 30
            active_typing = {k: v for k, v in typing_status.items() if now - v < 3}
            self.wfile.write(json.dumps({"general": messages, "private": private_msgs, "users": users, "typing": active_typing}).encode('utf-8'))
        else: self.send_error(404)

    def do_POST(self):
        l = int(self.headers['Content-Length'])
        d = json.loads(self.rfile.read(l).decode())
        if self.path == '/register':
            username = d['username']
            if username in users:
                self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
                self.wfile.write(json.dumps({"error": "Этот @username уже занят!"}).encode('utf-8'))
                return
            users[username] = {"nick": d['nick'], "username": username, "avatar": d['avatar'], "bio": d['bio'], "last_seen": time.time(), "online": True}
            self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
            self.wfile.write(json.dumps({"user": users[username]}).encode('utf-8'))
        elif self.path == '/join': 
            if d['username'] in users: users[d['username']]['last_seen'] = time.time()
        elif self.path == '/typing':
            typing_status[d['target']] = time.time()
        elif self.path == '/send': 
            msg_obj = {"username": d['username'], "avatar": d['avatar'], "text": d['text'], "time": datetime.datetime.now().strftime("%H:%M")}
            if d['target'] == 'GENERAL': messages.append(msg_obj)
            else:
                key = "|".join(sorted([d['username'], d['target']]))
                if key not in private_msgs: private_msgs[key] = []
                private_msgs[key].append(msg_obj)
        self.send_response(200); self.end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), ChatHandler) as httpd:
        print("Сервер v13.0 запущен")
        httpd.serve_forever()
