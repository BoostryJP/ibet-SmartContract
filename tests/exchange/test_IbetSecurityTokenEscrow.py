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

from ape import project
from ape_utils import ZERO_ADDRESS, call_view_method, event_args, has_event, reverts


def init_args():
    deploy_args = [
        "test_share",
        "test_symbol",
        2**256 - 1,
        2**256 - 1,
        2**256 - 1,
        "20200829",
        "20200831",
        "20191231",
        2**256 - 1,
    ]
    return deploy_args


def deploy(
    users,
    deploy_args: list,
    tradable_exchange: str,
    transferable: bool = True,
    transfer_approval_required: bool = False,
):
    token = users["issuer"].deploy(project.IbetShare, *deploy_args)  # type: ignore
    token.setTradableExchange(tradable_exchange, sender=users["issuer"])

    if transferable:
        token.setTransferable(True, sender=users["issuer"])

    if transfer_approval_required:
        token.setTransferApprovalRequired(True, sender=users["issuer"])

    return token


def transfer_application(st_escrow, escrow_id):
    return tuple(call_view_method(st_escrow, "getApplicationForTransfer", escrow_id))


# TEST_deploy
class TestDeploy:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_escrow, st_escrow_storage):
        # assertion
        assert st_escrow.owner() == users["admin"]
        assert st_escrow.storageAddress() == st_escrow_storage.address


# TEST_storageAddress
class TestStorageAddress:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, st_escrow, st_escrow_storage):
        # assertion
        assert st_escrow.storageAddress() == st_escrow_storage.address


# TEST_latestEscrowId
class TestLatestEscrowId:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_escrow, st_escrow_storage):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # assertion
        assert st_escrow.latestEscrowId() == st_escrow_storage.getLatestEscrowId()


# TEST_getEscrow
class TestGetEscrow:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_escrow, st_escrow_storage):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # assertion
        latest_escrow_id = st_escrow.latestEscrowId()
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )
        assert st_escrow.getEscrow(latest_escrow_id) == st_escrow_storage.getEscrow(
            latest_escrow_id
        )


# TEST_getApplicationForTransfer
class TestGetApplicationForTransfer:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True,
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # assertion
        latest_escrow_id = st_escrow.latestEscrowId()
        assert transfer_application(st_escrow, latest_escrow_id) == (
            token.address,
            _transfer_application_data,
            "",
            True,
            False,
            False,
        )


# TEST_balanceOf
class TestBalanceOf:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_escrow, st_escrow_storage):
        _issuer = users["issuer"]
        _value = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _value, sender=_issuer)

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _value
        assert st_escrow.balanceOf(
            _issuer, token.address
        ) == st_escrow_storage.getBalance(_issuer, token.address)


# TEST_commitmentOf
class TestCommitmentOf:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_escrow, st_escrow_storage):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # assertion
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.commitmentOf(
            _issuer, token.address
        ) == st_escrow_storage.getCommitment(_issuer, token.address)


