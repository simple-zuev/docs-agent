ROOT := /Users/zuevvladimir/AI/docs-agent

.PHONY: install-dev fmt lint test check precommit-install

install-dev:
	python3 -m pip install -r $(ROOT)/requirements-dev.txt

fmt:
	python3 -m ruff format $(ROOT)
	python3 -m ruff check --fix $(ROOT)

lint:
	python3 -m ruff check $(ROOT)
	python3 -m ruff format --check $(ROOT)

test:
	cd $(ROOT) && python3 -m pytest

check:
	$(ROOT)/scripts/check.sh

precommit-install:
	cd $(ROOT) && python3 -m pre_commit install
