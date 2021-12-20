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
import brownie_utils


def init_args():
    name = 'test_bond'
    symbol = 'BND'
    total_supply = 2 ** 256 - 1
    face_value = 2 ** 256 - 1
    redemption_date = '20191231'
    redemption_value = 2 ** 256 - 1
    return_date = '20191231'
    return_amount = 'some_return'
    purpose = 'some_purpose'

    deploy_args = [
        name,
        symbol,
        total_supply,
        face_value,
        redemption_date,
        redemption_value,
        return_date,
        return_amount,
        purpose
    ]
    return deploy_args


def issue_transferable_bond_token(issuer, exchange_address, personal_info_address):
    from brownie import IbetStraightBond

    name = 'test_bond'
    symbol = 'BND'
    total_supply = 10000
    face_value = 10000
    redemption_date = '20191231'
    redemption_value = 100
    return_date = '20191231'
    return_amount = 'some_return'
    purpose = 'some_purpose'

    deploy_args = [
        name,
        symbol,
        total_supply,
        face_value,
        redemption_date,
        redemption_value,
        return_date,
        return_amount,
        purpose
    ]

    bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)
    bond_token.setTradableExchange.transact(exchange_address, {'from': issuer})
    bond_token.setPersonalInfoAddress.transact(personal_info_address, {'from': issuer})
    bond_token.setTransferable.transact(True, {'from': issuer})
    return bond_token, deploy_args


# TEST_deploy
class TestDeploy:

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users['issuer']
        deploy_args = init_args()
        bond_contract = brownie_utils.force_deploy(
            issuer,
            IbetStraightBond,
            *deploy_args
        )

        # assertion
        owner_address = bond_contract.owner()
        name = bond_contract.name()
        symbol = bond_contract.symbol()
        total_supply = bond_contract.totalSupply()
        face_value = bond_contract.faceValue()
        redemption_date = bond_contract.redemptionDate()
        redemption_value = bond_contract.redemptionValue()
        return_date = bond_contract.returnDate()
        return_amount = bond_contract.returnAmount()
        purpose = bond_contract.purpose()
        transferable = bond_contract.transferable()
        balance = bond_contract.balanceOf(issuer)
        is_redeemed = bond_contract.isRedeemed()
        status = bond_contract.status()

        assert owner_address == issuer
        assert name == deploy_args[0]
        assert symbol == deploy_args[1]
        assert total_supply == deploy_args[2]
        assert face_value == deploy_args[3]
        assert redemption_date == deploy_args[4]
        assert redemption_value == deploy_args[5]
        assert return_date == deploy_args[6]
        assert return_amount == deploy_args[7]
        assert purpose == deploy_args[8]
        assert transferable == False
        assert balance == total_supply
        assert is_redeemed == False
        assert status == True

        # backward compatible calls
        assert bond_contract.initialOfferingStatus() == False
        assert bond_contract.getImageURL(0) == ""


