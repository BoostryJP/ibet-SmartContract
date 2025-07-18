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
import brownie_utils
import pytest


def init_args():
    name = "test_bond"
    symbol = "BND"
    total_supply = 2**256 - 1
    face_value = 2**256 - 1
    face_value_currency = "JPY"
    redemption_date = "20191231"
    redemption_value = 2**256 - 1
    redemption_value_currency = "JPY"
    return_date = "20191231"
    return_amount = "some_return"
    purpose = "some_purpose"

    deploy_args = [
        name,
        symbol,
        total_supply,
        face_value,
        face_value_currency,
        redemption_date,
        redemption_value,
        redemption_value_currency,
        return_date,
        return_amount,
        purpose,
    ]
    return deploy_args


def issue_transferable_bond_token(issuer, exchange_address, personal_info_address):
    from brownie import IbetStraightBond

    name = "test_bond"
    symbol = "BND"
    total_supply = 10000
    face_value = 10000
    face_value_currency = "JPY"
    redemption_date = "20191231"
    redemption_value = 100
    redemption_value_currency = "JPY"
    return_date = "20191231"
    return_amount = "some_return"
    purpose = "some_purpose"

    deploy_args = [
        name,
        symbol,
        total_supply,
        face_value,
        face_value_currency,
        redemption_date,
        redemption_value,
        redemption_value_currency,
        return_date,
        return_amount,
        purpose,
    ]

    bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)
    bond_token.setTradableExchange.transact(exchange_address, {"from": issuer})
    bond_token.setPersonalInfoAddress.transact(personal_info_address, {"from": issuer})
    bond_token.setTransferable.transact(True, {"from": issuer})
    return bond_token, deploy_args


# TEST_deploy
class TestDeploy:
    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]
        deploy_args = init_args()
        bond_contract = brownie_utils.force_deploy(
            issuer, IbetStraightBond, *deploy_args
        )

        # assertion
        owner_address = bond_contract.owner()
        name = bond_contract.name()
        symbol = bond_contract.symbol()
        total_supply = bond_contract.totalSupply()
        face_value = bond_contract.faceValue()
        face_value_currency = bond_contract.faceValueCurrency()
        redemption_date = bond_contract.redemptionDate()
        redemption_value = bond_contract.redemptionValue()
        redemption_value_currency = bond_contract.redemptionValueCurrency()
        return_date = bond_contract.returnDate()
        return_amount = bond_contract.returnAmount()
        purpose = bond_contract.purpose()
        transferable = bond_contract.transferable()
        balance = bond_contract.balanceOf(issuer)
        is_redeemed = bond_contract.isRedeemed()
        status = bond_contract.status()
        requirePersonalInfoRegistered = bond_contract.requirePersonalInfoRegistered()

        assert owner_address == issuer
        assert name == deploy_args[0]
        assert symbol == deploy_args[1]
        assert total_supply == deploy_args[2]
        assert face_value == deploy_args[3]
        assert face_value_currency == deploy_args[4]
        assert redemption_date == deploy_args[5]
        assert redemption_value == deploy_args[6]
        assert redemption_value_currency == deploy_args[7]
        assert return_date == deploy_args[8]
        assert return_amount == deploy_args[9]
        assert purpose == deploy_args[10]
        assert transferable == False
        assert balance == total_supply
        assert is_redeemed == False
        assert status == True
        assert requirePersonalInfoRegistered == True


# TEST_transfer
class TestTransfer:
    #######################################
    # Normal
    #######################################

    # Normal_1_1
    # Transfer to EOA
    # - requirePersonalInfoRegistered = true
    def test_normal_1_1(self, users, personal_info):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["trader"]
        transfer_amount = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # register personal info of to_address
        personal_info.register.transact(
            from_address.address, "encrypted_message", {"from": to_address}
        )

        # transfer
        tx = bond_token.transfer.transact(
            to_address.address, transfer_amount, {"from": issuer}
        )

        # assertion
        assert bond_token.balanceOf(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balanceOf(to_address) == transfer_amount

        assert tx.events["Transfer"]["from"] == from_address
        assert tx.events["Transfer"]["to"] == to_address
        assert tx.events["Transfer"]["value"] == transfer_amount

    # Normal_1_2
    # Transfer to EOA
    # - requirePersonalInfoRegistered = false
    def test_normal_1_2(self, users, personal_info):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["trader"]
        transfer_amount = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # set requirePersonalInfoRegistered to False
        bond_token.setRequirePersonalInfoRegistered.transact(False, {"from": issuer})

        # transfer
        tx = bond_token.transfer.transact(
            to_address.address, transfer_amount, {"from": issuer}
        )

        # assertion
        assert bond_token.balanceOf(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balanceOf(to_address) == transfer_amount

        assert tx.events["Transfer"]["from"] == from_address
        assert tx.events["Transfer"]["to"] == to_address
        assert tx.events["Transfer"]["value"] == transfer_amount

    # Normal_2
    # Transfer to contract address
    def test_normal_2(self, users, exchange, personal_info):
        issuer = users["issuer"]
        from_address = issuer
        transfer_amount = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=exchange.address,
            personal_info_address=personal_info.address,
        )

        # transfer
        to_address = exchange.address
        tx = bond_token.transfer.transact(
            to_address, transfer_amount, {"from": from_address}
        )

        # assertion
        assert bond_token.balanceOf(from_address) == deploy_args[3] - transfer_amount
        assert bond_token.balanceOf(to_address) == transfer_amount

        assert tx.events["Transfer"]["from"] == from_address
        assert tx.events["Transfer"]["to"] == to_address
        assert tx.events["Transfer"]["value"] == transfer_amount

    #######################################
    # Error
    #######################################

    # Error_1
    # Insufficient balance
    def test_error_1(self, users, personal_info):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["trader"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # register personal info of to_address
        personal_info.register.transact(
            from_address.address, "encrypted_message", {"from": to_address}
        )

        # transfer
        transfer_amount = deploy_args[3] + 1
        with brownie.reverts(revert_msg="120401"):
            bond_token.transfer.transact(
                to_address.address, transfer_amount, {"from": issuer}
            )

        # assertion
        assert bond_token.balanceOf(issuer) == deploy_args[3]
        assert bond_token.balanceOf(to_address) == 0

    # Error_2
    # Cannot access private function
    def test_error_2(self, users):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["trader"]
        transfer_amount = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=brownie.ZERO_ADDRESS,
        )

        with pytest.raises(AttributeError):
            bond_token.isContract(to_address)

        with pytest.raises(AttributeError):
            bond_token.transferToAddress.transact(
                to_address, transfer_amount, "test_data", {"from": from_address}
            )

        with pytest.raises(AttributeError):
            bond_token.transferToContract.transact(
                to_address, transfer_amount, "test_data", {"from": from_address}
            )

    # Error_3
    # Not transferable token
    def test_error_3(self, users, IbetStraightBond):
        issuer = users["issuer"]
        to_address = users["trader"]
        transfer_amount = 100

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # set to not transferable
        bond_token.setTransferable(False, {"from": issuer})

        # transfer
        with brownie.reverts(revert_msg="120402"):
            bond_token.transfer.transact(to_address, transfer_amount, {"from": issuer})

        # assertion
        from_balance = bond_token.balanceOf(issuer)
        to_balance = bond_token.balanceOf(to_address)
        assert from_balance == deploy_args[3]
        assert to_balance == 0

    # Error_4
    # Transfer to non-tradable exchange
    def test_error_4(self, users, exchange):
        issuer = users["issuer"]
        transfer_amount = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=brownie.ZERO_ADDRESS,
        )

        # transfer
        with brownie.reverts(revert_msg="120301"):
            bond_token.transfer.transact(exchange, transfer_amount, {"from": issuer})

        assert bond_token.balanceOf(issuer) == deploy_args[3]
        assert bond_token.balanceOf(exchange) == 0

    # Error_5
    # Transfer to an address with personal information not registered
    def test_error_5(self, users, personal_info):
        issuer = users["issuer"]
        to_address = users["trader"]
        transfer_amount = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # transfer
        with brownie.reverts(revert_msg="120202"):
            bond_token.transfer.transact(
                to_address.address, transfer_amount, {"from": issuer}
            )

        # assertion
        assert bond_token.balanceOf(issuer) == deploy_args[3]
        assert bond_token.balanceOf(to_address) == 0


