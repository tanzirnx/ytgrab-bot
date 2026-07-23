# ═══════════════════════════════════════════════════════════
# YTGrab Bot - Makefile
# Bot: @YTGrabDownBot
# ═══════════════════════════════════════════════════════════

.PHONY: help install run docker-build docker-run docker-stop test lint clean update

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

run: ## Run the bot
	python bot.py

docker-build: ## Build Docker image
	docker build -t ytgrab-bot .

docker-run: ## Run in Docker
	docker-compose up -d

docker-stop: ## Stop Docker container
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f ytgrab-bot

test: ## Run tests
	python -m pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage
	python -m pytest tests/ -v --cov=. --cov-report=html

lint: ## Run linter
	python -m flake8 . --max-line-length=120 --ignore=E501,W503

clean: ## Clean temp files and caches
	rm -rf /tmp/ytgrab/*
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov
	find . -name "*.pyc" -delete

update: ## Update yt-dlp
	pip install -U yt-dlp

setup: ## Full setup (install + create dirs)
	pip install -r requirements.txt
	mkdir -p logs data /tmp/ytgrab/downloads /tmp/ytgrab/processing
	cp .env.example .env
	@echo "✅ Setup complete! Edit .env with your bot token."
