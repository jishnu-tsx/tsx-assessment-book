.PHONY: help install install-dev test test-cov lint format clean run

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

test-fast: ## Run tests in parallel
	pytest tests/ -n auto

lint: ## Run linting checks
	flake8 app/ tests/ --max-line-length=88 --extend-ignore=E203,W503
	black --check --diff app/ tests/
	isort --check-only --diff app/ tests/
	mypy app/ --ignore-missing-imports

format: ## Format code
	black app/ tests/
	isort app/ tests/

security: ## Run security checks
	bandit -r app/
	safety check

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf reports/
	rm -rf .pytest_cache/

run: ## Run the application
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Run the application in production mode
	uvicorn app.main:app --host 0.0.0.0 --port 8000

docker-build: ## Build Docker image
	docker build -t tsx-assessment-book .

docker-run: ## Run Docker container
	docker run -p 8000:8000 tsx-assessment-book

ci-test: ## Run CI tests locally
	pytest tests/ -v --cov=app --cov-report=xml --cov-report=html --cov-report=term-missing
	flake8 app/ tests/ --max-line-length=88 --extend-ignore=E203,W503
	black --check --diff app/ tests/
	isort --check-only --diff app/ tests/
	mypy app/ --ignore-missing-imports
	bandit -r app/ -f json -o bandit-report.json || true
	safety check --json --output safety-report.json || true 