# TEST_bulkTransfer
class TestBulkTransfer:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Bulk transfer to account address (1 data)
    def test_normal_1(self, users, personal_info):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["trader"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # register personal info (to_address)
        personal_info.register.transact(
            from_address.address, "encrypted_message", {"from": to_address}
        )

        # bulk transfer
        to_address_list = [to_address]
        amount_list = [1]
        bond_token.bulkTransfer.transact(
            to_address_list, amount_list, {"from": from_address}
        )

        # assertion
        from_balance = bond_token.balanceOf(from_address)
        to_balance = bond_token.balanceOf(to_address)
        assert from_balance == deploy_args[3] - 1
        assert to_balance == 1

    # Normal_2_1
    # Bulk transfer to account address (multiple data)
    # - requirePersonalInfoRegistered = true
    def test_normal_2_1(self, users, personal_info):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["trader"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # register personal info (to_address)
        personal_info.register.transact(
            from_address.address, "encrypted_message", {"from": to_address}
        )

        # bulk transfer
        to_address_list = []
        amount_list = []
        for i in range(100):
            to_address_list.append(to_address)
            amount_list.append(1)

        bond_token.bulkTransfer.transact(
            to_address_list, amount_list, {"from": from_address}
        )

        # assertion
        from_balance = bond_token.balanceOf(from_address)
        to_balance = bond_token.balanceOf(to_address)
        assert from_balance == deploy_args[3] - 100
        assert to_balance == 100

    # Normal_2_2
    # Bulk transfer to account address (multiple data)
    # - requirePersonalInfoRegistered = false
    def test_normal_2_2(self, users, personal_info):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["trader"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # set requirePersonalInfoRegistered to False
        bond_token.setRequirePersonalInfoRegistered.transact(False, {"from": issuer})

        # bulk transfer
        to_address_list = []
        amount_list = []
        for i in range(100):
            to_address_list.append(to_address)
            amount_list.append(1)

        bond_token.bulkTransfer.transact(
            to_address_list, amount_list, {"from": from_address}
        )

        # assertion
        from_balance = bond_token.balanceOf(from_address)
        to_balance = bond_token.balanceOf(to_address)
        assert from_balance == deploy_args[3] - 100
        assert to_balance == 100

    # Normal_3
    # Bulk transfer to contract address
    def test_normal_3(self, users, exchange, personal_info):
        issuer = users["issuer"]
        from_address = issuer

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=exchange.address,
            personal_info_address=personal_info.address,
        )

        # bulk transfer
        to_address_list = [exchange.address]
        amount_list = [1]
        bond_token.bulkTransfer.transact(
            to_address_list, amount_list, {"from": from_address}
        )

        # assertion
        from_balance = bond_token.balanceOf(from_address)
        to_balance = bond_token.balanceOf(exchange.address)
        assert from_balance == deploy_args[3] - 1
        assert to_balance == 1

    #######################################
    # Error
    #######################################

    # Error_1
    # Insufficient balance
    def test_error_1(self, users, personal_info):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["trader"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # register personal info (to_address)
        personal_info.register.transact(
            from_address, "encrypted_message", {"from": to_address}
        )

        # bulk transfer
        with brownie.reverts(revert_msg="120502"):
            bond_token.bulkTransfer.transact(
                [to_address, to_address], [deploy_args[3], 1], {"from": issuer}
            )

        # assertion
        assert bond_token.balanceOf(issuer) == deploy_args[3]
        assert bond_token.balanceOf(to_address) == 0

    # Error_2
    # Not transferable token
    def test_error_2(self, users, personal_info):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["trader"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )
        bond_token.setTransferable.transact(False, {"from": issuer})

        # register personal info (to_address)
        personal_info.register.transact(
            from_address, "encrypted_message", {"from": to_address}
        )

        # bulk transfer
        with brownie.reverts(revert_msg="120503"):
            bond_token.bulkTransfer.transact([to_address], [1], {"from": issuer})

        # assertion
        from_balance = bond_token.balanceOf(issuer)
        to_balance = bond_token.balanceOf(to_address)
        assert from_balance == deploy_args[3]
        assert to_balance == 0

    # Error_3
    # Transfer to an address with no personal information registered
    def test_error_3(self, users, personal_info):
        issuer = users["issuer"]
        to_address = users["trader"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # bulk transfer
        with brownie.reverts(revert_msg="120202"):
            bond_token.bulkTransfer.transact([to_address], [1], {"from": issuer})

        # assertion
        from_balance = bond_token.balanceOf(issuer)
        to_balance = bond_token.balanceOf(to_address)
        assert from_balance == deploy_args[3]
        assert to_balance == 0


# TEST_transferFrom
class TestTransferFrom:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, personal_info):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["user1"]
        value = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # forced transfer
        bond_token.transferFrom.transact(
            from_address, to_address, value, {"from": issuer}
        )

        # assertion
        assert bond_token.balanceOf(issuer) == deploy_args[3] - value
        assert bond_token.balanceOf(to_address) == value

    #######################################
    # Error
    #######################################

    # Error_1
    # Insufficient balance
    def test_error_1(self, users, personal_info):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["user1"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # forced transfer
        with brownie.reverts(revert_msg="120601"):
            bond_token.transferFrom.transact(
                from_address, to_address, deploy_args[3] + 1, {"from": issuer}
            )

        # assertion
        assert bond_token.balanceOf(issuer) == deploy_args[3]
        assert bond_token.balanceOf(to_address) == 0

    # Error_2
    # Not authorized
    def test_error_2(self, users, personal_info):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["user1"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # forced transfer
        with brownie.reverts(revert_msg="500001"):
            bond_token.transferFrom.transact(
                from_address, to_address, deploy_args[3] + 1, {"from": to_address}
            )

        # assertion
        assert bond_token.balanceOf(issuer) == deploy_args[3]
        assert bond_token.balanceOf(to_address) == 0


# TEST_bulkTransferFrom
class TestBulkTransferFrom:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, personal_info):
        issuer = users["issuer"]
        to_address_1 = users["user1"]
        to_address_2 = users["user2"]
        value = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # bulk forced transfer
        #   issuer -> to_address_1 -> to_address_2
        bond_token.bulkTransferFrom.transact(
            [issuer, to_address_1],
            [to_address_1, to_address_2],
            [value, value],
            {"from": issuer},
        )

        # assertion
        assert bond_token.balanceOf(issuer) == deploy_args[3] - value
        assert bond_token.balanceOf(to_address_1) == 0
        assert bond_token.balanceOf(to_address_2) == value

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    # -> revert: 500001
    def test_error_1(self, users, personal_info):
        issuer = users["issuer"]
        to_address = users["user1"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # bulk forced transfer
        with brownie.reverts(revert_msg="500001"):
            bond_token.bulkTransferFrom.transact(
                [issuer], [to_address], [10, 10], {"from": to_address}
            )

        # assertion
        assert bond_token.balanceOf(issuer) == deploy_args[3]
        assert bond_token.balanceOf(to_address) == 0

    # Error_2
    # Some list lengths are unequal.
    # -> revert: 121501
    def test_error_2(self, users, personal_info):
        issuer = users["issuer"]
        to_address_1 = users["user1"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # bulk forced transfer
        with brownie.reverts(revert_msg="121501"):
            bond_token.bulkTransferFrom.transact(
                [issuer, issuer], [to_address_1], [10, 10], {"from": issuer}
            )

        # assertion
        assert bond_token.balanceOf(issuer) == deploy_args[3]
        assert bond_token.balanceOf(to_address_1) == 0

    # Error_3
    # Insufficient balance
    # -> revert: 120601
    def test_error_3(self, users, personal_info):
        issuer = users["issuer"]
        to_address_1 = users["user1"]
        to_address_2 = users["user2"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # bulk forced transfer
        #   issuer -> to_address_1
        #   to_address_2 -> to_address_1
        with brownie.reverts(revert_msg="120601"):
            bond_token.bulkTransferFrom.transact(
                [issuer, to_address_2],
                [to_address_1, to_address_1],
                [10, 10],
                {"from": issuer},
            )

        # assertion
        assert bond_token.balanceOf(issuer) == deploy_args[3]
        assert bond_token.balanceOf(to_address_1) == 0
        assert bond_token.balanceOf(to_address_2) == 0


# TEST_balanceOf
class TestBalanceOf:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # assertion
        balance = bond_token.balanceOf(issuer)
        assert balance == deploy_args[3]


# TEST_setTradableExchange
class TestSetTradableExchange:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # change exchange contract
        bond_token.setTradableExchange.transact(brownie.ETH_ADDRESS, {"from": issuer})

        # assertion
        assert bond_token.tradableExchange() == brownie.ETH_ADDRESS

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # change exchange contract
        with brownie.reverts(revert_msg="500001"):
            bond_token.setTradableExchange.transact(
                brownie.ETH_ADDRESS, {"from": users["user1"]}
            )

        # assertion
        assert bond_token.tradableExchange() == brownie.ZERO_ADDRESS


# TEST_setPersonalInfoAddress
class TestSetPersonalInfoAddress:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update contract
        bond_token.setPersonalInfoAddress.transact(
            brownie.ETH_ADDRESS, {"from": issuer}
        )

        # assertion
        assert bond_token.personalInfoAddress() == brownie.ETH_ADDRESS

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update contract
        with brownie.reverts(revert_msg="500001"):
            bond_token.setPersonalInfoAddress.transact(
                brownie.ETH_ADDRESS, {"from": users["user1"]}
            )

        # assertion
        assert bond_token.personalInfoAddress() == brownie.ZERO_ADDRESS


# TEST_setRequirePersonalInfoRegistered
class TestSetRequirePersonalInfoRegistered:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        # update contract
        bond_token.setRequirePersonalInfoRegistered.transact(False, {"from": issuer})

        # assertion
        assert bond_token.requirePersonalInfoRegistered() == False

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        # update contract
        with brownie.reverts(revert_msg="500001"):
            bond_token.setRequirePersonalInfoRegistered.transact(
                False, {"from": users["user1"]}
            )

        # assertion
        assert bond_token.requirePersonalInfoRegistered() == True


# TEST_setContactInformation
class TestSetContactInformation:
    #######################################
    # Normal
    #######################################

    # 正常系1: 発行（デプロイ） -> 修正
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.setContactInformation.transact(
            "updated contact information", {"from": issuer}
        )

        # assertion
        contact_information = bond_token.contactInformation()
        assert contact_information == "updated contact information"

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        with brownie.reverts(revert_msg="500001"):
            bond_token.setContactInformation.transact(
                "updated contact information", {"from": users["user1"]}
            )

        # assertion
        contact_information = bond_token.contactInformation()
        assert contact_information == ""


# TEST_setPrivacyPolicy
class TestSetPrivacyPolicy:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.setPrivacyPolicy.transact("updated privacy policy", {"from": issuer})

        # assertion
        privacy_policy = bond_token.privacyPolicy()
        assert privacy_policy == "updated privacy policy"

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        with brownie.reverts(revert_msg="500001"):
            bond_token.setPrivacyPolicy.transact(
                "updated privacy policy", {"from": users["user1"]}
            )

        # assertion
        privacy_policy = bond_token.privacyPolicy()
        assert privacy_policy == ""


# TEST_setMemo
class TestSetMemo:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # set memo
        bond_token.setMemo.transact("updated memo", {"from": issuer})

        # assertion
        memo = bond_token.memo()
        assert memo == "updated memo"

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # set memo
        with brownie.reverts(revert_msg="500001"):
            bond_token.setMemo.transact("updated memo", {"from": users["user1"]})

        memo = bond_token.memo()
        assert memo == ""


# TEST_setInterestRate
class TestSetInterestRate:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_setInterestRate_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.setInterestRate.transact(123, {"from": issuer})

        # assertion
        interest_rate = bond_token.interestRate()
        assert interest_rate == 123

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_setInterestRate_error_2(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        with brownie.reverts(revert_msg="500001"):
            bond_token.setInterestRate.transact(123, {"from": users["user1"]})

        # assertion
        interest_rate = bond_token.interestRate()
        assert interest_rate == 0


# TEST_setInterestPaymentDate
class TestSetInterestPaymentDate:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.setInterestPaymentDate.transact(
            '{"interestPaymentDate1":"0331","interestPaymentDate2":"0930"}',
            {"from": issuer},
        )

        # assertion
        interest_payment_date = bond_token.interestPaymentDate()
        assert (
            interest_payment_date
            == '{"interestPaymentDate1":"0331","interestPaymentDate2":"0930"}'
        )

    #######################################
    # Error
    #######################################

    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # Owner以外のアドレスから更新 -> Failure
        with brownie.reverts(revert_msg="500001"):
            bond_token.setInterestPaymentDate.transact(
                '{"interestPaymentDate1":"0331","interestPaymentDate2":"0930"}',
                {"from": users["user1"]},
            )

        # assertion
        interest_payment_date = bond_token.interestPaymentDate()
        assert interest_payment_date == ""


# TEST_setTransferable
class TestSetTransferable:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.setTransferable.transact(True, {"from": issuer})

        # assertion
        assert bond_token.transferable() is True

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        with brownie.reverts(revert_msg="500001"):
            bond_token.setTransferable.transact(True, {"from": users["user1"]})

        # assertion
        assert bond_token.transferable() is False


# TEST_setStatus
class TestSetStatus:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.setStatus(False, {"from": issuer})

        # assertion
        assert bond_token.status() is False

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # change exchange contract
        with brownie.reverts(revert_msg="500001"):
            bond_token.setStatus(False, {"from": users["user1"]})


# TEST_changeOfferingStatus
class TestChangeOfferingStatus:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.changeOfferingStatus(True, {"from": issuer})

        # assertion
        assert bond_token.status() is True

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # change exchange contract
        with brownie.reverts(revert_msg="500001"):
            bond_token.changeOfferingStatus(True, {"from": users["user1"]})


# TEST_applyForOffering
class TestApplyForOffering:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Default value
    def test_normal_1(self, users, personal_info):
        issuer = users["issuer"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # assertion
        application = bond_token.applicationsForOffering(brownie.ETH_ADDRESS)
        assert application[0] == 0
        assert application[1] == 0
        assert application[2] == ""

    # Normal_2_1
    # Apply for offering
    # - requirePersonalInfoRegistered = true
    def test_normal_2_1(self, users, personal_info):
        issuer = users["issuer"]
        applicant = users["user1"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # update offering status
        bond_token.changeOfferingStatus.transact(True, {"from": issuer})

        # register personal info of applicant
        personal_info.register.transact(
            issuer, "encrypted_message", {"from": applicant}
        )

        # apply for offering
        bond_token.applyForOffering.transact(10, "abcdefgh", {"from": applicant})

        # assertion
        application = bond_token.applicationsForOffering(applicant)
        assert application[0] == 10
        assert application[1] == 0
        assert application[2] == "abcdefgh"

    # Normal_2_2
    # Apply for offering
    # - requirePersonalInfoRegistered = false
    def test_normal_2_2(self, users, personal_info):
        issuer = users["issuer"]
        applicant = users["user1"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # update offering status
        bond_token.changeOfferingStatus.transact(True, {"from": issuer})

        # set requirePersonalInfoRegistered to False
        bond_token.setRequirePersonalInfoRegistered.transact(False, {"from": issuer})

        # apply for offering
        bond_token.applyForOffering.transact(10, "abcdefgh", {"from": applicant})

        # assertion
        application = bond_token.applicationsForOffering(applicant)
        assert application[0] == 10
        assert application[1] == 0
        assert application[2] == "abcdefgh"

    # Normal_3
    # Multiple applications
    def test_normal_3(self, users, personal_info):
        issuer = users["issuer"]
        applicant = users["user1"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # update offering status
        bond_token.changeOfferingStatus.transact(True, {"from": issuer})

        # register personal info of applicant
        personal_info.register.transact(
            issuer, "encrypted_message", {"from": applicant}
        )

        # apply for offering (1)
        bond_token.applyForOffering.transact(10, "abcdefgh", {"from": applicant})

        # apply for offering (2)
        bond_token.applyForOffering.transact(20, "vwxyz", {"from": applicant})

        # assertion
        application = bond_token.applicationsForOffering(applicant)
        assert application[0] == 20
        assert application[1] == 0
        assert application[2] == "vwxyz"

    #######################################
    # Error
    #######################################

    # Error_1
    # The offering status must be true.
    def test_error_1(self, users, personal_info):
        issuer = users["issuer"]
        applicant = users["user1"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # apply for offering
        with brownie.reverts(revert_msg="121001"):
            bond_token.applyForOffering.transact(10, "abcdefgh", {"from": applicant})

        # assertion
        application = bond_token.applicationsForOffering(applicant)
        assert application[0] == 0
        assert application[1] == 0
        assert application[2] == ""

    # Error_2
    # Applicant need to register personal information.
    def test_error_2(self, users, personal_info):
        issuer = users["issuer"]
        applicant = users["user1"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # update offering status
        bond_token.changeOfferingStatus.transact(True, {"from": issuer})

        # apply for offering
        with brownie.reverts(revert_msg="121002"):
            bond_token.applyForOffering.transact(10, "abcdefgh", {"from": applicant})

        # assertion
        application = bond_token.applicationsForOffering(applicant)
        assert application[0] == 0
        assert application[1] == 0
        assert application[2] == ""


# TEST_allot
class TestAllot:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, personal_info):
        issuer = users["issuer"]
        applicant = users["user1"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # update offering status
        bond_token.changeOfferingStatus.transact(True, {"from": issuer})

        # register personal info of applicant
        personal_info.register.transact(
            issuer, "encrypted_message", {"from": applicant}
        )

        # apply for offering
        bond_token.applyForOffering.transact(10, "abcdefgh", {"from": applicant})

        # allot
        bond_token.allot.transact(applicant, 5, {"from": issuer})

        # assertion
        application = bond_token.applicationsForOffering(applicant)
        assert application[0] == 10
        assert application[1] == 5
        assert application[2] == "abcdefgh"

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, personal_info):
        issuer = users["issuer"]
        applicant = users["user1"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # update offering status
        bond_token.changeOfferingStatus.transact(True, {"from": issuer})

        # allot
        with brownie.reverts(revert_msg="500001"):
            bond_token.allot.transact(applicant, 5, {"from": applicant})

        # assertion
        application = bond_token.applicationsForOffering(applicant)
        assert application[0] == 0
        assert application[1] == 0
        assert application[2] == ""


# TEST_changeToRedeemed
class TestChangeToRedeemed:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_redeem_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # redeem
        bond_token.changeToRedeemed.transact({"from": issuer})

        # assertion
        is_redeemed = bond_token.isRedeemed()
        assert is_redeemed is True

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_redeem_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # redeem
        with brownie.reverts(revert_msg="500001"):
            bond_token.changeToRedeemed.transact({"from": users["user1"]})

        # assertion
        is_redeemed = bond_token.isRedeemed()
        assert is_redeemed is False


# TEST_lock/lockedOf
class TestLock:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Lock assets to lock address
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]
        user = users["user1"]
        lock_eoa = users["user2"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 10

        # transfer to account
        bond_token.transferFrom.transact(
            issuer, user, transfer_amount, {"from": issuer}
        )

        # lock
        tx = bond_token.lock.transact(
            lock_eoa, lock_amount, "some_extra_data", {"from": user}
        )

        # assertion
        assert bond_token.balanceOf(user) == transfer_amount - lock_amount
        assert bond_token.lockedOf(lock_eoa, user) == lock_amount

        assert tx.events["Lock"]["accountAddress"] == user
        assert tx.events["Lock"]["lockAddress"] == lock_eoa
        assert tx.events["Lock"]["value"] == lock_amount
        assert tx.events["Lock"]["data"] == "some_extra_data"

    #######################################
    # Error
    #######################################

    # Error_1
    # Insufficient balance
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]
        user = users["user1"]
        lock_eoa = users["user2"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 40

        # transfer to account
        bond_token.transferFrom.transact(
            issuer, user, transfer_amount, {"from": issuer}
        )

        # lock
        with brownie.reverts(revert_msg="120002"):
            bond_token.lock.transact(
                lock_eoa, lock_amount, "some_extra_data", {"from": user}
            )

        # assertion
        assert bond_token.balanceOf(user) == transfer_amount
        assert bond_token.lockedOf(lock_eoa, user) == 0


# TEST_forceLock
class TestForceLock:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Force-Lock assets to lock address
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]
        user = users["user1"]
        lock_eoa = users["user2"]

        # issue token
        deploy_args = init_args()
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 10

        # transfer to account
        bond_token.transferFrom.transact(
            issuer, user, transfer_amount, {"from": issuer}
        )

        # force lock
        tx = bond_token.forceLock.transact(
            lock_eoa, user, lock_amount, "some_extra_data", {"from": issuer}
        )

        # assertion
        assert bond_token.balanceOf(user) == transfer_amount - lock_amount
        assert bond_token.lockedOf(lock_eoa, user) == lock_amount

        assert tx.events["ForceLock"]["accountAddress"] == user
        assert tx.events["ForceLock"]["lockAddress"] == lock_eoa
        assert tx.events["ForceLock"]["value"] == lock_amount
        assert tx.events["ForceLock"]["data"] == "some_extra_data"

    #######################################
    # Error
    #######################################

    # Error_1
    # Insufficient balance
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]
        user = users["user1"]
        lock_eoa = users["user2"]

        # issue token
        deploy_args = init_args()
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 40

        # transfer to account
        bond_token.transferFrom.transact(
            issuer, user, transfer_amount, {"from": issuer}
        )

        # force lock
        with brownie.reverts(revert_msg="121601"):
            bond_token.forceLock.transact(
                lock_eoa, user, lock_amount, "some_extra_data", {"from": issuer}
            )

        # assertion
        assert bond_token.balanceOf(user) == transfer_amount
        assert bond_token.lockedOf(lock_eoa, user) == 0

    # Error_2
    # Tx from not authorized account
    def test_error_2(self, users, IbetStraightBond):
        issuer = users["issuer"]
        user = users["user1"]
        lock_eoa = users["user2"]

        # issue token
        deploy_args = init_args()
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 10

        # transfer to account
        bond_token.transferFrom.transact(
            issuer, user, transfer_amount, {"from": issuer}
        )

        # force lock
        with brownie.reverts(revert_msg="500001"):
            bond_token.forceLock.transact(
                lock_eoa, user, lock_amount, "some_extra_data", {"from": user}
            )

        # assertion
        assert bond_token.balanceOf(user) == transfer_amount
        assert bond_token.lockedOf(lock_eoa, user) == 0


# TEST_unlock
class TestUnlock:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]
        user1 = users["user1"]
        user2 = users["user2"]
        lock_eoa = users["agent"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 20
        unlock_amount = 10

        # transfer to account
        bond_token.transferFrom.transact(
            issuer, user1, transfer_amount, {"from": issuer}
        )

        # lock
        bond_token.lock.transact(lock_eoa, lock_amount, "lock_message", {"from": user1})

        # unlock
        tx = bond_token.unlock.transact(
            user1, user2, unlock_amount, "unlock_message", {"from": lock_eoa}
        )

        # assertion
        assert bond_token.balanceOf(user1) == transfer_amount - lock_amount
        assert bond_token.balanceOf(user2) == unlock_amount
        assert bond_token.lockedOf(lock_eoa, user1) == lock_amount - unlock_amount

        assert tx.events["Unlock"]["accountAddress"] == user1.address
        assert tx.events["Unlock"]["lockAddress"] == lock_eoa.address
        assert tx.events["Unlock"]["recipientAddress"] == user2.address
        assert tx.events["Unlock"]["value"] == unlock_amount
        assert tx.events["Unlock"]["data"] == "unlock_message"

    #######################################
    # Error
    #######################################

    # Error_1
    # Cannot unlock a quantity that exceeds the lock quantity
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]
        user1 = users["user1"]
        user2 = users["user2"]
        lock_eoa = users["agent"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 10
        unlock_amount = 11

        # transfer to account
        bond_token.transferFrom.transact(
            issuer, user1, transfer_amount, {"from": issuer}
        )

        # lock
        bond_token.lock.transact(lock_eoa, lock_amount, "lock_message", {"from": user1})

        # unlock
        with brownie.reverts(revert_msg="120102"):
            bond_token.unlock.transact(
                user1, user2, unlock_amount, "unlock_message", {"from": lock_eoa}
            )

        # assertion
        assert bond_token.balanceOf(user1) == transfer_amount - lock_amount
        assert bond_token.balanceOf(user2) == 0
        assert bond_token.lockedOf(lock_eoa, user1) == lock_amount


# TEST_forceUnlock
class TestForceUnlock:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]
        user1 = users["user1"]
        user2 = users["user2"]
        lock_eoa = users["agent"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 20
        unlock_amount = 10

        # transfer to account
        bond_token.transferFrom.transact(
            issuer, user1, transfer_amount, {"from": issuer}
        )

        # lock
        bond_token.lock.transact(lock_eoa, lock_amount, "lock_message", {"from": user1})

        # forceUnlock
        tx = bond_token.forceUnlock.transact(
            lock_eoa, user1, user2, unlock_amount, "unlock_message", {"from": issuer}
        )

        # assertion
        assert bond_token.balanceOf(user1) == transfer_amount - lock_amount
        assert bond_token.balanceOf(user2) == unlock_amount
        assert bond_token.lockedOf(lock_eoa, user1) == lock_amount - unlock_amount

        assert tx.events["ForceUnlock"]["accountAddress"] == user1.address
        assert tx.events["ForceUnlock"]["lockAddress"] == lock_eoa.address
        assert tx.events["ForceUnlock"]["recipientAddress"] == user2.address
        assert tx.events["ForceUnlock"]["value"] == unlock_amount
        assert tx.events["ForceUnlock"]["data"] == "unlock_message"

    #######################################
    # Error
    #######################################

    # Error_1
    # Cannot unlock a quantity that exceeds the lock quantity
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]
        user1 = users["user1"]
        user2 = users["user2"]
        lock_eoa = users["agent"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 10
        unlock_amount = 11

        # transfer to account
        bond_token.transferFrom.transact(
            issuer, user1, transfer_amount, {"from": issuer}
        )

        # lock
        bond_token.lock.transact(lock_eoa, lock_amount, "lock_message", {"from": user1})

        # unlock
        with brownie.reverts(revert_msg="121201"):
            bond_token.forceUnlock.transact(
                lock_eoa,
                user1,
                user2,
                unlock_amount,
                "unlock_message",
                {"from": issuer},
            )

        # assertion
        assert bond_token.balanceOf(user1) == transfer_amount - lock_amount
        assert bond_token.balanceOf(user2) == 0
        assert bond_token.lockedOf(lock_eoa, user1) == lock_amount

    # Error_2
    # Tx from not authorized account
    def test_error_2(self, users, IbetStraightBond):
        issuer = users["issuer"]
        user1 = users["user1"]
        user2 = users["user2"]
        lock_eoa = users["agent"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 10

        # transfer to account
        bond_token.transferFrom.transact(
            issuer, user1, transfer_amount, {"from": issuer}
        )

        # lock
        bond_token.lock.transact(lock_eoa, lock_amount, "lock_message", {"from": user1})

        # unlock
        with brownie.reverts(revert_msg="500001"):
            bond_token.forceUnlock.transact(
                lock_eoa, user1, user2, lock_amount, "unlock_message", {"from": user2}
            )

        # assertion
        assert bond_token.balanceOf(user1) == transfer_amount - lock_amount
        assert bond_token.balanceOf(user2) == 0
        assert bond_token.lockedOf(lock_eoa, user1) == lock_amount


# TEST_forceChangeLockedAccount
class TestForceChangeLockedAccount:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]
        user1 = users["user1"]
        user2 = users["user2"]
        lock_eoa = users["agent"]

        # issue token
        deploy_args = init_args()
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 20
        change_amount = 10

        # transfer to account
        bond_token.transferFrom.transact(
            issuer, user1, transfer_amount, {"from": issuer}
        )

        # lock
        bond_token.lock.transact(lock_eoa, lock_amount, "lock_message", {"from": user1})

        # forceChangeLockedAccount
        tx = bond_token.forceChangeLockedAccount.transact(
            lock_eoa, user1, user2, change_amount, "change_message", {"from": issuer}
        )

        # assertion
        assert bond_token.balanceOf(user1) == transfer_amount - lock_amount
        assert bond_token.balanceOf(user2) == 0
        assert bond_token.lockedOf(lock_eoa, user1) == lock_amount - change_amount
        assert bond_token.lockedOf(lock_eoa, user2) == change_amount

        assert tx.events["ForceChangeLockedAccount"]["lockAddress"] == lock_eoa.address
        assert (
            tx.events["ForceChangeLockedAccount"]["beforeAccountAddress"]
            == user1.address
        )
        assert (
            tx.events["ForceChangeLockedAccount"]["afterAccountAddress"]
            == user2.address
        )
        assert tx.events["ForceChangeLockedAccount"]["value"] == change_amount
        assert tx.events["ForceChangeLockedAccount"]["data"] == "change_message"

    #######################################
    # Error
    #######################################

    # Error_1
    # - Authorization error
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]
        user1 = users["user1"]
        user2 = users["user2"]
        lock_eoa = users["agent"]

        # issue token
        deploy_args = init_args()
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 20
        change_amount = 10

        # transfer to account
        bond_token.transferFrom.transact(
            issuer, user1, transfer_amount, {"from": issuer}
        )

        # lock
        bond_token.lock.transact(lock_eoa, lock_amount, "lock_message", {"from": user1})

        # forceChangeLockedAccount
        # - Tx from not authorized account
        with brownie.reverts(revert_msg="500001"):
            bond_token.forceChangeLockedAccount.transact(
                lock_eoa, user1, user2, change_amount, "change_message", {"from": user1}
            )

        # assertion
        assert bond_token.balanceOf(user1) == transfer_amount - lock_amount
        assert bond_token.balanceOf(user2) == 0
        assert bond_token.lockedOf(lock_eoa, user1) == lock_amount
        assert bond_token.lockedOf(lock_eoa, user2) == 0

    # Error_2
    # - Insufficient locked balance
    def test_error_2(self, users, IbetStraightBond):
        issuer = users["issuer"]
        user1 = users["user1"]
        user2 = users["user2"]
        lock_eoa = users["agent"]

        # issue token
        deploy_args = init_args()
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        change_amount = 10

        # forceChangeLockedAccount
        with brownie.reverts(revert_msg="121701"):
            bond_token.forceChangeLockedAccount.transact(
                lock_eoa,
                user1,
                user2,
                change_amount,
                "change_message",
                {"from": issuer},
            )

        # assertion
        assert bond_token.balanceOf(user1) == 0
        assert bond_token.balanceOf(user2) == 0
        assert bond_token.lockedOf(lock_eoa, user1) == 0
        assert bond_token.lockedOf(lock_eoa, user2) == 0


# TEST_issueFrom
class TestIssueFrom:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Issue from issuer address
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]
        issue_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 1000
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # issue from issuer address
        bond_token.issueFrom.transact(
            issuer, brownie.ZERO_ADDRESS, issue_amount, {"from": issuer}
        )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2] + issue_amount
        assert bond_token.balanceOf(issuer) == deploy_args[2] + issue_amount

    # Normal_2
    # Issue from EOA
    def test_normal_2(self, users, IbetStraightBond):
        issuer = users["issuer"]
        issue_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 1000
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # issue from EOA
        bond_token.issueFrom.transact(
            brownie.ETH_ADDRESS, brownie.ZERO_ADDRESS, issue_amount, {"from": issuer}
        )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2] + issue_amount
        assert bond_token.balanceOf(issuer) == deploy_args[2]
        assert bond_token.balanceOf(brownie.ETH_ADDRESS) == issue_amount

    # Normal_3
    # Issue from locked address
    def test_normal_3(self, users, IbetStraightBond):
        issuer = users["issuer"]
        lock_address = users["user1"]
        lock_amount = 10
        issue_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 1000
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # lock
        bond_token.lock.transact(
            lock_address, lock_amount, "lock_message", {"from": issuer}
        )

        # issue from lock address
        bond_token.issueFrom.transact(
            issuer, lock_address, issue_amount, {"from": issuer}
        )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2] + issue_amount
        assert bond_token.balanceOf(issuer) == deploy_args[2] - lock_amount
        assert bond_token.lockedOf(lock_address, issuer) == lock_amount + issue_amount

    #######################################
    # Error
    #######################################

    # Error_1_1
    # Over the limit
    # issuer address
    def test_error_1_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # issue from issuer address
        with brownie.reverts(revert_msg=""):
            bond_token.issueFrom.transact(
                issuer, brownie.ZERO_ADDRESS, 1, {"from": issuer}
            )

    # Error_1_2
    # Over the limit
    # locked address
    def test_error_1_2(self, users, IbetStraightBond):
        issuer = users["issuer"]
        lock_address = users["user1"]
        lock_amount = 2**256 - 1
        issue_amount = 1

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # lock
        bond_token.lock.transact(
            lock_address, lock_amount, "lock_message", {"from": issuer}
        )

        # issue from lock address
        with brownie.reverts(revert_msg=""):
            bond_token.issueFrom.transact(
                issuer, lock_address, issue_amount, {"from": issuer}
            )

        # assertion
        assert bond_token.balanceOf(issuer) == deploy_args[2] - lock_amount
        assert bond_token.lockedOf(lock_address, issuer) == lock_amount

    # Error_2
    # Not authorized
    def test_error_2(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # issue from not authorized user
        with brownie.reverts(revert_msg="500001"):
            bond_token.issueFrom.transact(
                issuer, brownie.ZERO_ADDRESS, 1, {"from": users["user1"]}
            )


# TEST_bulkIssueFrom
class TestBulkIssueFrom:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Bulk issue from EOA
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]
        issue_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 1000
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        # bulk issue
        bond_token.bulkIssueFrom.transact(
            [issuer, brownie.ETH_ADDRESS],
            [brownie.ZERO_ADDRESS, brownie.ZERO_ADDRESS],
            [issue_amount, issue_amount],
            {"from": issuer},
        )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2] + issue_amount * 2
        assert bond_token.balanceOf(issuer) == deploy_args[2] + issue_amount
        assert bond_token.balanceOf(brownie.ETH_ADDRESS) == issue_amount

    # Normal_2
    # Issue from locked address
    def test_normal_2(self, users, IbetStraightBond):
        issuer = users["issuer"]
        lock_address = users["user1"]
        lock_amount = 10
        issue_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 1000
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        # lock
        bond_token.lock.transact(
            lock_address, lock_amount, "lock_message", {"from": issuer}
        )

        # bulkIssue from lock address
        bond_token.bulkIssueFrom.transact(
            [issuer, brownie.ETH_ADDRESS],
            [lock_address, lock_address],
            [issue_amount, issue_amount],
            {"from": issuer},
        )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2] + issue_amount * 2

        assert bond_token.balanceOf(issuer) == deploy_args[2] - lock_amount
        assert bond_token.balanceOf(brownie.ETH_ADDRESS) == 0

        assert bond_token.lockedOf(lock_address, issuer) == lock_amount + issue_amount
        assert bond_token.lockedOf(lock_address, brownie.ETH_ADDRESS) == issue_amount

    #######################################
    # Error
    #######################################

    # Error_1_1
    # Over the limit
    # The balance quantity of some EOA exceeds the upper limit of integer.
    def test_error_1_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        # bulk issue
        with brownie.reverts(revert_msg="Integer overflow"):
            bond_token.bulkIssueFrom.transact(
                [brownie.ETH_ADDRESS, issuer],
                [brownie.ZERO_ADDRESS, brownie.ZERO_ADDRESS],
                [1, 1],
                {"from": issuer},
            )

        # assertion
        assert bond_token.balanceOf(issuer) == deploy_args[2]
        assert bond_token.balanceOf(brownie.ETH_ADDRESS) == 0

    # Error_1_2
    # Over the limit
    # The locked quantity of some EOA exceeds the upper limit of integer.
    def test_error_1_2(self, users, IbetStraightBond):
        issuer = users["issuer"]
        lock_address = users["user1"]
        lock_amount = 2**256 - 1
        issue_amount = 1

        # issue token
        deploy_args = init_args()
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        # lock
        bond_token.lock.transact(
            lock_address, lock_amount, "lock_message", {"from": issuer}
        )

        # bulk issue
        with brownie.reverts(revert_msg="Integer overflow"):
            bond_token.bulkIssueFrom.transact(
                [brownie.ETH_ADDRESS, issuer],
                [brownie.ZERO_ADDRESS, lock_address],
                [issue_amount, issue_amount],
                {"from": issuer},
            )

        # assertion
        assert bond_token.balanceOf(issuer) == deploy_args[2] - lock_amount
        assert bond_token.balanceOf(brownie.ETH_ADDRESS) == 0

        assert bond_token.lockedOf(lock_address, issuer) == lock_amount
        assert bond_token.lockedOf(lock_address, brownie.ETH_ADDRESS) == 0

    # Error_2
    # Not authorized
    # -> revert: 500001
    def test_error_2(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        # issue from not authorized user
        with brownie.reverts(revert_msg="500001"):
            bond_token.bulkIssueFrom.transact(
                [issuer], [brownie.ZERO_ADDRESS], [1], {"from": users["user1"]}
            )

    # Error_3
    # Some list lengths are unequal.
    # -> revert: 111301
    def test_error_3(self, users, IbetStraightBond):
        issuer = users["issuer"]
        issue_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 1000
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        # bulk issue
        with brownie.reverts(revert_msg="121301"):
            bond_token.bulkIssueFrom.transact(
                [issuer, brownie.ETH_ADDRESS],
                [brownie.ZERO_ADDRESS],
                [issue_amount],
                {"from": issuer},
            )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2]
        assert bond_token.balanceOf(issuer) == deploy_args[2]
        assert bond_token.balanceOf(brownie.ETH_ADDRESS) == 0


# TEST_setFaceValue
class TestSetFaceValue:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.setFaceValue(10001, {"from": issuer})

        # assertion
        assert bond_token.faceValue() == 10001

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        with brownie.reverts(revert_msg="500001"):
            bond_token.setFaceValue(10001, {"from": users["user1"]})

        assert bond_token.faceValue() == deploy_args[3]


# TEST_redeemFrom
class TestRedeemFrom:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Redeem from issuer address
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]
        redeem_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 1000
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # redeem
        bond_token.redeemFrom.transact(
            issuer, brownie.ZERO_ADDRESS, redeem_amount, {"from": issuer}
        )

        # assertion
        total_supply = bond_token.totalSupply()
        balance = bond_token.balanceOf(issuer)
        assert total_supply == deploy_args[2] - redeem_amount
        assert balance == deploy_args[2] - redeem_amount

    # Normal_2
    # Redeem from EOA
    def test_normal_2(self, users, IbetStraightBond):
        issuer = users["issuer"]
        user = users["user1"]
        transfer_amount = 20
        redeem_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 1000
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # transfer to user
        bond_token.transferFrom.transact(
            issuer, user, transfer_amount, {"from": issuer}
        )

        # redeem
        bond_token.redeemFrom.transact(
            user, brownie.ZERO_ADDRESS, redeem_amount, {"from": issuer}
        )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2] - redeem_amount
        assert bond_token.balanceOf(issuer) == deploy_args[2] - transfer_amount
        assert bond_token.balanceOf(user) == transfer_amount - redeem_amount

    # Normal_3
    # Redeem from locked address
    def test_normal_3(self, users, IbetStraightBond):
        issuer = users["issuer"]
        lock_address = users["user1"]
        lock_amount = 20
        redeem_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 1000
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # lock
        bond_token.lock.transact(
            lock_address, lock_amount, "lock_message", {"from": issuer}
        )

        # redeem from lock address
        bond_token.redeemFrom.transact(
            issuer, lock_address, redeem_amount, {"from": issuer}
        )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2] - redeem_amount
        assert bond_token.balanceOf(issuer) == deploy_args[2] - lock_amount
        assert bond_token.lockedOf(lock_address, issuer) == lock_amount - redeem_amount

    #######################################
    # Error
    #######################################

    # Error_1
    # Exceeds balance
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]
        redeem_amount = 101

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 100
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # redeem
        with brownie.reverts(revert_msg="121102"):
            bond_token.redeemFrom.transact(
                issuer, brownie.ZERO_ADDRESS, redeem_amount, {"from": issuer}
            )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2]
        assert bond_token.balanceOf(issuer) == deploy_args[2]

    # Error_2
    # Exceeds locked quantity
    def test_error_2(self, users, IbetStraightBond):
        issuer = users["issuer"]
        lock_address = users["user1"]
        lock_amount = 20
        redeem_amount = 21

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 100
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # lock
        bond_token.lock.transact(
            lock_address, lock_amount, "lock_message", {"from": issuer}
        )

        # redeem from lock address
        with brownie.reverts(revert_msg="121101"):
            bond_token.redeemFrom.transact(
                issuer, lock_address, redeem_amount, {"from": issuer}
            )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2]
        assert bond_token.balanceOf(issuer) == deploy_args[2] - lock_amount
        assert bond_token.lockedOf(lock_address, issuer) == lock_amount

    # Error_3
    # Not authorized
    def test_error_3(self, users, IbetStraightBond):
        issuer = users["issuer"]
        redeem_amount = 100

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 100
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # redeem
        with brownie.reverts(revert_msg="500001"):
            bond_token.redeemFrom.transact(
                issuer, brownie.ZERO_ADDRESS, redeem_amount, {"from": users["user1"]}
            )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2]
        assert bond_token.balanceOf(issuer) == deploy_args[2]


