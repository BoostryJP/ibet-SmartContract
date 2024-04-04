.PHONY: install update format isort black compile test

install:
	poetry install --no-root --sync
	npm install
	poetry run pre-commit install

update:
	poetry update

format: isort black prettier

isort:
	isort .

black:
	black .

prettier:
	npx prettier --write --plugin=prettier-plugin-solidity **/*.sol

compile:
	brownie compile

test:
	pytest --network=test_network tests/ ${ARG}