# TEST_transfer
class TestTransfer:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Transfer to EOA
    def test_normal_1(self, users, personal_info):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["trader"]
        transfer_amount = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # register personal info of to_address
        personal_info.register.transact(
            from_address.address,
            "encrypted_message",
            {'from': to_address}
        )

        # transfer
        tx = bond_token.transfer.transact(
            to_address.address,
            transfer_amount,
            {"from": issuer}
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
            personal_info_address=personal_info.address
        )

        # transfer
        to_address = exchange.address
        tx = bond_token.transfer.transact(
            to_address,
            transfer_amount,
            {"from": from_address}
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
            personal_info_address=personal_info.address
        )

        # register personal info of to_address
        personal_info.register.transact(
            from_address.address,
            "encrypted_message",
            {'from': to_address}
        )

        # transfer
        transfer_amount = deploy_args[3] + 1
        with brownie.reverts(revert_msg="Sufficient balance is required."):
            bond_token.transfer.transact(
                to_address.address,
                transfer_amount,
                {"from": issuer}
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
            personal_info_address=brownie.ZERO_ADDRESS
        )

        with pytest.raises(AttributeError):
            bond_token.isContract(to_address)

        with pytest.raises(AttributeError):
            bond_token.transferToAddress.transact(
                to_address,
                transfer_amount,
                "test_data",
                {"from": from_address}
            )

        with pytest.raises(AttributeError):
            bond_token.transferToContract.transact(
                to_address,
                transfer_amount,
                "test_data",
                {"from": from_address}
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
        bond_token.setTransferable(
            False,
            {"from": issuer}
        )

        # transfer
        with brownie.reverts(revert_msg="Must be transferable."):
            bond_token.transfer.transact(
                to_address,
                transfer_amount,
                {"from": issuer}
            )

        # assertion
        from_balance = bond_token.balanceOf(issuer)
        to_balance = bond_token.balanceOf(to_address)
        assert from_balance == deploy_args[3]
        assert to_balance == 0

    # Error_4
    # Transfer to non-tradable exchange
    def test_error_4(self, users, exchange):
        issuer = users['issuer']
        transfer_amount = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=brownie.ZERO_ADDRESS
        )

        # transfer
        with brownie.reverts(revert_msg="Transfers to contract addresses are only possible to tradableExchange."):
            bond_token.transfer.transact(
                exchange,
                transfer_amount,
                {"from": issuer}
            )

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
            personal_info_address=personal_info.address
        )

        # transfer
        with brownie.reverts(revert_msg="The transfer is only possible if personal information is registered."):
            bond_token.transfer.transact(
                to_address.address,
                transfer_amount,
                {"from": issuer}
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
            personal_info_address=personal_info.address
        )

        # register personal info (to_address)
        personal_info.register.transact(
            from_address.address,
            "encrypted_message",
            {"from": to_address}
        )

        # bulk transfer
        to_address_list = [to_address]
        amount_list = [1]
        bond_token.bulkTransfer.transact(
            to_address_list,
            amount_list,
            {"from": from_address}
        )

        # assertion
        from_balance = bond_token.balanceOf(from_address)
        to_balance = bond_token.balanceOf(to_address)
        assert from_balance == deploy_args[3] - 1
        assert to_balance == 1

    # Normal_2
    # Bulk transfer to account address (multiple data)
    def test_normal_2(self, users, personal_info):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["trader"]

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # register personal info (to_address)
        personal_info.register.transact(
            from_address.address,
            "encrypted_message",
            {"from": to_address}
        )

        # bulk transfer
        to_address_list = []
        amount_list = []
        for i in range(100):
            to_address_list.append(to_address)
            amount_list.append(1)

        bond_token.bulkTransfer.transact(
            to_address_list,
            amount_list,
            {"from": from_address}
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
            personal_info_address=personal_info.address
        )

        # bulk transfer
        to_address_list = [exchange.address]
        amount_list = [1]
        bond_token.bulkTransfer.transact(
            to_address_list,
            amount_list,
            {"from": from_address}
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
        issuer = users['issuer']
        from_address = issuer
        to_address = users['trader']

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # register personal info (to_address)
        personal_info.register.transact(
            from_address,
            "encrypted_message",
            {"from": to_address}
        )

        # bulk transfer
        with brownie.reverts():
            bond_token.bulkTransfer.transact(
                [to_address, to_address],
                [deploy_args[3], 1],
                {'from': issuer}
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
            personal_info_address=personal_info.address
        )
        bond_token.setTransferable.transact(
            False,
            {"from": issuer}
        )

        # register personal info (to_address)
        personal_info.register.transact(
            from_address,
            "encrypted_message",
            {"from": to_address}
        )

        # bulk transfer
        with brownie.reverts():
            bond_token.bulkTransfer.transact(
                [to_address],
                [1],
                {"from": issuer}
            )

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
            personal_info_address=personal_info.address
        )

        # bulk transfer
        with brownie.reverts():
            bond_token.bulkTransfer.transact(
                [to_address],
                [1],
                {'from': issuer}
            )

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
        issuer = users['issuer']
        from_address = issuer
        to_address = users['user1']
        value = 100

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # forced transfer
        bond_token.transferFrom.transact(
            from_address,
            to_address,
            value,
            {'from': issuer}
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
        issuer = users['issuer']
        from_address = issuer
        to_address = users['user1']

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # forced transfer
        with brownie.reverts():
            bond_token.transferFrom.transact(
                from_address,
                to_address,
                deploy_args[3] + 1,
                {'from': issuer}
            )

        # assertion
        assert bond_token.balanceOf(issuer) == deploy_args[3]
        assert bond_token.balanceOf(to_address) == 0

    # Error_2
    # Not authorized
    def test_error_2(self, users, personal_info):
        issuer = users['issuer']
        from_address = issuer
        to_address = users['user1']

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # forced transfer
        with brownie.reverts():
            bond_token.transferFrom.transact(
                from_address,
                to_address,
                deploy_args[3] + 1,
                {'from': to_address}
            )

        # assertion
        assert bond_token.balanceOf(issuer) == deploy_args[3]
        assert bond_token.balanceOf(to_address) == 0


# TEST_balanceOf
class TestBalanceOf:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users['issuer']

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
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # change exchange contract
        bond_token.setTradableExchange.transact(
            brownie.ETH_ADDRESS,
            {'from': issuer}
        )

        # assertion
        assert bond_token.tradableExchange() == brownie.ETH_ADDRESS

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # change exchange contract
        with brownie.reverts():
            bond_token.setTradableExchange.transact(
                brownie.ETH_ADDRESS,
                {'from': users['user1']}
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
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update contract
        bond_token.setPersonalInfoAddress.transact(
            brownie.ETH_ADDRESS,
            {'from': issuer}
        )

        # assertion
        assert bond_token.personalInfoAddress() == brownie.ETH_ADDRESS

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update contract
        with brownie.reverts():
            bond_token.setPersonalInfoAddress.transact(
                brownie.ETH_ADDRESS,
                {'from': users['user1']}
            )

        # assertion
        assert bond_token.personalInfoAddress() == brownie.ZERO_ADDRESS


# TEST_setContactInformation
class TestSetContactInformation:

    #######################################
    # Normal
    #######################################

    # 正常系1: 発行（デプロイ） -> 修正
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.setContactInformation.transact(
            'updated contact information',
            {'from': issuer}
        )

        # assertion
        contact_information = bond_token.contactInformation()
        assert contact_information == 'updated contact information'

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        with brownie.reverts():
            bond_token.setContactInformation.transact(
                'updated contact information',
                {'from': users['user1']}
            )

        # assertion
        contact_information = bond_token.contactInformation()
        assert contact_information == ''


# TEST_setPrivacyPolicy
class TestSetPrivacyPolicy:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.setPrivacyPolicy.transact(
            'updated privacy policy',
            {'from': issuer}
        )

        # assertion
        privacy_policy = bond_token.privacyPolicy()
        assert privacy_policy == 'updated privacy policy'

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        with brownie.reverts():
            bond_token.setPrivacyPolicy.transact(
                'updated privacy policy',
                {'from': users['user1']}
            )

        # assertion
        privacy_policy = bond_token.privacyPolicy()
        assert privacy_policy == ''


# TEST_setMemo
class TestSetMemo:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # set memo
        bond_token.setMemo.transact(
            'updated memo',
            {'from': issuer}
        )

        # assertion
        memo = bond_token.memo()
        assert memo == 'updated memo'

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # set memo
        with brownie.reverts():
            bond_token.setMemo.transact(
                'updated memo',
                {'from': users['user1']}
            )

        memo = bond_token.memo()
        assert memo == ''


# TEST_setInterestRate
class TestSetInterestRate:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_setInterestRate_normal_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.setInterestRate.transact(
            123,
            {'from': issuer}
        )

        # assertion
        interest_rate = bond_token.interestRate()
        assert interest_rate == 123

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_setInterestRate_error_2(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        with brownie.reverts():
            bond_token.setInterestRate.transact(
                123,
                {'from': users['user1']}
            )

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
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.setInterestPaymentDate.transact(
            '{"interestPaymentDate1":"0331","interestPaymentDate2":"0930"}',
            {'from': issuer}
        )

        # assertion
        interest_payment_date = bond_token.interestPaymentDate()
        assert interest_payment_date == '{"interestPaymentDate1":"0331","interestPaymentDate2":"0930"}'

    #######################################
    # Error
    #######################################

    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # Owner以外のアドレスから更新 -> Failure
        with brownie.reverts():
            bond_token.setInterestPaymentDate.transact(
                '{"interestPaymentDate1":"0331","interestPaymentDate2":"0930"}',
                {'from': users['user1']}
            )

        # assertion
        interest_payment_date = bond_token.interestPaymentDate()
        assert interest_payment_date == ''


# TEST_setTransferable
class TestSetTransferable:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.setTransferable.transact(True, {'from': issuer})

        # assertion
        assert bond_token.transferable() is True

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        with brownie.reverts():
            bond_token.setTransferable.transact(True, {'from': users['user1']})

        # assertion
        assert bond_token.transferable() is False


# TEST_setStatus
class TestSetStatus:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.setStatus(False, {'from': issuer})

        # assertion
        assert bond_token.status() is False

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # change exchange contract
        with brownie.reverts():
            bond_token.setStatus(False, {'from': users['user1']})


# TEST_changeOfferingStatus
class TestChangeOfferingStatus:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.changeOfferingStatus(True, {'from': issuer})

        # assertion
        assert bond_token.status() is True

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # change exchange contract
        with brownie.reverts():
            bond_token.changeOfferingStatus(True, {'from': users['user1']})


# TEST_applyForOffering
class TestApplyForOffering:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Default value
    def test_normal_1(self, users, personal_info):
        issuer = users['issuer']

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # assertion
        application = bond_token.applicationsForOffering(brownie.ETH_ADDRESS)
        assert application[0] == 0
        assert application[1] == 0
        assert application[2] == ''

    # Normal_2
    def test_normal_2(self, users, personal_info):
        issuer = users['issuer']
        applicant = users['user1']

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # update offering status
        bond_token.changeOfferingStatus.transact(True, {'from': issuer})

        # register personal info of applicant
        personal_info.register.transact(
            issuer,
            "encrypted_message",
            {'from': applicant}
        )

        # apply for offering
        bond_token.applyForOffering.transact(
            10,
            'abcdefgh',
            {'from': applicant}
        )

        # assertion
        application = bond_token.applicationsForOffering(applicant)
        assert application[0] == 10
        assert application[1] == 0
        assert application[2] == 'abcdefgh'

    # Normal_3
    # Multiple applications
    def test_normal_3(self, users, personal_info):
        issuer = users['issuer']
        applicant = users['user1']

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # update offering status
        bond_token.changeOfferingStatus.transact(True, {'from': issuer})

        # register personal info of applicant
        personal_info.register.transact(
            issuer,
            "encrypted_message",
            {'from': applicant}
        )

        # apply for offering (1)
        bond_token.applyForOffering.transact(
            10,
            'abcdefgh',
            {'from': applicant}
        )

        # apply for offering (2)
        bond_token.applyForOffering.transact(
            20,
            'vwxyz',
            {'from': applicant}
        )

        # assertion
        application = bond_token.applicationsForOffering(applicant)
        assert application[0] == 20
        assert application[1] == 0
        assert application[2] == 'vwxyz'

    #######################################
    # Error
    #######################################

    # Error_1
    # The offering status must be true.
    def test_error_1(self, users, personal_info):
        issuer = users['issuer']
        applicant = users['user1']

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # apply for offering
        with brownie.reverts():
            bond_token.applyForOffering.transact(
                10,
                'abcdefgh',
                {'from': applicant}
            )

        # assertion
        application = bond_token.applicationsForOffering(applicant)
        assert application[0] == 0
        assert application[1] == 0
        assert application[2] == ''

    # Error_2
    # Applicant need to register personal information.
    def test_error_2(self, users, personal_info):
        issuer = users['issuer']
        applicant = users['user1']

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # update offering status
        bond_token.changeOfferingStatus.transact(True, {'from': issuer})

        # apply for offering
        with brownie.reverts():
            bond_token.applyForOffering.transact(
                10,
                'abcdefgh',
                {'from': applicant}
            )

        # assertion
        application = bond_token.applicationsForOffering(applicant)
        assert application[0] == 0
        assert application[1] == 0
        assert application[2] == ''


# TEST_allot
class TestAllot:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, personal_info):
        issuer = users['issuer']
        applicant = users['user1']

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # update offering status
        bond_token.changeOfferingStatus.transact(True, {'from': issuer})

        # register personal info of applicant
        personal_info.register.transact(
            issuer,
            "encrypted_message",
            {'from': applicant}
        )

        # apply for offering
        bond_token.applyForOffering.transact(
            10,
            'abcdefgh',
            {'from': applicant}
        )

        # allot
        bond_token.allot.transact(
            applicant,
            5,
            {'from': issuer}
        )

        # assertion
        application = bond_token.applicationsForOffering(applicant)
        assert application[0] == 10
        assert application[1] == 5
        assert application[2] == 'abcdefgh'

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, personal_info):
        issuer = users['issuer']
        applicant = users['user1']

        # issue token
        bond_token, deploy_args = issue_transferable_bond_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # update offering status
        bond_token.changeOfferingStatus.transact(True, {'from': issuer})

        # allot
        with brownie.reverts():
            bond_token.allot.transact(applicant, 5, {'from': applicant})

        # assertion
        application = bond_token.applicationsForOffering(applicant)
        assert application[0] == 0
        assert application[1] == 0
        assert application[2] == ''


# TEST_changeToRedeemed
class TestChangeToRedeemed:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_redeem_normal_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # redeem
        bond_token.changeToRedeemed.transact({'from': issuer})

        # assertion
        is_redeemed = bond_token.isRedeemed()
        assert is_redeemed is True

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_redeem_error_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # redeem
        with brownie.reverts():
            bond_token.changeToRedeemed.transact({'from': users['user1']})

        # assertion
        is_redeemed = bond_token.isRedeemed()
        assert is_redeemed is False


# TEST_authorizeLockAddress
class TestAuthorizeLockAddress:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # authorize
        bond_token.authorizeLockAddress.transact(
            brownie.ETH_ADDRESS,
            True,
            {'from': issuer}
        )

        # assertion
        assert bond_token.authorizedLockAddress(brownie.ETH_ADDRESS) is True
        assert bond_token.authorizedLockAddress(brownie.ZERO_ADDRESS) is False

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # authorize
        with brownie.reverts():
            bond_token.authorizeLockAddress.transact(
                brownie.ETH_ADDRESS,
                True,
                {'from': users['user1']}
            )

        # assertion
        assert bond_token.authorizedLockAddress(brownie.ETH_ADDRESS) is False


# TEST_lock/lockedOf
class TestLock:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Lock assets to authorized addresses
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users['issuer']
        user = users['user1']
        target = users['user2']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 10

        # transfer to account
        bond_token.transferFrom.transact(issuer, user, transfer_amount, {'from': issuer})

        # authorize target address
        bond_token.authorizeLockAddress.transact(target, True, {'from': issuer})

        # lock
        tx = bond_token.lock.transact(target, lock_amount, {'from': user})

        # assertion
        assert bond_token.balanceOf(user) == transfer_amount - lock_amount
        assert bond_token.lockedOf(target, user) == lock_amount

        assert tx.events["Lock"]["accountAddress"] == user
        assert tx.events["Lock"]["lockAddress"] == target
        assert tx.events["Lock"]["value"] == lock_amount

    # Normal_2
    # Lock assets to issuer addresses
    def test_normal_2(self, users, IbetStraightBond):
        issuer = users['issuer']
        user = users['user1']

        transfer_amount = 30
        lock_amount = 10

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # transfer to account
        bond_token.transferFrom.transact(issuer, user, transfer_amount, {'from': issuer})

        # lock
        bond_token.lock.transact(issuer, lock_amount, {'from': user})

        # assertion
        assert bond_token.balanceOf(user) == transfer_amount - lock_amount
        assert bond_token.lockedOf(issuer, user) == lock_amount

    #######################################
    # Error
    #######################################

    # Error_1
    # Insufficient balance
    def test_error_1(self, users, IbetStraightBond):
        issuer = users['issuer']
        user = users['user1']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 40

        # transfer to account
        bond_token.transferFrom.transact(issuer, user, transfer_amount, {'from': issuer})

        # lock
        with brownie.reverts():
            bond_token.lock.transact(issuer, lock_amount, {'from': user})

        # assertion
        assert bond_token.balanceOf(user) == transfer_amount
        assert bond_token.lockedOf(issuer, user) == 0

    # Error_2
    # Lock assets to not authorized address
    def test_error_2(self, users, IbetStraightBond):
        issuer = users['issuer']
        user = users['user1']
        not_authorized_address = users['user2']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 10

        # transfer to account
        bond_token.transferFrom.transact(issuer, user, transfer_amount, {'from': issuer})

        # lock
        with brownie.reverts():
            bond_token.lock.transact(not_authorized_address, lock_amount, {'from': user})

        # assertion
        assert bond_token.balanceOf(user) == transfer_amount
        assert bond_token.lockedOf(issuer, user) == 0


# TEST_unlock
class TestUnlock:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # authorized addresses
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users['issuer']
        user1 = users['user1']
        user2 = users['user2']
        target = users['agent']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 20
        unlock_amount = 10

        # transfer to account
        bond_token.transferFrom.transact(issuer, user1, transfer_amount, {'from': issuer})

        # authorize target address
        bond_token.authorizeLockAddress.transact(target, True, {'from': issuer})

        # lock
        bond_token.lock.transact(target, lock_amount, {'from': user1})

        # unlock
        tx = bond_token.unlock.transact(user1, user2, unlock_amount, {'from': target})

        # assertion
        assert bond_token.balanceOf(user1) == transfer_amount - lock_amount
        assert bond_token.balanceOf(user2) == unlock_amount
        assert bond_token.lockedOf(target, user1) == lock_amount - unlock_amount

        assert tx.events["Unlock"]["accountAddress"] == user1.address
        assert tx.events["Unlock"]["lockAddress"] == target.address
        assert tx.events["Unlock"]["recipientAddress"] == user2.address
        assert tx.events["Unlock"]["value"] == unlock_amount

    # Normal_2
    # issuer
    def test_normal_2(self, users, IbetStraightBond):
        issuer = users['issuer']
        user1 = users['user1']
        user2 = users['user2']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 20
        unlock_amount = 10

        # transfer to account
        bond_token.transferFrom.transact(issuer, user1, transfer_amount, {'from': issuer})

        # lock
        bond_token.lock.transact(issuer, lock_amount, {'from': user1})

        # unlock
        tx = bond_token.unlock.transact(user1, user2, unlock_amount, {'from': issuer})

        # assertion
        assert bond_token.balanceOf(user1) == transfer_amount - lock_amount
        assert bond_token.balanceOf(user2) == unlock_amount
        assert bond_token.lockedOf(issuer, user1) == lock_amount - unlock_amount

        assert tx.events["Unlock"]["accountAddress"] == user1.address
        assert tx.events["Unlock"]["lockAddress"] == issuer.address
        assert tx.events["Unlock"]["recipientAddress"] == user2.address
        assert tx.events["Unlock"]["value"] == unlock_amount

    #######################################
    # Error
    #######################################

    # Error_1
    # Cannot unlock a quantity that exceeds the lock quantity
    def test_error_1(self, users, IbetStraightBond):
        issuer = users['issuer']
        user1 = users['user1']
        user2 = users['user2']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 10
        unlock_amount = 11

        # transfer to account
        bond_token.transferFrom.transact(issuer, user1, transfer_amount, {'from': issuer})

        # lock
        bond_token.lock.transact(issuer, lock_amount, {'from': user1})

        # unlock
        with brownie.reverts():
            bond_token.unlock.transact(user1, user2, unlock_amount, {'from': issuer})

        # assertion
        assert bond_token.balanceOf(user1) == transfer_amount - lock_amount
        assert bond_token.balanceOf(user2) == 0
        assert bond_token.lockedOf(issuer, user1) == lock_amount

    # Error_2
    # Not authorized
    def test_error_2(self, users, IbetStraightBond):
        issuer = users['issuer']
        user1 = users['user1']
        user2 = users['user2']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        transfer_amount = 30
        lock_amount = 10
        unlock_amount = 3

        # transfer to account
        bond_token.transferFrom.transact(issuer, user1, transfer_amount, {'from': issuer})

        # lock
        bond_token.lock.transact(issuer, lock_amount, {'from': user1})

        # unlock
        with brownie.reverts():
            bond_token.unlock.transact(user1, user2, unlock_amount, {'from': user2})

        # assertion
        assert bond_token.balanceOf(user1) == transfer_amount - lock_amount
        assert bond_token.balanceOf(user2) == 0
        assert bond_token.lockedOf(issuer, user1) == lock_amount


# TEST_issueFrom
class TestIssueFrom:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Issue from issuer address
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users['issuer']
        issue_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 1000
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # issue from issuer address
        bond_token.issueFrom.transact(
            issuer,
            brownie.ZERO_ADDRESS,
            issue_amount,
            {'from': issuer}
        )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2] + issue_amount
        assert bond_token.balanceOf(issuer) == deploy_args[2] + issue_amount

    # Normal_2
    # Issue from EOA
    def test_normal_2(self, users, IbetStraightBond):
        issuer = users['issuer']
        issue_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 1000
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # issue from EOA
        bond_token.issueFrom.transact(
            brownie.ETH_ADDRESS,
            brownie.ZERO_ADDRESS,
            issue_amount,
            {'from': issuer}
        )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2] + issue_amount
        assert bond_token.balanceOf(issuer) == deploy_args[2]
        assert bond_token.balanceOf(brownie.ETH_ADDRESS) == issue_amount

    # Normal_3
    # Issue from locked address
    def test_normal_3(self, users, IbetStraightBond):
        issuer = users['issuer']
        lock_address = users['user1']
        lock_amount = 10
        issue_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 1000
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # authorize lock address
        bond_token.authorizeLockAddress.transact(lock_address, True, {'from': issuer})

        # lock
        bond_token.lock.transact(lock_address, lock_amount, {'from': issuer})

        # issue from lock address
        bond_token.issueFrom.transact(
            issuer,
            lock_address,
            issue_amount,
            {'from': issuer}
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
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # issue from issuer address
        with brownie.reverts():
            bond_token.issueFrom.transact(
                issuer,
                brownie.ZERO_ADDRESS,
                1,
                {'from': issuer}
            )

    # Error_1_2
    # Over the limit
    # locked address
    def test_error_1_2(self, users, IbetStraightBond):
        issuer = users['issuer']
        lock_address = users['user1']
        lock_amount = 2 ** 256 - 1
        issue_amount = 1

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # authorize lock address
        bond_token.authorizeLockAddress.transact(lock_address, True, {'from': issuer})

        # lock
        bond_token.lock.transact(lock_address, lock_amount, {'from': issuer})

        # issue from lock address
        with brownie.reverts():
            bond_token.issueFrom.transact(
                issuer,
                lock_address,
                issue_amount,
                {'from': issuer}
            )

        # assertion
        assert bond_token.balanceOf(issuer) == deploy_args[2] - lock_amount
        assert bond_token.lockedOf(lock_address, issuer) == lock_amount

    # Error_2
    # Not authorized
    def test_error_2(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # issue from not authorized user
        with brownie.reverts():
            bond_token.issueFrom.transact(
                issuer,
                brownie.ZERO_ADDRESS,
                1,
                {'from': users['user1']}
            )


# TEST_setFaceValue
class TestSetFaceValue:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.setFaceValue(10001, {'from': issuer})

        # assertion
        assert bond_token.faceValue() == 10001

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        with brownie.reverts():
            bond_token.setFaceValue(10001, {'from': users['user1']})

        assert bond_token.faceValue() == deploy_args[3]


# TEST_redeemFrom
class TestRedeemFrom:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Redeem from issuer address
    def test_normal_1(self, users, IbetStraightBond):
        issuer = users['issuer']
        redeem_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 1000
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # redeem
        bond_token.redeemFrom.transact(
            issuer,
            brownie.ZERO_ADDRESS,
            redeem_amount,
            {'from': issuer}
        )

        # assertion
        total_supply = bond_token.totalSupply()
        balance = bond_token.balanceOf(issuer)
        assert total_supply == deploy_args[2] - redeem_amount
        assert balance == deploy_args[2] - redeem_amount

    # Normal_2
    # Redeem from EOA
    def test_normal_2(self, users, IbetStraightBond):
        issuer = users['issuer']
        user = users['user1']
        transfer_amount = 20
        redeem_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 1000
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # transfer to user
        bond_token.transferFrom.transact(
            issuer,
            user,
            transfer_amount,
            {'from': issuer}
        )

        # redeem
        bond_token.redeemFrom.transact(
            user,
            brownie.ZERO_ADDRESS,
            redeem_amount,
            {'from': issuer}
        )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2] - redeem_amount
        assert bond_token.balanceOf(issuer) == deploy_args[2] - transfer_amount
        assert bond_token.balanceOf(user) == transfer_amount - redeem_amount

    # Normal_3
    # Redeem from locked address
    def test_normal_3(self, users, IbetStraightBond):
        issuer = users['issuer']
        lock_address = users['user1']
        lock_amount = 20
        redeem_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 1000
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # authorize lock address
        bond_token.authorizeLockAddress.transact(
            lock_address,
            True,
            {'from': issuer}
        )

        # lock
        bond_token.lock.transact(
            lock_address,
            lock_amount,
            {'from': issuer}
        )

        # redeem from lock address
        bond_token.redeemFrom.transact(
            issuer,
            lock_address,
            redeem_amount,
            {'from': issuer}
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
        issuer = users['issuer']
        redeem_amount = 101

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 100
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # redeem
        with brownie.reverts():
            bond_token.redeemFrom.transact(
                issuer,
                brownie.ZERO_ADDRESS,
                redeem_amount,
                {'from': issuer}
            )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2]
        assert bond_token.balanceOf(issuer) == deploy_args[2]

    # Error_2
    # Exceeds locked quantity
    def test_error_2(self, users, IbetStraightBond):
        issuer = users['issuer']
        lock_address = users['user1']
        lock_amount = 20
        redeem_amount = 21

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 100
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # authorize lock address
        bond_token.authorizeLockAddress.transact(
            lock_address,
            True,
            {'from': issuer}
        )

        # lock
        bond_token.lock.transact(
            lock_address,
            lock_amount,
            {'from': issuer}
        )

        # redeem from lock address
        with brownie.reverts():
            bond_token.redeemFrom.transact(
                issuer,
                lock_address,
                redeem_amount,
                {'from': issuer}
            )

        # assertion
        assert bond_token.totalSupply() == deploy_args[2]
        assert bond_token.balanceOf(issuer) == deploy_args[2] - lock_amount
        assert bond_token.lockedOf(lock_address, issuer) == lock_amount

    # Error_3
    # Not authorized
    def test_error_3(self, users, IbetStraightBond):
        issuer = users['issuer']
        redeem_amount = 100

        # issue token
        deploy_args = init_args()
        deploy_args[2] = 100
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # redeem
        with brownie.reverts():
            bond_token.redeemFrom.transact(
                issuer,
                brownie.ZERO_ADDRESS,
                redeem_amount,
                {'from': users['user1']}
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
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        bond_token.setRedemptionValue(10000, {'from': issuer})

        # assertion
        assert bond_token.redemptionValue() == 10000

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetStraightBond):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        bond_token = brownie_utils.force_deploy(issuer, IbetStraightBond, *deploy_args)

        # update
        with brownie.reverts():
            bond_token.setRedemptionValue(10000, {'from': users['user1']})

        # assertion
        assert bond_token.redemptionValue() == deploy_args[5]


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
            personal_info_address=brownie.ZERO_ADDRESS
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
            personal_info_address=brownie.ZERO_ADDRESS
        )

        # update
        tx = bond_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

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
            personal_info_address=personal_info.address
        )

        # set required to True
        with brownie.reverts():
            bond_token.setTransferApprovalRequired(
                True,
                {"from": users["user1"]}
            )

        # assertion
        assert bond_token.transferApprovalRequired() == False


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
            personal_info_address=personal_info.address
        )
        bond_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # register personal information (to_address)
        personal_info.register(
            issuer,
            "encrypted_message",
            {"from": to_address}
        )

        # apply for transfer
        tx = bond_token.applyForTransfer(
            to_address,
            transfer_amount,
            transfer_data,
            {"from": issuer}
        )

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(to_address) == 0
        assert bond_token.pendingTransfer(issuer) == transfer_amount
        assert bond_token.applicationsForTransfer(0) == (
            issuer,
            to_address,
            transfer_amount,
            True
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
            personal_info_address=personal_info.address
        )
        bond_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # register personal information (to_address)
        personal_info.register(
            issuer,
            "encrypted_message",
            {"from": to_address}
        )

        # apply for transfer
        for i in range(2):
            bond_token.applyForTransfer(
                to_address,
                transfer_amount,
                transfer_data,
                {"from": issuer}
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
                True
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
            personal_info_address=personal_info.address
        )
        bond_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # apply for transfer
        bond_token.applyForTransfer(
            to_address,
            transfer_amount,
            transfer_data,
            {"from": issuer}
        )

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.pendingTransfer(issuer) == transfer_amount
        assert bond_token.applicationsForTransfer(0) == (
            issuer,
            to_address,
            transfer_amount,
            True
        )

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
            personal_info_address=brownie.ZERO_ADDRESS
        )

        # apply for transfer
        with brownie.reverts():
            bond_token.applyForTransfer(
                to_address,
                transfer_amount,
                transfer_data,
                {"from": issuer}
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
            personal_info_address=brownie.ZERO_ADDRESS
        )
        bond_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )
        bond_token.setTransferable(
            False,
            {"from": issuer}
        )

        # apply for transfer
        with brownie.reverts():
            bond_token.applyForTransfer(
                to_address,
                transfer_amount,
                transfer_data,
                {"from": issuer}
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
            personal_info_address=brownie.ZERO_ADDRESS
        )
        bond_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # apply for transfer
        with brownie.reverts():
            bond_token.applyForTransfer(
                to_address,
                deploy_args[3] + 1,
                transfer_data,
                {"from": issuer}
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
            personal_info_address=personal_info.address
        )
        bond_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # apply for transfer
        with brownie.reverts():
            bond_token.applyForTransfer(
                to_address,
                transfer_amount,
                transfer_data,
                {"from": issuer}
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
            personal_info_address=personal_info.address
        )
        bond_token.transferFrom(
            issuer,
            user1,
            transfer_amount,
            {"from": issuer}
        )
        bond_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # register personal information (to_address)
        personal_info.register(
            issuer,
            "encrypted_message",
            {"from": user2}
        )

        # apply for transfer
        bond_token.applyForTransfer(
            user2,
            transfer_amount,
            "test_data",
            {"from": user1}  # from user1 to user2
        )

        # cancel transfer (from applicant)
        tx = bond_token.cancelTransfer(
            0,
            "test_data",
            {"from": user1}
        )

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(user1) == transfer_amount
        assert bond_token.pendingTransfer(user1) == 0
        assert bond_token.applicationsForTransfer(0) == (
            user1,
            user2,
            transfer_amount,
            False
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
            personal_info_address=personal_info.address
        )
        bond_token.transferFrom(
            issuer,
            user1,
            transfer_amount,
            {"from": issuer}
        )
        bond_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # register personal information (to_address)
        personal_info.register(
            issuer,
            "encrypted_message",
            {"from": user2}
        )

        # apply for transfer
        bond_token.applyForTransfer(
            user2,
            transfer_amount,
            "test_data",
            {"from": user1}  # from user1 to user2
        )

        # cancel transfer (from issuer)
        tx = bond_token.cancelTransfer(
            0,
            "test_data",
            {"from": issuer}
        )

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(user1) == transfer_amount
        assert bond_token.pendingTransfer(user1) == 0
        assert bond_token.applicationsForTransfer(0) == (
            user1,
            user2,
            transfer_amount,
            False
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
            personal_info_address=personal_info.address
        )
        bond_token.transferFrom(
            issuer,
            user1,
            transfer_amount,
            {"from": issuer}
        )
        bond_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # register personal information (to_address)
        personal_info.register(
            issuer,
            "encrypted_message",
            {"from": user2}
        )

        # apply for transfer
        bond_token.applyForTransfer(
            user2,
            transfer_amount,
            "test_data",
            {"from": user1}  # from user1 to user2
        )

        # cancel transfer (from issuer)
        with brownie.reverts():
            bond_token.cancelTransfer(
                0,
                "test_data",
                {"from": user2}
            )

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(user1) == 0
        assert bond_token.pendingTransfer(user1) == transfer_amount
        assert bond_token.applicationsForTransfer(0) == (
            user1,
            user2,
            transfer_amount,
            True
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
            personal_info_address=personal_info.address
        )
        bond_token.transferFrom(
            issuer,
            user1,
            transfer_amount,
            {"from": issuer}
        )
        bond_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # register personal information (to_address)
        personal_info.register(
            issuer,
            "encrypted_message",
            {"from": user2}
        )

        # apply for transfer
        bond_token.applyForTransfer(
            user2,
            transfer_amount,
            "test_data",
            {"from": user1}  # from user1 to user2
        )

        # cancel transfer (1)
        bond_token.cancelTransfer(
            0,
            "test_data",
            {"from": user1}
        )

        # cancel transfer (2)
        with brownie.reverts():
            bond_token.cancelTransfer(
                0,
                "test_data",
                {"from": user1}
            )

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(user1) == transfer_amount
        assert bond_token.pendingTransfer(user1) == 0
        assert bond_token.applicationsForTransfer(0) == (
            user1,
            user2,
            transfer_amount,
            False
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
            personal_info_address=personal_info.address
        )
        bond_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # register personal information (to_address)
        personal_info.register(
            issuer,
            "encrypted_message",
            {"from": user1}
        )

        # apply for transfer
        bond_token.applyForTransfer(
            user1,
            transfer_amount,
            "test_data",
            {"from": issuer}  # from issuer to user1
        )

        # approve transfer
        tx = bond_token.approveTransfer(
            0,
            "test_data",
            {"from": issuer}
        )

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(user1) == transfer_amount
        assert bond_token.pendingTransfer(issuer) == 0
        assert bond_token.applicationsForTransfer(0) == (
            issuer,
            user1,
            transfer_amount,
            False
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
            personal_info_address=personal_info.address
        )
        bond_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # register personal information (to_address)
        personal_info.register(
            issuer,
            "encrypted_message",
            {"from": user1}
        )

        # apply for transfer
        bond_token.applyForTransfer(
            user1,
            transfer_amount,
            "test_data",
            {"from": issuer}  # from issuer to user1
        )

        # approve transfer
        with brownie.reverts():
            bond_token.approveTransfer(
                0,
                "test_data",
                {"from": user1}
            )

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(user1) == 0
        assert bond_token.pendingTransfer(issuer) == transfer_amount
        assert bond_token.applicationsForTransfer(0) == (
            issuer,
            user1,
            transfer_amount,
            True
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
            personal_info_address=personal_info.address
        )
        bond_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # register personal information (to_address)
        personal_info.register(
            issuer,
            "encrypted_message",
            {"from": user1}
        )

        # apply for transfer
        bond_token.applyForTransfer(
            user1,
            transfer_amount,
            "test_data",
            {"from": issuer}  # from issuer to user1
        )

        # approve transfer
        bond_token.setTransferable(
            False,
            {"from": issuer}
        )
        with brownie.reverts():
            bond_token.approveTransfer(
                0,
                "test_data",
                {"from": issuer}
            )

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(user1) == 0
        assert bond_token.pendingTransfer(issuer) == transfer_amount
        assert bond_token.applicationsForTransfer(0) == (
            issuer,
            user1,
            transfer_amount,
            True
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
            personal_info_address=personal_info.address
        )
        bond_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # register personal information (to_address)
        personal_info.register(
            issuer,
            "encrypted_message",
            {"from": user1}
        )

        # apply for transfer
        bond_token.applyForTransfer(
            user1,
            transfer_amount,
            "test_data",
            {"from": issuer}  # from issuer to user1
        )

        # approve transfer (1)
        bond_token.approveTransfer(
            0,
            "test_data",
            {"from": issuer}
        )

        # approve transfer (2)
        with brownie.reverts():
            bond_token.approveTransfer(
                0,
                "test_data",
                {"from": issuer}
            )

        # assertion
        assert bond_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert bond_token.balances(user1) == transfer_amount
        assert bond_token.pendingTransfer(issuer) == 0
        assert bond_token.applicationsForTransfer(0) == (
            issuer,
            user1,
            transfer_amount,
            False
        )
