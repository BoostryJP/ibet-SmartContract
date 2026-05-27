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

encrypted_message = "encrypted_message"
encrypted_message_after = "encrypted_message_after"


# TEST_register
class TestRegister:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, personal_info):
        account = users["trader"]
        link = users["issuer"]

        # register
        tx = personal_info.register(link, encrypted_message, sender=account)

        # assertion
        registered_personal_info = personal_info.personal_info(account, link)
        assert registered_personal_info[0] == account
        assert registered_personal_info[1] == link
        assert registered_personal_info[2] == encrypted_message

        is_registered = personal_info.isRegistered(account, link)
        assert is_registered is True

        event = event_args(tx, personal_info.Register)
        assert event["account_address"] == account.address
        assert event["link_address"] == link.address

    # Normal_2
    # Update
    def test_normal_2(self, users, personal_info):
        account = users["trader"]
        link = users["issuer"]

        # register 1
        personal_info.register(link.address, encrypted_message, sender=account)

        # register 2
        personal_info.register(link, encrypted_message_after, sender=account)

        # assertion
        registered_personal_info = personal_info.personal_info(account, link)
        assert registered_personal_info[0] == account
        assert registered_personal_info[1] == link
        assert registered_personal_info[2] == encrypted_message_after

        is_registered = personal_info.isRegistered(account, link)
        assert is_registered is True


# TEST_isRegistered
class TestIsRegistered:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Default value
    def test_normal_1(self, users, personal_info):
        account = users["trader"]
        link = users["issuer"]

        # assertion
        is_registered = personal_info.isRegistered(account, link)
        assert is_registered is False

    # Normal_2
    def test_normal_2(self, users, personal_info):
        account = users["trader"]
        link = users["issuer"]

        # register
        personal_info.register(link, encrypted_message, sender=account)

        # assertion
        is_registered = personal_info.isRegistered(account, link)
        assert is_registered is True


# TEST_modify
class TestModify:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, personal_info):
        account = users["trader"]
        link = users["issuer"]

        # register
        personal_info.register(link, encrypted_message, sender=account)

        # modify
        tx = personal_info.modify(account, encrypted_message_after, sender=link)

        # assertion
        modified_personal_info = personal_info.personal_info(account, link)
        assert modified_personal_info[0] == account
        assert modified_personal_info[1] == link
        assert modified_personal_info[2] == encrypted_message_after

        event = event_args(tx, personal_info.Modify)
        assert event["account_address"] == account.address
        assert event["link_address"] == link.address

    #######################################
    # Error
    #######################################

    # Error_1
    # Not registered
    def test_error_1(self, users, personal_info):
        account = users["trader"]
        link = users["issuer"]

        # modify
        with reverts("400001"):
            personal_info.modify(account, encrypted_message_after, sender=link)

        # assertion
        actual_personal_info = personal_info.personal_info(account, link)
        assert actual_personal_info[0] == ZERO_ADDRESS
        assert actual_personal_info[1] == ZERO_ADDRESS
        assert actual_personal_info[2] == ""

        is_registered = personal_info.isRegistered(account, link)
        assert is_registered is False

    # Error_2
    # Not authorized
    def test_error_2(self, users, personal_info):
        account = users["trader"]
        link = users["issuer"]
        modifier = users["admin"]

        # register
        personal_info.register(link, encrypted_message, sender=account)

        # modify
        with reverts("400001"):
            personal_info.modify(account, encrypted_message_after, sender=modifier)

        # assertion
        actual_personal_info = personal_info.personal_info(account, link)
        assert actual_personal_info[0] == account
        assert actual_personal_info[1] == link
        assert actual_personal_info[2] == encrypted_message


# TEST_forceRegister
class TestForceRegister:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, personal_info):
        account = users["trader"]
        link = users["issuer"]

        # register
        tx = personal_info.forceRegister(
            account.address, encrypted_message, sender=link
        )

        # assertion
        registered_personal_info = personal_info.personal_info(account, link)
        assert registered_personal_info[0] == account
        assert registered_personal_info[1] == link
        assert registered_personal_info[2] == encrypted_message

        is_registered = personal_info.isRegistered(account, link)
        assert is_registered is True

        event = event_args(tx, personal_info.Register)
        assert event["account_address"] == account.address
        assert event["link_address"] == link.address

    # Normal_2
    # Update
    def test_normal_2(self, users, personal_info):
        account = users["trader"]
        link = users["issuer"]

        # register 1
        personal_info.forceRegister(account.address, encrypted_message, sender=link)

        # register 2
        personal_info.forceRegister(
            account.address, encrypted_message_after, sender=link
        )

        # assertion
        registered_personal_info = personal_info.personal_info(account, link)
        assert registered_personal_info[0] == account
        assert registered_personal_info[1] == link
        assert registered_personal_info[2] == encrypted_message_after

        is_registered = personal_info.isRegistered(account, link)
        assert is_registered is True
