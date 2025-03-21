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


class TestSendMessage:
    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, E2EMessaging, users):
        admin = users["admin"]
        sender = users["user1"]
        receiver = users["user2"]

        test_message = "test_message"

        # Deploy contract
        e2e_messaging = admin.deploy(E2EMessaging)

        # Send message
        tx = e2e_messaging.sendMessage.transact(
            receiver, test_message, {"from": sender}
        )

        # Assertion
        assert tx.events["Message"]["sender"] == sender
        assert tx.events["Message"]["receiver"] == receiver
        assert tx.events["Message"]["text"] == test_message

        last_msg_index = e2e_messaging.last_msg_index(receiver)
        assert last_msg_index == 1

        message = e2e_messaging.messages(receiver, 0)
        assert message[0] == sender
        assert message[1] == test_message
        assert message[2] == tx.events["Message"]["time"]

    # Normal_2
    # Send twice
    def test_normal_2(self, E2EMessaging, users):
        admin = users["admin"]
        sender = users["user1"]
        receiver = users["user2"]

        test_message_1 = "test_message_1"
        test_message_2 = "test_message_2"

        # Deploy contract
        e2e_messaging = admin.deploy(E2EMessaging)

        # Send message (1)
        tx1 = e2e_messaging.sendMessage.transact(
            receiver, test_message_1, {"from": sender}
        )

        # Send message (2)
        tx2 = e2e_messaging.sendMessage.transact(
            receiver, test_message_2, {"from": sender}
        )

        # Assertion
        assert tx1.events["Message"]["sender"] == sender
        assert tx1.events["Message"]["receiver"] == receiver
        assert tx1.events["Message"]["text"] == test_message_1

        assert tx2.events["Message"]["sender"] == sender
        assert tx2.events["Message"]["receiver"] == receiver
        assert tx2.events["Message"]["text"] == test_message_2

        last_msg_index = e2e_messaging.last_msg_index(receiver)
        assert last_msg_index == 2

        message_1 = e2e_messaging.messages(receiver, 0)
        assert message_1[0] == sender
        assert message_1[1] == test_message_1
        assert message_1[2] == tx1.events["Message"]["time"]

        message_2 = e2e_messaging.messages(receiver, 1)
        assert message_2[0] == sender
        assert message_2[1] == test_message_2
        assert message_2[2] == tx2.events["Message"]["time"]


class TestLastIndex:
    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, E2EMessaging, users):
        admin = users["admin"]
        sender = users["user1"]
        receiver = users["user2"]

        test_message = "test_message"

        # Deploy contract
        e2e_messaging = admin.deploy(E2EMessaging)

        last_msg_index_before = e2e_messaging.last_msg_index(receiver)

        # Send message
        e2e_messaging.sendMessage.transact(receiver, test_message, {"from": sender})

        # Assertion
        assert last_msg_index_before == 0
        last_msg_index_after = e2e_messaging.last_msg_index(receiver)
        assert last_msg_index_after == 1


class TestGetLastMessage:
    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, E2EMessaging, users):
        admin = users["admin"]
        sender = users["user1"]
        receiver = users["user2"]

        test_message = "test_message"

        # Deploy contract
        e2e_messaging = admin.deploy(E2EMessaging)

        # Send message
        tx = e2e_messaging.sendMessage.transact(
            receiver, test_message, {"from": sender}
        )

        # Assertion
        message = e2e_messaging.getLastMessage(receiver)
        assert message[0] == sender
        assert message[1] == test_message
        assert message[2] == tx.events["Message"]["time"]

    # Normal_2
    # Send twice
    def test_normal_2(self, E2EMessaging, users):
        admin = users["admin"]
        sender = users["user1"]
        receiver = users["user2"]

        test_message_1 = "test_message_1"
        test_message_2 = "test_message_2"

        # Deploy contract
        e2e_messaging = admin.deploy(E2EMessaging)

        # Send message (1)
        e2e_messaging.sendMessage.transact(receiver, test_message_1, {"from": sender})

        # Send message (2)
        tx = e2e_messaging.sendMessage.transact(
            receiver, test_message_2, {"from": sender}
        )

        # Assertion
        message = e2e_messaging.getLastMessage(receiver)
        assert message[0] == sender
        assert message[1] == test_message_2
        assert message[2] == tx.events["Message"]["time"]

    ##########################################################
    # Error
    ##########################################################

    # Normal_1
    # last message index == 0
    def test_error_1(self, E2EMessaging, users):
        admin = users["admin"]
        receiver = users["user2"]

        # Deploy contract
        e2e_messaging = admin.deploy(E2EMessaging)

        # Assertion
        with pytest.raises(ValueError):
            e2e_messaging.getLastMessage(receiver)


