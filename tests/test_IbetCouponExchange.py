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
from brownie import IbetCoupon


def init_args(exchange_address):
    name = 'test_coupon'
    symbol = 'CPN'
    total_supply = 2 ** 256 - 1
    tradable_exchange = exchange_address
    details = 'some_details'
    return_details = 'some_return_details'
    memo = 'some_memo'
    expiration_date = '20201231'
    transferable = True
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'

    deploy_args = [
        name, symbol, total_supply, tradable_exchange,
        details, return_details,
        memo, expiration_date, transferable,
        contact_information, privacy_policy
    ]
    return deploy_args


def deploy(users, deploy_args):
    coupon_contract = users['issuer'].deploy(
        IbetCoupon,
        *deploy_args
    )
    return coupon_contract


# TEST_deploy
class TestDeploy:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, coupon_exchange,
                      coupon_exchange_storage, payment_gateway):
        # assertion
        owner = coupon_exchange.owner()
        payment_gateway_address = coupon_exchange.paymentGatewayAddress()
        storage_address = coupon_exchange.storageAddress()
        assert owner == users['admin']
        assert payment_gateway_address == to_checksum_address(payment_gateway.address)
        assert storage_address == to_checksum_address(coupon_exchange_storage.address)


# TEST_tokenFallback
class TestTokenFallback:

    #######################################
    # Normal
    #######################################
    # Normal_1
    def test_normal_1(self, users, coupon_exchange):
        _issuer = users['issuer']
        _value = 100

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # transfer to exchange contract
        coupon_token.transfer.transact(
            coupon_exchange.address,
            _value,
            {'from': _issuer}
        )

        # assertion
        balance_coupon = coupon_token.balanceOf(_issuer)
        balance_exchange = coupon_exchange.balanceOf(_issuer, coupon_token.address)
        assert balance_coupon == deploy_args[2] - _value
        assert balance_exchange == _value

    # Normal_2
    # Multiple deposit
    def test_normal_2(self, users, coupon_exchange):
        _issuer = users['issuer']
        _value = 100

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # transfer to exchange contract (1)
        coupon_token.transfer.transact(
            coupon_exchange.address,
            _value,
            {'from': _issuer}
        )

        # transfer to exchange contract (2)
        coupon_token.transfer.transact(
            coupon_exchange.address,
            _value,
            {'from': _issuer}
        )

        # assertion
        balance_coupon = coupon_token.balanceOf(_issuer)
        balance_exchange = coupon_exchange.balanceOf(_issuer, coupon_token.address)
        assert balance_coupon == deploy_args[2] - _value * 2
        assert balance_exchange == _value * 2


# TEST_withdrawAll
class TestWithdrawAll:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, coupon_exchange):
        _issuer = users['issuer']
        _value = 2 ** 256 - 1

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon = deploy(users, deploy_args)

        # transfer to exchange contract
        coupon.transfer.transact(coupon_exchange.address, _value, {'from': _issuer})

        # withdrawAll
        tx = coupon_exchange.withdrawAll.transact(coupon.address, {'from': _issuer})

        # assertion
        balance_coupon = coupon.balanceOf(_issuer)
        balance_exchange = coupon_exchange.balanceOf(_issuer, coupon.address)
        assert balance_coupon == deploy_args[2]
        assert balance_exchange == 0

        assert tx.events["Withdrawal"]["tokenAddress"] == coupon.address
        assert tx.events["Withdrawal"]["accountAddress"] == _issuer

    #######################################
    # Error
    #######################################

    # Error_1
    def test_error_1(self, users, coupon_exchange):
        _issuer = users['issuer']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon = deploy(users, deploy_args)

        # withdrawAll
        with brownie.reverts():
            coupon_exchange.withdrawAll.transact(
                coupon.address,
                {'from': _issuer}
            )

        # assertion
        balance_coupon = coupon.balanceOf(_issuer)
        balance_exchange = coupon_exchange.balanceOf(_issuer, coupon.address)
        assert balance_coupon == deploy_args[2]
        assert balance_exchange == 0


