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
from ape.exceptions import VirtualMachineError
from ape_utils import ZERO_ADDRESS, event_args, reverts
from eth_abi.exceptions import ValueOutOfBounds


def init_args(exchange_address):
    name = "test_coupon"
    symbol = "CPN"
    total_supply = 1000000
    tradable_exchange = exchange_address
    details = "some_details"
    return_details = "some_return_details"
    memo = "some_memo"
    expiration_date = "20201231"
    transferable = True
    contact_information = "some_contact_information"
    privacy_policy = "some_privacy_policy"

    deploy_args = [
        name,
        symbol,
        total_supply,
        tradable_exchange,
        details,
        return_details,
        memo,
        expiration_date,
        transferable,
        contact_information,
        privacy_policy,
    ]
    return deploy_args


# TEST_deploy
class TestDeploy:
    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]

        # deploy
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # assertion
        owner_address = coupon.owner()
        name = coupon.name()
        symbol = coupon.symbol()
        total_supply = coupon.totalSupply()
        tradable_exchange = coupon.tradableExchange()
        details = coupon.details()
        return_details = coupon.returnDetails()
        memo = coupon.memo()
        expiration_date = coupon.expirationDate()
        is_valid = coupon.status()
        transferable = coupon.transferable()
        contact_information = coupon.contactInformation()
        privacy_policy = coupon.privacyPolicy()
        assert owner_address == issuer
        assert name == deploy_args[0]
        assert symbol == deploy_args[1]
        assert total_supply == deploy_args[2]
        assert tradable_exchange == deploy_args[3]
        assert details == deploy_args[4]
        assert return_details == deploy_args[5]
        assert memo == deploy_args[6]
        assert expiration_date == deploy_args[7]
        assert is_valid is True
        assert transferable == deploy_args[8]
        assert contact_information == deploy_args[9]
        assert privacy_policy == deploy_args[10]


# TEST_transfer
class TestTransfer:
    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    # Transfer to account address
    def test_normal_1(self, IbetCoupon, users, exchange):
        _from = users["issuer"]
        _to = users["trader"]
        _value = 100

        # deploy
        deploy_args = init_args(exchange.address)
        coupon = _from.deploy(IbetCoupon, *deploy_args)

        # transfer
        tx = coupon.transfer(_to, _value, sender=_from)

        # assertion
        from_balance = coupon.balanceOf(_from)
        to_balance = coupon.balanceOf(_to)
        assert from_balance == deploy_args[2] - _value
        assert to_balance == _value

        event = event_args(tx, coupon.Transfer)
        assert event["from"] == _from
        assert event["to"] == _to
        assert event["value"] == _value

    # Normal_2
    # Transfer to contract address
    def test_normal_2(self, IbetCoupon, users, exchange):
        _from = users["issuer"]
        _to = exchange.address
        _value = 100

        # deploy
        deploy_args = init_args(exchange.address)
        coupon = _from.deploy(IbetCoupon, *deploy_args)

        # transfer
        tx = coupon.transfer(_to, _value, sender=_from)

        # assertion
        from_balance = coupon.balanceOf(_from)
        to_balance = coupon.balanceOf(_to)
        assert from_balance == deploy_args[2] - _value
        assert to_balance == _value

        event = event_args(tx, coupon.Transfer)
        assert event["from"] == _from
        assert event["to"] == _to
        assert event["value"] == _value

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    # Insufficient balance
    def test_error_1(self, IbetCoupon, users, exchange):
        _from = users["issuer"]
        _to = users["trader"]

        # deploy
        deploy_args = init_args(exchange.address)
        coupon = _from.deploy(IbetCoupon, *deploy_args)

        # transfer
        _value = deploy_args[2] + 1
        with reverts("130101"):
            coupon.transfer(_to, _value, sender=_from)

        # assertion
        assert coupon.balanceOf(_from) == deploy_args[2]
        assert coupon.balanceOf(_to) == 0

    # Error_2
    # Cannot access private functions
    def test_error_2(self, IbetCoupon, users, exchange):
        _from = users["issuer"]
        _to = users["trader"]

        # deploy
        deploy_args = init_args(exchange.address)
        coupon = _from.deploy(IbetCoupon, *deploy_args)

        with pytest.raises(AttributeError):
            coupon.isContract(_to, sender=_from)

        with pytest.raises(AttributeError):
            coupon.transferToAddress(_to, 10, "test_data", sender=_from)

        with pytest.raises(AttributeError):
            coupon.transferToContract(_to, 10, "test_data", sender=_from)

    # Error_3
    # Not transferable token
    def test_error_3(self, IbetCoupon, users, exchange):
        _from = users["issuer"]
        _to = users["trader"]

        # deploy
        deploy_args = init_args(exchange.address)
        deploy_args[8] = False  # not transferable
        coupon = _from.deploy(IbetCoupon, *deploy_args)

        # transfer
        _value = 1
        with reverts("130102"):
            coupon.transfer(_to, _value, sender=_from)

        # assertion
        assert coupon.balanceOf(_from) == deploy_args[2]
        assert coupon.balanceOf(_to) == 0

    # Error_4
    # Transfer to contract address
    # Not tradable exchange
    def test_error_4(
        self,
        IbetCoupon,
        IbetExchange,
        users,
        exchange,
        exchange_storage,
        payment_gateway,
    ):
        _issuer = users["issuer"]

        # deploy
        deploy_args = init_args(exchange.address)
        coupon = _issuer.deploy(IbetCoupon, *deploy_args)

        # deploy (not tradable exchange)
        not_tradable_exchange = users["admin"].deploy(
            IbetExchange, payment_gateway.address, exchange_storage.address
        )

        # transfer
        _value = deploy_args[2]
        with reverts("130001"):
            coupon.transfer(not_tradable_exchange.address, _value, sender=_issuer)

        # assertion
        assert coupon.balanceOf(_issuer) == deploy_args[2]
        assert coupon.balanceOf(not_tradable_exchange.address) == 0


