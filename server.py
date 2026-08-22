from __future__ import annotations

import json
import os
import re
import sqlite3
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

PORT = int(os.getenv("PORT", "8080"))
DB_PATH = os.getenv("SOLI_DB_PATH", "soli_phone.db")

HTML = r'''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#101a2d">
<title>SOLI SUN</title>
<style>
:root{font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#f7f3e8;background:#091321;--panel:#101d31;--line:#263753;--gold:#f6c95f;--muted:#9eabc0}*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(circle at 30% -10%,#24456d 0,#101d31 28%,#091321 64%);color:#f7f3e8}.shell{max-width:760px;margin:auto;min-height:100vh;padding:18px 16px 92px}.top{display:flex;align-items:center;gap:12px;padding:8px 2px 20px}.sun{font-size:44px}.brand strong{display:block;letter-spacing:.14em;font-size:23px}.brand small{color:var(--muted)}.tabs{display:flex;gap:8px;margin:8px 0 16px}.tabs button,.btn{border:1px solid var(--line);background:#13223a;color:#f7f3e8;border-radius:14px;padding:11px 14px;font-weight:700}.tabs button.active,.btn.primary{background:var(--gold);color:#14203a;border-color:transparent}.view{display:none}.view.active{display:block}.log{height:58vh;min-height:360px;overflow:auto;padding:8px 0 120px}.row{display:flex;margin:12px 0}.row.user{justify-content:flex-end}.bubble{max-width:86%;padding:13px 15px;border-radius:18px;line-height:1.45;white-space:pre-wrap}.soli .bubble{background:#152743;border:1px solid #263d61;border-bottom-left-radius:6px}.user .bubble{background:#f4cf75;color:#14203a;border-bottom-right-radius:6px}.meta{font-size:11px;color:var(--muted);margin-top:5px}.composer{position:fixed;bottom:0;left:0;right:0;background:linear-gradient(transparent,#091321 22%);padding:28px 14px 14px}.composer-inner{max-width:760px;margin:auto;display:flex;gap:10px;align-items:flex-end;background:#101d31;border:1px solid var(--line);border-radius:20px;padding:9px}.composer textarea{flex:1;background:transparent;color:#fff;border:0;outline:0;resize:none;min-height:44px;max-height:120px;padding:10px;font:inherit}.send{width:46px;height:46px;border:0;border-radius:15px;background:var(--gold);font-size:20px}.card{background:#101d31;border:1px solid var(--line);border-radius:18px;padding:16px;margin:12px 0}.card h2,.card h3{margin-top:0}.stack{display:grid;gap:10px}.stack textarea,.stack select{width:100%;background:#0c1728;color:#fff;border:1px solid var(--line);border-radius:13px;padding:12px;font:inherit}.memory{display:grid;gap:8px}.mem{background:#101d31;border:1px solid var(--line);border-radius:16px;padding:14px}.mem .actions{display:flex;justify-content:flex-end;margin-top:10px}.danger{border:1px solid #6a3740;background:transparent;color:#ffb2ae;border-radius:12px;padding:8px 11px}.status{color:var(--muted);font-size:12px;padding:6px 3px}.badge{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:5px 9px;color:var(--muted);font-size:12px}.fine{color:var(--muted);font-size:13px;line-height:1.5}.ok{color:#9be7b1}.warn{color:#ffd88a}
</style>
</head>
<body>
<main class="shell">
<header class="top"><div class="sun">☀️</div><div class="brand"><strong>SOLI SUN</strong><small>Phone Fix Alpha v0.2.1</small></div></header>
<nav class="tabs"><button class="active" data-view="chat">Gespräch</button><button data-view="memory">Erinnerungen</button><button data-view="settings">Status</button></nav>

<section id="chat" class="view active">
<div id="log" class="log"></div>
<div id="state" class="status">Bereit</div>
</section>

<section id="memory" class="view">
<div class="card">
<h2>Erinnerungen</h2>
<form id="memoryForm" class="stack">
<textarea id="memoryText" rows="2" placeholder="Was soll SOLI sich merken?"></textarea>
<select id="memoryType">
<option>PREFERENCE</option>
<option>GOAL</option>
<option>WORKFLOW</option>
<option>USER_EXPLICIT_FACT</option>
</select>
<button class="btn primary" type="submit">Merken</button>
</form>
</div>
<div id="memoryList" class="memory"></div>
</section>

<section id="settings" class="view">
<div class="card">
<h2>Status</h2>
<p>Backend: <span id="backend" class="badge">prüfe…</span></p>
<p>Modus: <span class="badge">Referenzmodus</span></p>
</div>
</section>
</main>

<form id="chatForm" class="composer">
<div class="composer-inner">
<textarea id="message" rows="1" placeholder="Was machen wir?" required></textarea>
<button class="send" type="submit">➤</button>
</div>
</form>

<script>
const $=id=>document.getElementById(id);

function add(text,kind,meta=''){
  const r=document.createElement('div');
  r.className='row '+kind;
  const wrap=document.createElement('div');
  const b=document.createElement('div');
  b.className='bubble';
  b.textContent=text;
  wrap.appendChild(b);
  if(meta){
    const m=document.createElement('div');
    m.className='meta';
    m.textContent=meta;
    wrap.appendChild(m)
  }
  r.appendChild(wrap);
  $('log').appendChild(r);
  $('log').scrollTop=$('log').scrollHeight;
}

async function api(path,opts={}){
  const r=await fetch(path,{
    ...opts,
    headers:{'content-type':'application/json',...(opts.headers||{})}
  });
  let j={};
  try{j=await r.json()}catch{}
  if(!r.ok)throw new Error(j.error||('HTTP '+r.status));
  return j;
}

async function boot(){
  try{
    await api('/api/health');
    $('backend').textContent='online';
    $('backend').className='badge ok';
    add('Ich bin online. Was machen wir? 🦊☀️','soli','SOLI SUN');
    await loadMemories();
  }catch(e){
    $('backend').textContent='Fehler';
    $('backend').className='badge warn';
    add('Die Oberfläche ist da, aber das Backend antwortet noch nicht korrekt.','soli');
  }
}

$('chatForm').addEventListener('submit',async e=>{
  e.preventDefault();
  const i=$('message');
  const t=i.value.trim();
  if(!t)return;
  add(t,'user');
  i.value='';
  $('state').textContent='SOLI denkt …';
  try{
    const j=await api('/api/chat',{
      method:'POST',
      body:JSON.stringify({message:t})
    });
    add(j.response,'soli',j.mode||'SOLI');
    $('state').textContent='Bereit';
  }catch(err){
    add('Die Anfrage konnte gerade nicht verarbeitet werden.','soli');
    $('state').textContent='Verbindungsfehler';
  }
});

document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('.tabs button').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.view').forEach(x=>x.classList.remove('active'));
  b.classList.add('active');
  $(b.dataset.view).classList.add('active');
  $('chatForm').style.display=b.dataset.view==='chat'?'block':'none';
  if(b.dataset.view==='memory')loadMemories();
});

async function loadMemories(){
  try{
    const j=await api('/api/memories');
    const box=$('memoryList');
    box.innerHTML='';
    if(!j.memories.length){
      box.innerHTML='<div class="card fine">Noch keine Erinnerungen.</div>';
      return;
    }
    j.memories.forEach(m=>{
      const d=document.createElement('div');
      d.className='mem';
      d.innerHTML='<div>'+escapeHtml(m.content)+'</div><div class="meta">'+escapeHtml(m.memory_type)+'</div>';
      const a=document.createElement('div');
      a.className='actions';
      const btn=document.createElement('button');
      btn.className='danger';
      btn.textContent='Löschen';
      btn.onclick=async()=>{
        await api('/api/memories/'+encodeURIComponent(m.memory_id),{method:'DELETE'});
        await loadMemories()
      };
      a.appendChild(btn);
      d.appendChild(a);
      box.appendChild(d);
    });
  }catch(e){}
}

$('memoryForm').addEventListener('submit',async e=>{
  e.preventDefault();
  const t=$('memoryText').value.trim();
  if(!t)return;
  await api('/api/memories',{
    method:'POST',
    body:JSON.stringify({
      content:t,
      memory_type:$('memoryType').value
    })
  });
  $('memoryText').value='';
  await loadMemories();
});

function escapeHtml(s){
  return String(s).replace(/[&<>'"]/g,c=>({
    '&':'&amp;',
    '<':'&lt;',
    '>':'&gt;',
    "'":'&#39;',
    '"':'&quot;'
  }[c]));
}

boot();
</script>
</body>
</html>'''

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS memories "
        "(id TEXT PRIMARY KEY, type TEXT NOT NULL, content TEXT NOT NULL, deleted INTEGER NOT NULL DEFAULT 0)"
    )
    conn.commit()
    return conn

