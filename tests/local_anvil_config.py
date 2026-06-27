"""
Copyright BOOSTRY Co., Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
"""

from typing import Any
from urllib.parse import urlparse

from ape import networks


def _normalized_derivation_path(value: str) -> str:
    return value.replace("{}", "").rstrip("/") + "/"


def _provider_host(host: str | None = None, port: int | None = None) -> str | None:
    if host is None and port is None:
        return None

    resolved_host = host or "127.0.0.1"
    resolved_port = port or 8545
    return f"http://{resolved_host}:{resolved_port}"


def local_foundry_provider(host: str | None = None, port: int | None = None):
    """Get the local Foundry provider with optional host and port overrides."""
    provider_settings: dict[str, Any] = {}
    if configured_host := _provider_host(host, port):
        provider_settings["host"] = configured_host

    return networks.ethereum.local.get_provider(  # type: ignore
        "foundry", provider_settings=provider_settings
    )


def local_anvil_command(host: str | None = None, port: int | None = None) -> list[str]:
    """Generate the command to start a local Anvil instance with optional host and port overrides."""
    provider = local_foundry_provider(host=host, port=port)
    parsed_uri = urlparse(provider.uri)

    command = [
        provider.anvil_bin,
        "--host",
        parsed_uri.hostname or "127.0.0.1",
        "--port",
        str(parsed_uri.port or 8545),
        "--chain-id",
        str(provider.settings.chain_id),
        "--hardfork",
        str(provider.settings.evm_version),
        "--gas-limit",
        str(provider.settings.gas_limit),
        "--gas-price",
        str(provider.settings.gas_price),
        "--block-base-fee-per-gas",
        str(provider.settings.base_fee),
        "--mnemonic",
        provider.mnemonic,
        "--accounts",
        str(provider.number_of_accounts),
        "--balance",
        str(provider.initial_balance),
        "--derivation-path",
        _normalized_derivation_path(str(provider.test_config.hd_path)),
        "--steps-tracing",
    ]
    return command
