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
import argparse
import os
import sys

from brownie import (
    accounts,
    project,
    network,
    web3
)

# brownieプロジェクトを読み込む
p = project.load('.', name="ibet_smart_contract")
p.load_config()
from brownie.project.ibet_smart_contract import (
    ExchangeStorage,
    IbetExchange
)

APP_ENV = os.environ.get('APP_ENV') or 'local'
if APP_ENV == 'local':
    network_id = 'local_network'
else:
    network_id = 'dev_network'
network.connect(network_id)


def main():
    parser = argparse.ArgumentParser(description='Upgrade DEX contracts')
    parser.add_argument(
        '-ex',
        '--exchange',
        help="Target Exchange contract address to be updated",
        action='append',
        default=[]
    )
    if len(sys.argv) == 1:
        parser.error('No arguments')
        return

    args = parser.parse_args()

    deployer = accounts[0]
    web3.geth.personal.unlock_account(
        deployer.address,
        os.environ.get('ETH_ACCOUNT_PASSWORD'),
        1000
    )

    upgrade_results = []
    try:
        # ------------------------------------
        # IbetExchange
        # ------------------------------------
        for address in args.exchange:
            exchange = _upgrade_exchange(address, deployer)
            upgrade_results.append({
                'dex': 'IbetExchange',
                'old_address': address,
                'new_address': exchange.address
            })
    finally:
        for result in upgrade_results:
            print(f'{result["dex"]} : {result["old_address"]} --> {result["new_address"]}')


def _upgrade_exchange(old_address, deployer):
    old_exchange = IbetExchange.at(old_address)

    # Storage
    exchange_storage_address = old_exchange.storageAddress({'from': deployer})
    exchange_storage = ExchangeStorage.at(exchange_storage_address)

    # IbetExchange
    deploy_args = [
        old_exchange.paymentGatewayAddress({'from': deployer}),
        exchange_storage_address
    ]
    exchange = deployer.deploy(IbetExchange, *deploy_args)

    # Upgrade Version
    exchange_storage.upgradeVersion(exchange.address, {'from': deployer})

    return exchange


if __name__ == '__main__':
    main()
