.PHONY: help install test test-cov test-verbose lint format lint-black format-black run db-migrate db-upgrade db-downgrade clean

help:
	@echo "Task Manager - Available Commands"
	@echo "=================================="
	@echo ""
	@echo "Setup & Dependencies:"
	@echo "  make install           Install project dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run               Run the Flask development server"
	@echo "  make lint              Lint code with ruff"
	@echo "  make format            Format code with ruff"
	@echo "  make lint-black        Lint code with black"
	@echo "  make format-black      Format code with black"
	@echo ""
	@echo "Testing:"
	@echo "  make test              Run tests"
	@echo "  make test-verbose      Run tests with verbose output"
	@echo "  make test-cov          Run tests with coverage report"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate        Create new migration"
	@echo "  make db-upgrade        Upgrade database to latest migration"
	@echo "  make db-downgrade      Downgrade database by one migration"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean             Clean up cache and build artifacts"
	@echo "  make clean-db          Drop and recreate test database"
	@echo ""

install:
	@echo "Installing dependencies..."
	uv pip install -e ".[test]" 2>/dev/null || uv sync

run:
	@echo "Starting Flask development server..."
	uv run python app.py

test:
	@echo "Running tests..."
	uv run pytest tests/

test-verbose:
	@echo "Running tests (verbose)..."
	uv run pytest tests/ -v

test-cov:
	@echo "Running tests with coverage..."
	uv run pytest tests/ --cov=. --cov-report=term-missing --cov-report=html --ignore=migrations --ignore=.venv
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	@echo "Linting code with ruff..."
	uv run ruff check . --exclude migrations

format:
	@echo "Formatting code with ruff..."
	uv run ruff format . --exclude migrations
	@echo "Checking formatting..."
	uv run ruff check . --fix --exclude migrations

lint-black:
	@echo "Linting code with black..."
	uv run black --check . --exclude "migrations|\.venv"

format-black:
	@echo "Formatting code with black..."
	uv run black . --exclude "migrations|\.venv"

db-migrate:
	@read -p "Enter migration message: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"

db-upgrade:
	@echo "Upgrading database to latest migration..."
	uv run alembic upgrade head

db-downgrade:
	@echo "Downgrading database by one migration..."
	uv run alembic downgrade -1

clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov build dist *.egg-info
	@echo "Clean complete"

clean-db:
	@echo "Dropping and recreating test database..."
	@read -p "Are you sure? (y/n) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "Recreating database..."; \
		dropdb taskmanager_dev 2>/dev/null || true; \
		createdb taskmanager_dev; \
		uv run alembic upgrade head; \
		echo "Database reset complete"; \
	else \
		echo "Cancelled"; \
	fi

.DEFAULT_GOAL := help
