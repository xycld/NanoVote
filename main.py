import sqlite3
import uuid
import time
import json
import logging
import os
import uvicorn
from typing import List
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, field_validator
from jinja2 import Environment, DictLoader, select_autoescape

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NanoVote")

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "9527"))

DATA_DIR = os.getenv("DATA_DIR", ".")
DB_NAME = "nanovote.db"
DB_FILE = os.path.join(DATA_DIR, DB_NAME)

MAX_POLLS = 1000
CACHE_TTL = 60

if DATA_DIR != "." and not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

VOTE_CACHE = {}

app = FastAPI(title="NanoVote", docs_url=None, redoc_url=None)

def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS polls (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON polls(created_at);")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id TEXT NOT NULL,
            text TEXT NOT NULL,
            votes INTEGER DEFAULT 0,
            FOREIGN KEY (poll_id) REFERENCES polls (id) ON DELETE CASCADE
        );
        """)
        conn.commit()
        logger.info(f"🚀 数据库初始化完成: {DB_FILE}")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
    finally:
        if 'conn' in locals(): conn.close()

init_db()

HTML_BASE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - NanoVote</title>
    <link rel="preconnect" href="https://cdn.tailwindcss.com">
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    animation: {
                        'fade-in-up': 'fadeInUp 0.5s ease-out forwards',
                    },
                    keyframes: {
                        fadeInUp: {
                            '0%': { opacity: '0', transform: 'translateY(10px)' },
                            '100%': { opacity: '1', transform: 'translateY(0)' },
                        }
                    }
                }
            }
        }
    </script>
    <style>
        [x-cloak] { display: none !important; }
        .progress-bar { transition: width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1); }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 antialiased min-h-screen flex flex-col">
    <header class="w-full p-6 flex justify-center">
        <a href="/" class="text-2xl font-black tracking-tighter text-indigo-600 hover:scale-105 transition-transform">
            NanoVote<span class="text-slate-300">.</span>
        </a>
    </header>
    <main class="flex-grow flex flex-col items-center justify-start pt-4 px-4 w-full max-w-xl mx-auto">
        {% block content %}{% endblock %}
    </main>
    <footer class="py-8 text-center text-xs text-slate-400 font-mono">
        SIMPLE • ANONYMOUS • FAST
    </footer>
</body>
</html>
"""

PAGE_CREATE = """
{% extends "base" %}
{% block content %}
<div x-data="{
    options: ['', ''],
    title: '',
    loading: false,
    error: '',
    addOption() { if(this.options.length < 20) this.options.push('') },
    removeOption(idx) { if(this.options.length > 2) this.options.splice(idx, 1) },
    async submit() {
        if(!this.title || this.options.some(o => !o.trim())) return;
        this.loading = true;
        this.error = '';
        try {
            const res = await fetch('/api/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({title: this.title, options: this.options})
            });
            const data = await res.json();
            if(res.ok && data.url) window.location.href = data.url;
            else this.error = data.detail || '创建失败';
        } catch(e) {
            this.error = '网络连接错误';
        } finally {
            this.loading = false;
        }
    }
}" class="w-full animate-fade-in-up">
    <div class="bg-white rounded-3xl shadow-xl shadow-indigo-100/50 p-6 sm:p-10 border border-slate-100">
        <h1 class="text-3xl font-bold mb-2 text-slate-900 tracking-tight">发起新投票</h1>

        <div x-show="error" x-cloak class="mb-4 p-3 bg-rose-50 text-rose-600 text-sm rounded-lg border border-rose-100" x-text="error"></div>

        <div class="mb-8">
            <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">问题</label>
            <input x-model="title" type="text" maxlength="100" placeholder="今天中午吃什么？"
                class="w-full px-0 py-2 text-xl font-bold bg-transparent border-0 border-b-2 border-slate-200 focus:border-indigo-500 focus:ring-0 transition placeholder-slate-300" autofocus>
        </div>

        <div class="space-y-4 mb-10">
            <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">选项</label>
            <template x-for="(opt, index) in options" :key="index">
                <div class="flex items-center gap-3 group">
                    <span class="text-slate-300 font-mono text-sm w-4 text-center" x-text="index + 1"></span>
                    <input x-model="options[index]" type="text" maxlength="50"
                        @keydown.enter.prevent="addOption()"
                        class="flex-1 px-4 py-3 rounded-xl bg-slate-50 border-transparent focus:bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 transition text-sm font-medium">
                    <button x-show="options.length > 2" @click="removeOption(index)" class="text-slate-300 hover:text-rose-500 transition p-2 opacity-0 group-hover:opacity-100 focus:opacity-100">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                    </button>
                </div>
            </template>
            <button @click="addOption()" class="text-sm text-indigo-600 font-bold hover:text-indigo-700 mt-2 flex items-center gap-1 px-8 py-2 rounded-lg hover:bg-indigo-50 w-max transition">
                + 添加选项
            </button>
        </div>

        <button @click="submit()" :disabled="loading || !title"
            class="w-full py-4 rounded-2xl font-bold text-white text-lg shadow-lg shadow-indigo-200 transition-all flex justify-center items-center gap-2"
            :class="(!title || loading) ? 'bg-slate-200 cursor-not-allowed shadow-none' : 'bg-indigo-600 hover:bg-indigo-700 active:scale-[0.98]'">
            <span x-show="!loading">创建投票</span>
            <span x-show="loading" class="animate-spin">⏳</span>
        </button>
    </div>
</div>
{% endblock %}
"""

