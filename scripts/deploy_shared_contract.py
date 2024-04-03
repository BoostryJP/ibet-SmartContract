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

import brownie
from brownie import (
    accounts,
    project,
    network,
    web3
)

p = project.load('.', name="ibet_smart_contract")
p.load_config()

from brownie.project.ibet_smart_contract import (
    E2EMessaging,
    TokenList,
    PersonalInfo,
    PaymentGateway,
    ExchangeStorage,
    IbetExchange,
    EscrowStorage,
    IbetEscrow,
    IbetSecurityTokenEscrow,
    DVPStorage,
    IbetSecurityTokenDVP,
    FreezeLog
)


def main():

    # Settings
    deployer = set_up_deployer()

    # Parse args
    args = parse_args()
    contract_type = args.get("contract_type")

    # Deploy
    if contract_type == "E2EMessaging":
        deployer.deploy(E2EMessaging)
    elif contract_type == "TokenList":
        deployer.deploy(TokenList)
    elif contract_type == "PersonalInfo":
        deployer.deploy(PersonalInfo)
    elif contract_type == "PaymentGateway":
        deployer.deploy(PaymentGateway)
    elif contract_type == "IbetExchange":
        payment_gateway_address = args.get("payment_gateway")
        # Exchange Storage
        exchange_storage = deployer.deploy(ExchangeStorage)
        # IbetExchange
        deploy_args = [
            payment_gateway_address,
            exchange_storage.address
        ]
        exchange = deployer.deploy(
            IbetExchange,
            *deploy_args
        )
        # Upgrade Version
        exchange_storage.upgradeVersion(
            exchange.address,
            {'from': deployer}
        )
    elif contract_type == "IbetEscrow":
        # Escrow Storage
        escrow_storage = deployer.deploy(EscrowStorage)
        # IbetEscrow
        deploy_args = [escrow_storage.address]
        escrow = deployer.deploy(
            IbetEscrow,
            *deploy_args
        )
        # Upgrade Version
        escrow_storage.upgradeVersion(
            escrow.address,
            {'from': deployer}
        )
    elif contract_type == "IbetSecurityTokenEscrow":
        # Escrow Storage
        escrow_storage = deployer.deploy(EscrowStorage)
        # IbetSecurityTokenEscrow
        deploy_args = [escrow_storage.address]
        escrow = deployer.deploy(
            IbetSecurityTokenEscrow,
            *deploy_args
        )
        # Upgrade Version
        escrow_storage.upgradeVersion(
            escrow.address,
            {'from': deployer}
        )
    elif contract_type == "IbetSecurityTokenDVP":
        # Escrow Storage
        dvp_storage = deployer.deploy(DVPStorage)
        # IbetSecurityTokenDVP
        deploy_args = [dvp_storage.address]
        dvp = deployer.deploy(
            IbetSecurityTokenDVP,
            *deploy_args
        )
        # Upgrade Version
        dvp_storage.upgradeVersion(
            dvp.address,
            {'from': deployer}
        )
    elif contract_type == "FreezeLog":
        deployer.deploy(FreezeLog)


def set_up_deployer():
    """Deployerの設定"""

    # 環境設定の読み込み
    APP_ENV = os.environ.get('APP_ENV') or 'local'
    ETH_ACCOUNT_PASSWORD = os.environ.get('ETH_ACCOUNT_PASSWORD') or 'password'
    REFER_ACCOUNT = os.environ.get('REFER_ACCOUNT') or 'GETH'

    if APP_ENV == 'local':
        network_id = 'local_network'
    else:
        network_id = 'main_network'
    network.connect(network_id)

    # アカウント設定
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

    return deployer


def parse_args():
    """引数の読み込み"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "arg1",
        help="Contract Type"
    )
    parser.add_argument(
        "--payment_gateway",
        help="Deployed Payment Gateway Contract",
        default=brownie.ZERO_ADDRESS
    )

    if len(sys.argv) <= 1:
        parser.error("No arguments")
        return

    _args = parser.parse_args()

    deployable_contracts = [
        "E2EMessaging",
        "TokenList",
        "PersonalInfo",
        "PaymentGateway",
        "IbetExchange",
        "IbetEscrow",
        "IbetSecurityTokenEscrow",
        "IbetSecurityTokenDVP",
        "FreezeLog"
    ]
    if _args.arg1 not in deployable_contracts:
        parser.error(f"This is a contract that cannot be deployed. : {_args.arg1}")

    args = {
        "contract_type": _args.arg1,
        "payment_gateway": _args.payment_gateway
    }

    return args


if __name__ == '__main__':
    main()
