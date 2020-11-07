"""
Copyright BOOSTRY Co., Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed onan "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
"""

# 収納代行業者（Agent）アドレス登録
# ・認可されたAgentアドレスをPaymentGatewayコントラクトに登録する。
#
# Parameters
# ----------
# contract_address : str
#     PaymentGatewayコントラクトのアドレス。
#     デプロイ済のものを指定する。
# agent_address : str
#     収納代行業者のアカウントアドレス。

import os

import sys
from brownie import accounts, project, network, web3

# brownieプロジェクトを読み込む
p = project.load('.', name="ibet_smart_contract")
p.load_config()
from brownie.project.ibet_smart_contract import PaymentGateway

APP_ENV = os.environ.get('APP_ENV') or 'local'
if APP_ENV == 'local':
    network_id = 'local_network'
else:
    network_id = 'dev_network'
network.connect(network_id)

contract_address = sys.argv[1]
agent_address = sys.argv[2]


def main():
    deployer = accounts[0]
    web3.geth.personal.unlock_account(
        deployer.address,
        os.environ.get('ETH_ACCOUNT_PASSWORD'),
        1000
    )

    payment_gateway = PaymentGateway.at(contract_address)

    payment_gateway.addAgent.transact(agent_address, {'from': deployer})

    agent_available = payment_gateway.getAgent(agent_address)
    print(agent_available)


if __name__ == '__main__':
    main()
