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


def init_args():
    deploy_args = [
        'test_share',
        'test_symbol',
        2 ** 256 - 1,
        2 ** 256 - 1,
        2 ** 256 - 1,
        '20200829',
        '20200831',
        '20191231',
        2 ** 256 - 1
    ]
    return deploy_args


def deploy(users, deploy_args: list,
           tradable_exchange: str,
           transferable: bool = True,
           transfer_approval_required: bool = False):
    from brownie import IbetShare

    token = users["issuer"].deploy(
        IbetShare,
        *deploy_args
    )
    token.setTradableExchange(
        tradable_exchange,
        {'from': users["issuer"]}
    )

    if transferable:
        token.setTransferable(
            True,
            {'from': users["issuer"]}
        )

    if transfer_approval_required:
        token.setTransferApprovalRequired(
            True,
            {'from': users["issuer"]}
        )

    return token


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
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
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
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # assertion
        latest_escrow_id = st_escrow.latestEscrowId()
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True
        )
        assert st_escrow.getEscrow(latest_escrow_id) == \
               st_escrow_storage.getEscrow(latest_escrow_id)


# TEST_getApplicationForTransfer
class TestGetApplicationForTransfer:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # assertion
        latest_escrow_id = st_escrow.latestEscrowId()
        assert st_escrow.getApplicationForTransfer(latest_escrow_id) == (
            token.address,
            _transfer_application_data,
            "",
            True,
            False,
            False
        )


# TEST_balanceOf
class TestBalanceOf:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_escrow, st_escrow_storage):
        _issuer = users['issuer']
        _value = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _value,
            {'from': _issuer}
        )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _value
        assert st_escrow.balanceOf(_issuer, token.address) == \
               st_escrow_storage.getBalance(_issuer, token.address)


# TEST_commitmentOf
class TestCommitmentOf:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_escrow, st_escrow_storage):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # assertion
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == \
               st_escrow_storage.getCommitment(_issuer, token.address)