# TEST_bulkRedeemFrom
class TestBulkRedeemFrom:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Redeem from EOA
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]
        transfer_amount = 20
        redeem_amount = 10

        # issue token
        deploy_args = init_args()
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        # transfer token to other EOA
        bond_token.transferFrom.transact(
            issuer, brownie.ETH_ADDRESS, transfer_amount, {"from": issuer}
        )

        # bulk redeem
        bond_token.bulkRedeemFrom.transact(
            [issuer, brownie.ETH_ADDRESS],
            [brownie.ZERO_ADDRESS, brownie.ZERO_ADDRESS],
            [redeem_amount, redeem_amount],
            {"from": issuer},
        )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2] - redeem_amount * 2
        assert (
            bond_token.balanceOf(issuer)
            == deploy_args[2] - transfer_amount - redeem_amount
        )
        assert (
            bond_token.balanceOf(brownie.ETH_ADDRESS) == transfer_amount - redeem_amount
        )

    # Normal_2
    # Redeem from locked address
    def test_normal_2(self, users, IbetStraightBond):
        issuer = users["issuer"]
        lock_address = users["user1"]
        transfer_amount = 30
        lock_amount = 20
        redeem_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 1000
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        # transfer token to other EOA
        bond_token.transferFrom.transact(
            issuer, brownie.ETH_ADDRESS, transfer_amount, {"from": issuer}
        )

        # lock
        bond_token.lock.transact(
            lock_address, lock_amount, "lock_message", {"from": issuer}
        )
        bond_token.lock.transact(
            lock_address, lock_amount, "lock_message", {"from": brownie.ETH_ADDRESS}
        )

        # bulk redeem from lock address
        bond_token.bulkRedeemFrom.transact(
            [issuer, brownie.ETH_ADDRESS],
            [lock_address, lock_address],
            [redeem_amount, redeem_amount],
            {"from": issuer},
        )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2] - redeem_amount * 2

        assert (
            bond_token.balanceOf(issuer)
            == deploy_args[2] - transfer_amount - lock_amount
        )
        assert (
            bond_token.balanceOf(brownie.ETH_ADDRESS) == transfer_amount - lock_amount
        )

        assert bond_token.lockedOf(lock_address, issuer) == lock_amount - redeem_amount
        assert (
            bond_token.lockedOf(lock_address, brownie.ETH_ADDRESS)
            == lock_amount - redeem_amount
        )

    #######################################
    # Error
    #######################################

    # Error_1
    # Some list lengths are unequal.
    # -> revert: 111401
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]
        transfer_amount = 20
        redeem_amount = 10

        # issue token
        deploy_args = init_args()
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        # transfer token to other EOA
        bond_token.transferFrom.transact(
            issuer, brownie.ETH_ADDRESS, transfer_amount, {"from": issuer}
        )

        # bulk redeem
        with brownie.reverts(revert_msg="121401"):
            bond_token.bulkRedeemFrom.transact(
                [issuer, brownie.ETH_ADDRESS],
                [brownie.ZERO_ADDRESS],
                [redeem_amount],
                {"from": issuer},
            )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2]
        assert bond_token.balanceOf(issuer) == deploy_args[2] - transfer_amount
        assert bond_token.balanceOf(brownie.ETH_ADDRESS) == transfer_amount

    # Error_2_1
    # Exceeds balance
    # -> revert: 111102
    def test_error_2_1(self, users, IbetStraightBond):
        issuer = users["issuer"]
        transfer_amount = 90
        redeem_amount = 11

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 100
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        # transfer token to other EOA
        bond_token.transferFrom.transact(
            issuer, brownie.ETH_ADDRESS, transfer_amount, {"from": issuer}
        )

        # redeem
        with brownie.reverts(revert_msg="121102"):
            bond_token.bulkRedeemFrom.transact(
                [brownie.ETH_ADDRESS, issuer],
                [brownie.ZERO_ADDRESS, brownie.ZERO_ADDRESS],
                [redeem_amount, redeem_amount],
                {"from": issuer},
            )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2]
        assert bond_token.balanceOf(issuer) == deploy_args[2] - transfer_amount
        assert bond_token.balanceOf(brownie.ETH_ADDRESS) == transfer_amount

    # Error_2_2
    # Exceeds locked quantity
    # revert: 111101
    def test_error_2_2(self, users, IbetStraightBond):
        issuer = users["issuer"]
        lock_address = users["user1"]
        transfer_amount = 80
        lock_amount = 20

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 1000
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        # transfer token to other EOA
        bond_token.transferFrom.transact(
            issuer, brownie.ETH_ADDRESS, transfer_amount, {"from": issuer}
        )

        # lock
        bond_token.lock.transact(
            lock_address, lock_amount, "lock_message", {"from": issuer}
        )
        bond_token.lock.transact(
            lock_address, lock_amount, "lock_message", {"from": brownie.ETH_ADDRESS}
        )

        # redeem from lock address
        with brownie.reverts(revert_msg="121101"):
            bond_token.bulkRedeemFrom.transact(
                [brownie.ETH_ADDRESS, issuer],
                [lock_address, lock_address],
                [20, 21],
                {"from": issuer},
            )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2]

        assert (
            bond_token.balanceOf(issuer)
            == deploy_args[2] - transfer_amount - lock_amount
        )
        assert (
            bond_token.balanceOf(brownie.ETH_ADDRESS) == transfer_amount - lock_amount
        )

        assert bond_token.lockedOf(lock_address, issuer) == lock_amount
        assert bond_token.lockedOf(lock_address, brownie.ETH_ADDRESS) == lock_amount

    # Error_3
    # Not authorized
    # -> revert: 500001
    def test_error_3(self, users, IbetStraightBond):
        issuer = users["issuer"]
        redeem_amount = 100

        # issue token
        deploy_args = init_args()
        bond_token = issuer.deploy(IbetStraightBond, *deploy_args)

        # redeem
        with brownie.reverts(revert_msg="500001"):
            bond_token.bulkRedeemFrom.transact(
                [issuer],
                [brownie.ZERO_ADDRESS],
                [redeem_amount],
                {"from": users["user1"]},
            )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2]
        assert bond_token.balanceOf(issuer) == deploy_args[2]


