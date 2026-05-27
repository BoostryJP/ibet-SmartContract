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
from ape_utils import ZERO_ADDRESS, event_args, has_event, reverts


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


# TEST_deploy
class TestDeploy:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_dvp, st_dvp_storage):
        # assertion
        assert st_dvp.owner() == users["admin"]
        assert st_dvp.storageAddress() == st_dvp_storage.address


# TEST_storageAddress
class TestStorageAddress:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, st_dvp, st_dvp_storage):
        # assertion
        assert st_dvp.storageAddress() == st_dvp_storage.address


# TEST_latestDeliveryId
class TestLatestDeliveryId:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_dvp, st_dvp_storage):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _dvp_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _dvp_amount, _agent, _data, sender=_issuer
        )

        # assertion
        assert st_dvp.latestDeliveryId() == st_dvp_storage.getLatestDeliveryId()


# TEST_getDelivery
class TestGetDelivery:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Data exists
    def test_normal_1(self, users, st_dvp, st_dvp_storage):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # assertion
        latest_delivery_id = st_dvp.latestDeliveryId()
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            False,
            True,
        )
        assert st_dvp.getDelivery(latest_delivery_id) == st_dvp_storage.getDelivery(
            latest_delivery_id
        )

    # Normal_2
    # No data exists
    def test_normal_2(self, users, st_dvp, st_dvp_storage):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # assertion
        delivery_id = st_dvp.latestDeliveryId()
        assert st_dvp.getDelivery(delivery_id) == (
            "0x0000000000000000000000000000000000000000",
            "0x0000000000000000000000000000000000000000",
            "0x0000000000000000000000000000000000000000",
            0,
            "0x0000000000000000000000000000000000000000",
            False,
            False,
        )
        assert st_dvp.getDelivery(delivery_id) == st_dvp_storage.getDelivery(
            delivery_id
        )


# TEST_balanceOf
class TestBalanceOf:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Data exists
    def test_normal_1(self, users, st_dvp, st_dvp_storage):
        _issuer = users["issuer"]
        _value = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _value, sender=_issuer)

        # assertion
        assert st_dvp.balanceOf(_issuer, token.address) == _value
        assert st_dvp.balanceOf(_issuer, token.address) == st_dvp_storage.getBalance(
            _issuer, token.address
        )

    # Normal_2
    # No data exists
    def test_normal_2(self, users, st_dvp, st_dvp_storage):
        _issuer = users["issuer"]
        user1 = users["user1"]
        _value = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _value, sender=_issuer)

        # assertion
        assert st_dvp.balanceOf(user1, token.address) == 0
        assert st_dvp.balanceOf(user1, token.address) == st_dvp_storage.getBalance(
            user1, token.address
        )


# TEST_commitmentOf
class TestCommitmentOf:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # Data exists
    def test_normal_1(self, users, st_dvp, st_dvp_storage):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # assertion
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.commitmentOf(
            _issuer, token.address
        ) == st_dvp_storage.getCommitment(_issuer, token.address)

    # Normal_2
    # Data exists
    def test_normal_2(self, users, st_dvp, st_dvp_storage):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # assertion
        assert st_dvp.commitmentOf(_buyer, token.address) == 0
        assert st_dvp.commitmentOf(
            _buyer, token.address
        ) == st_dvp_storage.getCommitment(_buyer, token.address)


