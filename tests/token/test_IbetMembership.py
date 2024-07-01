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
import pytest


def init_args(exchange_address):
    name = "test_membership"
    symbol = "MEM"
    initial_supply = 1000000
    tradable_exchange = exchange_address
    details = "some_details"
    return_details = "some_return"
    expiration_date = "20191231"
    memo = "some_memo"
    transferable = True
    contact_information = "some_contact_information"
    privacy_policy = "some_privacy_policy"

    deploy_args = [
        name,
        symbol,
        initial_supply,
        tradable_exchange,
        details,
        return_details,
        expiration_date,
        memo,
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
    def test_normal_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]

        # deploy
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # assertion
        owner_address = membership_contract.owner()
        name = membership_contract.name()
        symbol = membership_contract.symbol()
        total_supply = membership_contract.totalSupply()
        tradable_exchange = membership_contract.tradableExchange()
        details = membership_contract.details()
        return_details = membership_contract.returnDetails()
        expiration_date = membership_contract.expirationDate()
        memo = membership_contract.memo()
        transferable = membership_contract.transferable()
        status = membership_contract.status()
        balance = membership_contract.balanceOf(issuer)
        contact_information = membership_contract.contactInformation()
        privacy_policy = membership_contract.privacyPolicy()
        assert owner_address == issuer
        assert name == deploy_args[0]
        assert symbol == deploy_args[1]
        assert total_supply == deploy_args[2]
        assert tradable_exchange == deploy_args[3]
        assert details == deploy_args[4]
        assert return_details == deploy_args[5]
        assert expiration_date == deploy_args[6]
        assert memo == deploy_args[7]
        assert transferable == deploy_args[8]
        assert status is True
        assert balance == deploy_args[2]
        assert contact_information == deploy_args[9]
        assert privacy_policy == deploy_args[10]