# TEST_bulkTransfer
class TestBulkTransfer:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Bulk transfer to account address (1 data)
    def test_normal_1(self, IbetCoupon, users, exchange):
        from_address = users["issuer"]
        to_address = users["trader"]

        # issue coupon token
        deploy_args = init_args(exchange.address)
        coupon_contract = from_address.deploy(IbetCoupon, *deploy_args)

        # bulk transfer
        to_address_list = [to_address]
        amount_list = [1]
        tx = coupon_contract.bulkTransfer(
            to_address_list, amount_list, sender=from_address
        )

        # assertion
        from_balance = coupon_contract.balanceOf(from_address)
        to_balance = coupon_contract.balanceOf(to_address)
        assert from_balance == deploy_args[2] - 1
        assert to_balance == 1

        event = event_args(tx, coupon_contract.Transfer)
        assert event["from"] == from_address
        assert event["to"] == to_address
        assert event["value"] == 1

    # Normal_2
    # Bulk transfer to account address (multiple data)
    def test_normal_2(self, IbetCoupon, users, exchange):
        from_address = users["issuer"]
        to_address = users["trader"]

        # issue coupon token
        deploy_args = init_args(exchange.address)
        coupon_contract = from_address.deploy(IbetCoupon, *deploy_args)

        # bulk transfer
        to_address_list = []
        amount_list = []
        for i in range(100):
            to_address_list.append(to_address)
            amount_list.append(1)
        coupon_contract.bulkTransfer(to_address_list, amount_list, sender=from_address)

        # assertion
        from_balance = coupon_contract.balanceOf(from_address)
        to_balance = coupon_contract.balanceOf(to_address)
        assert from_balance == deploy_args[2] - 100
        assert to_balance == 100

    # Normal_3
    # Bulk transfer to contract address
    def test_normal_3(self, IbetCoupon, users, exchange):
        from_address = users["issuer"]

        # issue coupon token
        deploy_args = init_args(exchange.address)
        coupon_contract = from_address.deploy(IbetCoupon, *deploy_args)

        # bulk transfer
        to_address_list = [exchange.address]
        amount_list = [1]
        tx = coupon_contract.bulkTransfer(
            to_address_list, amount_list, sender=from_address
        )

        # assertion
        from_balance = coupon_contract.balanceOf(from_address)
        to_balance = coupon_contract.balanceOf(exchange.address)
        assert from_balance == deploy_args[2] - 1
        assert to_balance == 1

        event = event_args(tx, coupon_contract.Transfer)
        assert event["from"] == from_address
        assert event["to"] == exchange.address
        assert event["value"] == 1

    #######################################
    # Error
    #######################################

    # Error_1
    # Over/Under the limit
    def test_error_1(self, IbetCoupon, users, exchange):
        from_address = users["issuer"]
        to_address = users["trader"]

        # issue coupon token
        deploy_args = init_args(exchange.address)
        deploy_args[2] = 2**256 - 1
        coupon_contract = from_address.deploy(IbetCoupon, *deploy_args)

        # over the upper limit
        with pytest.raises(VirtualMachineError):
            coupon_contract.bulkTransfer(
                [to_address, to_address], [2**256 - 1, 1], sender=from_address
            )

        # under the lower limit
        with pytest.raises((OverflowError, ValueOutOfBounds)):
            coupon_contract.bulkTransfer([to_address], [-1], sender=from_address)

        # assertion
        from_balance = coupon_contract.balanceOf(from_address)
        to_balance = coupon_contract.balanceOf(to_address)
        assert from_balance == deploy_args[2]
        assert to_balance == 0

    # Error_2
    # Insufficient balance
    def test_error_2(self, IbetCoupon, users, exchange):
        from_address = users["issuer"]
        to_address = users["trader"]

        # issue coupon token
        deploy_args = init_args(exchange.address)
        coupon_contract = from_address.deploy(IbetCoupon, *deploy_args)

        # bulk transfer
        with reverts("130202"):
            coupon_contract.bulkTransfer(
                [to_address, to_address], [deploy_args[2], 1], sender=from_address
            )

        # assertion
        assert coupon_contract.balanceOf(from_address) == deploy_args[2]
        assert coupon_contract.balanceOf(to_address) == 0

    # Error_3
    # Not transferable token
    def test_error_3(self, IbetCoupon, users, exchange):
        from_address = users["issuer"]
        to_address = users["trader"]

        # issue coupon token
        deploy_args = init_args(exchange.address)
        coupon_contract = from_address.deploy(IbetCoupon, *deploy_args)

        # change to not-transferable
        coupon_contract.setTransferable(False, sender=from_address)

        # bulk transfer
        with reverts("130203"):
            coupon_contract.bulkTransfer([to_address], [1], sender=from_address)

        # assertion
        from_balance = coupon_contract.balanceOf(from_address)
        to_balance = coupon_contract.balanceOf(to_address)
        assert from_balance == deploy_args[2]
        assert to_balance == 0


