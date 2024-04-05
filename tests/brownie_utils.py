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

import brownie
from brownie import web3
from brownie.network.contract import Contract, ContractCall, ContractTx

_BROWNIE_RESERVED_NAMES = [
    "abi",
    "at",
    "bytecode",
    "deploy",
    "get_method",
    "info",
    "remove",
    "selectors",
    "signatures",
    "topics",
    "tx",
]
"""
Brownieコントラクトに定義済みのプロパティ名。
同名の公開関数がスマートコントラクトに存在するとBrownieでのデプロイ時にエラーになる。
"""


def force_deploy(deployer, contract, *deploy_args):
    """
    Brownieだとエラーが発生するコントラクトを強制的にデプロイする。

    Brownieでは brownie.network.contract.Contract に定義済みプロパティと
    同名の公開関数を持つコントラクトはエラーとなりデプロイできない。
    この関数はBrownieを利用せずweb3で直接デプロイすることでエラーを回避する。
    なお、この関数により生成したContractオブジェクトではBrownieが提供する一部のDebug機能は使用できない。

    使用例
    >>> returned_contract = force_deploy(deployer, contract, *deploy_args)
    >>> # 普通の関数はそのまま使用できる。
    >>> returned_contract.nameOfFunction.transact({'from': deployer})
    >>> # エラーの原因となる関数は `.functions` 経由でアクセスする。
    >>> returned_contract.functions.signatures()
    >>> returned_contract.functions.remove.transact({'from': deployer})

    :param deployer: コントラクトをデプロイするアカウント
    :param contract: Brownieのコントラクトオブジェクト
    :param deploy_args: コントラクトのコンストラクタ引数
    :return: Brownieのコントラクトインスタンス
    """
    # 引数の型変換 (Note: web3.pyとBrownieでは型変換規則が異なる)
    constructor_abi = list(
        filter(lambda entry: entry["type"] == "constructor", contract.abi)
    )
    if len(constructor_abi) == 1:
        deploy_args = brownie.convert.normalize.format_input(
            constructor_abi[0], deploy_args
        )

    # web3を用いてデプロイする
    web3_contract = web3.eth.contract(abi=contract.abi, bytecode=contract.bytecode)
    txn_hash = web3_contract.constructor(*deploy_args).transact(
        {"from": deployer.address}
    )
    receipt = web3.eth.wait_for_transaction_receipt(txn_hash)
    contract_address = receipt["contractAddress"]

    # Brownieでエラーを発生させるメソッドを取り除いたABIを作成する
    # このABIを用いることでBrownieのContractオブジェクトが作成できるようになる
    brownie_safe_abi = []
    excluded_function_abi = []
    for abi_entry in contract.abi:
        if (
            abi_entry["type"] == "function"
            and abi_entry["name"] in _BROWNIE_RESERVED_NAMES
        ):
            excluded_function_abi.append(abi_entry)
        else:
            brownie_safe_abi.append(abi_entry)

    contract_name = _resolve_contract_name(contract) + "__brownie_utils"
    brownie_contract = Contract.from_abi(
        contract_name, contract_address, brownie_safe_abi
    )

    # ABIから削除したメソッドを復元する
    # （オーバロードには未対応）
    brownie_contract.functions = _BrownieUnsafeFunctionContainer()
    for abi_entry in excluded_function_abi:
        name = abi_entry["name"]
        if _is_constant(abi_entry):
            recovered_function = ContractCall(contract_address, abi_entry, name, None)
        else:
            recovered_function = ContractTx(contract_address, abi_entry, name, None)
        setattr(brownie_contract.functions, name, recovered_function)

    return brownie_contract


class _BrownieUnsafeFunctionContainer:
    """Brownieでエラーとなるスマートコントラクトの関数を保持するクラス"""

    pass


def _resolve_contract_name(contract):
    # コントラクト名は非公開となっているため、存在確認してから取得する
    if hasattr(contract, "_name"):
        return str(contract._name)
    else:
        return "None"


def _is_constant(abi):
    if "constant" in abi:
        return abi["constant"]
    else:
        return abi["stateMutability"] in ("view", "pure")
