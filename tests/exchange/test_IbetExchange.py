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

from ape import project
from ape_utils import event_args, reverts
from eth_utils.address import to_checksum_address


def init_args(tradable_exchange):
    name = "test_token"
    symbol = "MEM"
    initial_supply = 2**256 - 1
    tradable_exchange = tradable_exchange
    contact_information = "some_contact_information"
    privacy_policy = "some_privacy_policy"

    deploy_args = [
        name,
        symbol,
        initial_supply,
        tradable_exchange,
        contact_information,
        privacy_policy,
    ]
    return deploy_args


def deploy(users, deploy_args):
    token = users["issuer"].deploy(project.IbetStandardToken, *deploy_args)  # type: ignore
    return token


def deploy_share(users, deploy_args):
    token = users["issuer"].deploy(project.IbetShare, *deploy_args)  # type: ignore
    return token


def agreement(exchange, order_id, agreement_id):
    return list(exchange.getAgreement(order_id, agreement_id))


# TEST_deploy
class TestDeploy:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, exchange, exchange_storage, payment_gateway):
        # assertion
        owner = exchange.owner()
        payment_gateway_address = exchange.paymentGatewayAddress()
        storage_address = exchange.storageAddress()
        assert owner == users["admin"]
        assert payment_gateway_address == to_checksum_address(payment_gateway.address)
        assert storage_address == to_checksum_address(exchange_storage.address)


# TEST_tokenFallback
class TestTokenFallback:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, exchange):
        _issuer = users["issuer"]
        _value = 100

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to exchange contract
        token.transfer(exchange.address, _value, sender=_issuer)

        # assertion
        balance_token = token.balanceOf(_issuer)
        balance_exchange = exchange.balanceOf(_issuer, token.address)
        assert balance_token == deploy_args[2] - _value
        assert balance_exchange == _value

    # Normal_2
    # Multiple deposit
    def test_normal_2(self, users, exchange):
        _issuer = users["issuer"]
        _value = 100

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to exchange contract (1)
        token.transfer(exchange.address, _value, sender=_issuer)

        # transfer to exchange contract (2)
        token.transfer(exchange.address, _value, sender=_issuer)

        # assertion
        balance_token = token.balanceOf(_issuer)
        balance_exchange = exchange.balanceOf(_issuer, token.address)
        assert balance_token == deploy_args[2] - _value * 2
        assert balance_exchange == _value * 2