# TEST_transferFrom
class TestTransferFrom:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Transfer to account address
    def test_normal_1(self, users, IbetCoupon, exchange):
        issuer = users["issuer"]
        from_address = users["admin"]
        to_address = users["trader"]
        value = 100

        # issue coupon token
        deploy_args = init_args(exchange.address)
        coupon_contract = issuer.deploy(IbetCoupon, *deploy_args)

        # transfer to account address
        coupon_contract.transfer(from_address, value, sender=issuer)
        tx = coupon_contract.transferFrom(
            from_address, to_address, value, sender=issuer
        )

        # assertion
        issuer_balance = coupon_contract.balanceOf(issuer)
        from_balance = coupon_contract.balanceOf(from_address)
        to_balance = coupon_contract.balanceOf(to_address)
        assert issuer_balance == deploy_args[2] - value
        assert from_balance == 0
        assert to_balance == value

        event = event_args(tx, coupon_contract.Transfer)
        assert event["from"] == from_address
        assert event["to"] == to_address
        assert event["value"] == value

    # Normal_2
    # Transfer to contract address
    def test_normal_2(self, users, IbetCoupon, exchange):
        issuer = users["issuer"]
        from_address = users["trader"]
        value = 100

        # issue coupon token
        deploy_args = init_args(exchange.address)
        coupon_contract = issuer.deploy(IbetCoupon, *deploy_args)

        # transfer to contract address
        coupon_contract.transfer(from_address, value, sender=issuer)
        to_address = exchange.address
        tx = coupon_contract.transferFrom(
            from_address, to_address, value, sender=issuer
        )

        # assertion
        issuer_balance = coupon_contract.balanceOf(issuer)
        from_balance = coupon_contract.balanceOf(from_address)
        to_balance = coupon_contract.balanceOf(to_address)
        assert issuer_balance == deploy_args[2] - value
        assert from_balance == 0
        assert to_balance == value

        event = event_args(tx, coupon_contract.Transfer)
        assert event["from"] == from_address
        assert event["to"] == to_address
        assert event["value"] == value

    # Normal_3_1
    # Upper limit
    def test_normal_3_1(self, users, IbetCoupon, exchange):
        issuer = users["issuer"]
        from_address = users["admin"]
        to_address = users["trader"]
        max_value = 2**256 - 1

        # issuer coupon token
        deploy_args = init_args(exchange.address)
        deploy_args[2] = max_value
        coupon_contract = issuer.deploy(IbetCoupon, *deploy_args)

        # transfer
        coupon_contract.transfer(from_address, max_value, sender=issuer)
        tx = coupon_contract.transferFrom(
            from_address, to_address, max_value, sender=issuer
        )

        # assertion
        issuer_balance = coupon_contract.balanceOf(issuer)
        from_balance = coupon_contract.balanceOf(from_address)
        to_balance = coupon_contract.balanceOf(to_address)
        assert issuer_balance == 0
        assert from_balance == 0
        assert to_balance == max_value

        event = event_args(tx, coupon_contract.Transfer)
        assert event["from"] == from_address
        assert event["to"] == to_address
        assert event["value"] == max_value

    # Normal_3_2
    # Lower limit
    def test_normal_3_2(self, users, IbetCoupon, exchange):
        issuer = users["issuer"]
        from_address = users["admin"]
        to_address = users["trader"]
        min_value = 0

        # issue coupon token
        deploy_args = init_args(exchange.address)
        deploy_args[2] = min_value
        coupon_contract = issuer.deploy(IbetCoupon, *deploy_args)

        # transfer
        coupon_contract.transfer(from_address, min_value, sender=issuer)
        tx = coupon_contract.transferFrom(
            from_address, to_address, min_value, sender=issuer
        )

        # assertion
        issuer_balance = coupon_contract.balanceOf(issuer)
        from_balance = coupon_contract.balanceOf(from_address)
        to_balance = coupon_contract.balanceOf(to_address)
        assert issuer_balance == 0
        assert from_balance == 0
        assert to_balance == 0

        event = event_args(tx, coupon_contract.Transfer)
        assert event["from"] == from_address
        assert event["to"] == to_address
        assert event["value"] == min_value

    #######################################
    # Error
    #######################################

    # Error_1
    # Insufficient balance
    def test_error_1(self, users, IbetCoupon, exchange):
        issuer = users["issuer"]
        to_address = users["trader"]

        # issue coupon token
        deploy_args = init_args(exchange.address)
        coupon_contract = issuer.deploy(IbetCoupon, *deploy_args)

        # transfer
        transfer_amount = 10000000000
        with reverts("130301"):
            coupon_contract.transferFrom(
                issuer, to_address, transfer_amount, sender=issuer
            )

        # assertion
        assert coupon_contract.balanceOf(issuer) == deploy_args[2]
        assert coupon_contract.balanceOf(to_address) == 0

    # Error_2
    # Unauthorized
    def test_error_2(self, users, IbetCoupon, exchange):
        issuer = users["issuer"]
        admin = users["admin"]
        to_address = users["trader"]
        transfer_amount = 100

        # issue coupon token
        deploy_args = init_args(exchange.address)
        coupon_contract = issuer.deploy(IbetCoupon, *deploy_args)

        # transfer
        with reverts("500001"):
            coupon_contract.transferFrom(
                issuer,
                to_address,
                transfer_amount,
                sender=admin,  # unauthorized account
            )

        # assertion
        assert coupon_contract.balanceOf(issuer) == deploy_args[2]
        assert coupon_contract.balanceOf(to_address) == 0


