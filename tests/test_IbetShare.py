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


def init_args():
    name = 'test_share'
    symbol = 'test_symbol'
    issue_price = 2 ** 256 - 1
    total_supply = 2 ** 256 - 1
    dividends = 2 ** 256 - 1
    dividend_record_date = '20200829'
    dividend_payment_date = '20200831'
    cancellation_date = '20191231'
    principal_value = 2 ** 256 - 1

    deploy_args = [
        name,
        symbol,
        issue_price,
        total_supply,
        dividends,
        dividend_record_date,
        dividend_payment_date,
        cancellation_date,
        principal_value
    ]
    return deploy_args


def issue_transferable_share_token(issuer, exchange_address, personal_info_address):
    from brownie import IbetShare

    name = 'test_share'
    symbol = 'IBS'
    issue_price = 1000
    total_supply = 10000
    dividends = 1000
    dividend_record_date = '20200829'
    dividend_payment_date = '20200831'
    cancellation_date = '20191231'
    principal_value = 1000

    deploy_args = [
        name,
        symbol,
        issue_price,
        total_supply,
        dividends,
        dividend_record_date,
        dividend_payment_date,
        cancellation_date,
        principal_value
    ]

    share_token = issuer.deploy(IbetShare, *deploy_args)
    share_token.setTradableExchange.transact(exchange_address, {'from': issuer})
    share_token.setPersonalInfoAddress.transact(personal_info_address, {'from': issuer})
    share_token.setTransferable.transact(True, {'from': issuer})
    return share_token, deploy_args


# TEST_deploy
class TestDeploy:

    # Normal_1
    def test_normal_1(self, IbetShare, users):
        issuer = users['issuer']
        deploy_args = init_args()

        share_contract = issuer.deploy(
            IbetShare,
            *deploy_args
        )

        owner_address = share_contract.owner()
        name = share_contract.name()
        symbol = share_contract.symbol()
        issue_price = share_contract.issuePrice()
        principal_value = share_contract.principalValue()
        total_supply = share_contract.totalSupply()
        dividend_information = share_contract.dividendInformation()
        cancellation_date = share_contract.cancellationDate()
        is_canceled = share_contract.isCanceled()
        status = share_contract.status()
        balance = share_contract.balanceOf(issuer)

        assert owner_address == issuer
        assert name == deploy_args[0]
        assert symbol == deploy_args[1]
        assert issue_price == deploy_args[2]
        assert total_supply == deploy_args[3]
        assert dividend_information[0] == deploy_args[4]
        assert dividend_information[1] == deploy_args[5]
        assert dividend_information[2] == deploy_args[6]
        assert cancellation_date == deploy_args[7]
        assert principal_value == deploy_args[8]
        assert is_canceled == False
        assert status == True
        assert balance == total_supply


# TEST_setPrincipalValue
class TestSetPrincipalValue:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetShare):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # update principal value
        share_token.setPrincipalValue.transact(
            9000,
            {"from": issuer}
        )

        # assertion
        assert share_token.principalValue() == 9000

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetShare):
        issuer = users["issuer"]
        trader = users['trader']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # update principal value
        with brownie.reverts():
            share_token.setPrincipalValue.transact(
                9000,
                {"from": trader}
            )

        # assertion
        assert share_token.principalValue() == deploy_args[8]


# TEST_setTradableExchange
class TestSetTradableExchange:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # change exchange contract
        share_token.setTradableExchange.transact(
            brownie.ETH_ADDRESS,
            {'from': issuer}
        )

        # assertion
        assert share_token.tradableExchange() == brownie.ETH_ADDRESS

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # change exchange contract
        with brownie.reverts():
            share_token.setTradableExchange.transact(
                brownie.ETH_ADDRESS,
                {'from': users['user1']}
            )

        # assertion
        assert share_token.tradableExchange() == brownie.ZERO_ADDRESS


# TEST_setPersonalInfoAddress
class TestSetPersonalInfoAddress:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # update contract
        share_token.setPersonalInfoAddress.transact(
            brownie.ETH_ADDRESS,
            {'from': issuer}
        )

        # assertion
        assert share_token.personalInfoAddress() == brownie.ETH_ADDRESS

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # update contract
        with brownie.reverts():
            share_token.setPersonalInfoAddress.transact(
                brownie.ETH_ADDRESS,
                {'from': users['user1']}
            )

        # assertion
        assert share_token.personalInfoAddress() == brownie.ZERO_ADDRESS


# TEST_setDividendInformation
class TestSetDividendInformation:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # update
        share_token.setDividendInformation.transact(
            22000,
            '20200829',
            '20200831',
            {'from': issuer}
        )

        # assertion
        dividend_information = share_token.dividendInformation()
        assert dividend_information[0] == 22000
        assert dividend_information[1] == '20200829'
        assert dividend_information[2] == '20200831'

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # update
        with brownie.reverts():
            share_token.setDividendInformation.transact(
                22000,
                '20200829',
                '20200831',
                {'from': users['user1']}
            )

        # assertion
        dividend_information = share_token.dividendInformation()
        assert dividend_information[0] == deploy_args[4]
        assert dividend_information[1] == deploy_args[5]
        assert dividend_information[2] == deploy_args[6]


# TEST_setCancellationDate
class TestSetCancellationDate:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # update
        share_token.setCancellationDate.transact(
            '20200831',
            {'from': issuer}
        )

        # assertion
        cancellation_date = share_token.cancellationDate()
        assert cancellation_date == '20200831'

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # update
        with brownie.reverts():
            share_token.setCancellationDate.transact(
                '20200930',
                {'from': users['user1']}
            )

        # assertion
        cancellation_date = share_token.cancellationDate()
        assert cancellation_date == deploy_args[7]