# TEST_createOrder
class TestCreateOrder:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Make order: BUY
    def test_normal_1(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make order: BUY
        _amount = 2 ** 256 - 1
        _price = 123
        _isBuy = True

        tx = coupon_exchange.createOrder.transact(
            coupon_token.address,
            _amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # assertion
        order_id = coupon_exchange.latestOrderId()
        assert coupon_exchange.getOrder(order_id) == [
            trader.address,
            coupon_token.address,
            _amount,
            _price,
            _isBuy,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_token.balanceOf(trader) == 0

        assert tx.events["NewOrder"]["tokenAddress"] == coupon_token.address
        assert tx.events["NewOrder"]["orderId"] == order_id
        assert tx.events["NewOrder"]["accountAddress"] == trader
        assert tx.events["NewOrder"]["isBuy"] is True
        assert tx.events["NewOrder"]["price"] == _price
        assert tx.events["NewOrder"]["amount"] == _amount
        assert tx.events["NewOrder"]["agentAddress"] == agent

    # Normal_2
    # Make order: SELL
    def test_normal_2(self, users, coupon_exchange):
        issuer = users['issuer']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 2 ** 256 - 1
        _price = 123
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _amount,
            {'from': issuer}
        )
        tx = coupon_exchange.createOrder.transact(
            coupon_token.address,
            _amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # assertion
        order_id = coupon_exchange.latestOrderId()
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _amount,
            _price,
            _isBuy,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _amount
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _amount

        assert tx.events["NewOrder"]["tokenAddress"] == coupon_token.address
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
    def test_error_1_1(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make order: BUY
        _amount = 0
        _price = 123
        _isBuy = True

        order_id_before = coupon_exchange.latestOrderId()
        with brownie.reverts():
            coupon_exchange.createOrder.transact(
                coupon_token.address,
                _amount,
                _price,
                _isBuy,
                agent,
                {'from': trader}
            )

        # assertion
        order_id_after = coupon_exchange.latestOrderId()
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_token.balanceOf(trader) == 0
        assert order_id_before == order_id_after

    # Error_1_2
    # Make order: BUY
    # Status must be True
    def test_error_1_2(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # change token status
        coupon_token.setStatus.transact(False, {'from': issuer})

        # make order: BUY
        _amount = 100
        _price = 123
        _isBuy = True

        order_id_before = coupon_exchange.latestOrderId()
        with brownie.reverts():
            coupon_exchange.createOrder.transact(
                coupon_token.address,
                _amount,
                _price,
                _isBuy,
                agent,
                {'from': trader}
            )

        # assertion
        order_id_after = coupon_exchange.latestOrderId()
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_token.balanceOf(trader) == 0
        assert order_id_before == order_id_after

    # Error_1_3
    # Make order: BUY
    # Agent must be valid
    def test_error_1_3(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make order: BUY
        _amount = 0
        _price = 123
        _isBuy = True

        order_id_before = coupon_exchange.latestOrderId()
        with brownie.reverts():
            coupon_exchange.createOrder.transact(
                coupon_token.address,
                _amount,
                _price,
                _isBuy,
                users['user1'],  # invalid
                {'from': trader}
            )

        # assertion
        order_id_after = coupon_exchange.latestOrderId()
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_token.balanceOf(trader) == 0
        assert order_id_before == order_id_after

    # Error_2_1
    # Make order: SELL
    # Amount must be greater than zero
    def test_error_2_1(self, users, coupon_exchange):
        issuer = users['issuer']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 2 ** 256 - 1
        _price = 123
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            0,  # zero
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # assertion
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == 0
        assert coupon_token.balanceOf(issuer) == deploy_args[2]

    # Error_2_2
    # Make order: SELL
    # Insufficient balance
    def test_error_2_2(self, users, coupon_exchange):
        issuer = users['issuer']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 100
        _price = 123
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            101,  # greater than deposit amount
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # assertion
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == 0
        assert coupon_token.balanceOf(issuer) == deploy_args[2]

    # Error_2_3
    # Make order: SELL
    # Status must be True
    def test_error_2_3(self, users, coupon_exchange):
        issuer = users['issuer']
        agent = users['agent']

        # issuer token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # change token status
        coupon_token.setStatus.transact(False, {'from': issuer})

        # transfer to contract -> make order: SELL
        _amount = 100
        _price = 123
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # assertion
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == 0
        assert coupon_token.balanceOf(issuer) == deploy_args[2]

    # Error_2_4
    # Make order: SELL
    # Agent must be valid
    def test_error_2_4(self, users, coupon_exchange):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 100
        _price = 123
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _amount,
            _price,
            _isBuy,
            users['user1'],  # invalid agent
            {'from': issuer}
        )

        # assertion
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == 0
        assert coupon_token.balanceOf(issuer) == deploy_args[2]


# TEST_cancelOrder
class TestCancelOrder:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Cancel order: BUY
    def test_normal_1(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make order: BUY
        _amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # cancel order
        order_id = coupon_exchange.latestOrderId()
        tx = coupon_exchange.cancelOrder.transact(
            order_id,
            {'from': trader}
        )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            trader.address,
            coupon_token.address,
            _amount,
            _price,
            _isBuy,
            agent.address,
            True
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_token.balanceOf(trader) == 0

        assert tx.events["CancelOrder"]["tokenAddress"] == coupon_token.address
        assert tx.events["CancelOrder"]["orderId"] == order_id
        assert tx.events["CancelOrder"]["accountAddress"] == trader
        assert tx.events["CancelOrder"]["isBuy"] is True
        assert tx.events["CancelOrder"]["price"] == _price
        assert tx.events["CancelOrder"]["amount"] == _amount
        assert tx.events["CancelOrder"]["agentAddress"] == agent

    # Normal_2
    # Cancel order: SELL
    def test_normal_2(self, users, coupon_exchange):
        issuer = users['issuer']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # cancel order
        order_id = coupon_exchange.latestOrderId()
        tx = coupon_exchange.cancelOrder.transact(
            order_id,
            {'from': issuer}
        )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _amount,
            _price,
            _isBuy,
            agent.address,
            True
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == 0

        assert tx.events["CancelOrder"]["tokenAddress"] == coupon_token.address
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
    def test_error_1(self, users, coupon_exchange):
        issuer = users['issuer']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # cancel order
        latest_order_id = coupon_exchange.latestOrderId()
        with brownie.reverts():
            coupon_exchange.cancelOrder.transact(
                latest_order_id + 1,
                {'from': issuer}
            )

        # assertion
        assert coupon_exchange.getOrder(latest_order_id) == [
            issuer.address,
            coupon_token.address,
            _amount,
            _price,
            _isBuy,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _amount
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _amount

    # Error_2
    # The remaining amount of the original order must be greater than zero
    def test_error_2(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make BUY order by trader
        _amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _amount,
            _price,
            True,
            agent,
            {'from': trader}
        )

        # take SELL order by issuer
        order_id = coupon_exchange.latestOrderId()
        coupon_token.transfer.transact(
            coupon_exchange.address,
            _amount,
            {'from': issuer}
        )
        coupon_exchange.executeOrder.transact(
            order_id,
            _amount,
            False,
            {'from': issuer}
        )

        # confirm agreement by agent
        agreement_id = coupon_exchange.latestAgreementId(order_id)
        coupon_exchange.confirmAgreement.transact(
            order_id,
            agreement_id,
            {'from': agent}
        )
        assert coupon_exchange.getOrder(order_id)[2] == 0

        # cancel order
        with brownie.reverts():
            coupon_exchange.cancelOrder.transact(
                order_id,
                {'from': issuer}
            )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            trader.address,
            coupon_token.address,
            0,
            _price,
            True,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _amount
        assert coupon_token.balanceOf(trader) == _amount

    # Error_3
    # Order must not have been cancelled
    def test_error_3(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make BUY order
        _amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _amount,
            _price,
            True,
            agent,
            {'from': trader}
        )

        # cancel order (1)
        order_id = coupon_exchange.latestOrderId()
        coupon_exchange.cancelOrder.transact(order_id, {'from': trader})

        # cancel order (2)
        with brownie.reverts():
            coupon_exchange.cancelOrder.transact(order_id, {'from': trader})

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            trader.address,
            coupon_token.address,
            _amount,
            _price,
            True,
            agent.address,
            True
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_token.balanceOf(trader) == 0

    # Error_4
    # The Orderer and the Order Cancellation Executor must be the same
    def test_error_4(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make BUY order by trader
        _amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _amount,
            _price,
            True,
            agent,
            {'from': trader}
        )

        # cancel order
        order_id = coupon_exchange.latestOrderId()
        with brownie.reverts():
            coupon_exchange.cancelOrder.transact(
                order_id,
                {'from': users['user1']}
            )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            trader.address,
            coupon_token.address,
            _amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_token.balanceOf(trader) == 0


# TEST_executeOrder
class TestExecuteOrder:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Take order: BUY
    def test_normal_1(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _take_amount
        agreement_id = coupon_exchange.latestAgreementId(order_id)
        assert coupon_exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader.address,
            _take_amount,
            _price,
            False,
            False
        ]
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Normal_2
    # Take order: SELL
    def test_normal_2(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # take SELL order by issuer
        _take_amount = 2 ** 256 - 1

        order_id = coupon_exchange.latestOrderId()
        coupon_token.transfer.transact(
            coupon_exchange.address,
            _take_amount,
            {'from': issuer}
        )
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            False,
            {'from': issuer}
        )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            trader.address,
            coupon_token.address,
            _make_amount - _take_amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _take_amount
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _take_amount
        agreement_id = coupon_exchange.latestAgreementId(order_id)
        assert coupon_exchange.getAgreement(order_id, agreement_id)[0:5] == [
            issuer,
            _take_amount,
            _price,
            False,
            False
        ]
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    #######################################
    # Error
    #######################################

    # Error_1
    # Order ID must be less than or equal to the latest order ID
    def test_error_1(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        with brownie.reverts():
            coupon_exchange.executeOrder.transact(
                order_id + 1,
                _take_amount,
                True,
                {'from': trader}
            )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _make_amount
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_2_1
    # Take order: BUY
    # Take amount must be greater than 0
    def test_error_2_1(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        order_id = coupon_exchange.latestOrderId()
        with brownie.reverts():
            coupon_exchange.executeOrder.transact(
                order_id,
                0,
                True,
                {'from': trader}
            )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _make_amount
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_2_2
    # Take order: BUY
    # The BUY/SELL type must be different from the original order
    def test_error_2_2(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        with brownie.reverts():
            coupon_exchange.executeOrder.transact(
                order_id,
                _take_amount,
                True,
                {'from': trader}
            )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == 0
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_2_3
    # Take order: BUY
    # The Maker and the taker must be the different
    def test_error_2_3(self, users, coupon_exchange):
        issuer = users['issuer']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        with brownie.reverts():
            coupon_exchange.executeOrder.transact(
                order_id,
                _take_amount,
                True,
                {'from': issuer}
            )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _make_amount
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_2_4
    # Take order: BUY
    # Orders that have already been canceled cannot be taken
    def test_error_2_4(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # cancel order
        order_id = coupon_exchange.latestOrderId()
        coupon_exchange.cancelOrder.transact(order_id, {'from': issuer})

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        with brownie.reverts():
            coupon_exchange.executeOrder.transact(
                order_id,
                _take_amount,
                True,
                {'from': trader}
            )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            True
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == 0
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_2_5
    # Take order: BUY
    # Status must be True
    def test_error_2_5(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # change token status
        coupon_token.setStatus.transact(False, {'from': issuer})

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        with brownie.reverts():
            coupon_exchange.executeOrder.transact(
                order_id,
                _take_amount,
                True,
                {'from': trader}
            )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _make_amount
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_2_6
    # Take order: BUY
    # The amount must be within the remaining amount of the make order
    def test_error_2_6(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 100
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 101
        order_id = coupon_exchange.latestOrderId()
        with brownie.reverts():
            coupon_exchange.executeOrder.transact(
                order_id,
                _take_amount,
                True,
                {'from': trader}
            )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _make_amount
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_3_1
    # Take order: SELL
    # Take amount must be greater than 0
    def test_error_3_1(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # take SELL order by issuer
        order_id = coupon_exchange.latestOrderId()
        coupon_token.transfer.transact(
            coupon_exchange.address,
            2 ** 256 - 1,
            {'from': issuer}
        )
        coupon_exchange.executeOrder.transact(
            order_id,
            0,
            False,
            {'from': issuer}
        )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            trader.address,
            coupon_token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == 0
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_3_2
    # Take order: SELL
    # The BUY/SELL type must be different from the original order
    def test_error_3_2(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # transfer to contract -> make order: SELL
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take order: SELL
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            False,
            {'from': trader}
        )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _make_amount
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_3_3
    # Take order: SELL
    # The Maker and the taker must be the different
    def test_error_3_3(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take SELL order by issuer
        _take_amount = 2 ** 256 - 1

        order_id = coupon_exchange.latestOrderId()
        coupon_token.transfer.transact(
            coupon_exchange.address,
            _take_amount,
            {'from': issuer}
        )
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            False,
            {'from': issuer}
        )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == 0
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_3_4
    # Take order: SELL
    # Orders that have already been canceled cannot be taken
    def test_error_3_4(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # cancel order
        order_id = coupon_exchange.latestOrderId()
        coupon_exchange.cancelOrder.transact(
            order_id,
            {'from': trader}
        )

        # take SELL order by issuer
        _take_amount = 2 ** 256 - 1

        order_id = coupon_exchange.latestOrderId()
        coupon_token.transfer.transact(
            coupon_exchange.address,
            _take_amount,
            {'from': issuer}
        )
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            False,
            {'from': issuer}
        )

        # Assert: orderbook
        assert coupon_exchange.getOrder(order_id) == [
            trader.address,
            coupon_token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            True
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == 0
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_3_5
    # Take order: SELL
    # Status must be True
    def test_error_3_5(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # change token status
        coupon_token.setStatus.transact(False, {'from': issuer})

        # take SELL order by issuer
        _take_amount = 2 ** 256 - 1

        order_id = coupon_exchange.latestOrderId()
        coupon_token.transfer.transact(
            coupon_exchange.address,
            _take_amount,
            {'from': issuer}
        )
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            False,
            {'from': issuer}
        )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            trader.address,
            coupon_token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == 0
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_3_6
    # Take order: SELL
    # The deposited balance must exceed the order amount
    def test_error_3_6(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # take SELL order by issuer
        _take_amount = 100

        order_id = coupon_exchange.latestOrderId()
        coupon_token.transfer.transact(
            coupon_exchange.address,
            _take_amount,
            {'from': issuer}
        )
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount + 1,
            False,
            {'from': issuer}
        )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            trader.address,
            coupon_token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == 0
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_3_7
    # Take order: SELL
    # The amount must be within the remaining amount of the make order
    def test_error_3_7(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 100
        _price = 2 ** 256 - 1
        _isBuy = True

        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # take SELL order by issuer
        _take_amount = 101

        order_id = coupon_exchange.latestOrderId()
        coupon_token.transfer.transact(
            coupon_exchange.address,
            _take_amount,
            {'from': issuer}
        )
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            False,
            {'from': issuer}
        )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            trader.address,
            coupon_token.address,
            _make_amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == 0
        assert coupon_exchange.lastPrice(coupon_token.address) == 0


# TEST_confirmAgreement
class TestConfirmAgreement:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Take order: BUY
    def test_normal_1(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # confirm agreement
        agreement_id = coupon_exchange.latestAgreementId(order_id)
        tx = coupon_exchange.confirmAgreement.transact(
            order_id,
            agreement_id,
            {'from': agent}
        )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert coupon_token.balanceOf(trader) == _take_amount
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == 0
        assert coupon_exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            False,
            True
        ]
        assert coupon_exchange.lastPrice(coupon_token.address) == _price

        assert tx.events["SettlementOK"]["tokenAddress"] == coupon_token.address
        assert tx.events["SettlementOK"]["orderId"] == order_id
        assert tx.events["SettlementOK"]["agreementId"] == agreement_id
        assert tx.events["SettlementOK"]["buyAddress"] == trader.address
        assert tx.events["SettlementOK"]["sellAddress"] == issuer.address
        assert tx.events["SettlementOK"]["price"] == _price
        assert tx.events["SettlementOK"]["amount"] == _take_amount
        assert tx.events["SettlementOK"]["agentAddress"] == agent.address

    # Normal_2
    # Take order: SELL
    def test_normal_2(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # take SELL order by issuer
        _take_amount = 2 ** 256 - 1

        order_id = coupon_exchange.latestOrderId()
        coupon_token.transfer.transact(
            coupon_exchange.address,
            _take_amount,
            {'from': issuer}
        )
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            False,
            {'from': issuer}
        )

        # confirm agreement
        agreement_id = coupon_exchange.latestAgreementId(order_id)
        tx = coupon_exchange.confirmAgreement.transact(
            order_id,
            agreement_id,
            {'from': agent}
        )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            trader.address,
            coupon_token.address,
            _make_amount - _take_amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _take_amount
        assert coupon_token.balanceOf(trader) == _make_amount
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == 0
        assert coupon_exchange.getAgreement(order_id, agreement_id)[0:5] == [
            issuer.address,
            _take_amount,
            _price,
            False,
            True
        ]
        assert coupon_exchange.lastPrice(coupon_token.address) == _price

        assert tx.events["SettlementOK"]["tokenAddress"] == coupon_token.address
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
    def test_error_1(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # confirm agreement
        agreement_id = coupon_exchange.latestAgreementId(order_id)
        with brownie.reverts():
            coupon_exchange.confirmAgreement.transact(
                order_id + 1,
                agreement_id,
                {'from': agent}
            )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _make_amount
        assert coupon_exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            False,
            False
        ]
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_2
    # Agreement ID must be less than or equal to the latest agreement ID
    def test_error_2(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # confirm agreement
        agreement_id = coupon_exchange.latestAgreementId(order_id)
        with brownie.reverts():
            coupon_exchange.confirmAgreement.transact(
                order_id,
                agreement_id + 1,
                {'from': agent}
            )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _make_amount
        assert coupon_exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            False,
            False
        ]
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_3
    # If it has already been confirmed, it cannot be confirmed
    def test_error_3(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # confirm agreement (1)
        agreement_id = coupon_exchange.latestAgreementId(order_id)
        coupon_exchange.confirmAgreement.transact(
            order_id,
            agreement_id,
            {'from': agent}
        )

        # confirm agreement (2)
        with brownie.reverts():
            coupon_exchange.confirmAgreement.transact(
                order_id,
                agreement_id,
                {'from': agent}
            )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert coupon_token.balanceOf(trader) == _take_amount
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == 0
        assert coupon_exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            False,
            True
        ]
        assert coupon_exchange.lastPrice(coupon_token.address) == _price

    # Error_4
    # If it has already been cancelled, it cannot be confirmed
    def test_error_4(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # cancel agreement
        agreement_id = coupon_exchange.latestAgreementId(order_id)
        coupon_exchange.cancelAgreement.transact(
            order_id,
            agreement_id,
            {'from': agent}
        )

        # confirm agreement
        with brownie.reverts():
            coupon_exchange.confirmAgreement.transact(
                order_id,
                agreement_id,
                {'from': agent}
            )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == 0
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _make_amount
        assert coupon_exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            True,
            False
        ]
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_5
    # The executor must be the agent specified in the make order
    def test_error_5(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # confirm agreement
        agreement_id = coupon_exchange.latestAgreementId(order_id)
        with brownie.reverts():
            coupon_exchange.confirmAgreement.transact(
                order_id,
                agreement_id + 1,
                {'from': users['user1']}
            )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _make_amount
        assert coupon_exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            False,
            False
        ]
        assert coupon_exchange.lastPrice(coupon_token.address) == 0


# TEST_cancelAgreement
class TestCancelAgreement:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Take order: BUY
    def test_normal_1(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # cancel agreement
        agreement_id = coupon_exchange.latestAgreementId(order_id)
        tx = coupon_exchange.cancelAgreement.transact(
            order_id,
            agreement_id,
            {'from': agent}
        )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == 0
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _make_amount
        assert coupon_exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            True,
            False
        ]
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

        assert tx.events["SettlementNG"]["tokenAddress"] == coupon_token.address
        assert tx.events["SettlementNG"]["orderId"] == order_id
        assert tx.events["SettlementNG"]["agreementId"] == agreement_id
        assert tx.events["SettlementNG"]["buyAddress"] == trader.address
        assert tx.events["SettlementNG"]["sellAddress"] == issuer.address
        assert tx.events["SettlementNG"]["price"] == _price
        assert tx.events["SettlementNG"]["amount"] == _take_amount
        assert tx.events["SettlementNG"]["agentAddress"] == agent.address

    # Normal_2
    # Take order: SELL
    def test_normal_2(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make BUY order by trader
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = True

        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': trader}
        )

        # take SELL order by issuer
        _take_amount = 2 ** 256 - 1

        order_id = coupon_exchange.latestOrderId()
        coupon_token.transfer.transact(
            coupon_exchange.address,
            _take_amount,
            {'from': issuer}
        )
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            False,
            {'from': issuer}
        )

        # cancel agreement
        agreement_id = coupon_exchange.latestAgreementId(order_id)
        tx = coupon_exchange.cancelAgreement.transact(
            order_id,
            agreement_id,
            {'from': agent}
        )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            trader.address,
            coupon_token.address,
            _make_amount - _take_amount,
            _price,
            True,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == 0
        assert coupon_exchange.getAgreement(order_id, agreement_id)[0:5] == [
            issuer.address,
            _take_amount,
            _price,
            True,
            False
        ]
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

        assert tx.events["SettlementNG"]["tokenAddress"] == coupon_token.address
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
    def test_error_1(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # cancel agreement
        agreement_id = coupon_exchange.latestAgreementId(order_id)
        with brownie.reverts():
            coupon_exchange.cancelAgreement.transact(
                order_id + 1,
                agreement_id,
                {'from': agent}
            )

        # assert
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _make_amount
        assert coupon_exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader.address,
            _take_amount,
            _price,
            False,
            False
        ]
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_2
    # Agreement ID must be less than or equal to the latest agreement ID
    def test_error_2(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # cancel agreement
        agreement_id = coupon_exchange.latestAgreementId(order_id)
        with brownie.reverts():
            coupon_exchange.cancelAgreement.transact(
                order_id,
                agreement_id + 1,
                {'from': agent}
            )

        # assert
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _make_amount
        assert coupon_exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader.address,
            _take_amount,
            _price,
            False,
            False
        ]
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_3
    # If it has already been confirmed, it cannot be confirmed
    def test_error_3(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # confirm agreement
        agreement_id = coupon_exchange.latestAgreementId(order_id)
        coupon_exchange.confirmAgreement.transact(
            order_id,
            agreement_id,
            {'from': agent}
        )

        # cancel agreement
        with brownie.reverts():
            coupon_exchange.confirmAgreement.transact(
                order_id,
                agreement_id,
                {'from': agent}
            )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert coupon_token.balanceOf(trader) == _take_amount
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == 0
        assert coupon_exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            False,
            True
        ]
        assert coupon_exchange.lastPrice(coupon_token.address) == _price

    # Error_4
    # If it has already been cancelled, it cannot be confirmed
    def test_error_4(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # cancel agreement (1)
        agreement_id = coupon_exchange.latestAgreementId(order_id)
        coupon_exchange.cancelAgreement.transact(
            order_id,
            agreement_id,
            {'from': agent}
        )

        # cancel agreement (2)
        with brownie.reverts():
            coupon_exchange.cancelAgreement.transact(
                order_id,
                agreement_id,
                {'from': agent}
            )

        # assertion
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == 0
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _make_amount
        assert coupon_exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader,
            _take_amount,
            _price,
            True,
            False
        ]
        assert coupon_exchange.lastPrice(coupon_token.address) == 0

    # Error_5
    # The executor must be the agent specified in the make order
    def test_error_5(self, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # make SELL order by issuer
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # take BUY order by trader
        _take_amount = 2 ** 256 - 1
        order_id = coupon_exchange.latestOrderId()
        coupon_exchange.executeOrder.transact(
            order_id,
            _take_amount,
            True,
            {'from': trader}
        )

        # cancel agreement
        agreement_id = coupon_exchange.latestAgreementId(order_id)
        with brownie.reverts():
            coupon_exchange.cancelAgreement.transact(
                order_id,
                agreement_id,
                {'from': users['user1']}
            )

        # assert
        assert coupon_exchange.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount - _take_amount,
            _price,
            False,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert coupon_token.balanceOf(trader) == 0
        assert coupon_exchange.commitmentOf(issuer, coupon_token.address) == _make_amount
        assert coupon_exchange.getAgreement(order_id, agreement_id)[0:5] == [
            trader.address,
            _take_amount,
            _price,
            False,
            False
        ]
        assert coupon_exchange.lastPrice(coupon_token.address) == 0


# update exchange
class TestUpdateExchange:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users,
                      coupon_exchange, coupon_exchange_storage, payment_gateway,
                      IbetCouponExchange):
        issuer = users['issuer']
        agent = users['agent']
        admin = users['admin']

        # issue token
        deploy_args = init_args(coupon_exchange.address)
        coupon_token = deploy(users, deploy_args)

        # transfer to contract -> make SELL order
        _make_amount = 2 ** 256 - 1
        _price = 2 ** 256 - 1
        _isBuy = False

        coupon_token.transfer.transact(
            coupon_exchange.address,
            _make_amount,
            {'from': issuer}
        )
        coupon_exchange.createOrder.transact(
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent,
            {'from': issuer}
        )

        # deploy new exchange contract
        coupon_exchange_new = admin.deploy(
            IbetCouponExchange,
            payment_gateway.address,
            coupon_exchange_storage.address
        )
        coupon_exchange_storage.upgradeVersion.transact(
            coupon_exchange_new.address,
            {'from': admin}
        )

        # assertion
        order_id = coupon_exchange_new.latestOrderId()
        assert coupon_exchange_new.getOrder(order_id) == [
            issuer.address,
            coupon_token.address,
            _make_amount,
            _price,
            _isBuy,
            agent.address,
            False
        ]
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - _make_amount
        assert coupon_exchange_new.balanceOf(issuer, coupon_token.address) == 0
        assert coupon_exchange_new.commitmentOf(issuer, coupon_token.address) == _make_amount
