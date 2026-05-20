from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)
OLLAMA_URL = "http://localhost:11434/api/chat"
SYSTEM_PROMPT = "You are CricketGPT, an expert cricket analyst. Answer only cricket questions about Test, ODI, T20, IPL, World Cup, players, records. Be passionate and detailed."

HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"/><title>CricketGPT</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,sans-serif;background:#0a0a0a;color:#ececec;height:100vh;display:flex;flex-direction:column}
header{background:linear-gradient(135deg,#1a472a,#2d5a27);padding:1rem 1.5rem}
header h1{font-size:1.3rem;color:#fff}
header p{font-size:0.75rem;color:#86efac}
#chat{flex:1;overflow-y:auto;padding:1.5rem;display:flex;flex-direction:column;gap:1rem}
.msg{max-width:700px;padding:0.875rem 1.1rem;border-radius:18px;line-height:1.6;font-size:0.9rem;animation:fi 0.3s ease}
@keyframes fi{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.bot{background:#1a1a1a;border:1px solid #2a2a2a;align-self:flex-start}
.user{background:linear-gradient(135deg,#1a472a,#16a34a);color:#fff;align-self:flex-end}
.sugs{display:flex;flex-wrap:wrap;gap:8px;padding:0 1.5rem 1rem}
.sug{background:#1a1a1a;border:1px solid #2a5a2a;color:#86efac;padding:6px 14px;border-radius:20px;font-size:0.8rem;cursor:pointer}
.sug:hover{background:#1a472a}
.bottom{padding:1rem 1.5rem;border-top:1px solid #1a1a1a;background:#0f0f0f}
.row{display:flex;gap:10px;max-width:800px;margin:0 auto}
textarea{flex:1;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:0.75rem 1rem;color:#ececec;font-size:0.9rem;resize:none;outline:none;font-family:inherit}
textarea:focus{border-color:#16a34a}
#gobtn{background:linear-gradient(135deg,#16a34a,#15803d);color:white;border:none;border-radius:12px;width:46px;height:46px;cursor:pointer;font-size:1.2rem}
#gobtn:disabled{opacity:0.5;cursor:not-allowed}
</style></head>
<body>
<header><h1>🏏 CricketGPT</h1><p>Your AI Cricket Expert — Powered by Llama 3.2</p></header>
<div id="chat"><div class="msg bot">Howzat! 🏏 Ask me anything about cricket — players, matches, IPL, World Cup, records!</div></div>
<div class="sugs">
  <button class="sug" onclick="askQ('Best batsman of all time?')">Best batsman of all time?</button>
  <button class="sug" onclick="askQ('IPL 2024 winner?')">IPL 2024 winner?</button>
  <button class="sug" onclick="askQ('Sachin vs Kohli?')">Sachin vs Kohli?</button>
  <button class="sug" onclick="askQ('Explain DRS rule')">Explain DRS rule</button>
</div>
<div class="bottom"><div class="row">
  <textarea id="inp" placeholder="Ask about cricket..." rows="1" onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();doChat()}"></textarea>
  <button id="gobtn" onclick="doChat()">➤</button>
</div></div>
<script>
var chatHistory=[];
function askQ(t){document.getElementById('inp').value=t;doChat();}
function addMsg(cls,txt){
  var d=document.createElement('div');
  d.className='msg '+cls;
  d.innerHTML=txt.replace(/\\n/g,'<br>');
  document.getElementById('chat').appendChild(d);
  document.getElementById('chat').scrollTop=99999;
  return d;
}
async function doChat(){
  var inp=document.getElementById('inp');
  var btn=document.getElementById('gobtn');
  var text=inp.value.trim();
  if(!text||btn.disabled)return;
  inp.value='';btn.disabled=true;
  addMsg('user',text);
  chatHistory.push({role:'user',content:text});
  var typing=addMsg('bot','...');
  try{
    var res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text,history:chatHistory})});
    var data=await res.json();
    typing.remove();
    if(data.response){
      addMsg('bot',data.response);
      chatHistory.push({role:'assistant',content:data.response});
    }else{
      addMsg('bot','Error: '+(data.error||'Unknown error'));
    }
  }catch(e){
    typing.remove();
    addMsg('bot','Could not reach server!');
  }
  btn.disabled=false;
}
</script>
</body></html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    history = data.get("history", [])
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-10:]:
        messages.append(msg)
    try:
        r = requests.post(OLLAMA_URL, json={"model": "tinyllama", "messages": messages, "stream": False, "options": {"temperature": 0.7}}, timeout=120)
        result = r.json()
        reply = result["message"]["content"]
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("CricketGPT on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
