ROOT := /Users/zuevvladimir/AI/docs-agent
ROOT_PYTHON := $(ROOT)/venv/bin/python
BACKEND_PYTHON := $(ROOT)/operator_backend/.venv/bin/python
FOUNDATION_FILES := \
	$(ROOT)/tests/test_smoke_syntax.py

.PHONY: install-dev fmt lint test test-cli test-backend test-all check precommit-install

install-dev:
	python3 -m pip install -r $(ROOT)/requirements-dev.txt

fmt:
	python3 -m ruff format $(FOUNDATION_FILES)
	python3 -m ruff check --fix $(FOUNDATION_FILES)

lint:
	python3 -m ruff check $(FOUNDATION_FILES)
	python3 -m ruff format --check $(FOUNDATION_FILES)

test:
	cd $(ROOT) && $(ROOT_PYTHON) -m pytest tests/test_smoke_syntax.py

test-cli:
	cd $(ROOT) && $(ROOT_PYTHON) -m pytest

test-backend:
	cd $(ROOT) && $(BACKEND_PYTHON) -m pytest operator_backend/tests

test-all: test-cli test-backend

check:
	$(ROOT)/scripts/check.sh

precommit-install:
	cd $(ROOT) && python3 -m pre_commit install