# TEST_createEscrow
class TestCreateEscrow:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Transfer approval not required
    def test_normal_1(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        tx = st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        latest_escrow_id = st_escrow.latestEscrowId()
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True
        )

        assert tx.events["EscrowCreated"]["escrowId"] == latest_escrow_id
        assert tx.events["EscrowCreated"]["token"] == token.address
        assert tx.events["EscrowCreated"]["sender"] == _issuer
        assert tx.events["EscrowCreated"]["recipient"] == _recipient
        assert tx.events["EscrowCreated"]["amount"] == _escrow_amount
        assert tx.events["EscrowCreated"]["agent"] == _agent
        assert tx.events["EscrowCreated"]["data"] == _data

    # Normal_2
    # Transfer approval required
    def test_normal_2(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        tx = st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount

        latest_escrow_id = st_escrow.latestEscrowId()
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True
        )
        assert st_escrow.getApplicationForTransfer(latest_escrow_id) == (
            token.address,
            _transfer_application_data,
            "",
            True,
            False,
            False
        )

        assert tx.events["ApplyForTransfer"]["escrowId"] == latest_escrow_id
        assert tx.events["ApplyForTransfer"]["token"] == token.address
        assert tx.events["ApplyForTransfer"]["from"] == _issuer
        assert tx.events["ApplyForTransfer"]["to"] == _recipient
        assert tx.events["ApplyForTransfer"]["value"] == _escrow_amount
        assert tx.events["ApplyForTransfer"]["data"] == _transfer_application_data

        assert tx.events["EscrowCreated"]["escrowId"] == latest_escrow_id
        assert tx.events["EscrowCreated"]["token"] == token.address
        assert tx.events["EscrowCreated"]["sender"] == _issuer
        assert tx.events["EscrowCreated"]["recipient"] == _recipient
        assert tx.events["EscrowCreated"]["amount"] == _escrow_amount
        assert tx.events["EscrowCreated"]["agent"] == _agent
        assert tx.events["EscrowCreated"]["data"] == _data

    # Normal_3
    # Create twice
    def test_normal_3(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow (1)
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # create escrow (2)
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount * 2
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount * 2

    #######################################
    # Error
    #######################################

    # Error_1
    # The amount must be greater than zero.
    def test_error_1(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        with brownie.reverts(revert_msg="240001"):
            st_escrow.createEscrow(
                token.address,
                _recipient,
                0,
                _agent,
                _transfer_application_data,
                _data,
                {'from': _issuer}
            )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0

    # Error_2
    # The amount must be less than or equal to the balance.
    def test_error_2(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        with brownie.reverts(revert_msg="240002"):
            st_escrow.createEscrow(
                token.address,
                _recipient,
                _deposit_amount + 1,
                _agent,
                _transfer_application_data,
                _data,
                {'from': _issuer}
            )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0

    # Error_3
    # The status of the token must be true.
    def test_error_3(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # set status to False
        token.setStatus(
            False,
            {'from': _issuer}
        )

        # create escrow
        with brownie.reverts(revert_msg="240003"):
            st_escrow.createEscrow(
                token.address,
                _recipient,
                _escrow_amount,
                _agent,
                _transfer_application_data,
                _data,
                {'from': _issuer}
            )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0

    # Error_4
    # Storage is not writable.
    def test_error_4(self, users, st_escrow, st_escrow_storage):
        _admin = users['admin']
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # update storage
        st_escrow_storage.upgradeVersion(
            brownie.ZERO_ADDRESS,
            {'from': _admin}
        )

        # create escrow
        bf_latest_escrow_id = st_escrow.latestEscrowId()
        with brownie.reverts(revert_msg=""):
            st_escrow.createEscrow(
                token.address,
                _recipient,
                _escrow_amount,
                _agent,
                _transfer_application_data,
                _data,
                {'from': _issuer}
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
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # cancel escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        tx = st_escrow.cancelEscrow(
            latest_escrow_id,
            {'from': _issuer}
        )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False
        )

        assert tx.events["EscrowCanceled"]["escrowId"] == latest_escrow_id
        assert tx.events["EscrowCanceled"]["token"] == token.address
        assert tx.events["EscrowCanceled"]["sender"] == _issuer
        assert tx.events["EscrowCanceled"]["recipient"] == _recipient
        assert tx.events["EscrowCanceled"]["amount"] == _escrow_amount
        assert tx.events["EscrowCanceled"]["agent"] == _agent

    # Normal_2
    # msg.sender is the agent of the escrow
    def test_normal_2(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # cancel escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        tx = st_escrow.cancelEscrow(
            latest_escrow_id,
            {'from': _agent}
        )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False
        )

        assert tx.events["EscrowCanceled"]["escrowId"] == latest_escrow_id
        assert tx.events["EscrowCanceled"]["token"] == token.address
        assert tx.events["EscrowCanceled"]["sender"] == _issuer
        assert tx.events["EscrowCanceled"]["recipient"] == _recipient
        assert tx.events["EscrowCanceled"]["amount"] == _escrow_amount
        assert tx.events["EscrowCanceled"]["agent"] == _agent

    # Normal_3_1
    # transfer approval required
    def test_normal_3_1(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # cancel escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        tx = st_escrow.cancelEscrow(
            latest_escrow_id,
            {'from': _issuer}
        )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False
        )
        assert st_escrow.getApplicationForTransfer(latest_escrow_id) == (
            token.address,
            _transfer_application_data,
            "",
            False,
            False,
            False
        )

        assert tx.events["CancelTransfer"]["escrowId"] == latest_escrow_id
        assert tx.events["CancelTransfer"]["token"] == token.address
        assert tx.events["CancelTransfer"]["from"] == _issuer
        assert tx.events["CancelTransfer"]["to"] == _recipient

        assert tx.events["EscrowCanceled"]["escrowId"] == latest_escrow_id
        assert tx.events["EscrowCanceled"]["token"] == token.address
        assert tx.events["EscrowCanceled"]["sender"] == _issuer
        assert tx.events["EscrowCanceled"]["recipient"] == _recipient
        assert tx.events["EscrowCanceled"]["amount"] == _escrow_amount
        assert tx.events["EscrowCanceled"]["agent"] == _agent

    # Normal_3_2
    # transfer approval required (application does not exist)
    def test_normal_3_2(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token (transfer approval not required)
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # change to transfer approval required
        token.setTransferApprovalRequired(
            True,
            {'from': _issuer}
        )

        # cancel escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        tx = st_escrow.cancelEscrow(
            latest_escrow_id,
            {'from': _issuer}
        )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False
        )

        assert tx.events["EscrowCanceled"]["escrowId"] == latest_escrow_id
        assert tx.events["EscrowCanceled"]["token"] == token.address
        assert tx.events["EscrowCanceled"]["sender"] == _issuer
        assert tx.events["EscrowCanceled"]["recipient"] == _recipient
        assert tx.events["EscrowCanceled"]["amount"] == _escrow_amount
        assert tx.events["EscrowCanceled"]["agent"] == _agent

    #######################################
    # Error
    #######################################

    # Error_1
    # The escrowId must be less than or equal to the latest escrow ID.
    def test_error_1(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # cancel escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with brownie.reverts(revert_msg="240101"):
            st_escrow.cancelEscrow(
                latest_escrow_id + 1,
                {'from': _issuer}
            )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True
        )

    # Error_2
    # Escrow must be valid.
    def test_error_2(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # cancel escrow (1)
        latest_escrow_id = st_escrow.latestEscrowId()
        st_escrow.cancelEscrow(
            latest_escrow_id,
            {'from': _issuer}
        )

        # cancel escrow (2)
        with brownie.reverts(revert_msg="240102"):
            st_escrow.cancelEscrow(
                latest_escrow_id,
                {'from': _issuer}
            )

    # Error_3
    # msg.sender must be the sender or agent of the escrow.
    def test_error_3(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # cancel escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with brownie.reverts(revert_msg="240103"):
            st_escrow.cancelEscrow(
                latest_escrow_id,
                {'from': _recipient}
            )

    # Error_4
    # The status of the token must be true.
    def test_error_4(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # set status to False
        token.setStatus(
            False,
            {'from': _issuer}
        )

        # cancel escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with brownie.reverts(revert_msg="240104"):
            st_escrow.cancelEscrow(
                latest_escrow_id,
                {'from': _issuer}
            )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True
        )

    # Error_5
    # Storage is not writable.
    def test_error_5(self, users, st_escrow, st_escrow_storage):
        _admin = users['admin']
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # update storage
        st_escrow_storage.upgradeVersion(
            brownie.ZERO_ADDRESS,
            {'from': _admin}
        )

        # cancel escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with brownie.reverts(revert_msg=""):
            st_escrow.cancelEscrow(
                latest_escrow_id,
                {'from': _issuer}
            )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount


# TEST_approveTransfer
class TestApproveTransfer:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _transfer_approval_data = 'transfer_approval_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        st_escrow.finishEscrow(
            latest_escrow_id,
            {'from': _agent}
        )

        # approve transfer
        tx = st_escrow.approveTransfer(
            latest_escrow_id,
            _transfer_approval_data,
            {'from': _issuer}
        )

        # assertion
        assert st_escrow.getApplicationForTransfer(latest_escrow_id) == (
            token.address,
            _transfer_application_data,
            _transfer_approval_data,
            True,
            True,
            True
        )
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert st_escrow.balanceOf(_recipient, token.address) == _escrow_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False
        )

        assert tx.events["ApproveTransfer"]["escrowId"] == latest_escrow_id
        assert tx.events["ApproveTransfer"]["token"] == token.address
        assert tx.events["ApproveTransfer"]["data"] == _transfer_approval_data

    #######################################
    # Error
    #######################################

    # Error_1
    # Application does not exist.
    def test_error_1(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _transfer_approval_data = 'transfer_approval_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # approve transfer
        latest_escrow_id = st_escrow.latestEscrowId()
        with brownie.reverts(revert_msg="240201"):
            st_escrow.approveTransfer(
                latest_escrow_id,
                _transfer_approval_data,
                {'from': _issuer}
            )

    # Error_2
    # Approver must be the owner of the token.
    def test_error_2(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _transfer_approval_data = 'transfer_approval_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # approve transfer
        latest_escrow_id = st_escrow.latestEscrowId()
        with brownie.reverts(revert_msg="240202"):
            st_escrow.approveTransfer(
                latest_escrow_id,
                _transfer_approval_data,
                {'from': _recipient}
            )

    # Error_3
    # Application for transfer must be valid.
    def test_error_3(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _transfer_approval_data = 'transfer_approval_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # cancel escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        st_escrow.cancelEscrow(
            latest_escrow_id,
            {'from': _issuer}
        )

        # approve transfer
        with brownie.reverts(revert_msg="240203"):
            st_escrow.approveTransfer(
                latest_escrow_id,
                _transfer_approval_data,
                {'from': _issuer}
            )

    # Error_4
    # The escrow status of the application must be in a finished state.
    def test_error_4(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _transfer_approval_data = 'transfer_approval_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # approve transfer
        latest_escrow_id = st_escrow.latestEscrowId()
        with brownie.reverts(revert_msg="240204"):
            st_escrow.approveTransfer(
                latest_escrow_id,
                _transfer_approval_data,
                {'from': _issuer}
            )

    # Error_5
    # The status of the token must be true.
    def test_error_5(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _transfer_approval_data = 'transfer_approval_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        st_escrow.finishEscrow(
            latest_escrow_id,
            {'from': _agent}
        )

        # set status to False
        token.setStatus(
            False,
            {'from': _issuer}
        )

        # approve transfer
        with brownie.reverts(revert_msg="240205"):
            st_escrow.approveTransfer(
                latest_escrow_id,
                _transfer_approval_data,
                {'from': _issuer}
            )


# TEST_finishEscrow
class TestFinishEscrow:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Transfer approval not required
    def test_normal_1(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        tx = st_escrow.finishEscrow(
            latest_escrow_id,
            {'from': _agent}
        )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert st_escrow.balanceOf(_recipient, token.address) == _escrow_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False
        )

        assert tx.events["EscrowFinished"]["escrowId"] == latest_escrow_id
        assert tx.events["EscrowFinished"]["token"] == token.address
        assert tx.events["EscrowFinished"]["sender"] == _issuer
        assert tx.events["EscrowFinished"]["recipient"] == _recipient
        assert tx.events["EscrowFinished"]["amount"] == _escrow_amount
        assert tx.events["EscrowFinished"]["agent"] == _agent
        assert tx.events["EscrowFinished"]["transferApprovalRequired"] == False

        assert tx.events["HolderChanged"]["token"] == token.address
        assert tx.events["HolderChanged"]["from"] == _issuer
        assert tx.events["HolderChanged"]["to"] == _recipient
        assert tx.events["HolderChanged"]["value"] == _escrow_amount

    # Normal_2
    # Transfer approval required
    def test_normal_2(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address,
            transfer_approval_required=True
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        tx = st_escrow.finishEscrow(
            latest_escrow_id,
            {'from': _agent}
        )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert st_escrow.balanceOf(_recipient, token.address) == 0
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False
        )
        assert st_escrow.getApplicationForTransfer(latest_escrow_id) == (
            token.address,
            _transfer_application_data,
            "",
            True,
            True,
            False
        )

        assert tx.events["EscrowFinished"]["escrowId"] == latest_escrow_id
        assert tx.events["EscrowFinished"]["token"] == token.address
        assert tx.events["EscrowFinished"]["sender"] == _issuer
        assert tx.events["EscrowFinished"]["recipient"] == _recipient
        assert tx.events["EscrowFinished"]["amount"] == _escrow_amount
        assert tx.events["EscrowFinished"]["agent"] == _agent
        assert tx.events["EscrowFinished"]["transferApprovalRequired"] == True

    #######################################
    # Error
    #######################################

    # Error_1
    # The escrowId must be less than or equal to the latest escrow ID.
    def test_error_1(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with brownie.reverts(revert_msg="240301"):
            st_escrow.finishEscrow(
                latest_escrow_id + 1,
                {'from': _agent}
            )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert st_escrow.balanceOf(_recipient, token.address) == 0
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True
        )

    # Error_2
    # Escrow must be valid.
    def test_error_2(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # finish escrow (1)
        latest_escrow_id = st_escrow.latestEscrowId()
        st_escrow.finishEscrow(
            latest_escrow_id,
            {'from': _agent}
        )

        # finish escrow (2)
        with brownie.reverts(revert_msg="240302"):
            st_escrow.finishEscrow(
                latest_escrow_id,
                {'from': _agent}
            )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert st_escrow.balanceOf(_recipient, token.address) == _escrow_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == 0
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False
        )

    # Error_3
    # msg.sender must be the agent of the escrow.
    def test_error_3(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with brownie.reverts(revert_msg="240303"):
            st_escrow.finishEscrow(
                latest_escrow_id,
                {'from': _recipient}
            )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert st_escrow.balanceOf(_recipient, token.address) == 0
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True
        )

    # Error_4
    # The status of the token must be true.
    def test_error_4(self, users, st_escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # set status to False
        token.setStatus(
            False,
            {'from': _issuer}
        )

        # finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with brownie.reverts(revert_msg="240304"):
            st_escrow.finishEscrow(
                latest_escrow_id,
                {'from': _agent}
            )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert st_escrow.balanceOf(_recipient, token.address) == 0
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert st_escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True
        )

    # Error_5
    # Storage is not writable.
    def test_error_5(self, users, st_escrow, st_escrow_storage):
        _admin = users['admin']
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _transfer_application_data = 'transfer_application_data'
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        st_escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _transfer_application_data,
            _data,
            {'from': _issuer}
        )

        # update storage
        st_escrow_storage.upgradeVersion(
            brownie.ZERO_ADDRESS,
            {'from': _admin}
        )

        # finish escrow
        latest_escrow_id = st_escrow.latestEscrowId()
        with brownie.reverts(revert_msg=""):
            st_escrow.finishEscrow(
                latest_escrow_id,
                {'from': _agent}
            )

        # assertion
        assert st_escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert st_escrow.commitmentOf(_issuer, token.address) == _escrow_amount


# TEST_withdraw
class TestWithdraw:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_escrow):
        _issuer = users['issuer']
        _value = 2 ** 256 - 1

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _value,
            {'from': _issuer}
        )

        # withdraw
        tx = st_escrow.withdraw(
            token.address,
            {'from': _issuer}
        )

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2]
        assert st_escrow.balanceOf(_issuer, token.address) == 0

        assert tx.events["Withdrawn"]["token"] == token.address
        assert tx.events["Withdrawn"]["account"] == _issuer

    #######################################
    # Error
    #######################################

    # Error_1
    # The balance must be greater than zero.
    def test_error_1(self, users, st_escrow):
        _issuer = users['issuer']

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # withdraw
        with brownie.reverts(revert_msg="240401"):
            st_escrow.withdraw(
                token.address,
                {'from': _issuer}
            )

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2]
        assert st_escrow.balanceOf(_issuer, token.address) == 0

    # Error_2
    # Storage is not writable.
    def test_error_2(self, users, st_escrow, st_escrow_storage):
        _admin = users['admin']
        _issuer = users['issuer']
        _value = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _value,
            {'from': _issuer}
        )

        # update storage
        st_escrow_storage.upgradeVersion(
            brownie.ZERO_ADDRESS,
            {'from': _admin}
        )

        # withdraw
        with brownie.reverts(revert_msg=""):
            st_escrow.withdraw(
                token.address,
                {'from': _issuer}
            )

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2] - _value
        assert st_escrow.balanceOf(_issuer, token.address) == _value

    # Error_3
    # Must be transferable.
    def test_error_3(self, users, st_escrow):
        _issuer = users['issuer']
        _value = 2 ** 256 - 1

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        token.transfer(
            st_escrow.address,
            _value,
            {'from': _issuer}
        )

        # set to not transferable
        token.setTransferable(
            False,
            {'from': _issuer}
        )

        # withdraw
        with brownie.reverts(revert_msg="110402"):
            st_escrow.withdraw(
                token.address,
                {'from': _issuer}
            )

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
        _issuer = users['issuer']
        _value = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract
        tx = token.transfer(
            st_escrow.address,
            _value,
            {'from': _issuer}
        )

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2] - _value
        assert st_escrow.balanceOf(_issuer, token.address) == _value

        assert tx.events["Deposited"]["token"] == token.address
        assert tx.events["Deposited"]["account"] == _issuer

    # Normal_2
    # Multiple deposit
    def test_normal_2(self, users, st_escrow):
        _issuer = users['issuer']
        _value = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # transfer to escrow contract (1)
        token.transfer(
            st_escrow.address,
            _value,
            {'from': _issuer}
        )

        # transfer to escrow contract (2)
        token.transfer(
            st_escrow.address,
            _value,
            {'from': _issuer}
        )

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2] - _value * 2
        assert st_escrow.balanceOf(_issuer, token.address) == _value * 2

    #######################################
    # Error
    #######################################

    # Error_1
    # Storage is not writable.
    def test_error_1(self, users, st_escrow, st_escrow_storage):
        _admin = users['admin']
        _issuer = users['issuer']
        _value = 100

        # issue token
        deploy_args = init_args()
        token = deploy(
            users,
            deploy_args=deploy_args,
            tradable_exchange=st_escrow.address
        )

        # update storage
        st_escrow_storage.upgradeVersion(
            brownie.ZERO_ADDRESS,
            {'from': _admin}
        )

        # transfer to escrow contract
        with brownie.reverts(revert_msg=""):
            token.transfer(
                st_escrow.address,
                _value,
                {'from': _issuer}
            )

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2]
        assert st_escrow.balanceOf(_issuer, token.address) == 0
