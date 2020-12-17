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
from brownie import accounts, project, network, web3

# brownieプロジェクトを読み込む
p = project.load('.', name="ibet_smart_contract")
p.load_config()
from brownie.project.ibet_smart_contract import OTCExchangeStorage, IbetOTCExchange, ExchangeStorage, \
    IbetMembershipExchange, IbetCouponExchange, IbetStraightBondExchange

APP_ENV = os.environ.get('APP_ENV') or 'local'
if APP_ENV == 'local':
    network_id = 'local_network'
else:
    network_id = 'dev_network'
network.connect(network_id)


def main():
    parser = argparse.ArgumentParser(description='DEX更新')
    parser.add_argument('-o', '--otc-exchange', help="更新対象のOTC取引コントラクトアドレス", action='append', default=[])
    parser.add_argument('-b', '--bond-exchange', help="更新対象の債券取引コントラクトアドレス", action='append', default=[])
    parser.add_argument('-c', '--coupon-exchange', help="更新対象のクーポン取引コントラクトアドレス", action='append', default=[])
    parser.add_argument('-m', '--membership-exchange', help="更新対象の会員権取引コントラクトアドレス", action='append', default=[])
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
        # IbetOTC
        # ------------------------------------
        for address in args.otc_exchange:
            otc_exchange = _upgrade_otc_exchange(address, deployer)
            upgrade_results.append({
                'dex': 'IbetOTCExchange',
                'old_address': address,
                'new_address': otc_exchange.address
            })

        # ------------------------------------
        # IbetStraightBond
        # ------------------------------------
        for address in args.bond_exchange:
            bond_exchange = _upgrade_bond_exchange(address, deployer)
            upgrade_results.append({
                'dex': 'IbetStraightBondExchange',
                'old_address': address,
                'new_address': bond_exchange.address
            })

        # ------------------------------------
        # IbetCoupon
        # ------------------------------------
        for address in args.coupon_exchange:
            coupon_exchange = _upgrade_coupon_exchange(address, deployer)
            upgrade_results.append({
                'dex': 'IbetCouponExchange',
                'old_address': address,
                'new_address': coupon_exchange.address
            })

        # ------------------------------------
        # IbetMembership
        # ------------------------------------
        for address in args.membership_exchange:
            membership_exchange = _upgrade_membership_exchange(address, deployer)
            upgrade_results.append({
                'dex': 'IbetMembershipExchange',
                'old_address': address,
                'new_address': membership_exchange.address
            })
    finally:
        for result in upgrade_results:
            print(f'{result["dex"]} : {result["old_address"]} --> {result["new_address"]}')


def _upgrade_otc_exchange(old_address, deployer):
    old_otc_exchange = IbetOTCExchange.at(old_address)

    # Storage
    otc_exchange_storage_address = old_otc_exchange.storageAddress({'from': deployer})
    otc_exchange_storage = OTCExchangeStorage.at(otc_exchange_storage_address)

    # IbetOTCExchange
    deploy_args = [
        old_otc_exchange.paymentGatewayAddress({'from': deployer}),
        old_otc_exchange.personalInfoAddress({'from': deployer}),
        otc_exchange_storage_address,
        old_otc_exchange.regulatorServiceAddress({'from': deployer})
    ]
    otc_exchange = deployer.deploy(IbetOTCExchange, *deploy_args)

    # Upgrade Version
    otc_exchange_storage.upgradeVersion.transact(otc_exchange, {'from': deployer})

    return otc_exchange


def _upgrade_bond_exchange(old_address, deployer):
    old_bond_exchange = IbetStraightBondExchange.at(old_address)

    # Storage
    bond_exchange_storage_address = old_bond_exchange.storageAddress({'from': deployer})
    bond_exchange_storage = ExchangeStorage.at(bond_exchange_storage_address)

    # IbetStraightBondExchange
    deploy_args = [
        old_bond_exchange.paymentGatewayAddress({'from': deployer}),
        old_bond_exchange.personalInfoAddress({'from': deployer}),
        bond_exchange_storage_address,
        old_bond_exchange.regulatorServiceAddress({'from': deployer})
    ]
    bond_exchange = deployer.deploy(IbetStraightBondExchange, *deploy_args)

    # Upgrade Version
    bond_exchange_storage.upgradeVersion.transact(bond_exchange.address, {'from': deployer})

    return bond_exchange


def _upgrade_coupon_exchange(old_address, deployer):
    old_coupon_exchange = IbetCouponExchange.at(old_address)

    # Storage
    coupon_exchange_storage_address = old_coupon_exchange.storageAddress({'from': deployer})
    coupon_exchange_storage = ExchangeStorage.at(coupon_exchange_storage_address)

    # IbetCouponExchange
    deploy_args = [
        old_coupon_exchange.paymentGatewayAddress({'from': deployer}),
        coupon_exchange_storage_address
    ]
    coupon_exchange = deployer.deploy(IbetCouponExchange, *deploy_args)

    # Upgrade Version
    coupon_exchange_storage.upgradeVersion.transact(coupon_exchange.address, {'from': deployer})

    return coupon_exchange


def _upgrade_membership_exchange(old_address, deployer):
    old_membership_exchange = IbetMembershipExchange.at(old_address)

    # Storage
    membership_exchange_storage_address = old_membership_exchange.storageAddress({'from': deployer})
    membership_exchange_storage = ExchangeStorage.at(membership_exchange_storage_address)

    # IbetMembershipExchange
    deploy_args = [
        old_membership_exchange.paymentGatewayAddress({'from': deployer}),
        membership_exchange_storage_address
    ]
    membership_exchange = deployer.deploy(IbetMembershipExchange, *deploy_args)

    # Upgrade Version
    membership_exchange_storage.upgradeVersion(membership_exchange.address, {'from': deployer})

    return membership_exchange


if __name__ == '__main__':
    main()
