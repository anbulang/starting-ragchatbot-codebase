# Development commands for RAG Chatbot

.PHONY: help install format lint check quality test clean

help: ## Show this help message
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install all dependencies
	uv sync

format: ## Format code with black and isort
	./scripts/format.sh

format-docker: ## Format code using Docker (recommended for compatibility)
	./scripts/format-docker.sh

lint: ## Run linting checks (flake8, mypy)
	./scripts/lint.sh

lint-docker: ## Run linting checks using Docker (recommended for compatibility)
	./scripts/lint-docker.sh

check: ## Run all quality checks without modifying files
	./scripts/check.sh

quality: ## Run complete quality workflow (format + lint + test)
	./scripts/quality.sh

test: ## Run tests
	uv run pytest backend/tests/ -v

clean: ## Clean up temporary files and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

# Docker commands
docker-build: ## Build Docker image
	docker build -t rag-chatbot .

docker-run: ## Run application in Docker
	docker run -p 8000:8000 --env-file .env rag-chatbot

docker-up: ## Start with docker-compose
	docker-compose up --build

# Development server
dev: ## Start development server
	./run.sh