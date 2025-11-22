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
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' style='stop-color:%234F46E5'/%3E%3Cstop offset='100%25' style='stop-color:%233730A3'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect x='32' y='32' width='448' height='448' rx='96' fill='url(%23g)'/%3E%3Cpath d='M 138 260 L 218 340 L 366 168' fill='none' stroke='%23FFF' stroke-width='72' stroke-linecap='round' stroke-linejoin='round'/%3E%3Ccircle cx='366' cy='168' r='36' fill='%2314B8A6'/%3E%3C/svg%3E">
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    animation: {
                        'fade-in-up': 'fadeInUp 0.5s ease-out forwards',
                        'scale-in': 'scaleIn 0.3s ease-out forwards',
                        'shimmer': 'shimmer 1.5s ease-in-out',
                    },
                    keyframes: {
                        fadeInUp: {
                            '0%': { opacity: '0', transform: 'translateY(10px)' },
                            '100%': { opacity: '1', transform: 'translateY(0)' },
                        },
                        scaleIn: {
                            '0%': { opacity: '0', transform: 'scale(0.8)' },
                            '100%': { opacity: '1', transform: 'scale(1)' },
                        },
                        shimmer: {
                            '0%': { transform: 'translateX(-100%) skewX(-12deg)' },
                            '100%': { transform: 'translateX(200%) skewX(-12deg)' },
                        },
                        expandWidth: {
                            'from': { width: '0%', opacity: '0' },
                            'to': { width: 'var(--target-width)', opacity: '1' },
                        }
                    }
                }
            }
        }
    </script>
    <style>
        [x-cloak] { display: none !important; }
        .progress-bar {
            animation: expandWidth 1.2s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        }
        @keyframes expandWidth {
            from { width: 0%; opacity: 0; }
            to { width: var(--target-width); opacity: 1; }
        }
    </style>
</head>
<body class="h-screen w-full bg-[#F5F5F7] text-neutral-900 antialiased flex flex-col items-center justify-center p-4 sm:p-6 relative overflow-hidden">
    <!-- 极简氛围光 -->
    <div class="absolute top-[-10%] left-[10%] md:left-[20%] w-[400px] md:w-[800px] h-[400px] md:h-[800px] bg-white rounded-full blur-[80px] md:blur-[120px] mix-blend-overlay pointer-events-none"></div>
    <div class="absolute bottom-[-10%] right-[10%] md:right-[20%] w-[300px] md:w-[600px] h-[300px] md:h-[600px] bg-indigo-100/40 rounded-full blur-[60px] md:blur-[100px] mix-blend-multiply pointer-events-none"></div>

    <main class="relative z-10 w-full max-w-[420px] max-h-[calc(100vh-2rem)] sm:max-h-[calc(100vh-3rem)] flex flex-col">
        {% block content %}{% endblock %}
    </main>
</body>
</html>
"""

PAGE_CREATE = """
{% extends "base" %}
{% block content %}
<style>
    .grid-animate {
        display: grid;
        transition: grid-template-rows 0.5s cubic-bezier(0.2,0.8,0.2,1), opacity 0.5s, margin 0.5s;
    }
    .grid-animate.visible { grid-template-rows: 1fr; opacity: 1; margin-bottom: 0.75rem; }
    .grid-animate.hidden { grid-template-rows: 0fr; opacity: 0; margin-bottom: 0; }

    /* 自定义滚动条样式 */
    .options-scroll::-webkit-scrollbar {
        width: 6px;
    }
    .options-scroll::-webkit-scrollbar-track {
        background: transparent;
    }
    .options-scroll::-webkit-scrollbar-thumb {
        background: #d4d4d4;
        border-radius: 3px;
    }
    .options-scroll::-webkit-scrollbar-thumb:hover {
        background: #a3a3a3;
    }
    /* Firefox 滚动条样式 */
    .options-scroll {
        scrollbar-width: thin;
        scrollbar-color: #d4d4d4 transparent;
    }