# TEST_transfer
class TestTransfer:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1_1
    # Transfer to account address
    def test_normal_1_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        trader = users["trader"]
        transfer_amount = 100

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # transfer
        tx = membership_contract.transfer.transact(
            trader, transfer_amount, {"from": issuer}
        )

        # assertion
        issuer_balance = membership_contract.balanceOf(issuer)
        trader_balance = membership_contract.balanceOf(trader)
        assert issuer_balance == deploy_args[2] - transfer_amount
        assert trader_balance == transfer_amount

        assert tx.events["Transfer"]["from"] == issuer
        assert tx.events["Transfer"]["to"] == trader
        assert tx.events["Transfer"]["value"] == transfer_amount

    # Normal_1_2
    # Transfer to account address
    # Upper limit
    def test_normal_1_2(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        trader = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        deploy_args[2] = 2**256 - 1
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # transfer
        transfer_amount = 2**256 - 1
        tx = membership_contract.transfer.transact(
            trader, transfer_amount, {"from": issuer}
        )

        # assertion
        assert membership_contract.balanceOf(issuer) == 0
        assert membership_contract.balanceOf(trader) == 2**256 - 1

        assert tx.events["Transfer"]["from"] == issuer
        assert tx.events["Transfer"]["to"] == trader
        assert tx.events["Transfer"]["value"] == transfer_amount

    # Normal_2_1
    # Transfer to contract address
    def test_normal_2_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        transfer_amount = 100

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # transfer to contract address
        exchange_address = exchange.address
        tx = membership_contract.transfer.transact(
            exchange_address, transfer_amount, {"from": issuer}
        )

        # assertion
        assert membership_contract.balanceOf(issuer) == deploy_args[2] - transfer_amount
        assert membership_contract.balanceOf(exchange_address) == transfer_amount

        assert tx.events["Transfer"]["from"] == issuer
        assert tx.events["Transfer"]["to"] == exchange_address
        assert tx.events["Transfer"]["value"] == transfer_amount

    # Normal_2_2
    # Transfer to contract address
    # Upper limit
    def test_normal_2_2(self, users, IbetMembership, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        deploy_args[2] = 2**256 - 1
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # transfer
        exchange_address = exchange.address
        transfer_amount = 2**256 - 1
        tx = membership_contract.transfer.transact(
            exchange_address, transfer_amount, {"from": issuer}
        )

        # assertion
        assert membership_contract.balanceOf(issuer) == 0
        assert membership_contract.balanceOf(exchange_address) == 2**256 - 1

        assert tx.events["Transfer"]["from"] == issuer
        assert tx.events["Transfer"]["to"] == exchange_address
        assert tx.events["Transfer"]["value"] == transfer_amount

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    # Insufficient balance
    def test_error_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        trader = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # transfer
        transfer_amount = 10000000000
        with brownie.reverts(revert_msg="140101"):
            membership_contract.transfer.transact(
                trader, transfer_amount, {"from": issuer}
            )

        assert membership_contract.balanceOf(issuer) == deploy_args[2]
        assert membership_contract.balanceOf(trader) == 0

    # Error_2
    # Cannot access private functions
    def test_error_2(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        trader = users["trader"]

        transfer_amount = 100
        data = "test_data"

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        with pytest.raises(AttributeError):
            membership_contract.isContract(trader, {"from": issuer})

        with pytest.raises(AttributeError):
            membership_contract.transferToAddress.transact(
                trader, transfer_amount, data, {"from": issuer}
            )

        with pytest.raises(AttributeError):
            membership_contract.transferToContract.transact(
                trader, transfer_amount, data, {"from": issuer}
            )

    # Error_3
    # Not transferable token
    def test_error_3(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        trader = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        deploy_args[8] = False
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # transfer
        transfer_amount = 10
        with brownie.reverts(revert_msg="140102"):
            membership_contract.transfer(trader, transfer_amount, {"from": issuer})

        # assertion
        assert membership_contract.balanceOf(issuer) == deploy_args[2]
        assert membership_contract.balanceOf(trader) == 0

    # Error_4
    # Transfer to contract address
    # Not tradable exchange
    def test_error_4(
        self,
        users,
        IbetMembership,
        IbetExchange,
        exchange,
        exchange_storage,
        payment_gateway,
    ):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # deploy (not tradable exchange)
        not_tradable_exchange = users["admin"].deploy(
            IbetExchange, payment_gateway.address, exchange_storage.address
        )

        # transfer
        transfer_amount = 10
        with brownie.reverts(revert_msg="140001"):
            membership_contract.transfer.transact(
                not_tradable_exchange.address, transfer_amount, {"from": issuer}
            )

        # assertion
        assert membership_contract.balanceOf(issuer) == deploy_args[2]
        assert membership_contract.balanceOf(not_tradable_exchange.address) == 0


# TEST_bulkTransfer
class TestBulkTransfer:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Bulk transfer to account address (1 data)
    def test_normal_1(self, IbetMembership, users, exchange):
        from_address = users["issuer"]
        to_address = users["trader"]

        # issue membership token
        deploy_args = init_args(exchange.address)
        membership_contract = from_address.deploy(IbetMembership, *deploy_args)

        # bulk transfer
        to_address_list = [to_address]
        amount_list = [1]
        membership_contract.bulkTransfer.transact(
            to_address_list, amount_list, {"from": from_address}
        )

        # assertion
        from_balance = membership_contract.balanceOf(from_address)
        to_balance = membership_contract.balanceOf(to_address)
        assert from_balance == deploy_args[2] - 1
        assert to_balance == 1

    # Normal_2
    # Bulk transfer to account address (multiple data)
    def test_normal_2(self, IbetMembership, users, exchange):
        from_address = users["issuer"]
        to_address = users["trader"]

        # issue membership token
        deploy_args = init_args(exchange.address)
        membership_contract = from_address.deploy(IbetMembership, *deploy_args)

        # bulk transfer
        to_address_list = []
        amount_list = []
        for i in range(100):
            to_address_list.append(to_address)
            amount_list.append(1)
        membership_contract.bulkTransfer.transact(
            to_address_list, amount_list, {"from": from_address}
        )

        # assertion
        from_balance = membership_contract.balanceOf(from_address)
        to_balance = membership_contract.balanceOf(to_address)
        assert from_balance == deploy_args[2] - 100
        assert to_balance == 100

    # Normal_3
    # Bulk transfer to contract address
    def test_normal_3(self, IbetMembership, users, exchange):
        from_address = users["issuer"]

        # issue membership token
        deploy_args = init_args(exchange.address)
        membership_contract = from_address.deploy(IbetMembership, *deploy_args)

        # bulk transfer
        to_address_list = [exchange.address]
        amount_list = [1]
        membership_contract.bulkTransfer.transact(
            to_address_list, amount_list, {"from": from_address}
        )

        # assertion
        from_balance = membership_contract.balanceOf(from_address)
        to_balance = membership_contract.balanceOf(exchange.address)
        assert from_balance == deploy_args[2] - 1
        assert to_balance == 1

    #######################################
    # Error
    #######################################

    # Error_1
    # Over the limit
    def test_error_1(self, IbetMembership, users, exchange):
        from_address = users["issuer"]
        to_address = users["trader"]

        # issue membership token
        deploy_args = init_args(exchange.address)
        deploy_args[2] = 2**256 - 1
        membership_contract = from_address.deploy(IbetMembership, *deploy_args)

        # over the upper limit
        with brownie.reverts(revert_msg=""):
            membership_contract.bulkTransfer.transact(
                [to_address, to_address], [2**256 - 1, 1], {"from": from_address}
            )

        from_balance = membership_contract.balanceOf(from_address)
        to_balance = membership_contract.balanceOf(to_address)
        assert from_balance == deploy_args[2]
        assert to_balance == 0

    # Error_2
    # Insufficient balance
    def test_error_2(self, IbetMembership, users, exchange):
        from_address = users["issuer"]
        to_address = users["trader"]

        # issue membership token
        deploy_args = init_args(exchange.address)
        membership_contract = from_address.deploy(IbetMembership, *deploy_args)

        # bulk transfer
        with brownie.reverts(revert_msg="140202"):
            membership_contract.bulkTransfer.transact(
                [to_address, to_address], [deploy_args[2], 1], {"from": from_address}
            )  # error

        assert membership_contract.balanceOf(from_address) == deploy_args[2]
        assert membership_contract.balanceOf(to_address) == 0

    # Error_3
    # Non-transferable token
    def test_error_3(self, IbetMembership, users, exchange):
        from_address = users["issuer"]
        to_address = users["trader"]

        # issue membership token
        deploy_args = init_args(exchange.address)
        membership_contract = from_address.deploy(IbetMembership, *deploy_args)

        # change to non-transferable
        membership_contract.setTransferable.transact(False, {"from": from_address})

        # bulk transfer
        with brownie.reverts(revert_msg="140203"):
            membership_contract.bulkTransfer.transact(
                [to_address], [1], {"from": from_address}
            )  # error

        # assertion
        from_balance = membership_contract.balanceOf(from_address)
        to_balance = membership_contract.balanceOf(to_address)
        assert from_balance == deploy_args[2]
        assert to_balance == 0


# TEST_transferFrom
class TestTransferFrom:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1_1
    # Transfer to account address
    def test_normal_1_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        from_address = users["admin"]
        to_address = users["trader"]
        value = 100

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # transfer
        membership_contract.transfer.transact(from_address, value, {"from": issuer})

        # forced transfer
        tx = membership_contract.transferFrom.transact(
            from_address, to_address, value, {"from": issuer}
        )

        # assertion
        issuer_balance = membership_contract.balanceOf(issuer)
        from_balance = membership_contract.balanceOf(from_address)
        to_balance = membership_contract.balanceOf(to_address)
        assert issuer_balance == deploy_args[2] - value
        assert from_balance == 0
        assert to_balance == value

        assert tx.events["Transfer"]["from"] == from_address
        assert tx.events["Transfer"]["to"] == to_address
        assert tx.events["Transfer"]["value"] == value

    # Normal_1_2
    # Transfer to account address
    # Upper limit
    def test_normal_1_2(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        from_address = users["admin"]
        to_address = users["trader"]
        max_value = 2**256 - 1

        # issue token
        deploy_args = init_args(exchange.address)
        deploy_args[2] = max_value
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # transfer
        membership_contract.transfer.transact(from_address, max_value, {"from": issuer})

        # forced transfer
        tx = membership_contract.transferFrom.transact(
            from_address, to_address, max_value, {"from": issuer}
        )

        # assertion
        issuer_balance = membership_contract.balanceOf(issuer)
        from_balance = membership_contract.balanceOf(from_address)
        to_balance = membership_contract.balanceOf(to_address)
        assert issuer_balance == 0
        assert from_balance == 0
        assert to_balance == max_value

        assert tx.events["Transfer"]["from"] == from_address
        assert tx.events["Transfer"]["to"] == to_address
        assert tx.events["Transfer"]["value"] == max_value

    # Normal_2_1
    # Transfer to contract address
    def test_normal_2_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        from_address = users["trader"]
        value = 100

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)
        to_address = exchange.address

        # transfer
        membership_contract.transfer.transact(from_address, value, {"from": issuer})

        # forced transfer
        tx = membership_contract.transferFrom.transact(
            from_address, to_address, value, {"from": issuer}
        )

        # assertion
        issuer_balance = membership_contract.balanceOf(issuer)
        from_balance = membership_contract.balanceOf(from_address)
        to_balance = membership_contract.balanceOf(to_address)
        assert issuer_balance == deploy_args[2] - value
        assert from_balance == 0
        assert to_balance == value

        assert tx.events["Transfer"]["from"] == from_address
        assert tx.events["Transfer"]["to"] == to_address
        assert tx.events["Transfer"]["value"] == value

    # Normal_2_2
    # Transfer to contract address
    # Upper limit
    def test_normal_2_2(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        from_address = users["admin"]
        to_address = exchange.address
        max_value = 2**256 - 1

        # issue token
        deploy_args = init_args(exchange.address)
        deploy_args[2] = max_value
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # transfer
        membership_contract.transfer.transact(from_address, max_value, {"from": issuer})

        # forced transfer
        tx = membership_contract.transferFrom.transact(
            from_address, to_address, max_value, {"from": issuer}
        )

        issuer_balance = membership_contract.balanceOf(issuer)
        from_balance = membership_contract.balanceOf(from_address)
        to_balance = membership_contract.balanceOf(to_address)
        assert issuer_balance == 0
        assert from_balance == 0
        assert to_balance == max_value

        assert tx.events["Transfer"]["from"] == from_address
        assert tx.events["Transfer"]["to"] == to_address
        assert tx.events["Transfer"]["value"] == max_value

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    # Insufficient balance
    def test_error_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        to_address = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # forced transfer
        transfer_amount = 10000000000
        with brownie.reverts(revert_msg="140301"):
            membership_contract.transferFrom.transact(
                issuer, to_address, transfer_amount, {"from": issuer}
            )

        # assertion
        assert membership_contract.balanceOf(issuer) == deploy_args[2]
        assert membership_contract.balanceOf(to_address) == 0

    # Unauthorized
    def test_error_2(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        admin = users["admin"]
        to_address = users["trader"]
        transfer_amount = 100

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # forced transfer
        with brownie.reverts(revert_msg="500001"):
            membership_contract.transferFrom.transact(
                issuer, to_address, transfer_amount, {"from": admin}
            )

        # assertion
        assert membership_contract.balanceOf(issuer) == deploy_args[2]
        assert membership_contract.balanceOf(to_address) == 0


# TEST_balanceOf
class TestBalanceOf:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # assertion
        balance = membership_contract.balanceOf(issuer)
        assert balance == deploy_args[2]

    # Normal_2
    # No data
    def test_normal_2(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        trader = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # assertion
        balance = membership_contract.balanceOf(trader)
        assert balance == 0


# TEST_setDetails
class TestSetDetails:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        after_details = "after_details"

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # change token details
        membership_contract.setDetails.transact(after_details, {"from": issuer})

        # assertion
        details = membership_contract.details()
        assert after_details == details

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    # Unauthorized
    def test_error_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        attacker = users["trader"]
        after_details = "after_details"

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # change token details
        with brownie.reverts(revert_msg="500001"):
            membership_contract.setDetails.transact(after_details, {"from": attacker})

        # assertion
        details = membership_contract.details()
        assert details == deploy_args[4]


# TEST_setReturnDetails
class TestSetReturnDetails:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        after_return_details = "after_return_details"

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # set return details
        membership_contract.setReturnDetails.transact(
            after_return_details, {"from": issuer}
        )

        # assertion
        return_details = membership_contract.returnDetails()
        assert after_return_details == return_details

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    # Unauthorized
    def test_error_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        attacker = users["trader"]
        after_return_details = "after_return_details"

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # set return details
        with brownie.reverts(revert_msg="500001"):
            membership_contract.setReturnDetails.transact(
                after_return_details, {"from": attacker}
            )

        # assertion
        return_details = membership_contract.returnDetails()
        assert return_details == deploy_args[5]


# TEST_setExpirationDate
class TestSetExpirationDate:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        after_expiration_date = "after_expiration_date"

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # set expiration date
        membership_contract.setExpirationDate.transact(
            after_expiration_date, {"from": issuer}
        )

        # assertion
        expiration_date = membership_contract.expirationDate()
        assert after_expiration_date == expiration_date

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    # Unauthorized
    def test_error_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        attacker = users["trader"]
        after_expiration_date = "after_expiration_date"

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # set expiration date
        with brownie.reverts(revert_msg="500001"):
            membership_contract.setExpirationDate.transact(
                after_expiration_date, {"from": attacker}
            )

        # assertion
        expiration_date = membership_contract.expirationDate()
        assert expiration_date == deploy_args[6]


# TEST_setMemo
class TestSetMemo:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        after_memo = "after_memo"

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # set memo
        membership_contract.setMemo.transact(after_memo, {"from": issuer})

        # assertion
        memo = membership_contract.memo()
        assert after_memo == memo

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    # Unauthorized
    def test_error_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        attacker = users["trader"]
        after_memo = "after_memo"

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # set memo
        with brownie.reverts(revert_msg="500001"):
            membership_contract.setMemo.transact(after_memo, {"from": attacker})

        # assertion
        memo = membership_contract.memo()
        assert memo == deploy_args[7]


# TEST_setTransferable
class TestSetTransferable:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        after_transferable = False

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # set transferable
        membership_contract.setTransferable.transact(
            after_transferable, {"from": issuer}
        )

        # assertion
        transferable = membership_contract.transferable()
        assert after_transferable == transferable

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    # Unauthorized
    def test_error_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        attacker = users["trader"]
        after_transferable = False

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # set transferable
        with brownie.reverts(revert_msg="500001"):
            membership_contract.setTransferable.transact(
                after_transferable, {"from": attacker}
            )

        # assertion
        transferable = membership_contract.transferable()
        assert transferable == deploy_args[8]


# TEST_setStatus
class TestSetStatus:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        after_status = False

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # change status
        membership_contract.setStatus.transact(after_status, {"from": issuer})

        # assertion
        status = membership_contract.status()
        assert after_status == status

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    # Unauthorized
    def test_error_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        attacker = users["trader"]
        after_status = False

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # change status
        with brownie.reverts(revert_msg="500001"):
            membership_contract.setStatus.transact(after_status, {"from": attacker})

        # assertion
        status = membership_contract.status()
        assert status is True


# TEST_setImageURL, getImageURL
class TestSetImageUrl:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        after_url = "http://hoge.com"

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # set image url
        membership_contract.setImageURL.transact(0, after_url, {"from": issuer})

        # assertion
        url = membership_contract.getImageURL(0)
        assert after_url == url

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    # Unauthorized
    def test_error_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        attacker = users["trader"]
        after_url = "http://hoge.com"

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # set image url
        with brownie.reverts(revert_msg="500001"):
            membership_contract.setImageURL.transact(0, after_url, {"from": attacker})

        # assertion
        url = membership_contract.getImageURL(0)
        assert url == ""


# TEST_issue
class TestIssue:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        value = 10

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # additional issue
        membership_contract.issue.transact(value, {"from": issuer})

        # assertion
        total_supply = membership_contract.totalSupply()
        balance = membership_contract.balanceOf(issuer)
        assert total_supply == deploy_args[2] + value
        assert balance == deploy_args[2] + value

    # Normal_2
    # Upper limit
    def test_normal_2(self, users, IbetMembership, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        deploy_args[2] = 2**256 - 2
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # additional issue
        membership_contract.issue.transact(1, {"from": issuer})

        # assertion
        total_supply = membership_contract.totalSupply()
        balance = membership_contract.balanceOf(issuer)
        assert total_supply == 2**256 - 1
        assert balance == 2**256 - 1

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    # Exceeding the upper limit
    def test_error_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        deploy_args[2] = 2**256 - 1
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # additional issue
        with brownie.reverts(revert_msg="Integer overflow"):
            membership_contract.issue.transact(1, {"from": issuer})

        # assertion
        total_supply = membership_contract.totalSupply()
        balance = membership_contract.balanceOf(issuer)
        assert total_supply == deploy_args[2]
        assert balance == deploy_args[2]

    # Error_2
    # Unauthorized
    def test_error_2(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        attacker = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # additional issue
        with brownie.reverts(revert_msg="500001"):
            membership_contract.issue.transact(1, {"from": attacker})

        # assertion
        total_supply = membership_contract.totalSupply()
        balance = membership_contract.balanceOf(issuer)
        assert total_supply == deploy_args[2]
        assert balance == deploy_args[2]


# TEST_setTradableExchange
class TestSetTradableExchange:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # change exchange contract
        membership_contract.setTradableExchange.transact(
            brownie.ZERO_ADDRESS, {"from": issuer}
        )

        # assertion
        assert membership_contract.tradableExchange() == brownie.ZERO_ADDRESS

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    # Unauthorized
    def test_error_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        trader = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # change exchange contract
        with brownie.reverts(revert_msg="500001"):
            membership_contract.setTradableExchange.transact(
                brownie.ZERO_ADDRESS, {"from": trader}
            )

        # assertion
        assert membership_contract.tradableExchange() == exchange.address


# TEST_setInitialOfferingStatus
class TestSetInitialOfferingStatus:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)
        assert membership_contract.initialOfferingStatus() is False

        # change offering status
        membership_contract.setInitialOfferingStatus.transact(True, {"from": issuer})

        # assertion
        assert membership_contract.initialOfferingStatus() is True

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    # Unauthorized
    def test_error_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # change offering status
        with brownie.reverts(revert_msg="500001"):
            membership_contract.setInitialOfferingStatus.transact(
                True, {"from": users["user1"]}
            )

        # assertion
        assert membership_contract.initialOfferingStatus() is False


# TEST_applyForOffering
class TestApplyForOffering:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    # Default value
    def test_normal_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        trader = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)
        membership_contract.setInitialOfferingStatus.transact(True, {"from": issuer})

        # assertion
        assert membership_contract.applications(trader) == ""

    # Normal_2
    def test_normal_2(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        trader = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)
        membership_contract.setInitialOfferingStatus.transact(True, {"from": issuer})

        # apply for
        tx = membership_contract.applyForOffering.transact("abcdefgh", {"from": trader})

        # assertion
        assert membership_contract.applications(trader) == "abcdefgh"

        assert tx.events["ApplyFor"]["accountAddress"] == trader

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    # Offering status is False
    def test_error_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        trader = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # apply for
        with brownie.reverts(revert_msg="140401"):
            membership_contract.applyForOffering.transact("abcdefgh", {"from": trader})

        # assertion
        assert membership_contract.applications(trader) == ""


# TEST_setContactInformation
class TestSetContactInformation:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # set contact information
        membership_contract.setContactInformation.transact(
            "updated contact information", {"from": issuer}
        )

        # assertion
        contact_information = membership_contract.contactInformation()
        assert contact_information == "updated contact information"

    #######################################
    # Error
    #######################################

    # Error_1
    def test_error_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        other = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # set contact information
        with brownie.reverts(revert_msg="500001"):
            membership_contract.setContactInformation.transact(
                "updated contact information", {"from": other}
            )

        # assertion
        contact_information = membership_contract.contactInformation()
        assert contact_information == "some_contact_information"


# TEST_setPrivacyPolicy
class TestSetPrivacyPolicy:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # set privacy policy
        membership_contract.setPrivacyPolicy.transact(
            "updated privacy policy", {"from": issuer}
        )

        # assertion
        privacy_policy = membership_contract.privacyPolicy()
        assert privacy_policy == "updated privacy policy"

    #######################################
    # Error
    #######################################

    # Error_1
    # Unauthorized
    def test_error_1(self, users, IbetMembership, exchange):
        issuer = users["issuer"]
        other = users["trader"]

        # issue token
        deploy_args = init_args(exchange.address)
        membership_contract = issuer.deploy(IbetMembership, *deploy_args)

        # set privacy policy
        with brownie.reverts(revert_msg="500001"):
            membership_contract.setPrivacyPolicy.transact(
                "updated privacy policy", {"from": other}
            )

        # assertion
        privacy_policy = membership_contract.privacyPolicy()
        assert privacy_policy == "some_privacy_policy"