# TEST_bulkTransferFrom
class TestBulkTransferFrom:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetCoupon, exchange):
        issuer = users["issuer"]
        to_address_1 = users["user1"]
        to_address_2 = users["user2"]
        value = 100

        # issue token
        deploy_args = init_args(exchange.address)
        coupon_token = issuer.deploy(IbetCoupon, *deploy_args)

        # bulk forced transfer
        #   issuer -> to_address_1 -> to_address_2
        coupon_token.bulkTransferFrom(
            [issuer, to_address_1],
            [to_address_1, to_address_2],
            [value, value],
            sender=issuer,
        )

        # assertion
        assert coupon_token.balanceOf(issuer) == deploy_args[2] - value
        assert coupon_token.balanceOf(to_address_1) == 0
        assert coupon_token.balanceOf(to_address_2) == value

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    # -> revert: 500001
    def test_error_1(self, users, IbetCoupon, exchange):
        issuer = users["issuer"]
        to_address = users["user1"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon_token = issuer.deploy(IbetCoupon, *deploy_args)

        # bulk forced transfer
        with reverts("500001"):
            coupon_token.bulkTransferFrom(
                [issuer], [to_address], [10, 10], sender=to_address
            )

        # assertion
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_token.balanceOf(to_address) == 0

    # Error_2
    # Some list lengths are unequal.
    # -> revert: 130601
    def test_error_2(self, users, IbetCoupon, exchange):
        issuer = users["issuer"]
        to_address_1 = users["user1"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon_token = issuer.deploy(IbetCoupon, *deploy_args)

        # bulk forced transfer
        with reverts("130601"):
            coupon_token.bulkTransferFrom(
                [issuer, issuer], [to_address_1], [10, 10], sender=issuer
            )

        # assertion
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_token.balanceOf(to_address_1) == 0

    # Error_3
    # Insufficient balance
    # -> revert: 130301
    def test_error_3(self, users, IbetCoupon, exchange):
        issuer = users["issuer"]
        to_address_1 = users["user1"]
        to_address_2 = users["user2"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon_token = issuer.deploy(IbetCoupon, *deploy_args)

        # bulk forced transfer
        #   issuer -> to_address_1
        #   to_address_2 -> to_address_1
        with reverts("130301"):
            coupon_token.bulkTransferFrom(
                [issuer, to_address_2],
                [to_address_1, to_address_1],
                [10, 10],
                sender=issuer,
            )

        # assertion
        assert coupon_token.balanceOf(issuer) == deploy_args[2]
        assert coupon_token.balanceOf(to_address_1) == 0
        assert coupon_token.balanceOf(to_address_2) == 0


# TEST_consume
class TestConsume:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, IbetCoupon, users, exchange):
        _user = users["issuer"]
        _value = 1

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = _user.deploy(IbetCoupon, *deploy_args)

        # consume
        tx = coupon.consume(_value, sender=_user)

        # assertion
        balance = coupon.balanceOf(_user)
        used = coupon.usedOf(_user)
        assert balance == deploy_args[2] - _value
        assert used == _value

        event = event_args(tx, coupon.Consume)
        assert event["consumer"] == _user
        assert event["balance"] == balance
        assert event["used"] == used
        assert event["value"] == _value

    #######################################
    # Error
    #######################################

    # Error_1
    # Insufficient balance
    def test_error_1(self, IbetCoupon, users, exchange):
        _issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = _issuer.deploy(IbetCoupon, *deploy_args)

        # consume
        with reverts("130401"):
            _value = deploy_args[2] + 1
            coupon.consume(_value, sender=_issuer)

        # assertion
        assert coupon.balanceOf(_issuer) == deploy_args[2]
        assert coupon.usedOf(_issuer) == 0


# TEST_issue
class TestIssue:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, IbetCoupon, users, exchange):
        _issuer = users["issuer"]
        _value = 1

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = _issuer.deploy(IbetCoupon, *deploy_args)

        # additional issue
        coupon.issue(_value, sender=_issuer)

        # assertion
        balance = coupon.balanceOf(_issuer)
        total_supply = coupon.totalSupply()
        assert balance == deploy_args[2] + _value
        assert total_supply == deploy_args[2] + _value

    #######################################
    # Error
    #######################################

    # Error_1
    # Over maximum value
    def test_error_1(self, IbetCoupon, users, exchange):
        _issuer = users["issuer"]
        _consumer = users["trader"]
        _transfer_quantity = 999999
        _value = 2**256 - 1

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = _issuer.deploy(IbetCoupon, *deploy_args)

        # transfer
        coupon.transferFrom(_issuer, _consumer, _transfer_quantity, sender=_issuer)

        # additional issue
        with pytest.raises(VirtualMachineError):
            coupon.issue(_value, sender=_issuer)  # 2**256 - 1 + 1

        # assertion
        balance = coupon.balanceOf(_issuer)
        total_supply = coupon.totalSupply()
        assert balance == deploy_args[2] - _transfer_quantity
        assert total_supply == deploy_args[2]

    # Error_2
    # Unauthorized
    def test_error_2(self, IbetCoupon, users, exchange):
        _issuer = users["issuer"]
        _other = users["trader"]
        _value = 1000

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = _issuer.deploy(IbetCoupon, *deploy_args)

        # additional issue
        with reverts("500001"):
            coupon.issue(_value, sender=_other)

        # assertion
        balance = coupon.balanceOf(_issuer)
        total_supply = coupon.totalSupply()
        assert balance == deploy_args[2]
        assert total_supply == deploy_args[2]


# TEST_setDetails
class TestSetDetails:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # set details
        coupon.setDetails("updated details", sender=issuer)

        # assertion
        details = coupon.details()
        assert details == "updated details"

    #######################################
    # Error
    #######################################

    # Error_1
    # Unauthorized
    def test_error_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]
        other = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # set details
        with reverts("500001"):
            coupon.setDetails("updated details", sender=other)

        details = coupon.details()
        assert details == "some_details"