class TestGetMessageByIndex:
    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, E2EMessaging, users):
        admin = users["admin"]
        sender = users["user1"]
        receiver = users["user2"]

        test_message = "test_message"

        # Deploy contract
        e2e_messaging = admin.deploy(E2EMessaging)

        # Send message
        tx = e2e_messaging.sendMessage.transact(
            receiver, test_message, {"from": sender}
        )

        # Assertion
        message = e2e_messaging.getMessageByIndex(receiver, 0)
        assert message[0] == sender
        assert message[1] == test_message
        assert message[2] == tx.events["Message"]["time"]

    # Normal_2
    # Send twice
    def test_normal_2(self, E2EMessaging, users):
        admin = users["admin"]
        sender = users["user1"]
        receiver = users["user2"]

        test_message_1 = "test_message_1"
        test_message_2 = "test_message_2"

        # Deploy contract
        e2e_messaging = admin.deploy(E2EMessaging)

        # Send message (1)
        tx1 = e2e_messaging.sendMessage.transact(
            receiver, test_message_1, {"from": sender}
        )

        # Send message (2)
        tx2 = e2e_messaging.sendMessage.transact(
            receiver, test_message_2, {"from": sender}
        )

        # Assertion
        message = e2e_messaging.getMessageByIndex(receiver, 0)
        assert message[0] == sender
        assert message[1] == test_message_1
        assert message[2] == tx1.events["Message"]["time"]

        message = e2e_messaging.getMessageByIndex(receiver, 1)
        assert message[0] == sender
        assert message[1] == test_message_2
        assert message[2] == tx2.events["Message"]["time"]

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    # Unregistered index
    def test_error_1(self, E2EMessaging, users):
        admin = users["admin"]
        receiver = users["user2"]

        # Deploy contract
        e2e_messaging = admin.deploy(E2EMessaging)

        # Assertion
        message = e2e_messaging.getMessageByIndex(receiver, 1)
        assert message[0] == brownie.ZERO_ADDRESS
        assert message[1] == ""
        assert message[2] == 0


class TestClearMessage:
    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, E2EMessaging, users):
        admin = users["admin"]
        sender = users["user1"]
        receiver = users["user2"]

        test_message = "test_message"

        # Deploy contract
        e2e_messaging = admin.deploy(E2EMessaging)

        # Send message
        tx1 = e2e_messaging.sendMessage.transact(
            receiver, test_message, {"from": sender}
        )

        # Clear message
        latest_index = e2e_messaging.last_msg_index(receiver)
        tx2 = e2e_messaging.clearMessage.transact(
            receiver, latest_index - 1, {"from": sender}
        )

        # Assertion
        assert tx2.events["MessageCleared"]["sender"] == sender
        assert tx2.events["MessageCleared"]["receiver"] == receiver
        assert tx2.events["MessageCleared"]["index"] == latest_index - 1

        message = e2e_messaging.messages(receiver, latest_index - 1)
        assert message[0] == sender
        assert message[1] == ""
        assert message[2] == tx1.events["Message"]["time"]

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    # msg.sender must be the sender of the message.
    def test_error_1(self, E2EMessaging, users):
        admin = users["admin"]
        sender = users["user1"]
        receiver = users["user2"]

        test_message = "test_message"

        # Deploy contract
        e2e_messaging = admin.deploy(E2EMessaging)

        # Send message
        tx1 = e2e_messaging.sendMessage.transact(
            receiver, test_message, {"from": sender}
        )

        # Clear message
        latest_index = e2e_messaging.last_msg_index(receiver)
        with brownie.reverts(revert_msg="610101"):
            e2e_messaging.clearMessage.transact(
                receiver, latest_index - 1, {"from": receiver}
            )

        message = e2e_messaging.messages(receiver, latest_index - 1)
        assert message[0] == sender
        assert message[1] == test_message
        assert message[2] == tx1.events["Message"]["time"]


class TestGetPublicKey:
    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, E2EMessaging, users):
        admin = users["admin"]
        who = users["user1"]

        # Deploy contract
        e2e_messaging = admin.deploy(E2EMessaging)

        # Set public key
        e2e_messaging.setPublicKey.transact("test_key", "test_key_type", {"from": who})

        # Assertion
        public_key = e2e_messaging.getPublicKey(who)
        assert public_key[0] == "test_key"
        assert public_key[1] == "test_key_type"


class TestSetPublicKey:
    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, E2EMessaging, users):
        admin = users["admin"]
        who = users["user1"]

        # Deploy contract
        e2e_messaging = admin.deploy(E2EMessaging)

        # Set public key
        tx = e2e_messaging.setPublicKey.transact(
            "test_key", "test_key_type", {"from": who}
        )

        # Assertion
        public_key = e2e_messaging.getPublicKey(who)
        assert public_key[0] == "test_key"
        assert public_key[1] == "test_key_type"

        assert tx.events["PublicKeyUpdated"]["who"] == who
        assert tx.events["PublicKeyUpdated"]["key"] == "test_key"
        assert tx.events["PublicKeyUpdated"]["key_type"] == "test_key_type"

    # Normal_2
    # Set twice
    def test_normal_2(self, E2EMessaging, users):
        admin = users["admin"]
        who = users["user1"]

        # Deploy contract
        e2e_messaging = admin.deploy(E2EMessaging)

        # Set public key (1)
        e2e_messaging.setPublicKey.transact(
            "test_key_1", "test_key_type_1", {"from": who}
        )

        # Set public key (2)
        e2e_messaging.setPublicKey.transact(
            "test_key_2", "test_key_type_2", {"from": who}
        )

        # Assertion
        public_key = e2e_messaging.getPublicKey(who)
        assert public_key[0] == "test_key_2"
        assert public_key[1] == "test_key_type_2"