# TEST_setRedemptionValue
class TestSetRedemptionValue:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.setRedemptionValue(10000, {"from": issuer})

        # assertion
        assert bond_token.redemptionValue() == 10000

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        with brownie.reverts(revert_msg="500001"):
            bond_token.setRedemptionValue(10000, {"from": users["user1"]})

        # assertion
        assert bond_token.redemptionValue() == deploy_args[6]


# TEST_setRedemptionDate
class TestSetRedemptionDate:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.setRedemptionDate("20240813", {"from": issuer})

        # assertion
        assert bond_token.redemptionDate() == "20240813"

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        with brownie.reverts(revert_msg="500001"):
            bond_token.setRedemptionDate("20240813", {"from": users["user1"]})

        # assertion
        assert bond_token.redemptionDate() == deploy_args[5]


# TEST_setTransferApprovalRequired
class TestSetTransferApprovalRequired:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Default value
    def test_normal_1(self, users):
        issuer = users["issuer"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=brownie.ZERO_ADDRESS,
        )

        # assertion
        assert bond_token.transferApprovalRequired() == False

    # Normal_2
    def test_normal_2(self, users):
        issuer = users["issuer"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=brownie.ZERO_ADDRESS,
        )

        # update
        tx = bond_token.setTransferApprovalRequired(True, {"from": issuer})

        # assertion
        assert bond_token.transferApprovalRequired() == True
        assert tx.events["ChangeTransferApprovalRequired"]["required"] == True

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, personal_info):
        issuer = users["issuer"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )

        # set required to True
        with brownie.reverts(revert_msg="500001"):
            bond_token.setTransferApprovalRequired(True, {"from": users["user1"]})

        # assertion
        assert bond_token.transferApprovalRequired() == False