# TEST_createEscrow
class TestCreateEscrow:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Transfer approval not required
    def test_normal_1(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        tx = st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        latest_escrow_id = st_escrow.latestEscrowId()
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

        event = event_args(tx, st_escrow.EscrowCreated)
        assert event["escrowId"] == latest_escrow_id
        assert event["token"] == token.address
        assert event["sender"] == _issuer
        assert event["recipient"] == _recipient
        assert event["amount"] == _escrow_amount
        assert event["agent"] == _agent
        assert event["data"] == _data

    # Normal_2
    # Transfer approval required
    def test_normal_2(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True,
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        tx = st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount

        latest_escrow_id = st_escrow.latestEscrowId()
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )
        assert transfer_application(st_escrow, latest_escrow_id) == (
            token.address,
            _transfer_application_data,
            "",
            True,
            False,
            False,
        )

        apply_event = event_args(tx, st_escrow.ApplyForTransfer)
        assert apply_event["escrowId"] == latest_escrow_id
        assert apply_event["token"] == token.address
        assert apply_event["from"] == _issuer
        assert apply_event["to"] == _recipient
        assert apply_event["value"] == _escrow_amount
        assert apply_event["data"] == _transfer_application_data

        escrow_created_event = event_args(tx, st_escrow.EscrowCreated)
        assert escrow_created_event["escrowId"] == latest_escrow_id
        assert escrow_created_event["token"] == token.address
        assert escrow_created_event["sender"] == _issuer
        assert escrow_created_event["recipient"] == _recipient
        assert escrow_created_event["amount"] == _escrow_amount
        assert escrow_created_event["agent"] == _agent
        assert escrow_created_event["data"] == _data

    # Normal_3
    # Create twice
    def test_normal_3(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow (1)
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # create escrow (2)
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount * 2
        )
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount * 2

    #######################################
    # Error
    #######################################

    # Error_1
    # The amount must be greater than zero.
    def test_error_1(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        with reverts("240001"):
            st_escrow.createEscrow(
                token.address,
                _recipient,
                0,
                _agent,
                _transfer_application_data,
                _data,
                sender=_issuer,
            )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0

    # Error_2
    # The amount must be less than or equal to the balance.
    def test_error_2(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        with reverts("240002"):
            st_escrow.createEscrow(
                token.address,
                _recipient,
                _deposit_amount + 1,
                _agent,
                _transfer_application_data,
                _data,
                sender=_issuer,
            )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0

    # Error_3
    # The status of the token must be true.
    def test_error_3(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # set status to False
        token.setStatus(False, sender=_issuer)

        # create escrow
        with reverts("240003"):
            st_escrow.createEscrow(
                token.address,
                _recipient,
                _escrow_amount,
                _agent,
                _transfer_application_data,
                _data,
                sender=_issuer,
            )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0

    # Error_4
    # Storage is not writable.
    def test_error_4(self, users, st_escrow, st_escrow_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # update storage
        st_escrow_storage.upgradeVersion(ZERO_ADDRESS, sender=_admin)

        # create escrow
        bf_latest_escrow_id = st_escrow.latestEscrowId()
        with reverts("220001"):
            st_escrow.createEscrow(
                token.address,
                _recipient,
                _escrow_amount,
                _agent,
                _transfer_application_data,
                _data,
                sender=_issuer,
            )
        af_latest_escrow_id = st_escrow.latestEscrowId()

        # assertion
        assert bf_latest_escrow_id == af_latest_escrow_id
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0


# TEST_cancelEscrow
class TestCancelEscrow:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # msg.sender is the sender of the escrow
    def test_normal_1(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # cancel escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        tx = st_escrow.cancelEscrow(latest_escrow_id, sender=_issuer)

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
        )

        event = event_args(tx, st_escrow.EscrowCanceled)
        assert event["escrowId"] == latest_escrow_id
        assert event["token"] == token.address
        assert event["sender"] == _issuer
        assert event["recipient"] == _recipient
        assert event["amount"] == _escrow_amount
        assert event["agent"] == _agent

    # Normal_2
    # msg.sender is the agent of the escrow
    def test_normal_2(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # cancel escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        tx = st_escrow.cancelEscrow(latest_escrow_id, sender=_agent)

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
        )

        event = event_args(tx, st_escrow.EscrowCanceled)
        assert event["escrowId"] == latest_escrow_id
        assert event["token"] == token.address
        assert event["sender"] == _issuer
        assert event["recipient"] == _recipient
        assert event["amount"] == _escrow_amount
        assert event["agent"] == _agent

    # Normal_3_1
    # transfer approval required
    def test_normal_3_1(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True,
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # cancel escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        tx = st_escrow.cancelEscrow(latest_escrow_id, sender=_issuer)

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
        )
        assert transfer_application(st_escrow, latest_escrow_id) == (
            token.address,
            _transfer_application_data,
            "",
            False,
            False,
            False,
        )

        event_cancel_transfer = event_args(tx, st_escrow.CancelTransfer)
        assert event_cancel_transfer["escrowId"] == latest_escrow_id
        assert event_cancel_transfer["token"] == token.address
        assert event_cancel_transfer["from"] == _issuer
        assert event_cancel_transfer["to"] == _recipient

        event_escrow_canceled = event_args(tx, st_escrow.EscrowCanceled)
        assert event_escrow_canceled["escrowId"] == latest_escrow_id
        assert event_escrow_canceled["token"] == token.address
        assert event_escrow_canceled["sender"] == _issuer
        assert event_escrow_canceled["recipient"] == _recipient
        assert event_escrow_canceled["amount"] == _escrow_amount
        assert event_escrow_canceled["agent"] == _agent

    # Normal_3_2
    # transfer approval required (application does not exist)
    def test_normal_3_2(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token (transfer approval not required)
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # change to transfer approval required
        token.setTransferApprovalRequired(True, sender=_issuer)

        # cancel escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        tx = st_escrow.cancelEscrow(latest_escrow_id, sender=_issuer)

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
        )

        event = event_args(tx, st_escrow.EscrowCanceled)
        assert event["escrowId"] == latest_escrow_id
        assert event["token"] == token.address
        assert event["sender"] == _issuer
        assert event["recipient"] == _recipient
        assert event["amount"] == _escrow_amount
        assert event["agent"] == _agent

    #######################################
    # Error
    #######################################

    # Error_1
    # The escrowId must be less than or equal to the latest escrow ID.
    def test_error_1(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # cancel escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with reverts("240101"):
            st_escrow.cancelEscrow(latest_escrow_id + 1, sender=_issuer)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_2
    # Escrow must be valid.
    def test_error_2(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # cancel escrow (1)
        latest_escrow_id = st_escrow.latestEscrowId()
        st_escrow.cancelEscrow(latest_escrow_id, sender=_issuer)

        # cancel escrow (2)
        with reverts("240102"):
            st_escrow.cancelEscrow(latest_escrow_id, sender=_issuer)

    # Error_3
    # msg.sender must be the sender or agent of the escrow.
    def test_error_3(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # cancel escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with reverts("240103"):
            st_escrow.cancelEscrow(latest_escrow_id, sender=_recipient)

    # Error_4
    # The status of the token must be true.
    def test_error_4(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # set status to False
        token.setStatus(False, sender=_issuer)

        # cancel escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with reverts("240104"):
            st_escrow.cancelEscrow(latest_escrow_id, sender=_issuer)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_5
    # Storage is not writable.
    def test_error_5(self, users, st_escrow, st_escrow_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # update storage
        st_escrow_storage.upgradeVersion(ZERO_ADDRESS, sender=_admin)

        # cancel escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with reverts("220001"):
            st_escrow.cancelEscrow(latest_escrow_id, sender=_issuer)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount


# TEST_approveTransfer
class TestApproveTransfer:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _transfer_approval_data = "transfer_approval_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True,
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        st_escrow.finishEscrow(latest_escrow_id, sender=_agent)

        # approve transfer
        tx = st_escrow.approveTransfer(
            latest_escrow_id, _transfer_approval_data, sender=_issuer
        )

        # assertion
        assert transfer_application(st_escrow, latest_escrow_id) == (
            token.address,
            _transfer_application_data,
            _transfer_approval_data,
            True,
            True,
            True,
        )
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.balanceOf(_recipient, token.address) == _escrow_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
        )

        event = event_args(tx, st_escrow.ApproveTransfer)
        assert event["escrowId"] == latest_escrow_id
        assert event["token"] == token.address
        assert event["data"] == _transfer_approval_data

    #######################################
    # Error
    #######################################

    # Error_1
    # Application does not exist.
    def test_error_1(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _transfer_approval_data = "transfer_approval_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True,
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # approve transfer
        latest_escrow_id = st_escrow.latestEscrowId()
        with reverts("240201"):
            st_escrow.approveTransfer(
                latest_escrow_id, _transfer_approval_data, sender=_issuer
            )

    # Error_2
    # Approver must be the owner of the token.
    def test_error_2(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _transfer_approval_data = "transfer_approval_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True,
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # approve transfer
        latest_escrow_id = st_escrow.latestEscrowId()
        with reverts("240202"):
            st_escrow.approveTransfer(
                latest_escrow_id, _transfer_approval_data, sender=_recipient
            )

    # Error_3
    # Application for transfer must be valid.
    def test_error_3(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _transfer_approval_data = "transfer_approval_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True,
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # cancel escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        st_escrow.cancelEscrow(latest_escrow_id, sender=_issuer)

        # approve transfer
        with reverts("240203"):
            st_escrow.approveTransfer(
                latest_escrow_id, _transfer_approval_data, sender=_issuer
            )

    # Error_4
    # The escrow status of the application must be in a finished state.
    def test_error_4(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _transfer_approval_data = "transfer_approval_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True,
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # approve transfer
        latest_escrow_id = st_escrow.latestEscrowId()
        with reverts("240204"):
            st_escrow.approveTransfer(
                latest_escrow_id, _transfer_approval_data, sender=_issuer
            )

    # Error_5
    # The status of the token must be true.
    def test_error_5(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _transfer_approval_data = "transfer_approval_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True,
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        st_escrow.finishEscrow(latest_escrow_id, sender=_agent)

        # set status to False
        token.setStatus(False, sender=_issuer)

        # approve transfer
        with reverts("240205"):
            st_escrow.approveTransfer(
                latest_escrow_id, _transfer_approval_data, sender=_issuer
            )


# TEST_finishEscrow
class TestFinishEscrow:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Transfer approval not required
    def test_normal_1(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        tx = st_escrow.finishEscrow(latest_escrow_id, sender=_agent)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.balanceOf(_recipient, token.address) == _escrow_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
        )

        finish_event = event_args(tx, st_escrow.EscrowFinished)
        assert finish_event["escrowId"] == latest_escrow_id
        assert finish_event["token"] == token.address
        assert finish_event["sender"] == _issuer
        assert finish_event["recipient"] == _recipient
        assert finish_event["amount"] == _escrow_amount
        assert finish_event["agent"] == _agent
        assert finish_event["transferApprovalRequired"] is False

        holder_changed_event = event_args(tx, st_escrow.HolderChanged)
        assert holder_changed_event["token"] == token.address
        assert holder_changed_event["from"] == _issuer
        assert holder_changed_event["to"] == _recipient
        assert holder_changed_event["value"] == _escrow_amount

    # Normal_2
    # Transfer approval required
    def test_normal_2(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True,
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        tx = st_escrow.finishEscrow(latest_escrow_id, sender=_agent)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.balanceOf(_recipient, token.address) == 0
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
        )
        assert transfer_application(st_escrow, latest_escrow_id) == (
            token.address,
            _transfer_application_data,
            "",
            True,
            True,
            False,
        )

        finish_event = event_args(tx, st_escrow.EscrowFinished)
        assert finish_event["escrowId"] == latest_escrow_id
        assert finish_event["token"] == token.address
        assert finish_event["sender"] == _issuer
        assert finish_event["recipient"] == _recipient
        assert finish_event["amount"] == _escrow_amount
        assert finish_event["agent"] == _agent
        assert finish_event["transferApprovalRequired"] is True

    #######################################
    # Error
    #######################################

    # Error_1
    # The escrowId must be less than or equal to the latest escrow ID.
    def test_error_1(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with reverts("240301"):
            st_escrow.finishEscrow(latest_escrow_id + 1, sender=_agent)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.balanceOf(_recipient, token.address) == 0
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_2
    # Escrow must be valid.
    def test_error_2(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # finish escrow (1)
        latest_escrow_id = st_escrow.latestEscrowId()
        st_escrow.finishEscrow(latest_escrow_id, sender=_agent)

        # finish escrow (2)
        with reverts("240302"):
            st_escrow.finishEscrow(latest_escrow_id, sender=_agent)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.balanceOf(_recipient, token.address) == _escrow_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
        )

    # Error_3
    # msg.sender must be the agent of the escrow.
    def test_error_3(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with reverts("240303"):
            st_escrow.finishEscrow(latest_escrow_id, sender=_recipient)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.balanceOf(_recipient, token.address) == 0
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_4
    # The status of the token must be true.
    def test_error_4(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # set status to False
        token.setStatus(False, sender=_issuer)

        # finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with reverts("240304"):
            st_escrow.finishEscrow(latest_escrow_id, sender=_agent)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.balanceOf(_recipient, token.address) == 0
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_5
    # Storage is not writable.
    def test_error_5(self, users, st_escrow, st_escrow_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # update storage
        st_escrow_storage.upgradeVersion(ZERO_ADDRESS, sender=_admin)

        # finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with reverts("220001"):
            st_escrow.finishEscrow(latest_escrow_id, sender=_agent)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount


# TEST_bulkFinishEscrow
class TestBulkFinishEscrow:
    #######################################
    # Normal
    #######################################

    # Normal_1_1
    # Transfer approval not required (1 data)
    def test_normal_1_1(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # bulk finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        tx = st_escrow.bulkFinishEscrow([latest_escrow_id], sender=_agent)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.balanceOf(_recipient, token.address) == _escrow_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
        )

        finish_event = event_args(tx, st_escrow.EscrowFinished)
        assert finish_event["escrowId"] == latest_escrow_id
        assert finish_event["token"] == token.address
        assert finish_event["sender"] == _issuer
        assert finish_event["recipient"] == _recipient
        assert finish_event["amount"] == _escrow_amount
        assert finish_event["agent"] == _agent
        assert finish_event["transferApprovalRequired"] is False

        holder_changed_event = event_args(tx, st_escrow.HolderChanged)
        assert holder_changed_event["token"] == token.address
        assert holder_changed_event["from"] == _issuer
        assert holder_changed_event["to"] == _recipient
        assert holder_changed_event["value"] == _escrow_amount

    # Normal_1_2
    # Transfer approval not required (multiple data)
    def test_normal_1_2(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 10000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        escrow_id_list = []
        for _ in range(100):
            st_escrow.createEscrow(
                token.address,
                _recipient,
                _escrow_amount,
                _agent,
                _transfer_application_data,
                _data,
                sender=_issuer,
            )
            latest_escrow_id = st_escrow.latestEscrowId()
            escrow_id_list.append(latest_escrow_id)

        # bulk finish escrow
        st_escrow.bulkFinishEscrow(escrow_id_list, sender=_agent)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount * 100
        )
        assert st_escrow.balanceOf(_recipient, token.address) == _escrow_amount * 100
        assert st_escrow.commitmentOf(_issuer, token.address) == 0
        for escrow_id in escrow_id_list:
            assert st_escrow.getEscrow(escrow_id) == (
                token.address,
                _issuer,
                _recipient,
                _escrow_amount,
                _agent,
                False,
            )

    # Normal_2_1
    # Transfer approval required (1 data)
    def test_normal_2_1(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True,
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # bulk finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        tx = st_escrow.bulkFinishEscrow([latest_escrow_id], sender=_agent)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.balanceOf(_recipient, token.address) == 0
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
        )
        assert transfer_application(st_escrow, latest_escrow_id) == (
            token.address,
            _transfer_application_data,
            "",
            True,
            True,
            False,
        )

        finish_event = event_args(tx, st_escrow.EscrowFinished)
        assert finish_event["escrowId"] == latest_escrow_id
        assert finish_event["token"] == token.address
        assert finish_event["sender"] == _issuer
        assert finish_event["recipient"] == _recipient
        assert finish_event["amount"] == _escrow_amount
        assert finish_event["agent"] == _agent
        assert finish_event["transferApprovalRequired"] is True

    # Normal_2_2
    # Transfer approval required (multiple data)
    def test_normal_2_2(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 10000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True,
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        escrow_id_list = []
        for _ in range(100):
            st_escrow.createEscrow(
                token.address,
                _recipient,
                _escrow_amount,
                _agent,
                _transfer_application_data,
                _data,
                sender=_issuer,
            )
            latest_escrow_id = st_escrow.latestEscrowId()
            escrow_id_list.append(latest_escrow_id)

        # bulk finish escrow
        tx = st_escrow.bulkFinishEscrow(escrow_id_list, sender=_agent)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount * 100
        )
        assert st_escrow.balanceOf(_recipient, token.address) == 0
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount * 100

        for escrow_id in escrow_id_list:
            assert st_escrow.getEscrow(escrow_id) == (
                token.address,
                _issuer,
                _recipient,
                _escrow_amount,
                _agent,
                False,
            )

        assert not has_event(tx, st_escrow.HolderChanged)

    #######################################
    # Error
    #######################################

    # Error_1_1
    # The escrowId must be less than or equal to the latest escrow ID. (1 data)
    def test_error_1_1(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # bulk finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with reverts("240301"):
            tx = st_escrow.bulkFinishEscrow([latest_escrow_id + 1], sender=_agent)
            assert not has_event(tx, st_escrow.EscrowFinished)
            assert not has_event(tx, st_escrow.HolderChanged)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.balanceOf(_recipient, token.address) == 0
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_1_2
    # The escrowId must be less than or equal to the latest escrow ID. (multiple data)
    def test_error_1_2(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # bulk finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with reverts("240301"):
            tx = st_escrow.bulkFinishEscrow(
                [latest_escrow_id, latest_escrow_id + 1], sender=_agent
            )
            assert not has_event(tx, st_escrow.EscrowFinished)
            assert not has_event(tx, st_escrow.HolderChanged)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.balanceOf(_recipient, token.address) == 0
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_2_1
    # Escrow must be valid. (1 data)
    def test_error_2_1(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # bulk finish escrow (1)
        latest_escrow_id = st_escrow.latestEscrowId()
        st_escrow.bulkFinishEscrow([latest_escrow_id], sender=_agent)

        # bulk finish escrow (2)
        with reverts("240302"):
            tx = st_escrow.bulkFinishEscrow([latest_escrow_id], sender=_agent)
            assert not has_event(tx, st_escrow.EscrowFinished)
            assert not has_event(tx, st_escrow.HolderChanged)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.balanceOf(_recipient, token.address) == _escrow_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
        )

    # Error_2_2
    # Escrow must be valid. (multiple data)
    def test_error_2_2(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow (1)
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )
        valid_escrow_id = st_escrow.latestEscrowId()

        # create escrow (2)
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )
        latest_escrow_id = st_escrow.latestEscrowId()

        # bulk finish escrow (1)
        st_escrow.bulkFinishEscrow([latest_escrow_id], sender=_agent)

        # bulk finish escrow (2)
        with reverts("240302"):
            tx = st_escrow.bulkFinishEscrow(
                [valid_escrow_id, latest_escrow_id], sender=_agent
            )
            assert not has_event(tx, st_escrow.EscrowFinished)
            assert not has_event(tx, st_escrow.HolderChanged)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount * 2
        )
        assert st_escrow.balanceOf(_recipient, token.address) == _escrow_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
        )
        assert st_escrow.getEscrow(valid_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_3_1
    # msg.sender must be the agent of the escrow. (1 data)
    def test_error_3_1(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # bulk finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with reverts("240303"):
            tx = st_escrow.bulkFinishEscrow([latest_escrow_id], sender=_recipient)
            assert not has_event(tx, st_escrow.EscrowFinished)
            assert not has_event(tx, st_escrow.HolderChanged)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.balanceOf(_recipient, token.address) == 0
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_3_2
    # msg.sender must be the agent of the escrow. (multiple data)
    def test_error_3_2(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow (1)
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )
        latest_escrow_id_1 = st_escrow.latestEscrowId()

        # create escrow (2)
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _recipient,  # recipient is set as agent
            _transfer_application_data,
            _data,
            sender=_issuer,
        )
        latest_escrow_id_2 = st_escrow.latestEscrowId()

        # bulk finish escrow
        with reverts("240303"):
            tx = st_escrow.bulkFinishEscrow(
                [latest_escrow_id_1, latest_escrow_id_2], sender=_agent
            )
            assert not has_event(tx, st_escrow.EscrowFinished)
            assert not has_event(tx, st_escrow.HolderChanged)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount * 2
        )
        assert st_escrow.balanceOf(_recipient, token.address) == 0
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount * 2
        assert st_escrow.getEscrow(latest_escrow_id_1) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )
        assert st_escrow.getEscrow(latest_escrow_id_2) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _recipient,
            True,
        )

    # Error_4_1
    # The status of the token must be true. (1 data)
    def test_error_4_1(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # set status to False
        token.setStatus(False, sender=_issuer)

        # bulk finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with reverts("240304"):
            tx = st_escrow.bulkFinishEscrow([latest_escrow_id], sender=_agent)
            assert not has_event(tx, st_escrow.EscrowFinished)
            assert not has_event(tx, st_escrow.HolderChanged)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.balanceOf(_recipient, token.address) == 0
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_4_2
    # The status of the token must be true. (multiple data)
    def test_error_4_2(self, users, st_escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token_1 = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )
        token_2 = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract (1)
        token_1.transfer(st_escrow.address, _deposit_amount, sender=_issuer)
        # transfer to escrow contract (2)
        token_2.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow (1)
        st_escrow.createEscrow(
            token_1.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )
        latest_escrow_id_1 = st_escrow.latestEscrowId()

        # create escrow (2)
        st_escrow.createEscrow(
            token_2.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )
        latest_escrow_id_2 = st_escrow.latestEscrowId()

        # set status to False
        token_1.setStatus(False, sender=_issuer)

        # bulk finish escrow
        with reverts("240304"):
            tx = st_escrow.bulkFinishEscrow(
                [latest_escrow_id_1, latest_escrow_id_2], sender=_agent
            )
            assert not has_event(tx, st_escrow.EscrowFinished)
            assert not has_event(tx, st_escrow.HolderChanged)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token_1.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.balanceOf(_recipient, token_1.address) == 0
        assert st_escrow.commitmentOf(_issuer, token_1.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id_1) == (
            token_1.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )
        assert (
            st_escrow.balanceOf(_issuer, token_2.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.balanceOf(_recipient, token_2.address) == 0
        assert st_escrow.commitmentOf(_issuer, token_2.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id_2) == (
            token_2.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_5
    # Storage is not writable.
    def test_error_5(self, users, st_escrow, st_escrow_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _transfer_application_data = "transfer_application_data"
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _deposit_amount, sender=_issuer)

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            sender=_issuer,
        )

        # update storage
        st_escrow_storage.upgradeVersion(ZERO_ADDRESS, sender=_admin)

        # bulk finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with reverts("220001"):
            tx = st_escrow.bulkFinishEscrow([latest_escrow_id], sender=_agent)
            assert not has_event(tx, st_escrow.EscrowFinished)
            assert not has_event(tx, st_escrow.HolderChanged)

        # assertion
        assert (
            st_escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount
        )
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount


# TEST_withdraw
class TestWithdraw:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_escrow):
        _issuer = users["issuer"]
        _value = 2**256 - 1

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _value, sender=_issuer)

        # withdraw
        tx = st_escrow.withdraw(token.address, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2]
        assert st_escrow.balanceOf(_issuer, token.address) == 0

        event = event_args(tx, st_escrow.Withdrawn)
        assert event["token"] == token.address
        assert event["account"] == _issuer

    #######################################
    # Error
    #######################################

    # Error_1
    # The balance must be greater than zero.
    def test_error_1(self, users, st_escrow):
        _issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # withdraw
        with reverts("240401"):
            st_escrow.withdraw(token.address, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2]
        assert st_escrow.balanceOf(_issuer, token.address) == 0

    # Error_2
    # Storage is not writable.
    def test_error_2(self, users, st_escrow, st_escrow_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _value = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _value, sender=_issuer)

        # update storage
        st_escrow_storage.upgradeVersion(ZERO_ADDRESS, sender=_admin)

        # withdraw
        with reverts("220001"):
            st_escrow.withdraw(token.address, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2] - _value
        assert st_escrow.balanceOf(_issuer, token.address) == _value

    # Error_3
    # Must be transferable.
    def test_error_3(self, users, st_escrow):
        _issuer = users["issuer"]
        _value = 2**256 - 1

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(st_escrow.address, _value, sender=_issuer)

        # set to not transferable
        token.setTransferable(False, sender=_issuer)

        # withdraw
        with reverts("110402"):
            st_escrow.withdraw(token.address, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == 0
        assert token.balanceOf(st_escrow.address) == deploy_args[3]
        assert st_escrow.balanceOf(_issuer, token.address) == deploy_args[3]


# TEST_tokenFallback
class TestTokenFallback:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_escrow):
        _issuer = users["issuer"]
        _value = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        tx = token.transfer(st_escrow.address, _value, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2] - _value
        assert st_escrow.balanceOf(_issuer, token.address) == _value

        event = event_args(tx, st_escrow.Deposited)
        assert event["token"] == token.address
        assert event["account"] == _issuer

    # Normal_2
    # Multiple deposit
    def test_normal_2(self, users, st_escrow):
        _issuer = users["issuer"]
        _value = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract (1)
        token.transfer(st_escrow.address, _value, sender=_issuer)

        # transfer to escrow contract (2)
        token.transfer(st_escrow.address, _value, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2] - _value * 2
        assert st_escrow.balanceOf(_issuer, token.address) == _value * 2

    #######################################
    # Error
    #######################################

    # Error_1
    # Storage is not writable.
    def test_error_1(self, users, st_escrow, st_escrow_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _value = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_escrow.address
        )

        # update storage
        st_escrow_storage.upgradeVersion(ZERO_ADDRESS, sender=_admin)

        # transfer to escrow contract
        with reverts("220001"):
            token.transfer(st_escrow.address, _value, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2]
        assert st_escrow.balanceOf(_issuer, token.address) == 0
