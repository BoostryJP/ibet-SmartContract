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

from ape_utils import ZERO_ADDRESS, call_view_method, event_args, reverts


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
        tx = e2e_messaging.sendMessage(receiver, test_message, sender=sender)

        # Assertion
        event = event_args(tx, e2e_messaging.Message)
        assert event["sender"] == sender
        assert event["receiver"] == receiver
        assert event["text"] == test_message

        last_msg_index = e2e_messaging.last_msg_index(receiver)
        assert last_msg_index == 1

        message = call_view_method(e2e_messaging, "messages", receiver, 0)
        assert message[0] == sender
        assert message[1] == test_message
        assert message[2] == event["time"]

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
        tx1 = e2e_messaging.sendMessage(receiver, test_message_1, sender=sender)

        # Send message (2)
        tx2 = e2e_messaging.sendMessage(receiver, test_message_2, sender=sender)

        # Assertion
        event_1 = event_args(tx1, e2e_messaging.Message)
        assert event_1["sender"] == sender
        assert event_1["receiver"] == receiver
        assert event_1["text"] == test_message_1

        event_2 = event_args(tx2, e2e_messaging.Message)
        assert event_2["sender"] == sender
        assert event_2["receiver"] == receiver
        assert event_2["text"] == test_message_2

        last_msg_index = e2e_messaging.last_msg_index(receiver)
        assert last_msg_index == 2

        message_1 = call_view_method(e2e_messaging, "messages", receiver, 0)
        assert message_1[0] == sender
        assert message_1[1] == test_message_1
        assert message_1[2] == event_1["time"]

        message_2 = call_view_method(e2e_messaging, "messages", receiver, 1)
        assert message_2[0] == sender
        assert message_2[1] == test_message_2
        assert message_2[2] == event_2["time"]


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
        e2e_messaging.sendMessage(receiver, test_message, sender=sender)

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
        tx = e2e_messaging.sendMessage(receiver, test_message, sender=sender)

        # Assertion
        message = call_view_method(e2e_messaging, "getLastMessage", receiver)
        assert message[0] == sender
        assert message[1] == test_message
        event = event_args(tx, e2e_messaging.Message)
        assert message[2] == event["time"]

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
        e2e_messaging.sendMessage(receiver, test_message_1, sender=sender)

        # Send message (2)
        tx = e2e_messaging.sendMessage(receiver, test_message_2, sender=sender)

        # Assertion
        message = call_view_method(e2e_messaging, "getLastMessage", receiver)
        assert message[0] == sender
        assert message[1] == test_message_2
        event = event_args(tx, e2e_messaging.Message)
        assert message[2] == event["time"]

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
        with reverts("610001"):
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
        tx = e2e_messaging.sendMessage(receiver, test_message, sender=sender)

        # Assertion
        message = call_view_method(e2e_messaging, "getMessageByIndex", receiver, 0)
        assert message[0] == sender
        assert message[1] == test_message
        event = event_args(tx, e2e_messaging.Message)
        assert message[2] == event["time"]

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
        tx1 = e2e_messaging.sendMessage(receiver, test_message_1, sender=sender)

        # Send message (2)
        tx2 = e2e_messaging.sendMessage(receiver, test_message_2, sender=sender)

        # Assertion
        message = call_view_method(e2e_messaging, "getMessageByIndex", receiver, 0)
        assert message[0] == sender
        assert message[1] == test_message_1
        event_1 = event_args(tx1, e2e_messaging.Message)
        assert message[2] == event_1["time"]

        message = call_view_method(e2e_messaging, "getMessageByIndex", receiver, 1)
        assert message[0] == sender
        assert message[1] == test_message_2
        event_2 = event_args(tx2, e2e_messaging.Message)
        assert message[2] == event_2["time"]

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
        message = call_view_method(e2e_messaging, "getMessageByIndex", receiver, 1)
        assert message[0] == ZERO_ADDRESS
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
        tx1 = e2e_messaging.sendMessage(receiver, test_message, sender=sender)

        # Clear message
        latest_index = e2e_messaging.last_msg_index(receiver)
        tx2 = e2e_messaging.clearMessage(receiver, latest_index - 1, sender=sender)

        # Assertion
        event = event_args(tx2, e2e_messaging.MessageCleared)
        assert event["sender"] == sender
        assert event["receiver"] == receiver
        assert event["index"] == latest_index - 1

        message = call_view_method(
            e2e_messaging, "messages", receiver, latest_index - 1
        )
        created_event = event_args(tx1, e2e_messaging.Message)
        assert message[0] == sender
        assert message[1] == ""
        assert message[2] == created_event["time"]

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
        tx1 = e2e_messaging.sendMessage(receiver, test_message, sender=sender)

        # Clear message
        latest_index = e2e_messaging.last_msg_index(receiver)
        with reverts("610101"):
            e2e_messaging.clearMessage(receiver, latest_index - 1, sender=receiver)

        message = call_view_method(
            e2e_messaging, "messages", receiver, latest_index - 1
        )
        event = event_args(tx1, e2e_messaging.Message)
        assert message[0] == sender
        assert message[1] == test_message
        assert message[2] == event["time"]


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
        e2e_messaging.setPublicKey("test_key", "test_key_type", sender=who)

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
        tx = e2e_messaging.setPublicKey("test_key", "test_key_type", sender=who)

        # Assertion
        public_key = e2e_messaging.getPublicKey(who)
        assert public_key[0] == "test_key"
        assert public_key[1] == "test_key_type"

        event = event_args(tx, e2e_messaging.PublicKeyUpdated)
        assert event["who"] == who
        assert event["key"] == "test_key"
        assert event["key_type"] == "test_key_type"

    # Normal_2
    # Set twice
    def test_normal_2(self, E2EMessaging, users):
        admin = users["admin"]
        who = users["user1"]

        # Deploy contract
        e2e_messaging = admin.deploy(E2EMessaging)

        # Set public key (1)
        e2e_messaging.setPublicKey("test_key_1", "test_key_type_1", sender=who)

        # Set public key (2)
        e2e_messaging.setPublicKey("test_key_2", "test_key_type_2", sender=who)

        # Assertion
        public_key = e2e_messaging.getPublicKey(who)
        assert public_key[0] == "test_key_2"
        assert public_key[1] == "test_key_type_2"
