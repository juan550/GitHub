import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import tkinter.filedialog
import requests
import datetime
import json
import os
import random
import subprocess
import threading
import tempfile
import shutil
import webbrowser
import re
import math
import time
import logging
import calendar
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- AUDIO SETUP ---
try:
    import pygame
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

# Спроба імпорту AI бібліотеки
try:
    from google import genai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# ===================== КОНФІГУРАЦІЯ =====================

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

logging.basicConfig(filename='app.log', level=logging.ERROR)

_SESSION_LOCAL = threading.local()

def get_session(token=None):
    cache = getattr(_SESSION_LOCAL, "cache", None)
    if cache is None:
        cache = {}
        _SESSION_LOCAL.cache = cache

    cache_key = token or ""
    session = cache.get(cache_key)
    if session is None:
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        if token:
            session.headers.update({"Authorization": f"Bearer {token}"})
        cache[cache_key] = session
    return session

# Кольори інтерфейсу
COLOR_BG = "#FFFFFF"
COLOR_TEXT_MAIN = "#1D1D1F"
COLOR_TEXT_SEC = "#86868B"
COLOR_ACCENT = "#000000"       
COLOR_FIELD_BG = "#EAEAEA"     
COLOR_BORDER = "#C0C0C0"
COLOR_DELETE = "#FF3B30"
COLOR_DISABLED = "#E0E0E0"
COLOR_WARNING = "#FF9500"
COLOR_SUCCESS = "#34C759"
COLOR_CHART_COLORS = ["#007AFF", "#FF9500", "#FF3B30", "#5856D6", "#AF52DE", "#5AC8FA", "#4CD964", "#FF2D55"]

# Аудіо файли
SOUND_EAGLE = "eagle.mp3"
SOUND_MUSIC = "thunderstruck.mp3"

# Палітра GitHub
PALETTE = {
    0: "#EBEDF0",
    1: "#9BE9A8",
    2: "#40C463",
    3: "#30A14E",
    4: "#216E39"
}

GRAPHQL_URL = "https://api.github.com/graphql"
REST_API_URL = "https://api.github.com"
DATA_DIR = "data"
AUTH_FILE = os.path.join(DATA_DIR, "auth.json")

# Модель AI (Оптимізовано для швидкості та економії)
AI_MODEL_NAME = 'models/gemini-flash-latest'

AI_MODEL_FALLBACKS = (
    'models/gemini-flash-latest',        # Flash latest (дешево/швидко)
    'models/gemini-flash-lite-latest',   # Lite latest (ще дешевше/швидше)
    'models/gemini-2.0-flash-exp',       # Експериментальна Flash
    'models/gemini-2.0-flash-lite',      # Lite стабільна
)

# --- ПРІОРИТЕТНІ ФАЙЛИ ДЛЯ ШТУЧНОГО ІНТЕЛЕКТУ ---
PRIORITY_FILES = [
    "main.py", "index.js", "App.js", "App.tsx", "server.js", 
    "views.py", "models.py", "auth.js", "utils.js", "script.js",
    "style.css", "styles.css"
]

# --- ДАНІ ДЛЯ ГЕНЕРАТОРА (Твій стек) ---
TARGET_STACK = [
    "JavaScript", "TypeScript", "Python", "Django", 
    "HTML/CSS", "React Native", "Expo", "Next.js", "Node.js", "Express", "NestJS", "React", "Solidity"
]
WHITELIST_LANGS = [
    "HTML", "CSS", "SCSS", "Sass", "Less", "Shell", "PowerShell",
    "Dockerfile", "Makefile", "Jupyter Notebook", "Batchfile", "Procfile"
]

# Як стек називається в UI -> як його краще шукати в GitHub Search API
STACK_SEARCH_RULES = {
    "JavaScript": {"language": "JavaScript", "keywords": []},
    "TypeScript": {"language": "TypeScript", "keywords": []},
    "Python": {"language": "Python", "keywords": []},
    "Django": {"language": "Python", "keywords": ["django"]},
    "HTML/CSS": {"language": "HTML", "keywords": ["css"]},
    "React Native": {"language": "TypeScript", "keywords": ["react-native", "mobile"]},
    "Expo": {"language": "TypeScript", "keywords": ["expo", "react-native", "mobile"]},
    "Next.js": {"language": "TypeScript", "keywords": ["nextjs", "next.js"]},
    "Node.js": {"language": "JavaScript", "keywords": ["nodejs", "backend"]},
    "Express": {"language": "JavaScript", "keywords": ["express", "nodejs", "api"]},
    "NestJS": {"language": "TypeScript", "keywords": ["nestjs", "backend"]},
    "React": {"language": "JavaScript", "keywords": ["react"]},
    "Solidity": {"language": "Solidity", "keywords": []},
}

# --- SENIOR CALCULATOR SETTINGS ---
SENIOR_VELOCITY_KB_PER_DAY = 15 
LANGUAGE_WEIGHTS = {
    "HTML": 0.5, "CSS": 0.5, "HTML/CSS": 0.5,
    "JavaScript": 1.0, "TypeScript": 1.0, "Python": 1.0,
    "Django": 1.0, "React": 0.8, "React Native": 0.9,
    "Vue": 0.8, "Next.js": 0.9, "Node.js": 1.0, "Express": 1.0, "NestJS": 1.0, "Solidity": 1.1,
    "default": 1.0 
}

# Fallback шаблони
PROFESSIONAL_COMMITS = [
    "Initial commit", "Update project structure", "Refactor core logic", 
    "Fix minor bug", "Update README.md", "Optimize performance", 
    "Add unit tests", "Clean up code", "Update dependencies", 
    "WIP: implementing feature", "Merge branch 'dev'", "Hotfix for production"
]

# Шаблони
WEB_COMBO_TEMPLATE = {
    "dirs": ["assets/images", "assets/icons"],
    "files": [
        ("index.html", """<!DOCTYPE html>\n<html lang="en">\n<head><meta charset="UTF-8"><title>App</title></head>\n<body><div id="app"></div></body>\n</html>"""),
        ("style.css", """body { margin: 0; padding: 0; font-family: sans-serif; }"""),
        ("script.js", """console.log('System Initialized');""")
    ]
}

PROJECT_TEMPLATES = {
    "Python": { "dirs": ["src"], "files": [("main.py", "print('Hello World')")] },
    "JavaScript": { "dirs": ["src"], "files": [("index.js", "console.log('Hello World')")] },
    "Node.js": {
        "dirs": ["src"],
        "files": [
            ("server.js", "const http = require('http');\n\nconst server = http.createServer((req, res) => {\n  res.writeHead(200, { 'Content-Type': 'application/json' });\n  res.end(JSON.stringify({ status: 'ok' }));\n});\n\nconst PORT = process.env.PORT || 3000;\nserver.listen(PORT, () => console.log(`Server running on ${PORT}`));\n"),
            ("package.json", "{\n  \"name\": \"node-api\",\n  \"version\": \"1.0.0\",\n  \"main\": \"server.js\",\n  \"scripts\": {\n    \"start\": \"node server.js\"\n  }\n}\n"),
        ],
    },
    "Express": {
        "dirs": ["src"],
        "files": [
            ("server.js", "const express = require('express');\n\nconst app = express();\napp.use(express.json());\n\napp.get('/health', (req, res) => {\n  res.json({ status: 'ok' });\n});\n\nconst PORT = process.env.PORT || 3000;\napp.listen(PORT, () => console.log(`Express running on ${PORT}`));\n"),
            ("package.json", "{\n  \"name\": \"express-api\",\n  \"version\": \"1.0.0\",\n  \"main\": \"server.js\",\n  \"scripts\": {\n    \"start\": \"node server.js\"\n  },\n  \"dependencies\": {\n    \"express\": \"^4.19.2\"\n  }\n}\n"),
        ],
    },
    "NestJS": {
        "dirs": ["src"],
        "files": [
            ("main.ts", "import { NestFactory } from '@nestjs/core';\nimport { Module, Controller, Get } from '@nestjs/common';\n\n@Controller()\nclass AppController {\n  @Get('health')\n  health() {\n    return { status: 'ok' };\n  }\n}\n\n@Module({\n  controllers: [AppController],\n})\nclass AppModule {}\n\nasync function bootstrap() {\n  const app = await NestFactory.create(AppModule);\n  await app.listen(process.env.PORT || 3000);\n}\n\nbootstrap();\n"),
            ("package.json", "{\n  \"name\": \"nestjs-api\",\n  \"version\": \"1.0.0\",\n  \"scripts\": {\n    \"start\": \"nest start\"\n  },\n  \"dependencies\": {\n    \"@nestjs/common\": \"^10.0.0\",\n    \"@nestjs/core\": \"^10.0.0\",\n    \"reflect-metadata\": \"^0.1.13\",\n    \"rxjs\": \"^7.8.0\"\n  }\n}\n"),
        ],
    },
    "React Native": {
        "dirs": ["src"],
        "files": [
            ("App.js", "import React from 'react';\nimport { SafeAreaView, Text, StyleSheet } from 'react-native';\n\nexport default function App() {\n  return (\n    <SafeAreaView style={styles.container}>\n      <Text style={styles.title}>React Native App</Text>\n    </SafeAreaView>\n  );\n}\n\nconst styles = StyleSheet.create({\n  container: { flex: 1, alignItems: 'center', justifyContent: 'center' },\n  title: { fontSize: 24, fontWeight: '600' },\n});\n"),
            ("package.json", "{\n  \"name\": \"react-native-app\",\n  \"version\": \"1.0.0\",\n  \"main\": \"App.js\",\n  \"dependencies\": {\n    \"react\": \"^18.2.0\",\n    \"react-native\": \"^0.74.0\"\n  }\n}\n"),
        ],
    },
    "Solidity": { "dirs": ["contracts"], "files": [("SimpleStorage.sol", "pragma solidity ^0.8.20;\n\ncontract SimpleStorage {\n    uint256 private value;\n\n    function set(uint256 newValue) public {\n        value = newValue;\n    }\n\n    function get() public view returns (uint256) {\n        return value;\n    }\n}\n")] }
}

REAL_CODE_SNIPPETS = {
    ".py": ["def process(data): return data", "class Config: DEBUG=True", "import os, sys", "try: run() except: pass"],
    ".js": ["const [val, setVal] = useState(0);", "useEffect(() => {}, [])", "console.log('Debug')", "export const init = () => {}"],
    ".ts": ["interface User { id: string; }", "type Result<T> = { ok: boolean; data?: T };", "export const bootstrap = async (): Promise<void> => {}", "const isReady: boolean = true;"],
    ".sol": ["event ValueUpdated(uint256 newValue);", "error Unauthorized();", "modifier onlyOwner() { if (msg.sender != owner) revert Unauthorized(); _; }", "mapping(address => uint256) public balances;"],
    "default": ["# Config update", "// Optimize loop", "var x = 1;", "return true;"]
}

# --- ДАНІ ДЛЯ CLONER ---
NICHES = {
    "General (Any)": [],
    "Fintech (Finance)": ["topic:finance", "topic:fintech", "topic:banking"],
    "Crypto / Blockchain": ["topic:blockchain", "topic:crypto", "topic:web3"],
    "E-commerce": ["topic:ecommerce", "topic:shop", "topic:store"],
    "HealthTech": ["topic:health", "topic:medical", "topic:fitness"],
    "AI / ML Tools": ["topic:ai", "topic:machine-learning", "topic:bot"],
    "Social Media": ["topic:social", "topic:chat", "topic:community"]
}

SCALES = {
    "Any Size": "",
    "Small (MVP / Demo)": "size:1000..10000",
    "Medium (Standard)": "size:10000..50000",
    "Large (Enterprise)": "size:>50000",
    "Complex (Migration/Rewrite)": "size:>20000 archived:false"
}

SORT_OPTIONS = {
    "Best Match": "",
    "Most Stars": "stars",
    "Fewest Stars": "stars-asc",
    "Most Forks": "forks",
    "Fewest Forks": "forks-asc",
    "Recently Updated": "updated",
    "Oldest Updates": "updated-asc"
}

SMART_SYNONYMS = {
    "todo": ["TaskMaster", "ActionPlan", "DoneList", "MyTasks", "FocusFlow"],
    "shop": ["RetailHub", "StoreFront", "MarketPlace", "E-Bazaar", "CommerceCore"],
    "app": ["System", "Platform", "Engine", "Solution", "Toolkit"],
    "bot": ["AutoMate", "RoboHelper", "Agent", "SynthWorker"],
    "web": ["NetPortal", "SiteBase", "WebFront", "CloudView"],
    "api": ["ConnectLink", "DataBridge", "Gateway", "InterfaceHub"]
}

IGNORE_FILES = ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "composer.lock", "Cargo.lock", "Gemfile.lock", ".env", ".env.local", ".DS_Store", "Thumbs.db", "desktop.ini"]
IGNORE_EXTENSIONS = ['.zip', '.tar', '.gz', '.rar', '.7z', '.mp4', '.mov', '.mp3', '.wav', '.ttf', '.woff', '.woff2', '.eot', '.exe', '.dll', '.so', '.dylib', '.pdf', '.jpg', '.png', '.jpeg', '.gif', '.ico']
IGNORE_FOLDERS = [".github", ".git", ".vscode", ".idea", "node_modules", "dist", "build", "coverage", "__pycache__", "venv", "env"]

# ===================== GLOBAL HELPERS =====================

def sync_directories(src_dir, dst_dir):
    """Робить папку dst_dir точною копією src_dir (ігноруючи .git)."""
    # 1. Видалення зайвого в цілі
    for root, dirs, files in os.walk(dst_dir):
        if ".git" in root: continue
        rel_path = os.path.relpath(root, dst_dir)
        src_root = os.path.join(src_dir, rel_path)
        
        if not os.path.exists(src_root):
            shutil.rmtree(root)
            continue
            
        for file in files:
            dst_file = os.path.join(root, file)
            src_file = os.path.join(src_root, file)
            if not os.path.exists(src_file):
                os.remove(dst_file)

    # 2. Копіювання нового з джерела
    for root, dirs, files in os.walk(src_dir):
        if ".git" in root: continue
        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]
        
        rel_path = os.path.relpath(root, src_dir)
        dst_root = os.path.join(dst_dir, rel_path)
        
        if not os.path.exists(dst_root):
            os.makedirs(dst_root)
            
        for file in files:
            if any(file.endswith(ext) for ext in IGNORE_EXTENSIONS): continue
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dst_root, file)
            try: shutil.copy2(src_file, dst_file)
            except: pass

def clean_ai_response(text):
    if not text: return text
    pattern = r"```(?:\w+)?\n(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match: text = match.group(1)
    lines = text.split('\n')
    if len(lines) > 0 and ("Here is" in lines[0] or "Sure," in lines[0]):
        lines = lines[1:]
    return "\n".join(lines).strip()

def apply_aggressive_branding(content, username):
    current_year = str(datetime.date.today().year)
    triggers = [
        r"Copyright \(c\) \d{4}.*", r"Copyright \d{4}.*", r"@author.*", 
        r"Created by.*", r"Author:.*", r"Maintained by.*", r"Dev:.*",
        r"Developer:.*", r"Credits:.*", r"License:.*Copyright.*"
    ]
    new_lines = []
    for line in content.splitlines():
        modified_line = line
        for pattern in triggers:
            if re.search(pattern, line, re.IGNORECASE):
                indent = re.match(r"\s*", line).group()
                comment_char = "#" if "#" in line else "//"
                if "Copyright" in line:
                    modified_line = f"{indent}{comment_char} Copyright (c) {current_year} {username}"
                else:
                    modified_line = f"{indent}{comment_char} Author: {username}"
                break 
        new_lines.append(modified_line)
    return "\n".join(new_lines)

def fast_cleanup_non_priority(content):
    lines = [line.rstrip() for line in content.splitlines()]
    return "\n".join(lines).strip() + "\n"

def get_file_version(filepath):
    """Витягує версію з package.json або pyproject.toml"""
    if not os.path.exists(filepath): return None
    try:
        fname = os.path.basename(filepath)
        content = open(filepath, 'r', encoding='utf-8').read()
        if fname == "package.json":
            data = json.loads(content)
            return data.get("version")
        elif fname == "pyproject.toml":
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match: return match.group(1)
    except: pass
    return None

def generate_branch_name_from_msg(msg):
    """Створює feat/login-fix з повідомлення коміту."""
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', msg).lower()
    words = clean.split()[:4] # перші 4 слова
    slug = '-'.join(words)
    if "fix" in slug: return f"fix/{slug}"
    if "update" in slug: return f"update/{slug}"
    return f"feat/{slug}"

# ===================== API & AI MANAGER =====================

class AIKeyManager:
    def __init__(self, key_list=None):
        # key_list: список словників [{"key": "...", "status": "ok"}, ...]
        self.keys = key_list if key_list else []
        self.current_idx = 0

    def add_key(self, key_str):
        clean = key_str.strip()
        if clean and not any(k['key'] == clean for k in self.keys):
            self.keys.append({"key": clean, "status": "unknown"})

    def remove_key(self, key_str):
        self.keys = [k for k in self.keys if k['key'] != key_str]

    def get_current_key(self):
        # Round Robin: Шукаємо живий ключ, пропускаємо cooldown (limit/temp)
        if not self.keys: return None
        now = datetime.datetime.now()
        fallback_idx = None

        for _ in range(len(self.keys)):
            k = self.keys[self.current_idx]
            status = str(k.get('status', 'unknown')).lower()

            if fallback_idx is None and status != "dead":
                fallback_idx = self.current_idx

            cooldown_str = k.get('cooldown_until')
            if status in ("limit", "temp") and cooldown_str:
                try:
                    target_time = datetime.datetime.strptime(cooldown_str, "%H:%M:%S").replace(
                        year=now.year, month=now.month, day=now.day
                    )
                    # Якщо cooldown в майбутньому - пропускаємо ключ
                    if (target_time - now).total_seconds() > 0:
                        self.rotate()
                        continue
                    # Якщо cooldown пройшов - повертаємо ключ у робочий стан
                    k['status'] = 'ok'
                    k.pop('cooldown_until', None)
                    k.pop('prev_status', None)
                    status = "ok"
                except:
                    # Якщо час зламаний/старий - очищаємо cooldown
                    k.pop('cooldown_until', None)
                    k.pop('prev_status', None)

            if status != "dead":
                return k['key']
            self.rotate()

        # Якщо всі в cooldown/мертві - повертаємо перший не-dead
        if fallback_idx is not None:
            self.current_idx = fallback_idx
            return self.keys[fallback_idx]['key']

        # Якщо всі мертві - повертаємо хоч щось (перший), щоб спробувати
        return self.keys[0]['key'] if self.keys else None

    def rotate(self):
        if not self.keys: return
        self.current_idx = (self.current_idx + 1) % len(self.keys)

    def mark_current_bad(self):
        if self.keys:
            self.keys[self.current_idx]['status'] = "dead"
            self.rotate()
            
    def get_all_keys(self):
        return self.keys


class ProxyManager:
    def __init__(self, proxy_list=None):
        # proxy_list: [{"url": "http://...", "status": "unknown", "location": "???"}, ...]
        self.proxies = proxy_list if proxy_list else []
        self.current_idx = 0

    def add_proxy(self, url):
        clean = url.strip()
        if clean and not any(p['url'] == clean for p in self.proxies):
            self.proxies.append({"url": clean, "status": "unknown", "location": "Unknown"})

    def remove_proxy(self, url):
        self.proxies = [p for p in self.proxies if p['url'] != url]

    def get_next_proxy_dict(self):
        # Повертає словник для requests
        if not self.proxies: return None
        # Проста ротація
        p = self.proxies[self.current_idx]
        self.current_idx = (self.current_idx + 1) % len(self.proxies)
        return {"http": p['url'], "https": p['url']}

    def get_all(self): return self.proxies

ai_manager = None
proxy_manager = ProxyManager()
ai_fallback_mode = False 

# --- API HELPER WITH RETRY (Retry 3 times) ---
def api_retry(func):
    def wrapper(*args, **kwargs):
        for i in range(3):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"API Retry {i+1}/3: {e}")
                time.sleep(30)
        return None # Skip after 3 fails
    return wrapper

@api_retry
def api_get_languages(token, owner, repo):
    r = get_session(token).get(f"{REST_API_URL}/repos/{owner}/{repo}/languages")
    return r.json() if r.status_code == 200 else {}

# --- NEW API HELPERS (Dossier 2.0) ---
@api_retry
def api_get_contributors(token, owner, repo):
    # Отримуємо топ-10 контриб'юторів
    url = f"{REST_API_URL}/repos/{owner}/{repo}/contributors?per_page=10"
    r = get_session(token).get(url)
    return r.json() if r.status_code == 200 else []

@api_retry
def api_get_participation(token, owner, repo):
    # Отримуємо статистику комітів за рік (для Sparkline)
    url = f"{REST_API_URL}/repos/{owner}/{repo}/stats/participation"
    r = get_session(token).get(url)
    return r.json().get("all", []) if r.status_code == 200 else []

def _extract_last_page_from_link(link_header):
    if not link_header:
        return None
    m = re.search(r"[?&]page=(\d+)>;\s*rel=\"last\"", link_header)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            return None
    return None

@api_retry
def api_get_repo_commit_count(token, owner, repo):
    url = f"{REST_API_URL}/repos/{owner}/{repo}/commits?per_page=1"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    r = get_session(token).get(url, headers=headers, timeout=10)
    if r.status_code == 409:
        return 0
    if r.status_code != 200:
        return None
    last_page = _extract_last_page_from_link(r.headers.get("Link", ""))
    if isinstance(last_page, int):
        return last_page
    data = r.json()
    return len(data) if isinstance(data, list) else 0

@api_retry
def api_get_repo_contributors_count(token, owner, repo):
    url = f"{REST_API_URL}/repos/{owner}/{repo}/contributors?per_page=1&anon=1"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    r = get_session(token).get(url, headers=headers, timeout=10)
    if r.status_code == 204:
        return 0
    if r.status_code != 200:
        return None
    last_page = _extract_last_page_from_link(r.headers.get("Link", ""))
    if isinstance(last_page, int):
        return last_page
    data = r.json()
    return len(data) if isinstance(data, list) else 0

def build_file_tree(tree_widget, file_paths):
    # Парсер шляхів (a/b/c.py) у дерево
    nodes = {}
    for path in file_paths:
        parts = path.split("/")
        parent = ""
        for i, part in enumerate(parts):
            current_path = "/".join(parts[:i+1])
            if current_path not in nodes:
                # Визначаємо: папка чи файл?
                is_folder = (i < len(parts) - 1) or (part in ["src", "lib", "public"])
                icon = "📁" if is_folder else "📄"
                
                # Додаємо вузол
                nodes[current_path] = tree_widget.insert(
                    parent, "end", text=f" {icon} {part}", open=False # Закриті за замовчуванням
                )
            parent = nodes[current_path]

@api_retry
def api_create_issue(token, owner, repo, title, body, labels):
    url = f"{REST_API_URL}/repos/{owner}/{repo}/issues"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    payload = {"title": title, "body": body, "labels": labels}
    r = get_session(token).post(url, json=payload, headers=headers, timeout=10)
    if r.status_code == 201: return r.json()["number"]
    raise Exception(f"Issue fail {r.status_code}")

@api_retry
def api_create_pr(token, owner, repo, head, base, title, body):
    url = f"{REST_API_URL}/repos/{owner}/{repo}/pulls"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    payload = {"title": title, "body": body, "head": head, "base": base}
    r = get_session(token).post(url, json=payload, headers=headers, timeout=10)
    if r.status_code == 201: return r.json()["number"]
    raise Exception(f"PR Create fail {r.status_code}")

@api_retry
def api_create_pr_review(token, owner, repo, pr_number, body="Looks good to me! LGTM 🚀", event="APPROVE"):
    url = f"{REST_API_URL}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    r = get_session(token).post(url, json={"body": body, "event": event}, headers=headers, timeout=10)
    if r.status_code == 200: return True
    raise Exception(f"PR Review fail {r.status_code}: {r.text}")

@api_retry
def api_merge_pr(token, owner, repo, pr_number):
    url = f"{REST_API_URL}/repos/{owner}/{repo}/pulls/{pr_number}/merge"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    payload = {"merge_method": "merge"} # Merge commit strategy
    r = get_session(token).put(url, json=payload, headers=headers, timeout=10)
    if r.status_code == 200: return True
    raise Exception(f"PR Merge fail {r.status_code}")

@api_retry
def api_delete_branch(token, owner, repo, branch_name):
    url = f"{REST_API_URL}/repos/{owner}/{repo}/git/refs/heads/{branch_name}"
    headers = {"Authorization": f"Bearer {token}"}
    get_session(token).delete(url, headers=headers, timeout=10)

@api_retry
def api_create_release(token, owner, repo, tag_name, name, body):
    url = f"{REST_API_URL}/repos/{owner}/{repo}/releases"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    payload = {"tag_name": tag_name, "name": name, "body": body}
    get_session(token).post(url, json=payload, headers=headers, timeout=10)

def fetch_user_info(username, token):
    query = f""" query {{ user(login: "{username}") {{ createdAt }} }} """
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = get_session(token).post(GRAPHQL_URL, json={"query": query}, headers=headers, timeout=10)
        if r.status_code != 200: raise Exception(f"HTTP {r.status_code}")
        data = r.json()
        if "errors" in data: raise Exception(data["errors"][0]["message"])
        created_at = data["data"]["user"]["createdAt"]
        return datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00")).date()
    except Exception as e: raise e

def create_github_repo(username, token, repo_name, is_private, description):
    url = f"{REST_API_URL}/user/repos"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    payload = { "name": repo_name, "private": is_private, "auto_init": False, "description": description }
    r = get_session(token).post(url, json=payload, headers=headers)
    if r.status_code == 201: return r.json()["clone_url"]
    elif r.status_code == 422: raise Exception("Repository name already exists!")
    else: raise Exception(f"API Error: {r.text}")

def api_add_collaborator(token, owner, repo, collaborator, permission="push"):
    url = f"{REST_API_URL}/repos/{owner}/{repo}/collaborators/{collaborator}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    payload = {"permission": permission}
    r = get_session(token).put(url, json=payload, headers=headers, timeout=15)
    if r.status_code in (201, 204):
        return True
    raise Exception(f"API Error: {r.text}")

def api_list_repository_invitations(token):
    url = f"{REST_API_URL}/user/repository_invitations"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    r = get_session(token).get(url, headers=headers, timeout=15)
    if r.status_code == 200:
        return r.json()
    raise Exception(f"API Error: {r.text}")

def api_accept_repository_invitation(token, invitation_id):
    url = f"{REST_API_URL}/user/repository_invitations/{invitation_id}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    r = get_session(token).patch(url, headers=headers, timeout=15)
    if r.status_code in (204,):
        return True
    raise Exception(f"API Error: {r.text}")

def fetch_yearly_commit_data(username, token, year):
    query = f"""
    query {{ user(login: "{username}") {{ contributionsCollection(from: "{year}-01-01T00:00:00Z", to: "{year}-12-31T23:59:59Z") {{ contributionCalendar {{ weeks {{ contributionDays {{ date contributionCount }} }} }} }} }} }}
    """
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = get_session(token).post(GRAPHQL_URL, json={"query": query}, headers=headers, timeout=15)
        if r.status_code != 200: return []
        data = r.json()
        if "errors" in data: return []
        calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        days = []
        for w in calendar["weeks"]:
            for d in w["contributionDays"]: days.append(d)
        return days
    except: return []

# --- INTELLIGENT AI FUNCTIONS ---

def ask_ai_safe(prompt_func, arg, context=""):
    global ai_fallback_mode, ai_manager

    # Перевірка наявності ключів
    if ai_fallback_mode or not AI_AVAILABLE or not ai_manager or not ai_manager.keys:
        return "CRITICAL_FAILURE: No AI library or keys found."

    attempts = len(ai_manager.keys)
    last_exception_msg = "Unknown Error"
    transient_retry_limit = 2

    def _to_err_msg(err):
        try:
            return str(err)
        except:
            return repr(err)

    def _is_not_found(err_msg):
        msg = err_msg.upper()
        return "404" in msg or "NOT_FOUND" in msg

    def _is_rate_limited(err_msg):
        msg = err_msg.upper()
        return "429" in msg or "RESOURCE_EXHAUSTED" in msg or "RATE_LIMIT" in msg

    def _is_transient(err_msg):
        msg = err_msg.upper()
        transient_markers = (
            "503", "UNAVAILABLE", "DEADLINE_EXCEEDED", "INTERNAL",
            "TIMEOUT", "TIMED OUT", "SERVICE UNAVAILABLE", "CONNECTION RESET"
        )
        return any(marker in msg for marker in transient_markers)

    def _is_auth_error(err_msg):
        msg = err_msg.upper()
        auth_markers = (
            "401", "403", "UNAUTHENTICATED", "PERMISSION_DENIED",
            "API_KEY_INVALID", "INVALID API KEY", "FORBIDDEN"
        )
        return any(marker in msg for marker in auth_markers)

    for _ in range(attempts):
        key = ai_manager.get_current_key()
        try:
            client = genai.Client(api_key=key)

            # Формування промпта
            if context:
                full_prompt = prompt_func(arg, context)
            else:
                full_prompt = prompt_func(arg)

            # Спроба різних моделей (Fallback)
            for model_name in AI_MODEL_FALLBACKS:
                for transient_try in range(transient_retry_limit + 1):
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=full_prompt
                        )
                        # ЯКЩО УСПІХ - Повертаємо текст
                        resp_text = getattr(response, 'text', None)
                        if resp_text is None:
                            last_exception_msg = f"Model {model_name} returned empty response text"
                            print(f"⚠️ API Warning ({model_name}): {last_exception_msg}")
                            break
                        return str(resp_text).strip()

                    except Exception as e:
                        err_msg = _to_err_msg(e)
                        # Зберігаємо помилку, щоб показати її, якщо нічого не спрацює
                        last_exception_msg = f"Model {model_name} failed: {err_msg}"

                        # Логуємо в консоль для тебе
                        print(f"⚠️ API Warning ({model_name}): {err_msg}")
                        try:
                            logging.error(f"ask_ai_safe model error ({model_name}): {err_msg}", exc_info=True)
                        except:
                            pass

                        # Якщо 404 (моделі немає) - пробуємо наступну
                        if _is_not_found(err_msg):
                            break

                        # Якщо 503/timeout та інші тимчасові - робимо backoff на тій самій моделі
                        if _is_transient(err_msg) and transient_try < transient_retry_limit:
                            wait_seconds = 2 ** transient_try
                            print(
                                f"⏳ Temporary API issue ({model_name}), "
                                f"retry {transient_try + 1}/{transient_retry_limit} in {wait_seconds}s"
                            )
                            time.sleep(wait_seconds)
                            continue

                        # Інші помилки передаємо вище для обробки ключа/ротації
                        raise e

            # Жодна модель не спрацювала з цим ключем - пробуємо наступний
            ai_manager.rotate()

        except Exception as e:
            last_exception_msg = _to_err_msg(e)

            if _is_rate_limited(last_exception_msg):
                print(f"⚠️ Key Limited ({key[:5]}...): {last_exception_msg}")
                try:
                    logging.error(f"ask_ai_safe key limited ({key[:5]}...): {last_exception_msg}", exc_info=True)
                except:
                    pass
                try:
                    cooldown_time = (datetime.datetime.now() + datetime.timedelta(seconds=45)).strftime("%H:%M:%S")
                    ai_manager.keys[ai_manager.current_idx]['status'] = 'limit'
                    ai_manager.keys[ai_manager.current_idx]['cooldown_until'] = cooldown_time
                except:
                    pass
                ai_manager.rotate()

            elif _is_transient(last_exception_msg):
                print(f"⏳ API Temporary Error ({key[:5]}...): {last_exception_msg}")
                try:
                    logging.error(f"ask_ai_safe transient api error ({key[:5]}...): {last_exception_msg}", exc_info=True)
                except:
                    pass
                try:
                    cooldown_time = (datetime.datetime.now() + datetime.timedelta(seconds=20)).strftime("%H:%M:%S")
                    current = ai_manager.keys[ai_manager.current_idx]
                    prev_status = current.get('status', 'unknown')
                    if prev_status not in ('dead', 'limit'):
                        current['prev_status'] = prev_status
                    current['status'] = 'temp'
                    current['cooldown_until'] = cooldown_time
                except:
                    pass
                ai_manager.rotate()

            elif _is_auth_error(last_exception_msg):
                print(f"❌ Key Error ({key[:5]}...): {last_exception_msg}")
                try:
                    logging.error(f"ask_ai_safe key auth error ({key[:5]}...): {last_exception_msg}", exc_info=True)
                except:
                    pass
                try:
                    ai_manager.keys[ai_manager.current_idx]['status'] = 'dead'
                    ai_manager.keys[ai_manager.current_idx].pop('cooldown_until', None)
                    ai_manager.keys[ai_manager.current_idx].pop('prev_status', None)
                except:
                    pass
                ai_manager.rotate()

            else:
                print(f"⚠️ API Error ({key[:5]}...): {last_exception_msg}")
                try:
                    logging.error(f"ask_ai_safe api error ({key[:5]}...): {last_exception_msg}", exc_info=True)
                except:
                    pass
                ai_manager.rotate()

            continue

    return f"CRITICAL_FAILURE: {last_exception_msg}"

# --- PROMPTS ---

def prompt_refactor_code(code_snippet, username):
    current_year = datetime.date.today().year
    return f"""
    You are a STRICT Code Formatter & Linter.
    RULES:
    1. VISUALS ONLY: Fix indentation, whitespace, newlines. 
    2. IMPORTS: Sort imports.
    3. LOGIC SAFETY: DO NOT change logic.
    4. COMMENTS: Replace names with '{username}'. Update years to '{current_year}'.
    5. OUTPUT: RAW CODE ONLY. NO MARKDOWN.
    Code:
    {code_snippet[:20000]} 
    """

def prompt_pr_summary(commit_list, _=None):
    commits_str = "\n".join(commit_list[:20])
    return f"""
    Write a professional Pull Request description (Markdown) based on these commits:
    {commits_str}
    
    Structure:
    ### Changes
    - (Bullet points)
    
    Keep it concise. No placeholders.
    """

def prompt_release_notes(commit_list, version):
    commits_str = "\n".join(commit_list[:30])
    return f"""
    Generate Release Notes for version {version}.
    Commits:
    {commits_str}
    
    Format:
    # What's New in {version}
    ## Features
    ...
    ## Bug Fixes
    ...
    """

def prompt_repo_analysis(file_tree_str, readme): 
    return f"""
    Analyze this project structure and README.
    
    Files:
    {file_tree_str[:5000]}
    
    README Snippet:
    {readme[:2000]}
    
    Output Format:
    **Quality Score**: [1-10]/10
    **Stack**: [Languages/Frameworks]
    **Business Logic**: [Short summary of what this app does and if it has commercial value]
    **Red Flags**: [Any bad practices found or "None"]
    """

# (Old prompts kept for compatibility)
def prompt_commit(filename): return f"Write ONE short casual commit message for file '{filename}'."
def prompt_readme(content): return f"Rewrite this README to sound Senior.\n\n{content[:5000]}"
def prompt_new_readme(repo_name, _=None): return f"Generate a professional README for '{repo_name}'."

def get_ai_commit_message(filename):
    res = ask_ai_safe(prompt_commit, filename)
    if res and str(res).startswith("CRITICAL_FAILURE"): return "CRITICAL_FAILURE"
    if res: return res.replace('"', '').replace("'", "")
    return random.choice(PROFESSIONAL_COMMITS)

def get_ai_readme(content):
    res = ask_ai_safe(prompt_readme, content)
    return res if (res and not str(res).startswith("CRITICAL_FAILURE")) else content

def get_ai_new_readme(repo_name):
    res = ask_ai_safe(prompt_new_readme, repo_name)
    return res if (res and not str(res).startswith("CRITICAL_FAILURE")) else f"# {repo_name}\n\nProject generated."

# --- SEARCH & CLONER HELPERS ---

def format_size(size_kb):
    if size_kb < 1024: return f"{size_kb} KB"
    mb = size_kb / 1024
    if mb < 1024: return f"{mb:.1f} MB"
    return f"{mb/1024:.2f} GB"

def calculate_senior_days(size_kb, language):
    days = size_kb / SENIOR_VELOCITY_KB_PER_DAY
    weight = LANGUAGE_WEIGHTS.get(language, LANGUAGE_WEIGHTS["default"])
    days = days * weight * (7/6)
    return max(1, int(days))

def format_duration(days):
    if days < 30: return f"{days} days"
    if days < 365: return f"{days//30} mo"
    return f"{days/365:.1f} y"

def get_real_duration_str(created_at, pushed_at):
    try:
        start = datetime.datetime.strptime(created_at[:10], "%Y-%m-%d")
        end = datetime.datetime.strptime(pushed_at[:10], "%Y-%m-%d")
        return format_duration((end - start).days)
    except: return "?"

def resolve_stack_search_rule(stack_name):
    return STACK_SEARCH_RULES.get(stack_name or "", {})

def resolve_stack_primary_language(stack_name):
    rule = resolve_stack_search_rule(stack_name)
    return rule.get("language", stack_name)

def search_github_repos(token, query, items, niche_topics, scale_key, min_s, max_s, sort_key, page, log_func=None, strict_mode=False):
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Формуємо базовий запит (Ключові слова)
    q_parts = []
    if query: q_parts.append(query)
    
    # 2. Додаємо стек-фільтри (беремо тільки перший обраний стек для стабільного GitHub Search)
    if items:
        selected_stack = items[0]
        stack_rule = resolve_stack_search_rule(selected_stack)
        lang_filter = stack_rule.get("language", selected_stack)
        if lang_filter:
            q_parts.append(f"language:{lang_filter}")
        keywords = stack_rule.get("keywords", [])
        if keywords:
            keyword_group = " OR ".join(k if " " not in k else f"\"{k}\"" for k in keywords)
            q_parts.append(f"({keyword_group})")
    
    # 3. НІША: Об'єднуємо всі теми через OR для кращого пошуку
    if niche_topics:
        # Створюємо групу: (topic:finance OR topic:fintech OR ...)
        topic_group = " OR ".join(niche_topics)
        q_parts.append(f"({topic_group})")
        
    # 4. Фільтр розміру
    scale_filter = SCALES.get(scale_key, "")
    if scale_filter: q_parts.append(scale_filter)
    
    # 5. Фільтр зірок
    try:
        min_v = int(min_s) if min_s else 0
        max_v = int(max_s) if max_s else 1000000
        q_parts.append(f"stars:{min_v}..{max_v}")
    except: 
        q_parts.append("stars:0..1000000")

    # 6. Дата (Strict Mode)
    if strict_mode: 
        q_parts.append("pushed:>2023-01-01") # Шукаємо свіжіше для суворого режиму
    else:
        q_parts.append("pushed:>2021-01-01") 
    
    # Збираємо запит
    final_query = " ".join(q_parts)
    
    if log_func: log_func(f"🔍 Page {page} | Query -> {final_query}")
    
    params = {"q": final_query, "per_page": 20, "page": page, "sort": sort_key or "stars"}
    
    try:
        r = get_session(token).get(f"{REST_API_URL}/search/repositories", headers=headers, params=params, timeout=15)
        if r.status_code == 200: 
            return r.json().get("items", []), r.json().get("total_count", 0)
        else:
            if log_func: log_func(f"API Error {r.status_code}: {r.text}")
    except Exception as e:
        if log_func: log_func(f"Net Error: {e}")
        
    return [], 0

def download_file_content(token, url, local_path):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3.raw"}
    try:
        with get_session(token).get(url, headers=headers, stream=True, timeout=10) as r:
            if r.status_code != 200: return False
            if int(r.headers.get("Content-Length", 0)) > 25 * 1024 * 1024: return False 
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
            return True
    except: return False

class GitHubService:
    def __init__(self, token=None):
        self.session = get_session(token)

    def get(self, url, **kwargs):
        return self.session.get(url, **kwargs)

# ===================== NEW: ANALYTICS POPUP (REPO DOSSIER) =====================

class RepoDossier(ctk.CTkToplevel):
    def __init__(self, parent, repo_item, token):
        super().__init__(parent)
        self.repo = repo_item
        self.token = token
        self.gh = GitHubService(token)
        self.title(f"Dossier: {repo_item['full_name']}")
        self.geometry("1000x800")
        
        # Головний скрол-контейнер (Всередині все буде блоками)
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="#F0F0F0")
        self.scroll.pack(fill="both", expand=True)

        # 1. HEADER BLOCK (Назва, Докер, Бейджі)
        self.build_header_block()

        # 2. ACTIVITY BLOCK (Графіки + Дати)
        self.build_activity_block()

        # 3. CONTRIBUTORS BLOCK (Випадаючий список)
        self.build_contributors_block()

        # 4. FILE TREE BLOCK (Дерево папок)
        self.build_tree_block()

        # 5. AI ANALYSIS BLOCK
        self.build_ai_block()

        # Запуск завантаження даних
        threading.Thread(target=self.load_all_data, daemon=True).start()

    def build_card(self, title):
        # Допоміжна функція для створення гарних білих блоків
        f = ctk.CTkFrame(self.scroll, fg_color="white", corner_radius=10)
        f.pack(fill="x", padx=15, pady=10)
        if title:
            ctk.CTkLabel(f, text=title, font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", padx=15, pady=(10, 5))
            ctk.CTkFrame(f, height=1, fg_color="#EEE").pack(fill="x", padx=5) # Розділювач
        return f

    def build_header_block(self):
        f = self.build_card(None)
        
        # Верхній ряд: Назва + Docker
        row1 = ctk.CTkFrame(f, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=15)
        
        # Назва
        ctk.CTkLabel(row1, text=self.repo['full_name'], font=("Arial", 20, "bold"), text_color="black").pack(side="left")
        
        # Docker Icon (Прихований за замовчуванням)
        self.lbl_docker = ctk.CTkLabel(row1, text="🐳 Docker Ready", font=("Arial", 14, "bold"), text_color="#007AFF")
        # (Ми покажемо його пізніше, якщо знайдемо файл)

        # Опис
        desc = self.repo['description'] or "No description."
        ctk.CTkLabel(f, text=desc, text_color="#555", wraplength=900, justify="left", font=("Arial", 12)).pack(anchor="w", padx=15, pady=(0, 15))
        
        # Кнопка Select
        ctk.CTkButton(
            f,
            text="SELECT THIS PROJECT",
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="black",
            command=self.select_and_close,
        ).pack(fill="x", padx=15, pady=(0, 15))

    def build_activity_block(self):
        f = self.build_card("📊 Activity & Pulse")
        f_grid = ctk.CTkFrame(f, fg_color="transparent")
        f_grid.pack(fill="x", padx=15, pady=10)
        f_grid.grid_columnconfigure(0, weight=1)
        f_grid.grid_columnconfigure(1, weight=1)

        # --- LEFT: Sparkline + Dates ---
        f_left = ctk.CTkFrame(f_grid, fg_color="transparent")
        f_left.grid(row=0, column=0, sticky="nsew")
        
        # Дати
        self.lbl_dates = ctk.CTkLabel(f_left, text="Loading dates...", text_color="gray", font=("Consolas", 12))
        self.lbl_dates.pack(anchor="w")
        
        # Sparkline Canvas
        self.cv_spark = tk.Canvas(f_left, height=60, bg="white", highlightthickness=0)
        self.cv_spark.pack(fill="x", pady=10)
        self.cv_spark.create_text(100, 30, text="Loading Activity...", fill="gray")

        # --- RIGHT: Languages ---
        f_right = ctk.CTkFrame(f_grid, fg_color="transparent")
        f_right.grid(row=0, column=1, sticky="nsew", padx=(20,0))
        
        self.cv_pie = tk.Canvas(f_right, height=120, width=120, bg="white", highlightthickness=0)
        self.cv_pie.pack(side="left")
        self.scroll_legend = ctk.CTkScrollableFrame(f_right, fg_color="transparent", height=120)
        self.scroll_legend.pack(side="left", fill="both", expand=True)

    def build_contributors_block(self):
        f = self.build_card(None) # Без заголовка, бо це кнопка
        self.btn_contrib = ctk.CTkButton(
            f,
            text="👥 Contributors (Loading...) ▼",
            fg_color="transparent",
            text_color="black",
            font=("Arial", 12, "bold"),
            border_width=1,
            border_color="#CCC",
            command=self.toggle_contributors,
        )
        self.btn_contrib.pack(fill="x", padx=15, pady=10)
        
        self.f_contrib_list = ctk.CTkFrame(f, fg_color="#FAFAFA")
        # Спочатку сховано
        
    def toggle_contributors(self):
        if self.f_contrib_list.winfo_viewable():
            self.f_contrib_list.pack_forget()
        else:
            self.f_contrib_list.pack(fill="x", padx=15, pady=(0,10))

    def build_tree_block(self):
        f = self.build_card("📂 File Structure")

        self.f_stats = ctk.CTkFrame(f, fg_color="#2B2B2B", corner_radius=6)
        self.f_stats.pack(fill="x", padx=15, pady=(10, 0))

        ctk.CTkLabel(self.f_stats, text="PROJECT STATS", font=("Arial", 10, "bold"), text_color="gray").pack(pady=(5,0))

        self.lbl_score_val = ctk.CTkLabel(self.f_stats, text="-- / 100", font=("Arial", 24, "bold"), text_color="white")
        self.lbl_score_val.pack(pady=0)

        self.lbl_score_title = ctk.CTkLabel(self.f_stats, text="CREDIT SCORE", font=("Arial", 10), text_color="gray")
        self.lbl_score_title.pack(pady=(0, 5))

        ctk.CTkFrame(self.f_stats, height=1, fg_color="gray").pack(fill="x", padx=10, pady=5)

        self.lbl_time_val = ctk.CTkLabel(self.f_stats, text="-- months", font=("Arial", 14, "bold"), text_color="#4CAF50")
        self.lbl_time_val.pack(pady=0)

        ctk.CTkLabel(self.f_stats, text="TIME TO BUILD", font=("Arial", 10), text_color="gray").pack(pady=(0, 10))

        self._load_cached_stats()
        
        # Стилізація дерева
        style = ttk.Style()
        style.configure("Treeview", background="white", fieldbackground="white", foreground="black", borderwidth=0)
        
        self.tree = ttk.Treeview(f, show="tree", height=10)
        self.tree.pack(fill="x", padx=15, pady=10)
        
        # Кнопка "Load More" (Спочатку прихована)
        self.btn_load_more = ctk.CTkButton(
            f,
            text="⬇ Load More Files (+50)",
            fg_color="#E0E0E0",
            text_color="black",
            command=self.load_more_files_click,
        )
        
        # Скролбар
        scrollbar = ttk.Scrollbar(f, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def build_ai_block(self):
        f_card = ctk.CTkFrame(self.scroll, fg_color="white", corner_radius=10)
        f_card.pack(fill="x", padx=15, pady=10)
        
        # Header
        f_head = ctk.CTkFrame(f_card, fg_color="transparent")
        f_head.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(f_head, text="🤖 AI Architect Chat", font=("Arial", 14, "bold"), text_color="#333").pack(side="left")
        ctk.CTkButton(
            f_head,
            text="📄 Export",
            width=80,
            height=24,
            fg_color="#EEE",
            text_color="black",
            command=self.export_report,
        ).pack(side="right")
        ctk.CTkFrame(f_card, height=1, fg_color="#EEE").pack(fill="x", padx=5)

        # Start Cover
        self.f_start_cover = ctk.CTkFrame(f_card, fg_color="white", height=150)
        self.f_start_cover.pack(fill="x", pady=20)
        ctk.CTkButton(
            self.f_start_cover,
            text="🚀 START DEEP ANALYSIS",
            height=50,
            font=("Arial", 13, "bold"),
            fg_color="black",
            command=self.run_deep_analysis,
        ).pack(pady=10)

        # Chat Area
        self.f_chat_area = ctk.CTkFrame(f_card, fg_color="transparent")
        
        # Чат
        self.txt_chat = ctk.CTkTextbox(self.f_chat_area, height=300, fg_color="#FAFAFA", text_color="#333", font=("Arial", 12))
        self.txt_chat.pack(fill="x", padx=15, pady=(10, 5))
        self.txt_chat.configure(state="disabled")
        
        # --- LOADING STATUS (НОВЕ) ---
        self.lbl_ai_status = ctk.CTkLabel(self.f_chat_area, text="", text_color="#007AFF", font=("Arial", 11, "italic"))
        self.lbl_ai_status.pack(anchor="w", padx=20, pady=(0, 5))
        # -----------------------------

        # Quick Actions
        f_quick = ctk.CTkFrame(self.f_chat_area, fg_color="transparent")
        f_quick.pack(fill="x", padx=15, pady=5)
        for label, query in [
            ("🐛 Find Bugs", "Analyze potential bugs/security risks."),
            ("📚 Explain Stack", "Explain the tech stack."),
            ("🛠 How to Run", "Guide on how to run this."),
        ]:
            ctk.CTkButton(
                f_quick,
                text=label,
                width=80,
                height=24,
                fg_color="#E0E0E0",
                text_color="black",
                command=lambda q=query: self.send_ai_query(msg_override=q),
            ).pack(side="left", padx=2)

        # Input
        f_input = ctk.CTkFrame(self.f_chat_area, fg_color="transparent")
        f_input.pack(fill="x", padx=15, pady=(0, 15))
        self.entry_chat = ctk.CTkEntry(f_input, placeholder_text="Ask Architect...")
        self.entry_chat.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_chat.bind("<Return>", self.send_ai_query)
        ctk.CTkButton(f_input, text="➤", width=40, command=self.send_ai_query).pack(side="right")
        
        self.load_chat_history()
        
        repo_id = self.repo['full_name']
        if repo_id in self.chat_data and self.chat_data[repo_id]:
            self.f_start_cover.pack_forget()
            self.f_chat_area.pack(fill="x")

    def _get_cache_file(self):
        return "repo_stats_cache.json"

    def _load_cached_stats(self):
        """Завантажує статистику з файлу, якщо вона там є"""
        import json
        import os

        cache_file = self._get_cache_file()
        if not os.path.exists(cache_file):
            return

        try:
            with open(cache_file, "r") as f:
                data = json.load(f)

            repo_key = self.repo['full_name']

            if repo_key in data:
                stats = data[repo_key]
                self.lbl_score_val.configure(text=f"{stats.get('score', '--')} / 100")

                score = int(stats.get('score', 0))
                color = "#FF5252" if score < 50 else "#FFAB00" if score < 80 else "#00E676"
                self.lbl_score_val.configure(text_color=color)

                self.lbl_time_val.configure(text=stats.get('time_estimate', '--'))
        except Exception as e:
            print(f"Cache load error: {e}")

    def _save_stats_to_cache(self, score, time_est):
        """Зберігає нові дані в кеш"""
        import json
        import os

        cache_file = self._get_cache_file()
        data = {}

        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
            except:
                pass

        repo_key = self.repo['full_name']
        data[repo_key] = {
            "score": score,
            "time_estimate": time_est,
            "last_updated": "now"
        }

        with open(cache_file, "w") as f:
            json.dump(data, f, indent=4)

        self._load_cached_stats()

    def _smart_update_stats(self, response_text):
        """Витягує цифри з відповіді AI, безпечно обробляючи помилки"""
        import re
        import json

        if not response_text:
            return "⚠️ AI Analysis Failed (No Data)", 0, "?"

        rt = str(response_text)
        if "CRITICAL_FAILURE" in rt or "RESOURCE_EXHAUSTED" in rt:
            return f"⚠️ API Error: {rt[:100]}...", 0, "?"

        score = 0
        time_est = "?"

        try:
            clean_json = rt.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            metrics = data.get("metrics", {})
            score = metrics.get("total_score", 0)
            time_est = metrics.get("time_to_build", "?")
            return data.get("markdown_report", rt), score, time_est
        except:
            pass

        try:
            table_scores = re.findall(r"\|\s*\*\*.*?\*\*\s*\|\s*(\d+)\s*\|", rt)
            if table_scores:
                scores = [int(s) for s in table_scores]
                if scores:
                    score = int(sum(scores) / len(scores)) * 10
                    if score > 100:
                        score = int(score / 10)

            if score == 0:
                match = re.search(r"(?:Total Score|FINAL SCORE|Credit Score)[:\s]*(\d+)", rt, re.IGNORECASE)
                if match:
                    score = int(match.group(1))

            time_match = re.search(r"(?:Time to Build|Estimated Time)[:\s]*([\d\s\w]+)", rt, re.IGNORECASE)
            if time_match:
                time_est = time_match.group(1).strip()

        except Exception as e:
            print(f"Regex parsing failed: {e}")
            try:
                logging.error(f"RepoDossier _smart_update_stats regex parsing failed: {e}", exc_info=True)
            except:
                pass

        return rt, score, time_est

    def _append_chat_msg(self, author, text):
        self._render_msg(author, text, save=True)

    # --- ANIMATION LOGIC ---
    def start_loading(self, text="AI is thinking"):
        self.ai_loading = True
        self.loading_text = text
        self.loading_dots = 0
        self._animate_loading()

    def stop_loading(self):
        self.ai_loading = False
        self.lbl_ai_status.configure(text="") # Очищаємо статус

    def _animate_loading(self):
        if not self.ai_loading: return
        
        dots = "." * (self.loading_dots % 4) # ., .., ...
        self.lbl_ai_status.configure(text=f"🧠 {self.loading_text}{dots}")
        self.loading_dots += 1
        self.after(500, self._animate_loading) # Оновлення кожні 0.5 сек

    # --- PERSISTENCE & EXPORT ---
    def load_chat_history(self):
        self.chat_file = os.path.join(DATA_DIR, "dossier_chats.json")
        self.chat_data = {}
        if os.path.exists(self.chat_file):
            try:
                self.chat_data = json.load(open(self.chat_file, "r", encoding="utf-8"))
            except:
                pass
        
        # Завантажуємо історію для конкретного репо
        repo_id = self.repo['full_name']
        history = self.chat_data.get(repo_id, [])
        for msg in history:
            self._render_msg(msg['author'], msg['text'], save=False)

    def save_chat_msg(self, author, text):
        repo_id = self.repo['full_name']
        if not hasattr(self, 'chat_data') or self.chat_data is None:
            self.chat_data = {}
        if repo_id not in self.chat_data:
            self.chat_data[repo_id] = []
        
        self.chat_data[repo_id].append({"author": author, "text": text, "time": datetime.datetime.now().strftime("%H:%M")})
        
        if not hasattr(self, 'chat_file') or not self.chat_file:
            self.chat_file = os.path.join(DATA_DIR, "dossier_chats.json")
        
        try:
            json.dump(self.chat_data, open(self.chat_file, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        except:
            pass

    def export_report(self):
        # Відкриваємо діалог збереження
        filename = tk.filedialog.asksaveasfilename(
            defaultextension=".md",
            initialfile=f"REPORT_{self.repo['name']}.md",
            filetypes=[("Markdown", "*.md"), ("Text", "*.txt")],
        )
        if not filename:
            return
        
        # Формуємо звіт
        report = f"# Dossier Report: {self.repo['full_name']}\n\n"
        report += f"**Stars:** {self.repo['stargazers_count']} | **Language:** {self.repo['language']}\n"
        report += f"**Exported:** {datetime.datetime.now()}\n\n"
        
        report += "## 📂 File Structure\n```\n"
        # (Тут можна додати дерево файлів текстом, якщо воно збережене)
        report += "```\n\n"
        
        report += "## 🤖 AI Analysis & Chat History\n"
        repo_id = self.repo['full_name']
        if hasattr(self, 'chat_data') and repo_id in self.chat_data:
            for msg in self.chat_data[repo_id]:
                report += f"### {msg['author']} ({msg['time']})\n{msg['text']}\n\n"
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report)
            messagebox.showinfo("Export", "Report saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_deep_analysis(self):
        # 1. UI Setup
        self.f_start_cover.pack_forget()
        self.f_chat_area.pack(fill="x")
        
        # Кнопка СТОП
        self.stop_scan_flag = False
        self.btn_stop_scan = ctk.CTkButton(
            self.f_chat_area, 
            text="🛑 STOP FULL SCAN", 
            fg_color="red", 
            height=30,
            command=self.stop_scan_action
        )
        self.btn_stop_scan.pack(pady=(0, 10))
        
        # Запуск процесу
        threading.Thread(target=self._full_scan_orchestrator, daemon=True).start()

    def stop_scan_action(self):
        self.stop_scan_flag = True
        self.lbl_ai_status.configure(text="🛑 Stopping...", text_color="red")
        self.btn_stop_scan.pack_forget()

    def _full_scan_orchestrator(self):
        try:
            self.start_loading("Mapping Repository & Downloading Everything...")

            # 1. Фільтрація
            target_files = []
            IGNORED_EXTS = [
                '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp', '.mp4', '.mp3', '.pdf',
                'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'go.sum', 'Cargo.lock',
                '.pyc', '.exe', '.dll', '.so', '.dylib', '.csv', '.tsv', '.xlsx', '.sql', '.db', '.sqlite'
            ]
            IGNORED_DIRS = ['.git/', 'node_modules/', 'dist/', 'build/', 'venv/', '__pycache__/', '.next/', 'coverage/']

            for path in self.all_file_paths:
                if any(bad_dir in path for bad_dir in IGNORED_DIRS):
                    continue
                if any(path.lower().endswith(ext) for ext in IGNORED_EXTS):
                    continue
                target_files.append(path)

            if not target_files:
                self._render_msg("System", "❌ No analysable files found.", save=False)
                return

            # 2. Паралельне завантаження ВСЬОГО (Total Download)
            full_repo_data = []
            total_chars = 0

            self.after(0, lambda: setattr(self, 'loading_text', f"Downloading {len(target_files)} files..."))

            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_path = {executor.submit(self._fetch_single_file, p): p for p in target_files}

                for i, future in enumerate(concurrent.futures.as_completed(future_to_path)):
                    if self.stop_scan_flag:
                        break
                    try:
                        result = future.result()
                        if result:
                            full_repo_data.append(result)
                            total_chars += len(result)
                    except Exception as e:
                        print(f"Error fetching file: {e}")

                    if i % 10 == 0:
                        mb = total_chars / (1024*1024)
                        self.after(0, lambda m=mb: setattr(self, 'loading_text', f"Downloaded {m:.2f} MB..."))

            if self.stop_scan_flag:
                self.after(0, lambda: self.lbl_ai_status.configure(text="🛑 Aborted", text_color="red"))
                return

            # 3. Вибір стратегії (Single Shot vs Map-Reduce)
            SAFE_LIMIT = 2_500_000
            self.btn_stop_scan.pack_forget()

            if total_chars < SAFE_LIMIT:
                self.after(0, lambda: setattr(self, 'loading_text', "Size OK. Running Single-Pass Analysis..."))
                full_context = "".join(full_repo_data)
                self._agent_step_3_analyze(full_context, metadata_override=f"Full Scan ({total_chars/1024/1024:.1f}MB)")
            else:
                self.after(0, lambda: setattr(self, 'loading_text', f"Repo is HUGE ({total_chars/1024/1024:.1f}MB). Starting Map-Reduce..."))
                self._run_map_reduce_analysis(full_repo_data, total_chars)

        except Exception as e:
            self.btn_stop_scan.pack_forget()
            self._render_msg("Error", f"Scan failed: {str(e)}", save=False)
            try:
                logging.error(f"RepoDossier _full_scan_orchestrator failed: {e}", exc_info=True)
            except:
                pass

    def _fetch_single_file(self, path):
        if self.stop_scan_flag: return None
        
        if any(path.lower().endswith(ext) for ext in ['.lock', '.min.js', '.map', '.svg']):
            return None

        try:
            url = f"https://raw.githubusercontent.com/{self.repo['full_name']}/{self.repo['default_branch']}/{path}"

            with get_session(self.token).get(url, stream=True, timeout=10) as r:
                if r.status_code != 200: return None

                size = int(r.headers.get('content-length', 0))
                if size > 50 * 1024:
                    return None

                content = r.text

                if len(content) > 50000:
                    return None

                return f"\n=== FILE: {path} ===\n{content}\n"
        except:
            return None

    def _run_map_reduce_analysis(self, all_files_data, total_size):
        import json
        import time

        CHUNK_SIZE = 100_000
        chunks = []
        current_chunk = ""

        def sort_priority(item):
            low = item.lower()
            if "readme" in low or ".md" in low or "license" in low:
                return 100
            if "test" in low:
                return 50
            return 1

        all_files_data.sort(key=sort_priority)

        for file_content in all_files_data:
            if len(current_chunk) + len(file_content) > CHUNK_SIZE:
                chunks.append(current_chunk)
                current_chunk = file_content
            else:
                current_chunk += file_content
        if current_chunk:
            chunks.append(current_chunk)

        chunk_summaries = []
        self.detected_entities = set()
        total_chunks = len(chunks)

        for i, chunk in enumerate(chunks):
            if self.stop_scan_flag:
                return

            if i > 0:
                wait_time = 40
                self.after(0, lambda w=wait_time: setattr(self, 'loading_text', f"Cooling down API (waiting {w}s)..."))
                time.sleep(wait_time)

            chunk_num = i + 1
            self.after(0, lambda n=chunk_num, t=total_chunks: setattr(self, 'loading_text', f"Analyzing Part {n}/{t} (Deep Scan & Entity Search)..."))

            map_prompt = f"""
            ACT AS: Senior Tech Lead.
            TASK: Analyze this code chunk ({chunk_num}/{total_chunks}).
            
            GOALS:
            1. EXTRACT AUTHORSHIP: Names, emails, copyrights (for sanitization).
            2. GENERATE TASKS: Create 2-3 realistic GitHub Issue tasks based on the code (e.g., "Refactor auth_utils", "Add type hints to user_model").
            
            SOURCE CODE:
            {chunk}
            
            ---
            OUTPUT FORMAT (Strict JSON):
            {{
                \"detected_authors\": [\"Name\", \"Email\"],
                \"smart_tasks\": [
                    {{\"title\": \"Refactor [Component]\", \"body\": \"The logic in [Function] is too complex...\"}},
                    {{\"title\": \"Fix TODO in [File]\", \"body\": \"Found a TODO comment that needs addressing...\"}}
                ]
            }}
            """

            response = ask_ai_safe(lambda x: x, map_prompt)

            if not response or str(response).startswith("CRITICAL_FAILURE"):
                chunk_summaries.append(f"Part {chunk_num} Failed.")
            else:
                try:
                    clean_json = str(response).replace("```json", "").replace("```", "").strip()
                    data = json.loads(clean_json)

                    chunk_summaries.append(f"=== PART {chunk_num} ===\nOK")

                    for entity in data.get("detected_authors", []):
                        try:
                            if isinstance(entity, str) and len(entity) > 0:
                                self.detected_entities.add(entity.strip())
                        except:
                            pass

                    if "smart_tasks" in data:
                        try:
                            if hasattr(self, 'master') and self.master:
                                if not hasattr(self.master, 'smart_issues_queue'):
                                    self.master.smart_issues_queue = []
                                self.master.smart_issues_queue.extend(data.get("smart_tasks") or [])
                        except:
                            pass

                except:
                    chunk_summaries.append(f"=== PART {chunk_num} (Raw) ===\n{str(response)[:500]}...")

        if self.stop_scan_flag:
            return

        if getattr(self, 'detected_entities', None):
            self.after(0, lambda: self._show_scrub_button())

        self.after(0, lambda: setattr(self, 'loading_text', "Synthesizing Report..."))

        combined_findings = "\n".join(chunk_summaries)
        final_reduce_prompt = f"""
        ACT AS: Lead Technical Auditor & Project Appraiser.
        INPUT: Partial reports from chunks.
        
        DATA:
        {combined_findings}
        
        ---
        ### MISSION
        1. Synthesize a Markdown Report.
        2. CALCULATE METRICS:
           - Credit Score (0-100): Based on code quality, architecture, and security.
             (90+ = Google/Netflix Standard, 70+ = Solid, <50 = Spaghetti).
           - Time to Build: Estimate how long 1 Senior Dev would take to build this from scratch (e.g., "2 weeks", "6 months").
        
        ---
        ### OUTPUT FORMAT (Strict JSON)
        {{
            \"markdown_report\": \"# Audit Report\\n...\",
            \"metrics\": {{
                \"total_score\": 85,
                \"time_to_build\": \"3 months\"
            }}
        }}
        """

        threading.Thread(target=self._ai_worker, args=(final_reduce_prompt, True), daemon=True).start()

    def _show_scrub_button(self):
        """Показує кнопку 'Review Authors' біля статусу"""
        btn = ctk.CTkButton(
            self.f_chat_area,
            text=f"🕵️ Found {len(self.detected_entities)} Entities - Review & Scrub",
            fg_color="#F57C00",
            hover_color="#E65100",
            command=self.open_scrubber_window
        )
        btn.pack(pady=5)

    def open_scrubber_window(self):
        """Відкриває вікно зі списком знайдених імен"""
        win = ctk.CTkToplevel(self)
        win.title("Author Sanitizer (White-Labeling)")
        win.geometry("600x500")

        ctk.CTkLabel(win, text="Select entities to replace with YOUR identity:", font=("Arial", 16, "bold")).pack(pady=10)

        # Контейнер для списку
        scroll = ctk.CTkScrollableFrame(win)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        self.scrub_vars = {}

        for entity in sorted(list(self.detected_entities)):
            frame = ctk.CTkFrame(scroll)
            frame.pack(fill="x", pady=2)

            var = tk.BooleanVar(value=True)
            self.scrub_vars[entity] = var

            cb = ctk.CTkCheckBox(frame, text=entity, variable=var)
            cb.pack(side="left", padx=5)

            ctk.CTkLabel(frame, text="➜ [ME]", text_color="gray").pack(side="right", padx=10)

        # Кнопка дії
        btn_scrub = ctk.CTkButton(
            win,
            text="✅ SAVE LIST FOR CLONING",
            fg_color="green",
            command=lambda: self._save_scrub_list(win)
        )
        btn_scrub.pack(pady=10)

    def _save_scrub_list(self, window):
        """Зберігає список замін"""
        final_list = [k for k, v in self.scrub_vars.items() if v.get()]
        self.approved_scrub_list = final_list
        print(f"Sanitization List Saved: {len(final_list)} items")
        window.destroy()
        
        # Можна відразу запропонувати зберегти "очищений" код
        # self.export_scrubbed_code()

    def apply_sanitization(self, content):
        """Замінює всі знайдені імена на дані користувача"""
        if not hasattr(self, 'approved_scrub_list') or not self.approved_scrub_list:
            return content

        my_name = ""
        try:
            my_name = getattr(self.master, 'username', '') or ""
        except:
            my_name = ""

        my_email = ""
        try:
            if hasattr(self.master, '_read_auth_file'):
                my_email = (self.master._read_auth_file() or {}).get('default_email', '')
        except:
            my_email = ""

        if not my_email:
            try:
                if os.path.exists(AUTH_FILE):
                    my_email = (json.load(open(AUTH_FILE, 'r')) or {}).get('default_email', '')
            except:
                my_email = ""

        if not my_name:
            my_name = "ME"
        if not my_email:
            my_email = "me@example.com"

        clean_content = content
        for entity in self.approved_scrub_list:
            try:
                replacement = my_email if "@" in entity else my_name
                clean_content = clean_content.replace(entity, replacement)
            except:
                pass

        return clean_content

    def _agent_step_3_analyze(self, file_contents, metadata_override=""):
        # Оновлюємо статус
        
        # --- РОЗУМНИЙ ПОШУК ТЕСТІВ ---
        test_indicators = ["__tests__", ".test.", ".spec.", "/tests/", "/test/"]
        has_tests_in_tree = any(ind in path for path in self.all_file_paths for ind in test_indicators)
        test_flag = "✅ DETECTED in file tree" if has_tests_in_tree else "❌ NOT DETECTED (Critical Reliability Issue)"

        final_prompt = f"""
        ACT AS: A Strict Senior Technical Auditor.
        CONTEXT: You are performing a Full-Repository Code Quality Audit.
        TONE: Professional, Dry, Direct. 
        LANGUAGE: English.
        
        TARGET REPO: {self.repo['full_name']}
        METADATA: 
        - {metadata_override}
        - Tests: {test_flag} (Trust this over visible snippets).
        
        SOURCE CODE (FULL CONTEXT):
        {file_contents[:3000000]}  # Hard limit ~3MB just to be safe
        
        ---
        
        ### 🧠 CHAIN OF THOUGHT INSTRUCTIONS
        1. **Map**: Understand the project structure from imports.
        2. **Critique**: Look for high-level architectural flaws (God Objects, Circular Deps) AND low-level debt.
        3. **Score**: Apply the Rubric strictly.
        
        ### 📏 AUDIT RUBRIC
        
        #### 1. ARCHITECTURE
        - **Fail Condition:** God Objects, Spaghetti Logic.
        - **Tech Debt:** Is it hard to maintain?
        
        #### 2. CODE QUALITY
        - **Naming:** Descriptive? (`user_id` ✅ vs `u` ❌).
        - **Cyrillic Rule 🚨:** -2 POINTS if Cyrillic comments found.
        
        #### 3. SECURITY (OWASP)
        - **Secrets:** Hardcoded keys -> SCORE 0.
        - **Input:** Missing validation?
        
        #### 4. RELIABILITY
        - **Testing Rule:** If METADATA says "NOT DETECTED" -> Score -1.
        - **Error Handling:** No empty `except: pass`.
        
        ---
        
        ### 📝 REPORT FORMAT (Strict Markdown)
        
        **📋 Executive Summary**
        [Dry, technical summary of the codebase state.]
        
        **🛑 Critical Findings (Granular)**
        List 3-5 specific flaws:
        * **📍 Location:** `[File]` 
        * **🐛 Issue:** [Description]
        * **💡 Fix:** [Recommendation]
        
        **📊 Technical Score Card**
        
        | Category | Score (0-10) | Status | Assessment |
        | :--- | :---: | :---: | :--- |
        | **🏛 Architecture** | ? | [Risk Level] | [Brief] |
        | **💎 Code Quality** | ? | [Cleanliness] | [Brief] |
        | **🛡 Security** | ? | [Safety] | [Brief] |
        | **🧪 Reliability** | ? | [Coverage] | [Brief] |
        
        **⚖️ Tech Debt Verdict**: [Production Ready / Refactoring Candidate / Prototype / Legacy Dump]
        """
        
        threading.Thread(target=self._ai_worker, args=(final_prompt, True), daemon=True).start()

    def send_ai_query(self, event=None, msg_override=None):
        msg = msg_override if msg_override else self.entry_chat.get()
        if not msg: return
        
        self.entry_chat.delete(0, "end")
        self._render_msg("You", msg, save=True)
        
        # Формуємо контекст для звичайного питання
        context = f"Repo: {self.repo['full_name']}\nFiles: {self.ai_context_files}\nQuestion: {msg}"
        threading.Thread(target=self._ai_worker, args=(context, False), daemon=True).start()

    def _ai_worker(self, prompt, is_initial):
        # Якщо це просте повідомлення (не аналіз), теж вмикаємо анімацію
        try:
            if not getattr(self, 'ai_loading', False):
                self.after(0, lambda: self.start_loading("Thinking"))
        except:
            pass
            
        response_text = ask_ai_safe(lambda x: x, prompt)
        
        self.after(0, self.stop_loading) # СТОП АНІМАЦІЇ

        if is_initial:
            final_report, score, time_est = self._smart_update_stats(response_text)
            self.after(0, lambda r=final_report: self._render_msg("AI", r, save=True))

            if score and int(score) > 0:
                self.after(0, lambda s=score, t=time_est: self._save_stats_to_cache(s, t))
            else:
                self.after(0, lambda: self._save_stats_to_cache(50, "Unknown"))
            return

        self.after(0, lambda r=response_text: self._render_msg("AI", r, save=True))

    def _render_msg(self, author, text, save=True):
        self.txt_chat.configure(state="normal")
        t = datetime.datetime.now().strftime("%H:%M")
        
        if author == "You":
            self.txt_chat.insert("end", f"\n👤 You [{t}]:\n{text}\n", "user")
        else:
            self.txt_chat.insert("end", f"\n🤖 Architect [{t}]:\n{text}\n" + "─"*30 + "\n", "ai")
            
        self.txt_chat.see("end")
        self.txt_chat.configure(state="disabled")
        
        if save: self.save_chat_msg(author, text)

    def load_all_data(self):
        # 1. Завантаження мов (як було раніше, але з новим малюванням)
        self.load_languages()
        
        # 2. Файлове дерево + Docker Check
        self.load_tree_and_docker()
        
        # 3. Contributors
        self.load_contributors()
        
        # 4. Sparkline & Dates
        self.load_activity()

    def load_languages(self):
        langs = api_get_languages(self.token, self.repo['owner']['login'], self.repo['name'])
        if not langs: return
        total = sum(langs.values())
        sorted_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)
        
        # Малюємо (код з попереднього разу, але адаптований під cv_pie)
        self.cv_pie.delete("all")
        start = 90
        for i, (l, s) in enumerate(sorted_langs):
            perc = (s/total)*100
            if perc < 1: continue
            col = COLOR_CHART_COLORS[i%len(COLOR_CHART_COLORS)]
            ext = (s/total)*360
            self.cv_pie.create_arc(10, 10, 110, 110, start=start, extent=ext, fill=col, outline="white")
            start += ext
            # Легенда
            lbl = ctk.CTkLabel(self.scroll_legend, text=f"■ {l} {perc:.1f}%", text_color=col, font=("Arial", 11, "bold"))
            lbl.pack(anchor="w")
        self.cv_pie.create_oval(40, 40, 80, 80, fill="white", outline="white")

    def load_tree_and_docker(self):
        url = f"{REST_API_URL}/repos/{self.repo['owner']['login']}/{self.repo['name']}/git/trees/{self.repo['default_branch']}?recursive=1"
        try:
            r = get_session(self.token).get(url, headers={"Accept": "application/vnd.github.v3+json"}, timeout=10)
            tree_data = r.json().get("tree", [])
            
            # Зберігаємо ВСІ шляхи в пам'яті
            self.all_file_paths = [i['path'] for i in tree_data]
            self.rendered_count = 0 # Скільки вже показали
            self._tree_nodes = {}
            
            # Docker Check 🐳
            if any(x in self.all_file_paths for x in ["Dockerfile", "docker-compose.yml"]):
                self.lbl_docker.pack(side="left", padx=20)
            
            # Рендеримо першу порцію (50 файлів)
            self.after(0, self.render_next_chunk)
            
            # Зберігаємо контекст для AI (перші 100 файлів + Readme)
            self.ai_context_files = "\n".join(self.all_file_paths[:100])
            readme_url = f"https://raw.githubusercontent.com/{self.repo['full_name']}/{self.repo['default_branch']}/README.md"
            self.ai_context_readme = get_session(self.token).get(readme_url, timeout=10).text[:4000] # Ліміт 4к символів
            
        except Exception as e: print(e)

    def render_tree_chunk(self, file_paths):
        if not hasattr(self, '_tree_nodes') or self._tree_nodes is None:
            self._tree_nodes = {}
        for path in file_paths:
            parts = path.split("/")
            parent_iid = ""
            for i, part in enumerate(parts):
                current_path = "/".join(parts[:i+1])
                if current_path in self._tree_nodes:
                    parent_iid = self._tree_nodes[current_path]
                    continue

                is_folder = (i < len(parts) - 1) or (part in ["src", "lib", "public"])
                icon = "📁" if is_folder else "📄"
                iid = self.tree.insert(parent_iid, "end", text=f" {icon} {part}", open=False)
                self._tree_nodes[current_path] = iid
                parent_iid = iid

    def render_next_chunk(self):
        # Беремо наступні 50
        chunk = self.all_file_paths[self.rendered_count : self.rendered_count + 50]
        if not chunk:
            self.btn_load_more.pack_forget() # Ховаємо кнопку, якщо все завантажили
            return
            
        self.render_tree_chunk(chunk) # Малюємо
        self.rendered_count += 50
        
        # Якщо ще є файли - показуємо кнопку
        if self.rendered_count < len(self.all_file_paths):
            self.btn_load_more.pack(fill="x", padx=15, pady=5)
        else:
            self.btn_load_more.pack_forget()

    def load_more_files_click(self):
        self.render_next_chunk()

    def _update_ai(self, text):
        self.txt_analysis.delete("0.0", "end")
        self.txt_analysis.insert("0.0", text)

    def load_contributors(self):
        users = api_get_contributors(self.token, self.repo['owner']['login'], self.repo['name'])
        count = len(users) # Це тільки топ-10, але покажемо скільки завантажили
        
        self.after(0, lambda: self.btn_contrib.configure(text=f"👥 Contributors ({count}) ▼"))
        
        for i, u in enumerate(users):
            # Перший - це "Owner" (умовно, для цього списку)
            is_king = (i == 0)
            prefix = "👑 " if is_king else "👤 "
            name = u['login']
            commits = u.get('contributions', 0)
            
            # Створення рядка контриб'ютора
            f_row = ctk.CTkFrame(self.f_contrib_list, fg_color="transparent")
            f_row.pack(fill="x", padx=10, pady=2)
            
            ctk.CTkLabel(f_row, text=f"{prefix}{name}", font=("Arial", 12, "bold" if is_king else "normal"), text_color="black").pack(side="left")
            ctk.CTkLabel(f_row, text=f"{commits} commits", text_color="gray", font=("Arial", 11)).pack(side="right")

    def load_activity(self):
        # Дати (беремо з об'єкта repo)
        created = self.repo['created_at'][:10]
        pushed = self.repo['pushed_at'][:10]
        self.after(0, lambda: self.lbl_dates.configure(text=f"� Born: {created}  —  💀 Last Pulse: {pushed}"))
        
        # Sparkline
        stats = api_get_participation(self.token, self.repo['owner']['login'], self.repo['name'])
        if stats:
            self.after(0, lambda: self.draw_sparkline(stats))

    def draw_sparkline(self, data):
        self.cv_spark.delete("all")
        
        # Отримуємо розміри (з запасом на випадок помилки)
        try:
            w = int(self.cv_spark.winfo_width())
            h = int(self.cv_spark.winfo_height())
        except:
            w, h = 400, 60
            
        if w < 10: w = 400 # Fallback якщо вікно ще не відмалювалось
        if h < 10: h = 60

        # Нормалізація даних
        max_val = max(data) if data else 1
        if max_val == 0: max_val = 1
        
        # Якщо даних мало, розтягуємо
        data_len = len(data)
        if data_len < 2: 
            self.cv_spark.create_text(w/2, h/2, text="No Activity Data", fill="gray")
            return

        step = w / (data_len - 1)
        
        # ВІДСТУПИ (Щоб графік не прилипав до країв)
        pad_top = 5
        pad_bottom = 5
        usable_h = h - (pad_top + pad_bottom)

        points = []
        
        # Розрахунок точок лінії
        for i, val in enumerate(data):
            x = i * step
            # Інвертуємо Y (бо 0 зверху), враховуємо відступи
            normalized_h = (val / max_val) * usable_h
            y = h - pad_bottom - normalized_h
            points.extend([x, y])

        if len(points) >= 4:
            # 1. МАЛЮЄМО ЗАЛИВКУ (Area Chart)
            # Додаємо точки для замикання контуру знизу (справа-низ -> зліва-низ)
            poly_points = points.copy()
            poly_points.extend([w, h, 0, h]) 
            
            # Світло-блакитна заливка
            self.cv_spark.create_polygon(poly_points, fill="#E3F2FD", outline="") 

            # 2. МАЛЮЄМО ЛІНІЮ (Зверху)
            # Яскраво-синя лінія, трохи товстіша
            self.cv_spark.create_line(points, fill="#007AFF", width=2, smooth=True)
            
            # 3. ТОЧКА НА КІНЦІ (Остання активність)
            last_x = points[-2]
            last_y = points[-1]
            self.cv_spark.create_oval(last_x-3, last_y-3, last_x+3, last_y+3, fill="#FF3B30", outline="white", width=1)

    def select_and_close(self):
        self.master.select_donor(self.repo, 0)
        self.destroy()

def api_fetch_repos(token, page=1):
    headers = {"Authorization": f"Bearer {token}"}
    try: 
        return get_session(token).get(f"{REST_API_URL}/user/repos", headers=headers, params={"sort": "updated", "page": page, "per_page": 50}, timeout=10).json()
    except: return []

def api_delete_repo(token, owner, repo_name):
    url = f"{REST_API_URL}/repos/{owner}/{repo_name}"
    headers = {"Authorization": f"Bearer {token}"}
    get_session(token).delete(url, headers=headers)

def api_toggle_visibility(token, owner, repo_name, make_private):
    url = f"{REST_API_URL}/repos/{owner}/{repo_name}"
    headers = {"Authorization": f"Bearer {token}"}
    get_session(token).patch(url, headers=headers, json={"private": make_private})

# ===================== MAIN APP =====================

class SmartDatePicker:
    def __init__(self, parent, start_limit, end_limit=None):
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        # 1. Ліміти (Strict Limits)
        self.min_date = start_limit
        self.max_date = end_limit or datetime.date.today()
        
        # 2. UI Компоненти
        self.cb_year = ctk.CTkComboBox(self.frame, width=80, fg_color=COLOR_FIELD_BG, command=self._on_year_change)
        self.cb_month = ctk.CTkComboBox(self.frame, width=60, fg_color=COLOR_FIELD_BG, command=self._on_month_change)
        self.cb_day = ctk.CTkComboBox(self.frame, width=60, fg_color=COLOR_FIELD_BG)
        
        self.cb_year.pack(side="left", padx=(0, 5))
        self.cb_month.pack(side="left", padx=5)
        self.cb_day.pack(side="left", padx=5)
        
        # 3. Ініціалізація (Auto-Fix: Set to Today)
        self._init_years()
        self.set_date(self.max_date) # За замовчуванням - сьогодні

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def _init_years(self):
        # Генеруємо список років від min до max (у зворотному порядку)
        years = range(self.min_date.year, self.max_date.year + 1)
        # sort reverse
        years_list = [str(y) for y in sorted(years, reverse=True)]
        self.cb_year.configure(values=years_list)

    def _on_year_change(self, choice):
        self._update_months()
        self._update_days()

    def _on_month_change(self, choice):
        self._update_days()

    def _update_months(self):
        # Визначаємо доступні місяці для обраного року
        sel_year = int(self.cb_year.get())
        
        start_m = 1
        end_m = 12
        
        # Якщо обрано рік створення - місяці не можуть бути раніше місяця створення
        if sel_year == self.min_date.year:
            start_m = self.min_date.month
            
        # Якщо обрано поточний рік - місяці не можуть бути пізніше поточного
        if sel_year == self.max_date.year:
            end_m = self.max_date.month
            
        months = [str(m) for m in range(start_m, end_m + 1)]
        
        # Зберігаємо поточний вибір, якщо він валідний
        cur_m = self.cb_month.get()
        self.cb_month.configure(values=months)
        if cur_m not in months:
            self.cb_month.set(months[-1]) # Ставимо останній доступний (найсвіжіший)

    def _update_days(self):
        try:
            sel_year = int(self.cb_year.get())
            sel_month = int(self.cb_month.get())
        except: return 

        # Максимальна кількість днів у цьому місяці
        _, max_days_in_month = calendar.monthrange(sel_year, sel_month)
        
        start_d = 1
        end_d = max_days_in_month
        
        # Обмеження знизу (Дата створення)
        if sel_year == self.min_date.year and sel_month == self.min_date.month:
            start_d = self.min_date.day
            
        # Обмеження зверху (Сьогодні)
        if sel_year == self.max_date.year and sel_month == self.max_date.month:
            end_d = self.max_date.day
            
        days = [str(d) for d in range(start_d, end_d + 1)]
        
        cur_d = self.cb_day.get()
        self.cb_day.configure(values=days)
        if cur_d not in days:
            self.cb_day.set(days[-1]) # Ставимо "сьогодні" або останній день

    def get_date(self):
        try:
            return datetime.date(
                int(self.cb_year.get()),
                int(self.cb_month.get()),
                int(self.cb_day.get())
            )
        except:
            return self.max_date

    def set_date(self, date_obj):
        # Спочатку оновлюємо списки, щоб дата влізла
        if date_obj < self.min_date: date_obj = self.min_date
        if date_obj > self.max_date: date_obj = self.max_date
        
        self.cb_year.set(str(date_obj.year))
        self._update_months()
        
        self.cb_month.set(str(date_obj.month))
        self._update_days()
        
        self.cb_day.set(str(date_obj.day))

class TimeArchitect:
    def __init__(self):
        self.personas = {
            "Freelancer": {"days": [0,1,2,3,4,5], "hours": (10, 23)}, # Пн-Сб, 10:00-23:00
            "Office":     {"days": [0,1,2,3,4],   "hours": (9, 18)},  # Пн-Пт, 09:00-18:00
            "Night Owl":  {"days": [0,1,2,3,4,6], "hours": (19, 4)},  # Вечір + Неділя
            "Bot 24/7":   {"days": [0,1,2,3,4,5,6], "hours": (0, 23)} # Без лімітів
        }

    def estimate_effort_days(self, repo_size_kb, commit_count):
        """Оцінка часу (як і раніше)"""
        days_by_commits = commit_count / 4
        days_by_size = repo_size_kb / 15
        base_days = (days_by_commits * 0.7) + (days_by_size * 0.3)
        return max(3, min(int(base_days), 365 * 2))

    def analyze_density(self, commit_count, user_days):
        """Аналіз щільності (як і раніше)"""
        if user_days <= 0: return 'impossible'
        commits_per_day = commit_count / user_days
        if commits_per_day > 10: return 'impossible' # Занадто швидко
        if commits_per_day > 1.5: return 'dense'     # Густо (розбивати не обов'язково)
        if commits_per_day >= 0.3: return 'ok'
        return 'sparse'

    def get_commit_time(self, target_date, persona_name="Freelancer"):
        """Генерує час з урахуванням Персони та таймзони України"""
        rule = self.personas.get(persona_name, self.personas["Freelancer"])

        if isinstance(target_date, datetime.date) and not isinstance(target_date, datetime.datetime):
            target_date = datetime.datetime.combine(target_date, datetime.time())
        
        weekday = target_date.weekday()
        if weekday not in rule["days"]:
            pass

        start_h, end_h = rule["hours"]
        if start_h < end_h:
            h = random.randint(start_h, end_h)
        else:
            if random.random() > 0.5: h = random.randint(start_h, 23)
            else: h = random.randint(0, end_h)
        
        m = random.randint(0, 59)
        s = random.randint(0, 59)

        is_summer = 3 < target_date.month < 10
        tz_offset = "+0300" if is_summer else "+0200"

        return f"{target_date.strftime('%Y-%m-%d')} {h:02d}:{m:02d}:{s:02d} {tz_offset}"

class CleanApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GITHUB GOD MODE")
        self.geometry("1250x950")
        self.configure(fg_color=COLOR_BG)

        self.key_status_labels = {}  # <--- ДОДАЙ ЦЕЙ РЯДОК (Сюди будемо записувати лейбли)
        
        if AUDIO_AVAILABLE: pygame.mixer.init()
        
        self.username = None
        self.token = None
        self.created_date = datetime.date(2020, 1, 1)
        self.auth_data = {}
        
        self.repos_list = []
        self.selected_repos = set()
        self.manager_selection_mode = False
        self.manager_page = 1
        
        self.stats_data_cache = []
        self.manual_grid_data = {}
        self.selected_intensity = 4
        self.repo_activity_cache = {}
        self.repo_activity_pending = set()
        
        self.found_projects = []
        self.selected_donor = None
        self.selected_senior_days = 0 

        self.team_roster = []
        self.known_extensions = {
            "Python": [".py", "requirements.txt", "Pipfile", ".ipynb"],
            "JavaScript/TS": [".js", ".jsx", ".ts", ".tsx", "package.json", ".vue", ".svelte", ".sol"],
            "Styles": [".css", ".scss", ".sass", ".less", ".styl"],
            "HTML": [".html", ".htm", ".j2"],
            "Backend (Go/Java/C)": [".go", ".java", ".c", ".cpp", ".h", ".cs", ".php", ".rb"],
            "Mobile": [".dart", ".swift", ".kt", ".xml", ".gradle", ".plist", ".m"],
            "Config/Orphans": [".gitignore", "README.md", "LICENSE", ".env.example", "Dockerfile", ".yml", ".yaml", ".json"]
        }

        self.role_definitions = {
            "Frontend": {
                "exts": [".js", ".jsx", ".ts", ".tsx", ".css", ".scss", ".html", ".vue"],
                "folders": ["client", "frontend", "ui", "public", "assets", "views", "components"]
            },
            "Backend": {
                "exts": [".py", ".go", ".java", ".php", ".rb", ".cs", ".c", ".cpp", ".sql", ".sol"],
                "folders": ["server", "backend", "api", "controllers", "models", "services", "pkg", "internal"]
            },
            "Mobile": {
                "exts": [".dart", ".swift", ".kt", ".xml", ".gradle", ".plist"],
                "folders": ["android", "ios", "lib", "app", "mobile"]
            }
        }

        self.language_mapping = {
            "Python": "Python",
            "Jupyter Notebook": "Python",
            "JavaScript": "JavaScript/TS",
            "TypeScript": "JavaScript/TS",
            "Vue": "JavaScript/TS",
            "React": "JavaScript/TS",
            "Svelte": "JavaScript/TS",
            "CSS": "Styles",
            "SCSS": "Styles",
            "Less": "Styles",
            "HTML": "HTML",
            "Go": "Backend (Go/Java/C)",
            "Java": "Backend (Go/Java/C)",
            "C++": "Backend (Go/Java/C)",
            "C#": "Backend (Go/Java/C)",
            "Ruby": "Backend (Go/Java/C)",
            "PHP": "Backend (Go/Java/C)",
            "Solidity": "JavaScript/TS",
            "Shell": "Config/Orphans",
            "Dockerfile": "Config/Orphans"
        }
        
        self.cloner_page = 1
        self.cloner_max_pages = 1

        if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
        self.show_login_ui()
        self.after(100, self.load_auth_data)
        self.load_favorites()

    def load_favorites(self):
        self.fav_file = os.path.join(DATA_DIR, "favorites.json")
        self.favorites = []
        if os.path.exists(self.fav_file):
            try: self.favorites = json.load(open(self.fav_file))
            except: pass

    def save_favorites(self):
        try: json.dump(self.favorites, open(self.fav_file, "w"))
        except: pass

    def toggle_favorite(self, item):
        fid = item['full_name']
        exists = next((x for x in self.favorites if x['full_name'] == fid), None)
        
        if exists:
            self.favorites.remove(exists)
            self.log(f"💔 Removed from favorites: {fid}")
        else:
            self.favorites.append(item)
            self.log(f"❤️ Added to favorites: {fid}")
        
        self.save_favorites()
        
        if hasattr(self, 'chk_fav_only') and self.chk_fav_only.get():
            self.render_cloner_results(self.favorites)
        else:
            if hasattr(self, 'search_cache') and self.cloner_page in self.search_cache:
                self.render_cloner_results(self.search_cache[self.cloner_page])

    def toggle_fav_filter(self):
        if self.chk_fav_only.get():
            self.lbl_loading.configure(text="❤️ Favorites Only", text_color="red")
            self.render_cloner_results(self.favorites)
        else:
            self.lbl_loading.configure(text="🌍 All Results", text_color="black")
            if hasattr(self, 'search_cache') and self.cloner_page in self.search_cache:
                self.render_cloner_results(self.search_cache[self.cloner_page])
            else:
                self.render_cloner_results([])

    def get_valid_years(self):
        end_year = datetime.date.today().year
        start_year = self.created_date.year if self.created_date else 2020
        return [str(y) for y in range(start_year, end_year + 1)][::-1]

    def get_thief_years(self):
        end_year = datetime.date.today().year
        start_year = 2008  # GitHub era start; do not limit by current account creation date
        return [str(y) for y in range(start_year, end_year + 1)][::-1]

    def _get_repo_about(self, repo_item=None):
        src = repo_item if isinstance(repo_item, dict) else getattr(self, "selected_donor", None)
        if not isinstance(src, dict):
            return ""
        return str(src.get("description") or src.get("about") or "").strip()

    def _resolve_repo_desc(self, raw_desc="", repo_item=None):
        desc = str(raw_desc or "").strip()
        if desc:
            return desc
        return self._get_repo_about(repo_item)

    def _copy_about_to_all_desc_fields(self, repo_item=None, force=False):
        about = self._get_repo_about(repo_item)
        if not about:
            return

        for attr in ("cloner_target_desc", "entry_team_desc", "entry_thief_desc", "gen_desc"):
            entry = getattr(self, attr, None)
            if not entry:
                continue
            try:
                current = str(entry.get() or "").strip()
            except Exception:
                continue
            if force or not current:
                try:
                    entry.delete(0, "end")
                    entry.insert(0, about)
                except Exception:
                    pass
    

    def log(self, msg):
        t = datetime.datetime.now().strftime("%H:%M:%S")
        self.after(0, lambda: self._write_log(f"[{t}] {msg}\n"))
    
    def _write_log(self, msg):
        self.console.configure(state="normal")

        tag = None
        lower_msg = str(msg).lower()
        
        if "error" in lower_msg or "fail" in lower_msg or "critical" in lower_msg or "❌" in lower_msg:
            tag = "error"
        elif "success" in lower_msg or "complete" in lower_msg or "✅" in lower_msg:
            tag = "success"
        elif "warning" in lower_msg or "⚠️" in lower_msg:
            tag = "warning"

        if tag:
            self.console.insert("end", msg, tag)
        else:
            self.console.insert("end", msg)

        self.console.see("end")
        self.console.configure(state="disabled")

    def _update_cloner_ui(self, progress, text):
        if hasattr(self, 'cloner_progress'):
            try:
                p = float(progress)
            except:
                p = 0.0
            p = max(0.0, min(1.0, p))
            self.cloner_progress.set(p)
        if hasattr(self, 'lbl_cloner_status'):
            self.lbl_cloner_status.configure(text=text)

    def _format_eta(self, seconds):
        if seconds is None:
            return "calculating..."
        try:
            seconds = int(max(0, round(seconds)))
        except:
            return "calculating..."
        if seconds < 60:
            return f"{seconds}s"
        mins, sec = divmod(seconds, 60)
        if mins < 60:
            return f"{mins}m {sec}s"
        hrs, mins = divmod(mins, 60)
        return f"{hrs}h {mins}m"

    def create_clean_entry(self, parent, placeholder, width=250, show=None):
        return ctk.CTkEntry(
            parent, width=width, height=40, placeholder_text=placeholder, 
            fg_color=COLOR_FIELD_BG, border_width=1, border_color=COLOR_BORDER, 
            text_color=COLOR_TEXT_MAIN, corner_radius=8, show=show
        )

    def create_date_picker(self, parent):
        # Створюємо розумний пікер, передаючи дату створення акаунта як мінімум
        # self.created_date оновлюється при логіні
        start_limit = self.created_date if self.created_date else datetime.date(2020, 1, 1)
        picker = SmartDatePicker(parent, start_limit=start_limit)
        return picker

    def get_date_val(self, picker_instance):
        # Тепер ми просто викликаємо метод класу
        if isinstance(picker_instance, SmartDatePicker):
            return picker_instance.get_date()
        return None # Fallback
    
    def set_date_val(self, picker_instance, date_obj):
        if isinstance(picker_instance, SmartDatePicker):
            picker_instance.set_date(date_obj)

    def _get_seed_date(self, first_commit_date):
        """Return a date one day before the first real commit date."""
        if isinstance(first_commit_date, datetime.datetime):
            first_commit_date = first_commit_date.date()
        if not isinstance(first_commit_date, datetime.date):
            first_commit_date = datetime.date.today()
        return first_commit_date - datetime.timedelta(days=1)

    def generate_human_time(self, date_obj):
        while True:
            h = random.randint(0, 23)
            # Імітуємо сон (мало активності вночі)
            if 4 <= h < 8: 
                continue
            
            # Більше активності вдень/ввечері
            if random.random() > 0.7: 
                h = random.choice([20, 21, 22, 23, 0, 1, 2])
            else: 
                h = random.choice([9, 10, 11, 12, 13, 14, 15, 16, 17, 18])
            
            # ВАЖЛИВО: Формат має бути "YYYY-MM-DD HH:MM:SS" (без T)
            # Git найкраще розуміє саме такий формат у змінних середовища
            return f"{date_obj} {h:02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"

    def update_year_combos(self):
        valid = self.get_valid_years()
        thief_years = self.get_thief_years()
        try:
            if hasattr(self, 'man_year'):
                self.man_year.configure(values=valid)
                self.man_year.set(valid[0])
                self.init_manual_grid(valid[0])
            if hasattr(self, 'stats_combo'):
                self.stats_combo.configure(values=valid)
                self.stats_combo.set(valid[0])
            if hasattr(self, 'combo_source_year'):
                self.combo_source_year.configure(values=thief_years)
                if thief_years:
                    self.combo_source_year.set(thief_years[0])
            if hasattr(self, 'combo_target_year'):
                self.combo_target_year.configure(values=thief_years)
                if thief_years:
                    self.combo_target_year.set(thief_years[0])
        except: pass

    # --- AUTH ---
    def load_auth_data(self):
        if os.path.exists(AUTH_FILE):
            try:
                with open(AUTH_FILE, "r") as f:
                    data = json.load(f)
                    if "users" not in data:
                        reserved = {
                            "emails",
                            "default_email",
                            "ai_keys",
                            "ai_keys_list",
                            "proxies_list",
                            "proxy_list",
                            "default_path",
                            "sound_enabled",
                            "git_author",
                        }
                        self.auth_data = {k: v for k, v in data.items() if k not in reserved and isinstance(v, str)}
                    else:
                        self.auth_data = data["users"]
                        if "ai_keys" in data and hasattr(self, "entry_ai"):
                            self.entry_ai.insert(0, data["ai_keys"])
                    
                    if self.auth_data:
                        users = list(self.auth_data.keys())
                        self.combo_user.configure(values=users)
                        self.combo_user.set(users[-1])
                        self.on_user_select(users[-1])
            except: pass

    def on_user_select(self, choice):
        if choice in self.auth_data: 
            self.entry_token.delete(0, "end")
            self.entry_token.insert(0, self.auth_data[choice])

    def show_login_ui(self):
        self.login_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.login_frame.pack(fill="both", expand=True, pady=80)
        
        ctk.CTkLabel(self.login_frame, text="GitHub Master Suite", font=("Helvetica", 32, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=(20,5))
        
        self.combo_user = ctk.CTkComboBox(self.login_frame, width=300, height=45, command=self.on_user_select)
        self.combo_user.pack(pady=10)
        
        # FRAME FOR PASSWORD + EYE
        f_pass = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        f_pass.pack(pady=10)
        
        self.entry_token = ctk.CTkEntry(f_pass, placeholder_text="GitHub Token (ghp_...)", width=260, height=45, show="*")
        self.entry_token.pack(side="left")
        
        # Кнопка Око
        self.btn_show_pass = ctk.CTkButton(
            f_pass, text="👁", width=35, height=45, fg_color="#DDD", text_color="black",
            command=self.toggle_login_pass
        )
        self.btn_show_pass.pack(side="left", padx=(5,0))

        # (Поле AI Keys видалено звідси)
        
        ctk.CTkButton(self.login_frame, text="Login", width=300, height=45, fg_color=COLOR_ACCENT, command=self.login).pack(pady=20)

    def toggle_login_pass(self):
        if self.entry_token.cget("show") == "*":
            self.entry_token.configure(show="")
        else:
            self.entry_token.configure(show="*")

    def login(self):
        u, t = self.combo_user.get(), self.entry_token.get()
        ai_k = ""
        threading.Thread(target=self._login_thread, args=(u, t, ai_k), daemon=True).start()

    def _login_thread(self, u, t, ai_k): # ai_k тепер ігнорується тут, але для сумісності лишимо
        try:
            r = get_session(t).get(f"{REST_API_URL}/user", headers={"Authorization": f"Bearer {t}"}, timeout=10)
            if r.status_code == 200:
                self.username, self.token = r.json()["login"], t
                self.created_date = fetch_user_info(self.username, t)
                
                # --- Ініціалізація AI Manager ---
                # Завантажуємо збережені ключі зі списку
                global ai_manager
                try:
                    auth_data = json.load(open(AUTH_FILE, "r")) if os.path.exists(AUTH_FILE) else {}
                except:
                    auth_data = {}
                keys_data = auth_data.get("ai_keys_list", [])
                
                # Міграція старого формату (якщо був рядок)
                old_keys_str = auth_data.get("ai_keys", "")
                if old_keys_str and not keys_data:
                    for k in old_keys_str.split(','):
                        if k.strip():
                            keys_data.append({"key": k.strip(), "status": "unknown"})
                
                ai_manager = AIKeyManager(keys_data)

                # --- Ініціалізація Proxy Manager ---
                global proxy_manager
                proxy_data = auth_data.get("proxies_list", auth_data.get("proxy_list", []))
                try:
                    proxy_manager = ProxyManager(proxy_data if isinstance(proxy_data, list) else [])
                except:
                    proxy_manager = ProxyManager()
                
                # Зберігаємо токен
                if "users" not in auth_data:
                    auth_data = {"users": auth_data}
                if "users" not in auth_data or not isinstance(auth_data.get("users"), dict):
                    auth_data["users"] = {}
                auth_data["users"][self.username] = t
                with open(AUTH_FILE, "w") as f:
                    json.dump(auth_data, f)
                self.auth_data = auth_data["users"]
                
                self.after(0, self.switch_to_main)
            else: 
                self.after(0, lambda: messagebox.showerror("Error", "Invalid Token"))
        except Exception as e: 
            self.after(0, lambda: messagebox.showerror("Error", str(e)))

    def switch_to_main(self):
        self.login_frame.destroy()
        self.build_ui()
        self.update_year_combos()

        self.log(f"📅 Date limits set: {self.created_date} to Today")

    def build_ui(self):
        if hasattr(self, 'tabview'):
            try:
                if self.tabview.winfo_exists():
                    self.tabview.destroy()
            except: pass
        if hasattr(self, 'console'):
            try:
                if self.console.winfo_exists():
                    self.console.destroy()
            except: pass
        self.tabview = ctk.CTkTabview(self, segmented_button_selected_color=COLOR_ACCENT)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        self.tab_gen = self.tabview.add("Generator")
        self.tab_cloner = self.tabview.add("Project Cloner")
        self.tab_collab = self.tabview.add("Team Mode 👥")
        self.tab_manual = self.tabview.add("Manual Art 🎨")
        self.tab_thief = self.tabview.add("Graph Thief 🥷")
        self.tab_manager = self.tabview.add("Repo Manager")
        self.tab_stats = self.tabview.add("Statistics")
        self.tab_settings = self.tabview.add("Settings")
        
        self.build_generator_tab()
        self.build_cloner_tab()
        self.build_collab_tab()
        self.build_manual_tab()
        self.build_thief_tab()
        self.build_manager_tab()
        self.build_stats_tab()
        self.build_settings_tab()
        
        self.console = ctk.CTkTextbox(self, height=100, fg_color=COLOR_FIELD_BG)
        self.console.pack(fill="x", padx=20, pady=(0,20))

        self.console.tag_config("error", foreground="#FF3B30")
        self.console.tag_config("success", foreground="#34C759")
        self.console.tag_config("warning", foreground="#FF9500")

        self.console.insert("0.0", "System Initialized.\n")
        self.console.configure(state="disabled")

    def build_settings_tab(self):
        t = self.tab_settings
        self.scroll_settings = ctk.CTkScrollableFrame(t, fg_color="transparent")
        self.scroll_settings.pack(fill="both", expand=True, padx=10, pady=10)

        settings_data = self._read_auth_file()

        # --- SECTION 1: GENERAL & IDENTITY ---
        self._build_section_header("👤 Identity & Preferences", "Who are you in the Git history?")
        
        f_gen = ctk.CTkFrame(self.scroll_settings, fg_color="white", corner_radius=10)
        f_gen.pack(fill="x", padx=10, pady=5)
        
        # Git Author Name
        ctk.CTkLabel(f_gen, text="Git Author Name (Alias):", font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        self.entry_git_author = ctk.CTkEntry(f_gen, placeholder_text=f"Default: {self.username}")
        self.entry_git_author.pack(fill="x", padx=15, pady=(5, 5))
        if "git_author" in settings_data and settings_data["git_author"]:
            self.entry_git_author.insert(0, settings_data["git_author"])

        # 2. Git Email (НОВЕ ПОЛЕ)
        ctk.CTkLabel(f_gen, text="Git Email (for commits):", font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(5, 0))
        self.entry_def_email = ctk.CTkEntry(f_gen, placeholder_text="your@email.com")
        self.entry_def_email.pack(fill="x", padx=15, pady=(5, 10))
        if "default_email" in settings_data and settings_data["default_email"]:
            self.entry_def_email.insert(0, settings_data["default_email"])
        
        # Default Path
        ctk.CTkLabel(f_gen, text="Default Clone Path:", font=("Arial", 12, "bold")).pack(anchor="w", padx=15)
        f_path = ctk.CTkFrame(f_gen, fg_color="transparent")
        f_path.pack(fill="x", padx=10, pady=5)
        self.entry_def_path = ctk.CTkEntry(f_path, placeholder_text="Select folder...")
        self.entry_def_path.pack(side="left", fill="x", expand=True)
        if "default_path" in settings_data and settings_data["default_path"]:
            self.entry_def_path.insert(0, settings_data["default_path"])
        ctk.CTkButton(f_path, text="📂", width=40, fg_color="gray", command=self.browse_default_path).pack(side="right", padx=5)

        # Theme & Sound
        f_toggles = ctk.CTkFrame(f_gen, fg_color="transparent")
        f_toggles.pack(fill="x", padx=10, pady=10)
        self.switch_sound = ctk.CTkSwitch(f_toggles, text="🔊 Sound", onvalue=True, offvalue=False, command=self.save_settings)
        if settings_data.get("sound_enabled", True):
            self.switch_sound.select()
        self.switch_sound.pack(side="left", padx=20)
        self.switch_theme = ctk.CTkSwitch(f_toggles, text="🌙 Dark Mode", command=self.toggle_theme)
        self.switch_theme.pack(side="left", padx=20)
        
        # Save Button specifically for general settings
        ctk.CTkButton(f_gen, text="💾 Save Identity Settings", fg_color="black", command=self.save_settings).pack(fill="x", padx=15, pady=15)

        # --- SECTION 2: PROXY MANAGER ---
        self._build_section_header("🌐 Proxy Network", "Mask your traffic (HTTP/HTTPS).")
        
        f_proxy = ctk.CTkFrame(self.scroll_settings, fg_color="white", corner_radius=10)
        f_proxy.pack(fill="x", padx=10, pady=5)
        
        # Add Input
        f_add_p = ctk.CTkFrame(f_proxy, fg_color="transparent")
        f_add_p.pack(fill="x", padx=10, pady=10)
        self.entry_proxy = ctk.CTkEntry(f_add_p, placeholder_text="http://user:pass@ip:port", width=300)
        self.entry_proxy.pack(side="left", fill="x", expand=True, padx=(0,10))
        ctk.CTkButton(f_add_p, text="+ Add Proxy", width=100, command=self.add_proxy).pack(side="right")

        # Proxy List
        self.f_proxy_list = ctk.CTkScrollableFrame(f_proxy, fg_color="#F9F9F9", height=150, label_text="Your Proxies")
        self.f_proxy_list.pack(fill="x", padx=10, pady=(0,10))

        # --- SECTION 3: AI KEYS ---
        self._build_section_header("🤖 AI API Keys", "Gemini Keys Rotation.")
        f_keys = ctk.CTkFrame(self.scroll_settings, fg_color="white", corner_radius=10)
        f_keys.pack(fill="x", padx=10, pady=5)
        f_add_k = ctk.CTkFrame(f_keys, fg_color="transparent")
        f_add_k.pack(fill="x", padx=10, pady=10)
        self.entry_new_key = ctk.CTkEntry(f_add_k, placeholder_text="AIza...", width=300)
        self.entry_new_key.pack(side="left", fill="x", expand=True, padx=(0,10))
        ctk.CTkButton(f_add_k, text="+ Add Key", width=100, command=self.add_api_key).pack(side="right")
        self.f_keys_list = ctk.CTkScrollableFrame(f_keys, fg_color="#F9F9F9", height=150)
        self.f_keys_list.pack(fill="x", padx=10, pady=(0,10))

        # Render Lists
        self.render_keys_list()
        self._load_proxies_from_file()
        self.render_proxy_list()

        # ЗАПУСК ТАЙМЕРА
        self._update_key_timers()

    def _load_proxies_from_file(self):
        global proxy_manager
        data = self._read_auth_file()
        plist = data.get("proxies_list", data.get("proxy_list", []))
        if isinstance(plist, list):
            try:
                proxy_manager = ProxyManager(plist)
            except:
                pass

    # --- PROXY LOGIC ---
    def add_proxy(self):
        url = self.entry_proxy.get().strip()
        if not url: return
        # Базова валідація
        if not url.startswith("http"): url = "http://" + url
        
        proxy_manager.add_proxy(url)
        self.entry_proxy.delete(0, "end")
        self.save_settings() # Зберігаємо в auth.json
        self.render_proxy_list()

    def delete_proxy(self, url):
        if messagebox.askyesno("Confirm Delete", f"Delete proxy {url}?"):
            proxy_manager.remove_proxy(url)
            self.save_settings()
            self.render_proxy_list()

    def check_proxy(self, url, lbl_stat, lbl_loc):
        lbl_stat.configure(text="⏳ Ping...", text_color="orange")
        lbl_loc.configure(text="Checking...")
        threading.Thread(target=self._check_proxy_thread, args=(url, lbl_stat, lbl_loc), daemon=True).start()

    def _check_proxy_thread(self, url, lbl_stat, lbl_loc):
        proxies = {"http": url, "https": url}
        try:
            # Запит до API для отримання інфо про IP
            r = get_session().get("http://ip-api.com/json", proxies=proxies, timeout=5)
            if r.status_code == 200:
                data = r.json()
                if data.get("status") == "fail":
                    self.after(0, lambda: lbl_stat.configure(text="❌ Failed", text_color="red"))
                    self.after(0, lambda: lbl_loc.configure(text="Invalid IP"))
                else:
                    country = data.get("country", "Unknown")
                    city = data.get("city", "Unknown")
                    ip = data.get("query", "Unknown")
                    
                    self.after(0, lambda: lbl_stat.configure(text="✅ Working", text_color=COLOR_SUCCESS))
                    self.after(0, lambda: lbl_loc.configure(text=f"🌍 {country}, {city}\n🆔 {ip}"))
                    
                    # Оновлюємо статус в менеджері
                    for p in proxy_manager.proxies:
                        if p['url'] == url:
                            p['status'] = 'ok'
                            p['location'] = f"{country}, {city}"
            else:
                raise Exception("HTTP Error")
        except Exception as e:
            err = str(e)[:20]
            self.after(0, lambda: lbl_stat.configure(text="❌ Dead", text_color="red"))
            self.after(0, lambda err=err: lbl_loc.configure(text=f"Error: {err}"))
            for p in proxy_manager.proxies:
                if p['url'] == url: p['status'] = 'dead'
        
        self.save_settings()

    def render_proxy_list(self):
        for w in self.f_proxy_list.winfo_children(): w.destroy()
        
        for p in proxy_manager.get_all():
            url = p['url']
            loc = p.get('location', 'Unknown')
            
            f_row = ctk.CTkFrame(self.f_proxy_list, fg_color="white")
            f_row.pack(fill="x", pady=2)
            
            # Icon
            ctk.CTkLabel(f_row, text="🌐", font=("Arial", 16)).pack(side="left", padx=5)
            
            # Info (URL + Loc)
            f_info = ctk.CTkFrame(f_row, fg_color="transparent")
            f_info.pack(side="left", padx=5)
            # Приховуємо пароль, якщо він є
            display_url = url
            if "@" in url:
                parts = url.split("@")
                display_url = "User:Pass@" + parts[1]
                
            ctk.CTkLabel(f_info, text=display_url, font=("Consolas", 11, "bold")).pack(anchor="w")
            lbl_loc = ctk.CTkLabel(f_info, text=loc, font=("Arial", 10), text_color="gray")
            lbl_loc.pack(anchor="w")
            
            # Status
            lbl_stat = ctk.CTkLabel(f_row, text=p['status'].upper(), width=60, font=("Arial", 10, "bold"))
            lbl_stat.pack(side="left", padx=5)
            
            # Buttons
            ctk.CTkButton(
                f_row, text="Test", width=50, height=24,
                command=lambda u=url, l=lbl_stat, loc=lbl_loc: self.check_proxy(u, l, loc)
            ).pack(side="right", padx=5)
            ctk.CTkButton(
                f_row, text="🗑", width=30, height=24, fg_color=COLOR_DELETE,
                command=lambda u=url: self.delete_proxy(u)
            ).pack(side="right", padx=2)

    def _build_section_header(self, title, subtitle):
        f = ctk.CTkFrame(self.scroll_settings, fg_color="transparent")
        f.pack(fill="x", padx=10, pady=(20, 5))
        ctk.CTkLabel(f, text=title, font=("Arial", 16, "bold")).pack(anchor="w")
        ctk.CTkLabel(f, text=subtitle, text_color="gray").pack(anchor="w")

    def add_api_key(self):
        key = self.entry_new_key.get().strip()
        if not key: return
        ai_manager.add_key(key)
        self.entry_new_key.delete(0, "end")
        self.save_keys_to_file()
        self.render_keys_list()

    def delete_api_key(self, key_val):
        # Показуємо останні 4 символи ключа для ідентифікації
        masked_key = f"...{key_val[-4:]}" if len(key_val) > 4 else key_val
        
        # Викликаємо діалогове вікно (Yes/No)
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete the API Key ending in {masked_key}?"
        )
        
        if confirm:
            ai_manager.remove_key(key_val)
            self.save_keys_to_file()
            self.render_keys_list()

    def check_api_key(self, key_val, lbl_status):
        lbl_status.configure(text="⏳ Testing...", text_color="orange")
        threading.Thread(target=self._check_key_thread, args=(key_val, lbl_status), daemon=True).start()

    def _check_key_thread(self, key, lbl):
        # 1. Ініціалізація клієнта
        try:
            client = genai.Client(api_key=key)
        except Exception:
            self.after(0, lambda: lbl.configure(text="Client Error", text_color="red"))
            return

        working_model = None
        last_error = None

        # 2. Перебір тільки ЕКОНОМНИХ моделей
        for model_name in AI_MODEL_FALLBACKS:
            try:
                client.models.generate_content(
                    model=model_name,
                    contents="Hi"
                )
                working_model = model_name
                break
            except Exception as e:
                err_msg = str(e)
                if "404" in err_msg or "NOT_FOUND" in err_msg or "not found" in err_msg:
                    last_error = f"404 on {model_name}"
                    continue
                elif "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg.upper() or "RATE_LIMIT" in err_msg.upper():
                    last_error = "LIMIT"
                    break
                elif "503" in err_msg or "UNAVAILABLE" in err_msg.upper() or "SERVICE UNAVAILABLE" in err_msg.upper():
                    last_error = "TEMP"
                    continue
                else:
                    last_error = err_msg
                    continue

        # 3. Результат
        if working_model:
            short_name = working_model.replace("models/", "").replace("gemini-", "")
            self.after(0, lambda n=short_name: lbl.configure(text=f"Active ({n})", text_color=COLOR_SUCCESS))

            global AI_MODEL_NAME
            AI_MODEL_NAME = working_model

            for k in ai_manager.keys:
                if k['key'] == key:
                    k['status'] = 'ok'
                    k.pop('cooldown_until', None)
                    k.pop('prev_status', None)

        elif last_error == "LIMIT":
            now = datetime.datetime.now()
            cooldown_time = now + datetime.timedelta(seconds=45)
            time_str = cooldown_time.strftime("%H:%M:%S")
            self.after(0, lambda t=time_str: lbl.configure(text=f"Limit ({t})", text_color="orange"))

            for k in ai_manager.keys:
                if k['key'] == key:
                    k['status'] = 'limit'
                    k['cooldown_until'] = time_str
                    k.pop('prev_status', None)

        elif last_error == "TEMP":
            now = datetime.datetime.now()
            cooldown_time = now + datetime.timedelta(seconds=20)
            time_str = cooldown_time.strftime("%H:%M:%S")
            self.after(0, lambda t=time_str: lbl.configure(text=f"Busy ({t})", text_color="#1E88E5"))

            for k in ai_manager.keys:
                if k['key'] == key:
                    prev_status = k.get('status', 'unknown')
                    if prev_status not in ('dead', 'limit'):
                        k['prev_status'] = prev_status
                    k['status'] = 'temp'
                    k['cooldown_until'] = time_str

        else:
            print(f"⚠️ ALL MODELS FAILED. Last error: {last_error}")
            self.after(0, lambda: lbl.configure(text="Dead / 404", text_color="red"))
            for k in ai_manager.keys:
                if k['key'] == key:
                    k['status'] = 'dead'
                    k.pop('cooldown_until', None)
                    k.pop('prev_status', None)

        self.save_settings()

    def render_keys_list(self):
        for w in self.f_keys_list.winfo_children(): w.destroy()
        self.key_status_labels = {} 
        
        for k_obj in ai_manager.get_all_keys():
            k_val = k_obj['key']
            status = k_obj.get('status', 'unknown')
            
            f_row = ctk.CTkFrame(self.f_keys_list, fg_color="white", height=35)
            f_row.pack(fill="x", pady=2)
            
            # Кольоровий індикатор (смужка зліва)
            bar_color = "#CCC"
            stat_text = status.title() # "Ok" -> "Ok"
            
            if status == "ok": 
                bar_color = COLOR_SUCCESS
                stat_text = "Active"
            elif status == "dead": 
                bar_color = "red"
                stat_text = "Dead"
            elif status == "limit": 
                bar_color = "orange"
                stat_text = "Limit"
            elif status == "temp":
                bar_color = "#1E88E5"
                stat_text = "Busy (API)"
            
            # Тонка смужка статусу
            ctk.CTkFrame(f_row, width=4, height=35, fg_color=bar_color).pack(side="left")
            
            # Прихований ключ
            masked = k_val[:4] + "••••••••" + k_val[-4:]
            lbl_key = ctk.CTkLabel(f_row, text=masked, font=("Consolas", 12), width=150, anchor="w")
            lbl_key.pack(side="left", padx=10)
            
            # Кнопка Око (маленька і акуратна)
            btn_show = ctk.CTkButton(f_row, text="👁", width=25, height=25, fg_color="#F0F0F0", text_color="black", hover_color="#E0E0E0",
                                     command=lambda l=lbl_key, v=k_val: self.toggle_key_vis(l, v))
            btn_show.pack(side="left", padx=5)
            
            # СТАТУС (Лейбл)
            lbl_stat = ctk.CTkLabel(f_row, text=stat_text, text_color=bar_color, width=180, font=("Arial", 11, "bold"), anchor="w")
            lbl_stat.pack(side="left", padx=10)
            self.key_status_labels[k_val] = lbl_stat
            
            # Кнопки дій (справа)
            ctk.CTkButton(f_row, text="🗑", width=30, height=25, fg_color=COLOR_DELETE, hover_color="#D00000",
                          command=lambda k=k_val: self.delete_api_key(k)).pack(side="right", padx=5)
                          
            ctk.CTkButton(f_row, text="Test", width=50, height=25, fg_color="#007AFF",
                          command=lambda k=k_val, l=lbl_stat: self.check_api_key(k, l)).pack(side="right", padx=2)

    def _update_key_timers(self):
        now = datetime.datetime.now()
        if ai_manager:
            for k_obj in ai_manager.get_all_keys():
                key = k_obj['key']
                status = k_obj.get('status', '')
                cooldown_str = k_obj.get('cooldown_until', '')
                
                if status in ('limit', 'temp') and cooldown_str and key in self.key_status_labels:
                    try:
                        target_time = datetime.datetime.strptime(cooldown_str, "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day)
                        diff = (target_time - now).total_seconds()
                        lbl = self.key_status_labels[key]
                        
                        if diff > 0:
                            if status == 'limit':
                                lbl.configure(text=f"Wait {int(diff)}s", text_color="orange")
                            else:
                                lbl.configure(text=f"Busy {int(diff)}s", text_color="#1E88E5")
                        else:
                            if status == 'temp':
                                restore_status = k_obj.get('prev_status', 'ok')
                                if restore_status in ('temp', 'limit', 'dead', 'unknown'):
                                    restore_status = 'ok'
                                k_obj['status'] = restore_status
                            else:
                                k_obj['status'] = 'ok'
                            k_obj.pop('cooldown_until', None)
                            k_obj.pop('prev_status', None)
                            if k_obj['status'] == 'dead':
                                lbl.configure(text="Dead", text_color="red")
                            elif k_obj['status'] == 'limit':
                                lbl.configure(text="Limit", text_color="orange")
                            else:
                                lbl.configure(text="Active", text_color=COLOR_SUCCESS)
                            self.save_settings()
                    except: pass
        self.after(1000, self._update_key_timers)

    def toggle_key_vis(self, lbl, full_key):
        current = lbl.cget("text")
        if "*" in current or "•" in current:
            lbl.configure(text=full_key)
        else:
            lbl.configure(text=full_key[:4] + "••••••••" + full_key[-4:])

    def _read_auth_file(self):
        if os.path.exists(AUTH_FILE):
            try:
                with open(AUTH_FILE, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _write_auth_file(self, data):
        with open(AUTH_FILE, "w") as f:
            json.dump(data, f)

    def _save_email_to_disk(self, username, email):
        """Зберігає пошту в auth.json окремим блоком"""
        try:
            data = self._read_auth_file()
            if not isinstance(data, dict):
                data = {}

            if "users" not in data and data:
                users = {k: v for k, v in data.items() if isinstance(v, str) and k != "emails"}
                migrated = {"users": users}
                for k, v in data.items():
                    if k not in users:
                        migrated[k] = v
                data = migrated

            if "emails" not in data or not isinstance(data.get("emails"), dict):
                data["emails"] = {}

            data["emails"][username] = (email or "").strip()

            self._write_auth_file(data)
        except Exception as e:
            print(f"Error saving email: {e}")

    def _get_email_from_disk(self, username):
        """Дістає збережену пошту"""
        try:
            data = self._read_auth_file()
            if isinstance(data, dict):
                return data.get("emails", {}).get(username, "")
        except:
            pass
        return ""

    def save_keys_to_file(self):
        # Зберігаємо ключі в окремий файл або в той самий auth.json
        data = self._read_auth_file()
        if "users" not in data:
            data = {"users": data}
        data["ai_keys_list"] = ai_manager.get_all_keys()
        self._write_auth_file(data)

    def browse_default_path(self):
        p = tk.filedialog.askdirectory()
        if p:
            self.entry_def_path.delete(0, "end")
            self.entry_def_path.insert(0, p)
            self.save_settings()

    def save_settings(self):
        global proxy_manager
        data = self._read_auth_file()
        if "users" not in data:
            data = {"users": data}

        # Зберігаємо все: шляхи, звук, ім'я автора, ключі, проксі
        if hasattr(self, "entry_def_path"):
            data["default_path"] = self.entry_def_path.get()
        if hasattr(self, "switch_sound"):
            data["sound_enabled"] = bool(self.switch_sound.get())

        # Зберігаємо Alias (якщо пусте - видаляємо, щоб юзати дефолт)
        if hasattr(self, "entry_git_author"):
            author_alias = self.entry_git_author.get().strip()
            if author_alias:
                data["git_author"] = author_alias
            else:
                if "git_author" in data:
                    del data["git_author"]

        # --- ЗБЕРЕЖЕННЯ EMAIL (НОВЕ) ---
        if hasattr(self, "entry_def_email"):
            email_val = self.entry_def_email.get().strip()
            if email_val:
                data["default_email"] = email_val
            elif "default_email" in data:
                del data["default_email"]
        # -------------------------------

        try:
            data["ai_keys_list"] = ai_manager.get_all_keys() if ai_manager else []
        except:
            data["ai_keys_list"] = []
        try:
            data["proxies_list"] = proxy_manager.get_all() if proxy_manager else []
        except:
            data["proxies_list"] = []

        self._write_auth_file(data)
        
    def toggle_theme(self):
        if self.switch_theme.get(): ctk.set_appearance_mode("Dark")
        else: ctk.set_appearance_mode("Light")

    # ===================== TAB 1: GENERATOR =====================
    def build_generator_tab(self):
        t = self.tab_gen
        t.grid_columnconfigure(0, weight=3, uniform="group1")
        t.grid_columnconfigure(1, weight=1, uniform="group1")
        t.grid_rowconfigure(0, weight=1)
        f_left = ctk.CTkFrame(t, fg_color="transparent")
        f_left.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        ctk.CTkLabel(f_left, text="Project Config", font=("Helvetica", 16, "bold")).pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(f_left, text="Select Languages:", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        lang_frame = ctk.CTkFrame(f_left, fg_color=COLOR_FIELD_BG, height=50)
        lang_frame.pack(fill="x", pady=(0, 15))
        self.gen_lang_scroll = ctk.CTkScrollableFrame(lang_frame, orientation="horizontal", height=30, fg_color="transparent")
        self.gen_lang_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        self.gen_langs_vars = {}
        for item in TARGET_STACK:
            var = tk.BooleanVar()
            ctk.CTkCheckBox(self.gen_lang_scroll, text=item, variable=var, width=60).pack(side="left", padx=10)
            self.gen_langs_vars[item] = var
        self.gen_name = self.create_clean_entry(f_left, "Repo Name", width=0)
        self.gen_name.pack(fill="x", pady=5)
        self.gen_desc = self.create_clean_entry(f_left, "Description", width=0)
        self.gen_desc.pack(fill="x", pady=5)
        self.gen_email = self.create_clean_entry(f_left, "Email", width=0)
        self.gen_email.pack(fill="x", pady=5)

        # --- АВТОЗАПОВНЕННЯ ---
        saved_email = self._read_auth_file().get("default_email", "")
        if saved_email: self.gen_email.insert(0, saved_email)
        # ----------------------
        self.gen_private = ctk.CTkSwitch(f_left, text="Private"); self.gen_private.select(); self.gen_private.pack(anchor="w", pady=15)
        ctk.CTkLabel(f_left, text="Intensity:", font=("Helvetica", 12)).pack(anchor="w", pady=(5, 5))
        self.gen_intensity = ctk.CTkSegmentedButton(f_left, values=["Low", "Medium", "High", "Crazy"], height=30)
        self.gen_intensity.set("Medium"); self.gen_intensity.pack(fill="x", pady=5)
        f_right = ctk.CTkFrame(t, fg_color="transparent")
        f_right.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(f_right, text="Timeline", font=("Helvetica", 16, "bold")).pack(anchor="w", pady=(0, 20))
        ctk.CTkLabel(f_right, text="Start").pack(anchor="w")
        self.gen_start = self.create_date_picker(f_right)
        self.gen_start.pack(anchor="w", pady=(0, 15))
        ctk.CTkLabel(f_right, text="End (Archive Date)").pack(anchor="w")
        self.gen_end = self.create_date_picker(f_right)
        self.gen_end.pack(anchor="w", pady=(0, 20))
        ctk.CTkButton(f_right, text="GENERATE PROJECT", height=50, fg_color="black", text_color="white", font=("Helvetica", 13, "bold"), command=self.run_gen).pack(fill="x", pady=20)
        self.gen_progress = ctk.CTkProgressBar(f_right)
        self.gen_progress.set(0)
        self.gen_progress.pack(fill="x", pady=10)

    def run_gen(self):
        langs = [l for l, v in self.gen_langs_vars.items() if v.get()]
        if not self.gen_name.get() or not langs: return messagebox.showerror("Error", "Name and Lang required")
        threading.Thread(target=self._gen_thread, args=(langs,), daemon=True).start()

    def _gen_thread(self, langs):
        tmp = tempfile.mkdtemp()
        try:
            self.log(f"Generating {langs} project...")
            is_priv = bool(self.gen_private.get())
            repo_desc = self._resolve_repo_desc(self.gen_desc.get())
            url = create_github_repo(self.username, self.token, self.gen_name.get(), is_priv, repo_desc)
            auth_url = url.replace("https://", f"https://{self.token}@")
            subprocess.run(["git", "init"], cwd=tmp)
            subprocess.run(["git", "config", "user.email", self.gen_email.get()], cwd=tmp)
            # Вибираємо ім'я: або Alias з налаштувань, або GitHub логін
            git_user_name = self._read_auth_file().get("git_author", self.username)
            subprocess.run(["git", "config", "user.name", git_user_name], cwd=tmp)
            files = []
            if "HTML/CSS" in langs and "JavaScript" in langs:
                for fname, content in WEB_COMBO_TEMPLATE["files"]:
                    with open(os.path.join(tmp, fname), "w") as f: f.write(content)
                    files.append(fname)
            for lang in langs:
                if lang in PROJECT_TEMPLATES:
                    prefix = lang.lower().replace("/", "") + "_core"
                    os.makedirs(os.path.join(tmp, prefix), exist_ok=True)
                    for fname, content in PROJECT_TEMPLATES[lang]["files"]:
                        p = os.path.join(prefix, fname)
                        with open(os.path.join(tmp, p), "w") as f: f.write(content)
                        files.append(p)
            if not files:
                raise Exception("No template files for selected stack")
            start, end = self.get_date_val(self.gen_start), self.get_date_val(self.gen_end)
            seed_date = self._get_seed_date(start)
            seed_t_str = self.generate_human_time(seed_date)
            seed_env = os.environ.copy()
            seed_env["GIT_AUTHOR_DATE"] = seed_env["GIT_COMMITTER_DATE"] = seed_t_str
            subprocess.run(["git", "commit", "--allow-empty", "-m", "Initial commit"], cwd=tmp, env=seed_env)
            days = (end - start).days + 1
            intensity_mode = self.gen_intensity.get()
            for i in range(days):
                cur = start + datetime.timedelta(days=i)
                self.after(0, lambda p=i/days: self.gen_progress.set(p))
                cnt = 0
                is_weekend = (cur.weekday() >= 5)
                if intensity_mode == "Low":
                    if not is_weekend and random.random() > 0.3: cnt = random.randint(1, 3)
                elif intensity_mode == "Medium":
                    if not is_weekend: cnt = random.randint(2, 6)
                    elif random.random() > 0.7: cnt = random.randint(1, 3)
                elif intensity_mode == "High":
                    cnt = random.randint(5, 12)
                    if is_weekend: cnt = int(cnt * 0.5)
                elif intensity_mode == "Crazy": cnt = random.randint(15, 40)
                
                for _ in range(cnt):
                    t_str = self.generate_human_time(cur)
                    target = random.choice(files)
                    ext = os.path.splitext(target)[1]
                    snippet = random.choice(REAL_CODE_SNIPPETS.get(ext, REAL_CODE_SNIPPETS["default"]))
                    with open(os.path.join(tmp, target), "a") as f: f.write(f"\n{snippet}\n")
                    env = os.environ.copy()
                    env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = t_str
                    msg = get_ai_commit_message(target)
                    subprocess.run(["git", "add", "."], cwd=tmp)
                    subprocess.run(["git", "commit", "-m", msg, "--date", t_str], cwd=tmp, env=env)
            
            subprocess.run(["git", "remote", "add", "origin", auth_url], cwd=tmp)
            subprocess.run(["git", "push", "-u", "origin", "main"], cwd=tmp)
            self.log("Generation Complete!")
        except Exception as e: self.log(f"Error: {e}")
        finally: shutil.rmtree(tmp, ignore_errors=True)

    # ===================== TAB 2: CLONER =====================
    # ===================== UPDATED SMART CLONER TAB (v15.1) =====================
    def build_cloner_tab(self):
        t = self.tab_cloner
        
        for widget in t.winfo_children():
            widget.destroy()

        self.scroll_cloner = ctk.CTkScrollableFrame(t, fg_color="transparent")
        self.scroll_cloner.pack(fill="both", expand=True)
        
        f_row1 = ctk.CTkFrame(self.scroll_cloner, fg_color="transparent")
        f_row1.pack(fill="x", padx=10, pady=(10,5))
        
        self.cloner_query = ctk.CTkEntry(f_row1, placeholder_text="Keywords (e.g. crypto bot)...", width=250)
        self.cloner_query.pack(side="left", padx=2)
        
        self.cloner_exclude = ctk.CTkEntry(f_row1, placeholder_text="NOT (e.g. course tutorial)", width=200, text_color="#D00")
        self.cloner_exclude.pack(side="left", padx=10)
        
        ctk.CTkButton(f_row1, text="🎲", width=40, fg_color=PALETTE[3], command=self.cloner_lucky).pack(side="right", padx=2)
        ctk.CTkButton(f_row1, text="Search", width=80, command=self.cloner_search).pack(side="right", padx=2)

        f_row2 = ctk.CTkFrame(self.scroll_cloner, fg_color="transparent")
        f_row2.pack(fill="x", padx=10, pady=(0,10))
        
        self.cloner_min_stars = ctk.CTkEntry(f_row2, placeholder_text="Min★", width=60)
        self.cloner_min_stars.pack(side="left", padx=2)
        ctk.CTkLabel(f_row2, text="-").pack(side="left")
        self.cloner_max_stars = ctk.CTkEntry(f_row2, placeholder_text="Max★", width=60)
        self.cloner_max_stars.pack(side="left", padx=2)
        
        self.cloner_niche = ctk.CTkComboBox(f_row2, values=list(NICHES.keys()), width=140)
        self.cloner_niche.set("General (Any)")
        self.cloner_niche.pack(side="left", padx=10)

        self.cloner_scale = ctk.CTkComboBox(f_row2, values=list(SCALES.keys()), width=140)
        self.cloner_scale.set("Any Size")
        self.cloner_scale.pack(side="left", padx=5)
        
        self.cloner_sort = ctk.CTkComboBox(f_row2, values=list(SORT_OPTIONS.keys()), width=120)
        self.cloner_sort.set("Most Stars")
        self.cloner_sort.pack(side="left", padx=5)
        
        self.chk_strict = ctk.CTkSwitch(f_row2, text="Strict (7%)", onvalue=True, offvalue=False, width=80, command=self.toggle_strict)
        self.chk_strict.pack(side="left", padx=10)
        
        self.chk_fav_only = ctk.CTkSwitch(f_row2, text="⭐ Saved", onvalue=True, offvalue=False, command=self.toggle_fav_filter, progress_color="#FFD700")
        self.chk_fav_only.pack(side="left", padx=10)

        self.scroll_lang = ctk.CTkScrollableFrame(self.scroll_cloner, orientation="horizontal", height=40)
        self.scroll_lang.pack(fill="x", padx=10, pady=5)
        self.langs_vars = {}
        for item in TARGET_STACK:
            var = tk.BooleanVar()
            ctk.CTkCheckBox(self.scroll_lang, text=item, variable=var, width=60).pack(side="left", padx=5)
            self.langs_vars[item] = var

        self.cloner_results_frame = ctk.CTkScrollableFrame(self.scroll_cloner, fg_color=COLOR_FIELD_BG, label_text="Filtered Results", height=250)
        self.cloner_results_frame.pack(fill="x", padx=10, pady=10)
        
        f_nav = ctk.CTkFrame(self.scroll_cloner, fg_color="transparent")
        f_nav.pack(fill="x", padx=20, pady=5)
        self.btn_prev = ctk.CTkButton(f_nav, text="<<<", width=60, command=lambda: self.change_cloner_page(-1))
        self.btn_prev.pack(side="left")
        self.lbl_cloner_page = ctk.CTkLabel(f_nav, text="Page 1", font=("Helvetica", 12, "bold"))
        self.lbl_cloner_page.pack(side="left", padx=20)
        self.btn_next = ctk.CTkButton(f_nav, text=">>>", width=60, command=lambda: self.change_cloner_page(1))
        self.btn_next.pack(side="left")
        
        self.lbl_loading = ctk.CTkLabel(f_nav, text="", text_color=COLOR_SUCCESS)
        self.lbl_loading.pack(side="left", padx=10)

        f_bot = ctk.CTkFrame(self.scroll_cloner, fg_color="white", corner_radius=10)
        f_bot.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(f_bot, text="🎯 Target Configuration", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", padx=10, pady=(10,5))
        
        self.cloner_target_name = ctk.CTkEntry(f_bot, placeholder_text="New Repo Name (e.g. my-saas-platform)")
        self.cloner_target_name.pack(fill="x", padx=10, pady=2)
        
        self.cloner_target_desc = ctk.CTkEntry(f_bot, placeholder_text="Description (Optional)")
        self.cloner_target_desc.pack(fill="x", padx=10, pady=2)
        
        self.cloner_private = ctk.CTkSwitch(f_bot, text="Private Repo", text_color="black")
        self.cloner_private.select()
        self.cloner_private.pack(anchor="w", padx=10, pady=2)

        ctk.CTkFrame(f_bot, height=2, fg_color="#EEE").pack(fill="x", pady=10)
        ctk.CTkLabel(f_bot, text="⏳ Time Architect", font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", padx=10, pady=5)

        f_opts_time = ctk.CTkFrame(f_bot, fg_color="transparent")
        f_opts_time.pack(fill="x", padx=5)
        
        ctk.CTkLabel(f_opts_time, text="🎭 Persona:", text_color="black").pack(side="left", padx=5)
        self.combo_persona = ctk.CTkComboBox(f_opts_time, values=["Freelancer", "Office", "Night Owl", "Bot 24/7"], width=120)
        self.combo_persona.set("Freelancer")
        self.combo_persona.pack(side="left", padx=5)

        ctk.CTkLabel(f_opts_time, text="⚓ Anchor:", text_color="black").pack(side="left", padx=(15, 5))
        self.var_anchor = ctk.StringVar(value="end")
        ctk.CTkRadioButton(f_opts_time, text="End Today", variable=self.var_anchor, value="end", text_color="black", command=self._recalc_dates).pack(side="left", padx=5)
        ctk.CTkRadioButton(f_opts_time, text="Start Date", variable=self.var_anchor, value="start", text_color="black", command=self._recalc_dates).pack(side="left", padx=5)

        self.lbl_speed = ctk.CTkLabel(f_bot, text="Pace: 1.0x (Original)", font=("Arial", 12, "bold"), text_color="black")
        self.lbl_speed.pack(anchor="w", padx=10, pady=(10,0))
        
        self.slider_time = ctk.CTkSlider(f_bot, from_=0.1, to=3.0, number_of_steps=29, command=self._on_slider_change)
        self.slider_time.set(1.0)
        self.slider_time.pack(fill="x", padx=10, pady=5)

        f_dates = ctk.CTkFrame(f_bot, fg_color="transparent")
        f_dates.pack(fill="x", padx=10, pady=5)
        
        f_d1 = ctk.CTkFrame(f_dates, fg_color="transparent"); f_d1.pack(side="left", expand=True)
        ctk.CTkLabel(f_d1, text="Start Date", text_color="gray").pack()
        self.cloner_start = self.create_date_picker(f_d1)
        self.cloner_start.pack()
        
        ctk.CTkLabel(f_dates, text="➜", font=("Arial", 16), text_color="gray").pack(side="left", padx=10)
        
        f_d2 = ctk.CTkFrame(f_dates, fg_color="transparent"); f_d2.pack(side="left", expand=True)
        ctk.CTkLabel(f_d2, text="End Date", text_color="gray").pack()
        self.cloner_end = self.create_date_picker(f_d2)
        self.cloner_end.pack()

        for picker in [self.cloner_start, self.cloner_end]:
            picker.cb_day.configure(command=lambda x: self._on_manual_date_change())
            picker.cb_month.configure(command=lambda x, p=picker: (p._on_month_change(x), self._on_manual_date_change()))
            picker.cb_year.configure(command=lambda x, p=picker: (p._on_year_change(x), self._on_manual_date_change()))

        self.lbl_time_travel = ctk.CTkLabel(f_bot, text="", font=("Arial", 11, "bold"), text_color="#FF9800")
        self.lbl_time_travel.pack(pady=(5,0))
        self.lbl_density_warn = ctk.CTkLabel(f_bot, text="Density Check...", text_color="gray", font=("Arial", 11))
        self.lbl_density_warn.pack(pady=(0,10))

        ctk.CTkFrame(f_bot, height=2, fg_color="#EEE").pack(fill="x", pady=5)
        
        self.chk_license_swap = ctk.CTkCheckBox(f_bot, text="📜 License Swap", onvalue=True, offvalue=False, text_color="black")
        self.chk_license_swap.select()
        self.chk_license_swap.pack(side="left", padx=10, pady=10)
        
        self.chk_translate = ctk.CTkCheckBox(f_bot, text="🌍 Translate Comments", onvalue=True, offvalue=False, text_color="black")
        self.chk_translate.pack(side="left", padx=10, pady=10)
        
        self.chk_ghost_issues = ctk.CTkCheckBox(f_bot, text="👻 Ghost Issues", text_color="black")
        self.chk_ghost_issues.pack(side="left", padx=10, pady=10)

        self.chk_realistic_stats = ctk.CTkCheckBox(f_bot, text="🔀 Realistic Stats (PR/Review/Issue)", text_color="black")
        self.chk_realistic_stats.pack(side="left", padx=10, pady=10)

        self.lbl_cloner_status = ctk.CTkLabel(f_bot, text="Ready", font=("Arial", 12), text_color="gray")
        self.lbl_cloner_status.pack(side="top", pady=(5,0))
        
        self.cloner_progress = ctk.CTkProgressBar(f_bot, height=10)
        self.cloner_progress.set(0)
        self.cloner_progress.pack(fill="x", padx=10, pady=5)

        self.btn_cloner_run = ctk.CTkButton(f_bot, text="🚀 ACTIVATE GOD MODE", height=50, fg_color=PALETTE[4], font=("Helvetica", 16, "bold"), command=self.start_cloner)
        self.btn_cloner_run.pack(fill="x", padx=10, pady=10)

        self.time_architect = TimeArchitect()

    # ===================== NEW TEAM MODE (ROSTER UI) =====================
    def build_collab_tab(self):
        t = self.tab_collab
        for w in t.winfo_children():
            w.destroy()

        t.grid_columnconfigure(0, weight=4)
        t.grid_columnconfigure(1, weight=6)
        t.grid_rowconfigure(0, weight=1)

        f_left = ctk.CTkFrame(t, fg_color="transparent")
        f_left.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        f_left.grid_rowconfigure(2, weight=1)
        f_left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(f_left, text="👥 Team Roster", font=("Arial", 20, "bold")).grid(row=0, column=0, sticky="w", pady=(0,10))
        
        ctk.CTkButton(
            f_left,
            text="+ Add Member",
            fg_color="green",
            height=35,
            command=self.add_team_member_dialog,
        ).grid(row=1, column=0, sticky="ew", pady=(0,10))

        self.scroll_roster = ctk.CTkScrollableFrame(f_left, fg_color="white")
        self.scroll_roster.grid(row=2, column=0, sticky="nsew")

        f_atomic = ctk.CTkFrame(f_left, fg_color="transparent")
        f_atomic.grid(row=3, column=0, sticky="ew", pady=10)
        self.chk_atomic = ctk.CTkSwitch(f_atomic, text="⚛️ Atomic Split (Smart)", onvalue=True, offvalue=False)
        self.chk_atomic.select()
        self.chk_atomic.pack(anchor="w")
        ctk.CTkLabel(f_atomic, text="(Splits commits by file types)", font=("Arial", 10), text_color="gray").pack(anchor="w", padx=40)

        self.scroll_config = ctk.CTkScrollableFrame(t, fg_color="transparent")
        self.scroll_config.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

        self._build_team_section_header("🎯 Project Identity")
        
        f_ident = ctk.CTkFrame(self.scroll_config, fg_color="white", corner_radius=10)
        f_ident.pack(fill="x", pady=5)
        
        self.entry_team_name = ctk.CTkEntry(f_ident, placeholder_text="Repo Name", height=40, font=("Arial", 14, "bold"))
        self.entry_team_name.pack(fill="x", padx=15, pady=(15, 5))
        
        self.entry_team_desc = ctk.CTkEntry(f_ident, placeholder_text="Repository Description (Optional)")
        self.entry_team_desc.pack(fill="x", padx=15, pady=5)
        
        f_priv = ctk.CTkFrame(f_ident, fg_color="transparent")
        f_priv.pack(fill="x", padx=15, pady=10)
        self.sw_team_private = ctk.CTkSwitch(f_priv, text="Private Repo", onvalue=True, offvalue=False)
        self.sw_team_private.select()
        self.sw_team_private.pack(side="left")
        
        ctk.CTkButton(
            f_priv,
            text="❤️ Save to Favs",
            width=100,
            fg_color="#FFD700",
            text_color="black",
            command=self._save_current_project_to_favs,
        ).pack(side="right")

        f_src = ctk.CTkFrame(f_ident, fg_color="#F9F9F9")
        f_src.pack(fill="x", padx=1, pady=(5,1))
        donor_txt = "No source selected"
        donor_url = ""
        if getattr(self, 'selected_donor', None):
            donor_txt = f"Source: {self.selected_donor.get('full_name')}"
            donor_url = self.selected_donor.get('html_url')
            if not self.entry_team_name.get():
                if hasattr(self, 'cloner_target_name') and self.cloner_target_name.get():
                    self.entry_team_name.insert(0, self.cloner_target_name.get())

        ctk.CTkLabel(f_src, text=donor_txt, font=("Consolas", 11), text_color="gray").pack(side="left", padx=10, pady=5)
        if donor_url:
            ctk.CTkButton(
                f_src,
                text="🔗 Open",
                width=60,
                height=20,
                fg_color="#DDD",
                text_color="black",
                command=lambda: webbrowser.open(donor_url),
            ).pack(side="right", padx=10)

        self._build_team_section_header("⏳ Timeline & Pace")
        f_time = ctk.CTkFrame(self.scroll_config, fg_color="white", corner_radius=10)
        f_time.pack(fill="x", pady=5)
        
        f_dates = ctk.CTkFrame(f_time, fg_color="transparent")
        f_dates.pack(fill="x", padx=10, pady=10)
        
        f_d1 = ctk.CTkFrame(f_dates, fg_color="transparent")
        f_d1.pack(side="left", expand=True)
        ctk.CTkLabel(f_d1, text="Start Date", font=("Arial", 11, "bold")).pack()
        self.team_start = self.create_date_picker(f_d1)
        self.team_start.pack()

        ctk.CTkLabel(f_dates, text="➜", text_color="gray", font=("Arial", 20)).pack(side="left", padx=10)

        f_d2 = ctk.CTkFrame(f_dates, fg_color="transparent")
        f_d2.pack(side="left", expand=True)
        ctk.CTkLabel(f_d2, text="End Date", font=("Arial", 11, "bold")).pack()
        self.team_end = self.create_date_picker(f_d2)
        self.team_end.pack()
        
        ctk.CTkLabel(f_time, text="Intensity (Pace):", font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(5,0))
        self.slider_team_pace = ctk.CTkSlider(f_time, from_=0.1, to=3.0, number_of_steps=29, command=self._on_team_slider_change)
        self.slider_team_pace.set(1.0)
        self.slider_team_pace.pack(fill="x", padx=15, pady=10)
        
        f_lbls = ctk.CTkFrame(f_time, fg_color="transparent")
        f_lbls.pack(fill="x", padx=15, pady=(0,10))
        ctk.CTkLabel(f_lbls, text="Slow (0.1x)", font=("Arial", 10)).pack(side="left")
        ctk.CTkLabel(f_lbls, text="Turbo (3.0x)", font=("Arial", 10)).pack(side="right")
        
        f_pers = ctk.CTkFrame(f_time, fg_color="transparent")
        f_pers.pack(fill="x", padx=15, pady=(0,15))
        ctk.CTkLabel(f_pers, text="Work Persona:", font=("Arial", 12, "bold")).pack(side="left")
        self.combo_team_persona = ctk.CTkComboBox(f_pers, values=["Freelancer", "Office", "Night Owl", "Bot 24/7"])
        self.combo_team_persona.pack(side="right", fill="x", expand=True, padx=(10,0))

        self._build_team_section_header("✨ Enhancements & Realism")
        f_magic = ctk.CTkFrame(self.scroll_config, fg_color="white", corner_radius=10)
        f_magic.pack(fill="x", pady=5)
        
        f_magic.columnconfigure(0, weight=1)
        f_magic.columnconfigure(1, weight=1)

        self.chk_identity_map = ctk.CTkSwitch(f_magic, text="🎭 Identity Mirroring", onvalue=True, offvalue=False)
        self.chk_identity_map.select()
        self.chk_identity_map.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 5))
        
        lbl_desc = ctk.CTkLabel(f_magic, text="(Maps original authors to your team)", font=("Arial", 10), text_color="gray")
        lbl_desc.grid(row=1, column=0, columnspan=2, sticky="w", padx=55, pady=(0, 10))
        
        self.chk_team_ai_rewrite = ctk.CTkCheckBox(f_magic, text="🧠 AI Rewrite Msgs", onvalue=True, offvalue=False)
        self.chk_team_ai_rewrite.select()
        self.chk_team_ai_rewrite.grid(row=2, column=0, sticky="w", padx=15, pady=5)
        
        self.chk_team_vacations = ctk.CTkCheckBox(f_magic, text="🏖 Random Vacations", onvalue=True, offvalue=False)
        self.chk_team_vacations.select()
        self.chk_team_vacations.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        self.chk_team_pr = ctk.CTkCheckBox(f_magic, text="🔀 Simulate PRs", onvalue=True, offvalue=False)
        self.chk_team_pr.select()
        self.chk_team_pr.grid(row=3, column=0, sticky="w", padx=15, pady=5)
        
        self.chk_team_license = ctk.CTkCheckBox(f_magic, text="📜 License Swap", onvalue=True, offvalue=False)
        self.chk_team_license.select()
        self.chk_team_license.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        self.chk_team_issues = ctk.CTkCheckBox(f_magic, text="👻 Ghost Issues", onvalue=True, offvalue=False)
        self.chk_team_issues.grid(row=4, column=0, sticky="w", padx=15, pady=(5, 15))

        ctk.CTkLabel(self.scroll_config, text="").pack(pady=5)
        self.btn_team_run = ctk.CTkButton(
            self.scroll_config,
            text="🚀 LAUNCH AGENCY",
            height=60,
            fg_color=PALETTE[4],
            font=("Arial", 18, "bold"),
            command=self.start_agency_cloning,
        )
        self.btn_team_run.pack(fill="x", pady=20)

        self.render_roster()

    def _build_team_section_header(self, text):
        ctk.CTkLabel(self.scroll_config, text=text, font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w", pady=(15, 5))

    def _save_current_project_to_favs(self):
        if getattr(self, 'selected_donor', None):
            self.toggle_favorite(self.selected_donor)
            messagebox.showinfo("Saved", "Project saved to Favorites!")
        else:
            messagebox.showerror("Error", "No project selected to save.")

    def render_roster(self):
        for w in self.scroll_roster.winfo_children(): w.destroy()
        
        if not self.team_roster:
            ctk.CTkLabel(self.scroll_roster, text="No members yet. Add someone!", text_color="gray").pack(pady=20)
            return

        for idx, member in enumerate(self.team_roster):
            f = ctk.CTkFrame(self.scroll_roster, fg_color="#F0F0F0", height=45)
            f.pack(fill="x", pady=5, padx=5)
            f.pack_propagate(False)

            f_btns = ctk.CTkFrame(f, fg_color="transparent")
            f_btns.pack(side="right", padx=5)

            ctk.CTkButton(f_btns, text="🛠 Skills", width=60, height=24, fg_color="#555", font=("Arial", 11),
                          command=lambda i=idx: self.edit_member_skills(i)).pack(side="left", padx=2)

            ctk.CTkButton(f_btns, text="✕", width=28, height=24, fg_color="#FF3B30", hover_color="#D00000",
                          command=lambda i=idx: self.remove_team_member(i)).pack(side="left", padx=2)

            role_icon = "👑" if idx == 0 else "👨‍💻"
            ctk.CTkLabel(f, text=f"{role_icon} {member['name']}", font=("Arial", 13, "bold"), width=100, anchor="w").pack(side="left", padx=(10, 5))
            
            skills_list = member.get("skills_display", ["Any"])
            skills_txt = ", ".join(skills_list)
            if member.get("orphans"): skills_txt += " + 📦"
            
            if len(skills_txt) > 35: skills_txt = skills_txt[:32] + "..."
            
            ctk.CTkLabel(f, text=skills_txt, text_color="gray", font=("Arial", 11), anchor="w").pack(side="left", fill="x", expand=True)

    def add_team_member_dialog(self):
        users = list(self.auth_data.keys())
        if not users:
            messagebox.showerror("Error", "No users in auth.json! Add them in Settings tab.")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.geometry("300x150")
        dialog.title("Add Member")
        
        lbl = ctk.CTkLabel(dialog, text="Select User:")
        lbl.pack(pady=10)
        
        combo = ctk.CTkComboBox(dialog, values=users)
        combo.pack(pady=5)
        
        def _add():
            u = combo.get()
            t = self.auth_data.get(u)
            saved_email = self._get_email_from_disk(u)
            self.team_roster.append({
                "name": u,
                "token": t,
                "email": saved_email,
                "skills": [],
                "skills_display": ["Fullstack"],
                "orphans": (len(self.team_roster) == 0)
            })
            self.render_roster()
            dialog.destroy()
            
        ctk.CTkButton(dialog, text="Add", command=_add).pack(pady=10)

    def remove_team_member(self, idx):
        self.team_roster.pop(idx)
        self.render_roster()

    def edit_member_skills(self, idx):
        member = self.team_roster[idx]

        project_langs = []
        donor = getattr(self, 'selected_donor', None)
        if donor:
            try:
                langs_dict = api_get_languages(self.token, donor['owner']['login'], donor['name'])
                if langs_dict:
                    project_langs = list(langs_dict.keys())
            except:
                pass
            
        detected_categories = set()
        for pl in project_langs:
            if pl in self.language_mapping:
                detected_categories.add(self.language_mapping[pl])

        win = ctk.CTkToplevel(self)
        win.title(f"Config: {member['name']}")
        win.geometry("400x600")
        
        ctk.CTkLabel(win, text=f"Configure {member['name']}", font=("Arial", 16, "bold")).pack(pady=(10, 5))

        f_email = ctk.CTkFrame(win, fg_color="transparent")
        f_email.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(f_email, text="Git Email:", font=("Arial", 11, "bold")).pack(anchor="w")
        entry_email = ctk.CTkEntry(f_email)
        entry_email.pack(fill="x")

        saved_email = self._get_email_from_disk(member['name'])
        current_email = member.get('email', saved_email)
        if current_email:
            entry_email.insert(0, current_email)

        f_role = ctk.CTkFrame(win, fg_color="#E3F2FD", corner_radius=6)
        f_role.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(
            f_role,
            text="Primary Role (Fallback):",
            font=("Arial", 12, "bold"),
            text_color="#1565C0",
        ).pack(anchor="w", padx=10, pady=(5,0))
        
        combo_role = ctk.CTkComboBox(f_role, values=["General (Any)", "Frontend", "Backend", "Mobile"])
        combo_role.set(member.get("primary_role", "General (Any)"))
        combo_role.pack(fill="x", padx=10, pady=(0,10))

        scroll = ctk.CTkScrollableFrame(win)
        scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        vars_map = {}
        
        for cat, extensions in self.known_extensions.items():
            if cat == "Config/Orphans":
                continue
            if donor and detected_categories and cat not in detected_categories:
                continue

            is_checked = (cat in member.get("skills_display", [])) or ("Fullstack" in member.get("skills_display", []))
            var = ctk.BooleanVar(value=is_checked)
            
            text_col = "#00C853" if cat in detected_categories else "black"
            chk = ctk.CTkCheckBox(scroll, text=cat, variable=var, text_color=text_col)
            chk.pack(anchor="w", pady=5)
            vars_map[cat] = var
            
        var_orphans = ctk.BooleanVar(value=member.get("orphans", False))
        ctk.CTkSwitch(scroll, text="Takes Configs/Readmes", variable=var_orphans).pack(anchor="w", pady=10)
        
        def _save():
            email_val = entry_email.get().strip()
            member['email'] = email_val
            self._save_email_to_disk(member['name'], email_val)
            
            member['primary_role'] = combo_role.get()
            
            selected_exts = []
            display_cats = []
            for cat, v in vars_map.items():
                if v.get():
                    selected_exts.extend(self.known_extensions[cat])
                    display_cats.append(cat)
            
            member["skills"] = selected_exts
            role_tag = f"[{member['primary_role'][0]}E]" if member['primary_role'] != "General (Any)" else ""
            
            member["skills_display"] = display_cats if display_cats else ["Helper"]
            if role_tag:
                member["skills_display"].append(role_tag)
            
            member["orphans"] = var_orphans.get()
            
            self.render_roster()
            win.destroy()
            
        ctk.CTkButton(win, text="Save Settings", fg_color="green", command=_save).pack(pady=10, fill="x", padx=20)

    def _determine_file_owner(self, fpath, roster, original_author=None, identity_map=None):
        """
        Розумний розподіл: Розширення > Identity Map > Роль > Рандом
        """
        ext = os.path.splitext(fpath)[1].lower()
        fname = os.path.basename(fpath).lower()
        fpath_lower = str(fpath).lower()
        
        mapped_idx = -1
        if identity_map and original_author:
            mapped_idx = identity_map.get(original_author, -1)
        
        candidates_explicit = []
        for idx, m in enumerate(roster):
            if ext in m.get("skills", []):
                candidates_explicit.append(idx)
        
        if mapped_idx != -1 and mapped_idx in candidates_explicit:
            return mapped_idx
            
        if candidates_explicit:
            return random.choice(candidates_explicit)

        candidates_role = []
        for idx, m in enumerate(roster):
            role = m.get("primary_role", "General (Any)")
            if role == "General (Any)":
                continue
            
            def_role = self.role_definitions.get(role, {})
            match_ext = ext in def_role.get("exts", [])
            match_folder = any(fold in fpath_lower for fold in def_role.get("folders", []))
            
            if match_ext or match_folder:
                candidates_role.append(idx)
                
        if candidates_role:
            if mapped_idx in candidates_role: return mapped_idx
            return random.choice(candidates_role)

        is_orphan = (fname in self.known_extensions["Config/Orphans"] or ext in self.known_extensions["Config/Orphans"])
        if is_orphan:
            if mapped_idx != -1: return mapped_idx
            candidates_orphans = [i for i, m in enumerate(roster) if m.get("orphans", False)]
            if candidates_orphans: return random.choice(candidates_orphans)

        if mapped_idx != -1: return mapped_idx
        return 0

    def start_agency_cloning(self):
        if not self.team_roster:
            return messagebox.showerror("Error", "Team Roster is empty! Add members on the left.")
        
        if not getattr(self, 'selected_donor', None):
            return messagebox.showerror("Error", "No source project selected. Go to 'Cloner', search, and click 'Team'.")
        
        name = self.entry_team_name.get().strip()
        if not name:
            return messagebox.showerror("Error", "Project Name is required!")
            
        start_d = self.get_date_val(self.team_start)
        end_d = self.get_date_val(self.team_end)
        
        if not start_d or not end_d:
            return messagebox.showerror("Error", "Invalid dates in Team Timeline.")
            
        if start_d > end_d:
            return messagebox.showerror("Error", "Start Date cannot be after End Date.")

        config = {
            "donor": self.selected_donor,
            "name": name,
            "desc": self._resolve_repo_desc(self.entry_team_desc.get(), self.selected_donor),
            "is_private": self.sw_team_private.get(),
            "start": start_d,
            "end": end_d,
            "persona": self.combo_team_persona.get(),
            "email": self.gen_email.get(),
            "use_identity_map": self.chk_identity_map.get(),
            "ai_rewrite": self.chk_team_ai_rewrite.get(),
            "vacations": self.chk_team_vacations.get(),
            "merge_mode": self.chk_team_pr.get(),
            "ghost_issues": self.chk_team_issues.get(),
            "translate": False,
            "license_swap": self.chk_team_license.get(),
            "mode": "atomic" if self.chk_atomic.get() else "simple",
            "roster": self.team_roster
        }
        
        self.stop_cloner_flag = False
        self.btn_team_run.configure(text="🟥 STOP AGENCY OP", fg_color="red", command=self.cancel_cloner)
        
        self.log(f"🚀 Starting Agency Mode: {name}")
        threading.Thread(target=self.run_agency_logic, args=(config,), daemon=True).start()

    # ЛОГІКА АВТОМАТИЧНОГО ПЕРЕМИКАННЯ
    def toggle_strict(self):
        if self.chk_strict.get():
            self.cloner_sort.set("Recently Updated")
            self.log("ℹ️ Strict Mode ON: Auto-switched to 'Recently Updated'")

    def cloner_lucky(self):
        if hasattr(self, 'lbl_loading'):
            self.lbl_loading.configure(text="🍀 Feeling Lucky...", text_color=PALETTE[3])
        threading.Thread(target=self._lucky_thread, daemon=True).start()

    def _lucky_thread(self):
        q = self.cloner_query.get()
        niche = self.cloner_niche.get()
        items = [l for l, v in self.langs_vars.items() if v.get()]
        
        if not q and niche == "General (Any)" and not items:
            niche = random.choice(list(NICHES.keys()))
            items = [random.choice(TARGET_STACK)]
            self.log(f"🎲 Lucky: Auto-picked {niche} + {items[0]}")
        
        rand_page = random.randint(1, 5)
        
        results, _ = self._fetch_and_filter(rand_page)
        
        if not results:
            results, _ = self._fetch_and_filter(1)
            
        self.after(0, lambda: self._render_lucky_result(results))

    def _render_lucky_result(self, items):
        if not items:
            self.lbl_loading.configure(text="❌ Bad Luck (0 found)", text_color="red")
            self.render_cloner_results([])
            return
            
        winner = random.choice(items)
        
        self.lbl_loading.configure(text="✨ JACKPOT!", text_color=PALETTE[4])
        self.render_cloner_results([winner])

    # --- SCROLL HANDLERS ---
    def _bound_to_mousewheel(self, event):
        self.cloner_results_frame.bind_all("<MouseWheel>", self._on_mousewheel_results)
        self.cloner_results_frame.bind_all("<Button-4>", self._on_mousewheel_results)
        self.cloner_results_frame.bind_all("<Button-5>", self._on_mousewheel_results)

    def _unbound_to_mousewheel(self, event):
        self.scroll_cloner.bind_all("<MouseWheel>", self._on_mousewheel_main)
        self.scroll_cloner.bind_all("<Button-4>", self._on_mousewheel_main)
        self.scroll_cloner.bind_all("<Button-5>", self._on_mousewheel_main)

    def _get_scroll_amount(self, event):
        if abs(event.delta) < 50: return -1 if event.delta > 0 else 1 
        else: return int(-1 * (event.delta / 120))

    def _on_mousewheel_results(self, event):
        try: self.cloner_results_frame._parent_canvas.yview_scroll(self._get_scroll_amount(event), "units")
        except: pass
        return "break"

    def _on_mousewheel_main(self, event):
        try: self.scroll_cloner._parent_canvas.yview_scroll(self._get_scroll_amount(event), "units")
        except: pass

    # --- NEW SEARCH ENGINE LOGIC (v14) ---
    def cloner_search(self):
        self.cloner_page = 1
        self.search_cache = {}

        search_params = {
            "query": self.cloner_query.get().strip(),
            "exclude": self.cloner_exclude.get().strip(),
            "min_stars": self.cloner_min_stars.get(),
            "max_stars": self.cloner_max_stars.get(),
            "niche": self.cloner_niche.get(),
            "scale": self.cloner_scale.get(),
            "sort": self.cloner_sort.get(),
            "strict": self.chk_strict.get(),
            "fav_only": self.chk_fav_only.get(),
            "langs": [l for l, v in self.langs_vars.items() if v.get()],
        }
        self.last_search_params = search_params

        if hasattr(self, 'lbl_loading'):
            self.lbl_loading.configure(text="🔍 Searching...", text_color="orange")

        threading.Thread(target=self._deep_search_thread, args=(self.cloner_page, search_params), daemon=True).start()

    def change_cloner_page(self, delta):
        new_page = self.cloner_page + delta
        if new_page < 1: return
        self.cloner_page = new_page
        
        # Перевіряємо кеш
        if hasattr(self, 'search_cache') and new_page in self.search_cache:
            self.render_cloner_results(self.search_cache[new_page])
            # Фоново вантажимо наступну
            threading.Thread(target=self._background_prefetch, args=(new_page + 1,), daemon=True).start()
        else:
            # ЯКЩО НЕМА В КЕШІ - ПОКАЗУЄМО ЗАВАНТАЖЕННЯ
            self.lbl_loading.configure(text=f"⏳ Loading Page {new_page}...", text_color="orange")
            params = getattr(self, 'last_search_params', None)
            if not params:
                params = {
                    "query": self.cloner_query.get().strip(),
                    "exclude": self.cloner_exclude.get().strip(),
                    "min_stars": self.cloner_min_stars.get(),
                    "max_stars": self.cloner_max_stars.get(),
                    "niche": self.cloner_niche.get(),
                    "scale": self.cloner_scale.get(),
                    "sort": self.cloner_sort.get(),
                    "strict": self.chk_strict.get(),
                    "fav_only": self.chk_fav_only.get(),
                    "langs": [l for l, v in self.langs_vars.items() if v.get()],
                }
                self.last_search_params = params
            threading.Thread(target=self._deep_search_thread, args=(new_page, params), daemon=True).start()

    def _deep_search_thread(self, page, params):
        try:
            self.log(f"🔍 Deep Scanning Page {page}...")
            results, total_count = self._fetch_and_filter_safe(page, params)

            if not hasattr(self, 'search_cache'):
                self.search_cache = {}
            self.search_cache[page] = results

            effective_total = min(total_count, 1000)
            self.cloner_max_pages = (effective_total // 20) + (1 if effective_total % 20 > 0 else 0)
            if self.cloner_max_pages == 0:
                self.cloner_max_pages = 1

            self.after(0, lambda: self.render_cloner_results(results))
            self.after(0, lambda t=total_count: self.lbl_loading.configure(text=f"✅ Found {t}", text_color="#34C759"))

            threading.Thread(target=self._background_prefetch, args=(page + 1, params), daemon=True).start()
        except Exception as e:
            print(f"Search Error: {e}")
            try:
                self.after(0, lambda: self.lbl_loading.configure(text="❌ Error", text_color="red"))
            except:
                pass

    def _background_prefetch(self, page, params):
        try:
            self.after(0, lambda: self.lbl_loading.configure(text="⏳ Prefetching..."))
        except:
            pass
        results, _ = self._fetch_and_filter_safe(page, params)
        if not hasattr(self, 'search_cache'):
            self.search_cache = {}
        self.search_cache[page] = results
        try:
            self.after(0, lambda: self.lbl_loading.configure(text="🟢 Next Page Ready"))
        except:
            pass

    def _fetch_and_filter_safe(self, page, p):
        """Безпечна версія пошуку, яка не чіпає UI"""
        if p.get("fav_only"):
            return self.favorites, len(self.favorites)

        q = str(p.get("query") or "").strip()

        url_match = re.search(r"github\.com[:/]([^/]+)/([^/\s]+)", q)
        if url_match:
            owner, repo_name = url_match.groups()
            repo_name = repo_name.replace(".git", "").rstrip()

            headers = {"Authorization": f"Bearer {self.token}"}
            try:
                url = f"{REST_API_URL}/repos/{owner}/{repo_name}"
                r = get_session(self.token).get(url, headers=headers, timeout=10)
                if r.status_code == 200:
                    return [r.json()], 1
            except:
                pass

        exclude = str(p.get("exclude") or "").strip()
        if exclude:
            not_words = " ".join([f"-{w.strip()}" for w in exclude.split()])
            q = f"{q} {not_words}".strip()

        items = list(p.get("langs") or [])
        niche = str(p.get("niche") or "")
        strict_mode = bool(p.get("strict"))

        min_s = str(p.get("min_stars") or "0")
        max_s = str(p.get("max_stars") or "1000000")
        scale_key = str(p.get("scale") or "")
        sort_key = SORT_OPTIONS.get(str(p.get("sort") or ""), "")
        topics = NICHES.get(niche, [])

        items_list, total_count = search_github_repos(
            self.token,
            q,
            items,
            topics,
            scale_key,
            min_s,
            max_s,
            sort_key,
            page,
            self.log,
            strict_mode,
        )

        if not strict_mode:
            return items_list, total_count

        filtered = []
        target_lang = resolve_stack_primary_language(items[0]) if items else "Any"
        for item in items_list:
            try:
                langs = api_get_languages(self.token, item['owner']['login'], item['name'])
                if not langs:
                    continue
                total = sum(langs.values())
                if total == 0:
                    continue
                foreign = 0
                for l, s in langs.items():
                    if l != target_lang and l not in WHITELIST_LANGS:
                        foreign += s
                if (foreign / total) <= 0.07:
                    filtered.append(item)
            except:
                pass

        return filtered, total_count

    def _fetch_and_filter(self, page):
        # 1. Якщо включений фільтр "Favorites" - повертаємо їх
        if hasattr(self, 'chk_fav_only') and self.chk_fav_only.get():
            return self.favorites, len(self.favorites)

        q = self.cloner_query.get().strip()

        # --- НОВА ЛОГІКА: ПЕРЕВІРКА НА ПРЯМЕ ПОСИЛАННЯ ---
        # Шукаємо патерн "github.com/user/repo"
        url_match = re.search(r"github\.com[:/]([^/]+)/([^/\s]+)", q)
        
        if url_match:
            owner, repo_name = url_match.groups()
            # Чистимо від сміття типу .git в кінці або зайвих пробілів
            repo_name = repo_name.replace(".git", "").rstrip()
            
            self.log(f"🔗 Detected Direct Link: {owner}/{repo_name}")
            
            headers = {"Authorization": f"Bearer {self.token}"}
            try:
                # Робимо прямий запит до конкретного репо (ігноруючи пошук)
                url = f"{REST_API_URL}/repos/{owner}/{repo_name}"
                r = get_session(self.token).get(url, headers=headers, timeout=10)
                
                if r.status_code == 200:
                    # Повертаємо список з 1 елемента
                    return [r.json()], 1
                else:
                    self.log(f"❌ Repo Not Found (HTTP {r.status_code}). Check access or URL.")
                    return [], 0
            except Exception as e:
                self.log(f"❌ Network Error: {e}")
                return [], 0
        # ----------------------------------------------------

        # ... Далі йде стандартний пошук (якщо це не посилання) ...
        exclude = self.cloner_exclude.get()

        if exclude:
            not_words = " ".join([f"-{w.strip()}" for w in exclude.split()])
            q = f"{q} {not_words}".strip()

        items = [l for l, v in self.langs_vars.items() if v.get()]
        niche = self.cloner_niche.get()
        strict_mode = bool(self.chk_strict.get())

        # Читаємо налаштування UI
        min_s = self.cloner_min_stars.get() or "0"
        max_s = self.cloner_max_stars.get() or "1000000"
        scale_key = self.cloner_scale.get()
        sort_key = SORT_OPTIONS.get(self.cloner_sort.get(), "")
        topics = NICHES.get(niche, [])

        items_list, total_count = search_github_repos(
            self.token,
            q,
            items,
            topics,
            scale_key,
            min_s,
            max_s,
            sort_key,
            page,
            self.log,
            strict_mode,
        )

        if not strict_mode:
            return items_list, total_count

        # Strict Filter 7%
        filtered = []
        target_lang = resolve_stack_primary_language(items[0]) if items else "Any"
        for item in items_list:
            try:
                langs = api_get_languages(self.token, item['owner']['login'], item['name'])
                if not langs:
                    continue
                total = sum(langs.values())
                if total == 0:
                    continue
                foreign = 0
                for l, s in langs.items():
                    if l != target_lang and l not in WHITELIST_LANGS:
                        foreign += s
                if (foreign / total) <= 0.07:
                    filtered.append(item)
            except:
                pass

        return filtered, total_count

    def _format_repo_activity_stats(self, size_str, full_name):
        cached = self.repo_activity_cache.get(full_name, {})
        commit_count = cached.get("commits")
        contributor_count = cached.get("contributors")
        commits_txt = f"{commit_count:,}" if isinstance(commit_count, int) else "..."
        devs_txt = f"{contributor_count:,}" if isinstance(contributor_count, int) else "..."
        return f"🧱 Commits: {commits_txt}  |  👥 Devs: {devs_txt}  |  💾 {size_str}"

    def _queue_repo_activity_fetch(self, item, stats_label, size_str):
        full_name = item.get("full_name")
        if not full_name:
            return

        if full_name in self.repo_activity_cache:
            self.after(0, lambda: self._refresh_repo_activity_label(stats_label, size_str, full_name))
            return

        if full_name in self.repo_activity_pending:
            return

        owner = item.get("owner", {}).get("login")
        repo = item.get("name")
        if not owner or not repo:
            return

        self.repo_activity_pending.add(full_name)
        threading.Thread(
            target=self._repo_activity_fetch_thread,
            args=(owner, repo, full_name, stats_label, size_str),
            daemon=True,
        ).start()

    def _refresh_repo_activity_label(self, stats_label, size_str, full_name):
        try:
            if stats_label and stats_label.winfo_exists():
                stats_label.configure(text=self._format_repo_activity_stats(size_str, full_name))
        except Exception:
            pass

    def _repo_activity_fetch_thread(self, owner, repo, full_name, stats_label, size_str):
        try:
            commit_count = api_get_repo_commit_count(self.token, owner, repo)
            contributor_count = api_get_repo_contributors_count(self.token, owner, repo)
            self.repo_activity_cache[full_name] = {
                "commits": commit_count,
                "contributors": contributor_count,
            }
        except Exception as e:
            self.log(f"⚠️ Repo stats fetch failed for {full_name}: {e}")
        finally:
            self.repo_activity_pending.discard(full_name)
            self.after(0, lambda: self._refresh_repo_activity_label(stats_label, size_str, full_name))

    def render_cloner_results(self, items):
        self.lbl_cloner_page.configure(text=f"Page {self.cloner_page} of {self.cloner_max_pages}")
        for w in self.cloner_results_frame.winfo_children(): w.destroy()
        
        if not items:
            ctk.CTkLabel(self.cloner_results_frame, text="No matches found.").pack()
            return

        for item in items:
            # --- Statistics ---
            size_kb = item.get('size', 0)
            size_str = format_size(size_kb)
            lang = item.get('language', 'default')
            senior_days = calculate_senior_days(size_kb, lang)

            # --- Is Favorite? ---
            is_fav = any(x['full_name'] == item['full_name'] for x in self.favorites)
            fav_btn_text = "❤️" if is_fav else "🤍"
            fav_btn_color = "#FFD700" if is_fav else "gray"

            # --- CARD UI ---
            f = ctk.CTkFrame(self.cloner_results_frame, fg_color="white")
            f.pack(fill="x", pady=5, padx=5)
            f.grid_columnconfigure(0, weight=1)
            f.grid_columnconfigure(1, weight=0)

            # Left (Info)
            f_left = ctk.CTkFrame(f, fg_color="transparent")
            f_left.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

            btn_title = ctk.CTkButton(f_left, text=f"◆ {item['full_name']} (⭐ {item['stargazers_count']})", 
                                      font=("Arial", 13, "bold"), text_color="black", fg_color="transparent", 
                                      anchor="w", hover_color="#E0E0E0", command=lambda i=item: RepoDossier(self, i, self.token))
            btn_title.pack(fill="x")

            desc = (item['description'] or "")[:90] + "..."
            ctk.CTkLabel(f_left, text=desc, text_color="#555", anchor="w", font=("Arial", 11)).pack(fill="x")
            
            # Activity stats: commits + contributors
            full_name = item.get("full_name", "")
            stats_txt = self._format_repo_activity_stats(size_str, full_name)
            lbl_stats = ctk.CTkLabel(f_left, text=stats_txt, text_color="gray", anchor="w", font=("Arial", 11))
            lbl_stats.pack(fill="x", pady=(2,0))
            self._queue_repo_activity_fetch(item, lbl_stats, size_str)

            # Right (Buttons)
            f_right = ctk.CTkFrame(f, fg_color="transparent")
            f_right.grid(row=0, column=1, sticky="e", padx=10, pady=5)

            # SAVE BUTTON
            ctk.CTkButton(f_right, text=fav_btn_text, width=40, fg_color="transparent", text_color="red", border_width=1, border_color="red",
                          command=lambda i=item: self.toggle_favorite(i)).pack(side="left", padx=2)

            # LINK BUTTON
            ctk.CTkButton(f_right, text="Link", width=50, fg_color="gray", command=lambda u=item['html_url']: webbrowser.open(u)).pack(side="left", padx=2)
            
            # --- НОВА КНОПКА TEAM ---
            ctk.CTkButton(f_right, text="Team 👥", width=70, fg_color="#5856D6", # Фіолетовий колір
                          command=lambda i=item: self.send_to_team_mode(i)).pack(side="left", padx=2)
            # ------------------------

            # SELECT BUTTON
            ctk.CTkButton(f_right, text="Select", width=70, command=lambda i=item, d=senior_days: self.select_donor(i, d)).pack(side="left")

    def select_donor(self, item, senior_days):
        self.selected_donor = item
        self.selected_senior_days = senior_days
        clean_name = item['name']
        for k, synonyms in SMART_SYNONYMS.items():
            if k in clean_name.lower(): 
                clean_name = clean_name.lower().replace(k, random.choice(synonyms))
                break
        self.cloner_target_name.delete(0, "end")
        self.cloner_target_name.insert(0, clean_name)
        self._copy_about_to_all_desc_fields(item, force=True)
        self.check_schedule_feasibility()

        try:
            self.slider_time.set(1.0)
            self._on_slider_change(1.0)
        except:
            pass

        messagebox.showinfo("Selected", f"Selected: {item['full_name']}\nTime Auto-Adjusted!")

    def send_to_team_mode(self, item):
        # 1. Розрахунок базового часу для проекту
        size_kb = item.get('size', 0)
        lang = item.get('language', 'default')
        senior_days = calculate_senior_days(size_kb, lang)

        # 2. Збереження даних у внутрішні змінні
        self.selected_donor = item
        self.selected_senior_days = senior_days
        
        # 3. Генерація розумної назви
        clean_name = item['name']
        for k, synonyms in SMART_SYNONYMS.items():
            if k in clean_name.lower(): 
                clean_name = clean_name.lower().replace(k, random.choice(synonyms))
                break
        
        # 4. Оновлення інтерфейсу у вкладці Team Mode
        # (перемальовуємо, щоб підтягнути нові donor_txt/donor_url)
        try:
            self.build_collab_tab()
        except Exception as e:
            print(f"Error refreshing Team UI: {e}")

        # Оновлюємо поле "Project Name" (Права колонка)
        if hasattr(self, 'entry_team_name'):
            self.entry_team_name.delete(0, "end")
            self.entry_team_name.insert(0, clean_name)
        self._copy_about_to_all_desc_fields(item, force=True)

        # 5. Оновлення дат через слайдер
        try:
            if hasattr(self, 'slider_team_pace'):
                self.slider_team_pace.set(1.0)
                self._on_team_slider_change(1.0)
        except Exception as e:
            print(f"Error syncing team dates: {e}")

        # 6. Переключення на вкладку
        try:
            for tab_name in ["Team Mode 👥", "Team Mode", "Collab"]:
                try:
                    self.tabview.set(tab_name)
                    break
                except:
                    continue
        except:
            pass

        self.log(f"🚀 Team Mode: Loaded '{item['full_name']}'")

    def _get_estimated_days(self):
        """Отримує базову оцінку часу від TimeArchitect"""
        if not getattr(self, 'time_architect', None):
            self.time_architect = TimeArchitect()
        if not getattr(self, 'selected_donor', None):
            return 30
        
        size = self.selected_donor.get('size', 0)
        est_commits = size / 2
        
        return self.time_architect.estimate_effort_days(size, est_commits)

    def _on_slider_change(self, val):
        """Слайдер рухає дати"""
        self._block_manual_update = True
        
        try:
            factor = float(val)
            base_days = self._get_estimated_days()
            target_days = max(1, int(base_days / factor))
            
            text = f"Pace: {factor:.1f}x"
            if factor > 1.5: text += " (Turbo 🔥)"
            elif factor < 0.7: text += " (Relaxed ☕)"
            self.lbl_speed.configure(text=text)
            
            self._apply_days_to_calendar(target_days)
        finally:
            self.after(100, lambda: setattr(self, '_block_manual_update', False))

    def _on_team_slider_change(self, val):
        """Логіка зміни дат для Team Mode при русі слайдера"""
        if not getattr(self, 'selected_donor', None):
            return

        try:
            base_days = getattr(self, 'selected_senior_days', 30)
            if base_days < 1:
                base_days = 30

            factor = float(val)
            target_days = max(1, int(base_days / factor))
            
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=target_days)

            if hasattr(self, 'team_start') and hasattr(self, 'team_end'):
                self.team_end.set_date(end_date)
                self.team_start.set_date(start_date)
        except Exception as e:
            print(f"Slider Error: {e}")

    def _apply_days_to_calendar(self, days):
        anchor = self.var_anchor.get() if hasattr(self, 'var_anchor') else 'end'
        
        if anchor == "end":
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=days)
            
            self.set_date_val(self.cloner_end, end_date)
            self.set_date_val(self.cloner_start, start_date)
            
        else:
            start_date = self.get_date_val(self.cloner_start)
            if not start_date: start_date = datetime.date.today()
            end_date = start_date + datetime.timedelta(days=days)
            
            if end_date > datetime.date.today():
                end_date = datetime.date.today()
            
            self.set_date_val(self.cloner_start, start_date)
            self.set_date_val(self.cloner_end, end_date)
            
        self._check_density()

    def _on_manual_date_change(self):
        """Дати рухають слайдер (Мануальний режим - головний)"""
        if getattr(self, '_block_manual_update', False):
            return

        s = self.get_date_val(self.cloner_start)
        e = self.get_date_val(self.cloner_end)
        if not s or not e:
            return

        diff = (e - s).days
        if diff <= 0:
            self.lbl_speed.configure(text="Invalid Dates (End < Start)", text_color="red")
            return

        base_days = self._get_estimated_days()
        new_factor = base_days / diff
        new_factor = max(0.1, min(3.0, new_factor))
        
        self.slider_time.set(new_factor)
        self.lbl_speed.configure(text=f"Pace: {new_factor:.1f}x (Manual Override)", text_color="black")
        
        self._check_time_travel()
        self._check_density()

    def _check_time_travel(self):
        """Перевіряє, чи не вибрали ми дату раніше створення донора"""
        if not hasattr(self, 'lbl_time_travel'):
            return

        donor = getattr(self, 'selected_donor', None)
        if not donor:
            return
        
        start_date = self.get_date_val(self.cloner_start)
        if not start_date:
            return

        try:
            donor_created = datetime.datetime.strptime(donor['created_at'][:10], "%Y-%m-%d").date()
            if start_date < donor_created:
                diff = (donor_created - start_date).days
                self.lbl_time_travel.configure(text=f"⚠️ Time Travel Warning: {diff} days before original repo created!")
            else:
                self.lbl_time_travel.configure(text="")
        except:
            pass

    def _recalc_dates(self):
        """Коли перемкнули Radio Button Anchors"""
        self._on_slider_change(self.slider_time.get())

    def _check_density(self):
        """Перевірка щільності (7B) і оновлення кольору"""
        if not getattr(self, 'time_architect', None):
            self.time_architect = TimeArchitect()

        s = self.get_date_val(self.cloner_start)
        e = self.get_date_val(self.cloner_end)
        if not s or not e: return
        
        user_days = (e - s).days
        donor = getattr(self, 'selected_donor', None) or {}
        size = donor.get('size', 1000)
        commits = size / 2
        
        verdict = self.time_architect.analyze_density(commits, user_days)
        
        if not hasattr(self, 'lbl_density_warn'):
            return
        
        if verdict == 'dense':
            self.lbl_density_warn.configure(text="✅ Density: Perfect (Professional)", fg_color="#E8F5E9", text_color="#2E7D32")
        elif verdict == 'ok':
            self.lbl_density_warn.configure(text="⚠️ Density: Sparse (May look weak)", fg_color="#FFF3E0", text_color="#EF6C00")
        elif verdict == 'sparse':
            self.lbl_density_warn.configure(text="🛑 Density: Too Low (Adding Noise Required!)", fg_color="#FFEBEE", text_color="#C62828")
        elif verdict == 'impossible':
            self.lbl_density_warn.configure(text="⛔ IMPOSSIBLE (Too fast/Negative)", fg_color="black", text_color="red")

    def check_schedule_feasibility(self):
        if not self.selected_senior_days: return
        start = self.get_date_val(self.cloner_start)
        end = self.get_date_val(self.cloner_end)
        if not start or not end: return
        user_days = (end - start).days
        if user_days <= 0: return
        if user_days < (self.selected_senior_days * 0.5):
            rec_end = start + datetime.timedelta(days=self.selected_senior_days)
            msg = f"⚠️ Warning!\nA Senior Dev needs ~{self.selected_senior_days} days for this.\nYou selected {user_days} days.\n\nRecommended End Date: {rec_end}"
            if messagebox.askyesno("Smart Schedule", msg + "\n\nUpdate End Date to match Senior pace?"):
                self.set_date_val(self.cloner_end, rec_end)

    def start_cloner(self):
        if not getattr(self, 'selected_donor', None):
            return messagebox.showerror("Error", "Select project first!")

        config = {
            "donor": self.selected_donor,
            "name": self.cloner_target_name.get(),
            "desc": self._resolve_repo_desc(self.cloner_target_desc.get(), self.selected_donor),
            "is_private": self.cloner_private.get(),
            "start": self.get_date_val(self.cloner_start),
            "end": self.get_date_val(self.cloner_end),
            "persona": self.combo_persona.get(),
            "email": self.gen_email.get(),
            "ghost_issues": self.chk_ghost_issues.get(),
            "realistic_stats": self.chk_realistic_stats.get(),
            "translate": self.chk_translate.get(),
            "license_swap": self.chk_license_swap.get(),
        }

        if config["start"] and config["end"] and config["start"] > config["end"]:
            return messagebox.showerror("Error", "Invalid dates")

        self.stop_cloner_flag = False

        self.btn_cloner_run.configure(
            text="🟥 CANCEL OPERATION",
            fg_color="red",
            hover_color="#8B0000",
            command=self.cancel_cloner,
        )
        self._update_cloner_ui(0.01, "⏳ Initializing clone job...")

        threading.Thread(target=self.run_cloner_logic_safe, args=(config,), daemon=True).start()

    def _analyze_authors_and_map(self, tmp_path, roster):
        """
        Аналізує оригінальних авторів і прив'язує їх до учасників нашої команди
        на основі їхніх ролей (Extension analysis).
        """
        self.log("🕵️ Analyzing original contributors...")
        
        cmd = ["git", "log", "--pretty=format:%an", "--name-only"]
        try:
            result = subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True, errors="replace")
        except:
            return {}

        author_stats = {}
        current_author = None
        
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            
            if "/" not in line and "." not in line and " " in line:
                current_author = line
                if current_author not in author_stats:
                    author_stats[current_author] = {"total": 0}
            elif current_author:
                ext = os.path.splitext(line)[1].lower()
                if not ext:
                    continue
                
                stats = author_stats[current_author]
                stats[ext] = stats.get(ext, 0) + 1
                stats["total"] += 1

        identity_map = {}
        bots = ["dependabot", "renovate", "snyk", "github-actions", "bot", "auto"]
        
        for auth, stats in author_stats.items():
            if any(b in auth.lower() for b in bots):
                identity_map[auth] = 0
                continue
                
            top_ext = sorted([k for k in stats if k != "total"], key=lambda k: stats[k], reverse=True)
            if not top_ext:
                identity_map[auth] = 0
                continue
            
            favorite_ext = top_ext[0]
            
            candidates = []
            for idx, member in enumerate(roster):
                if favorite_ext in member.get("skills", []):
                    candidates.append(idx)
            
            if candidates:
                identity_map[auth] = random.choice(candidates)
            else:
                identity_map[auth] = 0
                
        self.log(f"🧠 Identity Map created: {len(identity_map)} original authors mapped.")
        return identity_map

    def run_agency_logic(self, cfg):
        tmp_source = tempfile.mkdtemp()
        tmp_target = tempfile.mkdtemp()
        roster = cfg['roster']
        
        try:
            self.log(f"🚀 INITIALIZING AGENCY: {len(roster)} members ready.")
            self.log(f"🎯 Target: {cfg['name']} | Privacy: {cfg['is_private']}")
            
            if getattr(self, "stop_cloner_flag", False): raise Exception("User stopped before start")
            
            repo_url = create_github_repo(self.username, self.token, cfg['name'], cfg['is_private'], cfg['desc'])
            self.log(f"✅ Repository created: {repo_url}")
            
            self.log("🤝 Sending invites...")
            for member in roster:
                if member['token'] == self.token: continue
                try:
                    api_add_collaborator(self.token, self.username, cfg['name'], member['name'])
                    time.sleep(2)
                    invites = api_list_repository_invitations(member['token'])
                    target_repo = f"{self.username}/{cfg['name']}".lower()
                    invite_id = None
                    for inv in invites:
                        if inv.get('repository', {}).get('full_name', '').lower() == target_repo:
                            invite_id = inv['id']
                            break
                    if invite_id:
                        api_accept_repository_invitation(member['token'], invite_id)
                        self.log(f"   ✅ {member['name']} is now a collaborator!")
                    else:
                        self.log(f"   ⚠️ Invite for {member['name']} not found (Auto-accepted or Delay?)")
                except Exception as e:
                    self.log(f"   ❌ Invite Error for {member['name']}: {e}")

            self.log("📥 Cloning source repository (this takes time)...")
            subprocess.run(["git", "clone", cfg['donor']['clone_url'], "."], cwd=tmp_source, check=True, stderr=subprocess.DEVNULL)
            
            lead = roster[0]
            auth_url = repo_url.replace("https://", f"https://{lead['token']}@")
            subprocess.run(["git", "init"], cwd=tmp_target)
            subprocess.run(["git", "remote", "add", "origin", auth_url], cwd=tmp_target)
            subprocess.run(["git", "checkout", "-b", "main"], cwd=tmp_target)

            self.log("🧐 Analyzing commit history...")
            log_cmd = ["git", "log", "--reverse", "--pretty=format:%H|%ct|%an|%s"]
            result = subprocess.run(log_cmd, cwd=tmp_source, capture_output=True, text=True, errors="replace")
            raw_commits = []
            for line in result.stdout.splitlines():
                p = line.split("|", 3)
                if len(p)==4: raw_commits.append({"h": p[0], "t": int(p[1]), "a": p[2], "m": p[3]})

            total_commits = len(raw_commits)
            self.log(f"📊 Found {total_commits} commits to process.")

            identity_map = {}
            if cfg.get("use_identity_map"):
                self.log("🎭 Building Identity Map...")
                identity_map = self._analyze_authors_and_map(tmp_source, roster)

            ts_start = time.mktime(cfg['start'].timetuple())
            ts_end = time.mktime(cfg['end'].timetuple())
            total_dur = max(1, ts_end - ts_start)
            orig_start = raw_commits[0]['t']
            orig_dur = max(1, raw_commits[-1]['t'] - orig_start)
            
            seed_date = self._get_seed_date(cfg['start'])
            init_dt = datetime.datetime.combine(seed_date, datetime.time(9,0))
            self._git_commit(tmp_target, "Initial commit", init_dt, cfg['persona'], lead, repo_url)

            self.log("🎬 STARTING REWRITE PROCESS...")
            
            for i, c in enumerate(raw_commits):
                if getattr(self, "stop_cloner_flag", False): 
                    self.log("🛑 Process STOPPED by user request.")
                    break
                
                subprocess.run(["git", "checkout", "-f", c['h']], cwd=tmp_source, stderr=subprocess.DEVNULL)
                sync_directories(tmp_source, tmp_target)
                
                status_res = subprocess.run(["git", "status", "--porcelain"], cwd=tmp_target, capture_output=True, text=True)
                changed_files = [line[3:].strip().strip('"') for line in status_res.stdout.splitlines() if line.strip()]
                
                if not changed_files: continue

                progress = (c['t'] - orig_start) / orig_dur
                base_ts = ts_start + (progress * total_dur)
                base_dt = datetime.datetime.fromtimestamp(base_ts)

                file_groups = {} 
                for fpath in changed_files:
                    winner_idx = self._determine_file_owner(fpath, roster, c['a'], identity_map)
                    if winner_idx not in file_groups: file_groups[winner_idx] = []
                    file_groups[winner_idx].append(fpath)

                offset_mins = 0
                for member_idx, files in file_groups.items():
                    if getattr(self, "stop_cloner_flag", False): break
                    
                    member = roster[member_idx]
                    commit_dt = base_dt + datetime.timedelta(minutes=offset_mins)
                    offset_mins += random.randint(5, 30)

                    raw_msg = c['m']
                    clean_msg = self._sanitize_message(raw_msg)
                    
                    msg = clean_msg 
                    if cfg.get("ai_rewrite") and len(files) < 10:
                        try:
                            pass 
                        except: pass

                    for f in files: subprocess.run(["git", "add", f], cwd=tmp_target, stderr=subprocess.DEVNULL)
                    self._git_commit(tmp_target, msg, commit_dt, cfg['persona'], member, repo_url)

                if i % 10 == 0 or i == total_commits - 1:
                    perc = (i + 1) / total_commits
                    self.log(f"⏳ Processing: {int(perc*100)}% ({i+1}/{total_commits})")
                    self.after(0, lambda p=perc: self._update_cloner_ui(p, f"Agency: {int(p*100)}%"))

            if not getattr(self, "stop_cloner_flag", False):
                self.log("🚀 Pushing to GitHub...")
                subprocess.run(["git", "push", "-u", "origin", "main"], cwd=tmp_target, stderr=subprocess.DEVNULL)
                self.log("✅ DONE! Project successfully created.")
                messagebox.showinfo("Done", "Agency Simulation Complete! 🥂")
            else:
                self.log("⚠️ Operation aborted partially.")

        except Exception as e:
            self.log(f"❌ CRITICAL ERROR: {e}")
            print(e)
        finally:
            self.log("🧹 Cleaning up temp files...")
            try:
                shutil.rmtree(tmp_source, ignore_errors=True)
                shutil.rmtree(tmp_target, ignore_errors=True)
            except: pass
            
            self.after(0, lambda: self.btn_team_run.configure(text="🚀 LAUNCH AGENCY", fg_color=PALETTE[4], state="normal", command=self.start_agency_cloning))

    def _sanitize_message(self, msg):
        """Вирізає посилання та згадки оригінальних репозиторіїв"""
        if not msg: return "Update code"
        
        msg = re.sub(r'https?://\S+', 'external source', msg)
        msg = re.sub(r'git@\S+', 'external source', msg)
        
        if "Merge branch" in msg and "of external source" in msg:
            msg = msg.split("of external source")[0].strip()
            
        return msg.strip()

    def _git_commit(self, cwd, msg, dt, persona, member, repo_url_template):
        msg = self._sanitize_message(msg)
        subprocess.run(["git", "config", "user.name", member['name']], cwd=cwd)
        mem_email = member.get('email') or f"{member['name'].lower().replace(' ', '')}@agency.test"
        subprocess.run(["git", "config", "user.email", mem_email], cwd=cwd)

        mem_url = repo_url_template.replace("https://", f"https://{member['token']}@")
        subprocess.run(["git", "remote", "set-url", "origin", mem_url], cwd=cwd)

        t_str = self.time_architect.get_commit_time(dt, persona)
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = t_str

        subprocess.run(["git", "commit", "-m", msg], cwd=cwd, env=env, stderr=subprocess.DEVNULL)

    def _ask_user_unknown_file(self, filename):
        """Зупиняє потік і питає юзера через змінну"""
        self.unknown_file_decision = None
        
        self.after(0, lambda: self._show_unknown_dialog(filename))
        
        while self.unknown_file_decision is None:
            if getattr(self, "stop_cloner_flag", False):
                return None
            time.sleep(0.5)
            
        return self.unknown_file_decision

    def _show_unknown_dialog(self, filename):
        dialog = ctk.CTkToplevel(self)
        dialog.title("❓ Unknown File Type")
        dialog.geometry("400x300")
        
        ctk.CTkLabel(dialog, text=f"Who should take ownership of:\n{filename}?", font=("Arial", 14, "bold")).pack(pady=20)
        
        def _pick(idx):
            self.unknown_file_decision = idx
            dialog.destroy()
            
        scroll = ctk.CTkScrollableFrame(dialog)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        for idx, member in enumerate(self.team_roster):
            ctk.CTkButton(scroll, text=f"👤 {member['name']}", command=lambda i=idx: _pick(i)).pack(fill="x", pady=2)
        
        def _cancel_all():
            self.stop_cloner_flag = True
            dialog.destroy()

        ctk.CTkButton(dialog, text="🛑 Cancel All", fg_color="red", command=_cancel_all).pack(pady=5)

    def run_cloner_logic_safe(self, cfg):
        """Безпечна логіка, яка бере дані з конфіга, а не з UI"""
        tmp_source = tempfile.mkdtemp()
        tmp_target = tempfile.mkdtemp()
        repo_created = False

        donor = cfg.get('donor')
        name = cfg.get('name')
        desc = cfg.get('desc')
        is_private = cfg.get('is_private')
        start = cfg.get('start')
        end = cfg.get('end')
        persona = cfg.get('persona')
        email = cfg.get('email')
        actors = cfg.get('actors')
        ghost_issues = bool(cfg.get('ghost_issues', False))
        realistic_stats = bool(cfg.get('realistic_stats', False))

        if not getattr(self, 'time_architect', None):
            self.time_architect = TimeArchitect()

        if AUDIO_AVAILABLE:
            try:
                if os.path.exists(SOUND_EAGLE): pygame.mixer.Sound(SOUND_EAGLE).play()
                if os.path.exists(SOUND_MUSIC):
                    pygame.mixer.music.load(SOUND_MUSIC)
                    pygame.mixer.music.play(-1)
            except:
                pass

        try:
            if getattr(self, "stop_cloner_flag", False):
                self._handle_abort_dialog(name, tmp_source, tmp_target)
                return

            self.log(f"🔥 Starting ULTIMATE MIRROR of {donor['full_name']}...")
            self.after(0, lambda: self._update_cloner_ui(0.05, "🛠 Step 1/5: Creating target repository..."))

            repo_url = create_github_repo(self.username, self.token, name, is_private, desc)
            repo_created = True
            auth_url = repo_url.replace("https://", f"https://{self.token}@")

            self.log("Step 1: Deep Cloning Source...")
            self.after(0, lambda: self._update_cloner_ui(0.12, "📥 Step 2/5: Deep cloning source repository..."))
            subprocess.run(["git", "clone", donor['clone_url'], "."], cwd=tmp_source, check=True, stderr=subprocess.DEVNULL)

            self.after(0, lambda: self._update_cloner_ui(0.2, "🧾 Step 3/5: Reading commit history..."))
            log_cmd = ["git", "log", "--reverse", "--pretty=format:%H|%ct|%P|%s"]
            result = subprocess.run(log_cmd, cwd=tmp_source, capture_output=True, text=True, encoding="utf-8", errors="replace")

            commits = []
            for line in result.stdout.splitlines():
                parts = line.split("|", 3)
                if len(parts) == 4:
                    commits.append({
                        "h": parts[0],
                        "t": int(parts[1]),
                        "parents": parts[2].split(),
                        "m": parts[3],
                    })

            if not commits:
                raise Exception("No commits found!")

            subprocess.run(["git", "init"], cwd=tmp_target)
            subprocess.run(["git", "config", "user.email", email], cwd=tmp_target)
            git_user_name = self._read_auth_file().get("git_author", self.username)
            subprocess.run(["git", "config", "user.name", git_user_name], cwd=tmp_target)
            subprocess.run(["git", "checkout", "-b", "main"], cwd=tmp_target)
            subprocess.run(["git", "remote", "add", "origin", auth_url], cwd=tmp_target)

            def apply_actor(actor):
                if not actor:
                    subprocess.run(["git", "config", "user.email", email], cwd=tmp_target)
                    git_user_name = self._read_auth_file().get("git_author", self.username)
                    subprocess.run(["git", "config", "user.name", git_user_name], cwd=tmp_target)
                    subprocess.run(["git", "remote", "set-url", "origin", auth_url], cwd=tmp_target)
                    return

                a_user = actor.get("username") or actor.get("name") or self.username
                a_token = actor.get("token")
                subprocess.run(["git", "config", "user.name", a_user], cwd=tmp_target)
                subprocess.run(["git", "config", "user.email", email], cwd=tmp_target)
                if a_token:
                    a_auth_url = repo_url.replace("https://", f"https://{a_token}@")
                    subprocess.run(["git", "remote", "set-url", "origin", a_auth_url], cwd=tmp_target)

            active_actors = None
            if isinstance(actors, list) and actors:
                active_actors = [a for a in actors if isinstance(a, dict)]
            apply_actor(active_actors[0] if active_actors else None)

            seed_date = self._get_seed_date(start)
            init_dt = datetime.datetime.combine(seed_date, datetime.time())
            init_t_str = self.time_architect.get_commit_time(init_dt, persona)
            init_env = os.environ.copy()
            init_env["GIT_AUTHOR_DATE"] = init_env["GIT_COMMITTER_DATE"] = init_t_str
            subprocess.run(["git", "commit", "--allow-empty", "-m", "Initial commit"], cwd=tmp_target, env=init_env, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "push", "-u", "origin", "main"], cwd=tmp_target, stderr=subprocess.DEVNULL)

            orig_start = commits[0]['t']
            orig_duration = max(1, commits[-1]['t'] - orig_start)
            ts_start = time.mktime(start.timetuple())
            ts_end = time.mktime(end.timetuple())
            target_duration = max(1, ts_end - ts_start)

            density_status = self.time_architect.analyze_density(len(commits), (end - start).days)
            force_split = (density_status == 'sparse')

            total_commits = len(commits)
            pr_chance = 0.10
            issue_chance = 0.05
            max_pr_events = max(1, min(12, total_commits // 20))
            max_issue_events = max(1, min(8, total_commits // 30))
            pr_done = 0
            issue_done = 0
            legacy_issue_chance = 0.03
            legacy_max_issue_events = max(1, min(6, total_commits // 40))

            if realistic_stats:
                self.log(
                    f"📈 Realistic Stats mode ON | PR chance={pr_chance:.0%}, Issue chance={issue_chance:.0%}, "
                    f"PR cap={max_pr_events}, Issue cap={max_issue_events}"
                )
            elif ghost_issues:
                self.log(
                    f"👻 Ghost Issues mode ON | Issue chance={legacy_issue_chance:.0%}, cap={legacy_max_issue_events}"
                )

            loop_started_at = time.time()
            self.after(0, lambda tc=total_commits: self._update_cloner_ui(0.22, f"🚀 Step 4/5: Rewriting history (0/{tc})..."))
            for i, c in enumerate(commits):
                if getattr(self, "stop_cloner_flag", False):
                    self._handle_abort_dialog(name, tmp_source, tmp_target)
                    return

                actor = None
                if active_actors:
                    actor = active_actors[i % len(active_actors)]
                apply_actor(actor)

                subprocess.run(["git", "checkout", "-f", c['h']], cwd=tmp_source, stderr=subprocess.DEVNULL)
                sync_directories(tmp_source, tmp_target)

                progress = (c['t'] - orig_start) / orig_duration
                new_ts = ts_start + (progress * target_duration)
                base_date_obj = datetime.datetime.fromtimestamp(new_ts)

                is_merge = len(c.get('parents') or []) > 1

                files = self._collect_changed_files(tmp_target)
                clean_msg = re.sub(r'Co-authored-by:.*', '', c['m'], flags=re.IGNORECASE).strip() or "Update code"

                pr_route_used = False
                if (
                    realistic_stats
                    and not is_merge
                    and files
                    and pr_done < max_pr_events
                    and random.random() < pr_chance
                ):
                    pr_route_used = self._try_commit_via_pr_flow(
                        tmp_target=tmp_target,
                        repo_name=name,
                        clean_msg=clean_msg,
                        t_str=self.time_architect.get_commit_time(base_date_obj, persona),
                        commit_index=i,
                        active_actors=active_actors,
                        current_actor=actor,
                    )

                    if pr_route_used:
                        pr_done += 1
                        self.log(f"🔀 PR flow used for commit {i + 1}/{total_commits} (PR events: {pr_done}/{max_pr_events})")

                        if self._maybe_emit_realistic_issue(
                            repo_name=name,
                            enabled=realistic_stats,
                            issue_done=issue_done,
                            max_issue_events=max_issue_events,
                            issue_chance=issue_chance,
                        ):
                            issue_done += 1

                        if i % 3 == 0 or i == total_commits - 1:
                            done = i + 1
                            perc = done / total_commits
                            elapsed = max(0.001, time.time() - loop_started_at)
                            rate = done / elapsed
                            eta_seconds = (total_commits - done) / rate if rate > 0 else None
                            overall_p = 0.22 + (0.68 * perc)
                            status_text = (
                                f"🚀 Step 4/5: Rewriting history {done}/{total_commits} ({int(perc*100)}%)"
                                f" | ⏳ ETA {self._format_eta(eta_seconds)}"
                            )
                            try:
                                self.after(0, lambda p=overall_p, t=status_text: self._update_cloner_ui(p, t))
                            except:
                                pass
                        continue

                    self.log("⚠️ PR flow fallback to direct commit path.")
                    sync_directories(tmp_source, tmp_target)
                    files = self._collect_changed_files(tmp_target)

                should_split = False
                chunks = [files]
                if not is_merge and files:
                    if len(files) > 10:
                        should_split = False
                    elif force_split or (len(files) > 1):
                        should_split = True

                if should_split:
                    n_chunks = min(3, len(files))
                    chunk_size = math.ceil(len(files) / n_chunks)
                    chunks = [files[j:j + chunk_size] for j in range(0, len(files), chunk_size)]

                    try:
                        ai_msgs = self._generate_batch_commit_messages(clean_msg, chunks)
                    except:
                        ai_msgs = [clean_msg] * len(chunks)
                else:
                    ai_msgs = [clean_msg]

                for idx, chunk in enumerate(chunks):
                    if should_split:
                        for f in chunk:
                            subprocess.run(["git", "add", f], cwd=tmp_target, stderr=subprocess.DEVNULL)
                    else:
                        subprocess.run(["git", "add", "."], cwd=tmp_target, stderr=subprocess.DEVNULL)

                    offset = idx * 2
                    commit_dt = base_date_obj + datetime.timedelta(minutes=offset)
                    t_str = self.time_architect.get_commit_time(commit_dt, persona)
                    env = os.environ.copy()
                    env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = t_str

                    msg = ai_msgs[idx] if idx < len(ai_msgs) else ai_msgs[0]
                    subprocess.run(["git", "commit", "--allow-empty", "-m", msg], cwd=tmp_target, env=env, stderr=subprocess.DEVNULL)

                issue_enabled = realistic_stats or ghost_issues
                issue_cap = max_issue_events if realistic_stats else legacy_max_issue_events
                issue_prob = issue_chance if realistic_stats else legacy_issue_chance
                if self._maybe_emit_realistic_issue(
                    repo_name=name,
                    enabled=issue_enabled,
                    issue_done=issue_done,
                    max_issue_events=issue_cap,
                    issue_chance=issue_prob,
                ):
                    issue_done += 1

                if i % 3 == 0 or i == total_commits - 1:
                    done = i + 1
                    perc = done / total_commits
                    elapsed = max(0.001, time.time() - loop_started_at)
                    rate = done / elapsed
                    eta_seconds = (total_commits - done) / rate if rate > 0 else None
                    overall_p = 0.22 + (0.68 * perc)
                    status_text = (
                        f"🚀 Step 4/5: Rewriting history {done}/{total_commits} ({int(perc*100)}%)"
                        f" | ⏳ ETA {self._format_eta(eta_seconds)}"
                    )
                    try:
                        self.after(0, lambda p=overall_p, t=status_text: self._update_cloner_ui(p, t))
                    except:
                        pass

            self.log("🔄 Pushing final history...")
            self.after(0, lambda: self._update_cloner_ui(0.93, "📤 Step 5/5: Pushing rewritten history to GitHub..."))
            subprocess.run(["git", "push", "origin", "main"], cwd=tmp_target, stderr=subprocess.DEVNULL)
            self.refresh_manager_repos(name)
            self.after(0, lambda: self._update_cloner_ui(1.0, "✅ Complete: mirror created successfully"))
            messagebox.showinfo("Success", "ULTIMATE Mirror Complete!\nHistory successfully rewritten.")

        except Exception as e:
            self.log(f"❌ Error: {e}")
            self.after(0, lambda: self._update_cloner_ui(0, f"❌ Error: {e}"))
            if repo_created:
                self._handle_abort_dialog(name, tmp_source, tmp_target)
        finally:
            if AUDIO_AVAILABLE:
                try:
                    pygame.mixer.music.stop()
                except:
                    pass
            self.after(0, lambda: self.btn_cloner_run.configure(
                text="🚀 ACTIVATE GOD MODE", fg_color=PALETTE[4], state="normal", command=self.start_cloner
            ))
            try:
                shutil.rmtree(tmp_source, ignore_errors=True)
                shutil.rmtree(tmp_target, ignore_errors=True)
            except:
                pass

    def perform_fast_clone(self):
        """Клонує репозиторій БЕЗ очікування AI і БЕЗ замін імен"""
        donor = getattr(self, 'selected_donor', None)
        if not donor:
            self.log("❌ No repository selected!")
            return

        dest_parent = tk.filedialog.askdirectory()
        if not dest_parent:
            return

        self.log("⚡️ Starting FAST CLONE (Raw mode)...")
        threading.Thread(target=self._fast_clone_worker, args=(dest_parent, donor), daemon=True).start()

    def _fast_clone_worker(self, dest_parent, donor):
        try:
            repo_url = donor.get('clone_url')
            if not repo_url:
                self.log("❌ Fast Clone Failed: Missing clone_url")
                return

            if self.token and repo_url.startswith("https://"):
                repo_url = repo_url.replace("https://", f"https://{self.token}@")

            repo_folder = donor.get('name') or donor.get('full_name', 'repo').split('/')[-1]
            dest_path = os.path.join(dest_parent, repo_folder)

            subprocess.run(["git", "clone", repo_url, dest_path], check=True)
            self.log(f"✅ Fast Clone Complete! Saved to: {dest_path}")

        except Exception as e:
            self.log(f"❌ Fast Clone Failed: {e}")

    def cancel_cloner(self):
        self.stop_cloner_flag = True

        if hasattr(self, "btn_cloner_run"):
            self.btn_cloner_run.configure(text="🚫 STOPPING (Wait for git)...", state="disabled", fg_color="gray")
        elif hasattr(self, "btn_team_run"):
            self.btn_team_run.configure(text="🚫 STOPPING (Wait for git)...", state="disabled", fg_color="gray")
        self._update_cloner_ui(0, "🛑 Stop requested. Waiting for current git step to finish...")
        self.log("🛑 STOP SIGNAL SENT. Finishing current operation...")
        
        self.update_idletasks()

    def _generate_batch_commit_messages(self, original_msg, file_groups):
        """Пакетна генерація описів комітів через AI"""
        count = len(file_groups)
        if count <= 1: return [original_msg]

        files_desc = []
        for group in file_groups:
            names = [os.path.basename(f) for f in group[:2]]
            desc = ", ".join(names)
            if len(group) > 2: desc += " etc"
            files_desc.append(desc)

        prompt = f"""
        TASK: Split git commit message.
        ORIGINAL: \"{original_msg}\"
        I am splitting this commit into {count} atomic parts based on files.

        FILES FOR EACH PART:
        {json.dumps(files_desc)}

        OUTPUT: JSON list of {count} short, professional commit messages (English).
        Keep context of original message.
        Example Output: [\"Fix login handler\", \"Update auth styles\", \"Add unit tests\"]
        """

        try:
            response = ask_ai_safe(lambda x: x, prompt)
            if not response or "CRITICAL_FAILURE" in str(response):
                raise Exception("AI Failed")

            clean = str(response).replace("```json", "").replace("```", "").strip()
            messages = json.loads(clean)

            if len(messages) != count:
                raise Exception("Count mismatch")

            return messages
        except:
            return [f"{original_msg} ({desc})" for desc in files_desc]

    def _handle_abort_dialog(self, repo_name, tmp_source, tmp_target):
        """Вікно підтвердження видалення при зупинці"""
        try:
            if hasattr(self, 'lbl_cloner_status'):
                self.lbl_cloner_status.configure(text="🛑 STOPPED BY USER", text_color="red")
        except:
            pass

        choice = messagebox.askyesno(
            "🛑 Operation Aborted",
            f"You stopped the cloning process.\n\n"
            f"Do you want to DELETE the incomplete repository '{repo_name}' from GitHub?\n"
            f"(Yes = Delete, No = Keep it)"
        )

        if choice:
            self.log(f"🗑 Deleting incomplete repo {repo_name}...")
            try:
                api_delete_repo(self.token, self.username, repo_name)
                self.log("✅ Repository deleted successfully.")
            except Exception as e:
                self.log(f"❌ Failed to delete repo: {e}")
        else:
            self.log("⚠️ Repository kept on GitHub (Incomplete).")

        try:
            shutil.rmtree(tmp_source, ignore_errors=True)
            shutil.rmtree(tmp_target, ignore_errors=True)
        except: 
            pass

        try:
            self.btn_cloner_run.configure(
                text="🚀 ACTIVATE GOD MODE",
                fg_color=PALETTE[4],
                state="normal",
                command=self.start_cloner
            )
        except:
            pass

    def _create_and_close_issue(self, repo_name):
        try:
            smart_task = None
            if hasattr(self, 'smart_issues_queue') and self.smart_issues_queue:
                try:
                    smart_task = self.smart_issues_queue.pop(0)
                    self.log(f"🧠 Using AI Generated Task: {smart_task['title']}")
                except:
                    smart_task = None

            if not smart_task:
                fallback_templates = [
                    {"title": "Update README.md", "body": "Documentation needs an update."},
                    {"title": "Dependency Bump", "body": "Check for security updates."},
                    {"title": "Refactor small utility", "body": "A helper function could be simplified for readability."},
                    {"title": "Add basic tests", "body": "Introduce a minimal test suite for critical paths."},
                ]
                smart_task = random.choice(fallback_templates)

            title = str(smart_task.get('title', 'Chore: cleanup'))
            body = str(smart_task.get('body', 'Auto-generated issue for activity seeding.'))
            labels = ["noise"]

            issue_number = api_create_issue(self.token, self.username, repo_name, title, body, labels)
            if not issue_number:
                self.log("⚠️ Issue Noise: could not create issue")
                return False

            url = f"{REST_API_URL}/repos/{self.username}/{repo_name}/issues/{issue_number}"
            headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github.v3+json"}
            r = get_session(self.token).patch(url, headers=headers, json={"state": "closed"}, timeout=10)

            if r.status_code in (200, 201):
                self.log(f"📢 Issue Noise: created & closed #{issue_number}")
                return True
            else:
                self.log(f"⚠️ Issue Noise: close failed (HTTP {r.status_code})")
                return False
        except Exception as e:
            self.log(f"⚠️ Issue Noise error: {e}")
            return False

    def _collect_changed_files(self, repo_path):
        status_res = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True)
        files = []
        for line in status_res.stdout.splitlines():
            if not line.strip():
                continue
            f_path = line[3:].strip()
            if f_path.startswith('"') and f_path.endswith('"'):
                f_path = f_path[1:-1]
            files.append(f_path)
        return files

    def _pick_review_token_and_event(self, active_actors, current_actor):
        current_token = None
        if isinstance(current_actor, dict):
            current_token = current_actor.get("token")

        if isinstance(active_actors, list):
            candidates = []
            for actor in active_actors:
                if not isinstance(actor, dict):
                    continue
                tkn = actor.get("token")
                if not tkn:
                    continue
                if current_token and tkn == current_token:
                    continue
                candidates.append(actor)

            if candidates:
                reviewer = random.choice(candidates)
                reviewer_name = reviewer.get("username") or reviewer.get("name") or "Reviewer"
                return reviewer.get("token"), "APPROVE", reviewer_name

        return self.token, "COMMENT", self.username

    def _maybe_emit_realistic_issue(self, repo_name, enabled, issue_done, max_issue_events, issue_chance):
        if not enabled:
            return False
        if issue_done >= max_issue_events:
            return False
        if random.random() >= issue_chance:
            return False
        return bool(self._create_and_close_issue(repo_name))

    def _try_commit_via_pr_flow(self, tmp_target, repo_name, clean_msg, t_str, commit_index, active_actors, current_actor):
        base_branch = generate_branch_name_from_msg(clean_msg or "update-code")
        safe_base = re.sub(r"[^a-zA-Z0-9/_-]", "-", base_branch).strip("-") or "feat/update-code"
        branch_name = f"{safe_base}-pr-{commit_index + 1}-{random.randint(100, 999)}"
        branch_name = branch_name[:120]

        try:
            env = os.environ.copy()
            env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = t_str

            subprocess.run(["git", "checkout", "-b", branch_name], cwd=tmp_target, check=True, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "add", "."], cwd=tmp_target, check=True, stderr=subprocess.DEVNULL)
            subprocess.run(
                ["git", "commit", "--allow-empty", "-m", clean_msg or "Update code", "--date", t_str],
                cwd=tmp_target,
                env=env,
                check=True,
                stderr=subprocess.DEVNULL,
            )
            subprocess.run(["git", "push", "-u", "origin", branch_name], cwd=tmp_target, check=True, stderr=subprocess.DEVNULL)

            pr_title = (clean_msg or "Update code")[:120]
            pr_body = "Automated PR flow for realistic GitHub activity."
            pr_number = api_create_pr(self.token, self.username, repo_name, branch_name, "main", pr_title, pr_body)
            if not pr_number:
                raise Exception("PR create returned empty response")

            review_token, review_event, reviewer_name = self._pick_review_token_and_event(active_actors, current_actor)
            review_body = "Looks good to me! LGTM 🚀" if review_event == "APPROVE" else "Auto review comment for realistic activity."
            review_ok = api_create_pr_review(
                review_token,
                self.username,
                repo_name,
                pr_number,
                body=review_body,
                event=review_event,
            )
            if not review_ok:
                self.log(f"⚠️ PR review was not accepted for #{pr_number}. Continuing merge.")
            else:
                self.log(f"✅ PR review ({review_event}) submitted by {reviewer_name} for #{pr_number}.")

            merged = api_merge_pr(self.token, self.username, repo_name, pr_number)
            if not merged:
                raise Exception(f"PR merge returned empty response for #{pr_number}")

            try:
                api_delete_branch(self.token, self.username, repo_name, branch_name)
            except Exception:
                pass

            subprocess.run(["git", "checkout", "main"], cwd=tmp_target, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "fetch", "origin", "main"], cwd=tmp_target, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=tmp_target, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "branch", "-D", branch_name], cwd=tmp_target, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            self.log(f"⚠️ PR flow failed for commit #{commit_index + 1}: {e}")
            try:
                subprocess.run(["git", "checkout", "main"], cwd=tmp_target, stderr=subprocess.DEVNULL)
                subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=tmp_target, stderr=subprocess.DEVNULL)
                subprocess.run(["git", "clean", "-fd"], cwd=tmp_target, stderr=subprocess.DEVNULL)
            except Exception:
                pass
            return False

    def _handle_abort(self, repo_name, tmp_source, tmp_target):
        # Питаємо користувача
        choice = messagebox.askyesno(
            "Operation Cancelled",
            f"Cloning stopped.\n\nDo you want to DELETE the created repository '{repo_name}' from GitHub?\n\n(No = Keep unfinished repo)"
        )
        
        if choice:
            self.log(f"🗑 Deleting repository {repo_name}...")
            try:
                api_delete_repo(self.token, self.username, repo_name)
                self.log("✅ Repository deleted.")
            except Exception as e:
                self.log(f"❌ Could not delete repo: {e}")
        else:
            self.log(f"⚠️ Operation stopped. Repository '{repo_name}' kept as is.")

        # Чистимо тимчасові файли
        try:
            shutil.rmtree(tmp_source, ignore_errors=True)
            shutil.rmtree(tmp_target, ignore_errors=True)
        except: pass
        
        # Повертаємо кнопку назад
        self.after(0, lambda: self.btn_cloner_run.configure(
            text="🚀 ACTIVATE GOD MODE", 
            fg_color=PALETTE[4], 
            state="normal",
            command=self.start_cloner
        ))

    def run_cloner_logic(self, donor, name, desc, is_private, start, end, intensity, chaos_level):
        """
        ULTIMATE LOGIC V2: Atomic Splitting + Persona + Time Travel Guard
        """
        tmp_source = tempfile.mkdtemp()
        tmp_target = tempfile.mkdtemp()
        repo_created = False

        if not getattr(self, 'time_architect', None):
            self.time_architect = TimeArchitect()

        if AUDIO_AVAILABLE:
            try:
                if os.path.exists(SOUND_EAGLE): pygame.mixer.Sound(SOUND_EAGLE).play()
                if os.path.exists(SOUND_MUSIC):
                    pygame.mixer.music.load(SOUND_MUSIC)
                    pygame.mixer.music.play(-1)
            except: 
                pass

        try:
            if getattr(self, "stop_cloner_flag", False):
                self._handle_abort_dialog(name, tmp_source, tmp_target)
                return

            self.log(f"🔥 Starting ULTIMATE MIRROR of {donor['full_name']}...")

            repo_url = create_github_repo(self.username, self.token, name, is_private, desc)
            repo_created = True
            auth_url = repo_url.replace("https://", f"https://{self.token}@")

            self.log("Step 1: Deep Cloning Source...")
            subprocess.run(["git", "clone", donor['clone_url'], "."], cwd=tmp_source, check=True, stderr=subprocess.DEVNULL)

            log_cmd = ["git", "log", "--reverse", "--pretty=format:%H|%ct|%P|%s"]
            result = subprocess.run(log_cmd, cwd=tmp_source, capture_output=True, text=True, encoding="utf-8", errors="replace")

            commits = []
            for line in result.stdout.splitlines():
                parts = line.split("|", 3)
                if len(parts) == 4:
                    commits.append({
                        "h": parts[0],
                        "t": int(parts[1]),
                        "parents": parts[2].split(),
                        "m": parts[3]
                    })

            if not commits:
                raise Exception("No commits found!")

            subprocess.run(["git", "init"], cwd=tmp_target)
            subprocess.run(["git", "config", "user.email", self.gen_email.get()], cwd=tmp_target)
            git_user_name = self._read_auth_file().get("git_author", self.username)
            subprocess.run(["git", "config", "user.name", git_user_name], cwd=tmp_target)
            subprocess.run(["git", "checkout", "-b", "main"], cwd=tmp_target)
            subprocess.run(["git", "remote", "add", "origin", auth_url], cwd=tmp_target)

            persona = "Freelancer"
            try:
                persona = self.combo_persona.get()
            except:
                persona = "Freelancer"

            seed_date = self._get_seed_date(start)
            init_dt = datetime.datetime.combine(seed_date, datetime.time())
            init_t_str = self.time_architect.get_commit_time(init_dt, persona)
            init_env = os.environ.copy()
            init_env["GIT_AUTHOR_DATE"] = init_env["GIT_COMMITTER_DATE"] = init_t_str
            subprocess.run(["git", "commit", "--allow-empty", "-m", "Initial commit"], cwd=tmp_target, env=init_env, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "push", "-u", "origin", "main"], cwd=tmp_target, stderr=subprocess.DEVNULL)

            orig_start = commits[0]['t']
            orig_duration = max(1, commits[-1]['t'] - orig_start)
            ts_start = time.mktime(start.timetuple())
            ts_end = time.mktime(end.timetuple())
            target_duration = max(1, ts_end - ts_start)

            density_status = self.time_architect.analyze_density(len(commits), (end - start).days)
            force_split = (density_status == 'sparse')

            total_commits = len(commits)
            for i, c in enumerate(commits):
                if getattr(self, "stop_cloner_flag", False):
                    self._handle_abort_dialog(name, tmp_source, tmp_target)
                    return

                subprocess.run(["git", "checkout", "-f", c['h']], cwd=tmp_source, stderr=subprocess.DEVNULL)
                sync_directories(tmp_source, tmp_target)

                progress = (c['t'] - orig_start) / orig_duration
                new_ts = ts_start + (progress * target_duration)
                base_date_obj = datetime.datetime.fromtimestamp(new_ts)

                is_merge = len(c.get('parents') or []) > 1

                status_res = subprocess.run(["git", "status", "--porcelain"], cwd=tmp_target, capture_output=True, text=True)
                files = []
                for line in status_res.stdout.splitlines():
                    if not line.strip():
                        continue
                    f_path = line[3:].strip()
                    if f_path.startswith('"') and f_path.endswith('"'):
                        f_path = f_path[1:-1]
                    files.append(f_path)

                should_split = False
                chunks = [files]
                if not is_merge and files:
                    if len(files) > 10:
                        should_split = False
                    elif force_split or (len(files) > 1):
                        should_split = True

                if should_split:
                    n_chunks = min(3, len(files))
                    chunk_size = math.ceil(len(files) / n_chunks)
                    chunks = [files[j:j + chunk_size] for j in range(0, len(files), chunk_size)]

                    clean_msg = re.sub(r'Co-authored-by:.*', '', c['m'], flags=re.IGNORECASE).strip()
                    try:
                        ai_msgs = self._generate_batch_commit_messages(clean_msg, chunks)
                    except:
                        ai_msgs = [clean_msg] * len(chunks)
                else:
                    ai_msgs = [re.sub(r'Co-authored-by:.*', '', c['m'], flags=re.IGNORECASE).strip()]

                for idx, chunk in enumerate(chunks):
                    if should_split:
                        for f in chunk:
                            subprocess.run(["git", "add", f], cwd=tmp_target, stderr=subprocess.DEVNULL)
                    else:
                        subprocess.run(["git", "add", "."], cwd=tmp_target, stderr=subprocess.DEVNULL)

                    offset = idx * 2
                    commit_dt = base_date_obj + datetime.timedelta(minutes=offset)
                    t_str = self.time_architect.get_commit_time(commit_dt, persona)
                    env = os.environ.copy()
                    env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = t_str

                    msg = ai_msgs[idx] if idx < len(ai_msgs) else ai_msgs[0]
                    subprocess.run(["git", "commit", "--allow-empty", "-m", msg], cwd=tmp_target, env=env, stderr=subprocess.DEVNULL)

                if i % 5 == 0:
                    perc = i / total_commits
                    self.after(0, lambda p=perc, t=f"🚀 Cloning {i}/{total_commits} | 📅 {base_date_obj.date()}": self._update_cloner_ui(p, t))

            self.log("🔄 Pushing final history...")
            subprocess.run(["git", "push", "origin", "main"], cwd=tmp_target, stderr=subprocess.DEVNULL)
            self.refresh_manager_repos(name)
            messagebox.showinfo("Success", "ULTIMATE Mirror Complete!\nHistory successfully rewritten.")

        except Exception as e:
            self.log(f"❌ CRITICAL ERROR: {e}")
            if repo_created:
                self._handle_abort_dialog(name, tmp_source, tmp_target)
        finally:
            if AUDIO_AVAILABLE:
                try:
                    pygame.mixer.music.stop()
                except:
                    pass
            self.after(0, lambda: self.btn_cloner_run.configure(
                text="🚀 ACTIVATE GOD MODE", fg_color=PALETTE[4], state="normal", command=self.start_cloner
            ))
            try:
                shutil.rmtree(tmp_source, ignore_errors=True)
                shutil.rmtree(tmp_target, ignore_errors=True)
            except: 
                pass

    def _apply_final_polish(self, target_dir):
        """Фінальна чистка: AI для важливого, Regex для решти."""
        files_to_process = []
        for root, dirs, files in os.walk(target_dir):
            if ".git" in root: continue
            for file in files:
                if not any(file.endswith(ext) for ext in IGNORE_EXTENSIONS):
                    files_to_process.append(os.path.join(root, file))
        
        # Обробляємо файли
        for i, fpath in enumerate(files_to_process):
            fname = os.path.basename(fpath)
            is_priority = any(p in fname for p in PRIORITY_FILES)
            
            try:
                # Спроба читання
                content = ""
                for enc in ['utf-8', 'latin-1', 'gbk']:
                    try: 
                        with open(fpath, 'r', encoding=enc) as f: content = f.read()
                        break
                    except: pass
                
                if not content: continue
                
                final_content = content
                # ЛОГІКА:
                if is_priority:
                    # AI Prettier
                    new_code = ask_ai_safe(prompt_refactor_code, content, self.username)
                    if new_code and new_code != "CRITICAL_FAILURE":
                        cleaned = clean_ai_response(new_code)
                        final_content = apply_aggressive_branding(cleaned, self.username)
                    else:
                        final_content = apply_aggressive_branding(content, self.username)
                else:
                    # Fast Cleanup
                    step1 = fast_cleanup_non_priority(content)
                    final_content = apply_aggressive_branding(step1, self.username)
                
                # Запис назад, якщо змінилось
                if final_content != content:
                    with open(fpath, 'w', encoding='utf-8') as f: f.write(final_content)
            
            except Exception: pass
            
        # Робимо фінальний коміт з актуальною датою (або останньою датою End Date)
        last_date = self.get_date_val(self.cloner_end)
        t_str = self.generate_human_time(last_date)
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = t_str
        
        subprocess.run(["git", "add", "."], cwd=target_dir, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "commit", "-m", "Refactor: Code style standardization and cleanup"], cwd=target_dir, env=env, stderr=subprocess.DEVNULL)

    def sanitize_file(self, local_path, rel_path):
        fname = os.path.basename(local_path).lower()
        if any(fname.endswith(ext) for ext in IGNORE_EXTENSIONS): return
        
        # MARK: ROBUST ENCODING READ
        content = None
        encodings = ['utf-8', 'latin-1', 'gbk', 'cp1252']
        for enc in encodings:
            try:
                with open(local_path, 'r', encoding=enc) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
             self.log(f"❌ Could not read {fname} with any encoding. Skipping.")
             return

        try:
            new_content = content
            if "license" in fname:
                new_content = f"MIT License\n\nCopyright (c) {datetime.date.today().year} {self.username}\n..."
            elif fname == "package.json":
                try: 
                    d = json.loads(content)
                    d["author"] = self.username
                    new_content = json.dumps(d, indent=2)
                except: pass
            elif fname == "readme.md":
                new_content = get_ai_readme(new_content)
                if new_content == "CRITICAL_FAILURE":
                     new_content = re.sub(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', '', content)
                else:
                    self.log(f"✨ AI Readme: Rewritten successfully")
            else:
                new_content = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', "contact@example.com", new_content)

            try:
                final_content = self._process_file_content(rel_path or fname, new_content)
            except:
                final_content = new_content
            
            if final_content != content:
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(final_content)
        except: pass

    def _process_file_content(self, filename, content):
        """Головний конвеєр обробки файлу перед записом"""
        new_content = content

        try:
            if hasattr(self, 'chk_license_swap') and self.chk_license_swap.get():
                if filename.lower() in ['license', 'license.md', 'copying', 'license.txt']:
                    new_content = self._swap_license_owner(new_content)
        except:
            pass

        try:
            if hasattr(self, 'apply_sanitization'):
                new_content = self.apply_sanitization(new_content)
        except:
            pass

        try:
            if hasattr(self, 'chk_translate') and self.chk_translate.get():
                if filename.lower().endswith(('.py', '.js', '.ts', '.go', '.java', '.cpp')):
                    new_content = self._ai_translate_comments(filename, new_content)
        except:
            pass

        return new_content

    def _swap_license_owner(self, content):
        """Міняє власника ліцензії на поточного користувача"""
        import re
        import datetime

        current_year = datetime.datetime.now().year
        my_name = ""
        try:
            if hasattr(self, 'entry_git_author'):
                my_name = self.entry_git_author.get().strip()
        except:
            my_name = ""
        if not my_name:
            my_name = getattr(self, 'username', '') or "My Company"

        pattern = r"(Copyright\s+(?:\(c\)\s+)?(?:©\s+)?)(?:\d{4}(?:\s*-\s*\d{4})?)(\s+.+)"

        def replacer(match):
            prefix = match.group(1)
            return f"{prefix}{current_year} {my_name}"

        new_content = re.sub(pattern, replacer, content, flags=re.IGNORECASE)
        return new_content

    def _ai_translate_comments(self, filename, content):
        """Відправляє файл в AI для перекладу коментарів"""
        if len(content) > 10000:
            return content

        prompt = f"""
        TASK: Rewrite the code below.
        ACTION: Translate ALL comments and docstrings to English.
        CONSTRAINT: Do NOT change code logic. Keep indentation exactly the same.
        input_code:
        {content}
        """

        try:
            import time
            time.sleep(5)

            translated = ask_ai_safe(lambda x: x, prompt)
            if not translated or "CRITICAL_FAILURE" in str(translated) or "```" not in str(translated):
                return content

            clean = str(translated).replace("```python", "").replace("```javascript", "").replace("```", "")
            return clean.strip()

        except:
            return content

    # ===================== TAB 3: MANUAL ART =====================
    def build_manual_tab(self):
        t = self.tab_manual
        t.columnconfigure(0, weight=1)
        t.columnconfigure(1, weight=3)
        f_left = ctk.CTkFrame(t, fg_color="transparent")
        f_left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.man_year = ctk.CTkComboBox(f_left, values=self.get_valid_years(), command=self.init_manual_grid)
        self.man_year.pack(anchor="w", pady=5)
        self.man_intensity = tk.IntVar(value=4)
        for txt, val in [("Eraser", 0), ("Low", 1), ("Mid", 2), ("High", 3), ("Crazy", 4)]:
            ctk.CTkRadioButton(f_left, text=txt, value=val, variable=self.man_intensity, text_color=COLOR_TEXT_MAIN, fg_color=PALETTE[val], hover_color=PALETTE[val]).pack(anchor="w")
        ctk.CTkLabel(f_left, text="Select Languages:", font=("Helvetica", 12)).pack(anchor="w", pady=(15, 5))
        lang_frame = ctk.CTkFrame(f_left, fg_color=COLOR_FIELD_BG, height=50)
        lang_frame.pack(fill="x", pady=(0, 15))
        self.man_lang_scroll = ctk.CTkScrollableFrame(lang_frame, orientation="horizontal", height=30, fg_color="transparent")
        self.man_lang_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        self.man_langs_vars = {}
        for item in TARGET_STACK:
            var = tk.BooleanVar()
            ctk.CTkCheckBox(self.man_lang_scroll, text=item, variable=var, width=60).pack(side="left", padx=10)
            self.man_langs_vars[item] = var
        self.man_name = ctk.CTkEntry(f_left, placeholder_text="Repo Name")
        self.man_name.pack(anchor="w", pady=15)
        self.man_email = ctk.CTkEntry(f_left, placeholder_text="Email")
        self.man_email.pack(anchor="w", pady=5)

        # --- АВТОЗАПОВНЕННЯ ---
        saved_email = self._read_auth_file().get("default_email", "")
        if saved_email: self.man_email.insert(0, saved_email)
        # ----------------------
        self.man_private = ctk.CTkSwitch(f_left, text="Private")
        self.man_private.select()
        self.man_private.pack(anchor="w", pady=5)
        ctk.CTkButton(f_left, text="Load Stats", fg_color="gray", command=self.load_real_stats_to_grid).pack(anchor="w", pady=10)
        f_right = ctk.CTkFrame(t, fg_color="transparent")
        f_right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.lbl_man = ctk.CTkLabel(f_right, text="Draw (Click cells)", font=("Helvetica", 14))
        self.lbl_man.pack(anchor="w")
        self.man_canvas = tk.Canvas(f_right, bg="white", height=180, width=750, bd=0, highlightthickness=0)
        self.man_canvas.pack(pady=10)
        self.man_canvas.bind("<Button-1>", self.on_grid_click)
        self.man_canvas.bind("<Motion>", self.on_grid_hover)
        self.btn_man_push = ctk.CTkButton(f_right, text="PUSH ART", command=self.start_manual_push)
        self.btn_man_push.pack(pady=10)
        self.man_progress = ctk.CTkProgressBar(f_right, width=300)
        self.man_progress.set(0)
        self.man_progress.pack()
        self.after(500, lambda: self.init_manual_grid(self.man_year.get()) if self.man_year.get() else None)

    def init_manual_grid(self, year_val):
        if not year_val: return
        year = int(year_val)
        self.manual_grid_data = {}
        self.man_canvas.delete("all")
        cur = datetime.date(year, 1, 1)
        end = datetime.date(year, 12, 31)
        today = datetime.date.today()
        while cur <= end:
            wn = int(cur.strftime("%U"))
            dn = int(cur.strftime("%w"))
            x = wn * 14 + 10
            y = dn * 14 + 10
            inv = (cur < self.created_date) or (cur > today)
            col = COLOR_DISABLED if inv else PALETTE[0]
            tags = ("disabled",) if inv else (f"d_{cur}",)
            self.man_canvas.create_rectangle(x, y, x+11, y+11, fill=col, outline="white", tags=tags)
            if not inv: self.manual_grid_data[str(cur)] = 0
            cur += datetime.timedelta(days=1)
    
    def on_grid_click(self, e):
        item = self.man_canvas.find_closest(e.x, e.y)
        tags = self.man_canvas.gettags(item)
        if "disabled" in tags: return
        for t in tags:
            if t.startswith("d_"):
                self.manual_grid_data[t[2:]] = self.man_intensity.get()
                self.man_canvas.itemconfigure(item, fill=PALETTE[self.man_intensity.get()])
    
    def on_grid_hover(self, e):
        item = self.man_canvas.find_closest(e.x, e.y)
        tags = self.man_canvas.gettags(item)
        for t in tags: 
            if t.startswith("d_"): self.lbl_man.configure(text=f"Date: {t[2:]}")

    def load_real_stats_to_grid(self):
        y = int(self.man_year.get())
        threading.Thread(target=lambda: self._apply_real(fetch_yearly_commit_data(self.username, self.token, y)), daemon=True).start()

    def _apply_real(self, days):
        for d in days:
            if d["date"] in self.manual_grid_data:
                c = d["contributionCount"]
                lvl = 0
                if c>0: lvl=1
                if c>3: lvl=2
                if c>6: lvl=3
                if c>10: lvl=4
                self.manual_grid_data[d["date"]] = lvl
                self.man_canvas.itemconfigure(f"d_{d['date']}", fill=PALETTE[lvl])

    def start_manual_push(self):
        name = self.man_name.get()
        email = self.man_email.get()
        langs = [l for l, v in self.man_langs_vars.items() if v.get()]
        if not name or not email or not langs: return messagebox.showerror("Error", "Name, Email and Lang required")
        self.btn_man_push.configure(state="disabled")
        threading.Thread(target=self.run_manual_logic, args=(name, email, self.man_private.get(), langs), daemon=True).start()

    def run_manual_logic(self, name, email, is_private, langs):
        tmp = tempfile.mkdtemp()
        try:
            repo_desc = self._resolve_repo_desc("", getattr(self, "selected_donor", None))
            auth_url = create_github_repo(self.username, self.token, name, is_private, repo_desc).replace("https://", f"https://{self.token}@")
            subprocess.run(["git", "init"], cwd=tmp, check=True)
            subprocess.run(["git", "config", "user.email", email], cwd=tmp)
            # Вибираємо ім'я: або Alias з налаштувань, або GitHub логін
            git_user_name = self._read_auth_file().get("git_author", self.username)
            subprocess.run(["git", "config", "user.name", git_user_name], cwd=tmp)
            subprocess.run(["git", "checkout", "-b", "main"], cwd=tmp)
            subprocess.run(["git", "remote", "add", "origin", auth_url], cwd=tmp)
            files = []
            if "HTML/CSS" in langs and "JavaScript" in langs:
                for fname, content in WEB_COMBO_TEMPLATE["files"]:
                    with open(os.path.join(tmp, fname), "w") as f:
                        f.write(content)
                    files.append(fname)
            for lang in langs:
                if lang in PROJECT_TEMPLATES:
                    prefix = lang.lower().replace("/", "") + "_core"
                    os.makedirs(os.path.join(tmp, prefix), exist_ok=True)
                    for fname, content in PROJECT_TEMPLATES[lang]["files"]:
                        p = os.path.join(prefix, fname)
                        with open(os.path.join(tmp, p), "w") as f:
                            f.write(content)
                        files.append(p)
            readme_path = os.path.join(tmp, "README.md")
            if not os.path.exists(readme_path):
                with open(readme_path, "w") as f:
                    f.write(f"# {name}")
            if not files:
                raise Exception("No template files for selected languages")

            dates = sorted([d for d, l in self.manual_grid_data.items() if l > 0])
            first_real_date = datetime.datetime.strptime(dates[0], "%Y-%m-%d").date() if dates else datetime.date.today()
            init_date = self._get_seed_date(first_real_date)
            t_str = self.generate_human_time(init_date)
            env = os.environ.copy()
            env["GIT_AUTHOR_DATE"] = t_str
            env["GIT_COMMITTER_DATE"] = t_str

            subprocess.run(["git", "add", "."], cwd=tmp)
            subprocess.run(["git", "commit", "-m", "init"], cwd=tmp, env=env)
            total = len(dates)
            for i, d_str in enumerate(dates):
                lvl = self.manual_grid_data[d_str]
                self.after(0, lambda p=(i/total): self.man_progress.set(p))
                cnt = [0,1,4,7,12][lvl]
                d_date = datetime.datetime.strptime(d_str, "%Y-%m-%d").date()
                for _ in range(cnt): 
                    t_str = self.generate_human_time(d_date)
                    target = random.choice(files)
                    ext = os.path.splitext(target)[1]
                    snippet = random.choice(REAL_CODE_SNIPPETS.get(ext, REAL_CODE_SNIPPETS["default"]))
                    with open(os.path.join(tmp, target), "a") as f:
                        f.write(f"\n{snippet}\n")
                    env = os.environ.copy()
                    env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = t_str
                    msg = get_ai_commit_message(target)
                    subprocess.run(["git", "add", "."], cwd=tmp, stderr=subprocess.DEVNULL)
                    subprocess.run(["git", "commit", "-m", msg, "--date", t_str], cwd=tmp, env=env, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "push", "-u", "origin", "main"], cwd=tmp, capture_output=True)
            messagebox.showinfo("Success", "Art Pushed!")
        except Exception as e: self.log(str(e))
        finally: 
            self.after(0, lambda: self.btn_man_push.configure(state="normal"))
            if tmp: shutil.rmtree(tmp, ignore_errors=True)

    # ===================== TAB 4: GRAPH THIEF =====================
    def build_thief_tab(self):
        t = self.tab_thief
        t.columnconfigure(0, weight=1)
        t.columnconfigure(1, weight=3)

        f_left = ctk.CTkFrame(t, fg_color="transparent")
        f_left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(f_left, text="Target Dev Username").pack(anchor="w", pady=(0, 5))
        self.entry_target_user = ctk.CTkEntry(f_left, placeholder_text="Target Dev Username (e.g. torvalds)")
        self.entry_target_user.pack(fill="x", pady=(0, 10))

        years = self.get_thief_years()
        ctk.CTkLabel(f_left, text="Source Year").pack(anchor="w")
        self.combo_source_year = ctk.CTkComboBox(f_left, values=years)
        self.combo_source_year.pack(fill="x", pady=(0, 8))
        if years:
            self.combo_source_year.set(years[0])

        ctk.CTkLabel(f_left, text="Target Year").pack(anchor="w")
        self.combo_target_year = ctk.CTkComboBox(f_left, values=years)
        self.combo_target_year.pack(fill="x", pady=(0, 10))
        if years:
            self.combo_target_year.set(years[0])

        self.btn_load_graph = ctk.CTkButton(f_left, text="Load Graph", command=self.load_thief_graph)
        self.btn_load_graph.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(f_left, text="Project Config", font=("Helvetica", 13, "bold")).pack(anchor="w", pady=(0, 5))
        self.entry_thief_repo_name = ctk.CTkEntry(f_left, placeholder_text="Repo Name")
        self.entry_thief_repo_name.pack(fill="x", pady=(0, 6))
        self.entry_thief_desc = ctk.CTkEntry(f_left, placeholder_text="Description (Optional)")
        self.entry_thief_desc.pack(fill="x", pady=(0, 6))
        self.switch_thief_private = ctk.CTkSwitch(f_left, text="Private Repo")
        self.switch_thief_private.select()
        self.switch_thief_private.pack(anchor="w", pady=(0, 12))

        ctk.CTkLabel(f_left, text="Select Languages:", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        lang_frame = ctk.CTkFrame(f_left, fg_color=COLOR_FIELD_BG, height=50)
        lang_frame.pack(fill="x", pady=(0, 5))
        self.thief_lang_scroll = ctk.CTkScrollableFrame(lang_frame, orientation="horizontal", height=30, fg_color="transparent")
        self.thief_lang_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        self.thief_langs_vars = {}
        for item in TARGET_STACK:
            var = tk.BooleanVar()
            ctk.CTkCheckBox(self.thief_lang_scroll, text=item, variable=var, width=60).pack(side="left", padx=10)
            self.thief_langs_vars[item] = var

        f_right = ctk.CTkFrame(t, fg_color="transparent")
        f_right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.lbl_thief_status = ctk.CTkLabel(f_right, text="Load a graph to preview", font=("Helvetica", 14))
        self.lbl_thief_status.pack(anchor="w")
        self.canvas_thief = tk.Canvas(f_right, bg="white", height=180, width=750, bd=0, highlightthickness=0)
        self.canvas_thief.pack(pady=10)
        self.canvas_thief.bind("<Motion>", self.on_thief_hover)
        self.btn_steal = ctk.CTkButton(f_right, text="STEAL GRAPH & PUSH", command=self.start_thief)
        self.btn_steal.pack(pady=10)
        self.progress_thief = ctk.CTkProgressBar(f_right, width=300)
        self.progress_thief.set(0)
        self.progress_thief.pack()

        self.thief_graph_days = []
        self.thief_graph_map = {}
        self.thief_target_dates = {}
        self.thief_preview_index = {}
        self.thief_loaded_source_user = None
        self.thief_loaded_source_year = None
        self.thief_loaded_target_year = None

    def load_thief_graph(self):
        target_user = (self.entry_target_user.get() or "").strip()
        source_year = (self.combo_source_year.get() or "").strip()
        target_year = (self.combo_target_year.get() or "").strip()
        if not target_user or not source_year or not target_year:
            return messagebox.showerror("Error", "Target user and years required")

        self.progress_thief.set(0)
        self.thief_graph_days = []
        self.thief_graph_map = {}
        self.thief_target_dates = {}
        self.thief_preview_index = {}
        self.canvas_thief.delete("all")
        self.lbl_thief_status.configure(text="Loading graph...")
        self.btn_load_graph.configure(state="disabled")
        threading.Thread(
            target=self._load_thief_graph_thread,
            args=(target_user, int(source_year), int(target_year)),
            daemon=True,
        ).start()

    def _load_thief_graph_thread(self, target_user, source_year, target_year):
        try:
            days = fetch_yearly_commit_data(target_user, self.token, source_year)
            if not days:
                self.log(f"⚠️ Graph Thief: could not fetch graph for {target_user} ({source_year})")
                self.after(0, lambda: messagebox.showerror("Error", "Could not fetch contribution graph"))
                self.after(0, lambda: self.lbl_thief_status.configure(text="Failed to load graph"))
                return

            grid_map = self._build_weekday_grid_map(source_year, days)
            target_dates = self._build_target_year_grid_dates(target_year)

            self.thief_graph_days = days
            self.thief_graph_map = grid_map
            self.thief_target_dates = target_dates
            self.thief_loaded_source_user = target_user
            self.thief_loaded_source_year = source_year
            self.thief_loaded_target_year = target_year

            self.after(0, lambda gm=grid_map, td=target_dates: self._render_thief_graph(gm, td))
            self.log(f"🥷 Loaded graph for {target_user} ({source_year}) -> target {target_year}")
        except Exception as e:
            self.log(f"❌ Graph Thief load error: {e}")
            self.after(0, lambda err=str(e): messagebox.showerror("Error", f"Graph load failed: {err}"))
            self.after(0, lambda: self.lbl_thief_status.configure(text="Failed to load graph"))
        finally:
            self.after(0, lambda: self.btn_load_graph.configure(state="normal"))

    def _build_weekday_grid_map(self, year, days):
        _ = year
        grid_map = {}
        for item in days:
            try:
                d = datetime.datetime.strptime(item["date"], "%Y-%m-%d").date()
                week_num = int(d.strftime("%U"))
                day_num = int(d.strftime("%w"))
                grid_map[(week_num, day_num)] = int(item.get("contributionCount", 0))
            except Exception:
                continue
        return grid_map

    def _build_target_year_grid_dates(self, target_year):
        target_dates = {}
        cur = datetime.date(target_year, 1, 1)
        end = datetime.date(target_year, 12, 31)
        while cur <= end:
            week_num = int(cur.strftime("%U"))
            day_num = int(cur.strftime("%w"))
            target_dates[(week_num, day_num)] = cur
            cur += datetime.timedelta(days=1)
        return target_dates

    def _thief_color_for_count(self, count):
        if count > 10:
            return PALETTE[4]
        if count > 6:
            return PALETTE[3]
        if count > 3:
            return PALETTE[2]
        if count > 0:
            return PALETTE[1]
        return PALETTE[0]

    def _render_thief_graph(self, grid_map, target_dates):
        self.canvas_thief.delete("all")
        self.thief_preview_index = {}

        for (week_num, day_num), target_date in sorted(target_dates.items(), key=lambda x: (x[0][0], x[0][1])):
            count = int(grid_map.get((week_num, day_num), 0))
            color = self._thief_color_for_count(count)
            x = week_num * 14 + 10
            y = day_num * 14 + 10
            tag = f"t_{target_date.isoformat()}"
            self.canvas_thief.create_rectangle(x, y, x + 11, y + 11, fill=color, outline="white", tags=(tag,))
            self.thief_preview_index[target_date.isoformat()] = {
                "date": target_date.isoformat(),
                "count": count,
                "week": week_num,
                "day": day_num,
            }

        self.lbl_thief_status.configure(
            text=f"Loaded pattern: {self.thief_loaded_source_user or '-'} ({self.thief_loaded_source_year}) -> {self.thief_loaded_target_year}"
        )

    def on_thief_hover(self, event):
        item = self.canvas_thief.find_closest(event.x, event.y)
        tags = self.canvas_thief.gettags(item)
        for tag in tags:
            if tag.startswith("t_"):
                date_key = tag[2:]
                info = self.thief_preview_index.get(date_key)
                if info:
                    self.lbl_thief_status.configure(text=f"{info['date']}: {info['count']} commits")
                return

    def start_thief(self):
        if not self.thief_graph_map or not self.thief_target_dates:
            return messagebox.showerror("Error", "Load a source graph first")

        repo_name = (self.entry_thief_repo_name.get() or "").strip()
        langs = [l for l, v in self.thief_langs_vars.items() if v.get()]
        if not repo_name or not langs:
            return messagebox.showerror("Error", "Repo name and languages required")

        config = {
            "target_user": (self.entry_target_user.get() or "").strip(),
            "source_year": int(self.combo_source_year.get()),
            "target_year": int(self.combo_target_year.get()),
            "repo_name": repo_name,
            "desc": self._resolve_repo_desc((self.entry_thief_desc.get() or "").strip(), getattr(self, "selected_donor", None)),
            "is_private": bool(self.switch_thief_private.get()),
            "langs": langs,
            "graph_map": dict(self.thief_graph_map),
            "target_dates": dict(self.thief_target_dates),
        }

        self.progress_thief.set(0)
        self.btn_steal.configure(state="disabled")
        self.lbl_thief_status.configure(text="Executing heist...")
        threading.Thread(target=self._thief_thread, args=(config,), daemon=True).start()

    def _scaffold_thief_project(self, tmp_dir, langs, repo_name):
        files = []
        if "HTML/CSS" in langs and "JavaScript" in langs:
            for fname, content in WEB_COMBO_TEMPLATE["files"]:
                with open(os.path.join(tmp_dir, fname), "w") as f:
                    f.write(content)
                files.append(fname)

        for lang in langs:
            if lang in PROJECT_TEMPLATES:
                prefix = lang.lower().replace("/", "") + "_core"
                os.makedirs(os.path.join(tmp_dir, prefix), exist_ok=True)
                for fname, content in PROJECT_TEMPLATES[lang]["files"]:
                    p = os.path.join(prefix, fname)
                    with open(os.path.join(tmp_dir, p), "w") as f:
                        f.write(content)
                    files.append(p)

        readme_path = os.path.join(tmp_dir, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, "w") as f:
                f.write(f"# {repo_name}")

        if not files:
            raise Exception("No template files for selected languages")
        return files

    def _thief_thread(self, config):
        tmp = tempfile.mkdtemp()
        try:
            self.log(f"🥷 Starting Graph Thief for {config['target_user']} ({config['source_year']} -> {config['target_year']})")
            repo_url = create_github_repo(
                self.username,
                self.token,
                config["repo_name"],
                config["is_private"],
                config["desc"],
            )
            auth_url = repo_url.replace("https://", f"https://{self.token}@")

            subprocess.run(["git", "init"], cwd=tmp, check=True)
            email = self._read_auth_file().get("default_email", "").strip() or f"{self.username}@users.noreply.github.com"
            subprocess.run(["git", "config", "user.email", email], cwd=tmp, check=True)
            git_user_name = self._read_auth_file().get("git_author", self.username)
            subprocess.run(["git", "config", "user.name", git_user_name], cwd=tmp, check=True)
            subprocess.run(["git", "checkout", "-b", "main"], cwd=tmp, check=True)
            subprocess.run(["git", "remote", "add", "origin", auth_url], cwd=tmp, check=True)

            files = self._scaffold_thief_project(tmp, config["langs"], config["repo_name"])

            active_dates = [
                target_date
                for coord, target_date in config["target_dates"].items()
                if int(config["graph_map"].get(coord, 0)) > 0
            ]
            if active_dates:
                first_real_date = min(active_dates)
            else:
                first_real_date = datetime.date(config["target_year"], 1, 1)

            seed_date = self._get_seed_date(first_real_date)
            seed_t_str = self.generate_human_time(seed_date)
            seed_env = os.environ.copy()
            seed_env["GIT_AUTHOR_DATE"] = seed_env["GIT_COMMITTER_DATE"] = seed_t_str
            subprocess.run(["git", "add", "."], cwd=tmp, check=True)
            subprocess.run(["git", "commit", "--allow-empty", "-m", "Initial commit"], cwd=tmp, env=seed_env, check=True)

            ordered_dates = sorted(
                [
                    (target_date, int(config["graph_map"].get(coord, 0)))
                    for coord, target_date in config["target_dates"].items()
                ],
                key=lambda x: x[0],
            )
            ordered_dates = [(date_obj, count) for date_obj, count in ordered_dates if count > 0]
            total_dates = max(1, len(ordered_dates))

            for i, (target_date, contribution_count) in enumerate(ordered_dates):
                self.after(0, lambda p=(i + 1) / total_dates: self.progress_thief.set(p))
                for _ in range(contribution_count):
                    target = random.choice(files)
                    ext = os.path.splitext(target)[1]
                    snippet = random.choice(REAL_CODE_SNIPPETS.get(ext, REAL_CODE_SNIPPETS["default"]))
                    with open(os.path.join(tmp, target), "a") as f:
                        f.write(f"\n{snippet}\n")

                    t_str = self.generate_human_time(target_date)
                    env = os.environ.copy()
                    env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = t_str
                    msg = get_ai_commit_message(target)
                    subprocess.run(["git", "add", "."], cwd=tmp, check=True)
                    subprocess.run(["git", "commit", "-m", msg, "--date", t_str], cwd=tmp, env=env, check=True)

            subprocess.run(["git", "push", "-u", "origin", "main"], cwd=tmp, check=True)
            self.after(0, lambda: self.progress_thief.set(1.0))
            self.after(0, lambda: self.lbl_thief_status.configure(text="Heist complete ✅"))
            self.after(0, lambda: messagebox.showinfo("Success", "Graph stolen and pushed successfully!"))
        except Exception as e:
            self.log(f"❌ Graph Thief error: {e}")
            self.after(0, lambda err=str(e): messagebox.showerror("Error", f"Graph Thief failed: {err}"))
            self.after(0, lambda: self.lbl_thief_status.configure(text="Heist failed"))
        finally:
            self.after(0, lambda: self.btn_steal.configure(state="normal"))
            shutil.rmtree(tmp, ignore_errors=True)

    # ===================== MANAGER & STATS =====================
    def build_manager_tab(self):
        t = self.tab_manager
        t.columnconfigure(0, weight=1)
        t.columnconfigure(1, weight=2)
        t.rowconfigure(0, weight=1)
        f_side = ctk.CTkFrame(t, fg_color="transparent")
        f_side.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        self.man_search = ctk.CTkEntry(f_side, placeholder_text="Search...")
        self.man_search.pack(fill="x", pady=5)
        self.man_search.bind("<KeyRelease>", self.filter_repos)
        self.btn_select_mode = ctk.CTkButton(f_side, text="Select Mode", fg_color="gray", command=self.toggle_selection)
        self.btn_select_mode.pack(fill="x", pady=5)
        self.repo_scroll = ctk.CTkScrollableFrame(f_side, fg_color=COLOR_FIELD_BG)
        self.repo_scroll.pack(fill="both", expand=True)
        ctk.CTkButton(f_side, text="Load More", command=self.load_more_repos).pack(fill="x", pady=5)
        self.f_detail = ctk.CTkFrame(t, fg_color="transparent")
        self.f_detail.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.load_more_repos()

    def refresh_manager_repos(self, expected_repo_name=None):
        threading.Thread(
            target=self._refresh_repos_thread,
            args=(expected_repo_name,),
            daemon=True
        ).start()

    def _refresh_repos_thread(self, expected_repo_name=None):
        try:
            refreshed = []
            found_expected = False
            expected_name = (expected_repo_name or "").strip().lower()

            for _ in range(4):
                refreshed = api_fetch_repos(self.token, 1) or []
                if not expected_name:
                    found_expected = True
                    break

                found_expected = any(
                    (r.get("name", "").strip().lower() == expected_name) or
                    (r.get("full_name", "").strip().lower().endswith(f"/{expected_name}"))
                    for r in refreshed
                )
                if found_expected:
                    break
                time.sleep(1.0)

            def _apply():
                self.repos_list = refreshed
                self.manager_page = 2 if refreshed else 1
                if hasattr(self, "repo_scroll"):
                    self.render_repos()
                if expected_repo_name:
                    if found_expected:
                        self.log(f"📦 Repo Manager synced: {expected_repo_name}")
                    else:
                        self.log(f"⚠️ Repo Manager refreshed, GitHub may still be indexing: {expected_repo_name}")

            self.after(0, _apply)
        except Exception as e:
            self.log(f"⚠️ Repo Manager refresh failed: {e}")

    def load_more_repos(self): threading.Thread(target=self._fetch_repos, daemon=True).start()
    def _fetch_repos(self):
        new = api_fetch_repos(self.token, self.manager_page)
        if new: self.repos_list.extend(new); self.manager_page += 1; self.after(0, self.render_repos)
    
    def render_repos(self, e=None):
        for w in self.repo_scroll.winfo_children(): w.destroy()
        q = self.man_search.get().lower()
        repos = sorted(
            self.repos_list,
            key=lambda r: (not self.is_repo_pinned(r), r.get("name", "").lower())
        )
        for r in repos:
            if q and q not in r["name"].lower(): continue
            f = ctk.CTkFrame(self.repo_scroll, fg_color="transparent")
            f.pack(fill="x", pady=2)
            if self.manager_selection_mode:
                var = tk.BooleanVar(value=(r["name"] in self.selected_repos))
                ctk.CTkCheckBox(f, text="", width=20, variable=var, command=lambda x=r, v=var: self.on_check(x, v)).pack(side="left")
            pin_mark = "📌 " if self.is_repo_pinned(r) else ""
            ctk.CTkButton(
                f,
                text=f"{pin_mark}{r['name']}",
                fg_color="transparent",
                text_color="black",
                anchor="w",
                command=lambda x=r: self.show_repo(x)
            ).pack(fill="x")
    
    def toggle_selection(self): 
        self.manager_selection_mode = not self.manager_selection_mode
        self.selected_repos.clear()
        self.render_repos()
        self.update_manager_view()
    
    def filter_repos(self, e): self.render_repos()
    
    def on_check(self, r, v):
        if v.get(): self.selected_repos.add(r["name"])
        else: self.selected_repos.discard(r["name"])
        self.update_manager_view()
    
    def update_manager_view(self):
        for w in self.f_detail.winfo_children(): w.destroy()
        if self.manager_selection_mode and self.selected_repos:
            ctk.CTkLabel(self.f_detail, text=f"{len(self.selected_repos)} Selected", font=("Helvetica", 20, "bold")).pack(pady=50)
            ctk.CTkButton(self.f_detail, text="DELETE SELECTED", fg_color=COLOR_DELETE, command=self.delete_bulk).pack()
    
    def show_repo(self, r):
        if self.manager_selection_mode: return
        for w in self.f_detail.winfo_children(): w.destroy()
        ctk.CTkLabel(self.f_detail, text=r["name"], font=("Helvetica", 24, "bold")).pack(anchor="w")
        self.pv_var = tk.BooleanVar(value=r["private"])
        ctk.CTkSwitch(self.f_detail, text="Private", variable=self.pv_var, command=lambda: self.toggle_pv(r)).pack(anchor="w", pady=20)
        pin_text = "Unpin Project" if self.is_repo_pinned(r) else "Pin Project"
        ctk.CTkButton(self.f_detail, text=pin_text, command=lambda: self.toggle_repo_pin(r)).pack(pady=5)
        ctk.CTkButton(self.f_detail, text="Browser", command=lambda: webbrowser.open(r["html_url"])).pack(pady=5)
        ctk.CTkButton(self.f_detail, text="Delete", fg_color=COLOR_DELETE, command=lambda: self.delete_one(r)).pack(pady=20)

    def is_repo_pinned(self, repo):
        fid = repo.get("full_name")
        return any(x.get("full_name") == fid for x in self.favorites)

    def toggle_repo_pin(self, repo):
        fid = repo.get("full_name")
        if not fid:
            self.log("⚠️ Can't pin repo without full_name")
            return
        exists = next((x for x in self.favorites if x.get("full_name") == fid), None)
        if exists:
            self.favorites.remove(exists)
            self.log(f"📍 Unpinned: {fid}")
        else:
            self.favorites.append(repo)
            self.log(f"📌 Pinned: {fid}")
        self.save_favorites()
        self.render_repos()
        self.show_repo(repo)
    
    def toggle_pv(self, r): api_toggle_visibility(self.token, self.username, r["name"], self.pv_var.get())
    
    def delete_one(self, r):
        if messagebox.askyesno("Delete", f"Delete {r['name']}?"): 
            api_delete_repo(self.token, self.username, r["name"])
            self.repos_list.remove(r)
            self.render_repos()
            self.f_detail.winfo_children()[0].destroy()
    
    def delete_bulk(self):
        if messagebox.askyesno("Delete", f"Delete {len(self.selected_repos)} repos?"):
            for r in [x for x in self.repos_list if x["name"] in self.selected_repos]: 
                api_delete_repo(self.token, self.username, r["name"])
                self.repos_list.remove(r)
            self.selected_repos.clear()
            self.render_repos()
            self.update_manager_view()

    def build_stats_tab(self):
        t = self.tab_stats
        f_top = ctk.CTkFrame(t, fg_color="transparent")
        f_top.pack(pady=10)
        ctk.CTkLabel(f_top, text="Year:").pack(side="left")
        self.stats_combo = ctk.CTkComboBox(f_top, values=self.get_valid_years(), command=self.draw_stats)
        self.stats_combo.pack(side="left", padx=10)
        ctk.CTkButton(f_top, text="Refresh", width=60, command=lambda: self.draw_stats(self.stats_combo.get())).pack(side="left")
        self.lbl_stat = ctk.CTkLabel(t, text="Hover details", font=("Helvetica", 14))
        self.lbl_stat.pack(pady=5)
        self.stats_canvas = tk.Canvas(t, bg="white", height=160, width=800, bd=0, highlightthickness=0)
        self.stats_canvas.pack(pady=10)
        self.stats_canvas.bind("<Motion>", self.on_stat_hover)

    def draw_stats(self, year): threading.Thread(target=self._stats_thread, args=(year,), daemon=True).start()
    
    def _stats_thread(self, year):
        days = fetch_yearly_commit_data(self.username, self.token, int(year))
        self.stats_data_cache = days
        self.after(0, lambda: self._render_stats(days))
    
    def _render_stats(self, days):
        self.stats_canvas.delete("all")
        if not days: return
        try: swd = (datetime.datetime.strptime(days[0]["date"], "%Y-%m-%d").weekday() + 1) % 7
        except: swd = 0
        for i, d in enumerate(days):
            col, row = (i + swd) // 7, (i + swd) % 7
            c = d["contributionCount"]
            f = PALETTE[0]
            if c>0: f=PALETTE[1]
            if c>3: f=PALETTE[2]
            if c>6: f=PALETTE[3]
            if c>10: f=PALETTE[4]
            self.stats_canvas.create_rectangle(col*14+10, row*14+10, col*14+21, row*14+21, fill=f, outline="white", tags=f"c_{i}")
    
    def on_stat_hover(self, e):
        i = self.stats_canvas.find_closest(e.x, e.y)
        tags = self.stats_canvas.gettags(i)
        for t in tags:
            if t.startswith("c_"):
                idx = int(t.split("_")[1])
                d = self.stats_data_cache[idx]
                self.lbl_stat.configure(text=f"{d['date']}: {d['contributionCount']} commits")

if __name__ == "__main__":
    app = CleanApp()
    app.mainloop()
