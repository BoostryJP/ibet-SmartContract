# -*- coding:utf-8 -*-
import sys
import json
import os
from eth_utils import to_checksum_address
from populus import Project

"""
収納代行業者（Agent）アドレス登録
・認可されたAgentアドレスをPaymentGatewayコントラクトに登録する。

Parameters
----------
contract_address : str
    PaymentGatewayコントラクトのアドレス。
    デプロイ済のものを指定する。
agent_id : str
    収納代行業者のID。
    重複しないように割り振る。
    スクリプト内で str -> int 変換を行っている。
agent_address : str
    収納代行業者のアカウントアドレス。

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
    agent_id = int(sys.argv[2])
    agent_address = sys.argv[3]

    payment_gateway = web3.eth.contract(
        address=to_checksum_address(contract_address),
        abi=contracts['PaymentGateway']['abi'],
    )

    txn_hash = payment_gateway.transact().addAgent(agent_id, agent_address)
    chain.wait.for_receipt(txn_hash)

    agents = payment_gateway.call().getAgents()
    print(agents)
