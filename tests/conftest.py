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
        "user2": user2
    }

    yield users


@pytest.fixture()
def personal_info(PersonalInfo, users):
    personal_info = users['admin'].deploy(PersonalInfo)
    return personal_info


@pytest.fixture()
def payment_gateway(PaymentGateway, users):
    payment_gateway = users['admin'].deploy(PaymentGateway)
    payment_gateway.addAgent.transact(
        users['agent'],
        {'from': users['admin']}
    )
    return payment_gateway


@pytest.fixture()
def exchange_storage(ExchangeStorage, users):
    exchange_storage = users['admin'].deploy(ExchangeStorage)
    return exchange_storage


@pytest.fixture()
def exchange(IbetExchange, users, payment_gateway, exchange_storage):
    deploy_args = [payment_gateway.address, exchange_storage.address]
    exchange = users['admin'].deploy(IbetExchange, *deploy_args)
    exchange_storage.upgradeVersion.transact(exchange.address, {'from': users['admin']})
    return exchange


@pytest.fixture()
def escrow_storage(EscrowStorage, users):
    escrow_storage = users['admin'].deploy(EscrowStorage)
    return escrow_storage


@pytest.fixture()
def escrow(IbetEscrow, users, escrow_storage):
    deploy_args = [escrow_storage.address]
    escrow = users['admin'].deploy(IbetEscrow, *deploy_args)
    escrow_storage.upgradeVersion.transact(escrow.address, {'from': users['admin']})
    return escrow


@pytest.fixture()
def st_escrow_storage(EscrowStorage, users):
    escrow_storage = users['admin'].deploy(EscrowStorage)
    return escrow_storage


@pytest.fixture()
def st_escrow(IbetSecurityTokenEscrow, users, st_escrow_storage):
    deploy_args = [st_escrow_storage.address]
    st_escrow = users['admin'].deploy(
        IbetSecurityTokenEscrow,
        *deploy_args
    )
    st_escrow_storage.upgradeVersion.transact(
        st_escrow.address,
        {'from': users['admin']}
    )
    return st_escrow
