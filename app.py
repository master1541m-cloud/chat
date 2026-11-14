import http.server
import socketserver
import json
import datetime
import os

PORT = int(os.environ.get("PORT", 8080))
messages = []
private_msgs = {}
users = {}

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Мессенджер v7.0</title>
    <style>
        :root { --bg: #0d1117; --panel: #161b22; --text: #c9d1d9; --border: #30363d; --accent: #58a6ff; --green: #238636; }
        html, body { margin: 0; padding: 0; width: 100%; height: 100%; background: var(--bg); color: var(--text); font-family: sans-serif; overflow: hidden; display: flex; flex-direction: column; }
        
        /* Экран входа */
        #auth-screen { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 20px; box-sizing: border-box; }
        .auth-box { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 25px; width: 100%; max-width: 350px; }
        input { width: 100%; padding: 12px; margin-bottom: 12px; background: var(--bg); color: var(--text); border: 1px solid var(--border); border-radius: 6px; box-sizing: border-box; outline: none; }
        button { width: 100%; padding: 12px; background: var(--green); color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; }
        
        /* Основной экран */
        #main-screen { display: none; flex-direction: column; height: 100%; }
        
        /* Верхняя панель (Список) */
        #top-bar-list { background: var(--panel); border-bottom: 1px solid var(--border); padding: 10px 15px; display: flex; justify-content: space-between; align-items: center; }
        #search-bar { display: none; padding: 10px; background: var(--panel); border-bottom: 1px solid var(--border); }
        #search-bar input { margin-bottom: 0; }
        
        /* Список контактов */
        #contact-list { flex-grow: 1; overflow-y: auto; background: var(--bg); }
        .contact { padding: 15px; border-bottom: 1px solid var(--border); cursor: pointer; display: flex; align-items: center; gap: 15px; }
        .contact:hover { background: var(--panel); }
        .contact img { width: 45px; height: 45px; border-radius: 50%; }
        .contact-info { display: flex; flex-direction: column; }
        .contact-name { font-weight: bold; font-size: 16px; }
        .contact-sub { font-size: 12px; color: #888; }

        /* Окно чата (на весь экран) */
        #chat-screen { display: none; flex-direction: column; height: 100%; position: absolute; top: 0; left: 0; width: 100%; background: var(--bg); z-index: 10; }
        #chat-header { padding: 15px; border-bottom: 1px solid var(--border); font-weight: bold; background: var(--panel); display: flex; align-items: center; gap: 15px; }
        #chat-header button { width: auto; padding: 5px 10px; background: var(--border); }
        
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
        
        .icon-btn { font-size: 24px; cursor: pointer; width: auto; padding: 0 10px; background: none; color: var(--text); }
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
        <!-- Верхняя панель списка -->
        <div id="top-bar-list">
            <div style="font-weight:bold; font-size:18px;">Чаты</div>
            <button class="icon-btn" onclick="toggleSearch()">🔍</button>
        </div>
        
        <!-- Поиск -->
        <div id="search-bar">
            <input type="text" id="search-input" placeholder="Введите @ник и нажмите Enter..." onkeypress="if(event.key === 'Enter') searchUser()">
        </div>

        <!-- Список контактов -->
        <div id="contact-list">
            <div class="contact" onclick="openChat('GENERAL')">
                <div style="width:45px;height:45px;background:#5865F2;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px;">🌐</div>
                <div class="contact-info">
                    <div class="contact-name">Общий чат</div>
                    <div class="contact-sub">Писать всем</div>
                </div>
            </div>
            <!-- Остальные добавляются динамически -->
        </div>
    </div>

    <!-- Экран чата -->
    <div id="chat-screen">
        <div id="chat-header">
            <button onclick="closeChat()">← Назад</button>
            <div id="chat-title">Чат</div>
        </div>
        <div id="chat-box"></div>
        <div id="bottom-bar">
            <input type="text" id="msg-input" placeholder="Сообщение..." onkeypress="if(event.key === 'Enter') sendMsg()">
            <button onclick="sendMsg()" style="width:auto; padding:0 15px;">➤</button>
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

        function logout() { localStorage.removeItem('chatUser'); location.reload(); }

        function enterChat() {
            document.getElementById('auth-screen').style.display = 'none';
            document.getElementById('main-screen').style.display = 'flex';
            
            fetch('/join', { method: 'POST', body: JSON.stringify(myData) });
            setInterval(fetchData, 1500);
        }

        function toggleSearch() {
            let bar = document.getElementById('search-bar');
            bar.style.display = bar.style.display === 'block' ? 'none' : 'block';
            if (bar.style.display === 'block') document.getElementById('search-input').focus();
        }

        function searchUser() {
            const query = document.getElementById('search-input').value.trim();
            if (!query || query === myData.nick) return;
            
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
            toggleSearch(); // Скрываем поиск
            openChat(query); // Сразу открываем чат
        }

        function openChat(chatId) {
            currentChat = chatId;
            lastMsgCount = 0;
            document.getElementById('chat-title').innerText = chatId === 'GENERAL' ? 'Общий чат' : `@${chatId}`;
            document.getElementById('main-screen').style.display = 'none';
            document.getElementById('chat-screen').style.display = 'flex';
        }

        function closeChat() {
            document.getElementById('chat-screen').style.display = 'none';
            document.getElementById('main-screen').style.display = 'flex';
        }

        function fetchData() {
            fetch('/data').then(r => r.json()).then(data => {
                // Обновляем список контактов (только тех, кто в сети)
                const list = document.getElementById('contact-list');
                Object.keys(data.users).forEach(u => {
                    if (u !== myData.nick && !document.getElementById('contact-' + u)) {
                        let html = `<div class="contact" id="contact-${u}" onclick="openChat('${u}')">
                            <img src="${data.users[u].avatar}">
                            <div class="contact-info">
                                <div class="contact-name">@${u}</div>
                                <div class="contact-sub">В сети</div>
                            </div>
                        </div>`;
                        list.insertAdjacentHTML('beforeend', html);
                    }
                });

                // Если открыт чат - обновляем сообщения
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
            self.wfile.write(json.dumps({
                "general": messages, 
                "private": private_msgs,
                "users": users
            }).encode('utf-8'))
        else: self.send_error(404)

    def do_POST(self):
        l = int(self.headers['Content-Length'])
        d = json.loads(self.rfile.read(l).decode())
        
        if self.path == '/join': 
            users[d['nick']] = {"avatar": d['avatar']}
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
        print("Сервер v7.0 запущен")
        httpd.serve_forever()
