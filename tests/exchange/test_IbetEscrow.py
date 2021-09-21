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


def init_args(tradable_escrow):
    name = 'test_token'
    symbol = 'MEM'
    initial_supply = 2 ** 256 - 1
    tradable_escrow = tradable_escrow
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'

    deploy_args = [
        name,
        symbol,
        initial_supply,
        tradable_escrow,
        contact_information,
        privacy_policy
    ]
    return deploy_args


def deploy(users, deploy_args):
    from brownie import IbetStandardToken
    token = users["issuer"].deploy(
        IbetStandardToken,
        *deploy_args
    )
    return token


# TEST_deploy
class TestDeploy:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, escrow, escrow_storage):
        # assertion
        assert escrow.owner() == users["admin"]
        assert escrow.storageAddress() == escrow_storage.address


# TEST_storageAddress
class TestStorageAddress:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, escrow, escrow_storage):
        # assertion
        assert escrow.storageAddress() == escrow_storage.address


# TEST_latestEscrowId
class TestLatestEscrowId:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, escrow, escrow_storage):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # assertion
        assert escrow.latestEscrowId() == escrow_storage.getLatestEscrowId()


# TEST_getEscrow
class TestGetEscrow:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, escrow, escrow_storage):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # assertion
        latest_escrow_id = escrow.latestEscrowId()
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True
        )
        assert escrow.getEscrow(latest_escrow_id) == escrow_storage.getEscrow(latest_escrow_id)


# TEST_balanceOf
class TestBalanceOf:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, escrow, escrow_storage):
        _issuer = users['issuer']
        _value = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _value,
            {'from': _issuer}
        )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _value
        assert escrow.balanceOf(_issuer, token.address) == \
               escrow_storage.getBalance(_issuer, token.address)


# TEST_commitmentOf
class TestCommitmentOf:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, escrow, escrow_storage):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # assertion
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert escrow.commitmentOf(_issuer, token.address) == \
               escrow_storage.getCommitment(_issuer, token.address)


# TEST_tokenFallback
class TestTokenFallback:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, escrow):
        _issuer = users['issuer']
        _value = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        tx = token.transfer(
            escrow.address,
            _value,
            {'from': _issuer}
        )

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2] - _value
        assert escrow.balanceOf(_issuer, token.address) == _value

        assert tx.events["Deposited"]["token"] == token.address
        assert tx.events["Deposited"]["account"] == _issuer

    # Normal_2
    # Multiple deposit
    def test_normal_2(self, users, escrow):
        _issuer = users['issuer']
        _value = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract (1)
        token.transfer(
            escrow.address,
            _value,
            {'from': _issuer}
        )

        # transfer to escrow contract (2)
        token.transfer(
            escrow.address,
            _value,
            {'from': _issuer}
        )

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2] - _value * 2
        assert escrow.balanceOf(_issuer, token.address) == _value * 2

    #######################################
    # Error
    #######################################

    # Error_1
    # Storage is not writable.
    def test_error_1(self, users, escrow, escrow_storage):
        _admin = users['admin']
        _issuer = users['issuer']
        _value = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # update storage
        escrow_storage.upgradeVersion(
            brownie.ZERO_ADDRESS,
            {'from': _admin}
        )

        # transfer to escrow contract
        with brownie.reverts():
            token.transfer(
                escrow.address,
                _value,
                {'from': _issuer}
            )

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2]
        assert escrow.balanceOf(_issuer, token.address) == 0


# TEST_withdraw
class TestWithdraw:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, escrow):
        _issuer = users['issuer']
        _value = 2 ** 256 - 1

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _value,
            {'from': _issuer}
        )

        # withdraw
        tx = escrow.withdraw(
            token.address,
            {'from': _issuer}
        )

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2]
        assert escrow.balanceOf(_issuer, token.address) == 0

        assert tx.events["Withdrawn"]["token"] == token.address
        assert tx.events["Withdrawn"]["account"] == _issuer

    #######################################
    # Error
    #######################################

    # Error_1
    # The balance must be greater than zero.
    def test_error_1(self, users, escrow):
        _issuer = users['issuer']

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # withdraw
        with brownie.reverts(revert_msg="The balance must be greater than zero."):
            escrow.withdraw(
                token.address,
                {'from': _issuer}
            )

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2]
        assert escrow.balanceOf(_issuer, token.address) == 0

    # Error_2
    # Storage is not writable.
    def test_error_2(self, users, escrow, escrow_storage):
        _admin = users['admin']
        _issuer = users['issuer']
        _value = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _value,
            {'from': _issuer}
        )

        # update storage
        escrow_storage.upgradeVersion(
            brownie.ZERO_ADDRESS,
            {'from': _admin}
        )

        # withdraw
        with brownie.reverts():
            escrow.withdraw(
                token.address,
                {'from': _issuer}
            )

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2] - _value
        assert escrow.balanceOf(_issuer, token.address) == _value


