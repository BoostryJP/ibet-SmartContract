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
import os
import sys

path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
path = os.path.join(os.path.dirname(__file__), '../tests')
sys.path.append(path)

from config import (
    ACCOUNT_NAME,
    ACCOUNT_PASSWORD,
    WEB3_HTTP_PROVIDER,
    CHAIN_ID,
    TX_GAS_LIMIT
)
from util import (
    TestAccount,
    ContractUtils
)

# Deploy
args = [
    True,
    "0x0123456789abcDEF0123456789abCDef01234567",
    "test text",
    1,
    2,
    b'0123456789abcdefghijklmnopqrstuv'
]
contract_address, _, _ = ContractUtils.deploy_contract(args)

# Set for checking other version
contract = ContractUtils.get_contract(contract_address)
args = [
    False,
    "0x0123456789ABCDeF0123456789aBcdEF01234568",
    "test text2",
    4,
    8,
    b'456789abcdefghijklmnopqrstuvwxyz'
]
tx = contract.functions.setItem3(*args).buildTransaction(
    transaction={
        "chainId": CHAIN_ID,
        "from": TestAccount.address,
        "gas": TX_GAS_LIMIT,
        "gasPrice": 0
    }
)
_, txn_receipt = ContractUtils.send_transaction(
    transaction=tx,
    private_key=TestAccount.private_key
)
tx = contract.functions.setOptionalItem(txn_receipt["blockNumber"]).buildTransaction(
    transaction={
        "chainId": CHAIN_ID,
        "from": TestAccount.address,
        "gas": TX_GAS_LIMIT,
        "gasPrice": 0
    }
)
ContractUtils.send_transaction(
    transaction=tx,
    private_key=TestAccount.private_key
)

print(f"{contract_address}")
