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
    <title>Мессенджер v6.0</title>
    <style>
        :root { --bg: #0d1117; --panel: #161b22; --text: #c9d1d9; --border: #30363d; --accent: #58a6ff; --green: #238636; }
        html, body { margin: 0; padding: 0; width: 100%; height: 100%; background: var(--bg); color: var(--text); font-family: sans-serif; overflow: hidden; display: flex; flex-direction: column; }
        
        #auth-screen { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 20px; }
        .auth-box { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 25px; width: 100%; max-width: 350px; }
        input { width: 100%; padding: 12px; margin-bottom: 12px; background: var(--bg); color: var(--text); border: 1px solid var(--border); border-radius: 6px; box-sizing: border-box; outline: none; }
        button { width: 100%; padding: 12px; background: var(--green); color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; }
        
        #main-screen { display: none; flex-direction: column; height: 100%; }
        #top-bar { background: var(--panel); border-bottom: 1px solid var(--border); padding: 10px; display: flex; justify-content: space-between; align-items: center; }
        .my-profile { display: flex; align-items: center; gap: 10px; }
        .my-profile img { width: 40px; height: 40px; border-radius: 50%; border: 2px solid var(--accent); object-fit: cover; }
        
        #workspace { display: flex; flex-grow: 1; overflow: hidden; }
        #sidebar { width: 35%; background: var(--panel); border-right: 1px solid var(--border); display: flex; flex-direction: column; }
        
        /* Поиск */
        #search-area { padding: 10px; border-bottom: 1px solid var(--border); }
        #search-input { width: 100%; padding: 8px; margin-bottom: 5px; font-size: 14px; }
        #search-btn { padding: 8px; font-size: 14px; }
        
        #contact-list { flex-grow: 1; overflow-y: auto; }
        .contact { padding: 10px; border-bottom: 1px solid var(--border); cursor: pointer; display: flex; align-items: center; gap: 10px; }
        .contact:hover { background: var(--bg); }
        .contact img { width: 30px; height: 30px; border-radius: 50%; }
        .contact.active { background: var(--accent); color: white; }
        
        #chat-area { flex-grow: 1; display: flex; flex-direction: column; overflow: hidden; }
        #chat-header { padding: 10px; border-bottom: 1px solid var(--border); font-weight: bold; background: var(--bg); }
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
        <div id="top-bar">
            <div class="my-profile">
                <img id="my-avatar" src="">
                <span id="my-nick"></span>
            </div>
            <button onclick="logout()" style="width:auto; padding:5px 10px; background:var(--border);">Выйти</button>
        </div>
        
        <div id="workspace">
            <div id="sidebar">
                <div id="search-area">
                    <input type="text" id="search-input" placeholder="Поиск по @нику...">
                    <button onclick="searchUser()" id="search-btn">Найти</button>
                </div>
                <div id="contact-list">
                    <div class="contact active" onclick="openChat('GENERAL', this)" id="contact-general">
                        <div style="width:30px;height:30px;background:#5865F2;border-radius:50%;display:flex;align-items:center;justify-content:center;">🌐</div>
                        <span>Общий чат</span>
                    </div>
                </div>
            </div>
            
            <div id="chat-area">
                <div id="chat-header">Общий чат</div>
                <div id="chat-box"></div>
                <div id="bottom-bar">
                    <input type="text" id="msg-input" placeholder="Сообщение..." onkeypress="if(event.key === 'Enter') sendMsg()">
                    <button onclick="sendMsg()" style="width:auto; padding:0 15px;">➤</button>
                </div>
            </div>
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
            document.getElementById('my-nick').innerText = '@' + myData.nick;
            document.getElementById('my-avatar').src = myData.avatar;
            
            fetch('/join', { method: 'POST', body: JSON.stringify(myData) });
            setInterval(fetchData, 1500);
        }

        function openChat(chatId, element) {
            currentChat = chatId;
            lastMsgCount = 0;
            document.getElementById('chat-header').innerText = chatId === 'GENERAL' ? 'Общий чат' : `Чат с @${chatId}`;
            
            document.querySelectorAll('.contact').forEach(c => c.classList.remove('active'));
            if (element) element.classList.add('active');
        }

        function searchUser() {
            const query = document.getElementById('search-input').value.trim();
            if (!query || query === myData.nick) return;
            
            // Добавляем контакт в список (если его еще нет)
            if (!document.getElementById('contact-' + query)) {
                let html = `<div class="contact" id="contact-${query}" onclick="openChat('${query}', this)">
                    <img src="https://ui-avatars.com/api/?name=${query}&background=random&color=fff">
                    <span>@${query}</span>
                </div>`;
                document.getElementById('contact-list').insertAdjacentHTML('beforeend', html);
            }
            openChat(query, document.getElementById('contact-' + query));
        }

        function fetchData() {
            fetch('/data').then(r => r.json()).then(data => {
                // Обновляем список контактов (только тех, кто в сети)
                const list = document.getElementById('contact-list');
                Object.keys(data.users).forEach(u => {
                    if (u !== myData.nick && !document.getElementById('contact-' + u)) {
                        let html = `<div class="contact" id="contact-${u}" onclick="openChat('${u}', this)">
                            <img src="${data.users[u].avatar}">
                            <span>@${u}</span>
                        </div>`;
                        list.insertAdjacentHTML('beforeend', html);
                    }
                });

                // Сообщения для текущего чата
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
        print("Сервер v6.0 запущен")
        httpd.serve_forever()
