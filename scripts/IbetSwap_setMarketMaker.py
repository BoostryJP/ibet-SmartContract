# -*- coding:utf-8 -*-
import sys
import json
import os
from eth_utils import to_checksum_address
from populus import Project

"""
IbetSwapコントラクト：マーケットメイカー設定（setMarketMaker）

Parameters
----------
contract_address : str
    IbetSwapコントラクトのアドレス。
    自身がデプロイ済のものを指定する。
token_address : str
    トークンのアドレス。
market_maker_address : str
    マーケットメイカーのアカウントアドレス。

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
    token_address = sys.argv[2]
    market_maker_address = sys.argv[3]

    swap_contract = web3.eth.contract(
        address=to_checksum_address(contract_address),
        abi=contracts['IbetSwap']['abi'],
    )

    txn_hash = swap_contract.transact().setMarketMaker(token_address, market_maker_address)
    chain.wait.for_receipt(txn_hash)

    market_maker_address_after = swap_contract.call().marketMaker(token_address)
    print(market_maker_address_after)
