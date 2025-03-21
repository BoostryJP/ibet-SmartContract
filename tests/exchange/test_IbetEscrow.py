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
    name = "test_token"
    symbol = "MEM"
    initial_supply = 2**256 - 1
    tradable_escrow = tradable_escrow
    contact_information = "some_contact_information"
    privacy_policy = "some_privacy_policy"

    deploy_args = [
        name,
        symbol,
        initial_supply,
        tradable_escrow,
        contact_information,
        privacy_policy,
    ]
    return deploy_args


def deploy(users, deploy_args):
    from brownie import IbetStandardToken

    token = users["issuer"].deploy(IbetStandardToken, *deploy_args)
    return token


def deploy_share(users, deploy_args):
    from brownie import IbetShare

    token = users["issuer"].deploy(IbetShare, *deploy_args)
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
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
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
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # assertion
        latest_escrow_id = escrow.latestEscrowId()
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )
        assert escrow.getEscrow(latest_escrow_id) == escrow_storage.getEscrow(
            latest_escrow_id
        )


# TEST_balanceOf
class TestBalanceOf:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, escrow, escrow_storage):
        _issuer = users["issuer"]
        _value = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _value, {"from": _issuer})

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _value
        assert escrow.balanceOf(_issuer, token.address) == escrow_storage.getBalance(
            _issuer, token.address
        )


# TEST_commitmentOf
class TestCommitmentOf:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, escrow, escrow_storage):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # assertion
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert escrow.commitmentOf(
            _issuer, token.address
        ) == escrow_storage.getCommitment(_issuer, token.address)


# TEST_tokenFallback
class TestTokenFallback:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, escrow):
        _issuer = users["issuer"]
        _value = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        tx = token.transfer(escrow.address, _value, {"from": _issuer})

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2] - _value
        assert escrow.balanceOf(_issuer, token.address) == _value

        assert tx.events["Deposited"]["token"] == token.address
        assert tx.events["Deposited"]["account"] == _issuer

    # Normal_2
    # Multiple deposit
    def test_normal_2(self, users, escrow):
        _issuer = users["issuer"]
        _value = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract (1)
        token.transfer(escrow.address, _value, {"from": _issuer})

        # transfer to escrow contract (2)
        token.transfer(escrow.address, _value, {"from": _issuer})

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2] - _value * 2
        assert escrow.balanceOf(_issuer, token.address) == _value * 2

    #######################################
    # Error
    #######################################

    # Error_1
    # Storage is not writable.
    def test_error_1(self, users, escrow, escrow_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _value = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # update storage
        escrow_storage.upgradeVersion(brownie.ZERO_ADDRESS, {"from": _admin})

        # transfer to escrow contract
        with brownie.reverts(revert_msg="220001"):
            token.transfer(escrow.address, _value, {"from": _issuer})

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
        _issuer = users["issuer"]
        _value = 2**256 - 1

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _value, {"from": _issuer})

        # withdraw
        tx = escrow.withdraw(token.address, {"from": _issuer})

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
        _issuer = users["issuer"]

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # withdraw
        with brownie.reverts(revert_msg="230301"):
            escrow.withdraw(token.address, {"from": _issuer})

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2]
        assert escrow.balanceOf(_issuer, token.address) == 0

    # Error_2
    # Storage is not writable.
    def test_error_2(self, users, escrow, escrow_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _value = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _value, {"from": _issuer})

        # update storage
        escrow_storage.upgradeVersion(brownie.ZERO_ADDRESS, {"from": _admin})

        # withdraw
        with brownie.reverts(revert_msg="220001"):
            escrow.withdraw(token.address, {"from": _issuer})

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2] - _value
        assert escrow.balanceOf(_issuer, token.address) == _value

    # Error_3
    # Must be transferable.
    def test_error_3(self, users, escrow):
        _issuer = users["issuer"]
        _value = 2**256 - 1

        # issue token
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
        token = deploy_share(users, deploy_args)

        # set to transferable
        token.setTransferable(True, {"from": _issuer})

        # set to tradable contract
        token.setTradableExchange(escrow.address, {"from": _issuer})

        # transfer to escrow contract
        token.transfer(escrow.address, _value, {"from": _issuer})

        # set to not transferable
        token.setTransferable(False, {"from": _issuer})

        # withdraw
        with brownie.reverts(revert_msg="110402"):
            escrow.withdraw(token.address, {"from": _issuer})

        # assertion
        assert token.balanceOf(_issuer) == 0
        assert token.balanceOf(escrow.address) == deploy_args[3]
        assert escrow.balanceOf(_issuer, token.address) == deploy_args[3]