PAGE_VOTE = """
{% extends "base" %}
{% block content %}
<div x-data="{
    voted: localStorage.getItem('voted_{{ poll_id }}') === 'true',
    totalVotes: {{ total_votes }},
    options: {{ options_json }},
    async vote(optionId) {
        if(this.voted) return;
        this.voted = true;
        localStorage.setItem('voted_{{ poll_id }}', 'true');
        const opt = this.options.find(o => o.id === optionId);
        if(opt) { opt.votes++; this.totalVotes++; }
        try {
            const res = await fetch('/api/vote/' + optionId, {method: 'POST'});
            if(res.ok) {
                const data = await res.json();
                this.options = data.options;
                this.totalVotes = data.total_votes;
            }
        } catch(e) { console.error('Sync failed'); }
    }
}" class="w-full animate-fade-in-up">
    <div class="bg-white/90 backdrop-blur-xl rounded-3xl shadow-2xl shadow-indigo-100/60 border border-white p-6 sm:p-8">
        <h1 class="text-2xl sm:text-3xl font-black text-slate-900 mb-8 leading-tight break-words">
            {{ poll_title }}
        </h1>
        <div class="space-y-3">
            <template x-for="opt in options" :key="opt.id">
                <div class="relative w-full group">
                    <div class="absolute inset-0 bg-slate-50 rounded-xl overflow-hidden h-full w-full border border-slate-100">
                        <div class="h-full bg-indigo-100/70 progress-bar border-r border-indigo-200/50"
                             :style="'width: ' + (voted ? (opt.votes / (totalVotes || 1) * 100) + '%' : '0%')"></div>
                    </div>
                    <button @click="vote(opt.id)" :disabled="voted"
                        class="relative w-full flex items-center justify-between px-5 py-4 rounded-xl transition-all z-10"
                        :class="voted ? 'cursor-default' : 'hover:bg-white/40 hover:shadow-sm cursor-pointer active:scale-[0.99]'">
                        <span class="font-bold text-slate-700 z-20 text-left" x-text="opt.text"></span>
                        <div x-show="voted" x-transition class="flex items-center gap-3 z-20">
                            <span class="text-lg font-black text-indigo-600" x-text="Math.round(opt.votes / (totalVotes || 1) * 100) + '%'"></span>
                            <span class="text-xs font-medium text-slate-400 bg-white/50 px-2 py-1 rounded-md" x-text="opt.votes + ' 票'"></span>
                        </div>
                    </button>
                </div>
            </template>
        </div>
        <div class="mt-8 flex justify-between items-center text-xs font-medium text-slate-400 border-t border-slate-100 pt-5">
            <span x-text="totalVotes + ' 人参与'"></span>
            <button @click="navigator.clipboard.writeText(window.location.href); $el.innerText='已复制'" class="hover:text-indigo-600 cursor-pointer">分享链接</button>
        </div>
    </div>
</div>
{% endblock %}
"""