# TEST_createDelivery
class TestCreateDelivery:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        tx = st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        latest_delivery_id = st_dvp.latestDeliveryId()
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            False,
            True,
        )

        event = event_args(tx, st_dvp.DeliveryCreated)
        assert event["deliveryId"] == latest_delivery_id
        assert event["token"] == token.address
        assert event["seller"] == _issuer
        assert event["buyer"] == _buyer
        assert event["amount"] == _delivery_amount
        assert event["agent"] == _agent
        assert event["data"] == _data

    # Normal_2
    # Create twice
    def test_normal_2(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery (1)
        tx1 = st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )
        latest_delivery_id1 = st_dvp.latestDeliveryId()

        # create delivery (2)
        tx2 = st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )
        latest_delivery_id2 = st_dvp.latestDeliveryId()

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount * 2
        )
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount * 2

        assert st_dvp.getDelivery(latest_delivery_id1) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            False,
            True,
        )

        event_1 = event_args(tx1, st_dvp.DeliveryCreated)
        assert event_1["deliveryId"] == latest_delivery_id1
        assert event_1["token"] == token.address
        assert event_1["seller"] == _issuer
        assert event_1["buyer"] == _buyer
        assert event_1["amount"] == _delivery_amount
        assert event_1["agent"] == _agent
        assert event_1["data"] == _data

        assert st_dvp.getDelivery(latest_delivery_id2) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            False,
            True,
        )

        event_2 = event_args(tx2, st_dvp.DeliveryCreated)
        assert event_2["deliveryId"] == latest_delivery_id2
        assert event_2["token"] == token.address
        assert event_2["seller"] == _issuer
        assert event_2["buyer"] == _buyer
        assert event_2["amount"] == _delivery_amount
        assert event_2["agent"] == _agent
        assert event_2["data"] == _data

    #######################################
    # Error
    #######################################

    # Error_1
    # The amount must be greater than zero.
    # 260001
    def test_error_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        with reverts("260001"):
            st_dvp.createDelivery(
                token.address, _buyer, 0, _agent, _data, sender=_issuer
            )

        # assertion
        assert st_dvp.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_dvp.commitmentOf(_issuer, token.address) == 0

    # Error_2
    # The amount must be less than or equal to the balance.
    # 260002
    def test_error_2(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        with reverts("260002"):
            st_dvp.createDelivery(
                token.address,
                _buyer,
                _deposit_amount + 1,
                _agent,
                _data,
                sender=_issuer,
            )

        # assertion
        assert st_dvp.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_dvp.commitmentOf(_issuer, token.address) == 0

    # Error_3
    # The status of the token must be true.
    # 260003
    def test_error_3(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # set status to False
        token.setStatus(False, sender=_issuer)

        # create delivery
        with reverts("260003"):
            st_dvp.createDelivery(
                token.address,
                _buyer,
                _delivery_amount,
                _agent,
                _data,
                sender=_issuer,
            )

        # assertion
        assert st_dvp.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_dvp.commitmentOf(_issuer, token.address) == 0

    # Error_4
    # The transferApprovalRequired of the token must be false.
    # 260004
    def test_error_4(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # set status to False
        token.setTransferApprovalRequired(True, sender=_issuer)

        # create delivery
        with reverts("260004"):
            st_dvp.createDelivery(
                token.address,
                _buyer,
                _delivery_amount,
                _agent,
                _data,
                sender=_issuer,
            )

        # assertion
        assert st_dvp.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_dvp.commitmentOf(_issuer, token.address) == 0

    # Error_5
    # Storage is not writable.
    def test_error_5(self, users, st_dvp, st_dvp_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # update storage
        st_dvp_storage.upgradeVersion(ZERO_ADDRESS, sender=_admin)

        # create delivery
        bf_latest_delivery_id = st_dvp.latestDeliveryId()
        with reverts("250001"):
            st_dvp.createDelivery(
                token.address,
                _buyer,
                _delivery_amount,
                _agent,
                _data,
                sender=_issuer,
            )
        af_latest_delivery_id = st_dvp.latestDeliveryId()

        # assertion
        assert bf_latest_delivery_id == af_latest_delivery_id
        assert st_dvp.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_dvp.commitmentOf(_issuer, token.address) == 0


# TEST_cancelDelivery
class TestCancelDelivery:
    #######################################
    # Normal
    #######################################

    # Normal_1
    # msg.sender is the seller of the delivery
    def test_normal_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # cancel delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        tx = st_dvp.cancelDelivery(latest_delivery_id, sender=_issuer)

        # assertion
        assert st_dvp.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_dvp.commitmentOf(_issuer, token.address) == 0
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            False,
            False,
        )

        event = event_args(tx, st_dvp.DeliveryCanceled)
        assert event["deliveryId"] == latest_delivery_id
        assert event["token"] == token.address
        assert event["seller"] == _issuer
        assert event["buyer"] == _buyer
        assert event["amount"] == _delivery_amount
        assert event["agent"] == _agent

    # Normal_2
    # msg.sender is the buyer of the delivery
    def test_normal_2(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # cancel delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        tx = st_dvp.cancelDelivery(latest_delivery_id, sender=_buyer)

        # assertion
        assert st_dvp.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_dvp.commitmentOf(_issuer, token.address) == 0
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            False,
            False,
        )

        event = event_args(tx, st_dvp.DeliveryCanceled)
        assert event["deliveryId"] == latest_delivery_id
        assert event["token"] == token.address
        assert event["seller"] == _issuer
        assert event["buyer"] == _buyer
        assert event["amount"] == _delivery_amount
        assert event["agent"] == _agent

    #######################################
    # Error
    #######################################

    # Error_1
    # The deliveryId must be less than or equal to the latest delivery ID.
    # 260101
    def test_error_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # cancel delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        with reverts("260101"):
            st_dvp.cancelDelivery(latest_delivery_id + 1, sender=_issuer)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            False,
            True,
        )

    # Error_2
    # Delivery must be valid.
    # 260102
    def test_error_2(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # cancel delivery (1)
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.cancelDelivery(latest_delivery_id, sender=_issuer)

        # cancel delivery (2)
        with reverts("260102"):
            st_dvp.cancelDelivery(latest_delivery_id, sender=_issuer)

    # Error_3
    # Delivery must have not been confirmed.
    # 260103
    def test_error_3(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # cancel delivery
        with reverts("260103"):
            st_dvp.cancelDelivery(latest_delivery_id, sender=_buyer)

    # Error_4
    # msg.sender must be the sender or buyer of the delivery.
    # 260104
    def test_error_4(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # cancel delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        with reverts("260104"):
            st_dvp.cancelDelivery(latest_delivery_id, sender=_agent)

    # Error_5
    # Storage is not writable.
    def test_error_5(self, users, st_dvp, st_dvp_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # update storage
        st_dvp_storage.upgradeVersion(ZERO_ADDRESS, sender=_admin)

        # cancel delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        with reverts("250001"):
            st_dvp.cancelDelivery(latest_delivery_id, sender=_issuer)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount


# TEST_confirmDelivery
class TestConfirmDelivery:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        tx = st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)
        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        latest_delivery_id = st_dvp.latestDeliveryId()
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )

        event = event_args(tx, st_dvp.DeliveryConfirmed)
        assert event["deliveryId"] == latest_delivery_id
        assert event["token"] == token.address
        assert event["seller"] == _issuer
        assert event["buyer"] == _buyer
        assert event["amount"] == _delivery_amount
        assert event["agent"] == _agent

    #######################################
    # Error
    #######################################

    # Error_1
    # The deliveryId must be less than or equal to the latest delivery ID.
    # 260201
    def test_error_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # finish delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        with reverts("260201"):
            st_dvp.confirmDelivery(latest_delivery_id + 1, sender=_buyer)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            False,
            True,
        )

    # Error_2
    # Delivery must be valid.
    # 260202
    def test_error_2(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery (1)
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.cancelDelivery(latest_delivery_id, sender=_buyer)

        # confirm delivery (2)
        with reverts("260202"):
            st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # assertion
        assert st_dvp.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_dvp.commitmentOf(_issuer, token.address) == 0
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            False,
            False,
        )

    # Error_3
    # Delivery must have not been confirmed.
    # 260203
    def test_error_3(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery (1)
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # confirm delivery (2)
        with reverts("260203"):
            st_dvp.confirmDelivery(latest_delivery_id, sender=_agent)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )

    # Error_4
    # msg.sender must be the buyer of the delivery.
    # 260204
    def test_error_4(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        with reverts("260204"):
            st_dvp.confirmDelivery(latest_delivery_id, sender=_agent)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            False,
            True,
        )

    # Error_5
    # The status of the token must be true.
    # 260205
    def test_error_5(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # set status to False
        token.setStatus(False, sender=_issuer)

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        with reverts("260205"):
            st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            False,
            True,
        )

    # Error_6
    # The transferApprovalRequired of the token must be false.
    # 260206
    def test_error_6(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # set TransferApprovalRequired to True
        token.setTransferApprovalRequired(True, sender=_issuer)

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        with reverts("260206"):
            st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            False,
            True,
        )

    # Error_7
    # Storage is not writable.
    def test_error_7(self, users, st_dvp, st_dvp_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # update storage
        st_dvp_storage.upgradeVersion(ZERO_ADDRESS, sender=_admin)

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        with reverts("250001"):
            st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount


# TEST_finishDelivery
class TestFinishDelivery:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # finish delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)
        tx = st_dvp.finishDelivery(latest_delivery_id, sender=_agent)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == _delivery_amount
        assert st_dvp.commitmentOf(_issuer, token.address) == 0
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            False,
        )

        finish_event = event_args(tx, st_dvp.DeliveryFinished)
        assert finish_event["deliveryId"] == latest_delivery_id
        assert finish_event["token"] == token.address
        assert finish_event["seller"] == _issuer
        assert finish_event["buyer"] == _buyer
        assert finish_event["amount"] == _delivery_amount
        assert finish_event["agent"] == _agent

        holder_changed_event = event_args(tx, st_dvp.HolderChanged)
        assert holder_changed_event["token"] == token.address
        assert holder_changed_event["from"] == _issuer
        assert holder_changed_event["to"] == _buyer
        assert holder_changed_event["value"] == _delivery_amount

    #######################################
    # Error
    #######################################

    # Error_1
    # The deliveryId must be less than or equal to the latest delivery ID.
    # 260301
    def test_error_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # finish delivery
        with reverts("260301"):
            st_dvp.finishDelivery(latest_delivery_id + 1, sender=_agent)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == 0
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )

    # Error_2
    # Delivery must be valid.
    # 260302
    def test_error_2(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # finish delivery (1)
        st_dvp.finishDelivery(latest_delivery_id, sender=_agent)

        # finish delivery (2)
        with reverts("260302"):
            st_dvp.finishDelivery(latest_delivery_id, sender=_agent)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == _delivery_amount
        assert st_dvp.commitmentOf(_issuer, token.address) == 0
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            False,
        )

    # Error_3
    # Delivery must have been confirmed.
    # 260303
    def test_error_3(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # finish delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        with reverts("260303"):
            st_dvp.finishDelivery(latest_delivery_id, sender=_agent)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == 0
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            False,
            True,
        )

    # Error_4
    # msg.sender must be the agent of the delivery.
    # 260304
    def test_error_4(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # finish delivery
        with reverts("260304"):
            st_dvp.finishDelivery(latest_delivery_id, sender=_buyer)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == 0
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )

    # Error_5
    # The status of the token must be true.
    # 260305
    def test_error_5(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # set status to False
        token.setStatus(False, sender=_issuer)

        # finish delivery
        with reverts("260305"):
            st_dvp.finishDelivery(latest_delivery_id, sender=_agent)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == 0
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )

    # Error_6
    # The transferApprovalRequired of the token must be false.
    # 260306
    def test_error_6(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # set TransferApprovalRequired to True
        token.setTransferApprovalRequired(True, sender=_issuer)

        # finish delivery
        with reverts("260306"):
            st_dvp.finishDelivery(latest_delivery_id, sender=_agent)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == 0
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )

    # Error_7
    # Storage is not writable.
    def test_error_7(self, users, st_dvp, st_dvp_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # update storage
        st_dvp_storage.upgradeVersion(ZERO_ADDRESS, sender=_admin)

        # finish delivery
        with reverts("250001"):
            st_dvp.finishDelivery(latest_delivery_id, sender=_agent)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount


# TEST_bulkFinishDelivery
class TestBulkFinishDelivery:
    #######################################
    # Normal
    #######################################

    # Normal_1_1
    # 1 data
    def test_normal_1_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # bulk finish delivery
        tx = st_dvp.bulkFinishDelivery([latest_delivery_id], sender=_agent)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == _delivery_amount
        assert st_dvp.commitmentOf(_issuer, token.address) == 0
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            False,
        )

        finish_event = event_args(tx, st_dvp.DeliveryFinished)
        assert finish_event["deliveryId"] == latest_delivery_id
        assert finish_event["token"] == token.address
        assert finish_event["seller"] == _issuer
        assert finish_event["buyer"] == _buyer
        assert finish_event["amount"] == _delivery_amount
        assert finish_event["agent"] == _agent

        holder_changed_event = event_args(tx, st_dvp.HolderChanged)
        assert holder_changed_event["token"] == token.address
        assert holder_changed_event["from"] == _issuer
        assert holder_changed_event["to"] == _buyer
        assert holder_changed_event["value"] == _delivery_amount

    # Normal_1_2
    # multiple data
    def test_normal_1_2(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 10000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        delivery_id_list = []
        for _ in range(100):
            st_dvp.createDelivery(
                token.address,
                _buyer,
                _delivery_amount,
                _agent,
                _data,
                sender=_issuer,
            )
            # confirm delivery
            latest_delivery_id = st_dvp.latestDeliveryId()
            st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)
            delivery_id_list.append(latest_delivery_id)

        # bulk finish delivery
        st_dvp.bulkFinishDelivery(delivery_id_list, sender=_agent)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount * 100
        )
        assert st_dvp.balanceOf(_buyer, token.address) == _delivery_amount * 100
        assert st_dvp.commitmentOf(_issuer, token.address) == 0
        for delivery_id in delivery_id_list:
            assert st_dvp.getDelivery(delivery_id) == (
                token.address,
                _issuer,
                _buyer,
                _delivery_amount,
                _agent,
                True,
                False,
            )

    #######################################
    # Error
    #######################################

    # Error_1_1
    # The deliveryId must be less than or equal to the latest delivery ID. (1 data)
    # 260301
    def test_error_1_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # bulk finish delivery
        with reverts("260301"):
            tx = st_dvp.bulkFinishDelivery([latest_delivery_id + 1], sender=_agent)
            assert not has_event(tx, st_dvp.DeliveryFinished)
            assert not has_event(tx, st_dvp.HolderChanged)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == 0
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )

    # Error_1_2
    # The deliveryId must be less than or equal to the latest delivery ID. (multiple data)
    # 260301
    def test_error_1_2(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # bulk finish delivery
        with reverts("260301"):
            tx = st_dvp.bulkFinishDelivery(
                [latest_delivery_id, latest_delivery_id + 1], sender=_agent
            )
            assert not has_event(tx, st_dvp.DeliveryFinished)
            assert not has_event(tx, st_dvp.HolderChanged)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == 0
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )

    # Error_2_1
    # Delivery must be valid. (1 data)
    # 260302
    def test_error_2_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # bulk finish delivery (1)
        st_dvp.bulkFinishDelivery([latest_delivery_id], sender=_agent)

        # bulk finish delivery (2)
        with reverts("260302"):
            tx = st_dvp.bulkFinishDelivery([latest_delivery_id], sender=_agent)
            assert not has_event(tx, st_dvp.DeliveryFinished)
            assert not has_event(tx, st_dvp.HolderChanged)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == _delivery_amount
        assert st_dvp.commitmentOf(_issuer, token.address) == 0
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            False,
        )

    # Error_2_2
    # Delivery must be valid. (multiple data)
    # 260302
    def test_error_2_2(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery (1)
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery (1)
        valid_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(valid_delivery_id, sender=_buyer)

        # create delivery (2)
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # cancel delivery (2)
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.cancelDelivery(latest_delivery_id, sender=_buyer)

        # bulk finish delivery
        with reverts("260302"):
            tx = st_dvp.bulkFinishDelivery(
                [valid_delivery_id, latest_delivery_id], sender=_agent
            )
            assert not has_event(tx, st_dvp.DeliveryFinished)
            assert not has_event(tx, st_dvp.HolderChanged)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == 0
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(valid_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            False,
            False,
        )

    # Error_3_1
    # Delivery must have been confirmed. (1 data)
    # 260303
    def test_error_3_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # bulk finish delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        with reverts("260303"):
            tx = st_dvp.bulkFinishDelivery([latest_delivery_id], sender=_agent)
            assert not has_event(tx, st_dvp.DeliveryFinished)
            assert not has_event(tx, st_dvp.HolderChanged)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == 0
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            False,
            True,
        )

    # Error_3_2
    # Delivery must have been confirmed. (multiple data)
    # 260303
    def test_error_3_2(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery (1)
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        valid_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(valid_delivery_id, sender=_buyer)

        # create delivery (2)
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )
        latest_delivery_id = st_dvp.latestDeliveryId()

        # bulk finish delivery
        with reverts("260303"):
            tx = st_dvp.bulkFinishDelivery(
                [valid_delivery_id, latest_delivery_id], sender=_agent
            )
            assert not has_event(tx, st_dvp.DeliveryFinished)
            assert not has_event(tx, st_dvp.HolderChanged)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount * 2
        )
        assert st_dvp.balanceOf(_buyer, token.address) == 0
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount * 2
        assert st_dvp.getDelivery(valid_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            False,
            True,
        )

    # Error_4_1
    # msg.sender must be the agent of the delivery. (1 data)
    # 260304
    def test_error_4_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # bulk finish delivery
        with reverts("260304"):
            tx = st_dvp.bulkFinishDelivery([latest_delivery_id], sender=_buyer)
            assert not has_event(tx, st_dvp.DeliveryFinished)
            assert not has_event(tx, st_dvp.HolderChanged)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == 0
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )

    # Error_4_2
    # msg.sender must be the agent of the delivery. (multiple data)
    # 260304
    def test_error_4_2(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery (1)
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )
        latest_delivery_id_1 = st_dvp.latestDeliveryId()

        # confirm delivery (1)
        st_dvp.confirmDelivery(latest_delivery_id_1, sender=_buyer)

        # create delivery (2)
        st_dvp.createDelivery(
            token.address,
            _buyer,
            _delivery_amount,
            _buyer,  # buyer is set as agent
            _data,
            sender=_issuer,
        )

        # confirm delivery (2)
        latest_delivery_id_2 = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id_2, sender=_buyer)

        # bulk finish delivery
        with reverts("260304"):
            tx = st_dvp.bulkFinishDelivery(
                [latest_delivery_id_1, latest_delivery_id_2], sender=_agent
            )
            assert not has_event(tx, st_dvp.DeliveryFinished)
            assert not has_event(tx, st_dvp.HolderChanged)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount * 2
        )
        assert st_dvp.balanceOf(_buyer, token.address) == 0
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount * 2
        assert st_dvp.getDelivery(latest_delivery_id_1) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )
        assert st_dvp.getDelivery(latest_delivery_id_2) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _buyer,
            True,
            True,
        )

    # Error_5_1
    # The status of the token must be true. (1 data)
    # 260305
    def test_error_5_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # set status to False
        token.setStatus(False, sender=_issuer)

        # bulk finish delivery
        with reverts("260305"):
            tx = st_dvp.bulkFinishDelivery([latest_delivery_id], sender=_agent)
            assert not has_event(tx, st_dvp.DeliveryFinished)
            assert not has_event(tx, st_dvp.HolderChanged)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == 0
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )

    # Error_5_2
    # The status of the token must be true. (multiple data)
    # 260305
    def test_error_5_2(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token_1 = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_dvp.address
        )
        token_2 = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_dvp.address
        )

        # transfer to DVP contract (1)
        token_1.transfer(st_dvp.address, _deposit_amount, sender=_issuer)
        # transfer to DVP contract (2)
        token_2.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery (1)
        st_dvp.createDelivery(
            token_1.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery (1)
        latest_delivery_id_1 = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id_1, sender=_buyer)

        # create delivery (2)
        st_dvp.createDelivery(
            token_2.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery (2)
        latest_delivery_id_2 = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id_2, sender=_buyer)

        # set status to False
        token_1.setStatus(False, sender=_issuer)

        # bulk finish delivery
        with reverts("260305"):
            tx = st_dvp.bulkFinishDelivery(
                [latest_delivery_id_1, latest_delivery_id_2], sender=_agent
            )
            assert not has_event(tx, st_dvp.DeliveryFinished)
            assert not has_event(tx, st_dvp.HolderChanged)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token_1.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token_1.address) == 0
        assert st_dvp.commitmentOf(_issuer, token_1.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id_1) == (
            token_1.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )
        assert (
            st_dvp.balanceOf(_issuer, token_2.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token_2.address) == 0
        assert st_dvp.commitmentOf(_issuer, token_2.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id_2) == (
            token_2.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )

    # Error_6_1
    # The transferApprovalRequired of the token must be false. (1 data)
    # 260306
    def test_error_6_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # set transferApprovalRequired to True
        token.setTransferApprovalRequired(True, sender=_issuer)

        # bulk finish delivery
        with reverts("260306"):
            tx = st_dvp.bulkFinishDelivery([latest_delivery_id], sender=_agent)
            assert not has_event(tx, st_dvp.DeliveryFinished)
            assert not has_event(tx, st_dvp.HolderChanged)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == 0
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )

    # Error_6_2
    # The transferApprovalRequired of the token must be false. (multiple data)
    # 260306
    def test_error_6_2(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token_1 = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_dvp.address
        )
        token_2 = deploy(
            users, deploy_args=deploy_args, tradable_exchange=st_dvp.address
        )

        # transfer to DVP contract (1)
        token_1.transfer(st_dvp.address, _deposit_amount, sender=_issuer)
        # transfer to DVP contract (2)
        token_2.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery (1)
        st_dvp.createDelivery(
            token_1.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery (1)
        latest_delivery_id_1 = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id_1, sender=_buyer)

        # create delivery (2)
        st_dvp.createDelivery(
            token_2.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery (2)
        latest_delivery_id_2 = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id_2, sender=_buyer)

        # set transferApprovalRequired to True
        token_1.setTransferApprovalRequired(True, sender=_issuer)

        # bulk finish delivery
        with reverts("260306"):
            tx = st_dvp.bulkFinishDelivery(
                [latest_delivery_id_1, latest_delivery_id_2], sender=_agent
            )
            assert not has_event(tx, st_dvp.DeliveryFinished)
            assert not has_event(tx, st_dvp.HolderChanged)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token_1.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token_1.address) == 0
        assert st_dvp.commitmentOf(_issuer, token_1.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id_1) == (
            token_1.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )
        assert (
            st_dvp.balanceOf(_issuer, token_2.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token_2.address) == 0
        assert st_dvp.commitmentOf(_issuer, token_2.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id_2) == (
            token_2.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )

    # Error_5
    # Storage is not writable.
    def test_error_7(self, users, st_dvp, st_dvp_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # update storage
        st_dvp_storage.upgradeVersion(ZERO_ADDRESS, sender=_admin)

        # bulk finish delivery
        with reverts("250001"):
            tx = st_dvp.bulkFinishDelivery([latest_delivery_id], sender=_agent)
            assert not has_event(tx, st_dvp.DeliveryFinished)
            assert not has_event(tx, st_dvp.HolderChanged)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount


# TEST_abortDelivery
class TestAbortDelivery:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # finish delivery
        tx = st_dvp.abortDelivery(latest_delivery_id, sender=_agent)

        # assertion
        assert st_dvp.balanceOf(_issuer, token.address) == _deposit_amount
        assert st_dvp.balanceOf(_buyer, token.address) == 0
        assert st_dvp.commitmentOf(_issuer, token.address) == 0
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            False,
        )

        event = event_args(tx, st_dvp.DeliveryAborted)
        assert event["deliveryId"] == latest_delivery_id
        assert event["token"] == token.address
        assert event["seller"] == _issuer
        assert event["buyer"] == _buyer
        assert event["amount"] == _delivery_amount
        assert event["agent"] == _agent

    #######################################
    # Error
    #######################################

    # Error_1
    # The deliveryId must be less than or equal to the latest delivery ID.
    # 260401
    def test_error_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # finish delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)
        with reverts("260401"):
            st_dvp.abortDelivery(latest_delivery_id + 1, sender=_agent)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == 0
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )

    # Error_2
    # Delivery must be valid.
    # 260402
    def test_error_2(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # finish delivery
        st_dvp.finishDelivery(latest_delivery_id, sender=_agent)

        # abort delivery
        with reverts("260402"):
            st_dvp.abortDelivery(latest_delivery_id, sender=_agent)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == _delivery_amount
        assert st_dvp.commitmentOf(_issuer, token.address) == 0
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            False,
        )

    # Error_3
    # Delivery must have been confirmed.
    # 260403
    def test_error_3(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # abort delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        with reverts("260403"):
            st_dvp.abortDelivery(latest_delivery_id, sender=_agent)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == 0
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            False,
            True,
        )

    # Error_4
    # msg.sender must be the agent of the delivery.
    # 260404
    def test_error_4(self, users, st_dvp):
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # finish delivery
        with reverts("260404"):
            st_dvp.abortDelivery(latest_delivery_id, sender=_buyer)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.balanceOf(_buyer, token.address) == 0
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount
        assert st_dvp.getDelivery(latest_delivery_id) == (
            token.address,
            _issuer,
            _buyer,
            _delivery_amount,
            _agent,
            True,
            True,
        )

    # Error_5
    # Storage is not writable.
    def test_error_5(self, users, st_dvp, st_dvp_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _buyer = users["user1"]
        _agent = users["agent"]
        _data = "test_data"
        _deposit_amount = 1000
        _delivery_amount = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _deposit_amount, sender=_issuer)

        # create delivery
        st_dvp.createDelivery(
            token.address, _buyer, _delivery_amount, _agent, _data, sender=_issuer
        )

        # confirm delivery
        latest_delivery_id = st_dvp.latestDeliveryId()
        st_dvp.confirmDelivery(latest_delivery_id, sender=_buyer)

        # update storage
        st_dvp_storage.upgradeVersion(ZERO_ADDRESS, sender=_admin)

        # finish delivery
        with reverts("250001"):
            st_dvp.finishDelivery(latest_delivery_id, sender=_agent)

        # assertion
        assert (
            st_dvp.balanceOf(_issuer, token.address)
            == _deposit_amount - _delivery_amount
        )
        assert st_dvp.commitmentOf(_issuer, token.address) == _delivery_amount


