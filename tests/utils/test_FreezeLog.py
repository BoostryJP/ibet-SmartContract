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

from ape_utils import event_args, reverts


class TestRecordLog:
    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    # Add a record once.
    def test_normal_1(self, FreezeLog, users, web3):
        admin = users["admin"]
        user = users["user1"]

        # Deploy contract
        freeze_log = admin.deploy(FreezeLog)
        test_block = web3.eth.block_number + 1
        test_message = "test_message"
        test_freezing_grace_block_count = 5

        # Record Log
        tx = freeze_log.recordLog(
            test_message, test_freezing_grace_block_count, sender=user
        )

        # Assertion
        event = event_args(tx, freeze_log.Recorded)
        assert event["recorder"] == user

        log = freeze_log.getLog(user.address, 0, sender=user)
        assert log == (test_block, test_freezing_grace_block_count, test_message)

    # Normal_2
    # 2 person add a record each.
    def test_normal_2(self, FreezeLog, users, web3):
        admin = users["admin"]
        user1 = users["user1"]
        user2 = users["user2"]

        # Deploy contract
        freeze_log = admin.deploy(FreezeLog)
        test_block = web3.eth.block_number + 1
        test_message = "test_message"
        test_freezing_grace_block_count = 5

        # Record Log
        tx = freeze_log.recordLog(
            test_message, test_freezing_grace_block_count, sender=user1
        )

        # Assertion
        event = event_args(tx, freeze_log.Recorded)
        assert event["recorder"] == user1.address
        log = freeze_log.getLog(user1.address, 0, sender=user1)
        assert log == (test_block, test_freezing_grace_block_count, test_message)

        # Deploy contract
        freeze_log = admin.deploy(FreezeLog)
        test_block = web3.eth.block_number + 1
        test_message = "test_message"
        test_freezing_grace_block_count = 5

        # Record Log
        tx = freeze_log.recordLog(
            test_message, test_freezing_grace_block_count, sender=user2
        )

        # Assertion
        event = event_args(tx, freeze_log.Recorded)
        assert event["recorder"] == user2.address
        log = freeze_log.getLog(user2.address, 0, sender=user2)
        assert log == (test_block, test_freezing_grace_block_count, test_message)


class TestLastLogIndex:
    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    # Get last_log_index after adding a record.
    def test_normal_1(self, FreezeLog, users, web3):
        admin = users["admin"]
        user1 = users["user1"]
        user2 = users["user2"]
        # Deploy contract
        freeze_log = admin.deploy(FreezeLog)
        test_message = "test_message"
        test_freezing_grace_block_count = 5

        # Record Log
        freeze_log.recordLog(
            test_message, test_freezing_grace_block_count, sender=user1
        )

        # get last_log_index of user1
        user1_last_log_index = freeze_log.lastLogIndex(user1, sender=user2)
        assert user1_last_log_index == 1
        # get last_log_index of user2
        user2_last_log_index = freeze_log.lastLogIndex(user2, sender=user2)
        assert user2_last_log_index == 0


class TestUpdateLog:
    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    # After added a record, updating the record message.
    def test_normal_1(self, FreezeLog, users, web3):
        admin = users["admin"]
        user = users["user1"]

        # Deploy contract
        freeze_log = admin.deploy(FreezeLog)
        test_block = web3.eth.block_number + 1
        test_message = "test_message"
        test_freezing_grace_block_count = 5

        # Record Log
        tx = freeze_log.recordLog(
            test_message, test_freezing_grace_block_count, sender=user
        )
        # Assertion
        event = event_args(tx, freeze_log.Recorded)
        assert event["recorder"] == user

        user_last_log_index = freeze_log.lastLogIndex(user, sender=user)

        tx = freeze_log.updateLog(
            user_last_log_index - 1, test_message[::-1], sender=user
        )

        # Assertion
        event = event_args(tx, freeze_log.Updated)
        assert event["recorder"] == user
        assert event["index"] == user_last_log_index - 1

        log = freeze_log.getLog(user.address, user_last_log_index - 1, sender=user)
        assert log[0] == test_block
        assert log[1] == test_freezing_grace_block_count
        assert log[2] == test_message[::-1]

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    # Trying to update log of non-existent index, but fail.
    def test_error_1(self, FreezeLog, users, web3):
        admin = users["admin"]
        user1 = users["user1"]

        # Deploy contract
        freeze_log = admin.deploy(FreezeLog)

        test_idx = 10
        test_message = "test1 message"
        with reverts("620001"):
            freeze_log.updateLog(test_idx, test_message, sender=user1)
        log = freeze_log.getLog(user1.address, 0, sender=user1)
        assert log == (0, 0, "")

    # Error_2
    # Trying to update a frozen log, but fail.
    def test_error_2(self, FreezeLog, users, web3):
        admin = users["admin"]
        user1 = users["user1"]

        # Deploy contract
        freeze_log = admin.deploy(FreezeLog)

        test1_block = web3.eth.block_number + 1
        test1_message = "test1 message"
        test1_freezing_grace_block_count = 2

        # Write Log
        tx1 = freeze_log.recordLog(
            test1_message, test1_freezing_grace_block_count, sender=user1
        )
        log = freeze_log.getLog(user1.address, 0, sender=user1)

        # Assertion
        event = event_args(tx1, freeze_log.Recorded)
        assert event["recorder"] == user1.address
        assert log[0] == test1_block
        assert log[1] == test1_freezing_grace_block_count
        assert log[2] == test1_message

        # Add logs to freeze first log.
        for i in range(test1_freezing_grace_block_count):
            tx1 = freeze_log.recordLog(
                test1_message, test1_freezing_grace_block_count, sender=user1
            )

        # Trying to update a frozen log.
        with reverts("620001"):
            test1_message_update = "test1 message updated"
            freeze_log.updateLog(0, test1_message_update, sender=user1)

        log = freeze_log.getLog(user1.address, 0, sender=user1)
        assert log[0] == test1_block
        assert log[1] == test1_freezing_grace_block_count
        assert log[2] == test1_message


class TestGetLog:
    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    # Get a log record by index.
    def test_normal_1(self, FreezeLog, users, web3):
        admin = users["admin"]
        user1 = users["user1"]

        # Deploy contract
        freeze_log = admin.deploy(FreezeLog)
        test1_block = web3.eth.block_number + 1
        test1_message = "test1 message"
        test1_freezing_grace_block_count = 1

        # Write Log
        tx = freeze_log.recordLog(
            test1_message, test1_freezing_grace_block_count, sender=user1
        )

        # Assertion
        event = event_args(tx, freeze_log.Recorded)
        assert event["recorder"] == user1.address

        user1_last_log_index = freeze_log.lastLogIndex(user1.address)

        log = freeze_log.getLog(user1.address, user1_last_log_index - 1, sender=user1)
        assert log[0] == test1_block
        assert log[1] == test1_freezing_grace_block_count
        assert log[2] == test1_message
