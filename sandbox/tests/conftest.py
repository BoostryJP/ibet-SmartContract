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

import pytest
from brownie import web3
from web3.middleware import geth_poa_middleware

web3.middleware_onion.inject(geth_poa_middleware, layer=0)


@pytest.fixture()
def users(web3, accounts):
    admin = accounts[0]
    trader = accounts[1]
    issuer = accounts[2]
    agent = accounts[3]
    user1 = accounts[4]
    user2 = accounts[5]
    users = {
        "admin": admin,
        "trader": trader,
        "issuer": issuer,
        "agent": agent,
        "user1": user1,
        "user2": user2,
    }

    yield users


@pytest.fixture()
def personal_info(PersonalInfo, users):
    personal_info = users["admin"].deploy(PersonalInfo)
    return personal_info


@pytest.fixture()
def payment_gateway(PaymentGateway, users):
    payment_gateway = users["admin"].deploy(PaymentGateway)
    payment_gateway.addAgent.transact(users["agent"], {"from": users["admin"]})
    return payment_gateway


@pytest.fixture()
def exchange_regulator_service(ExchangeRegulatorService, users):
    admin = users["admin"]
    exchange_regulator_service = admin.deploy(ExchangeRegulatorService)
    exchange_regulator_service.register.transact(
        users["issuer"], False, {"from": admin}
    )
    exchange_regulator_service.register.transact(
        users["trader"], False, {"from": admin}
    )
    exchange_regulator_service.register.transact(users["admin"], False, {"from": admin})
    return exchange_regulator_service


@pytest.fixture()
def bond_exchange_storage(ExchangeStorage, users):
    bond_exchange_storage = users["admin"].deploy(ExchangeStorage)
    return bond_exchange_storage


@pytest.fixture()
def bond_exchange(
    IbetStraightBondExchange,
    users,
    personal_info,
    payment_gateway,
    bond_exchange_storage,
    exchange_regulator_service,
):
    deploy_args = [
        payment_gateway.address,
        personal_info.address,
        bond_exchange_storage.address,
        exchange_regulator_service.address,
    ]
    bond_exchange = users["admin"].deploy(IbetStraightBondExchange, *deploy_args)
    bond_exchange_storage.upgradeVersion.transact(
        bond_exchange.address, {"from": users["admin"]}
    )
    return bond_exchange


@pytest.fixture()
def membership_exchange_storage(ExchangeStorage, users):
    membership_exchange_storage = users["admin"].deploy(ExchangeStorage)
    return membership_exchange_storage


@pytest.fixture()
def membership_exchange(
    IbetMembershipExchange, users, payment_gateway, membership_exchange_storage
):
    deploy_args = [payment_gateway.address, membership_exchange_storage.address]
    membership_exchange = users["admin"].deploy(IbetMembershipExchange, *deploy_args)
    membership_exchange_storage.upgradeVersion.transact(
        membership_exchange.address, {"from": users["admin"]}
    )
    return membership_exchange


@pytest.fixture()
def coupon_exchange_storage(ExchangeStorage, users):
    coupon_exchange_storage = users["admin"].deploy(ExchangeStorage)
    return coupon_exchange_storage


@pytest.fixture()
def coupon_exchange(
    IbetCouponExchange, users, payment_gateway, coupon_exchange_storage
):
    deploy_args = [payment_gateway.address, coupon_exchange_storage.address]
    coupon_exchange = users["admin"].deploy(IbetCouponExchange, *deploy_args)
    coupon_exchange_storage.upgradeVersion.transact(
        coupon_exchange.address, {"from": users["admin"]}
    )
    return coupon_exchange


@pytest.fixture()
def share_exchange_storage(OTCExchangeStorage, users):
    share_exchange_storage = users["admin"].deploy(OTCExchangeStorage)
    return share_exchange_storage


@pytest.fixture()
def share_exchange(
    IbetOTCExchange,
    users,
    personal_info,
    payment_gateway,
    share_exchange_storage,
    exchange_regulator_service,
):
    deploy_args = [
        payment_gateway.address,
        personal_info.address,
        share_exchange_storage.address,
        exchange_regulator_service.address,
    ]
    share_exchange = users["admin"].deploy(IbetOTCExchange, *deploy_args)
    share_exchange_storage.upgradeVersion.transact(
        share_exchange.address, {"from": users["admin"]}
    )
    return share_exchange


@pytest.fixture()
def otc_exchange_storage(OTCExchangeStorage, users):
    otc_exchange_storage = users["admin"].deploy(OTCExchangeStorage)
    return otc_exchange_storage


@pytest.fixture()
def otc_exchange(
    IbetOTCExchange,
    users,
    personal_info,
    payment_gateway,
    otc_exchange_storage,
    exchange_regulator_service,
):
    admin = users["admin"]
    deploy_args = [
        payment_gateway.address,
        personal_info.address,
        otc_exchange_storage.address,
        exchange_regulator_service.address,
    ]
    otc_exchange = admin.deploy(IbetOTCExchange, *deploy_args)
    otc_exchange_storage.upgradeVersion.transact(otc_exchange.address, {"from": admin})
    return otc_exchange
