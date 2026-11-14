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
    <title>Мессенджер v10.0</title>
    <style>
        :root { --bg: #0d1117; --panel: #161b22; --text: #c9d1d9; --border: #30363d; --accent: #58a6ff; --green: #238636; }
        html, body { margin: 0; padding: 0; width: 100%; height: 100%; background: var(--bg); color: var(--text); font-family: sans-serif; overflow: hidden; display: flex; flex-direction: column; }
        
        /* Экран входа */
        #auth-screen { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 20px; box-sizing: border-box; }
        .auth-box { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 25px; width: 100%; max-width: 350px; }
        input { width: 100%; padding: 12px; margin-bottom: 12px; background: var(--bg); color: var(--text); border: 1px solid var(--border); border-radius: 6px; box-sizing: border-box; outline: none; }
        button { width: 100%; padding: 12px; background: var(--green); color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; }
        
        /* Основной экран */
        #main-screen { display: none; flex-direction: column; height: 100%; position: relative; }
        
        /* Контент вкладок */
        .tab-content { flex-grow: 1; overflow-y: auto; display: none; padding-bottom: 60px; }
        .tab-content.active { display: block; }
        
        /* Вкладка Чаты */
        .contact { padding: 15px; border-bottom: 1px solid var(--border); cursor: pointer; display: flex; align-items: center; gap: 15px; }
        .contact:hover { background: var(--panel); }
        .contact img { width: 45px; height: 45px; border-radius: 50%; }
        .contact-info { display: flex; flex-direction: column; flex-grow: 1; }
        .contact-name { font-weight: bold; font-size: 16px; }
        .contact-sub { font-size: 12px; color: #888; }
        .online-dot { width: 10px; height: 10px; background: #2ea043; border-radius: 50%; display: inline-block; margin-right: 5px; }

        /* Вкладка Аккаунт */
        .profile-view { text-align: center; padding: 40px 20px; }
        .profile-view img { width: 120px; height: 120px; border-radius: 50%; border: 3px solid var(--accent); object-fit: cover; margin-bottom: 20px; }
        .profile-view h1 { margin: 0; color: white; }
        
        /* Вкладка Настройки */
        .settings-list { list-style: none; padding: 0; margin: 0; }
        .settings-list li { padding: 15px; border-bottom: 1px solid var(--border); cursor: pointer; }
        
        /* Нижняя панель навигации */
        #bottom-nav { position: absolute; bottom: 0; left: 0; width: 100%; background: var(--panel); border-top: 1px solid var(--border); display: flex; justify-content: space-around; padding: 10px 0; z-index: 20; }
        .nav-item { display: flex; flex-direction: column; align-items: center; color: #888; cursor: pointer; font-size: 12px; }
        .nav-item.active { color: var(--accent); }
        .nav-item span { font-size: 20px; margin-bottom: 2px; }
        
        /* Экран чата (Поверх всего) */
        #chat-screen { display: none; flex-direction: column; height: 100%; position: absolute; top: 0; left: 0; width: 100%; background: var(--bg); z-index: 30; }
        #chat-header { padding: 10px 15px; border-bottom: 1px solid var(--border); background: var(--panel); display: flex; align-items: center; gap: 15px; }
        #chat-header button { width: auto; padding: 5px 10px; background: var(--border); }
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
        
        /* Поиск */
        #search-bar { display: none; padding: 10px; background: var(--panel); border-bottom: 1px solid var(--border); }
        
        /* Модалка профиля */
        #profile-modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 100; justify-content: center; align-items: center; }
        .profile-card { background: var(--panel); border: 1px solid var(--border); border-radius: 15px; padding: 30px; width: 80%; max-width: 300px; text-align: center; position: relative; }
        .profile-card img { width: 100px; height: 100px; border-radius: 50%; border: 3px solid var(--accent); object-fit: cover; margin-bottom: 15px; }
        .close-profile { position: absolute; top: 10px; right: 15px; font-size: 24px; cursor: pointer; color: #888; }
    </style>
</head>
<body>
    <div id="auth-screen">
        <div class="auth-box">
            <h2 style="text-align:center;">Вход</h2>
            <input type="text" id="nick" placeholder="Ваш ник (без @)">
            <input type="password" id="pass" placeholder="Пароль (любой)">
            <input type="text" id="avatar" placeholder="Ссылка на аватарку">
            <button onclick="doLogin()">Войти</button>
        </div>
    </div>

    <div id="main-screen">
        <!-- Вкладка 1: Чаты -->
        <div id="tab-chats" class="tab-content active">
            <div style="display:flex; justify-content:space-between; padding:15px; align-items:center;">
                <div style="font-weight:bold; font-size:18px;">Чаты</div>
                <div onclick="toggleSearch()" style="cursor:pointer; font-size:20px;">🔍</div>
            </div>
            <div id="search-bar">
                <input type="text" id="search-input" placeholder="Введите @ник и нажмите Enter..." onkeypress="if(event.key === 'Enter') searchUser()">
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

        <!-- Вкладка 2: Контакты -->
        <div id="tab-contacts" class="tab-content">
            <div style="padding:15px; font-weight:bold; font-size:18px;">Все пользователи</div>
            <div id="all-users-list"></div>
        </div>

        <!-- Вкладка 3: Аккаунт -->
        <div id="tab-account" class="tab-content">
            <div class="profile-view">
                <img id="account-avatar" src="">
                <h1 id="account-nick"></h1>
            </div>
        </div>

        <!-- Вкладка 4: Настройки -->
        <div id="tab-settings" class="tab-content">
            <div style="padding:15px; font-weight:bold; font-size:18px;">Настройки</div>
            <ul class="settings-list">
                <li onclick="logout()">🚪 Выйти из аккаунта</li>
            </ul>
        </div>

        <!-- Нижняя панель навигации -->
        <div id="bottom-nav">
            <div class="nav-item active" onclick="switchTab('chats', this)"><span>💬</span>Чаты</div>
            <div class="nav-item" onclick="switchTab('contacts', this)"><span>👥</span>Контакты</div>
            <div class="nav-item" onclick="switchTab('account', this)"><span>👤</span>Аккаунт</div>
            <div class="nav-item" onclick="switchTab('settings', this)"><span>⚙️</span>Настройки</div>
        </div>
    </div>

    <!-- Экран чата -->
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

    <div id="profile-modal" onclick="closeProfile(event)">
        <div class="profile-card" onclick="event.stopPropagation()">
            <span class="close-profile" onclick="closeProfile(event)">×</span>
            <img id="profile-avatar" src="">
            <h2 id="profile-name">@Ник</h2>
            <p id="profile-status">В сети</p>
        </div>
    </div>

    <script>
        let myData = null;
        let currentChat = 'GENERAL';
        let lastMsgCount = 0;

        window.onload = function() {
            let saved = localStorage.getItem('chatUser');
            if (saved) { myData = JSON.parse(saved); enterChat(); }
        }

        function doLogin() {
            const nick = document.getElementById('nick').value.trim();
            const pass = document.getElementById('pass').value.trim();
            let avatar = document.getElementById('avatar').value.trim();
            if (!nick || !pass) return alert("Введите ник и пароль!");
            if (!avatar) avatar = `https://ui-avatars.com/api/?name=${nick}&background=random&color=fff`;
            
            myData = { nick: nick, avatar: avatar };
            localStorage.setItem('chatUser', JSON.stringify(myData));
            enterChat();
        }

        function enterChat() {
            document.getElementById('auth-screen').style.display = 'none';
            document.getElementById('main-screen').style.display = 'flex';
            
            document.getElementById('account-avatar').src = myData.avatar;
            document.getElementById('account-nick').innerText = '@' + myData.nick;
            
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
            const query = document.getElementById('search-input').value.trim();
            if (!query || query === myData.nick) return;
            
            // Добавляем в чаты
            if (!document.getElementById('contact-' + query)) {
                let html = `<div class="contact" id="contact-${query}" onclick="openChat('${query}')">
                    <img src="https://ui-avatars.com/api/?name=${query}&background=random&color=fff">
                    <div class="contact-info">
                        <div class="contact-name">@${query}</div>
                        <div class="contact-sub">Нажмите, чтобы написать</div>
                    </div>
                </div>`;
                document.getElementById('contact-list').insertAdjacentHTML('beforeend', html);
            }
            document.getElementById('search-input').value = '';
            toggleSearch();
            openChat(query);
        }

        function openChat(chatId) {
            currentChat = chatId;
            lastMsgCount = 0;
            document.getElementById('main-screen').style.display = 'none';
            document.getElementById('chat-screen').style.display = 'flex';
            
            if (chatId === 'GENERAL') {
                document.getElementById('chat-title').innerText = 'Общий чат';
                document.getElementById('chat-avatar').style.display = 'none';
                document.getElementById('chat-status').innerText = '';
            } else {
                document.getElementById('chat-title').innerText = '@' + chatId;
                document.getElementById('chat-avatar').src = `https://ui-avatars.com/api/?name=${chatId}&background=random&color=fff`;
                document.getElementById('chat-avatar').style.display = 'block';
                document.getElementById('chat-status').innerText = '...';
            }
        }

        function closeChat() {
            document.getElementById('chat-screen').style.display = 'none';
            document.getElementById('main-screen').style.display = 'flex';
        }

        function openProfile(nick) {
            if (nick === 'GENERAL' || nick === myData.nick) return;
            document.getElementById('profile-avatar').src = `https://ui-avatars.com/api/?name=${nick}&background=random&color=fff`;
            document.getElementById('profile-name').innerText = '@' + nick;
            document.getElementById('profile-modal').style.display = 'flex';
        }

        function closeProfile(e) {
            if(e) e.stopPropagation();
            document.getElementById('profile-modal').style.display = 'none';
        }

        function notifyTyping() {
            if (currentChat === 'GENERAL') return;
            fetch('/typing', { method: 'POST', body: JSON.stringify({ nick: myData.nick, target: currentChat }) });
        }

        function fetchData() {
            fetch('/data').then(r => r.json()).then(data => {
                // Обновляем список контактов
                const list = document.getElementById('contact-list');
                const allList = document.getElementById('all-users-list');
                
                Object.keys(data.users).forEach(u => {
                    if (u !== myData.nick) {
                        // В чаты
                        if (!document.getElementById('contact-' + u)) {
                            let isOnline = data.users[u].online ? '<span class="online-dot"></span>' : '';
                            let html = `<div class="contact" id="contact-${u}" onclick="openChat('${u}')">
                                <img src="${data.users[u].avatar}">
                                <div class="contact-info">
                                    <div class="contact-name">@${u}</div>
                                    <div class="contact-sub">${isOnline} ${data.users[u].online ? 'В сети' : 'Не в сети'}</div>
                                </div>
                            </div>`;
                            list.insertAdjacentHTML('beforeend', html);
                        }
                        // В контакты
                        if (!document.getElementById('all-user-' + u)) {
                            let isOnline = data.users[u].online ? '<span class="online-dot"></span>' : '';
                            let html = `<div class="contact" id="all-user-${u}" onclick="openChat('${u}')">
                                <img src="${data.users[u].avatar}">
                                <div class="contact-info">
                                    <div class="contact-name">@${u}</div>
                                    <div class="contact-sub">${isOnline} ${data.users[u].online ? 'В сети' : 'Не в сети'}</div>
                                </div>
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
                        let key = [myData.nick, currentChat].sort().join('|');
                        currentMessages = data.private[key] || [];
                    }

                    if (currentMessages.length !== lastMsgCount) {
                        const box = document.getElementById('chat-box');
                        box.innerHTML = '';
                        currentMessages.forEach(m => {
                            let isMine = m.nick === myData.nick;
                            box.innerHTML += `
                                <div class="msg ${isMine ? 'mine' : ''}">
                                    <img src="${m.avatar}">
                                    <div class="msg-content">
                                        <div class="msg-name">@${m.nick} (${m.time})</div>
                                        <div>${m.text}</div>
                                    </div>
                                </div>`;
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
            
            fetch('/send', { method: 'POST', body: JSON.stringify(payload) })
            .then(() => { document.getElementById('msg-input').value = ''; });
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
            
            now = time.time()
            for u in users:
                users[u]['online'] = (now - users[u].get('last_seen', 0)) < 30
                
            active_typing = {k: v for k, v in typing_status.items() if now - v < 3}
                
            self.wfile.write(json.dumps({
                "general": messages, 
                "private": private_msgs,
                "users": users,
                "typing": active_typing
            }).encode('utf-8'))
        else: self.send_error(404)

    def do_POST(self):
        l = int(self.headers['Content-Length'])
        d = json.loads(self.rfile.read(l).decode())
        
        if self.path == '/join': 
            users[d['nick']] = {"avatar": d['avatar'], "last_seen": time.time(), "online": True}
        elif self.path == '/typing':
            typing_status[d['target']] = time.time()
        elif self.path == '/send': 
            msg_obj = {
                "nick": d['nick'], "avatar": d['avatar'], 
                "text": d['text'], "time": datetime.datetime.now().strftime("%H:%M")
            }
            if d['target'] == 'GENERAL':
                messages.append(msg_obj)
            else:
                key = "|".join(sorted([d['nick'], d['target']]))
                if key not in private_msgs: private_msgs[key] = []
                private_msgs[key].append(msg_obj)
                
        self.send_response(200); self.end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), ChatHandler) as httpd:
        print("Сервер v10.0 запущен")
        httpd.serve_forever()