jinja_env = Environment(
    loader=DictLoader({"base": HTML_BASE, "create": PAGE_CREATE, "vote": PAGE_VOTE}),
    autoescape=select_autoescape(['html', 'xml'])
)

class CreatePollRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="问题标题")
    options: List[str] = Field(..., min_items=2, max_items=20, description="选项列表")

    @field_validator('options')
    def validate_options(cls, v):
        cleaned = [opt.strip()[:50] for opt in v if opt.strip()]
        if len(cleaned) < 2:
            raise ValueError("至少需要两个有效选项")
        return cleaned

def cleanup_old_polls():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM polls")
        count = cursor.fetchone()[0]

        if count >= MAX_POLLS:
            limit_count = count - MAX_POLLS + 1
            cursor.execute("SELECT id FROM polls ORDER BY created_at ASC LIMIT ?", (limit_count,))
            rows = cursor.fetchall()
            if rows:
                ids_to_delete = [r[0] for r in rows]
                placeholders = ','.join('?' for _ in ids_to_delete)
                cursor.execute(f"DELETE FROM polls WHERE id IN ({placeholders})", ids_to_delete)
                conn.commit()
                logger.info(f"🧹 安全清理了 {len(ids_to_delete)} 个旧投票")
    except Exception as e:
        logger.error(f"清理失败: {e}")
    finally:
        if conn: conn.close()

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(jinja_env.get_template("create").render(title="创建投票"))

@app.post("/api/create")
async def create_poll(data: CreatePollRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(cleanup_old_polls)
    poll_id = str(uuid.uuid4())[:8]
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO polls (id, title) VALUES (?, ?)", (poll_id, data.title))
        for opt in data.options:
            cursor.execute("INSERT INTO options (poll_id, text) VALUES (?, ?)", (poll_id, opt))
        conn.commit()
        return {"poll_id": poll_id, "url": f"/p/{poll_id}"}
    except Exception as e:
        logger.error(f"Create Error: {e}")
        raise HTTPException(500, "创建失败")
    finally:
        conn.close()

@app.get("/p/{poll_id}", response_class=HTMLResponse)
async def view_poll(poll_id: str):
    if len(poll_id) != 8 or not poll_id.isalnum():
        return HTMLResponse("<h1>404 - 无效链接</h1>", status_code=404)

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM polls WHERE id = ?", (poll_id,))
        poll = cursor.fetchone()
        if not poll: return HTMLResponse("<h1>404 - 投票已过期</h1>", status_code=404)

        cursor.execute("SELECT id, text, votes FROM options WHERE poll_id = ?", (poll_id,))
        options = [dict(row) for row in cursor.fetchall()]
        return HTMLResponse(jinja_env.get_template("vote").render(
            title=poll['title'], poll_title=poll['title'], poll_id=poll_id,
            options_json=json.dumps(options), total_votes=sum(o['votes'] for o in options)
        ))
    finally:
        conn.close()

@app.post("/api/vote/{option_id}")
async def vote(option_id: int, request: Request):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT poll_id FROM options WHERE id = ?", (option_id,))
        res = cursor.fetchone()
        if not res: raise HTTPException(404, "Option not found")
        poll_id = res['poll_id']

        key = f"{request.client.host}_{poll_id}"
        if key not in VOTE_CACHE or (time.time() - VOTE_CACHE[key] > CACHE_TTL):
            cursor.execute("UPDATE options SET votes = votes + 1 WHERE id = ?", (option_id,))
            conn.commit()
            VOTE_CACHE[key] = time.time()

        cursor.execute("SELECT id, text, votes FROM options WHERE poll_id = ?", (poll_id,))
        options = [dict(row) for row in cursor.fetchall()]
        return {"options": options, "total_votes": sum(o['votes'] for o in options)}
    finally:
        conn.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=False)