# TEST_setMemo
class TestSetMemo:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # set memo
        coupon.setMemo("updated memo", sender=issuer)

        # assertion
        details = coupon.memo()
        assert details == "updated memo"

    #######################################
    # Error
    #######################################

    # Error_1
    # Unauthorized
    def test_error_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]
        other = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # set memo
        with reverts("500001"):
            coupon.setMemo("updated memo", sender=other)

        # assertion
        details = coupon.memo()
        assert details == "some_memo"


# TEST_balanceOf
class TestBalanceOf:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # get balance
        balance = coupon.balanceOf(issuer)

        # assertion
        assert balance == deploy_args[2]


# TEST_usedOf
class TestUsedOf:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, IbetCoupon, users, exchange):
        _issuer = users["issuer"]
        _value = 1

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = _issuer.deploy(IbetCoupon, *deploy_args)

        # consume
        coupon.consume(_value, sender=_issuer)

        # get used quantity
        used = coupon.usedOf(_issuer)

        # assertion
        assert used == _value


# TEST_setImageURL, getImageURL
class TestSetImageUrl:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Set one url
    def test_normal_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # set image url
        image_url = "https://some_image_url.com/image.png"
        coupon.setImageURL(0, image_url, sender=issuer)

        # assertion
        image_url_0 = coupon.getImageURL(0)
        assert image_url_0 == image_url

    # Normal_2
    # Set multiple urls
    def test_normal_2(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        image_url = "https://some_image_url.com/image1.png"

        # set image url (1)
        coupon.setImageURL(0, image_url, sender=issuer)

        # set image url (2)
        coupon.setImageURL(1, image_url, sender=issuer)

        # assertion
        image_url_0 = coupon.getImageURL(0)
        image_url_1 = coupon.getImageURL(1)
        assert image_url_0 == image_url
        assert image_url_1 == image_url

    # Normal_3
    # Overwriting
    def test_normal_3(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        image_url = "https://some_image_url.com/image.png"
        image_url_after = "https://some_image_url.com/image_after.png"

        # set image url
        coupon.setImageURL(0, image_url, sender=issuer)

        # overwrite image url
        coupon.setImageURL(0, image_url_after, sender=issuer)

        # assertion
        image_url_0 = coupon.getImageURL(0)
        assert image_url_0 == image_url_after

    #######################################
    # Error
    #######################################

    # Error_1
    # Unauthorized
    def test_error_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]
        other = users["admin"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # set image url
        image_url = "https://some_image_url.com/image.png"
        with reverts("500001"):
            coupon.setImageURL(0, image_url, sender=other)  # エラーになる

        # assertion
        image_url_0 = coupon.getImageURL(0)
        assert image_url_0 == ""


# TEST_setStatus
class TestSetStatus:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # change status
        coupon.setStatus(False, sender=issuer)

        # assertion
        assert coupon.status() is False

    #######################################
    # Error
    #######################################

    # Error_1
    # Unauthorized
    def test_error_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]
        other = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # change status
        with reverts("500001"):
            coupon.setStatus(False, sender=other)

        # assertion
        assert coupon.status() is True


# TEST_setTradableExchange
class TestSetTradableExchange:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # change exchange contract
        coupon.setTradableExchange(ZERO_ADDRESS, sender=issuer)

        # assertion
        assert coupon.tradableExchange() == ZERO_ADDRESS

    #######################################
    # Error
    #######################################

    # Error_1
    # Unauthorized
    def test_error_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # change exchange contract
        with reverts("500001"):
            coupon.setTradableExchange(ZERO_ADDRESS, sender=trader)

        # assertion
        assert coupon.tradableExchange() == exchange.address


# TEST_setExpirationDate
class TestSetExpirationDate:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]
        after_expiration_date = "after_expiration_date"

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # set expiration date
        coupon.setExpirationDate(after_expiration_date, sender=issuer)

        # assertion
        expiration_date = coupon.expirationDate()
        assert after_expiration_date == expiration_date

    #######################################
    # Error
    #######################################

    # Error_1
    # Unauthorized
    def test_error_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]
        attacker = users["trader"]
        after_expiration_date = "after_expiration_date"

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # set expiration date
        with reverts("500001"):
            coupon.setExpirationDate(after_expiration_date, sender=attacker)

        # assertion
        expiration_date = coupon.expirationDate()
        assert expiration_date == deploy_args[7]