# TEST_withdrawPartial
class TestWithdrawPartial:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _value = 2**256 - 1

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _value, sender=_issuer)

        # withdraw
        tx = st_dvp.withdrawPartial(token.address, 2**256 - 1, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2]
        assert st_dvp.balanceOf(_issuer, token.address) == 0

        event = event_args(tx, st_dvp.Withdrawn)
        assert event["token"] == token.address
        assert event["account"] == _issuer

    #######################################
    # Error
    #######################################

    # Error_1
    # Insufficient balance
    def test_error_1(self, users, st_dvp):
        _issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, 10, sender=_issuer)

        # withdraw
        with reverts("260601"):
            st_dvp.withdrawPartial(token.address, 11, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2] - 10
        assert st_dvp.balanceOf(_issuer, token.address) == 10

    # Error_2
    # Storage is not writable.
    def test_error_2(self, users, st_dvp, st_dvp_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _value = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _value, sender=_issuer)

        # update storage
        st_dvp_storage.upgradeVersion(ZERO_ADDRESS, sender=_admin)

        # withdraw
        with reverts("250001"):
            st_dvp.withdrawPartial(token.address, 10, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2] - _value
        assert st_dvp.balanceOf(_issuer, token.address) == _value

    # Error_3
    # Must be transferable.
    def test_error_3(self, users, st_dvp):
        _issuer = users["issuer"]
        _value = 2**256 - 1

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _value, sender=_issuer)

        # set to not transferable
        token.setTransferable(False, sender=_issuer)

        # withdraw
        with reverts("110402"):
            st_dvp.withdrawPartial(token.address, 10, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == 0
        assert token.balanceOf(st_dvp.address) == deploy_args[3]
        assert st_dvp.balanceOf(_issuer, token.address) == deploy_args[3]


# TEST_withdraw
class TestWithdraw:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _value = 2**256 - 1

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _value, sender=_issuer)

        # withdraw
        tx = st_dvp.withdraw(token.address, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2]
        assert st_dvp.balanceOf(_issuer, token.address) == 0

        event = event_args(tx, st_dvp.Withdrawn)
        assert event["token"] == token.address
        assert event["account"] == _issuer

    #######################################
    # Error
    #######################################

    # Error_1
    # The balance must be greater than zero.
    def test_error_1(self, users, st_dvp):
        _issuer = users["issuer"]

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # withdraw
        with reverts("260501"):
            st_dvp.withdraw(token.address, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2]
        assert st_dvp.balanceOf(_issuer, token.address) == 0

    # Error_2
    # Storage is not writable.
    def test_error_2(self, users, st_dvp, st_dvp_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _value = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _value, sender=_issuer)

        # update storage
        st_dvp_storage.upgradeVersion(ZERO_ADDRESS, sender=_admin)

        # withdraw
        with reverts("250001"):
            st_dvp.withdraw(token.address, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2] - _value
        assert st_dvp.balanceOf(_issuer, token.address) == _value

    # Error_3
    # Must be transferable.
    def test_error_3(self, users, st_dvp):
        _issuer = users["issuer"]
        _value = 2**256 - 1

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        token.transfer(st_dvp.address, _value, sender=_issuer)

        # set to not transferable
        token.setTransferable(False, sender=_issuer)

        # withdraw
        with reverts("110402"):
            st_dvp.withdraw(token.address, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == 0
        assert token.balanceOf(st_dvp.address) == deploy_args[3]
        assert st_dvp.balanceOf(_issuer, token.address) == deploy_args[3]


# TEST_tokenFallback
class TestTokenFallback:
    #######################################
    # Normal
    #######################################

    # Normal_1
    def test_normal_1(self, users, st_dvp):
        _issuer = users["issuer"]
        _value = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract
        tx = token.transfer(st_dvp.address, _value, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2] - _value
        assert st_dvp.balanceOf(_issuer, token.address) == _value

        event = event_args(tx, st_dvp.Deposited)
        assert event["token"] == token.address
        assert event["account"] == _issuer

    # Normal_2
    # Multiple deposit
    def test_normal_2(self, users, st_dvp):
        _issuer = users["issuer"]
        _value = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # transfer to DVP contract (1)
        token.transfer(st_dvp.address, _value, sender=_issuer)

        # transfer to DVP contract (2)
        token.transfer(st_dvp.address, _value, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2] - _value * 2
        assert st_dvp.balanceOf(_issuer, token.address) == _value * 2

    #######################################
    # Error
    #######################################

    # Error_1
    # Storage is not writable.
    def test_error_1(self, users, st_dvp, st_dvp_storage):
        _admin = users["admin"]
        _issuer = users["issuer"]
        _value = 100

        # issue token
        deploy_args = init_args()
        token = deploy(users, deploy_args=deploy_args, tradable_exchange=st_dvp.address)

        # update storage
        st_dvp_storage.upgradeVersion(ZERO_ADDRESS, sender=_admin)

        # transfer to DVP contract
        with reverts("250001"):
            token.transfer(st_dvp.address, _value, sender=_issuer)

        # assertion
        assert token.balanceOf(_issuer) == deploy_args[2]
        assert st_dvp.balanceOf(_issuer, token.address) == 0
