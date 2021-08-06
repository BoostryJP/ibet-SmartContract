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
import brownie
from eth_utils import to_checksum_address
from brownie import IbetStandardToken


def init_args(exchange_address):
    name = 'test_token'
    symbol = 'MEM'
    initial_supply = 2 ** 256 - 1
    tradable_exchange = exchange_address
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'

    deploy_args = [
        name,
        symbol,
        initial_supply,
        tradable_exchange,
        contact_information,
        privacy_policy
    ]
    return deploy_args


def deploy(users, deploy_args):
    token = users['issuer'].deploy(
        IbetStandardToken,
        *deploy_args
    )
    return token


# TEST_deploy
class TestDeploy:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, exchange,
                      exchange_storage, payment_gateway):
        # assertion
        owner = exchange.owner()
        payment_gateway_address = exchange.paymentGatewayAddress()
        storage_address = exchange.storageAddress()
        assert owner == users['admin']
        assert payment_gateway_address == to_checksum_address(payment_gateway.address)
        assert storage_address == to_checksum_address(exchange_storage.address)


# TEST_tokenFallback
class TestTokenFallback:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, exchange):
        _issuer = users['issuer']
        _value = 100

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to exchange contract
        token.transfer.transact(
            exchange.address,
            _value,
            {'from': _issuer}
        )

        # assertion
        balance_membership = token.balanceOf(_issuer)
        balance_exchange = exchange.balanceOf(_issuer, token.address)
        assert balance_membership == deploy_args[2] - _value
        assert balance_exchange == _value

    # Normal_2
    # Multiple deposit
    def test_normal_2(self, users, exchange):
        _issuer = users['issuer']
        _value = 100

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to exchange contract (1)
        token.transfer.transact(
            exchange.address,
            _value,
            {'from': _issuer}
        )

        # transfer to exchange contract (2)
        token.transfer.transact(
            exchange.address,
            _value,
            {'from': _issuer}
        )

        # assertion
        balance_membership = token.balanceOf(_issuer)
        balance_exchange = exchange.balanceOf(_issuer, token.address)
        assert balance_membership == deploy_args[2] - _value * 2
        assert balance_exchange == _value * 2


# TEST_withdrawAll
class TestWithdrawAll:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, exchange):
        _issuer = users['issuer']
        _value = 2 ** 256 - 1

        # issue token
        deploy_args = init_args(exchange.address)
        membership = deploy(users, deploy_args)

        # transfer to exchange contract
        membership.transfer.transact(exchange.address, _value, {'from': _issuer})

        # withdrawAll
        tx = exchange.withdrawAll.transact(membership.address, {'from': _issuer})

        # assertion
        balance_membership = membership.balanceOf(_issuer)
        balance_exchange = exchange.balanceOf(_issuer, membership.address)
        assert balance_membership == deploy_args[2]
        assert balance_exchange == 0

        assert tx.events["Withdrawal"]["tokenAddress"] == membership.address
        assert tx.events["Withdrawal"]["accountAddress"] == _issuer

    #######################################
    # Error
    #######################################

    # Error_1
    def test_error_1(self, users, exchange):
        _issuer = users['issuer']

        # issue token
        deploy_args = init_args(exchange.address)
        membership = deploy(users, deploy_args)

        # withdrawAll
        with brownie.reverts():
            exchange.withdrawAll.transact(
                membership.address,
                {'from': _issuer}
            )

        # assertion
        balance_membership = membership.balanceOf(_issuer)
        balance_exchange = exchange.balanceOf(_issuer, membership.address)
        assert balance_membership == deploy_args[2]
        assert balance_exchange == 0


