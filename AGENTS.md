# Repository Guidelines

## Project Structure & Module Organization

`contracts/` contains Solidity implementations grouped into `access/`, `exchange/`, `ledger/`, `payment/`, `token/`, and `utils/`. Shared interfaces live in `interfaces/`. Python tests mirror contract domains under `tests/`; shared fixtures and Anvil helpers live directly in that directory. `docs/Errors.md` documents contract errors. `tools/json_filter.py` generates distributable contract JSON in `output/`. Generated directories such as `.build/`, `output/`, and `reports/` are ignored; do not commit them.

## Build, Test, and Development Commands

Use Python 3.14, Node.js 24, uv, and Foundry Anvil. Ape pins Solidity 0.8.34 and OpenZeppelin 4.9.3 in `ape-config.yaml`.

- `make install`: install Python and Node dependencies and pre-commit hooks.
- `make setup`: install Solidity dependencies through Ape.
- `make compile`: compile contracts with Ape.
- `make test`: compile and run the full suite on `ethereum:local:foundry`.
- `uv run ape test tests/token/test_IbetERC20.py`: run one test module using the configured local network.
- `make format`: format Python and Solidity and sort Python imports.
- `make lint`: run Ruff with automatic fixes; use `uv run ruff check .` for a read-only check matching CI.

## Coding Style & Naming Conventions

Use four-space indentation. Solidity formatting follows `.prettierrc`: 80-column target, double quotes, and no bracket spacing. Python uses Ruff with an 88-column target and double quotes. Match existing PascalCase contract names and filenames, camelCase Solidity functions, and snake_case Python functions. Run formatting before submitting changes.

## Copyright & Source Comments

Preserve existing copyright and license notices. New project-owned Solidity and Python files, including tests, must carry the full `Copyright BOOSTRY Co., Ltd.` and Apache-2.0 header, including `SPDX-License-Identifier: Apache-2.0`, matching a neighboring file. Retain third-party attribution when reusing code.

New or modified code must include comments at the same level of detail as comparable existing code. Read nearby implementations first; use `contracts/payment/PaymentGateway.sol` as a Solidity reference. Follow the surrounding comment language, including Japanese where used. Document function purpose, restrictions, parameters, and return values with applicable NatSpec tags (`@notice`, `@dev`, `@param`, `@return`). Explain state variables, struct fields, mapping keys, events, and logical processing steps at the established granularity. Tests must retain equivalent scenario and step comments, such as `# deploy` and `# assertion`. Update comments with behavior changes; do not omit required explanations because the code appears self-explanatory.

## Testing Guidelines

Tests use Ape's pytest integration with Foundry Anvil. Name modules `test_<ContractName>.py`; existing suites group cases in `Test<Operation>` classes with `test_normal_*` and `test_error_*` methods. Reuse fixtures from `tests/conftest.py` and revert helpers from `tests/ape_utils.py`. Cover successful operations, authorization failures, reverts, and boundary conditions for changed behavior. No numerical coverage threshold is configured. Run affected tests during development and the full suite before submission.

## Commit & Pull Request Guidelines

Use short, imperative commit subjects matching history, such as `Update README.md` or `Bump version to 26.9`. For internal PRs, follow `.github/pull_request_template.md`: describe the change, link related issues with `Fixes #123` or `Closes #123`, list major changes, and update tests and documentation where necessary. Include validation results and ensure CI passes Ruff, Prettier, and unit tests.

External code contributions are currently not accepted, per `CONTRIBUTING.md`; external contributors should submit issues for bugs and feature requests.