# TEST_withdraw
class TestWithdraw:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, exchange):
        _issuer = users["issuer"]
        _value = 2**256 - 1

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to exchange contract
        token.transfer(exchange.address, _value, sender=_issuer)

        # withdraw
        tx = exchange.withdraw(token.address, sender=_issuer)

        # assertion
        balance_token = token.balanceOf(_issuer)
        balance_exchange = exchange.balanceOf(_issuer, token.address)
        assert balance_token == deploy_args[2]
        assert balance_exchange == 0

        event = event_args(tx, exchange.Withdrawn)
        assert event["token"] == token.address
        assert event["account"] == _issuer

    #######################################
    # Error
    #######################################

    # Error_1
    # The balance must be greater than zero.
    def test_error_1(self, users, exchange):
        _issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # withdraw
        with reverts("210601"):
            exchange.withdraw(token.address, sender=_issuer)

        # assertion
        balance_token = token.balanceOf(_issuer)
        balance_exchange = exchange.balanceOf(_issuer, token.address)
        assert balance_token == deploy_args[2]
        assert balance_exchange == 0

    # Error_2
    # Must be transferable.
    def test_error_2(self, users, exchange):
        _issuer = users["issuer"]
        _value = 2**256 - 1

        # issue token
        deploy_args = [
            "test_share",
            "test_symbol",
            2**256 - 1,
            2**256 - 1,
            2**256 - 1,
            "20200829",
            "20200831",
            "20191231",
            2**256 - 1,
        ]
        token = deploy_share(users, deploy_args)

        # set to transferable
        token.setTransferable(True, sender=_issuer)

        # set to tradable contract
        token.setTradableExchange(exchange.address, sender=_issuer)

        # transfer to exchange contract
        token.transfer(exchange.address, _value, sender=_issuer)

        # set to not transferable
        token.setTransferable(False, sender=_issuer)

        # withdraw
        with reverts("110402"):
            exchange.withdraw(token.address, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == 0
        assert token.balanceOf(exchange.address) == deploy_args[3]
        assert exchange.balanceOf(_issuer, token.address) == deploy_args[3]


# TEST_createOrder
class TestCreateOrder:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Make order: BUY
    def test_normal_1(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make order: BUY
        _amount = 2**256 - 1
        _price = 123
        _isBuy = True

        tx = exchange.createOrder(
            token.address, _amount, _price, _isBuy, agent, sender=trader
        )

        # assertion
        order_id = exchange.latestOrderId()
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _amount,
            _price,
            _isBuy,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0

        event = event_args(tx, exchange.NewOrder)
        assert event["tokenAddress"] == token.address
        assert event["orderId"] == order_id
        assert event["accountAddress"] == trader
        assert bool(event["isBuy"]) is True
        assert event["price"] == _price
        assert event["agentAddress"] == agent

    # Normal_2
    # Make order: SELL
    def test_normal_2(self, users, exchange):
        issuer = users["issuer"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 2**256 - 1
        _price = 123
        _isBuy = False

        token.transfer(exchange.address, _amount, sender=issuer)
        tx = exchange.createOrder(
            token.address, _amount, _price, _isBuy, agent, sender=issuer
        )

        # assertion
        order_id = exchange.latestOrderId()
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _amount,
            _price,
            _isBuy,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _amount
        assert exchange.commitmentOf(issuer, token.address) == _amount

        event = event_args(tx, exchange.NewOrder)
        assert event["tokenAddress"] == token.address
        assert event["orderId"] == order_id
        assert event["accountAddress"] == issuer
        assert bool(event["isBuy"]) is False
        assert event["price"] == _price
        assert event["amount"] == _amount
        assert event["agentAddress"] == agent

    #######################################
    # Error
    #######################################

    # Error_1_1
    # Make order: BUY
    # Amount must be greater than zero
    def test_error_1_1(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make order: BUY
        _amount = 0
        _price = 123
        _isBuy = True

        order_id_before = exchange.latestOrderId()
        with reverts("210001"):
            exchange.createOrder(
                token.address, _amount, _price, _isBuy, agent, sender=trader
            )

        # assertion
        order_id_after = exchange.latestOrderId()
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert order_id_before == order_id_after

    # Error_1_2
    # Make order: BUY
    # Status must be True
    def test_error_1_2(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # change token status
        token.setStatus(False, sender=issuer)

        # make order: BUY
        _amount = 100
        _price = 123
        _isBuy = True

        order_id_before = exchange.latestOrderId()
        with reverts("210001"):
            exchange.createOrder(
                token.address, _amount, _price, _isBuy, agent, sender=trader
            )

        # assertion
        order_id_after = exchange.latestOrderId()
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert order_id_before == order_id_after

    # Error_1_3
    # Make order: BUY
    # Agent must be valid
    def test_error_1_3(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make order: BUY
        _amount = 0
        _price = 123
        _isBuy = True

        order_id_before = exchange.latestOrderId()
        with reverts("210001"):
            exchange.createOrder(
                token.address,
                _amount,
                _price,
                _isBuy,
                users["user1"],  # invalid
                sender=trader,
            )

        # assertion
        order_id_after = exchange.latestOrderId()
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert order_id_before == order_id_after

    # Error_2_1
    # Make order: SELL
    # Amount must be greater than zero
    def test_error_2_1(self, users, exchange):
        issuer = users["issuer"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 2**256 - 1
        _price = 123
        _isBuy = False

        token.transfer(exchange.address, _amount, sender=issuer)
        exchange.createOrder(
            token.address,
            0,
            _price,
            _isBuy,
            agent,
            sender=issuer,  # zero
        )

        # assertion
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert token.balanceOf(issuer) == deploy_args[2]

    # Error_2_2
    # Make order: SELL
    # Insufficient balance
    def test_error_2_2(self, users, exchange):
        issuer = users["issuer"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 100
        _price = 123
        _isBuy = False

        token.transfer(exchange.address, _amount, sender=issuer)
        exchange.createOrder(
            token.address,
            101,  # greater than deposit amount
            _price,
            _isBuy,
            agent,
            sender=issuer,
        )

        # assertion
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert token.balanceOf(issuer) == deploy_args[2]

    # Error_2_3
    # Make order: SELL
    # Status must be True
    def test_error_2_3(self, users, exchange):
        issuer = users["issuer"]
        agent = users["agent"]

        # issuer token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # change token status
        token.setStatus(False, sender=issuer)

        # transfer to contract -> make order: SELL
        _amount = 100
        _price = 123
        _isBuy = False

        token.transfer(exchange.address, _amount, sender=issuer)
        exchange.createOrder(
            token.address, _amount, _price, _isBuy, agent, sender=issuer
        )

        # assertion
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert token.balanceOf(issuer) == deploy_args[2]

    # Error_2_4
    # Make order: SELL
    # Agent must be valid
    def test_error_2_4(self, users, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 100
        _price = 123
        _isBuy = False

        token.transfer(exchange.address, _amount, sender=issuer)
        exchange.createOrder(
            token.address,
            _amount,
            _price,
            _isBuy,
            users["user1"],  # invalid agent
            sender=issuer,
        )

        # assertion
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert token.balanceOf(issuer) == deploy_args[2]

    # Error_2_5
    # Make order: SELL
    # REVERT: Must be transferable.
    def test_error_2_5(self, users, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = [
            "test_share",
            "test_symbol",
            2**256 - 1,
            2**256 - 1,
            2**256 - 1,
            "20200829",
            "20200831",
            "20191231",
            2**256 - 1,
        ]
        token = deploy_share(users, deploy_args)

        token.setTransferable(True, sender=issuer)
        token.setTradableExchange(exchange.address, sender=issuer)

        # transfer to exchange contract
        _amount = 2**256 - 1
        token.transfer(exchange.address, _amount, sender=issuer)

        # set to not transferable
        token.setTransferable(False, sender=issuer)

        # make sell order
        _price = 123
        _isBuy = False
        with reverts("110402"):
            exchange.createOrder(
                token.address,
                _amount,
                _price,
                _isBuy,
                users["user1"],  # invalid agent
                sender=issuer,
            )

        # assertion
        assert token.balanceOf(issuer) == deploy_args[3] - _amount
        assert token.balanceOf(exchange.address) == _amount
        assert exchange.balanceOf(issuer, token.address) == _amount
        assert exchange.commitmentOf(issuer, token.address) == 0


# TEST_cancelOrder
class TestCancelOrder:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Cancel order: BUY
    def test_normal_1(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make order: BUY
        _amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = True

        exchange.createOrder(
            token.address, _amount, _price, _isBuy, agent, sender=trader
        )

        # cancel order
        order_id = exchange.latestOrderId()
        tx = exchange.cancelOrder(order_id, sender=trader)

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _amount,
            _price,
            _isBuy,
            agent.address,
            True,
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0

        event = event_args(tx, exchange.CancelOrder)
        assert event["tokenAddress"] == token.address
        assert event["orderId"] == order_id
        assert event["accountAddress"] == trader
        assert bool(event["isBuy"]) is True
        assert event["price"] == _price
        assert event["amount"] == _amount
        assert event["agentAddress"] == agent

    # Normal_2
    # Cancel order: SELL
    def test_normal_2(self, users, exchange):
        issuer = users["issuer"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _amount, sender=issuer)
        exchange.createOrder(
            token.address, _amount, _price, _isBuy, agent, sender=issuer
        )

        # cancel order
        order_id = exchange.latestOrderId()
        tx = exchange.cancelOrder(order_id, sender=issuer)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _amount,
            _price,
            _isBuy,
            agent.address,
            True,
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert exchange.commitmentOf(issuer, token.address) == 0

        event = event_args(tx, exchange.CancelOrder)
        assert event["tokenAddress"] == token.address
        assert event["orderId"] == order_id
        assert event["accountAddress"] == issuer
        assert bool(event["isBuy"]) is False
        assert event["price"] == _price
        assert event["amount"] == _amount
        assert event["agentAddress"] == agent

    #######################################
    # Error
    #######################################

    # Error_1
    # REVERT: The orderId must be less than or equal to the latest order ID.
    def test_error_1(self, users, exchange):
        issuer = users["issuer"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _amount, sender=issuer)
        exchange.createOrder(
            token.address, _amount, _price, _isBuy, agent, sender=issuer
        )

        # cancel order
        latest_order_id = exchange.latestOrderId()
        with reverts("210101"):
            exchange.cancelOrder(latest_order_id + 1, sender=issuer)

        # assertion
        assert exchange.getOrder(latest_order_id) == [
            issuer.address,
            token.address,
            _amount,
            _price,
            _isBuy,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _amount
        assert exchange.commitmentOf(issuer, token.address) == _amount

    # Error_2
    # REVERT: The remaining amount of the original order must be greater than zero.
    def test_error_2(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _amount = 2**256 - 1
        _price = 2**256 - 1
        exchange.createOrder(token.address, _amount, _price, True, agent, sender=trader)

        # take SELL order by issuer
        order_id = exchange.latestOrderId()
        token.transfer(exchange.address, _amount, sender=issuer)
        exchange.executeOrder(order_id, _amount, False, sender=issuer)

        # confirm agreement by agent
        agreement_id = exchange.latestAgreementId(order_id)
        exchange.confirmAgreement(order_id, agreement_id, sender=agent)
        assert exchange.getOrder(order_id)[2] == 0

        # cancel order
        with reverts("210102"):
            exchange.cancelOrder(order_id, sender=issuer)

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            0,
            _price,
            True,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _amount
        assert token.balanceOf(trader) == _amount

    # Error_3
    # REVERT: The order to be cancelled must not have been cancelled.
    def test_error_3(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order
        _amount = 2**256 - 1
        _price = 2**256 - 1
        exchange.createOrder(token.address, _amount, _price, True, agent, sender=trader)

        # cancel order (1)
        order_id = exchange.latestOrderId()
        exchange.cancelOrder(order_id, sender=trader)

        # cancel order (2)
        with reverts("210103"):
            exchange.cancelOrder(order_id, sender=trader)

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _amount,
            _price,
            True,
            agent.address,
            True,
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0

    # Error_4
    # REVERT: msg.sender must be an orderer.
    def test_error_4(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _amount = 2**256 - 1
        _price = 2**256 - 1
        exchange.createOrder(token.address, _amount, _price, True, agent, sender=trader)

        # cancel order
        order_id = exchange.latestOrderId()
        with reverts("210104"):
            exchange.cancelOrder(order_id, sender=users["user1"])

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _amount,
            _price,
            True,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0

    # Error_5
    # Cancel order: SELL
    # REVERT: Must be transferable.
    def test_error_5(self, users, exchange):
        issuer = users["issuer"]
        agent = users["agent"]

        # issue token
        deploy_args = [
            "test_share",
            "test_symbol",
            2**256 - 1,
            2**256 - 1,
            2**256 - 1,
            "20200829",
            "20200831",
            "20191231",
            2**256 - 1,
        ]
        token = deploy_share(users, deploy_args)
        token.setTransferable(True, sender=issuer)
        token.setTradableExchange(exchange.address, sender=issuer)

        # transfer to exchange contract
        _amount = 2**256 - 1
        token.transfer(exchange.address, _amount, sender=issuer)

        # make SELL order
        _amount = 2**256 - 1
        _price = 2**256 - 1
        exchange.createOrder(
            token.address, _amount, _price, False, agent, sender=issuer
        )

        # set to not transferable
        token.setTransferable(False, sender=issuer)

        # cancel order
        order_id = exchange.latestOrderId()
        with reverts("110402"):
            exchange.cancelOrder(order_id, sender=issuer)

        # assertion
        assert token.balanceOf(issuer) == 0
        assert token.balanceOf(exchange.address) == _amount
        assert exchange.balanceOf(issuer, token.address) == 0
        assert exchange.commitmentOf(issuer, token.address) == _amount


# TEST_forceCancelOrder
class TestForceCancelOrder:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Force cancel order: BUY
    def test_normal_1(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make order: BUY
        _amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = True

        exchange.createOrder(
            token.address, _amount, _price, _isBuy, agent, sender=trader
        )

        # force cancel order
        order_id = exchange.latestOrderId()
        tx = exchange.forceCancelOrder(order_id, sender=agent)

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _amount,
            _price,
            _isBuy,
            agent.address,
            True,
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0

        event = event_args(tx, exchange.ForceCancelOrder)
        assert event["tokenAddress"] == token.address
        assert event["orderId"] == order_id
        assert event["accountAddress"] == trader
        assert bool(event["isBuy"]) is True
        assert event["price"] == _price
        assert event["amount"] == _amount
        assert event["agentAddress"] == agent

    # Normal_2
    # Force cancel order: SELL
    def test_normal_2(self, users, exchange):
        issuer = users["issuer"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _amount, sender=issuer)
        exchange.createOrder(
            token.address, _amount, _price, _isBuy, agent, sender=issuer
        )

        # force cancel order
        order_id = exchange.latestOrderId()
        tx = exchange.forceCancelOrder(order_id, sender=agent)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _amount,
            _price,
            _isBuy,
            agent.address,
            True,
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert exchange.commitmentOf(issuer, token.address) == 0

        event = event_args(tx, exchange.ForceCancelOrder)
        assert event["tokenAddress"] == token.address
        assert event["orderId"] == order_id
        assert event["accountAddress"] == issuer
        assert bool(event["isBuy"]) is False
        assert event["price"] == _price
        assert event["amount"] == _amount
        assert event["agentAddress"] == agent

    #######################################
    # Error
    #######################################

    # Error_1
    # REVERT: The orderId must be less than or equal to the latest order ID.
    def test_error_1(self, users, exchange):
        issuer = users["issuer"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _amount, sender=issuer)
        exchange.createOrder(
            token.address, _amount, _price, _isBuy, agent, sender=issuer
        )

        # cancel order
        latest_order_id = exchange.latestOrderId()
        with reverts("210201"):
            exchange.forceCancelOrder(latest_order_id + 1, sender=agent)

        # assertion
        assert exchange.getOrder(latest_order_id) == [
            issuer.address,
            token.address,
            _amount,
            _price,
            _isBuy,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _amount
        assert exchange.commitmentOf(issuer, token.address) == _amount

    # Error_2
    # REVERT: The remaining amount of the original order must be greater than zero.
    def test_error_2(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _amount = 2**256 - 1
        _price = 2**256 - 1
        exchange.createOrder(token.address, _amount, _price, True, agent, sender=trader)

        # take SELL order by issuer
        order_id = exchange.latestOrderId()
        token.transfer(exchange.address, _amount, sender=issuer)
        exchange.executeOrder(order_id, _amount, False, sender=issuer)

        # confirm agreement by agent
        agreement_id = exchange.latestAgreementId(order_id)
        exchange.confirmAgreement(order_id, agreement_id, sender=agent)
        assert exchange.getOrder(order_id)[2] == 0

        # cancel order
        with reverts("210202"):
            exchange.forceCancelOrder(order_id, sender=agent)

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            0,
            _price,
            True,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _amount
        assert token.balanceOf(trader) == _amount

    # Error_3
    # REVERT: The order to be cancelled must not have been cancelled.
    def test_error_3(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order
        _amount = 2**256 - 1
        _price = 2**256 - 1
        exchange.createOrder(token.address, _amount, _price, True, agent, sender=trader)

        # cancel order (1)
        order_id = exchange.latestOrderId()
        exchange.cancelOrder(order_id, sender=trader)

        # cancel order (2)
        with reverts("210203"):
            exchange.forceCancelOrder(order_id, sender=agent)

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _amount,
            _price,
            True,
            agent.address,
            True,
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0

    # Error_4
    # REVERT: msg.sender must be an agent.
    def test_error_4(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _amount = 2**256 - 1
        _price = 2**256 - 1
        exchange.createOrder(token.address, _amount, _price, True, agent, sender=trader)

        # cancel order
        order_id = exchange.latestOrderId()
        with reverts("210204"):
            exchange.forceCancelOrder(order_id, sender=trader)

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _amount,
            _price,
            True,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0

    # Error_5
    # Cancel order: SELL
    # REVERT: Must be transferable.
    def test_error_5(self, users, exchange):
        issuer = users["issuer"]
        agent = users["agent"]

        # issue token
        deploy_args = [
            "test_share",
            "test_symbol",
            2**256 - 1,
            2**256 - 1,
            2**256 - 1,
            "20200829",
            "20200831",
            "20191231",
            2**256 - 1,
        ]
        token = deploy_share(users, deploy_args)
        token.setTransferable(True, sender=issuer)
        token.setTradableExchange(exchange.address, sender=issuer)

        # transfer to exchange contract
        _amount = 2**256 - 1
        token.transfer(exchange.address, _amount, sender=issuer)

        # make SELL order
        _amount = 2**256 - 1
        _price = 2**256 - 1
        exchange.createOrder(
            token.address, _amount, _price, False, agent, sender=issuer
        )

        # set to not transferable
        token.setTransferable(False, sender=issuer)

        # cancel order
        order_id = exchange.latestOrderId()
        with reverts("110402"):
            exchange.forceCancelOrder(order_id, sender=agent)

        # assertion
        assert token.balanceOf(issuer) == 0
        assert token.balanceOf(exchange.address) == _amount
        assert exchange.balanceOf(issuer, token.address) == 0
        assert exchange.commitmentOf(issuer, token.address) == _amount


# TEST_executeOrder
class TestExecuteOrder:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Take order: BUY
    def test_normal_1(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take BUY order by trader
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder(order_id, _take_amount, True, sender=trader)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _take_amount
        agreement_id = exchange.latestAgreementId(order_id)
        assert agreement(exchange, order_id, agreement_id)[0:5] == [
            trader.address,
            _take_amount,
            _price,
            False,
            False,
        ]
        assert exchange.lastPrice(token.address) == 0

    # Normal_2
    # Take order: SELL
    def test_normal_2(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = True

        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=trader
        )

        # take SELL order by issuer
        _take_amount = 2**256 - 1

        order_id = exchange.latestOrderId()
        token.transfer(exchange.address, _take_amount, sender=issuer)
        exchange.executeOrder(order_id, _take_amount, False, sender=issuer)

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            True,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _take_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _take_amount
        agreement_id = exchange.latestAgreementId(order_id)
        assert agreement(exchange, order_id, agreement_id)[0:5] == [
            issuer,
            _take_amount,
            _price,
            False,
            False,
        ]
        assert exchange.lastPrice(token.address) == 0

    #######################################
    # Error
    #######################################

    # Error_1
    # Order ID must be less than or equal to the latest order ID
    def test_error_1(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take BUY order by trader
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        with reverts("210301"):
            exchange.executeOrder(order_id + 1, _take_amount, True, sender=trader)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.lastPrice(token.address) == 0

    # Error_2_1
    # Take order: BUY
    # Take amount must be greater than 0
    def test_error_2_1(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take BUY order by trader
        order_id = exchange.latestOrderId()
        with reverts("210302"):
            exchange.executeOrder(order_id, 0, True, sender=trader)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.lastPrice(token.address) == 0

    # Error_2_2
    # Take order: BUY
    # The BUY/SELL type must be different from the original order
    def test_error_2_2(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = True

        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take BUY order by trader
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        with reverts("210302"):
            exchange.executeOrder(order_id, _take_amount, True, sender=trader)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.lastPrice(token.address) == 0

    # Error_2_3
    # Take order: BUY
    # The Maker and the taker must be the different
    def test_error_2_3(self, users, exchange):
        issuer = users["issuer"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take BUY order by trader
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        with reverts("210302"):
            exchange.executeOrder(order_id, _take_amount, True, sender=issuer)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.lastPrice(token.address) == 0

    # Error_2_4
    # Take order: BUY
    # Orders that have already been canceled cannot be taken
    def test_error_2_4(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # cancel order
        order_id = exchange.latestOrderId()
        exchange.cancelOrder(order_id, sender=issuer)

        # take BUY order by trader
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        with reverts("210302"):
            exchange.executeOrder(order_id, _take_amount, True, sender=trader)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            True,
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.lastPrice(token.address) == 0

    # Error_2_5
    # Take order: BUY
    # Status must be True
    def test_error_2_5(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # change token status
        token.setStatus(False, sender=issuer)

        # take BUY order by trader
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        with reverts("210302"):
            exchange.executeOrder(order_id, _take_amount, True, sender=trader)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.lastPrice(token.address) == 0

    # Error_2_6
    # Take order: BUY
    # The amount must be within the remaining amount of the make order
    def test_error_2_6(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 100
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take BUY order by trader
        _take_amount = 101
        order_id = exchange.latestOrderId()
        with reverts("210302"):
            exchange.executeOrder(order_id, _take_amount, True, sender=trader)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.lastPrice(token.address) == 0

    # Error_3_1
    # Take order: SELL
    # Take amount must be greater than 0
    def test_error_3_1(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = True

        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=trader
        )

        # take SELL order by issuer
        order_id = exchange.latestOrderId()
        token.transfer(exchange.address, 2**256 - 1, sender=issuer)
        exchange.executeOrder(order_id, 0, False, sender=issuer)

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.lastPrice(token.address) == 0

    # Error_3_2
    # Take order: SELL
    # The BUY/SELL type must be different from the original order
    def test_error_3_2(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take order: SELL
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder(order_id, _take_amount, False, sender=trader)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.lastPrice(token.address) == 0

    # Error_3_3
    # Take order: SELL
    # The Maker and the taker must be the different
    def test_error_3_3(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = True

        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take SELL order by issuer
        _take_amount = 2**256 - 1

        order_id = exchange.latestOrderId()
        token.transfer(exchange.address, _take_amount, sender=issuer)
        exchange.executeOrder(order_id, _take_amount, False, sender=issuer)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.lastPrice(token.address) == 0

    # Error_3_4
    # Take order: SELL
    # Orders that have already been canceled cannot be taken
    def test_error_3_4(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = True

        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=trader
        )

        # cancel order
        order_id = exchange.latestOrderId()
        exchange.cancelOrder(order_id, sender=trader)

        # take SELL order by issuer
        _take_amount = 2**256 - 1

        order_id = exchange.latestOrderId()
        token.transfer(exchange.address, _take_amount, sender=issuer)
        exchange.executeOrder(order_id, _take_amount, False, sender=issuer)

        # Assert: orderbook
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            True,
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.lastPrice(token.address) == 0

    # Error_3_5
    # Take order: SELL
    # Status must be True
    def test_error_3_5(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = True

        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=trader
        )

        # change token status
        token.setStatus(False, sender=issuer)

        # take SELL order by issuer
        _take_amount = 2**256 - 1

        order_id = exchange.latestOrderId()
        token.transfer(exchange.address, _take_amount, sender=issuer)
        exchange.executeOrder(order_id, _take_amount, False, sender=issuer)

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.lastPrice(token.address) == 0

    # Error_3_6
    # Take order: SELL
    # The deposited balance must exceed the order amount
    def test_error_3_6(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = True

        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=trader
        )

        # take SELL order by issuer
        _take_amount = 100

        order_id = exchange.latestOrderId()
        token.transfer(exchange.address, _take_amount, sender=issuer)
        exchange.executeOrder(order_id, _take_amount + 1, False, sender=issuer)

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.lastPrice(token.address) == 0

    # Error_3_7
    # Take order: SELL
    # The amount must be within the remaining amount of the make order
    def test_error_3_7(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 100
        _price = 2**256 - 1
        _isBuy = True

        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=trader
        )

        # take SELL order by issuer
        _take_amount = 101

        order_id = exchange.latestOrderId()
        token.transfer(exchange.address, _take_amount, sender=issuer)
        exchange.executeOrder(order_id, _take_amount, False, sender=issuer)

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.lastPrice(token.address) == 0

    # Error_3_8
    # Take order: SELL
    # REVERT: Must be transferable.
    def test_error_3_8(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = [
            "test_share",
            "test_symbol",
            2**256 - 1,
            2**256 - 1,
            2**256 - 1,
            "20200829",
            "20200831",
            "20191231",
            2**256 - 1,
        ]
        token = deploy_share(users, deploy_args)

        token.setTransferable(True, sender=issuer)
        token.setTradableExchange(exchange.address, sender=issuer)

        # make BUY order by trader
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = True

        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=trader
        )

        # transfer to exchange contract
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        token.transfer(exchange.address, _take_amount, sender=issuer)

        # set to not transferable
        token.setTransferable(False, sender=issuer)

        # take SELL
        with reverts("110402"):
            exchange.executeOrder(
                order_id,
                _take_amount,
                False,
                sender=trader,  # invalid msg.sender
            )

        # assertion
        assert token.balanceOf(issuer) == deploy_args[2] - _take_amount
        assert token.balanceOf(trader) == 0
        assert token.balanceOf(exchange.address) == _take_amount
        assert exchange.balanceOf(issuer, token.address) == _take_amount
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.balanceOf(trader, token.address) == 0
        assert exchange.commitmentOf(trader, token.address) == 0


# TEST_confirmAgreement
class TestConfirmAgreement:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Take order: BUY
    def test_normal_1(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take BUY order by trader
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder(order_id, _take_amount, True, sender=trader)

        # confirm agreement
        agreement_id = exchange.latestAgreementId(order_id)
        tx = exchange.confirmAgreement(order_id, agreement_id, sender=agent)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == _take_amount
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert agreement(exchange, order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            False,
            True,
        ]
        assert exchange.lastPrice(token.address) == _price

        event_settlement_ok = event_args(tx, exchange.SettlementOK)
        assert event_settlement_ok["tokenAddress"] == token.address
        assert event_settlement_ok["orderId"] == order_id
        assert event_settlement_ok["agreementId"] == agreement_id
        assert event_settlement_ok["buyAddress"] == trader.address
        assert event_settlement_ok["sellAddress"] == issuer.address
        assert event_settlement_ok["price"] == _price
        assert event_settlement_ok["amount"] == _take_amount
        assert event_settlement_ok["agentAddress"] == agent.address

        event_holder_changed = event_args(tx, exchange.HolderChanged)
        assert event_holder_changed["token"] == token.address
        assert event_holder_changed["from"] == issuer.address
        assert event_holder_changed["to"] == trader.address
        assert event_holder_changed["value"] == _take_amount

    # Normal_2
    # Take order: SELL
    def test_normal_2(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = True

        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=trader
        )

        # take SELL order by issuer
        _take_amount = 2**256 - 1

        order_id = exchange.latestOrderId()
        token.transfer(exchange.address, _take_amount, sender=issuer)
        exchange.executeOrder(order_id, _take_amount, False, sender=issuer)

        # confirm agreement
        agreement_id = exchange.latestAgreementId(order_id)
        tx = exchange.confirmAgreement(order_id, agreement_id, sender=agent)

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            True,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _take_amount
        assert token.balanceOf(trader) == _make_amount
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert agreement(exchange, order_id, agreement_id)[0:5] == [
            issuer.address,
            _take_amount,
            _price,
            False,
            True,
        ]
        assert exchange.lastPrice(token.address) == _price

        event_settlement_ok = event_args(tx, exchange.SettlementOK)
        assert event_settlement_ok["tokenAddress"] == token.address
        assert event_settlement_ok["orderId"] == order_id
        assert event_settlement_ok["agreementId"] == agreement_id
        assert event_settlement_ok["buyAddress"] == trader.address
        assert event_settlement_ok["sellAddress"] == issuer.address
        assert event_settlement_ok["price"] == _price
        assert event_settlement_ok["amount"] == _take_amount
        assert event_settlement_ok["agentAddress"] == agent.address

        event_holder_changed = event_args(tx, exchange.HolderChanged)
        assert event_holder_changed["token"] == token.address
        assert event_holder_changed["from"] == issuer.address
        assert event_holder_changed["to"] == trader.address
        assert event_holder_changed["value"] == _take_amount

    #######################################
    # Error
    #######################################

    # Error_1
    # Order ID must be less than or equal to the latest order ID
    def test_error_1(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take BUY order by trader
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder(order_id, _take_amount, True, sender=trader)

        # confirm agreement
        agreement_id = exchange.latestAgreementId(order_id)
        with reverts("210401"):
            exchange.confirmAgreement(order_id + 1, agreement_id, sender=agent)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert agreement(exchange, order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            False,
            False,
        ]
        assert exchange.lastPrice(token.address) == 0

    # Error_2
    # Agreement ID must be less than or equal to the latest agreement ID
    def test_error_2(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take BUY order by trader
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder(order_id, _take_amount, True, sender=trader)

        # confirm agreement
        agreement_id = exchange.latestAgreementId(order_id)
        with reverts("210402"):
            exchange.confirmAgreement(order_id, agreement_id + 1, sender=agent)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert agreement(exchange, order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            False,
            False,
        ]
        assert exchange.lastPrice(token.address) == 0

    # Error_3
    # If it has already been confirmed, it cannot be confirmed
    def test_error_3(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take BUY order by trader
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder(order_id, _take_amount, True, sender=trader)

        # confirm agreement (1)
        agreement_id = exchange.latestAgreementId(order_id)
        exchange.confirmAgreement(order_id, agreement_id, sender=agent)

        # confirm agreement (2)
        with reverts("210403"):
            exchange.confirmAgreement(order_id, agreement_id, sender=agent)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == _take_amount
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert agreement(exchange, order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            False,
            True,
        ]
        assert exchange.lastPrice(token.address) == _price

    # Error_4
    # If it has already been cancelled, it cannot be confirmed
    def test_error_4(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take BUY order by trader
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder(order_id, _take_amount, True, sender=trader)

        # cancel agreement
        agreement_id = exchange.latestAgreementId(order_id)
        exchange.cancelAgreement(order_id, agreement_id, sender=agent)

        # confirm agreement
        with reverts("210403"):
            exchange.confirmAgreement(order_id, agreement_id, sender=agent)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == 0
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert agreement(exchange, order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            True,
            False,
        ]
        assert exchange.lastPrice(token.address) == 0

    # Error_5
    # The executor must be the agent specified in the make order
    def test_error_5(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take BUY order by trader
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder(order_id, _take_amount, True, sender=trader)

        # confirm agreement
        agreement_id = exchange.latestAgreementId(order_id)
        with reverts("210402"):
            exchange.confirmAgreement(order_id, agreement_id + 1, sender=users["user1"])

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert agreement(exchange, order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            False,
            False,
        ]
        assert exchange.lastPrice(token.address) == 0

    # Error_6
    # Take order: SELL
    # REVERT: Must be transferable.
    def test_error_6(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = [
            "test_share",
            "test_symbol",
            2**256 - 1,
            2**256 - 1,
            2**256 - 1,
            "20200829",
            "20200831",
            "20191231",
            2**256 - 1,
        ]
        token = deploy_share(users, deploy_args)

        token.setTransferable(True, sender=issuer)
        token.setTradableExchange(exchange.address, sender=issuer)

        # make BUY order by trader
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = True

        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=trader
        )

        # take SELL order by issuer
        _take_amount = 2**256 - 1

        order_id = exchange.latestOrderId()
        token.transfer(exchange.address, _take_amount, sender=issuer)
        exchange.executeOrder(order_id, _take_amount, False, sender=issuer)

        # set to not transferable
        token.setTransferable(False, sender=issuer)

        # confirm agreement
        agreement_id = exchange.latestAgreementId(order_id)
        with reverts("110402"):
            exchange.confirmAgreement(order_id, agreement_id, sender=agent)

        # assertion
        assert token.balanceOf(issuer) == deploy_args[3] - _take_amount
        assert token.balanceOf(trader) == 0
        assert token.balanceOf(exchange.address) == _take_amount
        assert exchange.balanceOf(issuer, token.address) == 0
        assert exchange.balanceOf(trader, token.address) == 0
        assert exchange.commitmentOf(issuer, token.address) == _take_amount
        assert exchange.commitmentOf(trader, token.address) == 0


# TEST_cancelAgreement
class TestCancelAgreement:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Make SELL & Take BUY
    def test_normal_1(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take BUY order by trader
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder(order_id, _take_amount, True, sender=trader)

        # cancel agreement
        agreement_id = exchange.latestAgreementId(order_id)
        tx = exchange.cancelAgreement(order_id, agreement_id, sender=agent)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == 0
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert agreement(exchange, order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            True,
            False,
        ]
        assert exchange.lastPrice(token.address) == 0

        event_settlement_ng = event_args(tx, exchange.SettlementNG)
        assert event_settlement_ng["tokenAddress"] == token.address
        assert event_settlement_ng["orderId"] == order_id
        assert event_settlement_ng["agreementId"] == agreement_id
        assert event_settlement_ng["buyAddress"] == trader.address
        assert event_settlement_ng["sellAddress"] == issuer.address
        assert event_settlement_ng["price"] == _price
        assert event_settlement_ng["amount"] == _take_amount
        assert event_settlement_ng["agentAddress"] == agent.address

    # Normal_2
    # Make BUY & Take SELL
    def test_normal_2(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = True

        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=trader
        )

        # take SELL order by issuer
        _take_amount = 2**256 - 1

        order_id = exchange.latestOrderId()
        token.transfer(exchange.address, _take_amount, sender=issuer)
        exchange.executeOrder(order_id, _take_amount, False, sender=issuer)

        # cancel agreement
        agreement_id = exchange.latestAgreementId(order_id)
        tx = exchange.cancelAgreement(order_id, agreement_id, sender=agent)

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert agreement(exchange, order_id, agreement_id)[0:5] == [
            issuer.address,
            _take_amount,
            _price,
            True,
            False,
        ]
        assert exchange.lastPrice(token.address) == 0

        event_settlement_ng = event_args(tx, exchange.SettlementNG)
        assert event_settlement_ng["tokenAddress"] == token.address
        assert event_settlement_ng["orderId"] == order_id
        assert event_settlement_ng["agreementId"] == agreement_id
        assert event_settlement_ng["buyAddress"] == trader.address
        assert event_settlement_ng["sellAddress"] == issuer.address
        assert event_settlement_ng["price"] == _price
        assert event_settlement_ng["amount"] == _take_amount
        assert event_settlement_ng["agentAddress"] == agent.address

    #######################################
    # Error
    #######################################

    # Error_1
    # Order ID must be less than or equal to the latest order ID
    def test_error_1(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take BUY order by trader
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder(order_id, _take_amount, True, sender=trader)

        # cancel agreement
        agreement_id = exchange.latestAgreementId(order_id)
        with reverts("210501"):
            exchange.cancelAgreement(order_id + 1, agreement_id, sender=agent)

        # assert
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert agreement(exchange, order_id, agreement_id)[0:5] == [
            trader.address,
            _take_amount,
            _price,
            False,
            False,
        ]
        assert exchange.lastPrice(token.address) == 0

    # Error_2
    # Agreement ID must be less than or equal to the latest agreement ID
    def test_error_2(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take BUY order by trader
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder(order_id, _take_amount, True, sender=trader)

        # cancel agreement
        agreement_id = exchange.latestAgreementId(order_id)
        with reverts("210502"):
            exchange.cancelAgreement(order_id, agreement_id + 1, sender=agent)

        # assert
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert agreement(exchange, order_id, agreement_id)[0:5] == [
            trader.address,
            _take_amount,
            _price,
            False,
            False,
        ]
        assert exchange.lastPrice(token.address) == 0

    # Error_3
    # If it has already been confirmed, it cannot be confirmed
    def test_error_3(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take BUY order by trader
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder(order_id, _take_amount, True, sender=trader)

        # confirm agreement
        agreement_id = exchange.latestAgreementId(order_id)
        exchange.confirmAgreement(order_id, agreement_id, sender=agent)

        # cancel agreement
        with reverts("210504"):
            exchange.cancelAgreement(order_id, agreement_id, sender=agent)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == _take_amount
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert agreement(exchange, order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            False,
            True,
        ]
        assert exchange.lastPrice(token.address) == _price

    # Error_4
    # If it has already been cancelled, it cannot be confirmed
    def test_error_4(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take BUY order by trader
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder(order_id, _take_amount, True, sender=trader)

        # cancel agreement (1)
        agreement_id = exchange.latestAgreementId(order_id)
        exchange.cancelAgreement(order_id, agreement_id, sender=agent)

        # cancel agreement (2)
        with reverts("210504"):
            exchange.cancelAgreement(order_id, agreement_id, sender=agent)

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == 0
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert agreement(exchange, order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            True,
            False,
        ]
        assert exchange.lastPrice(token.address) == 0

    # Error_5
    # The executor must be the agent specified in the make order
    def test_error_5(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # take BUY order by trader
        _take_amount = 2**256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder(order_id, _take_amount, True, sender=trader)

        # cancel agreement
        agreement_id = exchange.latestAgreementId(order_id)
        with reverts("210504"):
            exchange.cancelAgreement(order_id, agreement_id, sender=users["user1"])

        # assert
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert agreement(exchange, order_id, agreement_id)[0:5] == [
            trader.address,
            _take_amount,
            _price,
            False,
            False,
        ]
        assert exchange.lastPrice(token.address) == 0

    # Error_6
    # Make BUY & Take SELL
    # REVERT: Must be transferable.
    def test_error_6(self, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        agent = users["agent"]

        # issue token
        deploy_args = [
            "test_share",
            "test_symbol",
            2**256 - 1,
            2**256 - 1,
            2**256 - 1,
            "20200829",
            "20200831",
            "20191231",
            2**256 - 1,
        ]
        token = deploy_share(users, deploy_args)

        token.setTransferable(True, sender=issuer)
        token.setTradableExchange(exchange.address, sender=issuer)

        # make BUY order by trader
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = True

        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=trader
        )

        # take SELL order by issuer
        _take_amount = 2**256 - 1

        order_id = exchange.latestOrderId()
        token.transfer(exchange.address, _take_amount, sender=issuer)
        exchange.executeOrder(order_id, _take_amount, False, sender=issuer)

        # set to not transferable
        token.setTransferable(False, sender=issuer)

        # cancel agreement
        agreement_id = exchange.latestAgreementId(order_id)
        with reverts("110402"):
            exchange.cancelAgreement(order_id, agreement_id, sender=agent)

        # assertion
        assert token.balanceOf(issuer) == deploy_args[3] - _take_amount
        assert token.balanceOf(trader) == 0
        assert token.balanceOf(exchange.address) == _take_amount
        assert exchange.balanceOf(issuer, token.address) == 0
        assert exchange.balanceOf(trader, token.address) == 0
        assert exchange.commitmentOf(issuer, token.address) == _take_amount
        assert exchange.commitmentOf(trader, token.address) == 0


# update exchange
class TestUpdateExchange:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(
        self, users, exchange, exchange_storage, payment_gateway, IbetExchange
    ):
        issuer = users["issuer"]
        agent = users["agent"]
        admin = users["admin"]

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make SELL order
        _make_amount = 2**256 - 1
        _price = 2**256 - 1
        _isBuy = False

        token.transfer(exchange.address, _make_amount, sender=issuer)
        exchange.createOrder(
            token.address, _make_amount, _price, _isBuy, agent, sender=issuer
        )

        # deploy new exchange contract
        exchange_new = admin.deploy(
            IbetExchange, payment_gateway.address, exchange_storage.address
        )
        exchange_storage.upgradeVersion(exchange_new.address, sender=admin)

        # assertion
        order_id = exchange_new.latestOrderId()
        assert exchange_new.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent.address,
            False,
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert exchange_new.balanceOf(issuer, token.address) == 0
        assert exchange_new.commitmentOf(issuer, token.address) == _make_amount