# TEST_createOrder
class TestCreateOrder:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Make order: BUY
    def test_normal_1(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make order: BUY
        _amount = 2 ** 256 - 1
        _price = 123
        _isBuy = True

        tx = exchange.createOrder.transact(
            token.address,
            _amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
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
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0

        assert tx.events["NewOrder"]["tokenAddress"] == token.address
        assert tx.events["NewOrder"]["orderId"] == order_id
        assert tx.events["NewOrder"]["accountAddress"] == trader
        assert tx.events["NewOrder"]["isBuy"] is True
        assert tx.events["NewOrder"]["price"] == _price
        assert tx.events["NewOrder"]["amount"] == _amount
        assert tx.events["NewOrder"]["agentAddress"] == agent

    # Normal_2
    # Make order: SELL
    def test_normal_2(self, users, exchange):
        issuer = users['issuer']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 2 ** 256 - 1
        _price = 123
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _amount,
            {'from': issuer}
        )
        tx = exchange.createOrder.transact(
            token.address,
            _amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
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
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _amount
        assert exchange.commitmentOf(issuer, token.address) == _amount

        assert tx.events["NewOrder"]["tokenAddress"] == token.address
        assert tx.events["NewOrder"]["orderId"] == order_id
        assert tx.events["NewOrder"]["accountAddress"] == issuer
        assert tx.events["NewOrder"]["isBuy"] is False
        assert tx.events["NewOrder"]["price"] == _price
        assert tx.events["NewOrder"]["amount"] == _amount
        assert tx.events["NewOrder"]["agentAddress"] == agent

    #######################################
    # Error
    #######################################

    # Error_1_1
    # Make order: BUY
    # Amount must be greater than zero
    def test_error_1_1(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make order: BUY
        _amount = 0
        _price = 123
        _isBuy = True

        order_id_before = exchange.latestOrderId()
        with brownie.reverts():
            exchange.createOrder.transact(
                token.address,
                _amount,
                _price,
                _isBuy,
                agent,
                {'from': trader}
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
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # change token status
        token.setStatus.transact(False, {'from': issuer})

        # make order: BUY
        _amount = 100
        _price = 123
        _isBuy = True

        order_id_before = exchange.latestOrderId()
        with brownie.reverts():
            exchange.createOrder.transact(
                token.address,
                _amount,
                _price,
                _isBuy,
                agent,
                {'from': trader}
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
        issuer = users['issuer']
        trader = users['trader']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make order: BUY
        _amount = 0
        _price = 123
        _isBuy = True

        order_id_before = exchange.latestOrderId()
        with brownie.reverts():
            exchange.createOrder.transact(
                token.address,
                _amount,
                _price,
                _isBuy,
                users['user1'],  # invalid
                {'from': trader}
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
        issuer = users['issuer']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 2 ** 256 - 1
        _price = 123
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            0,  # zero
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # assertion
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert token.balanceOf(issuer) == deploy_args[2]

    # Error_2_2
    # Make order: SELL
    # Insufficient balance
    def test_error_2_2(self, users, exchange):
        issuer = users['issuer']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 100
        _price = 123
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            101,  # greater than deposit amount
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # assertion
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert token.balanceOf(issuer) == deploy_args[2]

    # Error_2_3
    # Make order: SELL
    # Status must be True
    def test_error_2_3(self, users, exchange):
        issuer = users['issuer']
        agent = users['agent']

        # issuer token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # change token status
        token.setStatus.transact(False, {'from': issuer})

        # transfer to contract -> make order: SELL
        _amount = 100
        _price = 123
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # assertion
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert token.balanceOf(issuer) == deploy_args[2]

    # Error_2_4
    # Make order: SELL
    # Agent must be valid
    def test_error_2_4(self, users, exchange):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 100
        _price = 123
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _amount,
            _price,
            _isBuy,
            users['user1'],  # invalid agent
            {'from': issuer}
        )

        # assertion
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert token.balanceOf(issuer) == deploy_args[2]


# TEST_cancelOrder
class TestCancelOrder:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Cancel order: BUY
    def test_normal_1(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make order: BUY
        _amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        exchange.createOrder.transact(
            token.address,
            _amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # cancel order
        order_id = exchange.latestOrderId()
        tx = exchange.cancelOrder.transact(
            order_id,
            {'from': trader}
        )

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _amount,
            _price,
            _isBuy,
            agent.address,
            True
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0

        assert tx.events["CancelOrder"]["tokenAddress"] == token.address
        assert tx.events["CancelOrder"]["orderId"] == order_id
        assert tx.events["CancelOrder"]["accountAddress"] == trader
        assert tx.events["CancelOrder"]["isBuy"] is True
        assert tx.events["CancelOrder"]["price"] == _price
        assert tx.events["CancelOrder"]["amount"] == _amount
        assert tx.events["CancelOrder"]["agentAddress"] == agent

    # Normal_2
    # Cancel order: SELL
    def test_normal_2(self, users, exchange):
        issuer = users['issuer']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # cancel order
        order_id = exchange.latestOrderId()
        tx = exchange.cancelOrder.transact(
            order_id,
            {'from': issuer}
        )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _amount,
            _price,
            _isBuy,
            agent.address,
            True
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert exchange.commitmentOf(issuer, token.address) == 0

        assert tx.events["CancelOrder"]["tokenAddress"] == token.address
        assert tx.events["CancelOrder"]["orderId"] == order_id
        assert tx.events["CancelOrder"]["accountAddress"] == issuer
        assert tx.events["CancelOrder"]["isBuy"] is False
        assert tx.events["CancelOrder"]["price"] == _price
        assert tx.events["CancelOrder"]["amount"] == _amount
        assert tx.events["CancelOrder"]["agentAddress"] == agent

    #######################################
    # Error
    #######################################

    # Error_1
    # Order ID must be less than or equal to the latest order ID
    def test_error_1(self, users, exchange):
        issuer = users['issuer']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # cancel order
        latest_order_id = exchange.latestOrderId()
        with brownie.reverts():
            exchange.cancelOrder.transact(
                latest_order_id + 1,
                {'from': issuer}
            )

        # assertion
        assert exchange.getOrder(latest_order_id) == [
            issuer.address,
            token.address,
            _amount,
            _price,
            _isBuy,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _amount
        assert exchange.commitmentOf(issuer, token.address) == _amount

    # Error_2
    # The remaining amount of the original order must be greater than zero
    def test_error_2(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        exchange.createOrder.transact(
            token.address,
            _amount,
            _price,
            True,
            agent,
            {'from': trader}
        )

        # take SELL order by issuer
        order_id = exchange.latestOrderId()
        token.transfer.transact(
            exchange.address,
            _amount,
            {'from': issuer}
        )
        exchange.executeOrder.transact(
            order_id,
            _amount,
            False,
            {'from': issuer}
        )

        # confirm agreement by agent
        agreement_id = exchange.latestAgreementId(order_id)
        exchange.confirmAgreement.transact(
            order_id,
            agreement_id,
            {'from': agent}
        )
        assert exchange.getOrder(order_id)[2] == 0

        # cancel order
        with brownie.reverts():
            exchange.cancelOrder.transact(
                order_id,
                {'from': issuer}
            )

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            0,
            _price,
            True,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _amount
        assert token.balanceOf(trader) == _amount

    # Error_3
    # Order must not have been cancelled
    def test_error_3(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order
        _amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        exchange.createOrder.transact(
            token.address,
            _amount,
            _price,
            True,
            agent,
            {'from': trader}
        )

        # cancel order (1)
        order_id = exchange.latestOrderId()
        exchange.cancelOrder.transact(order_id, {'from': trader})

        # cancel order (2)
        with brownie.reverts():
            exchange.cancelOrder.transact(order_id, {'from': trader})

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _amount,
            _price,
            True,
            agent.address,
            True
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0

    # Error_4
    # The Orderer and the Order Cancellation Executor must be the same
    def test_error_4(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        exchange.createOrder.transact(
            token.address,
            _amount,
            _price,
            True,
            agent,
            {'from': trader}
        )

        # cancel order
        order_id = exchange.latestOrderId()
        with brownie.reverts():
            exchange.cancelOrder.transact(
                order_id,
                {'from': users['user1']}
            )

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0


# TEST_executeOrder
class TestExecuteOrder:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Take order: BUY
    def test_normal_1(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _take_amount
        agreement_id = exchange.latestAgreementId(order_id)
        assert exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader.address,
            _take_amount,
            _price,
            False,
            False
        ]
        assert exchange.lastPrice(token.address) == 0

    # Normal_2
    # Take order: SELL
    def test_normal_2(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # take SELL order by issuer
        _take_amount = 2 ** 256 - 1

        order_id = exchange.latestOrderId()
        token.transfer.transact(
            exchange.address,
            _take_amount,
            {'from': issuer}
        )
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            False,
            {'from': issuer}
        )

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _take_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _take_amount
        agreement_id = exchange.latestAgreementId(order_id)
        assert exchange.getAgreement(order_id, agreement_id)[0:5] == [
            issuer,
            _take_amount,
            _price,
            False,
            False
        ]
        assert exchange.lastPrice(token.address) == 0

    #######################################
    # Error
    #######################################

    # Error_1
    # Order ID must be less than or equal to the latest order ID
    def test_error_1(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        with brownie.reverts():
            exchange.executeOrder.transact(
                order_id + 1,
                _take_amount,
                True,
                {'from': trader}
            )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.lastPrice(token.address) == 0

    # Error_2_1
    # Take order: BUY
    # Take amount must be greater than 0
    def test_error_2_1(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        order_id = exchange.latestOrderId()
        with brownie.reverts():
            exchange.executeOrder.transact(
                order_id,
                0,
                True,
                {'from': trader}
            )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.lastPrice(token.address) == 0

    # Error_2_2
    # Take order: BUY
    # The BUY/SELL type must be different from the original order
    def test_error_2_2(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        with brownie.reverts():
            exchange.executeOrder.transact(
                order_id,
                _take_amount,
                True,
                {'from': trader}
            )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.lastPrice(token.address) == 0

    # Error_2_3
    # Take order: BUY
    # The Maker and the taker must be the different
    def test_error_2_3(self, users, exchange):
        issuer = users['issuer']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        with brownie.reverts():
            exchange.executeOrder.transact(
                order_id,
                _take_amount,
                True,
                {'from': issuer}
            )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.lastPrice(token.address) == 0

    # Error_2_4
    # Take order: BUY
    # Orders that have already been canceled cannot be taken
    def test_error_2_4(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # cancel order
        order_id = exchange.latestOrderId()
        exchange.cancelOrder.transact(order_id, {'from': issuer})

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        with brownie.reverts():
            exchange.executeOrder.transact(
                order_id,
                _take_amount,
                True,
                {'from': trader}
            )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            True
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.lastPrice(token.address) == 0

    # Error_2_5
    # Take order: BUY
    # Status must be True
    def test_error_2_5(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # change token status
        token.setStatus.transact(False, {'from': issuer})

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        with brownie.reverts():
            exchange.executeOrder.transact(
                order_id,
                _take_amount,
                True,
                {'from': trader}
            )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.lastPrice(token.address) == 0

    # Error_2_6
    # Take order: BUY
    # The amount must be within the remaining amount of the make order
    def test_error_2_6(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 100
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 101
        order_id = exchange.latestOrderId()
        with brownie.reverts():
            exchange.executeOrder.transact(
                order_id,
                _take_amount,
                True,
                {'from': trader}
            )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.lastPrice(token.address) == 0

    # Error_3_1
    # Take order: SELL
    # Take amount must be greater than 0
    def test_error_3_1(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # take SELL order by issuer
        order_id = exchange.latestOrderId()
        token.transfer.transact(
            exchange.address,
            2 ** 256 - 1,
            {'from': issuer}
        )
        exchange.executeOrder.transact(
            order_id,
            0,
            False,
            {'from': issuer}
        )

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.lastPrice(token.address) == 0

    # Error_3_2
    # Take order: SELL
    # The BUY/SELL type must be different from the original order
    def test_error_3_2(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take order: SELL
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            False,
            {'from': trader}
        )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.lastPrice(token.address) == 0

    # Error_3_3
    # Take order: SELL
    # The Maker and the taker must be the different
    def test_error_3_3(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take SELL order by issuer
        _take_amount = 2 ** 256 - 1

        order_id = exchange.latestOrderId()
        token.transfer.transact(
            exchange.address,
            _take_amount,
            {'from': issuer}
        )
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            False,
            {'from': issuer}
        )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.lastPrice(token.address) == 0

    # Error_3_4
    # Take order: SELL
    # Orders that have already been canceled cannot be taken
    def test_error_3_4(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # cancel order
        order_id = exchange.latestOrderId()
        exchange.cancelOrder.transact(
            order_id,
            {'from': trader}
        )

        # take SELL order by issuer
        _take_amount = 2 ** 256 - 1

        order_id = exchange.latestOrderId()
        token.transfer.transact(
            exchange.address,
            _take_amount,
            {'from': issuer}
        )
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            False,
            {'from': issuer}
        )

        # Assert: orderbook
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            True
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.lastPrice(token.address) == 0

    # Error_3_5
    # Take order: SELL
    # Status must be True
    def test_error_3_5(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # change token status
        token.setStatus.transact(False, {'from': issuer})

        # take SELL order by issuer
        _take_amount = 2 ** 256 - 1

        order_id = exchange.latestOrderId()
        token.transfer.transact(
            exchange.address,
            _take_amount,
            {'from': issuer}
        )
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            False,
            {'from': issuer}
        )

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.lastPrice(token.address) == 0

    # Error_3_6
    # Take order: SELL
    # The deposited balance must exceed the order amount
    def test_error_3_6(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # take SELL order by issuer
        _take_amount = 100

        order_id = exchange.latestOrderId()
        token.transfer.transact(
            exchange.address,
            _take_amount,
            {'from': issuer}
        )
        exchange.executeOrder.transact(
            order_id,
            _take_amount + 1,
            False,
            {'from': issuer}
        )

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.lastPrice(token.address) == 0

    # Error_3_7
    # Take order: SELL
    # The amount must be within the remaining amount of the make order
    def test_error_3_7(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 100
        _price = 2 ** 256 - 1
        _isBuy = True

        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # take SELL order by issuer
        _take_amount = 101

        order_id = exchange.latestOrderId()
        token.transfer.transact(
            exchange.address,
            _take_amount,
            {'from': issuer}
        )
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            False,
            {'from': issuer}
        )

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.lastPrice(token.address) == 0


# TEST_confirmAgreement
class TestConfirmAgreement:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Take order: BUY
    def test_normal_1(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # confirm agreement
        agreement_id = exchange.latestAgreementId(order_id)
        tx = exchange.confirmAgreement.transact(
            order_id,
            agreement_id,
            {'from': agent}
        )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == _take_amount
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            False,
            True
        ]
        assert exchange.lastPrice(token.address) == _price

        assert tx.events["SettlementOK"]["tokenAddress"] == token.address
        assert tx.events["SettlementOK"]["orderId"] == order_id
        assert tx.events["SettlementOK"]["agreementId"] == agreement_id
        assert tx.events["SettlementOK"]["buyAddress"] == trader.address
        assert tx.events["SettlementOK"]["sellAddress"] == issuer.address
        assert tx.events["SettlementOK"]["price"] == _price
        assert tx.events["SettlementOK"]["amount"] == _take_amount
        assert tx.events["SettlementOK"]["agentAddress"] == agent.address

    # Normal_2
    # Take order: SELL
    def test_normal_2(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # take SELL order by issuer
        _take_amount = 2 ** 256 - 1

        order_id = exchange.latestOrderId()
        token.transfer.transact(
            exchange.address,
            _take_amount,
            {'from': issuer}
        )
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            False,
            {'from': issuer}
        )

        # confirm agreement
        agreement_id = exchange.latestAgreementId(order_id)
        tx = exchange.confirmAgreement.transact(
            order_id,
            agreement_id,
            {'from': agent}
        )

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _take_amount
        assert token.balanceOf(trader) == _make_amount
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.getAgreement(order_id, agreement_id)[0:5] == [
            issuer.address,
            _take_amount,
            _price,
            False,
            True
        ]
        assert exchange.lastPrice(token.address) == _price

        assert tx.events["SettlementOK"]["tokenAddress"] == token.address
        assert tx.events["SettlementOK"]["orderId"] == order_id
        assert tx.events["SettlementOK"]["agreementId"] == agreement_id
        assert tx.events["SettlementOK"]["buyAddress"] == trader.address
        assert tx.events["SettlementOK"]["sellAddress"] == issuer.address
        assert tx.events["SettlementOK"]["price"] == _price
        assert tx.events["SettlementOK"]["amount"] == _take_amount
        assert tx.events["SettlementOK"]["agentAddress"] == agent.address

    #######################################
    # Error
    #######################################

    # Error_1
    # Order ID must be less than or equal to the latest order ID
    def test_error_1(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # confirm agreement
        agreement_id = exchange.latestAgreementId(order_id)
        with brownie.reverts():
            exchange.confirmAgreement.transact(
                order_id + 1,
                agreement_id,
                {'from': agent}
            )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            False,
            False
        ]
        assert exchange.lastPrice(token.address) == 0

    # Error_2
    # Agreement ID must be less than or equal to the latest agreement ID
    def test_error_2(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # confirm agreement
        agreement_id = exchange.latestAgreementId(order_id)
        with brownie.reverts():
            exchange.confirmAgreement.transact(
                order_id,
                agreement_id + 1,
                {'from': agent}
            )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            False,
            False
        ]
        assert exchange.lastPrice(token.address) == 0

    # Error_3
    # If it has already been confirmed, it cannot be confirmed
    def test_error_3(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # confirm agreement (1)
        agreement_id = exchange.latestAgreementId(order_id)
        exchange.confirmAgreement.transact(
            order_id,
            agreement_id,
            {'from': agent}
        )

        # confirm agreement (2)
        with brownie.reverts():
            exchange.confirmAgreement.transact(
                order_id,
                agreement_id,
                {'from': agent}
            )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == _take_amount
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            False,
            True
        ]
        assert exchange.lastPrice(token.address) == _price

    # Error_4
    # If it has already been cancelled, it cannot be confirmed
    def test_error_4(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # cancel agreement
        agreement_id = exchange.latestAgreementId(order_id)
        exchange.cancelAgreement.transact(
            order_id,
            agreement_id,
            {'from': agent}
        )

        # confirm agreement
        with brownie.reverts():
            exchange.confirmAgreement.transact(
                order_id,
                agreement_id,
                {'from': agent}
            )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == 0
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            True,
            False
        ]
        assert exchange.lastPrice(token.address) == 0

    # Error_5
    # The executor must be the agent specified in the make order
    def test_error_5(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # confirm agreement
        agreement_id = exchange.latestAgreementId(order_id)
        with brownie.reverts():
            exchange.confirmAgreement.transact(
                order_id,
                agreement_id + 1,
                {'from': users['user1']}
            )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            False,
            False
        ]
        assert exchange.lastPrice(token.address) == 0


# TEST_cancelAgreement
class TestCancelAgreement:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Take order: BUY
    def test_normal_1(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # cancel agreement
        agreement_id = exchange.latestAgreementId(order_id)
        tx = exchange.cancelAgreement.transact(
            order_id,
            agreement_id,
            {'from': agent}
        )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == 0
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            True,
            False
        ]
        assert exchange.lastPrice(token.address) == 0

        assert tx.events["SettlementNG"]["tokenAddress"] == token.address
        assert tx.events["SettlementNG"]["orderId"] == order_id
        assert tx.events["SettlementNG"]["agreementId"] == agreement_id
        assert tx.events["SettlementNG"]["buyAddress"] == trader.address
        assert tx.events["SettlementNG"]["sellAddress"] == issuer.address
        assert tx.events["SettlementNG"]["price"] == _price
        assert tx.events["SettlementNG"]["amount"] == _take_amount
        assert tx.events["SettlementNG"]["agentAddress"] == agent.address

    # Normal_2
    # Take order: SELL
    def test_normal_2(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # take SELL order by issuer
        _take_amount = 2 ** 256 - 1

        order_id = exchange.latestOrderId()
        token.transfer.transact(
            exchange.address,
            _take_amount,
            {'from': issuer}
        )
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            False,
            {'from': issuer}
        )

        # cancel agreement
        agreement_id = exchange.latestAgreementId(order_id)
        tx = exchange.cancelAgreement.transact(
            order_id,
            agreement_id,
            {'from': agent}
        )

        # assertion
        assert exchange.getOrder(order_id) == [
            trader.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2]
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.getAgreement(order_id, agreement_id)[0:5] == [
            issuer.address,
            _take_amount,
            _price,
            True,
            False
        ]
        assert exchange.lastPrice(token.address) == 0

        assert tx.events["SettlementNG"]["tokenAddress"] == token.address
        assert tx.events["SettlementNG"]["orderId"] == order_id
        assert tx.events["SettlementNG"]["agreementId"] == agreement_id
        assert tx.events["SettlementNG"]["buyAddress"] == trader.address
        assert tx.events["SettlementNG"]["sellAddress"] == issuer.address
        assert tx.events["SettlementNG"]["price"] == _price
        assert tx.events["SettlementNG"]["amount"] == _take_amount
        assert tx.events["SettlementNG"]["agentAddress"] == agent.address

    #######################################
    # Error
    #######################################

    # Error_1
    # Order ID must be less than or equal to the latest order ID
    def test_error_1(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # cancel agreement
        agreement_id = exchange.latestAgreementId(order_id)
        with brownie.reverts():
            exchange.cancelAgreement.transact(
                order_id + 1,
                agreement_id,
                {'from': agent}
            )

        # assert
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader.address,
            _take_amount,
            _price,
            False,
            False
        ]
        assert exchange.lastPrice(token.address) == 0

    # Error_2
    # Agreement ID must be less than or equal to the latest agreement ID
    def test_error_2(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # cancel agreement
        agreement_id = exchange.latestAgreementId(order_id)
        with brownie.reverts():
            exchange.cancelAgreement.transact(
                order_id,
                agreement_id + 1,
                {'from': agent}
            )

        # assert
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader.address,
            _take_amount,
            _price,
            False,
            False
        ]
        assert exchange.lastPrice(token.address) == 0

    # Error_3
    # If it has already been confirmed, it cannot be confirmed
    def test_error_3(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # confirm agreement
        agreement_id = exchange.latestAgreementId(order_id)
        exchange.confirmAgreement.transact(
            order_id,
            agreement_id,
            {'from': agent}
        )

        # cancel agreement
        with brownie.reverts():
            exchange.confirmAgreement.transact(
                order_id,
                agreement_id,
                {'from': agent}
            )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == _take_amount
        assert exchange.commitmentOf(issuer, token.address) == 0
        assert exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            False,
            True
        ]
        assert exchange.lastPrice(token.address) == _price

    # Error_4
    # If it has already been cancelled, it cannot be confirmed
    def test_error_4(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # cancel agreement (1)
        agreement_id = exchange.latestAgreementId(order_id)
        exchange.cancelAgreement.transact(
            order_id,
            agreement_id,
            {'from': agent}
        )

        # cancel agreement (2)
        with brownie.reverts():
            exchange.cancelAgreement.transact(
                order_id,
                agreement_id,
                {'from': agent}
            )

        # assertion
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == 0
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            True,
            False
        ]
        assert exchange.lastPrice(token.address) == 0

    # Error_5
    # The executor must be the agent specified in the make order
    def test_error_5(self, users, exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = exchange.latestOrderId()
        exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # cancel agreement
        agreement_id = exchange.latestAgreementId(order_id)
        with brownie.reverts():
            exchange.cancelAgreement.transact(
                order_id,
                agreement_id,
                {'from': users['user1']}
            )

        # assert
        assert exchange.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert token.balanceOf(trader) == 0
        assert exchange.commitmentOf(issuer, token.address) == _make_amount
        assert exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader.address,
            _take_amount,
            _price,
            False,
            False
        ]
        assert exchange.lastPrice(token.address) == 0


# update exchange
class TestUpdateExchange:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users,
                      exchange, exchange_storage, payment_gateway,
                      IbetExchange):
        issuer = users['issuer']
        agent = users['agent']
        admin = users['admin']

        # issue token
        deploy_args = init_args(exchange.address)
        token = deploy(users, deploy_args)

        # transfer to contract -> make SELL order
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        token.transfer.transact(
            exchange.address,
            _make_amount,
            {'from': issuer}
        )
        exchange.createOrder.transact(
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # deploy new exchange contract
        exchange_new = admin.deploy(
            IbetExchange,
            payment_gateway.address,
            exchange_storage.address
        )
        exchange_storage.upgradeVersion.transact(
            exchange_new.address,
            {'from': admin}
        )

        # assertion
        order_id = exchange_new.latestOrderId()
        assert exchange_new.getOrder(order_id) == [
            issuer.address,
            token.address,
            _make_amount,
            _price,
            _isBuy,
            agent.address,
            False
        ]
        assert token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert exchange_new.balanceOf(issuer, token.address) == 0
        assert exchange_new.commitmentOf(issuer, token.address) == _make_amount
