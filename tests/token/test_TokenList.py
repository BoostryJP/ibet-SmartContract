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

from ape_utils import ZERO_ADDRESS, event_args, reverts

deploy_args = [
    "test_share",  # name
    "test_symbol",  # symbol
    100000,  # total supply
    ZERO_ADDRESS,  # tradable exchange
    "test_contact_information",
    "test_privacy_policy",
]


# TEST_register
class TestRegister:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, TokenList, IbetStandardToken):
        admin = users["admin"]
        issuer = users["issuer"]

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list
        tx = token_list.register(token.address, "IbetStandardToken", sender=issuer)

        # assertion
        assert token_list.tokens(token.address) == (
            token.address,
            "IbetStandardToken",
            issuer.address,
        )

        assert token_list.token_list(0) == (
            token.address,
            "IbetStandardToken",
            issuer.address,
        )

        event = event_args(tx, token_list.Register)
        assert event["token_address"] == token.address
        assert event["token_template"] == "IbetStandardToken"
        assert event["owner_address"] == issuer.address

    #######################################
    # Error
    #######################################

    # Error_1
    # Registration can be done only once.
    def test_error_1(self, users, TokenList, IbetStandardToken):
        admin = users["admin"]
        issuer = users["issuer"]

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list (1)
        token_list.register(token.address, "IbetStandardToken", sender=issuer)

        # register to list (2)
        with reverts("100001"):
            token_list.register(token.address, "IbetStandardToken", sender=issuer)

    # Error_2
    # Not authorized
    def test_error_2(self, users, TokenList, IbetStandardToken):
        admin = users["admin"]
        issuer = users["issuer"]

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list
        with reverts("100002"):
            token_list.register(
                token.address, "IbetStandardToken", sender=users["user1"]
            )


# TEST_changeOwner
class TestChangeOwner:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, TokenList, IbetStandardToken):
        admin = users["admin"]
        issuer = users["issuer"]
        new_owner = users["user1"]

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list
        token_list.register(token.address, "IbetStandardToken", sender=issuer)

        # change token owner
        token_list.changeOwner(token.address, new_owner.address, sender=issuer)

        # assertion
        assert token_list.tokens(token.address) == (
            token.address,
            "IbetStandardToken",
            new_owner.address,
        )

        assert token_list.token_list(0) == (
            token.address,
            "IbetStandardToken",
            new_owner.address,
        )

    #######################################
    # Error
    #######################################

    # Error_1
    # Not registered
    def test_error_1(self, users, TokenList, IbetStandardToken):
        admin = users["admin"]
        issuer = users["issuer"]
        new_owner = users["user1"]

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # change token owner
        with reverts("100101"):
            token_list.changeOwner(token.address, new_owner.address, sender=issuer)

        # assertion
        assert token_list.tokens(token.address) == (
            ZERO_ADDRESS,
            "",
            ZERO_ADDRESS,
        )

    # Error_2
    # Not authorized
    def test_error_2(self, users, TokenList, IbetStandardToken):
        admin = users["admin"]
        issuer = users["issuer"]
        new_owner = users["user1"]

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list
        token_list.register(token.address, "IbetStandardToken", sender=issuer)

        # change token owner
        with reverts("100102"):
            token_list.changeOwner(token.address, new_owner.address, sender=new_owner)

        # assertion
        assert token_list.tokens(token.address) == (
            token.address,
            "IbetStandardToken",
            issuer.address,
        )

        assert token_list.token_list(0) == (
            token.address,
            "IbetStandardToken",
            issuer.address,
        )


# TEST_getOwnerAddress
class TestGetOwnerAddress:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, TokenList, IbetStandardToken):
        admin = users["admin"]
        issuer = users["issuer"]

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list
        token_list.register(token.address, "IbetStandardToken", sender=issuer)

        # assertion
        assert token_list.getOwnerAddress(token.address) == issuer.address


# TEST_getListLength
class TestGetListLength:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, TokenList, IbetStandardToken):
        admin = users["admin"]
        issuer = users["issuer"]

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list
        token_list.register(token.address, "IbetStandardToken", sender=issuer)

        # assertion
        assert token_list.getListLength() == 1


# TEST_getTokenByNum
class TestGetTokenByNum:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, TokenList, IbetStandardToken):
        admin = users["admin"]
        issuer = users["issuer"]

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list
        token_list.register(token.address, "IbetStandardToken", sender=issuer)

        # assertion
        assert token_list.getTokenByNum(0) == (
            token.address,
            "IbetStandardToken",
            issuer.address,
        )


# TEST_getTokenByAddress
class TestGetTokenByAddress:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, TokenList, IbetStandardToken):
        admin = users["admin"]
        issuer = users["issuer"]

        # deploy
        token_list = admin.deploy(TokenList)

        # issue token
        token = issuer.deploy(IbetStandardToken, *deploy_args)

        # register to list
        token_list.register(token.address, "IbetStandardToken", sender=issuer)

        # assertion
        assert token_list.getTokenByAddress(token.address) == (
            token.address,
            "IbetStandardToken",
            issuer.address,
        )
