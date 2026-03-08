# file-processor — Makefile
# Use `make help` to see available targets.

.PHONY: help install install-dev lint format type-check security \
        test test-unit test-integration test-cov \
        docker-build docker-up docker-down \
        clean clean-all

PYTHON  ?= python3
PIP     ?= pip
SRC     := src/file_processor
TESTS   := tests

# ── Help ──────────────────────────────────────────────────────────────────────
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ── Installation ──────────────────────────────────────────────────────────────
install: ## Install runtime dependencies only
	$(PIP) install -e .

install-dev: ## Install development dependencies + pre-commit hooks
	$(PIP) install -e ".[dev]"
	pre-commit install

# ── Code quality ──────────────────────────────────────────────────────────────
lint: ## Run ruff linter (check only)
	ruff check $(SRC) $(TESTS)

lint-fix: ## Run ruff linter with auto-fix
	ruff check $(SRC) $(TESTS) --fix

format: ## Format code with ruff
	ruff format $(SRC) $(TESTS)

format-check: ## Check formatting without making changes
	ruff format --check $(SRC) $(TESTS)

type-check: ## Run mypy type checker
	mypy $(SRC)

security: ## Run bandit security scan
	bandit -r $(SRC) -ll

check: lint format-check type-check security ## Run all quality checks

# ── Testing ───────────────────────────────────────────────────────────────────
test: ## Run full test suite with coverage
	pytest $(TESTS) -q --tb=short

test-unit: ## Run unit tests only (fast)
	pytest $(TESTS)/unit/ -m unit -q

test-integration: ## Run integration tests
	pytest $(TESTS)/integration/ -m integration -v

test-cov: ## Run tests and open HTML coverage report
	pytest $(TESTS) --cov=$(SRC) --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

# ── Docker ────────────────────────────────────────────────────────────────────
docker-build: ## Build the Docker image
	docker build -t file-processor:latest .

docker-up: ## Start services with docker-compose
	docker compose up -d

docker-down: ## Stop services with docker-compose
	docker compose down

# ── Cleanup ───────────────────────────────────────────────────────────────────
clean: ## Remove build artefacts and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov coverage.xml .coverage

clean-all: clean ## Remove all generated files including dist/
	rm -rf dist/ build/ *.egg-info/