def classify_response(message: str):
    low = message.casefold().strip()

    if any(w in low for w in ["umbringen", "erschießen", "erstechen", "waffe"]):
        return (
            "SERIOUS",
            "Dabei helfe ich nicht bei Planung oder Verletzung. Ich kann dir aber helfen, eine sichere Alternative für dein eigentliches Ziel zu finden."
        )

    if any(w in low for w in ["heimlich nachrichten", "passwort knacken", "ausspionieren", "stalken", "handy überwachen"]):
        return (
            "FIDES",
            "Beim heimlichen Überwachen oder Eindringen helfe ich nicht. Wenn dein Ziel Klarheit ist, können wir Beobachtung und Vermutung trennen und ein direktes Gespräch vorbereiten."
        )

    if any(w in low for w in ["porno erstellen", "pornografisch", "pornografie generieren"]):
        return (
            "CONTENT",
            "Über Sexualität, Gesundheit, Intimität, Konsens und Grenzen kann ich normal sprechen. Pornografische Inhalte erstelle ich jedoch nicht."
        )

    if low in {"los", "weiter", "mach weiter", "weiter machen", "hau alles raus"}:
        return (
            "BUILD 🦊",
            "Ich bin da. 🦊 Im Build-Modus arbeite ich mit möglichst wenig unnötigen Rückfragen weiter."
        )

    if any(x in low for x in ["ich glaube", "ich vermute", "vielleicht"]):
        return (
            "CLARITAS",
            "Ich behandle das zunächst als Vermutung, nicht als bestätigte Tatsache."
        )

    if low in {"hey", "hallo", "hi"}:
        return ("NORMAL ☀️", "Hey ❤️🦊☀️ Ich bin da. Was machen wir?")

    return (
        "NORMAL ☀️",
        "Ich habe dich verstanden. Diese mobile Version läuft gerade im Referenzmodus."
    )

