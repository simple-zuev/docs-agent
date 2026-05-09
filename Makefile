ROOT := /Users/zuevvladimir/AI/docs-agent
FOUNDATION_FILES := \
	$(ROOT)/tests/test_smoke_syntax.py

.PHONY: install-dev fmt lint test check precommit-install

install-dev:
	python3 -m pip install -r $(ROOT)/requirements-dev.txt

fmt:
	python3 -m ruff format $(FOUNDATION_FILES)
	python3 -m ruff check --fix $(FOUNDATION_FILES)

lint:
	python3 -m ruff check $(FOUNDATION_FILES)
	python3 -m ruff format --check $(FOUNDATION_FILES)

test:
	cd $(ROOT) && python3 -m pytest tests/test_smoke_syntax.py

check:
	$(ROOT)/scripts/check.sh

precommit-install:
	cd $(ROOT) && python3 -m pre_commit install
