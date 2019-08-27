# -*- coding:utf-8 -*-
import sys
import json
import os
from eth_utils import to_checksum_address
from populus import Project

"""
IbetSwapコントラクト：決済トークン設定（setSettlementToken）

Parameters
----------
contract_address : str
    IbetSwapコントラクトのアドレス。
    自身がデプロイ済のものを指定する。
settlement_token_address : str
    決済トークンのアドレス。

"""

APP_ENV = os.environ.get('APP_ENV') or 'local'
if APP_ENV == 'local':
    chain_env = 'local_chain'
else:
    chain_env = 'dev_chain'

project = Project()
with project.get_chain(chain_env) as chain:
    web3 = chain.web3
    web3.eth.defaultAccount = web3.eth.accounts[0]
    web3.personal.unlockAccount(
        web3.eth.defaultAccount,
        os.environ.get('ETH_ACCOUNT_PASSWORD'),
        1000
    )

    contracts = json.load(open('build/contracts.json', 'r'))

    contract_address = sys.argv[1]
    settlement_token_address = sys.argv[2]

    swap_contract = web3.eth.contract(
        address=to_checksum_address(contract_address),
        abi=contracts['IbetSwap']['abi'],
    )

    txn_hash = swap_contract.transact().setSettlementToken(settlement_token_address)
    chain.wait.for_receipt(txn_hash)

    settlement_token_address_after = swap_contract.call().settlementTokenAddress()
    print(settlement_token_address_after)