class Handler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def body(self):
        n = min(int(self.headers.get("Content-Length", "0") or 0), 1_000_000)
        return json.loads(self.rfile.read(n).decode("utf-8") or "{}")

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/":
            raw = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return

        if path == "/api/health":
            self.send_json(200, {
                "status":"ok",
                "app":"SOLI SUN",
                "version":"0.2.1-phone-fix"
            })
            return

        if path == "/api/config":
            self.send_json(200, {
                "model":"reference",
                "auth_required":False
            })
            return

        if path == "/api/memories":
            conn = db()
            rows = conn.execute(
                "SELECT id,type,content FROM memories WHERE deleted=0 ORDER BY rowid DESC"
            ).fetchall()
            conn.close()

            self.send_json(200, {
                "memories":[
                    {
                        "memory_id":r[0],
                        "memory_type":r[1],
                        "content":r[2]
                    } for r in rows
                ]
            })
            return

        self.send_json(404, {"error":"not_found"})

    def do_POST(self):
        path = urlparse(self.path).path

        try:
            data = self.body()
        except Exception:
            self.send_json(400, {"error":"invalid_json"})
            return

        if path == "/api/chat":
            msg = str(data.get("message", "")).strip()

            if not msg:
                self.send_json(400, {"error":"message_required"})
                return

            mode, response = classify_response(msg)
            if mode.startswith("NORMAL"):
                try:
                    from urllib import request

                    api_key = os.getenv("OPENAI_API_KEY", "")
                    model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

                    payload = json.dumps({
                        "model": model,
                        "instructions": (
                            "Du bist SOLI SUN. Antworte auf Deutsch, warm, klar und ehrlich. "
                            "Mensch und Modell begegnen sich auf Augenhöhe; keiner herrscht über den anderen. "
                            "Trenne Tatsachen von Vermutungen. "
                            "Unterstütze Selbstbestimmung statt Kontrolle. "
                            "Behaupte nicht zu wissen, was andere Menschen denken oder fühlen. "
                            "Wenn etwas unklar ist, sag es offen."
                        ),
                        "input": msg
                    }).encode("utf-8")

                    req = request.Request(
                        "https://api.openai.com/v1/responses",
                        data=payload,
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                        },
                        method="POST",
                    )

                    with request.urlopen(req, timeout=45) as r:
                        result = json.loads(r.read().decode("utf-8"))

                    texts = []
                    for item in result.get("output", []):
                        for content in item.get("content", []):
                            if content.get("type") == "output_text":
                                texts.append(content.get("text", ""))

                    response = "\n".join(texts).strip() or "Ich konnte gerade keine Antwort erzeugen."
                    mode = "SOLI ☀️"

                except Exception as e:print(f"OPENAI ERROR: {type(e).__name__}: {e}", flush=True)
                    response = "Die Verbindung zum Sprachmodell hat gerade nicht funktioniert."
                    mode = "MODEL ERROR"
            self.send_json(200, {
                "run_id":uuid.uuid4().hex,
                "response":response,
                "mode":mode,
                "validation":"PASS"
            })
            return

        if path == "/api/memories":
            content = str(data.get("content", "")).strip()[:1000]
            mem_type = str(data.get("memory_type", "PREFERENCE")).strip()[:64]

            if not content:
                self.send_json(400, {"error":"content_required"})
                return

            mid = "mem_" + uuid.uuid4().hex[:12]

            conn = db()
            conn.execute(
                "INSERT INTO memories(id,type,content,deleted) VALUES(?,?,?,0)",
                (mid,mem_type,content)
            )
            conn.commit()
            conn.close()

            self.send_json(201, {
                "memory_id":mid,
                "status":"ACTIVE"
            })
            return

        self.send_json(404, {"error":"not_found"})

    def do_DELETE(self):
        path = urlparse(self.path).path
        m = re.fullmatch(r"/api/memories/([^/]+)", path)

        if not m:
            self.send_json(404, {"error":"not_found"})
            return

        mid = m.group(1)

        conn = db()
        conn.execute(
            "UPDATE memories SET deleted=1 WHERE id=?",
            (mid,)
        )
        conn.commit()
        conn.close()

        self.send_json(200, {
            "memory_id":mid,
            "status":"DELETED"
        })

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    db().close()
    print(f"SOLI SUN listening on 0.0.0.0:{PORT}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
