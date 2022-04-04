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


class TestWriteLog:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, LogStorage, users, web3):
        admin = users["admin"]

        # Deploy contract
        log_storage = admin.deploy(LogStorage)
        test_block = web3.eth.block_number + 1
        test_message = "test_message"
        test_freezing_grace_block_count = 5

        # Write Log
        tx = log_storage.writeLog(
            test_message,
            test_freezing_grace_block_count
        )

        # Assertion
        assert tx.events["Wrote"]["logIndex"] == 0
        assert tx.events["Wrote"]["logAuthorAddress"] == admin
        assert tx.events["Wrote"]["message"] == test_message
        assert tx.events["Wrote"]["createdBlockNumber"] == test_block
        assert tx.events["Wrote"]["freezingGraceBlockCount"] == test_freezing_grace_block_count

    # Normal_2
    # Write twice
    def test_normal_2(self, LogStorage, users, web3):
        admin = users["admin"]
        author = users["user1"]

        # Deploy contract
        log_storage = admin.deploy(LogStorage)
        test1_block = web3.eth.block_number + 1
        test1_message = "test_message"
        test1_freezing_grace_block_count = 5

        # Write Log
        tx = log_storage.writeLog(
            test1_message,
            test1_freezing_grace_block_count,
            {"from": author}
        )

        # Assertion
        assert tx.events["Wrote"]["logIndex"] == 0
        assert tx.events["Wrote"]["logAuthorAddress"] == author
        assert tx.events["Wrote"]["message"] == test1_message
        assert tx.events["Wrote"]["createdBlockNumber"] == test1_block
        assert tx.events["Wrote"]["freezingGraceBlockCount"] == test1_freezing_grace_block_count

        # Deploy contract
        test2_block = web3.eth.block_number + 1
        test2_message = "test_message"
        test2_freezing_grace_block_count = 5

        # Write Log
        tx = log_storage.writeLog(
            test2_message,
            test2_freezing_grace_block_count,
            {"from": author}
        )

        # Assertion
        assert tx.events["Wrote"]["logIndex"] == 1
        assert tx.events["Wrote"]["logAuthorAddress"] == author
        assert tx.events["Wrote"]["message"] == test2_message
        assert tx.events["Wrote"]["createdBlockNumber"] == test2_block
        assert tx.events["Wrote"]["freezingGraceBlockCount"] == test2_freezing_grace_block_count

    def test_error_1(self, LogStorage, users, web3):
        pass


class TestEditLog:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, LogStorage, users, web3):
        admin = users["admin"]
        author = users["user1"]

        # Deploy contract
        log_storage = admin.deploy(LogStorage)
        test1_block = web3.eth.block_number + 1
        test1_message = "test1 message"
        test1_freezing_grace_block_count = 1

        # Write Log
        tx = log_storage.writeLog(
            test1_message,
            test1_freezing_grace_block_count,
            {"from": author}
        )

        # Assertion
        assert tx.events["Wrote"]["logIndex"] == 0
        assert tx.events["Wrote"]["logAuthorAddress"] == author
        assert tx.events["Wrote"]["message"] == test1_message
        assert tx.events["Wrote"]["createdBlockNumber"] == test1_block
        assert tx.events["Wrote"]["freezingGraceBlockCount"] == test1_freezing_grace_block_count

        test1_message_edit = "test1 message edited"
        tx = log_storage.editLog(
            0,
            test1_message_edit,
            {"from": author}
        )
        assert tx.events["Edited"]["logIndex"] == 0
        assert tx.events["Edited"]["logAuthorAddress"] == author
        assert tx.events["Edited"]["message"] == test1_message_edit

    ##########################################################
    # Error
    ##########################################################

    # Error_1
    def test_error_1(self, LogStorage, users, web3):
        admin = users["admin"]
        author = users["user1"]

        # Deploy contract
        log_storage = admin.deploy(LogStorage)
        test1_block = web3.eth.block_number + 1
        test1_message = "test1 message"
        test1_freezing_grace_block_count = 1

        # Write Log
        tx1 = log_storage.writeLog(
            test1_message,
            test1_freezing_grace_block_count,
            {"from": author}
        )

        # Assertion
        assert tx1.events["Wrote"]["logIndex"] == 0
        assert tx1.events["Wrote"]["logAuthorAddress"] == author
        assert tx1.events["Wrote"]["message"] == test1_message
        assert tx1.events["Wrote"]["createdBlockNumber"] == test1_block
        assert tx1.events["Wrote"]["freezingGraceBlockCount"] == test1_freezing_grace_block_count

        # Increment block number by write twice
        for i in range(2):
            log_storage.writeLog(
                test1_message,
                test1_freezing_grace_block_count,
                {"from": author}
            )
        with brownie.reverts(revert_msg="frozen"):
            test1_message_edit = "test1 message edited"
            tx3 = log_storage.editLog(
                0,
                test1_message_edit,
                {"from": author}
            )

    # Error_2
    def test_error_2(self, LogStorage, users, web3):
        admin = users["admin"]
        author = users["user1"]

        # Deploy contract
        log_storage = admin.deploy(LogStorage)
        test1_block = web3.eth.block_number + 1
        test1_message = "test1 message"
        test1_freezing_grace_block_count = 1

        # Write Log
        tx1 = log_storage.writeLog(
            test1_message,
            test1_freezing_grace_block_count,
            {"from": author}
        )

        # Assertion
        assert tx1.events["Wrote"]["logIndex"] == 0
        assert tx1.events["Wrote"]["logAuthorAddress"] == author
        assert tx1.events["Wrote"]["message"] == test1_message
        assert tx1.events["Wrote"]["createdBlockNumber"] == test1_block
        assert tx1.events["Wrote"]["freezingGraceBlockCount"] == test1_freezing_grace_block_count

        with brownie.reverts(revert_msg="Can be edited by the author."):
            test1_message_edit = "test1 message edited"
            log_storage.editLog(
                0,
                test1_message_edit,
                {"from": admin}
            )


class TestGetLogByIndex:

    ##########################################################
    # Normal
    ##########################################################

    # Normal_1
    def test_normal_1(self, LogStorage, users, web3):
        admin = users["admin"]
        author = users["user1"]

        # Deploy contract
        log_storage = admin.deploy(LogStorage)
        test1_block = web3.eth.block_number + 1
        test1_message = "test1 message"
        test1_freezing_grace_block_count = 1

        # Write Log
        tx = log_storage.writeLog(
            test1_message,
            test1_freezing_grace_block_count,
            {"from": author}
        )

        # Assertion
        assert tx.events["Wrote"]["logIndex"] == 0
        assert tx.events["Wrote"]["logAuthorAddress"] == author
        assert tx.events["Wrote"]["message"] == test1_message
        assert tx.events["Wrote"]["createdBlockNumber"] == test1_block
        assert tx.events["Wrote"]["freezingGraceBlockCount"] == test1_freezing_grace_block_count
        log = log_storage.getLogByIndex(0)
        assert log[0] == author
        assert log[1] == test1_message
        assert log[2] == test1_block
        assert log[3] == test1_freezing_grace_block_count

    # Error_1
    def test_error_1(self, LogStorage, users, web3):
        admin = users["admin"]

        # Deploy contract
        log_storage = admin.deploy(LogStorage)

        with brownie.reverts(revert_msg="Log of that index is not stored yet."):
            log = log_storage.getLogByIndex(0)
