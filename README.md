# CareBuddy - AI-Powered Health Assistant

An intelligent conversational health assistant utilizing local Large Language Models (LLMs via Ollama) alongside RAG-enhanced medical knowledge for secure, private, and real-time inference.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![Angular](https://img.shields.io/badge/Angular-17-red.svg)](https://angular.io)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)
[![CI](https://github.com/ansh-varshney/CareBuddy/actions/workflows/ci.yml/badge.svg)](https://github.com/ansh-varshney/CareBuddy/actions/workflows/ci.yml)

---

## Technical Features

- **Real-time streaming chat:** WebSocket-powered, rapid token-by-token responses for a seamless user experience.
- **RAG pipeline architecture:** Domain-specific knowledge retrieval utilizing ChromaDB and LangChain to minimize LLM hallucination and ground responses in established literature.
- **Safety guardrail implementation:** Real-time emergency detection, crisis response protocols, and automated symptom urgency triage mechanisms that precede LLM inference.
- **Personalized context injection:** System prompts are dynamically assembled using the user's explicit medical profile parameters (age, sex, existing conditions, current medications).
- **Longitudinal symptom journaling:** Comprehensive logging of historical symptoms featuring a zero-shot AI extraction pipeline to ingest unstructured free-text descriptions.
- **Secure architecture:** JWT-based authentication combined with bcrypt password hashing and localized model execution to guarantee patient data privacy.

---

## Infrastructure Stack

| Component | Technology | Description |
|---|---|---|
| **Backend API Framework** | FastAPI | Asynchronous standard for high-throughput WebSocket endpoints |
| **Generative AI Engine** | Ollama | Local execution of foundation models (qwen2, llama3, mistral) |
| **Retrieval Architecture** | LangChain, ChromaDB | Vector search operations for dynamic context provision |
| **Client Application** | Angular 17 | Standalone component architecture |
| **Relational Database** | SQLite / PostgreSQL | Structured persistence for user data and symptom ledgers |
| **Continuous Integration** | GitHub Actions | Parallelized pipeline for linting, testing, and dependency auditing |

---

## Local Environment Initialization

### System Prerequisites
- Python 3.12+
- Node.js 20+
- [Ollama](https://ollama.ai) daemon installed and operational

### 1. Backend Service Configuration

```bash
git clone https://github.com/ansh-varshney/CareBuddy.git
cd CareBuddy/backend

# Initialize and activate the virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Provision Python dependencies
pip install -r requirements.txt

# Provision environment variable template
cp .env.example .env
```

### 2. Procure AI Models

```bash
# Recommended baseline model for development throughput:
ollama pull qwen2:1.5b

# Recommended model for high-fidelity evaluation:
ollama pull llama3
```

### 3. Initialize the Vector Store

Execute the baseline ingestion script to populate the ChromaDB vector embeddings:
```bash
cd backend
python -m knowledge_base.ingest
```

### 4. Execute Application Services

**Backend API Service:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Frontend Application:**
```bash
cd frontend
npm install
npm run start
```

Access the development client at **http://localhost:4200**. The interactive Swagger API documentation is available at **http://localhost:8000/docs**.

---

## Testing Framework

Execute the automated test suite to validate core functionality and safety assertions.

```bash
cd backend

# Provision testing utilities
pip install -r requirements-test.txt

# Execute assertions
pytest
pytest --cov=app --cov-report=term-missing
```

---

## Continuous Integration Details

This repository utilizes GitHub Actions to run the full validation pipeline automatically on pull requests and commits to the main branch. 
The pipeline configuration is strictly defined in `.github/workflows/ci.yml` and currently encompasses:
- Pydantic and FastAPI schema validation (Ruff)
- State-machine validation and regression tests (Pytest)
- Component compilation validation (ESLint)
- Supply chain security auditing (`pip-audit`, `npm audit`)

---

## Clinical Safety Abstraction

The system intercepts high-risk natural language tokens prior to routing queries to the generative engine. This rules-based classification guarantees deterministic handling of medical emergencies.

| Trigger Condition | System Response Action |
|---|---|
| **Critical Physiology** (e.g., chest pain, rapid onset numbness) | Automated directive to contact emergency services (911/108) |
| **Psychiatric Crisis** (e.g., self-harm, severe ideation) | Automated directive to contact crisis hotlines (988/iCall) |
| **Severe Trajectory** (e.g., sustained high fever) | Internal categorization as urgency level 4 for triage prioritization |
| **Standard Inquiry** | Medical disclaimer appended indicating automated, non-diagnostic response |

---

## Future Scope and Architecture Roadmap

The CareBuddy framework establishes a baseline pipeline for localized, multi-agent healthcare assistance. Future architectural phases include:

- **EHR/EMR Interoperability Layer:** Adoption of FHIR and HL7 protocols to permit bidirectional synchronization with standard institutional health records.
- **Multimodal Diagnostic Ingestion:** Enhancing the RAG pipeline to ingest diagnostic imaging and continuous biomarker data streams from connected wearables (e.g., Apple HealthKit integrations).
- **Federated Learning Pipelines:** Implementing secure, privacy-preserving federated fine-tuning across localized user instances to improve clinical accuracy without centralizing patient-identifiable information (PII).
- **Proactive Anomaly Detection:** Applying timeseries forecasting models upon longitudinal symptom journal data to predict and alert users regarding chronic condition flare-ups prior to symptomatic manifestation.
- **Provider Triaging Protocols:** Export utilities to bundle historic journal data, generated diagnostic assessments, and biomedical profiles into structured clinical summaries for direct transmission to licensed physicians.

---

## Licensing Information

MIT License 2026. 
*Disclaimer: CareBuddy is an experimental software project developed for the Google Summer of Code (GSoC) 2026. It is not licensed medical software and should not be used as a substitute for professional clinical judgment.*
