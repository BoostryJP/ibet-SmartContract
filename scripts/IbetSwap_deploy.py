# -*- coding:utf-8 -*-
import os
from populus import Project

"""
IbetSwapコントラクト：初期デプロイ

Parameters
----------
なし

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
    web3.personal.unlockAccount(web3.eth.defaultAccount, os.environ.get('ETH_ACCOUNT_PASSWORD'), 1000)

    # Storageコントラクトのデプロイ
    exchange_storage, _ = chain.provider.deploy_contract('ExchangeStorage')

    # SettlementTokenアドレス（初期）
    settlement_token_address = '0x0000000000000000000000000000000000000000'

    # IbetSwapコントラクトのデプロイ
    deploy_args = [
        exchange_storage.address,
        settlement_token_address
    ]
    swap, _ = chain.provider.deploy_contract(
        'IbetSwap',
        deploy_transaction={'from': web3.eth.accounts[0], 'gas': 5000000},
        deploy_args=deploy_args
    )

    # バージョン変更
    exchange_storage.transact().upgradeVersion(swap.address)

    print('ExchangeStorage: ' + exchange_storage.address)
    print('IbetSwap : ' + swap.address)
