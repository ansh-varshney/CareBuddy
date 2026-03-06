.PHONY: help dev up down build test lint clean ingest

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

dev: ## Run backend in development mode (hot reload)
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

up: ## Start all services with Docker Compose
	docker compose up -d

down: ## Stop all services
	docker compose down

build: ## Build Docker images
	docker compose build

test: ## Run backend tests
	cd backend && pytest tests/ -v --cov=app

lint: ## Run linters
	cd backend && ruff check . && ruff format --check .

clean: ## Remove containers, volumes, and cache
	docker compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true

ingest: ## Ingest medical knowledge base into ChromaDB
	cd backend && python -m knowledge_base.ingest
