.PHONY: install setup update format compile test

install:
	uv sync --frozen --no-install-project
	uv run pre-commit install
	npm install

setup:
	uv run ape pm install

update:
	uv lock --upgrade
	npm update

format:
	uv run ruff format && uv run ruff check --fix --select I
	npx prettier --write --plugin=prettier-plugin-solidity contracts/**/*.sol interfaces/**/*.sol

lint:
	uv run ruff check --fix

compile:
	uv run ape compile

test:
	uv run ape test --network ethereum:local:foundry tests/ ${ARG}