</style>
<div x-data="{
    options: [{id: 1, text: '', isNew: false, deleting: false}, {id: 2, text: '', isNew: false, deleting: false}],
    nextId: 3,
    title: '',
    loading: false,
    error: '',
    addOption() {
        if(this.options.length < 20) {
            this.options.push({id: this.nextId++, text: '', isNew: true, deleting: false});
            this.$nextTick(() => {
                const inputs = document.querySelectorAll('[data-option-input]');
                inputs[inputs.length - 1]?.focus();
            });
        }
    },
    removeOption(id) {
        const activeCount = this.options.filter(o => !o.deleting).length;
        if(activeCount > 2) {
            const opt = this.options.find(o => o.id === id);
            if(opt) opt.deleting = true;
            setTimeout(() => {
                this.options = this.options.filter(o => o.id !== id);
            }, 500);
        }
    },
    async submit() {
        const validOptions = this.options.filter(o => !o.deleting);
        if(!this.title || validOptions.some(o => !o.text.trim())) return;
        this.loading = true;
        this.error = '';
        try {
            const res = await fetch('/api/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({title: this.title, options: validOptions.map(o => o.text)})
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
}" class="w-full h-full flex flex-col animate-fade-in-up">
    <div class="bg-white/80 backdrop-blur-2xl rounded-[2.5rem] p-8 border border-white/60 shadow-[0_20px_40px_-12px_rgba(0,0,0,0.05)] ring-1 ring-black/[0.03] transition-all duration-500 h-full flex flex-col">

        <!-- 固定部分：错误提示 + 问题输入 -->
        <div class="flex-shrink-0">
            <!-- 错误提示 -->
            <div x-show="error" x-cloak
                 x-transition:enter="transition ease-out duration-300"
                 x-transition:enter-start="opacity-0 -translate-y-2"
                 x-transition:enter-end="opacity-100 translate-y-0"
                 class="mb-6 p-3 bg-rose-50 text-rose-600 text-sm rounded-xl border border-rose-100" x-text="error"></div>

            <!-- 问题输入 -->
            <div class="mb-6 group">
                <label class="block text-xs font-medium text-neutral-400 uppercase tracking-wider mb-2 ml-1 group-focus-within:text-black transition-colors duration-300">
                    Question
                </label>
                <div class="relative">
                    <input x-model="title" type="text" maxlength="100" placeholder="What are we deciding?"
                        class="w-full bg-[#F9F9F9] text-xl font-medium text-neutral-900 placeholder:text-neutral-300/80 rounded-2xl px-5 py-4 border border-transparent outline-none focus:bg-white focus:shadow-[0_8px_30px_-4px_rgba(0,0,0,0.04)] focus:ring-1 focus:ring-black/5 transition-all duration-300 ease-out" autofocus>
                </div>
            </div>
        </div>

        <!-- 滚动部分：选项列表 -->
        <div class="flex-1 overflow-y-auto mb-6 min-h-0">
            <label class="block text-xs font-medium text-neutral-400 uppercase tracking-wider ml-1 mb-3">
                Options
            </label>

            <div class="w-full pr-1 options-scroll">
                <template x-for="(opt, index) in options" :key="opt.id">
                    <div class="grid-animate overflow-hidden"
                         :class="opt.deleting ? 'hidden' : (opt.isNew ? 'hidden' : 'visible')"
                         x-init="if(opt.isNew) { requestAnimationFrame(() => { $el.classList.remove('hidden'); $el.classList.add('visible'); opt.isNew = false; }); }">
                        <div class="overflow-hidden">
                            <div class="relative group">
                                <div class="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-300 font-mono text-xs pointer-events-none transition-colors group-focus-within:text-neutral-400"
                                     x-text="String(index + 1).padStart(2, '0')"></div>

                                <input x-model="opt.text" type="text" maxlength="50"
                                    data-option-input
                                    @keydown.enter.prevent="addOption()"
                                    :placeholder="'Option ' + (index + 1)"
                                    class="w-full bg-white border border-neutral-200/60 text-neutral-800 text-sm font-medium rounded-xl pl-12 pr-10 py-3.5 outline-none focus:border-neutral-300 focus:ring-4 focus:ring-neutral-100 transition-all duration-200 placeholder:text-neutral-300">

                                <button x-show="!opt.deleting && options.filter(o => !o.deleting).length > 2"
                                        @click="removeOption(opt.id)"
                                        class="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 rounded-full text-neutral-300 hover:text-red-500 hover:bg-red-50 transition-all duration-200 opacity-0 group-hover:opacity-100 focus:opacity-100">
                                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                                </button>
                            </div>
                        </div>
                    </div>
                </template>
            </div>

            <!-- 添加按钮 -->
            <button @click="addOption()"
                    class="w-full mt-1 py-3.5 rounded-xl border border-dashed border-neutral-300 text-neutral-400 text-sm font-medium hover:border-neutral-400 hover:text-neutral-600 hover:bg-white/40 active:bg-neutral-50 transition-all duration-200 flex items-center justify-center gap-2 group">
                <div class="w-5 h-5 rounded-full bg-neutral-100 flex items-center justify-center group-hover:bg-neutral-200 transition-colors">
                    <svg class="w-3 h-3 text-neutral-500 group-hover:text-neutral-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                </div>
                Add Option
            </button>
        </div>

        <!-- 固定部分：提交按钮 -->
        <div class="flex-shrink-0">
            <button @click="submit()" :disabled="loading || !title || options.filter(o => !o.deleting).some(o => !o.text.trim())"
                class="w-full h-14 rounded-[1.2rem] font-medium text-base flex items-center justify-center gap-2 transition-all duration-300 ease-out bg-black text-white shadow-[0_8px_20px_-6px_rgba(0,0,0,0.2)] hover:shadow-[0_12px_25px_-8px_rgba(0,0,0,0.3)] hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:hover:scale-100 disabled:shadow-none disabled:cursor-not-allowed">
                <span x-show="!loading">Create Poll</span>
                <svg x-show="!loading" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                <svg x-show="loading" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            </button>
        </div>
    </div>
</div>
{% endblock %}
"""

PAGE_VOTE = """
{% extends "base" %}
{% block content %}
<div x-data="{
    voted: localStorage.getItem('voted_{{ poll_id }}') === 'true',
    totalVotes: 0,
    options: [],
    loading: true,
    selectedId: null,
    showResults: false,
    async init() {
        try {
            const res = await fetch('/api/poll/{{ poll_id }}');
            if(res.ok) {
                const data = await res.json();
                this.options = data.options;
                this.totalVotes = data.total_votes;
            }
        } catch(e) { console.error('Load failed'); }
        this.loading = false;
        if(this.voted) {
            this.showResults = true;
        }
    },
    async vote(optionId) {
        if(this.voted) return;
        this.selectedId = optionId;
        this.voted = true;
        localStorage.setItem('voted_{{ poll_id }}', 'true');
        const opt = this.options.find(o => o.id === optionId);
        if(opt) { opt.votes++; this.totalVotes++; }
        setTimeout(() => this.showResults = true, 600);
        try {
            const res = await fetch('/api/vote/' + optionId, {method: 'POST'});
            if(res.ok) {
                const data = await res.json();
                this.options = data.options;
                this.totalVotes = data.total_votes;
            }
        } catch(e) { console.error('Sync failed'); }
    }
}" class="w-full h-full flex flex-col animate-fade-in-up">
    <div class="bg-white/70 backdrop-blur-2xl rounded-[2.5rem] p-8 border border-white/60 shadow-[0_20px_40px_-12px_rgba(0,0,0,0.05)] ring-1 ring-black/[0.03] transition-all duration-700 h-full flex flex-col"
         :class="voted ? 'scale-[1.01]' : ''">

        <!-- 固定部分：标题 -->
        <div class="flex-shrink-0 mb-6 text-center">
            <h1 class="text-xl font-medium text-neutral-900 tracking-tight leading-tight break-words">
                {{ poll_title }}
            </h1>
        </div>

        <!-- 滚动部分：加载状态 + 选项列表 -->
        <div class="flex-1 overflow-y-auto min-h-0 mb-6">
            <!-- 加载状态 -->
            <div x-show="loading" class="text-center py-8 text-neutral-400">
                <svg class="animate-spin w-5 h-5 mx-auto mb-2" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            </div>

            <!-- 选项列表 -->
            <div x-show="!loading" class="space-y-3 pr-1">
            <template x-for="opt in options" :key="opt.id">
                <button @click="vote(opt.id)" :disabled="voted"
                    class="group relative w-full h-[72px] rounded-[1.2rem] overflow-hidden transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)] flex items-center px-1 outline-none focus-visible:ring-2 focus-visible:ring-black/20"
                    :class="[
                        selectedId === opt.id ? 'bg-black shadow-lg scale-[1.02]' : 'bg-white hover:bg-[#F9F9F9] shadow-sm border border-neutral-100',
                        voted && selectedId !== opt.id ? 'opacity-40 scale-[0.98]' : 'opacity-100',
                        voted ? 'cursor-default' : 'cursor-pointer'
                    ]">

                    <!-- 进度条 -->
                    <div x-show="showResults"
                         class="absolute inset-0 z-0 transition-all duration-1000 ease-out origin-left progress-bar"
                         :class="selectedId === opt.id ? 'bg-white/20' : 'bg-neutral-100'"
                         :style="'--target-width: ' + Math.round(opt.votes / (totalVotes || 1) * 100) + '%'">
                    </div>

                    <!-- 内容 -->
                    <div class="relative z-10 w-full h-full flex items-center justify-between px-5">
                        <span class="text-[15px] font-medium tracking-normal transition-colors duration-300 text-left"
                              :class="selectedId === opt.id ? 'text-white' : 'text-neutral-900'"
                              x-text="opt.text"></span>

                        <!-- 状态区 -->
                        <div class="flex items-center">
                            <!-- 未投票时的箭头 -->
                            <div x-show="!voted"
                                 class="w-8 h-8 rounded-full flex items-center justify-center opacity-0 scale-50 group-hover:opacity-100 group-hover:scale-100 transition-all duration-300 ease-out"
                                 :class="selectedId === opt.id ? 'bg-white/20' : 'bg-neutral-100'">
                                <svg class="w-4 h-4" :class="selectedId === opt.id ? 'text-white' : 'text-neutral-900'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                                </svg>
                            </div>

                            <!-- 投票后显示百分比 -->
                            <div x-show="showResults" class="flex items-center gap-2">
                                <span class="text-base font-medium tracking-tight tabular-nums"
                                      :class="selectedId === opt.id ? 'text-white' : 'text-neutral-900'"
                                      x-text="Math.round(opt.votes / (totalVotes || 1) * 100) + '%'"></span>
                            </div>

                            <!-- 选中但未显示结果时的勾 -->
                            <div x-show="voted && !showResults && selectedId === opt.id" class="animate-scale-in text-white">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
                                </svg>
                            </div>
                        </div>
                    </div>

                    <!-- 选中态光泽 -->
                    <div x-show="selectedId === opt.id && !showResults"
                         class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 animate-shimmer pointer-events-none">
                    </div>
                </button>
            </template>
            </div>
        </div>

        <!-- 固定部分：底部信息 -->
        <div x-show="!loading" class="flex-shrink-0 pt-6 flex items-center justify-between text-[10px] uppercase tracking-[0.2em] text-neutral-400 font-medium border-t border-neutral-100">
            <span class="flex items-center gap-2">
                <span class="w-1.5 h-1.5 rounded-full transition-colors duration-500"
                      :class="voted ? 'bg-indigo-600' : 'bg-neutral-300'"></span>
                <span x-text="voted ? 'Vote Recorded' : 'Anonymous'"></span>
            </span>
            <button @click="
                const url = window.location.href;
                if (navigator.clipboard && window.isSecureContext) {
                    navigator.clipboard.writeText(url).then(() => $el.innerText = 'COPIED');
                } else {
                    const ta = document.createElement('textarea');
                    ta.value = url;
                    ta.style.position = 'fixed';
                    ta.style.left = '-9999px';
                    document.body.appendChild(ta);
                    ta.select();
                    document.execCommand('copy');
                    document.body.removeChild(ta);
                    $el.innerText = 'COPIED';
                }
                setTimeout(() => $el.innerText = 'SHARE', 2000);
            " class="hover:text-neutral-900 cursor-pointer transition-colors">
                SHARE
            </button>
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

        return HTMLResponse(jinja_env.get_template("vote").render(
            title=poll['title'], poll_title=poll['title'], poll_id=poll_id
        ))
    finally:
        conn.close()

@app.get("/api/poll/{poll_id}")
async def get_poll_data(poll_id: str):
    if len(poll_id) != 8 or not poll_id.isalnum():
        raise HTTPException(404, "Invalid poll ID")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM polls WHERE id = ?", (poll_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Poll not found")

        cursor.execute("SELECT id, text, votes FROM options WHERE poll_id = ?", (poll_id,))
        options = [dict(row) for row in cursor.fetchall()]
        return {"options": options, "total_votes": sum(o['votes'] for o in options)}
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
