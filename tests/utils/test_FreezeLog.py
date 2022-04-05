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


class TestFreezeLog:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
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
            test_message,
            test_freezing_grace_block_count,
            {"from": user}
        )

        # Assertion
        assert tx.events["Recorded"]["recorder"] == user

    # Normal_2
    # Write twice
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
            test_message,
            test_freezing_grace_block_count,
            {"from": user1}
        )

        # Assertion
        assert tx.events["Recorded"]["recorder"] == user1.address

        # Deploy contract
        freeze_log = admin.deploy(FreezeLog)
        test_block = web3.eth.block_number + 1
        test_message = "test_message"
        test_freezing_grace_block_count = 5

        # Record Log
        tx = freeze_log.recordLog(
            test_message,
            test_freezing_grace_block_count,
            {"from": user2}
        )

        # Assertion
        assert tx.events["Recorded"]["recorder"] == user2.address


class TestLastLogIndex:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, FreezeLog, users, web3):
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
            test_message,
            test_freezing_grace_block_count,
            {"from": user1}
        )

        user1_last_log_index = freeze_log.lastLogIndex(user1, {"from": user2})
        assert user1_last_log_index == 1
        user2_last_log_index = freeze_log.lastLogIndex(user2, {"from": user2})
        assert user2_last_log_index == 0


class TestUpdateLog:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, FreezeLog, users, web3):
        admin = users["admin"]
        user1 = users["user1"]

        # Deploy contract
        freeze_log = admin.deploy(FreezeLog)
        test_block = web3.eth.block_number + 1
        test_message = "test_message"
        test_freezing_grace_block_count = 5

        # Record Log
        tx = freeze_log.recordLog(
            test_message,
            test_freezing_grace_block_count,
            {"from": user1}
        )
        # Assertion
        assert tx.events["Recorded"]["recorder"] == user1

        user1_last_index = freeze_log.lastLogIndex(user1, {"from": user1})

        tx = freeze_log.updateLog(user1_last_index - 1, test_message[::-1], {"from": user1})

        # Assertion
        assert tx.events["Updated"]["recorder"] == user1
        assert tx.events["Updated"]["index"] == user1_last_index - 1

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    def test_error_1(self, FreezeLog, users, web3):
        admin = users["admin"]
        user1 = users["user1"]

        # Deploy contract
        freeze_log = admin.deploy(FreezeLog)

        test_idx = 10
        test_message = "test1 message"
        with brownie.reverts():
            freeze_log.updateLog(test_idx, test_message, {"from": user1})

    # Error_2
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
            test1_message,
            test1_freezing_grace_block_count,
            {"from": user1}
        )

        # Assertion
        assert tx1.events["Recorded"]["recorder"] == user1.address

        for i in range(test1_freezing_grace_block_count):
            # Write Log
            tx1 = freeze_log.recordLog(
                test1_message,
                test1_freezing_grace_block_count,
                {"from": user1}
            )

        with brownie.reverts(revert_msg="frozen"):
            test1_message_update = "test1 message updated"
            freeze_log.updateLog(
                0,
                test1_message_update,
                {"from": user1}
            )


class TestGetLog:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
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
            test1_message,
            test1_freezing_grace_block_count,
            {"from": user1}
        )

        # Assertion
        assert tx.events["Recorded"]["recorder"] == user1.address

        user1_last_log_index = freeze_log.lastLogIndex(user1.address)

        log = freeze_log.getLog(user1.address, user1_last_log_index - 1)

        assert log[0] == test1_block
        assert log[1] == test1_freezing_grace_block_count
        assert log[2] == test1_message

    # Error_1
    def test_error_1(self, FreezeLog, users, web3):
        admin = users["admin"]
        user1 = users["user1"]

        # Deploy contract
        freeze_log = admin.deploy(FreezeLog)

        with brownie.reverts():
            log = freeze_log.getLog(user1.address, 0)