# TEST_setTransferable
class TestSetTransferable:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # set transferable
        coupon.setTransferable(False, sender=issuer)

        # assertion
        transferable = coupon.transferable()
        assert transferable == False

    #######################################
    # Error
    #######################################

    # Error_1
    # Unauthorized
    def test_error_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]
        attacker = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # set transferable
        with reverts("500001"):
            coupon.setTransferable(False, sender=attacker)

        # assertion
        transferable = coupon.transferable()
        assert transferable == deploy_args[8]


# TEST_setInitialOfferingStatus
class TestSetInitialOfferingStatus:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)
        assert coupon.initialOfferingStatus() is False

        # change initial offering status
        coupon.setInitialOfferingStatus(True, sender=issuer)
        assert coupon.initialOfferingStatus() is True

    #######################################
    # Error
    #######################################

    # Error_1
    # Unauthorized
    def test_error_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]
        unauthorized_user = users["user1"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)
        assert coupon.initialOfferingStatus() is False

        # change initial offering status
        with reverts("500001"):
            coupon.setInitialOfferingStatus(True, sender=unauthorized_user)
        assert coupon.initialOfferingStatus() is False


# TEST_applyForOffering
class TestApplyForOffering:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Default value
    def test_normal_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)
        coupon.setInitialOfferingStatus(True, sender=issuer)

        # assertion
        assert coupon.applications(trader) == ""

    # Normal_2
    def test_normal_2(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)
        coupon.setInitialOfferingStatus(True, sender=issuer)

        # apply for
        tx = coupon.applyForOffering("abcdefgh", sender=trader)

        # assertion
        assert coupon.applications(trader) == "abcdefgh"

        event = event_args(tx, coupon.ApplyFor)
        assert event["accountAddress"] == trader

    #######################################
    # Error
    #######################################

    # Error_1
    # Offering status is False
    def test_error_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]
        trader = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # apply for
        with reverts("130501"):
            coupon.applyForOffering("abcdefgh", sender=trader)

        # assertion
        assert coupon.applications(trader) == ""