# TEST_SetReferenceUrls
class TestSetReferenceUrls:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # update
        reference_url = 'https://some_reference_url.com/image.png'
        share_token.setReferenceUrls.transact(
            0,
            reference_url,
            {'from': issuer}
        )

        # assertion
        reference_urls = share_token.referenceUrls(0)
        assert reference_urls == 'https://some_reference_url.com/image.png'

    #######################################
    # Error
    #######################################

    # Error_1
    def test_error_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # update
        reference_url = 'https://some_reference_url.com/image.png'
        with brownie.reverts():
            share_token.setReferenceUrls.transact(
                0,
                reference_url,
                {'from': users['user1']}
            )

        # assertion
        reference_url = share_token.referenceUrls(0)
        assert reference_url == ''


# TEST_setContactInformation
class TestSetContactInformation:

    #######################################
    # Normal
    #######################################

    # 正常系1: 発行（デプロイ） -> 修正
    def test_normal_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # update
        share_token.setContactInformation.transact(
            'updated contact information',
            {'from': issuer}
        )

        # assertion
        contact_information = share_token.contactInformation()
        assert contact_information == 'updated contact information'

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # update
        with brownie.reverts():
            share_token.setContactInformation.transact(
                'updated contact information',
                {'from': users['user1']}
            )

        # assertion
        contact_information = share_token.contactInformation()
        assert contact_information == ''


# TEST_setPrivacyPolicy
class TestSetPrivacyPolicy:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # update
        share_token.setPrivacyPolicy.transact(
            'updated privacy policy',
            {'from': issuer}
        )

        # assertion
        privacy_policy = share_token.privacyPolicy()
        assert privacy_policy == 'updated privacy policy'

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # update
        with brownie.reverts():
            share_token.setPrivacyPolicy.transact(
                'updated privacy policy',
                {'from': users['user1']}
            )

        # assertion
        privacy_policy = share_token.privacyPolicy()
        assert privacy_policy == ''


# TEST_setMemo
class TestSetMemo:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # set memo
        share_token.setMemo.transact(
            'updated memo',
            {'from': issuer}
        )

        # assertion
        memo = share_token.memo()
        assert memo == 'updated memo'

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # set memo
        with brownie.reverts():
            share_token.setMemo.transact(
                'updated memo',
                {'from': users['user1']}
            )

        memo = share_token.memo()
        assert memo == ''


# TEST_setTransferable
class TestSetTransferable:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # update
        share_token.setTransferable.transact(True, {'from': issuer})

        # assertion
        assert share_token.transferable() is True

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # update
        with brownie.reverts():
            share_token.setTransferable.transact(True, {'from': users['user1']})

        # assertion
        assert share_token.transferable() is False


# TEST_setOfferingStatus
class TestSetOfferingStatus:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # update
        share_token.setOfferingStatus.transact(True, {'from': issuer})

        # assertion
        assert share_token.offeringStatus() is True

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # change exchange contract
        with brownie.reverts():
            share_token.setOfferingStatus.transact(True, {'from': users['user1']})


# TEST_balanceOf
class TestBalanceOf:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # assertion
        balance = share_token.balanceOf(issuer)
        assert balance == deploy_args[3]


# TEST_authorize
class TestAuthorize:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # authorize
        share_token.authorize.transact(
            brownie.ETH_ADDRESS,
            True,
            {'from': issuer}
        )

        # assertion
        assert share_token.authorizedAddress(brownie.ETH_ADDRESS) is True
        assert share_token.authorizedAddress(brownie.ZERO_ADDRESS) is False

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # authorize
        with brownie.reverts():
            share_token.authorize.transact(
                brownie.ETH_ADDRESS,
                True,
                {'from': users['user1']}
            )

        # assertion
        assert share_token.authorizedAddress(brownie.ETH_ADDRESS) is False


# TEST_lock
class TestLock:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Lock assets to authorized addresses
    def test_normal_1(self, users, IbetShare):
        issuer = users['issuer']
        user = users['user1']
        target = users['user2']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        transfer_amount = 30
        lock_amount = 10

        # transfer to account
        share_token.transferFrom.transact(issuer, user, transfer_amount, {'from': issuer})

        # authorize target address
        share_token.authorize.transact(target, True, {'from': issuer})

        # lock
        tx = share_token.lock.transact(target, lock_amount, {'from': user})

        # assertion
        assert share_token.balanceOf(user) == transfer_amount - lock_amount
        assert share_token.lockedOf(target, user) == lock_amount

        assert tx.events["Lock"]["from"] == user
        assert tx.events["Lock"]["target_address"] == target
        assert tx.events["Lock"]["value"] == lock_amount

    # Normal_2
    # Lock assets to issuer addresses
    def test_normal_2(self, users, IbetShare):
        issuer = users['issuer']
        user = users['user1']

        transfer_amount = 30
        lock_amount = 10

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # transfer to account
        share_token.transferFrom.transact(issuer, user, transfer_amount, {'from': issuer})

        # lock
        share_token.lock.transact(issuer, lock_amount, {'from': user})

        # assertion
        assert share_token.balanceOf(user) == transfer_amount - lock_amount
        assert share_token.lockedOf(issuer, user) == lock_amount

    #######################################
    # Error
    #######################################

    # Error_1
    # Insufficient balance
    def test_error_1(self, users, IbetShare):
        issuer = users['issuer']
        user = users['user1']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        transfer_amount = 30
        lock_amount = 40

        # transfer to account
        share_token.transferFrom.transact(issuer, user, transfer_amount, {'from': issuer})

        # lock
        with brownie.reverts():
            share_token.lock.transact(issuer, lock_amount, {'from': user})

        # assertion
        assert share_token.balanceOf(user) == transfer_amount
        assert share_token.lockedOf(issuer, user) == 0

    # Error_2
    # Lock assets to not authorized address
    def test_error_2(self, users, IbetShare):
        issuer = users['issuer']
        user = users['user1']
        not_authorized_address = users['user2']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        transfer_amount = 30
        lock_amount = 10

        # transfer to account
        share_token.transferFrom.transact(issuer, user, transfer_amount, {'from': issuer})

        # lock
        with brownie.reverts():
            share_token.lock.transact(not_authorized_address, lock_amount, {'from': user})

        # assertion
        assert share_token.balanceOf(user) == transfer_amount
        assert share_token.lockedOf(issuer, user) == 0


