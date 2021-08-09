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

from brownie import (
    accounts,
    project,
    network,
    web3
)

p = project.load('.', name="ibet_smart_contract")
p.load_config()
from brownie.project.ibet_smart_contract import (
    TokenList,
    PersonalInfo,
    PaymentGateway,
    ExchangeStorage,
    IbetExchange,
)

APP_ENV = os.environ.get('APP_ENV') or 'local'
ETH_ACCOUNT_PASSWORD = os.environ.get('ETH_ACCOUNT_PASSWORD') or 'password'
REFER_ACCOUNT = os.environ.get('REFER_ACCOUNT') or 'GETH'
if APP_ENV == 'local':
    network_id = 'local_network'
else:
    network_id = 'dev_network'
network.connect(network_id)


def main():
    
    if REFER_ACCOUNT == 'GETH':
        deployer = accounts[0]
        web3.geth.personal.unlock_account(
            deployer.address,
            ETH_ACCOUNT_PASSWORD,
            1000
        )
    else:
        # NOTE: パスワード入力待ちあり
        deployer = accounts.load('deploy_user')

    ################################################
    # TokenList
    ################################################
    token_list = deployer.deploy(TokenList)

    ################################################
    # PersonalInfo
    ################################################
    personal_info = deployer.deploy(PersonalInfo)

    ################################################
    # PaymentGateway
    ################################################
    payment_gateway = deployer.deploy(PaymentGateway)

    ################################################
    # IbetExchange
    ################################################

    # Exchange Storage
    exchange_storage = deployer.deploy(ExchangeStorage)

    # IbetExchange
    deploy_args = [
        payment_gateway.address,
        exchange_storage.address
    ]
    exchange = deployer.deploy(IbetExchange, *deploy_args)

    # Upgrade Version
    exchange_storage.upgradeVersion.transact(exchange.address, {'from': deployer})

    print('TokenList : ' + token_list.address)
    print('PersonalInfo : ' + personal_info.address)
    print('PaymentGateway : ' + payment_gateway.address)
    print('ExchangeStorage : ' + exchange_storage.address)
    print('IbetExchange : ' + exchange.address)

if __name__ == '__main__':
    main()
