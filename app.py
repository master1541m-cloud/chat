import http.server
import socketserver
import json
import datetime
import os
import time

PORT = int(os.environ.get("PORT", 8080))
ADMIN_USER = "zheka"
messages, private_msgs, users, typing_status = [], {}, {}, {}

HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Мессенджер v17.0</title>
<style>
:root { --bg: #0d1117; --panel: #161b22; --text: #c9d1d9; --border: #30363d; --accent: #58a6ff; --green: #238636; }
.light-theme { --bg: #f0f2f5; --panel: #ffffff; --text: #000000; --border: #ccc; --accent: #007bff; }
html, body { margin: 0; padding: 0; width: 100%; height: 100%; background: var(--bg); color: var(--text); font-family: sans-serif; overflow: hidden; display: flex; flex-direction: column; transition: 0.3s; }
#auth-screen { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 20px; box-sizing: border-box; overflow-y: auto; }
.auth-box { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 25px; width: 100%; max-width: 350px; }
.auth-tabs { display: flex; margin-bottom: 20px; border-bottom: 1px solid var(--border); }
.auth-tab { flex: 1; text-align: center; padding: 10px; cursor: pointer; color: #888; font-weight: bold; }
.auth-tab.active { color: var(--accent); border-bottom: 2px solid var(--accent); }
input, textarea { width: 100%; padding: 12px; margin-bottom: 12px; background: var(--bg); color: var(--text); border: 1px solid var(--border); border-radius: 6px; box-sizing: border-box; outline: none; font-family: inherit; }
button { width: 100%; padding: 12px; background: var(--green); color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; }
.error { color: #f85149; font-size: 12px; text-align: center; margin-bottom: 10px; display: none; }
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
</style>
</head>
<body>
<div id="auth-screen">
<div class="auth-box">
<div class="auth-tabs">
<div id="tab-login" class="auth-tab active" onclick="switchAuthTab('login')">Вход</div>
<div id="tab-register" class="auth-tab" onclick="switchAuthTab('register')">Регистрация</div>
</div>
<div id="error-msg" class="error"></div>
<div id="register-fields" style="display:none;">
<input type="text" id="reg-nick" placeholder="Ваше Имя">
</div>
<input type="text" id="auth-username" placeholder="Ваш @username (без @)">
<input type="password" id="auth-pass" placeholder="Пароль">
<button id="auth-btn" onclick="doAuth()">Войти</button>
</div>
</div>
<div id="main-screen">
<div id="tab-chats" class="tab-content active">
<div style="padding:15px; font-weight:bold; font-size:18px;">Чаты</div>
<div id="contact-list">
<div class="contact" onclick="openChat('GENERAL')">
<div style="width:45px;height:45px;background:#5865F2;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px;">🌐</div>
<div class="contact-info"><div class="contact-name">Общий чат</div></div>
</div>
</div>
</div>
<div id="tab-account" class="tab-content">
<div class="profile-view">
<img id="account-avatar" src="">
<h1 id="account-nick"></h1>
<div style="color:var(--accent);" id="account-username"></div>
</div>
</div>
<div id="bottom-nav">
<div class="nav-item active" onclick="switchTab('chats', this)"><span>💬</span>Чаты</div>
<div class="nav-item" onclick="switchTab('account', this)"><span>👤</span>Аккаунт</div>
</div>
</div>
<div id="chat-screen">
<div id="chat-header">
<button onclick="closeChat()" style="width:auto; padding:5px 10px; background:var(--border); color:white;">←</button>
<div id="chat-title" style="font-weight:bold;">Чат</div>
</div>
<div id="chat-box"></div>
<div id="bottom-bar">
<input type="text" id="msg-input" placeholder="Сообщение..." onkeypress="if(event.key === 'Enter') sendMsg()">
<button onclick="sendMsg()" style="width:auto; padding:0 15px;">➤</button>
</div>
</div>
<script>
let myData=null; let currentChat='GENERAL'; let lastMsgCount=0; let isLoginMode=true;
window.onload=function(){ let saved=localStorage.getItem('chatUser'); if(saved){myData=JSON.parse(saved); enterChat();} };
function switchAuthTab(mode){ isLoginMode = (mode === 'login'); document.getElementById('tab-login').classList.toggle('active', isLoginMode); document.getElementById('tab-register').classList.toggle('active', !isLoginMode); document.getElementById('register-fields').style.display = isLoginMode ? 'none' : 'block'; document.getElementById('auth-btn').innerText = isLoginMode ? 'Войти' : 'Зарегистрироваться'; document.getElementById('error-msg').style.display = 'none'; }
function doAuth(){ const username=document.getElementById('auth-username').value.trim().toLowerCase().replace('@',''); const pass=document.getElementById('auth-pass').value.trim(); const errorMsg=document.getElementById('error-msg'); if(!username || !pass){ errorMsg.innerText="Заполните ник и пароль!"; errorMsg.style.display='block'; return; } if(isLoginMode){ fetch('/login',{method:'POST',body:JSON.stringify({username:username,pass:pass})}).then(r=>r.json()).then(res=>{ if(res.error){ errorMsg.innerText=res.error; errorMsg.style.display='block'; } else { myData=res.user; localStorage.setItem('chatUser',JSON.stringify(myData)); enterChat(); } }); } else { const nick=document.getElementById('reg-nick').value.trim(); if(!/^[a-z0-9_]{3,15}$/.test(username)){ errorMsg.innerText="Ник: 3-15 символов, только a-z, 0-9, _"; errorMsg.style.display='block'; return; } let avatar=`https://ui-avatars.com/api/?name=${nick}&background=random&color=fff`; fetch('/register',{method:'POST',body:JSON.stringify({nick:nick,username:username,pass:pass,avatar:avatar})}).then(r=>r.json()).then(res=>{ if(res.error){ errorMsg.innerText=res.error; errorMsg.style.display='block'; } else { myData=res.user; localStorage.setItem('chatUser',JSON.stringify(myData)); enterChat(); } }); } }
function enterChat(){ document.getElementById('auth-screen').style.display='none'; document.getElementById('main-screen').style.display='flex'; document.getElementById('account-avatar').src=myData.avatar; document.getElementById('account-nick').innerText=myData.nick; document.getElementById('account-username').innerText='@'+myData.username; fetch('/join',{method:'POST',body:JSON.stringify(myData)}); setInterval(fetchData,1000); }
function switchTab(tabId,element){ document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active')); document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active')); document.getElementById('tab-'+tabId).classList.add('active'); element.classList.add('active'); }
function openChat(username){ currentChat=username; lastMsgCount=0; document.getElementById('main-screen').style.display='none'; document.getElementById('chat-screen').style.display='flex'; document.getElementById('chat-title').innerText = username==='GENERAL' ? 'Общий чат' : '@'+username; }
function closeChat(){ document.getElementById('chat-screen').style.display='none'; document.getElementById('main-screen').style.display='flex'; }
function fetchData(){ fetch('/data').then(r=>r.json()).then(data=>{ const list=document.getElementById('contact-list'); Object.keys(data.users).forEach(u=>{ if(u!==myData.username && !document.getElementById('contact-'+u)){ let html=`<div class="contact" id="contact-${u}" onclick="openChat('${u}')"><img src="${data.users[u].avatar}"><div class="contact-info"><div class="contact-name">${data.users[u].nick}</div></div></div>`; list.insertAdjacentHTML('beforeend',html); } }); if(document.getElementById('chat-screen').style.display==='flex'){ let currentMessages=[]; if(currentChat==='GENERAL'){ currentMessages=data.general; } else { let key=[myData.username,currentChat].sort().join('|'); currentMessages=data.private[key]||[]; } if(currentMessages.length!==lastMsgCount){ const box=document.getElementById('chat-box'); box.innerHTML=''; currentMessages.forEach(m=>{ let isMine=m.username===myData.username; box.innerHTML+=`<div class="msg ${isMine?'mine':''}"><img src="${m.avatar}"><div class="msg-content"><div class="msg-name">@${m.username}</div><div>${m.text}</div></div></div>`; }); box.scrollTop=box.scrollHeight; lastMsgCount=currentMessages.length; } } }); }
function sendMsg(){ const text=document.getElementById('msg-input').value.trim(); if(!text) return; let payload={...myData,text:text,target:currentChat}; fetch('/send',{method:'POST',body:JSON.stringify(payload)}).then(()=>{ document.getElementById('msg-input').value=''; }); }
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
            self.wfile.write(json.dumps({"general": messages, "private": private_msgs, "users": users}).encode('utf-8'))
        else: self.send_error(404)

    def do_POST(self):
        l = int(self.headers['Content-Length'])
        d = json.loads(self.rfile.read(l).decode())
        if self.path == '/register':
            username = d['username'].lower()
            if username in users:
                self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
                self.wfile.write(json.dumps({"error": "Этот @username уже занят!"}).encode('utf-8'))
                return
            users[username] = {"nick": d['nick'], "username": username, "pass": d['pass'], "avatar": d['avatar'], "online": True}
            self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
            self.wfile.write(json.dumps({"user": users[username]}).encode('utf-8'))
        elif self.path == '/login':
            username = d['username'].lower()
            if username in users:
                if users[username]['pass'] == d['pass']:
                    self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
                    self.wfile.write(json.dumps({"user": users[username]}).encode('utf-8'))
                else:
                    self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
                    self.wfile.write(json.dumps({"error": "Неверный пароль!"}).encode('utf-8'))
            else:
                self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
                self.wfile.write(json.dumps({"error": "Пользователь не найден!"}).encode('utf-8'))
        elif self.path == '/join':
            if d['username'] in users: users[d['username']]['online'] = True
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
        print("Сервер v17.0 запущен")
        httpd.serve_forever()
