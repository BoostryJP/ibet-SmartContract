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


class TestSendMessage:
    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, SnapMessaging, users):
        admin = users["admin"]
        sender = users["user1"]
        receiver = users["user2"]

        test_message = "test_message"

        # Deploy contract
        snap_messaging = admin.deploy(SnapMessaging)

        # Send message
        tx = snap_messaging.sendMessage.transact(
            receiver, test_message, {"from": sender}
        )

        # Assertion
        assert tx.events["Message"]["sender"] == sender
        assert tx.events["Message"]["receiver"] == receiver
        assert tx.events["Message"]["time"] is not None
        assert tx.events["Message"]["text"] == test_message
