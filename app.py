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
<title>Мессенджер v16.0</title>
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
.avatar-upload { text-align: center; margin-bottom: 15px; }
.avatar-preview { width: 80px; height: 80px; border-radius: 50%; border: 2px solid var(--border); object-fit: cover; margin-bottom: 10px; display: none; background: #000; }
.upload-btn { background: var(--border); color: white; padding: 8px; border-radius: 6px; cursor: pointer; display: inline-block; font-size: 14px; margin-bottom: 10px; }
#main-screen { display: none; flex-direction: column; height: 100%; position: relative; }
.tab-content { flex-grow: 1; overflow-y: auto; display: none; padding-bottom: 60px; }
.tab-content.active { display: block; }
.contact { padding: 15px; border-bottom: 1px solid var(--border); cursor: pointer; display: flex; align-items: center; gap: 15px; }
.contact:hover { background: var(--panel); }
.contact img { width: 45px; height: 45px; border-radius: 50%; }
.contact-info { display: flex; flex-direction: column; flex-grow: 1; }
.contact-name { font-weight: bold; font-size: 16px; }
.contact-sub { font-size: 12px; color: #888; }
.online-dot { width: 10px; height: 10px; background: #2ea043; border-radius: 50%; display: inline-block; margin-right: 5px; }
.profile-view { text-align: center; padding: 40px 20px; }
.profile-view img { width: 120px; height: 120px; border-radius: 50%; border: 3px solid var(--accent); object-fit: cover; margin-bottom: 20px; }
.profile-view h1 { margin: 0; color: var(--text); }
.profile-view p { color: #888; margin-top: 5px; font-style: italic; }
.settings-section { background: var(--panel); margin: 15px; border-radius: 10px; overflow: hidden; }
.settings-item { padding: 15px; display: flex; align-items: center; gap: 15px; border-bottom: 1px solid var(--border); cursor: pointer; }
.settings-item:last-child { border-bottom: none; }
.settings-icon { width: 35px; height: 35px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.settings-text { display: flex; flex-direction: column; flex-grow: 1; }
.settings-title { font-size: 16px; color: var(--text); }
.settings-desc { font-size: 12px; color: #888; }
#bottom-nav { position: absolute; bottom: 0; left: 0; width: 100%; background: var(--panel); border-top: 1px solid var(--border); display: flex; justify-content: space-around; padding: 10px 0; z-index: 20; }
.nav-item { display: flex; flex-direction: column; align-items: center; color: #888; cursor: pointer; font-size: 12px; }
.nav-item.active { color: var(--accent); }
.nav-item span { font-size: 20px; margin-bottom: 2px; }
#chat-screen { display: none; flex-direction: column; height: 100%; position: absolute; top: 0; left: 0; width: 100%; background: var(--bg); z-index: 30; }
#chat-header { padding: 10px 15px; border-bottom: 1px solid var(--border); background: var(--panel); display: flex; align-items: center; gap: 15px; }
#chat-header button { width: auto; padding: 5px 10px; background: var(--border); color: var(--text); }
.chat-header-info { display: flex; align-items: center; gap: 10px; flex-grow: 1; cursor: pointer; }
.chat-header-info img { width: 35px; height: 35px; border-radius: 50%; }
.chat-header-name { font-weight: bold; font-size: 15px; }
.chat-header-status { font-size: 12px; color: #888; }
#chat-box { flex-grow: 1; overflow-y: scroll; padding: 15px; display: flex; flex-direction: column; gap: 10px; }
.msg { display: flex; gap: 10px; max-width: 90%; position: relative; }
.msg.mine { align-self: flex-end; flex-direction: row-reverse; }
.msg img.avatar { width: 30px; height: 30px; border-radius: 50%; }
.msg-content { background: var(--panel); padding: 8px 12px; border-radius: 10px; border: 1px solid var(--border); position: relative; }
.msg.mine .msg-content { background: #1f6feb; color: white; }
.msg-name { font-size: 11px; color: var(--accent); font-weight: bold; margin-bottom: 3px; }
.msg.mine .msg-name { color: #c9d1d9; text-align: right; }
.msg-img { max-width: 200px; border-radius: 5px; margin-top: 5px; display: block; }
.delete-btn { position: absolute; top: 5px; right: 5px; background: #f85149; color: white; border: none; border-radius: 50%; width: 20px; height: 20px; font-size: 12px; cursor: pointer; display: none; }
#bottom-bar { background: var(--panel); padding: 10px; border-top: 1px solid var(--border); display: flex; gap: 10px; align-items: center; }
#msg-input { margin-bottom: 0; flex-grow: 1; }
.icon-btn { background: none; border: none; color: var(--accent); font-size: 24px; cursor: pointer; padding: 0 5px; width: auto; }
#search-bar { display: none; padding: 10px; background: var(--panel); border-bottom: 1px solid var(--border); }
.modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 100; justify-content: center; align-items: center; }
.modal-content { background: var(--panel); border-radius: 15px; padding: 20px; width: 80%; max-width: 300px; text-align: center; position: relative; }
.close-modal { position: absolute; top: 10px; right: 15px; font-size: 24px; cursor: pointer; color: #888; }
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
<div class="avatar-upload">
<img id="avatar-preview" class="avatar-preview" src="">
<label for="avatar-file" class="upload-btn">📷 Выбрать аватарку</label>
<input type="file" id="avatar-file" accept="image/*" style="display:none;" onchange="previewAvatar(event)">
</div>
<input type="text" id="reg-nick" placeholder="Ваше Имя">
<textarea id="reg-bio" placeholder="О себе" rows="2"></textarea>
</div>
<input type="text" id="auth-username" placeholder="Ваш @username (без @)">
<input type="password" id="auth-pass" placeholder="Пароль">
<button id="auth-btn" onclick="doAuth()">Войти</button>
</div>
</div>
<div id="main-screen">
<div id="tab-chats" class="tab-content active">
<div style="display:flex;justify-content:space-between;padding:15px;align-items:center;">
<div style="font-weight:bold;font-size:18px;">Чаты</div>
<div onclick="toggleSearch()" style="cursor:pointer;font-size:20px;">🔍</div>
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
<div style="padding:15px;font-weight:bold;font-size:18px;">Все пользователи</div>
<div id="all-users-list"></div>
</div>
<div id="tab-account" class="tab-content">
<div class="profile-view">
<img id="account-avatar" src="">
<h1 id="account-nick"></h1>
<div style="color:var(--accent);font-size:16px;margin-bottom:10px;" id="account-username"></div>
<p id="account-bio"></p>
<button onclick="openEditProfile()" style="margin-top:20px;width:auto;padding:10px 20px;">Редактировать</button>
</div>
</div>
<div id="tab-settings" class="tab-content">
<div style="padding:15px;font-weight:bold;font-size:22px;">Настройки</div>
<div class="settings-section">
<div class="settings-item" onclick="toggleTheme()">
<div class="settings-icon" style="background:#e0a000;">🎨</div>
<div class="settings-text">
<div class="settings-title">Настройки чатов</div>
<div class="settings-desc">Сменить тему</div>
</div>
</div>
</div>
<div class="settings-section">
<div class="settings-item" onclick="toggleSound()">
<div class="settings-icon" style="background:#e64a4a;">🔔</div>
<div class="settings-text">
<div class="settings-title">Уведомления</div>
<div class="settings-desc" id="sound-status">Звук включен</div>
</div>
</div>
</div>
<div class="settings-section">
<div class="settings-item" onclick="logout()">
<div class="settings-icon" style="background:#888;">🚪</div>
<div class="settings-text">
<div class="settings-title" style="color:#f85149;">Выйти</div>
</div>
</div>
</div>
<div style="text-align:center;color:#555;font-size:12px;margin-top:20px;">Мессенджер v16.0</div>
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
<label for="chat-file" class="icon-btn">📎</label>
<input type="file" id="chat-file" accept="image/*" style="display:none;" onchange="sendImage(event)">
<input type="text" id="msg-input" placeholder="Сообщение..." oninput="notifyTyping()" onkeypress="if(event.key === 'Enter') sendMsg()">
<button onclick="sendMsg()" style="width:auto;padding:0 15px;">➤</button>
</div>
</div>
<div id="profile-modal" class="modal" onclick="closeModal('profile-modal')">
<div class="modal-content" onclick="event.stopPropagation()">
<span class="close-modal" onclick="closeModal('profile-modal')">×</span>
<img id="profile-avatar" style="width:100px;height:100px;border-radius:50%;margin-bottom:15px;">
<h2 id="profile-nick"></h2>
<div style="color:var(--accent);margin-bottom:10px;" id="profile-username"></div>
<p id="profile-bio" style="font-style:italic;color:#888;"></p>
<p id="profile-status"></p>
</div>
</div>
<div id="edit-modal" class="modal" onclick="closeModal('edit-modal')">
<div class="modal-content" onclick="event.stopPropagation()">
<span class="close-modal" onclick="closeModal('edit-modal')">×</span>
<h2>Редактировать</h2>
<img id="edit-avatar-preview" style="width:80px;height:80px;border-radius:50%;margin-bottom:10px;">
<label for="edit-avatar-file" style="color:var(--accent);cursor:pointer;display:block;margin-bottom:10px;">📷 Сменить фото</label>
<input type="file" id="edit-avatar-file" accept="image/*" style="display:none;" onchange="previewEditAvatar(event)">
<input type="text" id="edit-nick" placeholder="Имя">
<textarea id="edit-bio" placeholder="О себе" rows="2"></textarea>
<button onclick="saveProfile()">Сохранить</button>
</div>
</div>
<script>
let myData=null; let currentChat='GENERAL'; let lastMsgCount=0; let currentAvatarBase64=""; let editAvatarBase64=""; let soundEnabled=true; let isLoginMode=true;
window.onload=function(){ let saved=localStorage.getItem('chatUser'); if(saved){myData=JSON.parse(saved); enterChat();} if(localStorage.getItem('theme')==='light') document.body.classList.add('light-theme'); };
function switchAuthTab(mode){ isLoginMode = (mode === 'login'); document.getElementById('tab-login').classList.toggle('active', isLoginMode); document.getElementById('tab-register').classList.toggle('active', !isLoginMode); document.getElementById('register-fields').style.display = isLoginMode ? 'none' : 'block'; document.getElementById('auth-btn').innerText = isLoginMode ? 'Войти' : 'Зарегистрироваться'; document.getElementById('error-msg').style.display = 'none'; }
function playSound(){ if(!soundEnabled) return; const audioCtx=new (window.AudioContext||window.webkitAudioContext)(); const osc=audioCtx.createOscillator(); const gain=audioCtx.createGain(); osc.type='sine'; osc.frequency.setValueAtTime(800,audioCtx.currentTime); gain.gain.setValueAtTime(0.1,audioCtx.currentTime); osc.connect(gain); gain.connect(audioCtx.destination); osc.start(); osc.stop(audioCtx.currentTime+0.1); }
function toggleSound(){ soundEnabled=!soundEnabled; document.getElementById('sound-status').innerText=soundEnabled?"Звук включен":"Звук выключен"; }
function toggleTheme(){ document.body.classList.toggle('light-theme'); localStorage.setItem('theme',document.body.classList.contains('light-theme')?'light':'dark'); }
function previewAvatar(event){ const file=event.target.files[0]; if(!file) return; const reader=new FileReader(); reader.onload=function(e){ const img=new Image(); img.onload=function(){ const canvas=document.createElement('canvas'); canvas.width=150; canvas.height=150; const ctx=canvas.getContext('2d'); const minSize=Math.min(img.width,img.height); ctx.drawImage(img,(img.width-minSize)/2,(img.height-minSize)/2,minSize,minSize,0,0,150,150); currentAvatarBase64=canvas.toDataURL('image/jpeg',0.7); let preview=document.getElementById('avatar-preview'); preview.src=currentAvatarBase64; preview.style.display='block'; }; img.src=e.target.result; }; reader.readAsDataURL(file); }
function previewEditAvatar(event){ const file=event.target.files[0]; if(!file) return; const reader=new FileReader(); reader.onload=function(e){ const img=new Image(); img.onload=function(){ const canvas=document.createElement('canvas'); canvas.width=150; canvas.height=150; const ctx=canvas.getContext('2d'); const minSize=Math.min(img.width,img.height); ctx.drawImage(img,(img.width-minSize)/2,(img.height-minSize)/2,minSize,minSize,0,0,150,150); editAvatarBase64=canvas.toDataURL('image/jpeg',0.7); document.getElementById('edit-avatar-preview').src=editAvatarBase64; }; img.src=e.target.result; }; reader.readAsDataURL(file); }
function doAuth(){ const username=document.getElementById('auth-username').value.trim().toLowerCase().replace('@',''); const pass=document.getElementById('auth-pass').value.trim(); const errorMsg=document.getElementById('error-msg'); if(!username || !pass){ errorMsg.innerText="Заполните ник и пароль!"; errorMsg.style.display='block'; return; } if(isLoginMode){ fetch('/login',{method:'POST',body:JSON.stringify({username:username,pass:pass})}).then(r=>r.json()).then(res=>{ if(res.error){ errorMsg.innerText=res.error; errorMsg.style.display='block'; } else { myData=res.user; localStorage.setItem('chatUser',JSON.stringify(myData)); enterChat(); } }); } else { const nick=document.getElementById('reg-nick').value.trim(); const bio=document.getElementById('reg-bio').value.trim(); if(!/^[a-z0-9_]{3,15}$/.test(username)){ errorMsg.innerText="Ник: 3-15 символов, только a-z, 0-9, _"; errorMsg.style.display='block'; return; } if(!nick){ errorMsg.innerText="Введите имя!"; errorMsg.style.display='block'; return; } let avatar=currentAvatarBase64||`https://ui-avatars.com/api/?name=${nick}&background=random&color=fff`; fetch('/register',{method:'POST',body:JSON.stringify({nick:nick,username:username,pass:pass,avatar:avatar,bio:bio})}).then(r=>r.json()).then(res=>{ if(res.error){ errorMsg.innerText=res.error; errorMsg.style.display='block'; } else { myData=res.user; localStorage.setItem('chatUser',JSON.stringify(myData)); enterChat(); } }); } }
function enterChat(){ document.getElementById('auth-screen').style.display='none'; document.getElementById('main-screen').style.display='flex'; updateProfileUI(); fetch('/join',{method:'POST',body:JSON.stringify(myData)}); setInterval(fetchData,1000); }
function updateProfileUI(){ document.getElementById('account-avatar').src=myData.avatar; document.getElementById('account-nick').innerText=myData.nick; document.getElementById('account-username').innerText='@'+myData.username; document.getElementById('account-bio').innerText=myData.bio||"Без описания"; }
function openEditProfile(){ document.getElementById('edit-nick').value=myData.nick; document.getElementById('edit-bio').value=myData.bio||""; document.getElementById('edit-avatar-preview').src=myData.avatar; document.getElementById('edit-modal').style.display='flex'; }
function saveProfile(){ let newNick=document.getElementById('edit-nick').value.trim(); let newBio=document.getElementById('edit-bio').value.trim(); let newAvatar=editAvatarBase64||myData.avatar; fetch('/update_profile',{method:'POST',body:JSON.stringify({username:myData.username,nick:newNick,bio:newBio,avatar:newAvatar})}).then(r=>r.json()).then(res=>{ if(res.success){ myData.nick=newNick; myData.bio=newBio; myData.avatar=newAvatar; localStorage.setItem('chatUser',JSON.stringify(myData)); updateProfileUI(); closeModal('edit-modal'); } }); }
function logout(){ localStorage.removeItem('chatUser'); location.reload(); }
function switchTab(tabId,element){ document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active')); document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active')); document.getElementById('tab-'+tabId).classList.add('active'); element.classList.add('active'); }
function toggleSearch(){ let bar=document.getElementById('search-bar'); bar.style.display=bar.style.display==='block'?'none':'block'; if(bar.style.display==='block') document.getElementById('search-input').focus(); }
function searchUser(){ const query=document.getElementById('search-input').value.trim().replace('@','').toLowerCase(); if(!query||query===myData.username) return; if(!document.getElementById('contact-'+query)){ let html=`<div class="contact" id="contact-${query}" onclick="openChat('${query}')"><img src="https://ui-avatars.com/api/?name=${query}&background=random&color=fff"><div class="contact-info"><div class="contact-name">@${query}</div><div class="contact-sub">Нажмите, чтобы написать</div></div></div>`; document.getElementById('contact-list').insertAdjacentHTML('beforeend',html); } document.getElementById('search-input').value=''; toggleSearch(); openChat(query); }
function openChat(username){ currentChat=username; lastMsgCount=0; document.getElementById('main-screen').style.display='none'; document.getElementById('chat-screen').style.display='flex'; if(username==='GENERAL'){ document.getElementById('chat-title').innerText='Общий чат'; document.getElementById('chat-avatar').style.display='none'; document.getElementById('chat-status').innerText=''; } else { document.getElementById('chat-title').innerText='@'+username; document.getElementById('chat-avatar').src=`https://ui-avatars.com/api/?name=${username}&background=random&color=fff`; document.getElementById('chat-avatar').style.display='block'; document.getElementById('chat-status').innerText='...'; } }
function closeChat(){ document.getElementById('chat-screen').style.display='none'; document.getElementById('main-screen').style.display='flex'; }
function openProfile(username){ if(username==='GENERAL'||username===myData.username) return; fetch('/get_user/'+username).then(r=>r.json()).then(u=>{ if(u){ document.getElementById('profile-avatar').src=u.avatar; document.getElementById('profile-nick').innerText=u.nick; document.getElementById('profile-username').innerText='@'+u.username; document.getElementById('profile-bio').innerText=u.bio||"Без описания"; document.getElementById('profile-status').innerText=u.online?"В сети":"Не в сети"; document.getElementById('profile-modal').style.display='flex'; } }); }
function closeModal(id){ document.getElementById(id).style.display='none'; }
function notifyTyping(){ if(currentChat==='GENERAL') return; fetch('/typing',{method:'POST',body:JSON.stringify({username:myData.username,target:currentChat})}); }
function fetchData(){ fetch('/data').then(r=>r.json()).then(data=>{ const list=document.getElementById('contact-list'); const allList=document.getElementById('all-users-list'); Object.keys(data.users).forEach(u=>{ let userObj=data.users[u]; if(u!==myData.username){ if(!document.getElementById('contact-'+u)){ let isOnline=userObj.online?'<span class="online-dot"></span>':''; let html=`<div class="contact" id="contact-${u}" onclick="openChat('${u}')"><img src="${userObj.avatar}"><div class="contact-info"><div class="contact-name">${userObj.nick}</div><div class="contact-sub">@${u} | ${isOnline} ${userObj.online?'В сети':'Не в сети'}</div></div></div>`; list.insertAdjacentHTML('beforeend',html); } if(!document.getElementById('all-user-'+u)){ let isOnline=userObj.online?'<span class="online-dot"></span>':''; let html=`<div class="contact" id="all-user-${u}" onclick="openChat('${u}')"><img src="${userObj.avatar}"><div class="contact-info"><div class="contact-name">${userObj.nick}</div><div class="contact-sub">@${u} | ${isOnline} ${userObj.online?'В сети':'Не в сети'}</div></div></div>`; allList.insertAdjacentHTML('beforeend',html); } } }); if(currentChat!=='GENERAL'&&data.users[currentChat]){ let u=data.users[currentChat]; let status=u.online?'В сети':'Не в сети'; if(data.typing&&data.typing[currentChat]) status='печатает...'; document.getElementById('chat-status').innerText=status; } if(document.getElementById('chat-screen').style.display==='flex'){ let currentMessages=[]; if(currentChat==='GENERAL'){ currentMessages=data.general; } else { let key=[myData.username,currentChat].sort().join('|'); currentMessages=data.private[key]||[]; } if(currentMessages.length>lastMsgCount&&currentMessages.length>0){ let lastMsg=currentMessages[currentMessages.length-1]; if(lastMsg.username!==myData.username) playSound(); } if(currentMessages.length!==lastMsgCount){ const box=document.getElementById('chat-box'); box.innerHTML=''; currentMessages.forEach((m,idx)=>{ let isMine=m.username===myData.username; let imgHtml=m.image?`<br><img src="${m.image}" class="msg-img">`:''; let delBtn=(myData.username===ADMIN_USER||isMine)?`<button class="delete-btn" style="display:block;" onclick="deleteMsg(${idx})">×</button>`:''; box.innerHTML+=`<div class="msg ${isMine?'mine':''}">${delBtn}<img class="avatar" src="${m.avatar}"><div class="msg-content"><div class="msg-name">@${m.username} (${m.time})</div><div>${m.text}${imgHtml}</div></div></div>`; }); box.scrollTop=box.scrollHeight; lastMsgCount=currentMessages.length; } } }); }
function sendMsg(){ const text=document.getElementById('msg-input').value.trim(); if(!text) return; let payload={...myData,text:text,target:currentChat}; fetch('/send',{method:'POST',body:JSON.stringify(payload)}).then(()=>{ document.getElementById('msg-input').value=''; }); }
function sendImage(event){ const file=event.target.files[0]; if(!file) return; const reader=new FileReader(); reader.onload=function(e){ const img=new Image(); img.onload=function(){ const canvas=document.createElement('canvas'); canvas.width=400; canvas.height=img.height*(400/img.width); const ctx=canvas.getContext('2d'); ctx.drawImage(img,0,0,canvas.width,canvas.height); const b64=canvas.toDataURL('image/jpeg',0.7); let payload={...myData,text:"Фото",image:b64,target:currentChat}; fetch('/send',{method:'POST',body:JSON.stringify(payload)}); }; img.src=e.target.result; }; reader.readAsDataURL(file); }
function deleteMsg(idx){ if(confirm("Удалить?")){ fetch('/delete',{method:'POST',body:JSON.stringify({index:idx,target:currentChat,username:myData.username})}); } }
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
            username = d['username'].lower()
            if username in users:
                self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
                self.wfile.write(json.dumps({"error": "Этот @username уже занят!"}).encode('utf-8'))
                return
            users[username] = {"nick": d['nick'], "username": username, "pass": d['pass'], "avatar": d['avatar'], "bio": d['bio'], "last_seen": time.time(), "online": True}
            self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
            self.wfile.write(json.dumps({"user": users[username]}).encode('utf-8'))
        elif self.path == '/login':
            username = d['username'].lower()
            if username in users:
                if users[username]['pass'] == d['pass']:
                    users[username]['last_seen'] = time.time()
                    self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
                    self.wfile.write(json.dumps({"user": users[username]}).encode('utf-8'))
                else:
                    self.send_response(200); self.send_header('Content-type', 'application/json'); self.end_headers()
                    self.wfile.write(json.dumps({"error": "Неверный пароль!"}).encode('utf-8'))
            else:
                self.send_response(200); self.send_header('Content