# TEST_setReturnDetails
class TestSetReturnDetails:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]
        after_return_details = "after_return_details"

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # set return details
        coupon.setReturnDetails(after_return_details, sender=issuer)

        # assertion
        return_details = coupon.returnDetails()
        assert after_return_details == return_details

    #######################################
    # Error
    #######################################

    # Error_1
    # Unauthorized
    def test_error_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]
        attacker = users["trader"]
        after_return_details = "after_return_details"

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # set return details
        with reverts("500001"):
            coupon.setReturnDetails(after_return_details, sender=attacker)

        # assertion
        return_details = coupon.returnDetails()
        assert return_details == deploy_args[5]


# TEST_setContactInformation
class TestSetContactInformation:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # set contact information
        coupon.setContactInformation("updated contact information", sender=issuer)

        # assertion
        contact_information = coupon.contactInformation()
        assert contact_information == "updated contact information"

    #######################################
    # Error
    #######################################

    # Error_1
    # Unauthorized
    def test_error_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]
        other = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # set contact information
        with reverts("500001"):
            coupon.setContactInformation("updated contact information", sender=other)

        # assertion
        contact_information = coupon.contactInformation()
        assert contact_information == "some_contact_information"


# TEST_setPrivacyPolicy
class TestSetPrivacyPolicy:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # set privacy policy
        coupon.setPrivacyPolicy("updated privacy policy", sender=issuer)

        # assertion
        privacy_policy = coupon.privacyPolicy()
        assert privacy_policy == "updated privacy policy"

    #######################################
    # Error
    #######################################

    # Error_1
    # Unauthorized
    def test_error_1(self, IbetCoupon, users, exchange):
        issuer = users["issuer"]
        other = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # set privacy policy
        with reverts("500001"):
            coupon.setPrivacyPolicy("updated privacy policy", sender=other)

        # assertion
        privacy_policy = coupon.privacyPolicy()
        assert privacy_policy == "some_privacy_policy"
