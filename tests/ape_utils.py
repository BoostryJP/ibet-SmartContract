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

from ape import networks
from ape.api.transactions import ReceiptAPI
from ape.contracts import ContractEvent
from ape.pytest.contextmanagers import RevertsContextManager
from eth_utils.address import to_checksum_address
from eth_utils.conversions import to_hex

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def _custom_error_type(contract_container, error_name: str):
    matching_errors = [
        abi for abi in contract_container.contract_type.errors if abi.name == error_name
    ]

    if len(matching_errors) == 1:
        return getattr(contract_container, error_name)

    error_abi = matching_errors[0]
    return contract_container._create_custom_error_type(error_abi)


def reverts(
    expected: Any = None,
    error_name: str | None = None,
    **error_inputs,
):
    """
    Context manager for asserting that a transaction reverts with a specific error.

    Parameters:
    - expected: The expected error message or pattern. This can be a string or a regular expression pattern.
    - error_name: The name of the custom error to check for. If provided, this will be used to construct the expected error message.
    - error_inputs: Additional inputs for custom errors, if applicable.

    Returns:
    - A context manager that can be used with a `with` statement to assert that a transaction reverts with the specified error.
    """
    if error_name is not None:
        expected_message = _custom_error_type(expected, error_name)
    else:
        expected_message = expected

    return RevertsContextManager(expected_message=expected_message, **error_inputs)


def normalize_abi_value(canonical_type: str, value: Any) -> Any:
    """
    Normalize ABI value based on its canonical type.
    """

    if canonical_type == "address":
        return to_checksum_address(value)

    if canonical_type == "bool":
        return bool(value)

    if canonical_type == "bytes32":
        return to_hex(value)

    return value


def event_args(tx: ReceiptAPI, event: ContractEvent) -> dict[str, Any]:
    """
    Extract event arguments from a transaction receipt for a specific event.
    """

    logs = tx.events.filter(event)
    if not logs:
        logs = list(tx.decode_logs(event))

    assert logs

    normalized_args = dict(logs[-1].event_arguments)
    for abi_input in event.abi.inputs:
        if abi_input.name not in normalized_args:
            continue

        normalized_args[abi_input.name] = normalize_abi_value(
            abi_input.canonical_type,
            normalized_args[abi_input.name],
        )

    return normalized_args


def has_event(tx: ReceiptAPI, event: ContractEvent) -> bool:
    """
    Check whether a transaction receipt emitted a specific event.
    """

    return bool(tx.events.filter(event) or list(tx.decode_logs(event)))


def _normalize_web3_call_arg(value):
    if hasattr(value, "address"):
        return value.address

    if isinstance(value, tuple):
        return tuple(_normalize_web3_call_arg(item) for item in value)

    if isinstance(value, list):
        return [_normalize_web3_call_arg(item) for item in value]

    return value


def call_view_method(contract, method_name: str, *args):
    """
    Call a view method of a contract using Web3.py directly, bypassing Ape's call mechanism.
    """
    web3 = networks.provider.web3  # type: ignore
    abi = [
        item.model_dump(mode="json", by_alias=True, exclude_none=True)
        if hasattr(item, "model_dump")
        else item
        for item in contract.contract_type.abi
    ]
    web3_contract = web3.eth.contract(address=contract.address, abi=abi)
    normalized_args = [_normalize_web3_call_arg(arg) for arg in args]
    return getattr(web3_contract.functions, method_name)(*normalized_args).call()