# TEST_createEscrow
class TestCreateEscrow:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        tx = escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        latest_escrow_id = escrow.latestEscrowId()
        assert escrow.getEscrow(latest_escrow_id) == (
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
    # Create twice
    def test_normal_2(self, users, escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow (1)
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # create escrow (2)
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount * 2
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount * 2

    #######################################
    # Error
    #######################################

    # Error_1
    # The amount must be greater than zero.
    def test_error_1(self, users, escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        with brownie.reverts(revert_msg="The amount must be greater than zero."):
            escrow.createEscrow(
                token.address,
                _recipient,
                0,
                _agent,
                _data,
                {'from': _issuer}
            )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert escrow.commitmentOf(_issuer, token.address) == 0

    # Error_2
    # The amount must be less than or equal to the balance.
    def test_error_2(self, users, escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        with brownie.reverts(revert_msg="The amount must be less than or equal to the balance."):
            escrow.createEscrow(
                token.address,
                _recipient,
                _deposit_amount + 1,
                _agent,
                _data,
                {'from': _issuer}
            )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert escrow.commitmentOf(_issuer, token.address) == 0

    # Error_3
    # The status of the token must be true.
    def test_error_3(self, users, escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # set status to False
        token.setStatus(
            False,
            {'from': _issuer}
        )

        # create escrow
        with brownie.reverts(revert_msg="The status of the token must be true."):
            escrow.createEscrow(
                token.address,
                _recipient,
                _escrow_amount,
                _agent,
                _data,
                {'from': _issuer}
            )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert escrow.commitmentOf(_issuer, token.address) == 0

    # Error_4
    # Storage is not writable.
    def test_error_4(self, users, escrow, escrow_storage):
        _admin = users['admin']
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # update storage
        escrow_storage.upgradeVersion(
            brownie.ZERO_ADDRESS,
            {'from': _admin}
        )

        # create escrow
        bf_latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts():
            escrow.createEscrow(
                token.address,
                _recipient,
                _escrow_amount,
                _agent,
                _data,
                {'from': _issuer}
            )
        af_latest_escrow_id = escrow.latestEscrowId()

        # assertion
        assert bf_latest_escrow_id == af_latest_escrow_id
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert escrow.commitmentOf(_issuer, token.address) == 0


# TEST_cancelEscrow
class TestCancelEscrow:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # msg.sender is the sender of the escrow
    def test_normal_1(self, users, escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # cancel escrow
        latest_escrow_id = escrow.latestEscrowId()
        tx = escrow.cancelEscrow(
            latest_escrow_id,
            {'from': _issuer}
        )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert escrow.commitmentOf(_issuer, token.address) == 0
        assert escrow.getEscrow(latest_escrow_id) == (
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
    def test_normal_2(self, users, escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # cancel escrow
        latest_escrow_id = escrow.latestEscrowId()
        tx = escrow.cancelEscrow(
            latest_escrow_id,
            {'from': _agent}
        )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert escrow.commitmentOf(_issuer, token.address) == 0
        assert escrow.getEscrow(latest_escrow_id) == (
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
    def test_error_1(self, users, escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # cancel escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="The escrowId must be less than or equal to the latest escrow ID."):
            escrow.cancelEscrow(
                latest_escrow_id + 1,
                {'from': _issuer}
            )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True
        )

    # Error_2
    # Escrow must be valid.
    def test_error_2(self, users, escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # cancel escrow (1)
        latest_escrow_id = escrow.latestEscrowId()
        escrow.cancelEscrow(
            latest_escrow_id,
            {'from': _issuer}
        )

        # cancel escrow (2)
        with brownie.reverts(revert_msg="Escrow must be valid."):
            escrow.cancelEscrow(
                latest_escrow_id,
                {'from': _issuer}
            )

    # Error_3
    # msg.sender must be the sender or agent of the escrow.
    def test_error_3(self, users, escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # cancel escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="msg.sender must be the sender or agent of the escrow."):
            escrow.cancelEscrow(
                latest_escrow_id,
                {'from': _recipient}
            )

    # Error_4
    # The status of the token must be true.
    def test_error_4(self, users, escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # set status to False
        token.setStatus(
            False,
            {'from': _issuer}
        )

        # cancel escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="The status of the token must be true."):
            escrow.cancelEscrow(
                latest_escrow_id,
                {'from': _issuer}
            )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True
        )

    # Error_5
    # Storage is not writable.
    def test_error_5(self, users, escrow, escrow_storage):
        _admin = users['admin']
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # update storage
        escrow_storage.upgradeVersion(
            brownie.ZERO_ADDRESS,
            {'from': _admin}
        )

        # cancel escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts():
            escrow.cancelEscrow(
                latest_escrow_id,
                {'from': _issuer}
            )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount


# TEST_finishEscrow
class TestFinishEscrow:

    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # finish escrow
        latest_escrow_id = escrow.latestEscrowId()
        tx = escrow.finishEscrow(
            latest_escrow_id,
            {'from': _agent}
        )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert escrow.balanceOf(_recipient, token.address) == _escrow_amount
        assert escrow.commitmentOf(_issuer, token.address) == 0
        assert escrow.getEscrow(latest_escrow_id) == (
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

        assert tx.events["HolderChanged"]["token"] == token.address
        assert tx.events["HolderChanged"]["from"] == _issuer
        assert tx.events["HolderChanged"]["to"] == _recipient
        assert tx.events["HolderChanged"]["value"] == _escrow_amount

    #######################################
    # Error
    #######################################

    # Error_1
    # The escrowId must be less than or equal to the latest escrow ID.
    def test_error_1(self, users, escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # finish escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="The escrowId must be less than or equal to the latest escrow ID."):
            escrow.finishEscrow(
                latest_escrow_id + 1,
                {'from': _agent}
            )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert escrow.balanceOf(_recipient, token.address) == 0
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True
        )

    # Error_2
    # Escrow must be valid.
    def test_error_2(self, users, escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # finish escrow (1)
        latest_escrow_id = escrow.latestEscrowId()
        escrow.finishEscrow(
            latest_escrow_id,
            {'from': _agent}
        )

        # finish escrow (2)
        with brownie.reverts(revert_msg="Escrow must be valid."):
            escrow.finishEscrow(
                latest_escrow_id,
                {'from': _agent}
            )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert escrow.balanceOf(_recipient, token.address) == _escrow_amount
        assert escrow.commitmentOf(_issuer, token.address) == 0
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False
        )

    # Error_3
    # msg.sender must be the agent of the escrow.
    def test_error_3(self, users, escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # finish escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="msg.sender must be the agent of the escrow."):
            escrow.finishEscrow(
                latest_escrow_id,
                {'from': _recipient}
            )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert escrow.balanceOf(_recipient, token.address) == 0
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True
        )

    # Error_4
    # The status of the token must be true.
    def test_error_4(self, users, escrow):
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # set status to False
        token.setStatus(
            False,
            {'from': _issuer}
        )

        # finish escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="The status of the token must be true."):
            escrow.finishEscrow(
                latest_escrow_id,
                {'from': _agent}
            )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert escrow.balanceOf(_recipient, token.address) == 0
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True
        )

    # Error_5
    # Storage is not writable.
    def test_error_5(self, users, escrow, escrow_storage):
        _admin = users['admin']
        _issuer = users['issuer']
        _recipient = users['user1']
        _agent = users['agent']
        _data = 'test_data'
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(
            escrow.address,
            _deposit_amount,
            {'from': _issuer}
        )

        # create escrow
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {'from': _issuer}
        )

        # update storage
        escrow_storage.upgradeVersion(
            brownie.ZERO_ADDRESS,
            {'from': _admin}
        )

        # finish escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts():
            escrow.finishEscrow(
                latest_escrow_id,
                {'from': _agent}
            )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount