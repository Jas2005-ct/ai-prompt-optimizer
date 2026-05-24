# 🚀 AI Prompt Optimizer

A modern, production-ready Django Full Stack application that transforms raw/unstructured user prompts into **optimized, structured, role-based, production-quality AI prompts**.

---

## ✨ Features

- 🧠 **Prompt Optimization Engine** – Automatically improves clarity, grammar, formatting, role, context
- 🎯 **Multiple Prompt Types** – General, Coding, SQL, UI/UX, Image Gen, API, DevOps, Documentation, Architecture
- 🔌 **Multi-LLM Support** – OpenAI, Claude, Gemini, DeepSeek, Groq, OpenRouter
- 📜 **Prompt History** – Track all past optimizations
- 📋 **Prompt Templates** – Pre-built templates per category
- 📊 **Analytics Dashboard** – Usage and optimization stats
- 🐳 **Docker Ready** – One-command deployment
- 🔄 **HTMX + Alpine.js** – Reactive UI without heavy JS

---

## 🏗️ Architecture

```
core/
├── config/                    # Django settings (base, dev, prod)
├── apps/
│   ├── prompt_optimizer/      # Core optimization engine
│   ├── ai_providers/          # LLM provider abstraction layer
│   ├── prompt_templates/      # Pre-built prompt templates
│   ├── analytics/             # Usage analytics
│   ├── shared/                # Shared utilities, mixins, base classes
│   └── dashboard/             # Main dashboard views
├── static/                    # CSS, JS, Images
├── templates/                 # Django HTML templates
├── media/                     # User uploads (future)
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── .env.example
```

---

## 🛠️ Tech Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| **Backend** | Django 5.x + DRF | Mature, fast, clean |
| **Frontend** | Django Templates + HTMX + Alpine.js | Minimal JS, reactive |
| **CSS** | Tailwind CSS v3 | Modern utility-first |
| **Database** | SQLite (dev) / Supabase PostgreSQL (prod) | Flexible |
| **AI** | OpenAI / Claude / Gemini / Groq / DeepSeek | Multi-provider |
| **Cache** | Django Cache (Redis optional) | Optimized |
| **Deploy** | Docker + Render/Railway | Easy CI/CD |
| **Package Mgr** | UV | Fast Python packages |

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/Jas2005-ct/ai-prompt-optimizer.git
cd ai-prompt-optimizer

# Install UV (if not installed)
pip install uv

# Create virtualenv and install deps
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### 2. Environment Variables
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Database Setup
```bash
python manage.py migrate
python manage.py loaddata fixtures/templates.json
```

### 4. Run Development Server
```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000`

---

## 🐳 Docker

```bash
docker-compose up --build
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/optimize/` | Optimize a prompt |
| `GET` | `/api/history/` | Fetch optimization history |
| `POST` | `/api/save/` | Save a prompt |
| `GET` | `/api/templates/` | Fetch prompt templates |
| `POST` | `/api/switch-model/` | Switch AI model |

---

## 🔑 Supported AI Providers

- **OpenAI** (GPT-4o, GPT-4-turbo)
- **Anthropic Claude** (Claude 3.5 Sonnet)
- **Google Gemini** (Gemini 1.5 Pro)
- **Groq** (Llama 3, Mixtral)
- **DeepSeek** (DeepSeek Chat)
- **OpenRouter** (100+ models)

---

## 🤝 Contributing

Pull requests welcome! Open-source MVP — contributions encouraged.

---

## 📄 License

MIT License
