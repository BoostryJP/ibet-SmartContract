.PHONY: install update format compile test

install:
	uv sync --frozen --no-install-project
	uv run pre-commit install
	npm install

update:
	uv lock --upgrade
	npm update

format:
	uv run ruff format && uv run ruff check --fix --select I
	npx prettier --write --plugin=prettier-plugin-solidity contracts/**/*.sol interfaces/**/*.sol sandbox/**/*.sol

lint:
	uv run ruff check --fix

compile:
	brownie compile

test:
	uv run pytest --network=test_network tests/ ${ARG}
