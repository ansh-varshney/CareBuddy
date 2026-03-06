# CareBuddy — AI-Powered Health Assistant 🏥

> An intelligent conversational health assistant powered by local LLMs (via Ollama), RAG-enhanced medical knowledge, and real-time streaming chat.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![Angular](https://img.shields.io/badge/Angular-17-red.svg)](https://angular.io)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)

---

## Features

- 💬 **Real-time streaming chat** — WebSocket-powered token-by-token responses
- 🧠 **RAG pipeline** — ChromaDB + LangChain medical knowledge retrieval
- 🚨 **Safety guardrails** — Instant emergency detection, crisis response, urgency triage
- 🔄 **Model switching** — Hot-swap between llama3, qwen2, mistral, gemma at runtime
- 👤 **Personalized responses** — Medical profile (age, sex, conditions, meds) injected into system prompt
- 📋 **Symptom journal** — Log and track symptoms with AI-assisted extraction
- 🔐 **JWT authentication** — Secure user accounts with bcrypt hashing

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Python 3.11 |
| LLM | Ollama (local) — qwen2:1.5b, llama3, mistral |
| RAG | LangChain + ChromaDB |
| Frontend | Angular 17 (standalone components, WebSocket) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Cache | Redis (optional — in-memory fallback) |
| CI/CD | Jenkins (Jenkinsfile included) |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- [Ollama](https://ollama.ai) installed and running

### 1. Clone & Setup Backend

```bash
git clone https://github.com/YOUR_USERNAME/CareBuddy.git
cd CareBuddy/backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set your preferred model and secret key
```

### 2. Pull an Ollama Model

```bash
# Fast & lightweight (recommended for dev)
ollama pull qwen2:1.5b

# Or full size
ollama pull llama3
```

### 3. Seed the Knowledge Base

```bash
cd backend
python -m knowledge_base.ingest
# Output: ✅ Knowledge base ready! Total documents: 10
```

### 4. Start the Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 5. Start the Frontend

```bash
cd frontend
npm install
ng serve --port 4200
```

Open **http://localhost:4200** — register an account and start chatting.

---

## Environment Variables (`backend/.env`)

```ini
# LLM
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=qwen2:1.5b

# Database
DATABASE_URL=sqlite:///./carebuddy.db

# Auth
SECRET_KEY=your-random-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Optional
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:4200
```

---

## Running Tests

```bash
cd backend

# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# With coverage report
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_safety.py -v
```

---

## API Reference

Full interactive docs at **http://localhost:8000/docs** (Swagger UI).

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register with optional medical profile |
| `POST` | `/api/auth/login` | Login (returns JWT) |
| `GET` | `/api/auth/me` | Get user profile |
| `POST` | `/api/chat/` | Send message (REST) |
| `WS` | `/api/chat/ws/{conv_id}` | Streaming chat (WebSocket) |
| `GET` | `/api/chat/conversations` | List conversations |
| `GET` | `/api/chat/conversations/{id}` | Get conversation + messages |
| `GET/POST/DELETE` | `/api/symptoms/` | Symptom journal CRUD |
| `GET` | `/api/settings/models` | List available models |
| `PUT` | `/api/settings/models` | Switch active model |
| `GET` | `/api/settings/knowledge-base` | Knowledge base stats |
| `GET` | `/health` | Health check |

---

## CI/CD (Jenkins)

A `Jenkinsfile` is included at the project root. Pipeline stages:

```
Checkout → Backend Lint → Frontend Lint → Backend Tests → Frontend Tests
→ Security Scan → Build Docker → Push to Registry → Deploy
```

Push/Deploy stages only run on the `main` branch.

See `implementation_plan.md` for detailed Jenkins setup instructions.

---

## Project Structure

```
CareBuddy/
├── backend/
│   ├── app/
│   │   ├── api/routes/        # chat, auth, symptoms, settings, health
│   │   ├── core/              # llm_engine, rag_pipeline, triage, safety, memory
│   │   ├── models/            # SQLAlchemy User, Conversation, Message, SymptomEntry
│   │   └── utils/             # validators (Pydantic schemas)
│   ├── knowledge_base/        # Medical article ingestion scripts
│   ├── tests/                 # pytest test suite
│   ├── requirements.txt
│   ├── requirements-test.txt
│   └── Dockerfile
├── frontend/
│   ├── src/app/
│   │   ├── pages/             # chat, login, register, symptoms, settings
│   │   ├── services/          # auth, chat (WebSocket), api
│   │   ├── guards/            # authGuard, guestGuard
│   │   └── models/            # TypeScript interfaces
│   └── Dockerfile
├── Jenkinsfile
├── docker-compose.yml
└── README.md
```

---

## Safety Features

CareBuddy includes clinical safety guardrails that trigger **immediately** (no LLM wait):

| Trigger | Response |
|---|---|
| Emergency keywords (chest pain, can't breathe, seizure) | 🚨 Emergency response with 911/108 |
| Crisis keywords (suicidal, self-harm) | 💙 Crisis response with 988/iCall |
| High urgency (fever >103°F, blood in stool) | ⚠️ Flagged as urgency level 4 |
| All normal responses | Medical disclaimer appended |

---

## License

MIT License — built for the GSOC'26 CareBuddy project.
