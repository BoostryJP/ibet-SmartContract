# -*- coding:utf-8 -*-
"""
収納代行業者（Agent）アドレス登録
・認可されたAgentアドレスをPaymentGatewayコントラクトに登録する。

Parameters
----------
contract_address : str
    PaymentGatewayコントラクトのアドレス。
    デプロイ済のものを指定する。
agent_address : str
    収納代行業者のアカウントアドレス。

"""
import os

import sys
from brownie import accounts, project, network

# brownieプロジェクトを読み込む
p = project.load('.', name="ibet_smart_contract")
p.load_config()
from brownie.project.ibet_smart_contract import PaymentGateway

APP_ENV = os.environ.get('APP_ENV') or 'local'
if APP_ENV == 'local':
    network_id = 'development'
else:
    network_id = 'ganache'
network.connect(network_id)

contract_address = sys.argv[1]
agent_address = sys.argv[2]


def main():
    deployer = accounts[0]

    payment_gateway = PaymentGateway(contract_address)

    payment_gateway.addAgent.transact(agent_address, {'from': deployer})

    agent_available = payment_gateway.getAgent(agent_address)
    print(agent_available)


if __name__ == '__main__':
    main()
