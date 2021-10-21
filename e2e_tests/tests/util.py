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
import json
from typing import Tuple

from eth_utils import to_checksum_address
from eth_keyfile import decode_keyfile_json
from web3 import Web3
from web3.middleware import geth_poa_middleware

from config import (
    ACCOUNT_NAME,
    ACCOUNT_PASSWORD,
    WEB3_HTTP_PROVIDER,
    CHAIN_ID,
    TX_GAS_LIMIT
)

web3 = Web3(Web3.HTTPProvider(WEB3_HTTP_PROVIDER))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)


class TestAccount:
    address: str
    password: str
    keystore_json: dict
    private_key: bytes

    @classmethod
    def initialize(cls):
        keystore_json = json.load(open(f"{ACCOUNT_NAME}.json", "r"))
        address = to_checksum_address(f'0x{keystore_json["address"]}')
        password = ACCOUNT_PASSWORD
        private_key = decode_keyfile_json(
            raw_keyfile_json=keystore_json,
            password=password.encode("utf-8")
        )
        setattr(cls, "address", address)
        setattr(cls, "password", password)
        setattr(cls, "keystore_json", keystore_json)
        setattr(cls, "private_key", private_key)


class ContractUtils:

    @staticmethod
    def deploy_contract(_args: list) -> Tuple[str, dict, str]:
        """Deploy contract"""
        contract_json = json.load(open("build/contracts/E2ETest.json", "r"))
        contract = web3.eth.contract(
            abi=contract_json["abi"],
            bytecode=contract_json["bytecode"],
            bytecode_runtime=contract_json["deployedBytecode"],
        )

        # Build transaction
        tx = contract.constructor(*_args).buildTransaction(
            transaction={
                "chainId": CHAIN_ID,
                "from": TestAccount.address,
                "gas": TX_GAS_LIMIT,
                "gasPrice": 0
            }
        )
        # Send transaction
        tx_hash, txn_receipt = ContractUtils.send_transaction(
            transaction=tx,
            private_key=TestAccount.private_key
        )

        contract_address = None
        if txn_receipt is not None:
            if 'contractAddress' in txn_receipt.keys():
                contract_address = txn_receipt['contractAddress']

        return contract_address, contract_json['abi'], tx_hash

    @staticmethod
    def get_contract(contract_address: str):
        """Get contract"""
        contract_json = json.load(open("build/contracts/E2ETest.json", "r"))
        contract = web3.eth.contract(
            address=to_checksum_address(contract_address),
            abi=contract_json['abi'],
        )
        return contract

    @staticmethod
    def send_transaction(transaction: dict, private_key: bytes):
        """Send transaction"""
        _tx_from = transaction["from"]

        # Get nonce
        nonce = web3.eth.getTransactionCount(_tx_from)
        transaction["nonce"] = nonce
        signed_tx = web3.eth.account.sign_transaction(
            transaction_dict=transaction,
            private_key=private_key
        )
        # Send Transaction
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction.hex())
        txn_receipt = web3.eth.waitForTransactionReceipt(
            transaction_hash=tx_hash,
            timeout=10
        )
        if txn_receipt["status"] == 0:
            raise Exception("Error:waitForTransactionReceipt")

        return tx_hash.hex(), txn_receipt


TestAccount.initialize()
