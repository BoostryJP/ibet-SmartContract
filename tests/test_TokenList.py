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


deploy_args = [
    'test_share',  # name
    'test_symbol',  # symbol
    100000,  # total supply
    brownie.ZERO_ADDRESS,  # tradable exchange
    'test_contact_information',
    'test_privacy_policy'
]


# TEST_register
class TestRegister:

    #######################################
    # Normal
    #######################################
    
    # Normal_1
    def test_normal_1(self, users, TokenList, IbetStandardToken):
        admin = users['admin']
        issuer = users['issuer']
    
        # deploy
        token_list = admin.deploy(TokenList)
    
        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list
        tx = token_list.register.transact(
            token.address,
            'IbetStandardToken',
            {'from': issuer}
        )

        # assertion
        assert token_list.tokens(token.address) == (
            token.address,
            'IbetStandardToken',
            issuer.address
        )

        assert token_list.token_list(0) == (
            token.address,
            'IbetStandardToken',
            issuer.address
        )

        assert tx.events["Register"]["token_address"] == token.address
        assert tx.events["Register"]["token_template"] == 'IbetStandardToken'
        assert tx.events["Register"]["owner_address"] == issuer.address

    #######################################
    # Error
    #######################################

    # Error_1
    # Registration can be done only once.
    def test_error_1(self, users, TokenList, IbetStandardToken):
        admin = users['admin']
        issuer = users['issuer']

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list (1)
        token_list.register.transact(
            token.address,
            'IbetStandardToken',
            {'from': issuer}
        )

        # register to list (2)
        with brownie.reverts():
            token_list.register.transact(
                token.address,
                'IbetStandardToken',
                {'from': issuer}
            )

    # Error_2
    # Not authorized
    def test_error_2(self, users, TokenList, IbetStandardToken):
        admin = users['admin']
        issuer = users['issuer']

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list
        with brownie.reverts():
            token_list.register.transact(
                token.address,
                'IbetStandardToken',
                {'from': users["user1"]}
            )


# TEST_changeOwner
class TestChangeOwner:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, TokenList, IbetStandardToken):
        admin = users['admin']
        issuer = users['issuer']
        new_owner = users['user1']

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list
        token_list.register.transact(
            token.address,
            'IbetStandardToken',
            {'from': issuer}
        )

        # change token owner
        token_list.changeOwner.transact(
            token.address,
            new_owner.address,
            {'from': issuer}
        )

        # assertion
        assert token_list.tokens(token.address) == (
            token.address,
            'IbetStandardToken',
            new_owner.address
        )

        assert token_list.token_list(0) == (
            token.address,
            'IbetStandardToken',
            new_owner.address
        )

    #######################################
    # Error
    #######################################

    # Error_1
    # Not registered
    def test_error_1(self, users, TokenList, IbetStandardToken):
        admin = users['admin']
        issuer = users['issuer']
        new_owner = users['user1']

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # change token owner
        with brownie.reverts():
            token_list.changeOwner.transact(
                token.address,
                new_owner.address,
                {'from': issuer}
            )

        # assertion
        assert token_list.tokens(token.address) == (
            brownie.ZERO_ADDRESS,
            '',
            brownie.ZERO_ADDRESS
        )

    # Error_2
    # Not authorized
    def test_error_2(self, users, TokenList, IbetStandardToken):
        admin = users['admin']
        issuer = users['issuer']
        new_owner = users['user1']

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list
        token_list.register.transact(
            token.address,
            'IbetStandardToken',
            {'from': issuer}
        )

        # change token owner
        with brownie.reverts():
            token_list.changeOwner.transact(
                token.address,
                new_owner.address,
                {'from': new_owner}
            )

        # assertion
        assert token_list.tokens(token.address) == (
            token.address,
            'IbetStandardToken',
            issuer.address
        )

        assert token_list.token_list(0) == (
            token.address,
            'IbetStandardToken',
            issuer.address
        )


# TEST_getOwnerAddress
class TestGetOwnerAddress:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, TokenList, IbetStandardToken):
        admin = users['admin']
        issuer = users['issuer']

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list
        token_list.register.transact(
            token.address,
            'IbetStandardToken',
            {'from': issuer}
        )

        # assertion
        assert token_list.getOwnerAddress(token.address) == issuer.address


# TEST_getListLength
class TestGetListLength:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, TokenList, IbetStandardToken):
        admin = users['admin']
        issuer = users['issuer']

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list
        token_list.register.transact(
            token.address,
            'IbetStandardToken',
            {'from': issuer}
        )

        # assertion
        assert token_list.getListLength() == 1


# TEST_getTokenByNum
class TestGetTokenByNum:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, TokenList, IbetStandardToken):
        admin = users['admin']
        issuer = users['issuer']

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list
        token_list.register.transact(
            token.address,
            'IbetStandardToken',
            {'from': issuer}
        )

        # assertion
        assert token_list.getTokenByNum(0) == (
            token.address,
            'IbetStandardToken',
            issuer.address
        )


# TEST_getTokenByAddress
class TestGetTokenByAddress:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, TokenList, IbetStandardToken):
        admin = users['admin']
        issuer = users['issuer']

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list
        token_list.register.transact(
            token.address,
            'IbetStandardToken',
            {'from': issuer}
        )

        # assertion
        assert token_list.getTokenByAddress(token.address) == (
            token.address,
            'IbetStandardToken',
            issuer.address
        )