# TEST_lockedOf
class TestLockedOf:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetShare):
        issuer = users['issuer']
        user = users['user1']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        transfer_amount = 30
        lock_amount = 10

        # transfer to account
        share_token.transferFrom.transact(issuer, user, transfer_amount, {'from': issuer})

        # lock
        share_token.lock.transact(issuer, lock_amount, {'from': user})

        # assertion
        assert share_token.lockedOf(issuer, user) == lock_amount


# TEST_unlock
class TestUnlock:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # authorized addresses
    def test_normal_1(self, users, IbetShare):
        issuer = users['issuer']
        user1 = users['user1']
        user2 = users['user2']
        target = users['agent']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        transfer_amount = 30
        lock_amount = 20
        unlock_amount = 10

        # transfer to account
        share_token.transferFrom.transact(issuer, user1, transfer_amount, {'from': issuer})

        # authorize target address
        share_token.authorize.transact(target, True, {'from': issuer})

        # lock
        share_token.lock.transact(target, lock_amount, {'from': user1})

        # unlock
        tx = share_token.unlock.transact(user1, user2, unlock_amount, {'from': target})

        # assertion
        assert share_token.balanceOf(user1) == transfer_amount - lock_amount
        assert share_token.balanceOf(user2) == unlock_amount
        assert share_token.lockedOf(target, user1) == lock_amount - unlock_amount

        assert tx.events["Unlock"]["from"] == user1.address
        assert tx.events["Unlock"]["to"] == user2.address
        assert tx.events["Unlock"]["value"] == unlock_amount

    # Normal_2
    # issuer
    def test_normal_2(self, users, IbetShare):
        issuer = users['issuer']
        user1 = users['user1']
        user2 = users['user2']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        transfer_amount = 30
        lock_amount = 20
        unlock_amount = 10

        # transfer to account
        share_token.transferFrom.transact(issuer, user1, transfer_amount, {'from': issuer})

        # lock
        share_token.lock.transact(issuer, lock_amount, {'from': user1})

        # unlock
        tx = share_token.unlock.transact(user1, user2, unlock_amount, {'from': issuer})

        # assertion
        assert share_token.balanceOf(user1) == transfer_amount - lock_amount
        assert share_token.balanceOf(user2) == unlock_amount
        assert share_token.lockedOf(issuer, user1) == lock_amount - unlock_amount

        assert tx.events["Unlock"]["from"] == user1.address
        assert tx.events["Unlock"]["to"] == user2.address
        assert tx.events["Unlock"]["value"] == unlock_amount

    #######################################
    # Error
    #######################################

    # Error_1
    # Cannot unlock a quantity that exceeds the lock quantity
    def test_error_1(self, users, IbetShare):
        issuer = users['issuer']
        user1 = users['user1']
        user2 = users['user2']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        transfer_amount = 30
        lock_amount = 10
        unlock_amount = 11

        # transfer to account
        share_token.transferFrom.transact(issuer, user1, transfer_amount, {'from': issuer})

        # lock
        share_token.lock.transact(issuer, lock_amount, {'from': user1})

        # unlock
        with brownie.reverts():
            share_token.unlock.transact(user1, user2, unlock_amount, {'from': issuer})

        # assertion
        assert share_token.balanceOf(user1) == transfer_amount - lock_amount
        assert share_token.balanceOf(user2) == 0
        assert share_token.lockedOf(issuer, user1) == lock_amount

    # Error_2
    # Not authorized
    def test_error_2(self, users, IbetShare):
        issuer = users['issuer']
        user1 = users['user1']
        user2 = users['user2']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        transfer_amount = 30
        lock_amount = 10
        unlock_amount = 3

        # transfer to account
        share_token.transferFrom.transact(issuer, user1, transfer_amount, {'from': issuer})

        # lock
        share_token.lock.transact(issuer, lock_amount, {'from': user1})

        # unlock
        with brownie.reverts():
            share_token.unlock.transact(user1, user2, unlock_amount, {'from': user2})

        # assertion
        assert share_token.balanceOf(user1) == transfer_amount - lock_amount
        assert share_token.balanceOf(user2) == 0
        assert share_token.lockedOf(issuer, user1) == lock_amount


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
        share_token, deploy_args = issue_transferable_share_token(
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
        tx = share_token.transfer.transact(
            to_address.address,
            transfer_amount,
            {"from": issuer}
        )

        # assertion
        assert share_token.balanceOf(issuer) == deploy_args[3] - transfer_amount
        assert share_token.balanceOf(to_address) == transfer_amount

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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=exchange.address,
            personal_info_address=personal_info.address
        )

        # transfer
        to_address = exchange.address
        tx = share_token.transfer.transact(
            to_address,
            transfer_amount,
            {"from": from_address}
        )

        # assertion
        assert share_token.balanceOf(from_address) == deploy_args[3] - transfer_amount
        assert share_token.balanceOf(to_address) == transfer_amount

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
        share_token, deploy_args = issue_transferable_share_token(
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
        with brownie.reverts():
            share_token.transfer.transact(
                to_address.address,
                transfer_amount,
                {"from": issuer}
            )

        # assertion
        assert share_token.balanceOf(issuer) == deploy_args[3]
        assert share_token.balanceOf(to_address) == 0

    # Error_2
    # Cannot access private function
    def test_error_2(self, users):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["trader"]
        transfer_amount = 100

        # issue token
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=brownie.ZERO_ADDRESS
        )

        with pytest.raises(AttributeError):
            share_token.isContract(to_address)

        with pytest.raises(AttributeError):
            share_token.transferToAddress.transact(
                to_address,
                transfer_amount,
                "test_data",
                {"from": from_address}
            )

        with pytest.raises(AttributeError):
            share_token.transferToContract.transact(
                to_address,
                transfer_amount,
                "test_data",
                {"from": from_address}
            )

    # Error_3
    # Not transferable token
    def test_error_3(self, users, IbetShare):
        issuer = users["issuer"]
        to_address = users["trader"]
        transfer_amount = 100

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # transfer
        with brownie.reverts():
            share_token.transfer.transact(
                to_address,
                transfer_amount,
                {"from": issuer}
            )

        # assertion
        from_balance = share_token.balanceOf(issuer)
        to_balance = share_token.balanceOf(to_address)
        assert from_balance == deploy_args[3]
        assert to_balance == 0

    # Error_4
    # Transfer to non-tradable exchange
    def test_error_4(self, users, IbetShare, exchange):
        issuer = users['issuer']
        transfer_amount = 100

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # transfer
        with brownie.reverts():
            share_token.transfer.transact(
                exchange,
                transfer_amount,
                {"from": users["admin"]}
            )

        assert share_token.balanceOf(issuer) == deploy_args[3]
        assert share_token.balanceOf(exchange) == 0

    # Error_5
    # Transfer to an address with personal information not registered
    def test_error_5(self, users, personal_info):
        issuer = users["issuer"]
        to_address = users["trader"]
        transfer_amount = 100

        # issue token
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # transfer
        with brownie.reverts():
            share_token.transfer.transact(
                to_address.address,
                transfer_amount,
                {"from": issuer}
            )

        # assertion
        assert share_token.balanceOf(issuer) == deploy_args[3]
        assert share_token.balanceOf(to_address) == 0

    # Error_6
    # Tokens that require transfer approval
    def test_error_6(self, users, personal_info):
        issuer = users["issuer"]
        to_address = users["trader"]
        transfer_amount = 100

        # issue token
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )
        share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # transfer
        with brownie.reverts():
            share_token.transfer.transact(
                to_address,
                transfer_amount,
                {"from": issuer}
            )

        # assertion
        from_balance = share_token.balanceOf(issuer)
        to_balance = share_token.balanceOf(to_address)
        assert from_balance == deploy_args[3]
        assert to_balance == 0


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

        # issue share token
        share_contract, deploy_args = issue_transferable_share_token(
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
        share_contract.bulkTransfer.transact(
            to_address_list,
            amount_list,
            {"from": from_address}
        )

        # assertion
        from_balance = share_contract.balanceOf(from_address)
        to_balance = share_contract.balanceOf(to_address)
        assert from_balance == deploy_args[3] - 1
        assert to_balance == 1

    # Normal_2
    # Bulk transfer to account address (multiple data)
    def test_normal_2(self, users, personal_info):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["trader"]

        # issue share token
        share_contract, deploy_args = issue_transferable_share_token(
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

        share_contract.bulkTransfer.transact(
            to_address_list,
            amount_list,
            {"from": from_address}
        )

        # assertion
        from_balance = share_contract.balanceOf(from_address)
        to_balance = share_contract.balanceOf(to_address)
        assert from_balance == deploy_args[3] - 100
        assert to_balance == 100

    # Normal_3
    # Bulk transfer to contract address
    def test_normal_3(self, users, exchange, personal_info):
        issuer = users["issuer"]
        from_address = issuer

        # issue share token
        share_contract, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=exchange.address,
            personal_info_address=personal_info.address
        )

        # bulk transfer
        to_address_list = [exchange.address]
        amount_list = [1]
        share_contract.bulkTransfer.transact(
            to_address_list,
            amount_list,
            {"from": from_address}
        )

        # assertion
        from_balance = share_contract.balanceOf(from_address)
        to_balance = share_contract.balanceOf(exchange.address)
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

        # issue share token
        share_contract, deploy_args = issue_transferable_share_token(
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
            share_contract.bulkTransfer.transact(
                [to_address, to_address],
                [deploy_args[3], 1],
                {'from': issuer}
            )

        # assertion
        assert share_contract.balanceOf(issuer) == deploy_args[3]
        assert share_contract.balanceOf(to_address) == 0

    # Error_2
    # Not transferable token
    def test_error_2(self, users, personal_info):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["trader"]

        # issue share token
        share_contract, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )
        share_contract.setTransferable.transact(
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
            share_contract.bulkTransfer.transact(
                [to_address],
                [1],
                {"from": issuer}
            )

        # assertion
        from_balance = share_contract.balanceOf(issuer)
        to_balance = share_contract.balanceOf(to_address)
        assert from_balance == deploy_args[3]
        assert to_balance == 0

    # Error_3
    # Transfer to an address with no personal information registered
    def test_error_3(self, users, personal_info):
        issuer = users["issuer"]
        to_address = users["trader"]

        # issue share token
        share_contract, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # bulk transfer
        with brownie.reverts():
            share_contract.bulkTransfer.transact(
                [to_address],
                [1],
                {'from': issuer}
            )

        # assertion
        from_balance = share_contract.balanceOf(issuer)
        to_balance = share_contract.balanceOf(to_address)
        assert from_balance == deploy_args[3]
        assert to_balance == 0

    # Error_4
    # Tokens that require transfer approval cannot be executed.
    def test_error_4(self, users, personal_info):
        issuer = users["issuer"]
        to_address = users["trader"]

        # issue share token
        share_contract, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )
        share_contract.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # bulk transfer
        with brownie.reverts():
            share_contract.bulkTransfer.transact(
                [to_address],
                [1],
                {'from': issuer}
            )

        # assertion
        from_balance = share_contract.balanceOf(issuer)
        to_balance = share_contract.balanceOf(to_address)
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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # forced transfer
        share_token.transferFrom.transact(
            from_address,
            to_address,
            value,
            {'from': issuer}
        )

        # assertion
        assert share_token.balanceOf(issuer) == deploy_args[3] - value
        assert share_token.balanceOf(to_address) == value

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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # forced transfer
        with brownie.reverts():
            share_token.transferFrom.transact(
                from_address,
                to_address,
                deploy_args[3] + 1,
                {'from': issuer}
            )

        # assertion
        assert share_token.balanceOf(issuer) == deploy_args[3]
        assert share_token.balanceOf(to_address) == 0

    # Error_2
    # Not authorized
    def test_error_2(self, users, personal_info):
        issuer = users['issuer']
        from_address = issuer
        to_address = users['user1']

        # issue token
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # forced transfer
        with brownie.reverts():
            share_token.transferFrom.transact(
                from_address,
                to_address,
                deploy_args[3] + 1,
                {'from': to_address}
            )

        # assertion
        assert share_token.balanceOf(issuer) == deploy_args[3]
        assert share_token.balanceOf(to_address) == 0


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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # assertion
        application = share_token.applications(brownie.ETH_ADDRESS)
        assert application[0] == 0
        assert application[1] == 0
        assert application[2] == ''

    # Normal_2
    def test_normal_2(self, users, personal_info):
        issuer = users['issuer']
        applicant = users['user1']

        # issue token
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # update offering status
        share_token.setOfferingStatus.transact(True, {'from': issuer})

        # register personal info of applicant
        personal_info.register.transact(
            issuer,
            "encrypted_message",
            {'from': applicant}
        )

        # apply for offering
        share_token.applyForOffering.transact(
            10,
            'abcdefgh',
            {'from': applicant}
        )

        # assertion
        application = share_token.applications(applicant)
        assert application[0] == 10
        assert application[1] == 0
        assert application[2] == 'abcdefgh'

    # Normal_3
    # Multiple applications
    def test_normal_3(self, users, personal_info):
        issuer = users['issuer']
        applicant = users['user1']

        # issue token
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # update offering status
        share_token.setOfferingStatus.transact(True, {'from': issuer})

        # register personal info of applicant
        personal_info.register.transact(
            issuer,
            "encrypted_message",
            {'from': applicant}
        )

        # apply for offering (1)
        share_token.applyForOffering.transact(
            10,
            'abcdefgh',
            {'from': applicant}
        )

        # apply for offering (2)
        share_token.applyForOffering.transact(
            20,
            'vwxyz',
            {'from': applicant}
        )

        # assertion
        application = share_token.applications(applicant)
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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # apply for offering
        with brownie.reverts():
            share_token.applyForOffering.transact(
                10,
                'abcdefgh',
                {'from': applicant}
            )

        # assertion
        application = share_token.applications(applicant)
        assert application[0] == 0
        assert application[1] == 0
        assert application[2] == ''

    # Error_2
    # Applicant need to register personal information.
    def test_error_2(self, users, personal_info):
        issuer = users['issuer']
        applicant = users['user1']

        # issue token
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # update offering status
        share_token.setOfferingStatus.transact(True, {'from': issuer})

        # apply for offering
        with brownie.reverts():
            share_token.applyForOffering.transact(
                10,
                'abcdefgh',
                {'from': applicant}
            )

        # assertion
        application = share_token.applications(applicant)
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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # update offering status
        share_token.setOfferingStatus.transact(True, {'from': issuer})

        # register personal info of applicant
        personal_info.register.transact(
            issuer,
            "encrypted_message",
            {'from': applicant}
        )

        # apply for offering
        share_token.applyForOffering.transact(
            10,
            'abcdefgh',
            {'from': applicant}
        )

        # allot
        share_token.allot.transact(
            applicant,
            5,
            {'from': issuer}
        )

        # assertion
        application = share_token.applications(applicant)
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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # update offering status
        share_token.setOfferingStatus.transact(True, {'from': issuer})

        # allot
        with brownie.reverts():
            share_token.allot.transact(applicant, 5, {'from': applicant})

        # assertion
        application = share_token.applications(applicant)
        assert application[0] == 0
        assert application[1] == 0
        assert application[2] == ''


# TEST_issueFrom
class TestIssueFrom:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Issue from issuer address
    def test_normal_1(self, users, IbetShare):
        issuer = users['issuer']
        issue_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[3] = 1000
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # issue from issuer address
        share_token.issueFrom.transact(
            issuer,
            brownie.ZERO_ADDRESS,
            issue_amount,
            {'from': issuer}
        )

        # assertion
        assert share_token.totalSupply() == deploy_args[3] + issue_amount
        assert share_token.balanceOf(issuer) == deploy_args[3] + issue_amount

    # Normal_2
    # Issue from EOA
    def test_normal_2(self, users, IbetShare):
        issuer = users['issuer']
        issue_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[3] = 1000
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # issue from EOA
        share_token.issueFrom.transact(
            brownie.ETH_ADDRESS,
            brownie.ZERO_ADDRESS,
            issue_amount,
            {'from': issuer}
        )

        # assertion
        assert share_token.totalSupply() == deploy_args[3] + issue_amount
        assert share_token.balanceOf(issuer) == deploy_args[3]
        assert share_token.balanceOf(brownie.ETH_ADDRESS) == issue_amount

    # Normal_3
    # Issue from locked address
    def test_normal_3(self, users, IbetShare):
        issuer = users['issuer']
        lock_address = users['user1']
        lock_amount = 10
        issue_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[3] = 1000
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # authorize lock address
        share_token.authorize.transact(lock_address, True, {'from': issuer})

        # lock
        share_token.lock.transact(lock_address, lock_amount, {'from': issuer})

        # issue from lock address
        share_token.issueFrom.transact(
            issuer,
            lock_address,
            issue_amount,
            {'from': issuer}
        )

        # assertion
        assert share_token.totalSupply() == deploy_args[3] + issue_amount
        assert share_token.balanceOf(issuer) == deploy_args[3] - lock_amount
        assert share_token.lockedOf(lock_address, issuer) == lock_amount + issue_amount

    #######################################
    # Error
    #######################################

    # Error_1_1
    # Over the limit
    # issuer address
    def test_error_1_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # issue from issuer address
        with brownie.reverts():
            share_token.issueFrom.transact(
                issuer,
                brownie.ZERO_ADDRESS,
                1,
                {'from': issuer}
            )

    # Error_1_2
    # Over the limit
    # locked address
    def test_error_1_2(self, users, IbetShare):
        issuer = users['issuer']
        lock_address = users['user1']
        lock_amount = 2 ** 256 - 1
        issue_amount = 1

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # authorize lock address
        share_token.authorize.transact(lock_address, True, {'from': issuer})

        # lock
        share_token.lock.transact(lock_address, lock_amount, {'from': issuer})

        # issue from lock address
        with brownie.reverts():
            share_token.issueFrom.transact(
                issuer,
                lock_address,
                issue_amount,
                {'from': issuer}
            )

        # assertion
        assert share_token.balanceOf(issuer) == deploy_args[3] - lock_amount
        assert share_token.lockedOf(lock_address, issuer) == lock_amount

    # Error_2
    # Not authorized
    def test_error_2(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # issue from not authorized user
        with brownie.reverts():
            share_token.issueFrom.transact(
                issuer,
                brownie.ZERO_ADDRESS,
                1,
                {'from': users['user1']}
            )


# TEST_redeemFrom
class TestRedeemFrom:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Redeem from issuer address
    def test_normal_1(self, users, IbetShare):
        issuer = users['issuer']
        redeem_amount = 10

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # redeem
        share_token.redeemFrom.transact(
            issuer,
            brownie.ZERO_ADDRESS,
            redeem_amount,
            {'from': issuer}
        )

        # assertion
        total_supply = share_token.totalSupply()
        balance = share_token.balanceOf(issuer)
        assert total_supply == deploy_args[3] - redeem_amount
        assert balance == deploy_args[3] - redeem_amount

    # Normal_2
    # Redeem from EOA
    def test_normal_2(self, users, IbetShare):
        issuer = users['issuer']
        user = users['user1']
        transfer_amount = 20
        redeem_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[3] = 1000
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # transfer to user
        share_token.transferFrom.transact(
            issuer,
            user,
            transfer_amount,
            {'from': issuer}
        )

        # redeem
        share_token.redeemFrom.transact(
            user,
            brownie.ZERO_ADDRESS,
            redeem_amount,
            {'from': issuer}
        )

        # assertion
        assert share_token.totalSupply() == deploy_args[3] - redeem_amount
        assert share_token.balanceOf(issuer) == deploy_args[3] - transfer_amount
        assert share_token.balanceOf(user) == transfer_amount - redeem_amount

    # Normal_3
    # Redeem from locked address
    def test_normal_3(self, users, IbetShare):
        issuer = users['issuer']
        lock_address = users['user1']
        lock_amount = 20
        redeem_amount = 10

        # issue token
        deploy_args = init_args()
        deploy_args[3] = 1000
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # authorize lock address
        share_token.authorize.transact(
            lock_address,
            True,
            {'from': issuer}
        )

        # lock
        share_token.lock.transact(
            lock_address,
            lock_amount,
            {'from': issuer}
        )

        # redeem from lock address
        share_token.redeemFrom.transact(
            issuer,
            lock_address,
            redeem_amount,
            {'from': issuer}
        )

        # assertion
        assert share_token.totalSupply() == deploy_args[3] - redeem_amount
        assert share_token.balanceOf(issuer) == deploy_args[3] - lock_amount
        assert share_token.lockedOf(lock_address, issuer) == lock_amount - redeem_amount

    #######################################
    # Error
    #######################################

    # Error_1
    # Exceeds balance
    def test_error_1(self, users, IbetShare):
        issuer = users['issuer']
        redeem_amount = 101

        # issue token
        deploy_args = init_args()
        deploy_args[3] = 100
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # redeem
        with brownie.reverts():
            share_token.redeemFrom.transact(
                issuer,
                brownie.ZERO_ADDRESS,
                redeem_amount,
                {'from': issuer}
            )

        # assertion
        assert share_token.totalSupply() == deploy_args[3]
        assert share_token.balanceOf(issuer) == deploy_args[3]

    # Error_2
    # Exceeds locked quantity
    def test_error_2(self, users, IbetShare):
        issuer = users['issuer']
        lock_address = users['user1']
        lock_amount = 20
        redeem_amount = 21

        # issue token
        deploy_args = init_args()
        deploy_args[3] = 1000
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # authorize lock address
        share_token.authorize.transact(
            lock_address,
            True,
            {'from': issuer}
        )

        # lock
        share_token.lock.transact(
            lock_address,
            lock_amount,
            {'from': issuer}
        )

        # redeem from lock address
        with brownie.reverts():
            share_token.redeemFrom.transact(
                issuer,
                lock_address,
                redeem_amount,
                {'from': issuer}
            )

        # assertion
        assert share_token.totalSupply() == deploy_args[3]
        assert share_token.balanceOf(issuer) == deploy_args[3] - lock_amount
        assert share_token.lockedOf(lock_address, issuer) == lock_amount

    # Error_3
    # Not authorized
    def test_error_3(self, users, IbetShare):
        issuer = users['issuer']
        redeem_amount = 100

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # redeem
        with brownie.reverts():
            share_token.redeemFrom.transact(
                issuer,
                brownie.ZERO_ADDRESS,
                redeem_amount,
                {'from': users['user1']}
            )

        # assertion
        assert share_token.totalSupply() == deploy_args[3]
        assert share_token.balanceOf(issuer) == deploy_args[3]


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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )
        share_token.setTransferApprovalRequired(
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
        tx = share_token.applyForTransfer(
            to_address,
            transfer_amount,
            transfer_data,
            {"from": issuer}
        )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert share_token.balances(to_address) == 0
        assert share_token.pendingTransfer(issuer) == transfer_amount
        assert share_token.applicationsForTransfer(0) == (
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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )
        share_token.setTransferApprovalRequired(
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
            share_token.applyForTransfer(
                to_address,
                transfer_amount,
                transfer_data,
                {"from": issuer}
            )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - transfer_amount * 2
        assert share_token.balances(to_address) == 0
        assert share_token.pendingTransfer(issuer) == transfer_amount * 2
        for i in range(2):
            assert share_token.applicationsForTransfer(i) == (
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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )
        share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # apply for transfer
        share_token.applyForTransfer(
            to_address,
            transfer_amount,
            transfer_data,
            {"from": issuer}
        )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert share_token.pendingTransfer(issuer) == transfer_amount
        assert share_token.applicationsForTransfer(0) == (
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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=brownie.ZERO_ADDRESS
        )

        # apply for transfer
        with brownie.reverts():
            share_token.applyForTransfer(
                to_address,
                transfer_amount,
                transfer_data,
                {"from": issuer}
            )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3]
        assert share_token.balances(to_address) == 0
        assert share_token.pendingTransfer(issuer) == 0

    # Error_2
    # transferable = false
    def test_error_2(self, users):
        issuer = users["issuer"]
        to_address = users["user1"]
        transfer_amount = 100
        transfer_data = "test_data"

        # issue token
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=brownie.ZERO_ADDRESS
        )
        share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )
        share_token.setTransferable(
            False,
            {"from": issuer}
        )

        # apply for transfer
        with brownie.reverts():
            share_token.applyForTransfer(
                to_address,
                transfer_amount,
                transfer_data,
                {"from": issuer}
            )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3]
        assert share_token.balances(to_address) == 0
        assert share_token.pendingTransfer(issuer) == 0

    # Error_3
    # Insufficient balance
    def test_error_3(self, users):
        issuer = users["issuer"]
        to_address = users["user1"]
        transfer_data = "test_data"

        # issue token
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=brownie.ZERO_ADDRESS
        )
        share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # apply for transfer
        with brownie.reverts():
            share_token.applyForTransfer(
                to_address,
                deploy_args[3] + 1,
                transfer_data,
                {"from": issuer}
            )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3]
        assert share_token.balances(to_address) == 0
        assert share_token.pendingTransfer(issuer) == 0

    # Error_4
    # Personal information is not registered
    def test_error_4(self, users, personal_info):
        issuer = users["issuer"]
        to_address = users["user1"]
        transfer_amount = 100
        transfer_data = "test_data"

        # issue token
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )
        share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # apply for transfer
        with brownie.reverts():
            share_token.applyForTransfer(
                to_address,
                transfer_amount,
                transfer_data,
                {"from": issuer}
            )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3]
        assert share_token.balances(to_address) == 0
        assert share_token.pendingTransfer(issuer) == 0


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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )
        share_token.transferFrom(
            issuer,
            user1,
            transfer_amount,
            {"from": issuer}
        )
        share_token.setTransferApprovalRequired(
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
        share_token.applyForTransfer(
            user2,
            transfer_amount,
            "test_data",
            {"from": user1}  # from user1 to user2
        )

        # cancel transfer (from applicant)
        tx = share_token.cancelTransfer(
            0,
            "test_data",
            {"from": user1}
        )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert share_token.balances(user1) == transfer_amount
        assert share_token.pendingTransfer(user1) == 0
        assert share_token.applicationsForTransfer(0) == (
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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )
        share_token.transferFrom(
            issuer,
            user1,
            transfer_amount,
            {"from": issuer}
        )
        share_token.setTransferApprovalRequired(
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
        share_token.applyForTransfer(
            user2,
            transfer_amount,
            "test_data",
            {"from": user1}  # from user1 to user2
        )

        # cancel transfer (from issuer)
        tx = share_token.cancelTransfer(
            0,
            "test_data",
            {"from": issuer}
        )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert share_token.balances(user1) == transfer_amount
        assert share_token.pendingTransfer(user1) == 0
        assert share_token.applicationsForTransfer(0) == (
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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )
        share_token.transferFrom(
            issuer,
            user1,
            transfer_amount,
            {"from": issuer}
        )
        share_token.setTransferApprovalRequired(
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
        share_token.applyForTransfer(
            user2,
            transfer_amount,
            "test_data",
            {"from": user1}  # from user1 to user2
        )

        # cancel transfer (from issuer)
        with brownie.reverts():
            share_token.cancelTransfer(
                0,
                "test_data",
                {"from": user2}
            )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert share_token.balances(user1) == 0
        assert share_token.pendingTransfer(user1) == transfer_amount
        assert share_token.applicationsForTransfer(0) == (
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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )
        share_token.transferFrom(
            issuer,
            user1,
            transfer_amount,
            {"from": issuer}
        )
        share_token.setTransferApprovalRequired(
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
        share_token.applyForTransfer(
            user2,
            transfer_amount,
            "test_data",
            {"from": user1}  # from user1 to user2
        )

        # cancel transfer (1)
        share_token.cancelTransfer(
            0,
            "test_data",
            {"from": user1}
        )

        # cancel transfer (2)
        with brownie.reverts():
            share_token.cancelTransfer(
                0,
                "test_data",
                {"from": user1}
            )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert share_token.balances(user1) == transfer_amount
        assert share_token.pendingTransfer(user1) == 0
        assert share_token.applicationsForTransfer(0) == (
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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )
        share_token.setTransferApprovalRequired(
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
        share_token.applyForTransfer(
            user1,
            transfer_amount,
            "test_data",
            {"from": issuer}  # from issuer to user1
        )

        # approve transfer
        tx = share_token.approveTransfer(
            0,
            "test_data",
            {"from": issuer}
        )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert share_token.balances(user1) == transfer_amount
        assert share_token.pendingTransfer(issuer) == 0
        assert share_token.applicationsForTransfer(0) == (
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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )
        share_token.setTransferApprovalRequired(
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
        share_token.applyForTransfer(
            user1,
            transfer_amount,
            "test_data",
            {"from": issuer}  # from issuer to user1
        )

        # approve transfer
        with brownie.reverts():
            share_token.approveTransfer(
                0,
                "test_data",
                {"from": user1}
            )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert share_token.balances(user1) == 0
        assert share_token.pendingTransfer(issuer) == transfer_amount
        assert share_token.applicationsForTransfer(0) == (
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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )
        share_token.setTransferApprovalRequired(
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
        share_token.applyForTransfer(
            user1,
            transfer_amount,
            "test_data",
            {"from": issuer}  # from issuer to user1
        )

        # approve transfer
        share_token.setTransferable(
            False,
            {"from": issuer}
        )
        with brownie.reverts():
            share_token.approveTransfer(
                0,
                "test_data",
                {"from": issuer}
            )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert share_token.balances(user1) == 0
        assert share_token.pendingTransfer(issuer) == transfer_amount
        assert share_token.applicationsForTransfer(0) == (
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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )
        share_token.setTransferApprovalRequired(
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
        share_token.applyForTransfer(
            user1,
            transfer_amount,
            "test_data",
            {"from": issuer}  # from issuer to user1
        )

        # approve transfer (1)
        share_token.approveTransfer(
            0,
            "test_data",
            {"from": issuer}
        )

        # approve transfer (2)
        with brownie.reverts():
            share_token.approveTransfer(
                0,
                "test_data",
                {"from": issuer}
            )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - transfer_amount
        assert share_token.balances(user1) == transfer_amount
        assert share_token.pendingTransfer(issuer) == 0
        assert share_token.applicationsForTransfer(0) == (
            issuer,
            user1,
            transfer_amount,
            False
        )


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
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=brownie.ZERO_ADDRESS
        )

        # assertion
        assert share_token.transferApprovalRequired() == False

    # Normal_2
    def test_normal_2(self, users):
        issuer = users["issuer"]

        # issue token
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=brownie.ZERO_ADDRESS
        )

        # update
        tx = share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # assertion
        assert share_token.transferApprovalRequired() == True
        assert tx.events["ChangeTransferApprovalRequired"]["required"] == True

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, personal_info):
        issuer = users["issuer"]

        # issue token
        share_token, deploy_args = issue_transferable_share_token(
            issuer=issuer,
            exchange_address=brownie.ZERO_ADDRESS,
            personal_info_address=personal_info.address
        )

        # set required to True
        with brownie.reverts():
            share_token.setTransferApprovalRequired(
                True,
                {"from": users["user1"]}
            )

        # assertion
        assert share_token.transferApprovalRequired() == False


# TEST_Cancel
class TestCancel:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetShare):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # cancel
        share_token.cancel(
            {"from": issuer}
        )

        # assertion
        is_canceled = share_token.isCanceled()
        assert is_canceled is True

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetShare):
        issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # cancel
        with brownie.reverts():
            share_token.cancel(
                {"from": users["user1"]}
            )

        # assertion
        is_canceled = share_token.isCanceled()
        assert is_canceled is False


# TEST_setStatus
class TestSetStatus:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # update
        share_token.setStatus(False, {'from': issuer})

        # assertion
        assert share_token.status() is False

    #######################################
    # Error
    #######################################

    # Error_1
    # Not authorized
    def test_error_1(self, users, IbetShare):
        issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        share_token = issuer.deploy(IbetShare, *deploy_args)

        # change exchange contract
        with brownie.reverts():
            share_token.setStatus(False, {'from': users['user1']})