# TEST_setPurpose
class TestSetPurpose:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.setPurpose("updated_purpose", {"from": issuer})

        # assertion
        assert bond_token.purpose() == "updated_purpose"

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        with brownie.reverts(revert_msg="500001"):
            bond_token.setPurpose("updated_purpose", {"from": users["user1"]})

        # assertion
        assert bond_token.purpose() == deploy_args[10]


# TEST_setFaceValueCurrency
class TestSetFaceValueCurrency:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # assertion
        assert bond_token.faceValueCurrency() == "JPY"

        # update
        bond_token.setFaceValueCurrency("USD", {"from": issuer})

        # assertion
        assert bond_token.faceValueCurrency() == "USD"

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        with brownie.reverts(revert_msg="500001"):
            bond_token.setFaceValueCurrency("USD", {"from": users["user1"]})

        assert bond_token.faceValueCurrency() == "JPY"


# TEST_setInterestPaymentCurrency
class TestSetInterestPaymentCurrency:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # assertion
        assert bond_token.interestPaymentCurrency() == ""

        # update
        bond_token.setInterestPaymentCurrency("JPY", {"from": issuer})

        # assertion
        assert bond_token.interestPaymentCurrency() == "JPY"

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        with brownie.reverts(revert_msg="500001"):
            bond_token.setInterestPaymentCurrency("USD", {"from": users["user1"]})

        assert bond_token.interestPaymentCurrency() == ""