# TEST_createEscrow
class TestCreateEscrow:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        tx = escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        )
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        latest_escrow_id = escrow.latestEscrowId()
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
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
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow (1)
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # create escrow (2)
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount * 2
        )
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount * 2

    #######################################
    # Error
    #######################################

    # Error_1
    # The amount must be greater than zero.
    def test_error_1(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        with brownie.reverts(revert_msg="230001"):
            escrow.createEscrow(
                token.address, _recipient, 0, _agent, _data, {"from": _issuer}
            )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert escrow.commitmentOf(_issuer, token.address) == 0

    # Error_2
    # The amount must be less than or equal to the balance.
    def test_error_2(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        with brownie.reverts(revert_msg="230002"):
            escrow.createEscrow(
                token.address,
                _recipient,
                _deposit_amount + 1,
                _agent,
                _data,
                {"from": _issuer},
            )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert escrow.commitmentOf(_issuer, token.address) == 0

    # Error_3
    # The status of the token must be true.
    def test_error_3(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # set status to False
        token.setStatus(False, {"from": _issuer})

        # create escrow
        with brownie.reverts(revert_msg="230003"):
            escrow.createEscrow(
                token.address,
                _recipient,
                _escrow_amount,
                _agent,
                _data,
                {"from": _issuer},
            )

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert escrow.commitmentOf(_issuer, token.address) == 0

    # Error_4
    # Storage is not writable.
    def test_error_4(self, users, escrow, escrow_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # update storage
        escrow_storage.upgradeVersion(brownie.ZERO_ADDRESS, {"from": _admin})

        # create escrow
        bf_latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="220001"):
            escrow.createEscrow(
                token.address,
                _recipient,
                _escrow_amount,
                _agent,
                _data,
                {"from": _issuer},
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
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # cancel escrow
        latest_escrow_id = escrow.latestEscrowId()
        tx = escrow.cancelEscrow(latest_escrow_id, {"from": _issuer})

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert escrow.commitmentOf(_issuer, token.address) == 0
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
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
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # cancel escrow
        latest_escrow_id = escrow.latestEscrowId()
        tx = escrow.cancelEscrow(latest_escrow_id, {"from": _agent})

        # assertion
        assert escrow.balanceOf(_issuer, token.address) == _deposit_amount
        assert escrow.commitmentOf(_issuer, token.address) == 0
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
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
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # cancel escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="230101"):
            escrow.cancelEscrow(latest_escrow_id + 1, {"from": _issuer})

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        )
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_2
    # Escrow must be valid.
    def test_error_2(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # cancel escrow (1)
        latest_escrow_id = escrow.latestEscrowId()
        escrow.cancelEscrow(latest_escrow_id, {"from": _issuer})

        # cancel escrow (2)
        with brownie.reverts(revert_msg="230102"):
            escrow.cancelEscrow(latest_escrow_id, {"from": _issuer})

    # Error_3
    # msg.sender must be the sender or agent of the escrow.
    def test_error_3(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # cancel escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="230103"):
            escrow.cancelEscrow(latest_escrow_id, {"from": _recipient})

    # Error_4
    # The status of the token must be true.
    def test_error_4(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # set status to False
        token.setStatus(False, {"from": _issuer})

        # cancel escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="230104"):
            escrow.cancelEscrow(latest_escrow_id, {"from": _issuer})

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        )
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_5
    # Storage is not writable.
    def test_error_5(self, users, escrow, escrow_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # update storage
        escrow_storage.upgradeVersion(brownie.ZERO_ADDRESS, {"from": _admin})

        # cancel escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="220001"):
            escrow.cancelEscrow(latest_escrow_id, {"from": _issuer})

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        )
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount


# TEST_finishEscrow
class TestFinishEscrow:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # finish escrow
        latest_escrow_id = escrow.latestEscrowId()
        tx = escrow.finishEscrow(latest_escrow_id, {"from": _agent})

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        )
        assert escrow.balanceOf(_recipient, token.address) == _escrow_amount
        assert escrow.commitmentOf(_issuer, token.address) == 0
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
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
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # finish escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="230201"):
            escrow.finishEscrow(latest_escrow_id + 1, {"from": _agent})

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        )
        assert escrow.balanceOf(_recipient, token.address) == 0
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_2
    # Escrow must be valid.
    def test_error_2(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # finish escrow (1)
        latest_escrow_id = escrow.latestEscrowId()
        escrow.finishEscrow(latest_escrow_id, {"from": _agent})

        # finish escrow (2)
        with brownie.reverts(revert_msg="230202"):
            escrow.finishEscrow(latest_escrow_id, {"from": _agent})

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        )
        assert escrow.balanceOf(_recipient, token.address) == _escrow_amount
        assert escrow.commitmentOf(_issuer, token.address) == 0
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
        )

    # Error_3
    # msg.sender must be the agent of the escrow.
    def test_error_3(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # finish escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="230203"):
            escrow.finishEscrow(latest_escrow_id, {"from": _recipient})

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        )
        assert escrow.balanceOf(_recipient, token.address) == 0
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_4
    # The status of the token must be true.
    def test_error_4(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # set status to False
        token.setStatus(False, {"from": _issuer})

        # finish escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="230204"):
            escrow.finishEscrow(latest_escrow_id, {"from": _agent})

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        )
        assert escrow.balanceOf(_recipient, token.address) == 0
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_5
    # Storage is not writable.
    def test_error_5(self, users, escrow, escrow_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # update storage
        escrow_storage.upgradeVersion(brownie.ZERO_ADDRESS, {"from": _admin})

        # finish escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="220001"):
            escrow.finishEscrow(latest_escrow_id, {"from": _agent})

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        )
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount


# TEST_bulkFinishEscrow
class TestBulkFinishEscrow:
    #######################################
    # Normal
    #######################################

    # Normal_1_1
    # 1 data
    def test_normal_1_1(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # bulk finish escrow
        latest_escrow_id = escrow.latestEscrowId()
        tx = escrow.bulkFinishEscrow([latest_escrow_id], {"from": _agent})

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        )
        assert escrow.balanceOf(_recipient, token.address) == _escrow_amount
        assert escrow.commitmentOf(_issuer, token.address) == 0
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
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

    # Normal_1_2
    # multiple data
    def test_normal_1_2(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 10000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow_id_list = []
        for _ in range(100):
            escrow.createEscrow(
                token.address,
                _recipient,
                _escrow_amount,
                _agent,
                _data,
                {"from": _issuer},
            )
            latest_escrow_id = escrow.latestEscrowId()
            escrow_id_list.append(latest_escrow_id)

        # bulk finish escrow
        tx = escrow.bulkFinishEscrow(escrow_id_list, {"from": _agent})

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount * 100
        )
        assert escrow.balanceOf(_recipient, token.address) == _escrow_amount * 100
        assert escrow.commitmentOf(_issuer, token.address) == 0

        for escrow_id in escrow_id_list:
            assert escrow.getEscrow(escrow_id) == (
                token.address,
                _issuer,
                _recipient,
                _escrow_amount,
                _agent,
                False,
            )

        for event, escrow_id in zip(tx.events["EscrowFinished"], escrow_id_list):
            assert event["escrowId"] == escrow_id
            assert event["token"] == token.address
            assert event["sender"] == _issuer
            assert event["recipient"] == _recipient
            assert event["amount"] == _escrow_amount
            assert event["agent"] == _agent

        for event, escrow_id in zip(tx.events["HolderChanged"], escrow_id_list):
            assert event["token"] == token.address
            assert event["from"] == _issuer
            assert event["to"] == _recipient
            assert event["value"] == _escrow_amount

    #######################################
    # Error
    #######################################

    # Error_1_1
    # The escrowId must be less than or equal to the latest escrow ID. (1 data)
    def test_error_1_1(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # bulk finish escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="230201"):
            tx = escrow.bulkFinishEscrow([latest_escrow_id + 1], {"from": _agent})
            assert "EscrowFinished" not in tx.events
            assert "HolderChanged" not in tx.events

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        )
        assert escrow.balanceOf(_recipient, token.address) == 0
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_1_2
    # The escrowId must be less than or equal to the latest escrow ID. (multiple data)
    def test_error_1_2(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # bulk finish escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="230201"):
            tx = escrow.bulkFinishEscrow(
                [latest_escrow_id, latest_escrow_id + 1], {"from": _agent}
            )
            assert "EscrowFinished" not in tx.events
            assert "HolderChanged" not in tx.events

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        )
        assert escrow.balanceOf(_recipient, token.address) == 0
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_2_1
    # Escrow must be valid. (1 data)
    def test_error_2_1(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # bulk finish escrow (1)
        latest_escrow_id = escrow.latestEscrowId()
        escrow.bulkFinishEscrow([latest_escrow_id], {"from": _agent})

        # bulk finish escrow (2)
        with brownie.reverts(revert_msg="230202"):
            tx = escrow.bulkFinishEscrow([latest_escrow_id], {"from": _agent})
            assert "EscrowFinished" not in tx.events
            assert "HolderChanged" not in tx.events

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        )
        assert escrow.balanceOf(_recipient, token.address) == _escrow_amount
        assert escrow.commitmentOf(_issuer, token.address) == 0
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
        )

    # Error_2_2
    # Escrow must be valid. (multiple data)
    def test_error_2_2(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow (1)
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )
        valid_escrow_id = escrow.latestEscrowId()

        # create escrow (2)
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )
        latest_escrow_id = escrow.latestEscrowId()

        # bulk finish escrow (1)
        escrow.bulkFinishEscrow([latest_escrow_id], {"from": _agent})

        # bulk finish escrow (2)
        with brownie.reverts(revert_msg="230202"):
            tx = escrow.bulkFinishEscrow(
                [valid_escrow_id, latest_escrow_id], {"from": _agent}
            )
            assert "EscrowFinished" not in tx.events
            assert "HolderChanged" not in tx.events

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount * 2
        )
        assert escrow.balanceOf(_recipient, token.address) == _escrow_amount
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            False,
        )
        assert escrow.getEscrow(valid_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_3_1
    # msg.sender must be the agent of the escrow. (1 data)
    def test_error_3_1(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # bulk finish escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="230203"):
            tx = escrow.bulkFinishEscrow([latest_escrow_id], {"from": _recipient})
            assert "EscrowFinished" not in tx.events
            assert "HolderChanged" not in tx.events

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        )
        assert escrow.balanceOf(_recipient, token.address) == 0
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_3_2
    # msg.sender must be the agent of the escrow. (multiple data)
    def test_error_3_2(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow (1)
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )
        latest_escrow_id_1 = escrow.latestEscrowId()

        # create escrow (2)
        escrow.createEscrow(
            token.address,
            _recipient,
            _escrow_amount,
            _recipient,  # recipient is set as agent
            _data,
            {"from": _issuer},
        )
        latest_escrow_id_2 = escrow.latestEscrowId()

        # bulk finish escrow
        with brownie.reverts(revert_msg="230203"):
            tx = escrow.bulkFinishEscrow(
                [latest_escrow_id_1, latest_escrow_id_2], {"from": _recipient}
            )
            assert "EscrowFinished" not in tx.events
            assert "HolderChanged" not in tx.events

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address)
            == _deposit_amount - _escrow_amount * 2
        )
        assert escrow.balanceOf(_recipient, token.address) == 0
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount * 2
        assert escrow.getEscrow(latest_escrow_id_1) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )
        assert escrow.getEscrow(latest_escrow_id_2) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _recipient,
            True,
        )

    # Error_4_1
    # The status of the token must be true. (1 data)
    def test_error_4_1(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # set status to False
        token.setStatus(False, {"from": _issuer})

        # bulk finish escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="230204"):
            tx = escrow.bulkFinishEscrow([latest_escrow_id], {"from": _agent})
            assert "EscrowFinished" not in tx.events
            assert "HolderChanged" not in tx.events

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        )
        assert escrow.balanceOf(_recipient, token.address) == 0
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
        assert escrow.getEscrow(latest_escrow_id) == (
            token.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_4_2
    # The status of the token must be true. (multiple data)
    def test_error_4_2(self, users, escrow):
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token_1 = deploy(users, deploy_args)
        token_2 = deploy(users, deploy_args)

        # transfer to escrow contract (1)
        token_1.transfer(escrow.address, _deposit_amount, {"from": _issuer})
        # transfer to escrow contract (2)
        token_2.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow (1)
        escrow.createEscrow(
            token_1.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {"from": _issuer},
        )
        latest_escrow_id_1 = escrow.latestEscrowId()

        # create escrow (2)
        escrow.createEscrow(
            token_2.address,
            _recipient,
            _escrow_amount,
            _agent,
            _data,
            {"from": _issuer},
        )
        latest_escrow_id_2 = escrow.latestEscrowId()

        # set status to False
        token_1.setStatus(False, {"from": _issuer})

        # bulk finish escrow
        with brownie.reverts(revert_msg="230204"):
            tx = escrow.bulkFinishEscrow(
                [latest_escrow_id_1, latest_escrow_id_2], {"from": _agent}
            )
            assert "EscrowFinished" not in tx.events
            assert "HolderChanged" not in tx.events

        # assertion
        assert (
            escrow.balanceOf(_issuer, token_1.address)
            == _deposit_amount - _escrow_amount
        )
        assert escrow.balanceOf(_recipient, token_1.address) == 0
        assert escrow.commitmentOf(_issuer, token_1.address) == _escrow_amount
        assert escrow.getEscrow(latest_escrow_id_1) == (
            token_1.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )
        assert (
            escrow.balanceOf(_issuer, token_2.address)
            == _deposit_amount - _escrow_amount
        )
        assert escrow.balanceOf(_recipient, token_2.address) == 0
        assert escrow.commitmentOf(_issuer, token_2.address) == _escrow_amount
        assert escrow.getEscrow(latest_escrow_id_2) == (
            token_2.address,
            _issuer,
            _recipient,
            _escrow_amount,
            _agent,
            True,
        )

    # Error_5
    # Storage is not writable.
    def test_error_5(self, users, escrow, escrow_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _recipient = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _escrow_amount = 100

        # issue token
        deploy_args = init_args(escrow.address)
        token = deploy(users, deploy_args)

        # transfer to escrow contract
        token.transfer(escrow.address, _deposit_amount, {"from": _issuer})

        # create escrow
        escrow.createEscrow(
            token.address, _recipient, _escrow_amount, _agent, _data, {"from": _issuer}
        )

        # update storage
        escrow_storage.upgradeVersion(brownie.ZERO_ADDRESS, {"from": _admin})

        # bulk finish escrow
        latest_escrow_id = escrow.latestEscrowId()
        with brownie.reverts(revert_msg="220001"):
            tx = escrow.bulkFinishEscrow([latest_escrow_id], {"from": _agent})
            assert "EscrowFinished" not in tx.events
            assert "HolderChanged" not in tx.events

        # assertion
        assert (
            escrow.balanceOf(_issuer, token.address) == _deposit_amount - _escrow_amount
        )
        assert escrow.commitmentOf(_issuer, token.address) == _escrow_amount
