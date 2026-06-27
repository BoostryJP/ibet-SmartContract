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

from typing import TypedDict

import pytest
from ape import networks

pytest_plugins = ("anvil_manager",)


class Users(TypedDict):
    admin: str
    trader: str
    issuer: str
    agent: str
    user1: str
    user2: str


@pytest.fixture()
def users(accounts) -> Users:
    return {
        "admin": accounts[0],
        "trader": accounts[1],
        "issuer": accounts[2],
        "agent": accounts[3],
        "user1": accounts[4],
        "user2": accounts[5],
    }


@pytest.fixture()
def web3():
    return networks.provider.web3  # type: ignore


def _contract_fixture(contract_name: str):
    @pytest.fixture(name=contract_name)
    def fixture(project):
        return getattr(project, contract_name)

    return fixture


PersonalInfo = _contract_fixture("PersonalInfo")
PaymentGateway = _contract_fixture("PaymentGateway")
ExchangeStorage = _contract_fixture("ExchangeStorage")
IbetExchange = _contract_fixture("IbetExchange")
EscrowStorage = _contract_fixture("EscrowStorage")
IbetEscrow = _contract_fixture("IbetEscrow")
IbetSecurityTokenEscrow = _contract_fixture("IbetSecurityTokenEscrow")
DVPStorage = _contract_fixture("DVPStorage")
IbetSecurityTokenDVP = _contract_fixture("IbetSecurityTokenDVP")
ContractRegistry = _contract_fixture("ContractRegistry")
E2EMessaging = _contract_fixture("E2EMessaging")
FreezeLog = _contract_fixture("FreezeLog")
P256Wallet = _contract_fixture("P256Wallet")
SnapMessaging = _contract_fixture("SnapMessaging")
TokenList = _contract_fixture("TokenList")
IbetCoupon = _contract_fixture("IbetCoupon")
IbetERC20 = _contract_fixture("IbetERC20")
IbetERC721 = _contract_fixture("IbetERC721")
IbetMembership = _contract_fixture("IbetMembership")
IbetShare = _contract_fixture("IbetShare")
IbetStandardToken = _contract_fixture("IbetStandardToken")
IbetStraightBond = _contract_fixture("IbetStraightBond")
WalletTestReceiver = _contract_fixture("WalletTestReceiver")


@pytest.fixture()
def personal_info(PersonalInfo, users):
    personal_info = users["admin"].deploy(PersonalInfo)
    return personal_info


@pytest.fixture()
def payment_gateway(PaymentGateway, users):
    payment_gateway = users["admin"].deploy(PaymentGateway)
    payment_gateway.addAgent(users["agent"], sender=users["admin"])
    return payment_gateway


@pytest.fixture()
def exchange_storage(ExchangeStorage, users):
    exchange_storage = users["admin"].deploy(ExchangeStorage)
    return exchange_storage


@pytest.fixture()
def exchange(IbetExchange, users, payment_gateway, exchange_storage):
    deploy_args = [payment_gateway.address, exchange_storage.address]
    exchange = users["admin"].deploy(IbetExchange, *deploy_args)
    exchange_storage.upgradeVersion(exchange.address, sender=users["admin"])
    return exchange


@pytest.fixture()
def escrow_storage(EscrowStorage, users):
    escrow_storage = users["admin"].deploy(EscrowStorage)
    return escrow_storage


@pytest.fixture()
def escrow(IbetEscrow, users, escrow_storage):
    deploy_args = [escrow_storage.address]
    escrow = users["admin"].deploy(IbetEscrow, *deploy_args)
    escrow_storage.upgradeVersion(escrow.address, sender=users["admin"])
    return escrow


@pytest.fixture()
def st_escrow_storage(EscrowStorage, users):
    escrow_storage = users["admin"].deploy(EscrowStorage)
    return escrow_storage


@pytest.fixture()
def st_escrow(IbetSecurityTokenEscrow, users, st_escrow_storage):
    deploy_args = [st_escrow_storage.address]
    st_escrow = users["admin"].deploy(IbetSecurityTokenEscrow, *deploy_args)
    st_escrow_storage.upgradeVersion(st_escrow.address, sender=users["admin"])
    return st_escrow


@pytest.fixture()
def st_dvp_storage(DVPStorage, users):
    dvp_storage = users["admin"].deploy(DVPStorage)
    return dvp_storage


@pytest.fixture()
def st_dvp(IbetSecurityTokenDVP, users, st_dvp_storage):
    deploy_args = [st_dvp_storage.address]
    st_dvp = users["admin"].deploy(IbetSecurityTokenDVP, *deploy_args)
    st_dvp_storage.upgradeVersion(st_dvp.address, sender=users["admin"])
    return st_dvp