# TEST_setRedemptionValueCurrency
class TestSetRedemptionValueCurrency:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # assertion
        assert bond_token.redemptionValueCurrency() == "JPY"

        # update
        bond_token.setRedemptionValueCurrency("USD", {"from": issuer})

        # assertion
        assert bond_token.redemptionValueCurrency() == "USD"

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        with brownie.reverts(revert_msg="500001"):
            bond_token.setRedemptionValueCurrency("USD", {"from": users["user1"]})

        assert bond_token.redemptionValueCurrency() == "JPY"


# TEST_setBaseFXRate
class TestSetBaseFXRate:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # assertion
        assert bond_token.baseFXRate() == ""

        # update
        bond_token.setBaseFXRate("123.456", {"from": issuer})

        # assertion
        assert bond_token.baseFXRate() == "123.456"

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        with brownie.reverts(revert_msg="500001"):
            bond_token.setBaseFXRate("123.456", {"from": users["user1"]})

        assert bond_token.baseFXRate() == ""


# TEST_applyForTransfer
class TestApplyForTransfer:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, personal_info):
        issuer = users["issuer"]
        to_address = users["user1"]
        transfer_amount = 100
        transfer_data = "test_data"

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )
        bond_token.setTransferApprovalRequired(True, {"from": issuer})

        # register personal information (to_address)
        personal_info.register(issuer, "encrypted_message", {"from": to_address})

        # apply for transfer
        tx = bond_token.applyForTransfer(
            to_address, transfer_amount, transfer_data, {"from": issuer}
        )

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(to_address) == 0
        assert bond_token.pendingTransfer(issuer) == transfer_amount
        assert bond_token.applicationsForTransfer(0) == (
            issuer,
            to_address,
            transfer_amount,
            True,
        )

        assert tx.events["ApplyForTransfer"]["index"] == 0
        assert tx.events["ApplyForTransfer"]["from"] == issuer
        assert tx.events["ApplyForTransfer"]["to"] == to_address
        assert tx.events["ApplyForTransfer"]["value"] == transfer_amount
        assert tx.events["ApplyForTransfer"]["data"] == transfer_data

    # Normal_2
    # Multiple execution
    def test_normal_2(self, users, personal_info):
        issuer = users["issuer"]
        to_address = users["user1"]
        transfer_amount = 100
        transfer_data = "test_data"

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )
        bond_token.setTransferApprovalRequired(True, {"from": issuer})

        # register personal information (to_address)
        personal_info.register(issuer, "encrypted_message", {"from": to_address})

        # apply for transfer
        for i in range(2):
            bond_token.applyForTransfer(
                to_address, transfer_amount, transfer_data, {"from": issuer}
            )

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount * 2
        assert bond_token.balances(to_address) == 0
        assert bond_token.pendingTransfer(issuer) == transfer_amount * 2
        for i in range(2):
            assert bond_token.applicationsForTransfer(i) == (
                issuer,
                to_address,
                transfer_amount,
                True,
            )

    # Normal_3
    # Transfer to issuer
    # No need to register personal information
    def test_normal_3(self, users, personal_info):
        issuer = users["issuer"]
        to_address = issuer
        transfer_amount = 100
        transfer_data = "test_data"

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )
        bond_token.setTransferApprovalRequired(True, {"from": issuer})

        # apply for transfer
        bond_token.applyForTransfer(
            to_address, transfer_amount, transfer_data, {"from": issuer}
        )

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.pendingTransfer(issuer) == transfer_amount
        assert bond_token.applicationsForTransfer(0) == (
            issuer,
            to_address,
            transfer_amount,
            True,
        )

    # Normal_4
    # requirePersonalInfoRegistered = false
    def test_normal_4(self, users, personal_info):
        issuer = users["issuer"]
        to_address = users["user1"]
        transfer_amount = 100
        transfer_data = "test_data"

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )
        bond_token.setTransferApprovalRequired(True, {"from": issuer})

        # set requirePersonalInfoRegistered to False
        bond_token.setRequirePersonalInfoRegistered.transact(False, {"from": issuer})

        # apply for transfer
        tx = bond_token.applyForTransfer(
            to_address, transfer_amount, transfer_data, {"from": issuer}
        )

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(to_address) == 0
        assert bond_token.pendingTransfer(issuer) == transfer_amount
        assert bond_token.applicationsForTransfer(0) == (
            issuer,
            to_address,
            transfer_amount,
            True,
        )

        assert tx.events["ApplyForTransfer"]["index"] == 0
        assert tx.events["ApplyForTransfer"]["from"] == issuer
        assert tx.events["ApplyForTransfer"]["to"] == to_address
        assert tx.events["ApplyForTransfer"]["value"] == transfer_amount
        assert tx.events["ApplyForTransfer"]["data"] == transfer_data

    #######################################
    # Error
    #######################################

    # Error_1
    # transferApprovalRequired = false
    def test_error_1(self, users):
        issuer = users["issuer"]
        to_address = users["user1"]
        transfer_amount = 100
        transfer_data = "test_data"

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=brownie.ZERO_ADDRESS,
        )

        # apply for transfer
        with brownie.reverts(revert_msg="120701"):
            bond_token.applyForTransfer(
                to_address, transfer_amount, transfer_data, {"from": issuer}
            )

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3]
        assert bond_token.balances(to_address) == 0
        assert bond_token.pendingTransfer(issuer) == 0

    # Error_2
    # transferable = false
    def test_error_2(self, users):
        issuer = users["issuer"]
        to_address = users["user1"]
        transfer_amount = 100
        transfer_data = "test_data"

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=brownie.ZERO_ADDRESS,
        )
        bond_token.setTransferApprovalRequired(True, {"from": issuer})
        bond_token.setTransferable(False, {"from": issuer})

        # apply for transfer
        with brownie.reverts(revert_msg="120701"):
            bond_token.applyForTransfer(
                to_address, transfer_amount, transfer_data, {"from": issuer}
            )

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3]
        assert bond_token.balances(to_address) == 0
        assert bond_token.pendingTransfer(issuer) == 0

    # Error_3
    # Insufficient balance
    def test_error_3(self, users):
        issuer = users["issuer"]
        to_address = users["user1"]
        transfer_data = "test_data"

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=brownie.ZERO_ADDRESS,
        )
        bond_token.setTransferApprovalRequired(True, {"from": issuer})

        # apply for transfer
        with brownie.reverts(revert_msg="120701"):
            bond_token.applyForTransfer(
                to_address, deploy_args[3] + 1, transfer_data, {"from": issuer}
            )

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3]
        assert bond_token.balances(to_address) == 0
        assert bond_token.pendingTransfer(issuer) == 0

    # Error_4
    # Personal information is not registered
    def test_error_4(self, users, personal_info):
        issuer = users["issuer"]
        to_address = users["user1"]
        transfer_amount = 100
        transfer_data = "test_data"

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )
        bond_token.setTransferApprovalRequired(True, {"from": issuer})

        # apply for transfer
        with brownie.reverts(revert_msg="120702"):
            bond_token.applyForTransfer(
                to_address, transfer_amount, transfer_data, {"from": issuer}
            )

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3]
        assert bond_token.balances(to_address) == 0
        assert bond_token.pendingTransfer(issuer) == 0


# TEST_cancelTransfer
class TestCancelTransfer:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Cancel by applicant
    def test_normal_1(self, users, personal_info):
        issuer = users["issuer"]
        user1 = users["user1"]
        user2 = users["user2"]
        transfer_amount = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )
        bond_token.transferFrom(issuer, user1, transfer_amount, {"from": issuer})
        bond_token.setTransferApprovalRequired(True, {"from": issuer})

        # register personal information (to_address)
        personal_info.register(issuer, "encrypted_message", {"from": user2})

        # apply for transfer
        bond_token.applyForTransfer(
            user2,
            transfer_amount,
            "test_data",
            {"from": user1},  # from user1 to user2
        )

        # cancel transfer (from applicant)
        tx = bond_token.cancelTransfer(0, "test_data", {"from": user1})

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(user1) == transfer_amount
        assert bond_token.pendingTransfer(user1) == 0
        assert bond_token.applicationsForTransfer(0) == (
            user1,
            user2,
            transfer_amount,
            False,
        )

        assert tx.events["CancelTransfer"]["index"] == 0
        assert tx.events["CancelTransfer"]["from"] == user1
        assert tx.events["CancelTransfer"]["to"] == user2
        assert tx.events["CancelTransfer"]["data"] == "test_data"

    # Normal_2
    # Cancel by issuer
    def test_normal_2(self, users, personal_info):
        issuer = users["issuer"]
        user1 = users["user1"]
        user2 = users["user2"]
        transfer_amount = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )
        bond_token.transferFrom(issuer, user1, transfer_amount, {"from": issuer})
        bond_token.setTransferApprovalRequired(True, {"from": issuer})

        # register personal information (to_address)
        personal_info.register(issuer, "encrypted_message", {"from": user2})

        # apply for transfer
        bond_token.applyForTransfer(
            user2,
            transfer_amount,
            "test_data",
            {"from": user1},  # from user1 to user2
        )

        # cancel transfer (from issuer)
        tx = bond_token.cancelTransfer(0, "test_data", {"from": issuer})

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(user1) == transfer_amount
        assert bond_token.pendingTransfer(user1) == 0
        assert bond_token.applicationsForTransfer(0) == (
            user1,
            user2,
            transfer_amount,
            False,
        )

        assert tx.events["CancelTransfer"]["index"] == 0
        assert tx.events["CancelTransfer"]["from"] == user1
        assert tx.events["CancelTransfer"]["to"] == user2
        assert tx.events["CancelTransfer"]["data"] == "test_data"

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, personal_info):
        issuer = users["issuer"]
        user1 = users["user1"]
        user2 = users["user2"]
        transfer_amount = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )
        bond_token.transferFrom(issuer, user1, transfer_amount, {"from": issuer})
        bond_token.setTransferApprovalRequired(True, {"from": issuer})

        # register personal information (to_address)
        personal_info.register(issuer, "encrypted_message", {"from": user2})

        # apply for transfer
        bond_token.applyForTransfer(
            user2,
            transfer_amount,
            "test_data",
            {"from": user1},  # from user1 to user2
        )

        # cancel transfer (from issuer)
        with brownie.reverts(revert_msg="120801"):
            bond_token.cancelTransfer(0, "test_data", {"from": user2})

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(user1) == 0
        assert bond_token.pendingTransfer(user1) == transfer_amount
        assert bond_token.applicationsForTransfer(0) == (
            user1,
            user2,
            transfer_amount,
            True,
        )

    # Error_2
    # Applications that have already been cancelled cannot be cancelled.
    def test_error_2(self, users, personal_info):
        issuer = users["issuer"]
        user1 = users["user1"]
        user2 = users["user2"]
        transfer_amount = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )
        bond_token.transferFrom(issuer, user1, transfer_amount, {"from": issuer})
        bond_token.setTransferApprovalRequired(True, {"from": issuer})

        # register personal information (to_address)
        personal_info.register(issuer, "encrypted_message", {"from": user2})

        # apply for transfer
        bond_token.applyForTransfer(
            user2,
            transfer_amount,
            "test_data",
            {"from": user1},  # from user1 to user2
        )

        # cancel transfer (1)
        bond_token.cancelTransfer(0, "test_data", {"from": user1})

        # cancel transfer (2)
        with brownie.reverts(revert_msg="120802"):
            bond_token.cancelTransfer(0, "test_data", {"from": user1})

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(user1) == transfer_amount
        assert bond_token.pendingTransfer(user1) == 0
        assert bond_token.applicationsForTransfer(0) == (
            user1,
            user2,
            transfer_amount,
            False,
        )


# TEST_approveTransfer
class TestApproveTransfer:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, personal_info):
        issuer = users["issuer"]
        user1 = users["user1"]
        transfer_amount = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )
        bond_token.setTransferApprovalRequired(True, {"from": issuer})

        # register personal information (to_address)
        personal_info.register(issuer, "encrypted_message", {"from": user1})

        # apply for transfer
        bond_token.applyForTransfer(
            user1,
            transfer_amount,
            "test_data",
            {"from": issuer},  # from issuer to user1
        )

        # approve transfer
        tx = bond_token.approveTransfer(0, "test_data", {"from": issuer})

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(user1) == transfer_amount
        assert bond_token.pendingTransfer(issuer) == 0
        assert bond_token.applicationsForTransfer(0) == (
            issuer,
            user1,
            transfer_amount,
            False,
        )

        assert tx.events["ApproveTransfer"]["index"] == 0
        assert tx.events["ApproveTransfer"]["from"] == issuer
        assert tx.events["ApproveTransfer"]["to"] == user1
        assert tx.events["ApproveTransfer"]["data"] == "test_data"

        assert tx.events["Transfer"]["from"] == issuer
        assert tx.events["Transfer"]["to"] == user1
        assert tx.events["Transfer"]["value"] == transfer_amount

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, personal_info):
        issuer = users["issuer"]
        user1 = users["user1"]
        transfer_amount = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )
        bond_token.setTransferApprovalRequired(True, {"from": issuer})

        # register personal information (to_address)
        personal_info.register(issuer, "encrypted_message", {"from": user1})

        # apply for transfer
        bond_token.applyForTransfer(
            user1,
            transfer_amount,
            "test_data",
            {"from": issuer},  # from issuer to user1
        )

        # approve transfer
        with brownie.reverts(revert_msg="500001"):
            bond_token.approveTransfer(0, "test_data", {"from": user1})

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(user1) == 0
        assert bond_token.pendingTransfer(issuer) == transfer_amount
        assert bond_token.applicationsForTransfer(0) == (
            issuer,
            user1,
            transfer_amount,
            True,
        )

    # Error_2
    # transferable = false
    def test_error_2(self, users, personal_info):
        issuer = users["issuer"]
        user1 = users["user1"]
        transfer_amount = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )
        bond_token.setTransferApprovalRequired(True, {"from": issuer})

        # register personal information (to_address)
        personal_info.register(issuer, "encrypted_message", {"from": user1})

        # apply for transfer
        bond_token.applyForTransfer(
            user1,
            transfer_amount,
            "test_data",
            {"from": issuer},  # from issuer to user1
        )

        # approve transfer
        bond_token.setTransferable(False, {"from": issuer})
        with brownie.reverts(revert_msg="120901"):
            bond_token.approveTransfer(0, "test_data", {"from": issuer})

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(user1) == 0
        assert bond_token.pendingTransfer(issuer) == transfer_amount
        assert bond_token.applicationsForTransfer(0) == (
            issuer,
            user1,
            transfer_amount,
            True,
        )

    # Error_3
    # Applications that have already been approved cannot be approved.
    def test_error_3(self, users, personal_info):
        issuer = users["issuer"]
        user1 = users["user1"]
        transfer_amount = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address,
        )
        bond_token.setTransferApprovalRequired(True, {"from": issuer})

        # register personal information (to_address)
        personal_info.register(issuer, "encrypted_message", {"from": user1})

        # apply for transfer
        bond_token.applyForTransfer(
            user1,
            transfer_amount,
            "test_data",
            {"from": issuer},  # from issuer to user1
        )

        # approve transfer (1)
        bond_token.approveTransfer(0, "test_data", {"from": issuer})

        # approve transfer (2)
        with brownie.reverts(revert_msg="120902"):
            bond_token.approveTransfer(0, "test_data", {"from": issuer})

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(user1) == transfer_amount
        assert bond_token.pendingTransfer(issuer) == 0
        assert bond_token.applicationsForTransfer(0) == (
            issuer,
            user1,
            transfer_amount,
            False,
        )
