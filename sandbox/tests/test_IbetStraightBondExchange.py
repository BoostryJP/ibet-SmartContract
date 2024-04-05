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

import pytest
import utils
from eth_utils import to_checksum_address

"""
共通処理
"""


# PersonalInfo登録
def personalinfo_register(personalinfo, trader, issuer):
    message = "some_message"
    personalinfo.register.transact(issuer, message, {"from": trader})


# PaymentGatewayアカウント登録
def payment_gateway_register(payment_gateway, trader, agent):
    message = "some_message"
    payment_gateway.register.transact(agent, message, {"from": trader})


# PaymentGatewayアカウント認可
def payment_gateway_approve(payment_gateway, trader, agent):
    payment_gateway.approve.transact(trader, {"from": agent})


# Bondトークンを取引所にデポジット
def bond_transfer(bond_token, bond_exchange, trader, amount):
    bond_token.transfer.transact(bond_exchange.address, amount, {"from": trader})


"""
TEST_デプロイ
"""


# ＜正常系1＞
# Deploy　→　正常
def test_deploy_normal_1(
    users, bond_exchange, bond_exchange_storage, personal_info, payment_gateway
):
    owner = bond_exchange.owner()
    personal_info_address = bond_exchange.personalInfoAddress()
    payment_gateway_address = bond_exchange.paymentGatewayAddress()
    storage_address = bond_exchange.storageAddress()

    assert owner == users["admin"]
    assert personal_info_address == to_checksum_address(personal_info.address)
    assert payment_gateway_address == to_checksum_address(payment_gateway.address)
    assert storage_address == to_checksum_address(bond_exchange_storage.address)


# ＜エラー系1＞
# 入力値の型誤り（PaymentGatewayアドレス）
def test_deploy_error_1(users, IbetStraightBondExchange, personal_info):
    exchange_owner = users["admin"]

    deploy_args = [1234, personal_info.address]

    with pytest.raises(ValueError):
        exchange_owner.deploy(IbetStraightBondExchange, *deploy_args)


# ＜エラー系2＞
# 入力値の型誤り（PersonalInfoアドレス）
def test_deploy_error_2(users, IbetStraightBondExchange, payment_gateway):
    exchange_owner = users["admin"]
    deploy_args = [payment_gateway.address, 1234]
    with pytest.raises(ValueError):
        exchange_owner.deploy(IbetStraightBondExchange, *deploy_args)


"""
TEST_Make注文（createOrder）
"""


# 正常系１
# ＜発行体＞新規発行 -> ＜投資家＞新規注文（買）
def test_createorder_normal_1(users, bond_exchange, personal_info, payment_gateway):
    issuer = users["issuer"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文（買）
    _amount = 100
    _price = 123
    _isBuy = True
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )

    order_id = bond_exchange.latestOrderId()
    orderbook = bond_exchange.getOrder(order_id)

    assert orderbook == [
        issuer.address,
        to_checksum_address(bond_token.address),
        _amount,
        _price,
        _isBuy,
        agent.address,
        False,
    ]
    assert bond_token.balanceOf(issuer) == deploy_args[2]


# 正常系2
# ＜発行体＞新規発行 -> ＜発行体＞新規注文（売）
def test_createorder_normal_2(users, bond_exchange, personal_info, payment_gateway):
    issuer = users["issuer"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット
    _amount = 100
    bond_token.transfer.transact(bond_exchange.address, _amount, {"from": issuer})

    # 新規注文（売）
    _price = 123
    _isBuy = False
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )

    order_id = bond_exchange.latestOrderId()
    orderbook = bond_exchange.getOrder(order_id)
    commitment = bond_exchange.commitmentOf(issuer, bond_token.address)
    balance = bond_token.balanceOf(issuer)

    assert orderbook == [
        issuer.address,
        to_checksum_address(bond_token.address),
        _amount,
        _price,
        _isBuy,
        agent.address,
        False,
    ]
    assert balance == deploy_args[2] - _amount
    assert commitment == _amount


# エラー系1
# 入力値の型誤り（_token）
def test_createorder_error_1(users, bond_exchange):
    issuer = users["issuer"]
    agent = users["agent"]

    # 新規注文
    _price = 123
    _isBuy = False
    _amount = 100

    with pytest.raises(ValueError):
        bond_exchange.createOrder.transact(
            "1234", _amount, _price, _isBuy, agent, {"from": issuer}
        )

    with pytest.raises(ValueError):
        bond_exchange.createOrder.transact(
            1234, _amount, _price, _isBuy, agent, {"from": issuer}
        )


# エラー系2
# 入力値の型誤り（_amount）
def test_createorder_error_2(users, bond_exchange, personal_info):
    issuer = users["issuer"]
    agent = users["agent"]

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文
    _price = 123
    _isBuy = False

    with pytest.raises(OverflowError):
        bond_exchange.createOrder.transact(
            bond_token.address, -1, _price, _isBuy, agent, {"from": issuer}
        )

    with pytest.raises(OverflowError):
        bond_exchange.createOrder.transact(
            bond_token.address, 2**256, _price, _isBuy, agent, {"from": issuer}
        )

    with pytest.raises(TypeError):
        bond_exchange.createOrder.transact(
            bond_token.address, "abc", _price, _isBuy, agent, {"from": issuer}
        )


# エラー系3
# 入力値の型誤り（_price）
def test_createorder_error_3(users, bond_exchange, personal_info):
    issuer = users["issuer"]
    agent = users["agent"]

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文
    _amount = 100
    _isBuy = False

    with pytest.raises(OverflowError):
        bond_exchange.createOrder.transact(
            bond_token.address, _amount, -1, _isBuy, agent, {"from": issuer}
        )

    with pytest.raises(OverflowError):
        bond_exchange.createOrder.transact(
            bond_token.address, _amount, 2**256, _isBuy, agent, {"from": issuer}
        )

    with pytest.raises(TypeError):
        bond_exchange.createOrder.transact(
            bond_token.address, _amount, "abc", _isBuy, agent, {"from": issuer}
        )


# エラー系4
# 入力値の型誤り（_isBuy）
def test_createorder_error_4(users, bond_exchange, personal_info):
    issuer = users["issuer"]
    agent = users["agent"]

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文
    _amount = 100
    _price = 123

    with pytest.raises(ValueError):
        bond_exchange.createOrder.transact(
            bond_token.address, _amount, _price, 1234, agent, {"from": issuer}
        )

    with pytest.raises(ValueError):
        bond_exchange.createOrder.transact(
            bond_token.address, _amount, _price, "True", agent, {"from": issuer}
        )


# エラー系5
# 入力値の型誤り（_agent）
def test_createorder_error_5(users, bond_exchange, personal_info):
    issuer = users["issuer"]

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文
    _price = 123
    _isBuy = False
    _amount = 100

    with pytest.raises(ValueError):
        bond_exchange.createOrder.transact(
            bond_token.address, _amount, _price, _isBuy, "1234", {"from": issuer}
        )

    with pytest.raises(ValueError):
        bond_exchange.createOrder.transact(
            bond_token.address, _amount, _price, _isBuy, 1234, {"from": issuer}
        )


# エラー系6-1
# 買注文数量が0の場合
def test_createorder_error_6_1(users, bond_exchange, personal_info, payment_gateway):
    issuer = users["issuer"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文（買）
    _amount = 0
    _price = 123
    _isBuy = True
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )  # エラーになる

    commitment = bond_exchange.commitmentOf(issuer, bond_token.address)
    balance = bond_token.balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系6-2
# 売注文数量が0の場合
def test_createorder_error_6_2(users, bond_exchange, personal_info, payment_gateway):
    issuer = users["issuer"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット
    _amount = 100
    bond_token.transfer.transact(bond_exchange.address, _amount, {"from": issuer})

    # 新規注文（売）
    _amount = 0
    _price = 123
    _isBuy = False
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )  # エラーになる

    commitment = bond_exchange.commitmentOf(issuer, bond_token.address)
    balance = bond_token.balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系7-1
# 未認可のアカウントアドレスからの注文（買）
def test_createorder_error_7_1(users, bond_exchange, personal_info, payment_gateway):
    issuer = users["issuer"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)  # 未認可状態

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文（買）
    _amount = 100
    _price = 123
    _isBuy = False
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )  # エラーになる

    commitment = bond_exchange.commitmentOf(issuer, bond_token.address)
    balance = bond_token.balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系7-2
# 未認可のアカウントアドレスからの注文（売）
def test_createorder_error_7_2(users, bond_exchange, personal_info):
    issuer = users["issuer"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)  # 未認可状態

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット
    _amount = 100
    bond_token.transfer.transact(bond_exchange.address, _amount, {"from": issuer})

    # 新規注文（売）
    _amount = 0
    _price = 123
    _isBuy = False
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )  # エラーになる

    commitment = bond_exchange.commitmentOf(issuer, bond_token.address)
    balance = bond_token.balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系8-1
# 名簿用個人情報が登録されていない場合（買注文）
def test_createorder_error_8_1(users, bond_exchange, payment_gateway, personal_info):
    issuer = users["issuer"]
    agent = users["agent"]

    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文（買）
    _amount = 100
    _price = 123
    _isBuy = True
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )  # エラーになる

    commitment = bond_exchange.commitmentOf(issuer, bond_token.address)
    balance = bond_token.balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系8-2
# 名簿用個人情報が登録されていない場合（売注文）
def test_createorder_error_8_2(users, bond_exchange, payment_gateway, personal_info):
    issuer = users["issuer"]
    agent = users["agent"]

    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット
    _amount = 100
    bond_token.transfer.transact(bond_exchange.address, _amount, {"from": issuer})

    # 新規注文（売）
    _amount = 100
    _price = 123
    _isBuy = False
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )  # エラーになる

    commitment = bond_exchange.commitmentOf(issuer, bond_token.address)
    balance = bond_token.balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系9-1
# 償還済みフラグがTrueの場合
# ＜発行体＞新規発行 -> ＜発行体＞償還設定 -> ＜発行体＞新規注文（買）
def test_createorder_error_9_1(users, bond_exchange, personal_info, payment_gateway):
    issuer = users["issuer"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 償還設定
    bond_token.redeem.transact({"from": issuer})

    # 新規注文（買）
    _price = 123
    _isBuy = True
    _amount = 100
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )  # エラーになる

    commitment = bond_exchange.commitmentOf(issuer, bond_token.address)
    balance = bond_token.balanceOf(issuer)
    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系9-2
# 償還済みフラグがTrueの場合
# ＜発行体＞新規発行 -> ＜発行体＞償還設定 -> ＜発行体＞新規注文（売）
def test_createorder_error_9_2(users, bond_exchange, personal_info, payment_gateway):
    issuer = users["issuer"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット
    _amount = 100
    bond_token.transfer.transact(bond_exchange.address, _amount, {"from": issuer})

    # 償還設定
    bond_token.redeem.transact({"from": issuer})

    # 新規注文（売）
    _price = 123
    _isBuy = False
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )  # エラーになる

    commitment = bond_exchange.commitmentOf(issuer, bond_token.address)
    balance = bond_token.balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系10
# 残高不足
def test_createorder_error_10(users, bond_exchange, personal_info, payment_gateway):
    issuer = users["issuer"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット
    _amount = 100
    bond_token.transfer.transact(bond_exchange.address, _amount, {"from": issuer})

    # 新規注文（売）
    _price = 123
    _isBuy = False
    bond_exchange.createOrder.transact(
        bond_token.address, _amount + 1, _price, _isBuy, agent, {"from": issuer}
    )  # エラーになる

    commitment = bond_exchange.commitmentOf(issuer, bond_token.address)
    balance = bond_token.balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系11-1
# 無効な収納代行業者（Agent）の指定（買）
def test_createorder_error_11_1(users, bond_exchange, personal_info, payment_gateway):
    issuer = users["issuer"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文（買）
    _amount = 100
    _price = 123
    _isBuy = True
    invalid_agent = users["trader"]
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, invalid_agent, {"from": issuer}
    )  # エラーになる

    commitment = bond_exchange.commitmentOf(issuer, bond_token.address)
    balance = bond_token.balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系11-2
# 無効な収納代行業者（Agent）の指定（売）
def test_createorder_error_11_2(users, bond_exchange, payment_gateway, personal_info):
    issuer = users["issuer"]
    agent = users["agent"]

    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット
    _amount = 100
    bond_token.transfer.transact(bond_exchange.address, _amount, {"from": issuer})

    # 新規注文（売）
    _amount = 100
    _price = 123
    _isBuy = False
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )  # エラーになる

    commitment = bond_exchange.commitmentOf(issuer, bond_token.address)
    balance = bond_token.balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系12-1
# 取扱ステータスがFalseの場合（買）
def test_createorder_error_12_1(users, bond_exchange, personal_info, payment_gateway):
    issuer = users["issuer"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # ステータス変更
    bond_token.setStatus.transact(False, {"from": issuer})

    # 新規注文（買）
    _price = 123
    _isBuy = True
    _amount = 100
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )  # エラーになる

    commitment = bond_exchange.commitmentOf(issuer, bond_token.address)
    balance = bond_token.balanceOf(issuer)
    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系12-2
# 取扱ステータスがFalseの場合（売）
def test_createorder_error_12_2(users, bond_exchange, personal_info, payment_gateway):
    issuer = users["issuer"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # ステータス変更
    bond_token.setStatus.transact(False, {"from": issuer})

    # Exchangeへのデポジット
    _amount = 100
    bond_token.transfer.transact(bond_exchange.address, _amount, {"from": issuer})

    # 新規注文（売）
    _price = 123
    _isBuy = False
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )  # エラーになる

    commitment = bond_exchange.commitmentOf(issuer, bond_token.address)
    balance = bond_token.balanceOf(issuer)
    assert balance == deploy_args[2]
    assert commitment == 0


"""
TEST_注文キャンセル（cancelOrder）
"""


# 正常系1
# ＜発行体＞新規発行 -> ＜投資家（発行体）＞新規注文（買）
#  -> ＜投資家（発行体）＞注文キャンセル
def test_cancelOrder_normal_1(users, bond_exchange, personal_info, payment_gateway):
    issuer = users["issuer"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文（買）
    _amount = 100
    _price = 123
    _isBuy = True
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )

    # 注文キャンセル
    order_id = bond_exchange.latestOrderId()
    bond_exchange.cancelOrder.transact(order_id, {"from": issuer})

    orderbook = bond_exchange.getOrder(order_id)

    assert orderbook == [
        issuer.address,
        to_checksum_address(bond_token.address),
        _amount,
        _price,
        _isBuy,
        agent.address,
        True,
    ]
    assert bond_token.balanceOf(issuer) == deploy_args[2]


# 正常系2
# ＜発行体＞新規発行 -> ＜投資家（発行体）＞新規注文（売）
#  -> ＜投資家（発行体）＞注文キャンセル
def test_cancelOrder_normal_2(users, bond_exchange, personal_info, payment_gateway):
    issuer = users["issuer"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット
    _amount = 100
    bond_token.transfer.transact(bond_exchange.address, _amount, {"from": issuer})

    # 新規注文（売）
    _price = 123
    _isBuy = False
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )

    # 注文キャンセル
    order_id = bond_exchange.latestOrderId()
    bond_exchange.cancelOrder.transact(order_id, {"from": issuer})

    orderbook = bond_exchange.getOrder(order_id)
    commitment = bond_exchange.commitmentOf(issuer, bond_token.address)

    assert orderbook == [
        issuer.address,
        to_checksum_address(bond_token.address),
        _amount,
        _price,
        _isBuy,
        agent.address,
        True,
    ]
    assert bond_token.balanceOf(issuer) == deploy_args[2]
    assert commitment == 0


# エラー系1
# 入力値の型誤り（_orderId）
def test_cancelOrder_error_1(users, bond_exchange):
    issuer = users["issuer"]

    # 注文キャンセル

    with pytest.raises(OverflowError):
        bond_exchange.cancelOrder.transact(-1, {"from": issuer})

    with pytest.raises(OverflowError):
        bond_exchange.cancelOrder.transact(2**256, {"from": issuer})

    with pytest.raises(TypeError):
        bond_exchange.cancelOrder.transact("abc", {"from": issuer})


# エラー系2
# 指定した注文IDが直近の注文IDを超えている場合
def test_cancelOrder_error_2(users, bond_exchange, personal_info, payment_gateway):
    issuer = users["issuer"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文（買）
    _amount = 100
    _price = 123
    _isBuy = True
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )

    # 注文キャンセル
    order_id = bond_exchange.latestOrderId() + 1
    bond_exchange.cancelOrder.transact(order_id, {"from": issuer})  # エラーになる

    orderbook = bond_exchange.getOrder(order_id - 1)
    assert orderbook == [
        issuer.address,
        to_checksum_address(bond_token.address),
        _amount,
        _price,
        _isBuy,
        agent.address,
        False,
    ]
    assert bond_token.balanceOf(issuer) == deploy_args[2]


# エラー系3-1
# 注文がキャンセル済みの場合（買注文）
def test_cancelOrder_error_3_1(users, bond_exchange, personal_info, payment_gateway):
    issuer = users["issuer"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文（買）
    _amount = 100
    _price = 123
    _isBuy = True
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )

    # 注文キャンセル
    order_id = bond_exchange.latestOrderId()
    bond_exchange.cancelOrder.transact(order_id, {"from": issuer})

    # 注文キャンセル（2回目）
    bond_exchange.cancelOrder.transact(order_id, {"from": issuer})  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)

    assert orderbook == [
        issuer.address,
        to_checksum_address(bond_token.address),
        _amount,
        _price,
        _isBuy,
        agent.address,
        True,
    ]
    assert bond_token.balanceOf(issuer) == deploy_args[2]


# エラー系3-2
# 注文がキャンセル済みの場合（売注文）
def test_cancelOrder_error_3_2(users, bond_exchange, personal_info, payment_gateway):
    issuer = users["issuer"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット
    _amount = 100
    bond_token.transfer.transact(bond_exchange.address, _amount, {"from": issuer})

    # 新規注文（売）
    _price = 123
    _isBuy = False
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )

    # 注文キャンセル
    order_id = bond_exchange.latestOrderId()
    bond_exchange.cancelOrder.transact(order_id, {"from": issuer})

    # 注文キャンセル（2回目）
    bond_exchange.cancelOrder.transact(order_id, {"from": issuer})  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    assert orderbook == [
        issuer.address,
        to_checksum_address(bond_token.address),
        _amount,
        _price,
        _isBuy,
        agent.address,
        True,
    ]
    assert bond_token.balanceOf(issuer) == deploy_args[2]


# エラー系4-1
# 元注文の発注者と、注文キャンセルの実施者が異なる場合（買注文）
def test_cancelOrder_error_4_1(users, bond_exchange, personal_info, payment_gateway):
    issuer = users["issuer"]
    other = users["trader"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文（買）
    _amount = 100
    _price = 123
    _isBuy = True
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )

    # 注文キャンセル
    order_id = bond_exchange.latestOrderId()
    bond_exchange.cancelOrder.transact(order_id, {"from": other})  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    assert orderbook == [
        issuer.address,
        to_checksum_address(bond_token.address),
        _amount,
        _price,
        _isBuy,
        agent.address,
        False,
    ]
    assert bond_token.balanceOf(issuer) == deploy_args[2]


# エラー系4-2
# 元注文の発注者と、注文キャンセルの実施者が異なる場合（売注文）
def test_cancelOrder_error_4_2(users, bond_exchange, personal_info, payment_gateway):
    issuer = users["issuer"]
    other = users["trader"]
    agent = users["agent"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット
    _amount = 100
    bond_token.transfer.transact(bond_exchange.address, _amount, {"from": issuer})

    # 新規注文（売）
    _price = 123
    _isBuy = False
    bond_exchange.createOrder.transact(
        bond_token.address, _amount, _price, _isBuy, agent, {"from": issuer}
    )

    # 注文キャンセル
    order_id = bond_exchange.latestOrderId()
    bond_exchange.cancelOrder.transact(order_id, {"from": other})  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance = bond_token.balanceOf(issuer)
    commitment = bond_exchange.commitmentOf(issuer, bond_token.address)

    assert orderbook == [
        issuer.address,
        to_checksum_address(bond_token.address),
        _amount,
        _price,
        _isBuy,
        agent.address,
        False,
    ]
    assert balance == deploy_args[2] - _amount
    assert commitment == _amount


"""
TEST_Take注文（executeOrder）
"""


# 正常系1
# ＜発行体＞新規発行 -> ＜発行体＞新規注文（売） -> ＜投資家＞Take注文（買）
def test_executeOrder_normal_1(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # 新規注文（売）
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # Take注文（買）
    order_id = bond_exchange.latestOrderId()
    _amount_take = 50
    bond_exchange.executeOrder.transact(order_id, _amount_take, True, {"from": _trader})

    agreement_id = bond_exchange.latestAgreementId(order_id)

    orderbook = bond_exchange.getOrder(order_id)
    agree = bond_exchange.getAgreement(order_id, agreement_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price,
        False,
        _agent,
        False,
    ]

    assert agree[0:5] == [_trader, _amount_take, _price, False, False]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# 正常系2
# ＜発行体＞新規発行 -> ＜投資家＞新規注文（買） -> ＜発行体＞Take注文（売）
def test_executeOrder_normal_2(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文（買）：投資家
    _price = 123
    _amount_make = 100
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, True, _agent, {"from": _trader}
    )

    order_id = bond_exchange.latestOrderId()

    # 預かりをExchangeへのデポジット：発行体
    _amount_take = 50
    bond_token.transfer.transact(bond_exchange.address, _amount_take, {"from": _issuer})

    # Take注文（売）：発行体
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, False, {"from": _issuer}
    )

    agreement_id = bond_exchange.latestAgreementId(order_id)

    orderbook = bond_exchange.getOrder(order_id)
    agree = bond_exchange.getAgreement(order_id, agreement_id)
    balance_maker = bond_token.balanceOf(_trader)
    balance_taker = bond_token.balanceOf(_issuer)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader,
        to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price,
        True,
        _agent,
        False,
    ]

    assert agree[0:5] == [_issuer, _amount_take, _price, False, False]
    assert balance_maker == 0
    assert balance_taker == deploy_args[2] - _amount_take
    assert commitment == _amount_take


# エラー系1
# 入力値の型誤り（_orderId）
def test_executeOrder_error_1(users, bond_exchange):
    _trader = users["trader"]

    _amount = 50
    _is_buy = True

    with pytest.raises(OverflowError):
        bond_exchange.executeOrder.transact(-1, _amount, _is_buy, {"from": _trader})

    with pytest.raises(OverflowError):
        bond_exchange.executeOrder.transact(2**256, _amount, _is_buy, {"from": _trader})

    with pytest.raises(TypeError):
        bond_exchange.executeOrder.transact("abc", _amount, _is_buy, {"from": _trader})


# エラー系2
# 入力値の型誤り（_amount）
def test_executeOrder_error_2(users, bond_exchange):
    _trader = users["trader"]

    _order_id = 1000
    _is_buy = True

    with pytest.raises(OverflowError):
        bond_exchange.executeOrder.transact(_order_id, -1, _is_buy, {"from": _trader})

    with pytest.raises(OverflowError):
        bond_exchange.executeOrder.transact(
            _order_id, 2**256, _is_buy, {"from": _trader}
        )

    with pytest.raises(TypeError):
        bond_exchange.executeOrder.transact(
            _order_id, "abc", _is_buy, {"from": _trader}
        )


# エラー系3
# 入力値の型誤り（_isBuy）
def test_executeOrder_error_3(users, bond_exchange):
    _trader = users["trader"]

    _order_id = 1000
    _amount = 123

    with pytest.raises(ValueError):
        bond_exchange.executeOrder.transact(
            _order_id, _amount, "True", {"from": _trader}
        )

    with pytest.raises(ValueError):
        bond_exchange.executeOrder.transact(_order_id, _amount, 111, {"from": _trader})


# エラー系4
# 指定した注文IDが直近の注文IDを超えている場合
def test_executeOrder_error_4(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Make注文（買）：投資家
    _price = 123
    _amount_make = 100
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, True, _agent, {"from": _trader}
    )

    latest_order_id_error = bond_exchange.latestOrderId() + 1
    latest_order_id = bond_exchange.latestOrderId()

    # Take注文（売）
    order_id = latest_order_id_error
    _amount = 123
    bond_exchange.executeOrder.transact(
        order_id, _amount, False, {"from": _issuer}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(latest_order_id)
    balance_maker = bond_token.balanceOf(_trader)
    balance_taker = bond_token.balanceOf(_issuer)

    assert orderbook == [
        _trader,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        True,
        _agent,
        False,
    ]

    assert balance_maker == 0
    assert balance_taker == deploy_args[2]


# エラー系5-1
# 注文数量が0の場合
# Take買注文
def test_executeOrder_error_5_1(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 預かりをExchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # Take注文（買）：投資家
    order_id = bond_exchange.latestOrderId()
    bond_exchange.executeOrder.transact(
        order_id, 0, True, {"from": _trader}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        False,
        _agent,
        False,
    ]

    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系5-2
# 注文数量が0の場合
# Take売注文
def test_executeOrder_error_5_2(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文（買）：投資家
    _price = 123
    _amount_make = 100
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, True, _agent, {"from": _trader}
    )

    # 預かりをExchangeへのデポジット：発行体
    _amount_take = 50
    bond_token.transfer.transact(bond_exchange.address, _amount_take, {"from": _issuer})

    # Take注文（売）：発行体
    order_id = bond_exchange.latestOrderId()
    bond_exchange.executeOrder.transact(
        order_id, 0, False, {"from": _issuer}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_maker = bond_token.balanceOf(_trader)
    balance_taker = bond_token.balanceOf(_issuer)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        True,
        _agent,
        False,
    ]

    assert balance_maker == 0
    assert balance_taker == deploy_args[2]
    assert commitment == 0


# エラー系6-1
# 元注文と、発注する注文が同一の売買区分の場合
# Take買注文
def test_executeOrder_error_6_1(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 預かりをExchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # Take注文（売）：投資家
    order_id = bond_exchange.latestOrderId()
    _amount_take = 50
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, False, {"from": _trader}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        False,
        _agent,
        False,
    ]

    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系6-2
# 元注文と、発注する注文が同一の売買区分の場合
# Take売注文
def test_executeOrder_error_6_2(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文（買）：投資家
    _price = 123
    _amount_make = 100
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, True, _agent, {"from": _trader}
    )

    # Take注文（買）：発行体
    order_id = bond_exchange.latestOrderId()
    _amount_take = 50
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, True, {"from": _issuer}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_maker = bond_token.balanceOf(_trader)
    balance_taker = bond_token.balanceOf(_issuer)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        True,
        _agent,
        False,
    ]

    assert balance_maker == 0
    assert balance_taker == deploy_args[2]
    assert commitment == 0


# エラー系7-1
# 元注文の発注者と同一のアドレスからの発注の場合
# Take買注文
def test_executeOrder_error_7_1(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 預かりをExchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # Take注文（買）：発行体
    order_id = bond_exchange.latestOrderId()
    _amount_take = 50
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, True, {"from": _issuer}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_maker = bond_token.balanceOf(_issuer)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        False,
        _agent,
        False,
    ]

    assert balance_maker == deploy_args[2] - _amount_make
    assert commitment == _amount_make


# エラー系7-2
# 元注文の発注者と同一のアドレスからの発注の場合
# Take売注文
def test_executeOrder_error_7_2(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文（買）：発行体
    _price = 123
    _amount_make = 100
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, True, _agent, {"from": _issuer}
    )

    # 預かりをExchangeへのデポジット：発行体
    _amount_take = 50
    bond_token.transfer.transact(bond_exchange.address, _amount_take, {"from": _issuer})

    # Take注文（売）：発行体
    order_id = bond_exchange.latestOrderId()
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, False, {"from": _issuer}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_taker = bond_token.balanceOf(_issuer)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        True,
        _agent,
        False,
    ]
    assert commitment == 0
    assert balance_taker == deploy_args[2]


# エラー系8-1
# 元注文がキャンセル済の場合
# Take買注文
def test_executeOrder_error_8_1(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 預かりをExchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    order_id = bond_exchange.latestOrderId()

    # Make注文取消：発行体
    bond_exchange.cancelOrder.transact(order_id, {"from": _issuer})

    # Take注文（買）：投資家
    _amount_take = 50
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, True, {"from": _trader}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        False,
        _agent,
        True,  # 取消済み状態
    ]
    assert balance_maker == deploy_args[2]
    assert balance_taker == 0
    assert commitment == 0


# エラー系8-2
# 元注文の発注者と同一のアドレスからの発注の場合
# Take売注文
def test_executeOrder_error_8_2(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Make注文（買）：投資家
    _price = 123
    _amount_make = 100
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, True, _agent, {"from": _trader}
    )

    order_id = bond_exchange.latestOrderId()

    # Make注文取消：投資家
    bond_exchange.cancelOrder.transact(order_id, {"from": _trader})

    # 預かりをExchangeへのデポジット：発行体
    _amount_take = 50
    bond_token.transfer.transact(bond_exchange.address, _amount_take, {"from": _issuer})

    # Take注文（売）：発行体
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, False, {"from": _issuer}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_maker = bond_token.balanceOf(_trader)
    balance_taker = bond_token.balanceOf(_issuer)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        True,
        _agent,
        True,  # 取り消し済み状態
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]


# エラー系9-1
# 認可されたアドレスではない場合
# Take買注文
def test_executeOrder_error_9_1(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    # 未認可状態

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 預かりをExchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    order_id = bond_exchange.latestOrderId()

    # Take注文（買）：投資家
    _amount_take = 50
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, True, {"from": _trader}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        False,
        _agent,
        False,
    ]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系9-2
# 認可されたアドレスではない場合
# Take売注文
def test_executeOrder_error_9_2(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)  # 未認可状態

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Make注文（買）：投資家
    _price = 123
    _amount_make = 100
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, True, _agent, {"from": _trader}
    )

    order_id = bond_exchange.latestOrderId()

    # 預かりをExchangeへのデポジット：発行体
    _amount_take = 50
    bond_token.transfer.transact(bond_exchange.address, _amount_take, {"from": _issuer})

    # Take注文（売）：発行体
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, False, {"from": _issuer}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_maker = bond_token.balanceOf(_trader)
    balance_taker = bond_token.balanceOf(_issuer)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        True,
        _agent,
        False,
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]


# エラー系10-1
# 名簿用個人情報が登録されていない場合
# Take買注文
def test_executeOrder_error_10_1(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 預かりをExchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    order_id = bond_exchange.latestOrderId()

    # Take注文（買）：投資家
    _amount_take = 50
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, True, {"from": _trader}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        False,
        _agent,
        False,
    ]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系10-2
# 名簿用個人情報が登録されていない場合
# Take売注文
def test_executeOrder_error_10_2(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Make注文（買）：投資家
    _price = 123
    _amount_make = 100
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, True, _agent, {"from": _trader}
    )

    order_id = bond_exchange.latestOrderId()

    # 預かりをExchangeへのデポジット：発行体
    _amount_take = 50
    bond_token.transfer.transact(bond_exchange.address, _amount_take, {"from": _issuer})

    # Take注文（売）：発行体
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, False, {"from": _issuer}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_maker = bond_token.balanceOf(_trader)
    balance_taker = bond_token.balanceOf(_issuer)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        True,
        _agent,
        False,
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]


# エラー系11-1
# 償還済みフラグがTrueの場合
# Take買注文
def test_executeOrder_error_11_1(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 預かりをExchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    order_id = bond_exchange.latestOrderId()

    # 償還処理：発行体
    bond_token.redeem.transact({"from": _issuer})

    # Take注文（買）：投資家
    _amount_take = 50
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, True, {"from": _trader}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        False,
        _agent,
        False,
    ]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系11-2
# 償還済みフラグがTrueの場合
# Take売注文
def test_executeOrder_error_11_2(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Make注文（買）：投資家
    _price = 123
    _amount_make = 100
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, True, _agent, {"from": _trader}
    )

    order_id = bond_exchange.latestOrderId()

    # 償還処理：発行体
    bond_token.redeem.transact({"from": _issuer})

    # 預かりをExchangeへのデポジット：発行体
    _amount_take = 50
    bond_token.transfer.transact(bond_exchange.address, _amount_take, {"from": _issuer})

    # Take注文（売）：発行体
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, False, {"from": _issuer}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_maker = bond_token.balanceOf(_trader)
    balance_taker = bond_token.balanceOf(_issuer)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        True,
        _agent,
        False,
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]


# エラー系12-1
# Take数量が元注文の残数量を超過している場合
# Take買注文
def test_executeOrder_error_12_1(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 預かりをExchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    order_id = bond_exchange.latestOrderId()

    # Take注文（買）：投資家
    _amount_take = 101
    # Make注文の数量を超過
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, True, {"from": _trader}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        False,
        _agent,
        False,
    ]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系12-2
# Take数量が元注文の残数量を超過している場合
# Take売注文
def test_executeOrder_error_12_2(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Make注文（買）：投資家
    _price = 123
    _amount_make = 100
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, True, _agent, {"from": _trader}
    )

    order_id = bond_exchange.latestOrderId()

    # 預かりをExchangeへのデポジット：発行体
    _amount_take = 101  # Make注文の数量を超過
    bond_token.transfer.transact(bond_exchange.address, _amount_take, {"from": _issuer})

    # Take注文（売）：発行体
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, False, {"from": _issuer}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_maker = bond_token.balanceOf(_trader)
    balance_taker = bond_token.balanceOf(_issuer)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        True,
        _agent,
        False,
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]


# エラー系13
# Take注文の発注者の残高が発注数量を下回っている場合
def test_executeOrder_error_13(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Make注文（買）：投資家
    _price = 123
    _amount_make = 100
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, True, _agent, {"from": _trader}
    )

    order_id = bond_exchange.latestOrderId()

    # 預かりをExchangeへのデポジット：発行体
    _amount_take = 50
    bond_token.transfer.transact(bond_exchange.address, _amount_take, {"from": _issuer})

    # Take注文（売）：発行体
    bond_exchange.executeOrder.transact(
        order_id, _amount_take + 1, False, {"from": _issuer}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_maker = bond_token.balanceOf(_trader)
    balance_taker = bond_token.balanceOf(_issuer)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        True,
        _agent,
        False,
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]


# エラー系14-1
# 取扱ステータスがFalseの場合（買）
def test_executeOrder_error_14_1(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 預かりをExchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    order_id = bond_exchange.latestOrderId()

    # ステータス変更：発行体
    bond_token.setStatus.transact(False, {"from": _issuer})

    # Take注文（買）：投資家
    _amount_take = 50
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, True, {"from": _trader}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        False,
        _agent,
        False,
    ]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系14-2
# 取扱ステータスがFalseの場合（売）
def test_executeOrder_error_14_2(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Make注文（買）：投資家
    _price = 123
    _amount_make = 100
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, True, _agent, {"from": _trader}
    )

    order_id = bond_exchange.latestOrderId()

    # 償還処理：発行体
    bond_token.redeem.transact({"from": _issuer})

    # 預かりをExchangeへのデポジット：発行体
    _amount_take = 50
    bond_token.transfer.transact(bond_exchange.address, _amount_take, {"from": _issuer})

    # ステータス変更：発行体
    bond_token.setStatus.transact(False, {"from": _issuer})

    # Take注文（売）：発行体
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, False, {"from": _issuer}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    balance_maker = bond_token.balanceOf(_trader)
    balance_taker = bond_token.balanceOf(_issuer)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader,
        to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price,
        True,
        _agent,
        False,
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]


"""
TEST_決済承認（confirmAgreement）
"""


# 正常系1
# Make売、Take買
# ＜発行体＞新規発行 -> ＜発行体＞Make注文（売）
#  -> ＜投資家＞Take注文（買） -> ＜決済業者＞決済処理
def test_confirmAgreement_normal_1(
    users, bond_exchange, personal_info, payment_gateway
):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # Take注文（買）：投資家
    order_id = bond_exchange.latestOrderId()
    _amount_take = 50
    bond_exchange.executeOrder.transact(order_id, _amount_take, True, {"from": _trader})

    agreement_id = bond_exchange.latestAgreementId(order_id)

    # 決済承認：決済業者
    bond_exchange.confirmAgreement.transact(order_id, agreement_id, {"from": _agent})

    orderbook = bond_exchange.getOrder(order_id)
    agreement = bond_exchange.getAgreement(order_id, agreement_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price,
        False,
        _agent,
        False,
    ]

    assert agreement[0:5] == [_trader, _amount_take, _price, False, True]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == _amount_take
    assert commitment == _amount_make - _amount_take

    # Assert: last_price
    assert bond_exchange.lastPrice(bond_token.address) == 123


# 正常系2
# Make買、Take売
# ＜発行体＞新規発行 -> ＜投資家＞Make注文（買）
#  -> ＜発行体＞Take注文（売） -> ＜決済業者＞決済処理
def test_confirmAgreement_normal_2(
    users, bond_exchange, personal_info, payment_gateway
):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文（買）：投資家
    _price = 123
    _amount_make = 100
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, True, _agent, {"from": _trader}
    )

    order_id = bond_exchange.latestOrderId()

    # 預かりをExchangeへのデポジット：発行体
    _amount_take = 50
    bond_token.transfer.transact(bond_exchange.address, _amount_take, {"from": _issuer})

    # Take注文（売）：発行体
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, False, {"from": _issuer}
    )

    agreement_id = bond_exchange.latestAgreementId(order_id)

    # 決済承認：決済業者
    bond_exchange.confirmAgreement.transact(order_id, agreement_id, {"from": _agent})

    orderbook = bond_exchange.getOrder(order_id)
    agree = bond_exchange.getAgreement(order_id, agreement_id)
    balance_maker = bond_token.balanceOf(_trader)
    balance_taker = bond_token.balanceOf(_issuer)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader,
        to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price,
        True,
        _agent,
        False,
    ]
    assert agree[0:5] == [_issuer, _amount_take, _price, False, True]
    assert balance_maker == _amount_take
    assert balance_taker == deploy_args[2] - _amount_take
    assert commitment == 0

    # Assert: last_price
    assert bond_exchange.lastPrice(bond_token.address) == 123


# エラー系1
# 入力値の型誤り（_orderId）
def test_confirmAgreement_error_1(users, bond_exchange):
    _agent = users["agent"]

    # 決済承認：決済業者

    with pytest.raises(OverflowError):
        bond_exchange.confirmAgreement.transact(-1, 0, {"from": _agent})

    with pytest.raises(OverflowError):
        bond_exchange.confirmAgreement.transact(2**256, 0, {"from": _agent})

    with pytest.raises(TypeError):
        bond_exchange.confirmAgreement.transact("abc", 0, {"from": _agent})


# エラー系2
# 入力値の型誤り（_agreementId）
def test_confirmAgreement_error_2(users, bond_exchange):
    _agent = users["agent"]

    # 決済承認：決済業者

    with pytest.raises(OverflowError):
        bond_exchange.confirmAgreement.transact(0, -1, {"from": _agent})

    with pytest.raises(OverflowError):
        bond_exchange.confirmAgreement.transact(0, 2**256, {"from": _agent})

    with pytest.raises(TypeError):
        bond_exchange.confirmAgreement.transact(0, "abc", {"from": _agent})


# エラー系3
# 指定した注文番号が、直近の注文ID以上の場合
def test_confirmAgreement_error_3(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # Take注文（買）：投資家
    order_id = bond_exchange.latestOrderId()
    _amount_take = 50
    bond_exchange.executeOrder.transact(order_id, _amount_take, True, {"from": _trader})

    agreement_id = bond_exchange.latestAgreementId(order_id)

    # 決済承認：決済業者
    order_id_error = bond_exchange.latestOrderId() + 1
    bond_exchange.confirmAgreement.transact(
        order_id_error, agreement_id, {"from": _agent}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    agreement = bond_exchange.getAgreement(order_id, agreement_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price,
        False,
        _agent,
        False,
    ]

    assert agreement[0:5] == [_trader, _amount_take, _price, False, False]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make

    # Assert: last_price
    assert bond_exchange.lastPrice(bond_token.address) == 0


# エラー系4
# 指定した約定IDが、直近の約定ID以上の場合
def test_confirmAgreement_error_4(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # Take注文（買）：投資家
    order_id = bond_exchange.latestOrderId()
    _amount_take = 50
    bond_exchange.executeOrder.transact(order_id, _amount_take, True, {"from": _trader})

    agreement_id = bond_exchange.latestAgreementId(order_id)

    # 決済承認：決済業者
    agreement_id_error = bond_exchange.latestAgreementId(order_id) + 1
    bond_exchange.confirmAgreement.transact(
        order_id, agreement_id_error, {"from": _agent}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    agreement = bond_exchange.getAgreement(order_id, agreement_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price,
        False,
        _agent,
        False,
    ]

    assert agreement[0:5] == [_trader, _amount_take, _price, False, False]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make

    # Assert: last_price
    assert bond_exchange.lastPrice(bond_token.address) == 0


# エラー系5
# 指定した約定明細がすでに支払い済みの状態の場合
def test_confirmAgreement_error_5(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # Take注文（買）：投資家
    order_id = bond_exchange.latestOrderId()
    _amount_take = 50
    bond_exchange.executeOrder.transact(order_id, _amount_take, True, {"from": _trader})

    agreement_id = bond_exchange.latestAgreementId(order_id)

    # 決済承認：決済業者
    bond_exchange.confirmAgreement.transact(order_id, agreement_id, {"from": _agent})

    # 決済承認：決済業者（2回目）
    bond_exchange.confirmAgreement.transact(
        order_id, agreement_id, {"from": _agent}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    agreement = bond_exchange.getAgreement(order_id, agreement_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price,
        False,
        _agent,
        False,
    ]
    assert agreement[0:5] == [_trader, _amount_take, _price, False, True]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == _amount_take
    assert commitment == _amount_make - _amount_take

    # Assert: last_price
    assert bond_exchange.lastPrice(bond_token.address) == 123


# エラー系6
# 元注文で指定した決済業者ではない場合
def test_confirmAgreement_error_6(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # Take注文（買）：投資家
    order_id = bond_exchange.latestOrderId()
    _amount_take = 50
    bond_exchange.executeOrder.transact(order_id, _amount_take, True, {"from": _trader})

    agreement_id = bond_exchange.latestAgreementId(order_id)

    # 決済承認：投資家（指定した決済業者ではない）
    bond_exchange.confirmAgreement.transact(
        order_id, agreement_id, {"from": _trader}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    agreement = bond_exchange.getAgreement(order_id, agreement_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price,
        False,
        _agent,
        False,
    ]

    assert agreement[0:5] == [_trader, _amount_take, _price, False, False]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make

    # Assert: last_price
    assert bond_exchange.lastPrice(bond_token.address) == 0


# エラー系7
# 既に決済非承認済み（キャンセル済み）の場合
def test_confirmAgreement_error_7(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # Take注文（買）：投資家
    order_id = bond_exchange.latestOrderId()
    _amount_take = 50
    bond_exchange.executeOrder.transact(order_id, _amount_take, True, {"from": _trader})

    agreement_id = bond_exchange.latestAgreementId(order_id)

    # 決済非承認：決済業者
    bond_exchange.cancelAgreement.transact(order_id, agreement_id, {"from": _agent})

    # 決済承認：決済業者
    bond_exchange.confirmAgreement.transact(
        order_id, agreement_id, {"from": _agent}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    agreement = bond_exchange.getAgreement(order_id, agreement_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make,
        _price,
        False,
        _agent,
        False,
    ]
    assert agreement[0:5] == [_trader, _amount_take, _price, True, False]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make

    # Assert: last_price
    assert bond_exchange.lastPrice(bond_token.address) == 0


"""
TEST_決済非承認（cancelAgreement）
"""


# 正常系1
# Make売、Take買
# ＜発行体＞新規発行 -> ＜発行体＞Make注文（売）
#  -> ＜投資家＞Take注文（買） -> ＜決済業者＞決済非承認
def test_cancelAgreement_normal_1(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # Take注文（買）：投資家
    order_id = bond_exchange.latestOrderId()
    _amount_take = 50
    bond_exchange.executeOrder.transact(order_id, _amount_take, True, {"from": _trader})

    agreement_id = bond_exchange.latestAgreementId(order_id)

    # 決済非承認：決済業者
    bond_exchange.cancelAgreement.transact(order_id, agreement_id, {"from": _agent})

    orderbook = bond_exchange.getOrder(order_id)
    agreement = bond_exchange.getAgreement(order_id, agreement_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make,
        _price,
        False,
        _agent,
        False,
    ]
    assert agreement[0:5] == [_trader, _amount_take, _price, True, False]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# 正常系2
# Make買、Take売
# ＜発行体＞新規発行 -> ＜投資家＞Make注文（買）
#  -> ＜発行体＞Take注文（売） -> ＜決済業者＞決済非承認
def test_cancelAgreement_normal_2(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # 新規注文（買）：投資家
    _price = 123
    _amount_make = 100
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, True, _agent, {"from": _trader}
    )

    order_id = bond_exchange.latestOrderId()

    # 預かりをExchangeへのデポジット：発行体
    _amount_take = 50
    bond_token.transfer.transact(bond_exchange.address, _amount_take, {"from": _issuer})

    # Take注文（売）：発行体
    bond_exchange.executeOrder.transact(
        order_id, _amount_take, False, {"from": _issuer}
    )

    agreement_id = bond_exchange.latestAgreementId(order_id)

    # 決済非承認：決済業者
    bond_exchange.cancelAgreement.transact(order_id, agreement_id, {"from": _agent})

    orderbook = bond_exchange.getOrder(order_id)
    agree = bond_exchange.getAgreement(order_id, agreement_id)
    balance_maker = bond_token.balanceOf(_trader)
    balance_taker = bond_token.balanceOf(_issuer)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader,
        to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price,
        True,
        _agent,
        False,
    ]
    assert agree[0:5] == [_issuer, _amount_take, _price, True, False]
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]
    assert commitment == 0


# エラー系1
# 入力値の型誤り（_orderId）
def test_cancelAgreement_error_1(users, bond_exchange):
    _agent = users["agent"]

    # 決済非承認：決済業者

    with pytest.raises(OverflowError):
        bond_exchange.cancelAgreement.transact(-1, 0, {"from": _agent})

    with pytest.raises(OverflowError):
        bond_exchange.cancelAgreement.transact(2**256, 0, {"from": _agent})

    with pytest.raises(TypeError):
        bond_exchange.cancelAgreement.transact("abc", 0, {"from": _agent})


# エラー系2
# 入力値の型誤り（_agreementId）
def test_cancelAgreement_error_2(users, bond_exchange):
    _agent = users["agent"]

    # 決済非承認：決済業者

    with pytest.raises(OverflowError):
        bond_exchange.cancelAgreement.transact(0, -1, {"from": _agent})

    with pytest.raises(OverflowError):
        bond_exchange.cancelAgreement.transact(0, 2**256, {"from": _agent})

    with pytest.raises(TypeError):
        bond_exchange.cancelAgreement.transact(0, "aabc", {"from": _agent})


# エラー系3
# 指定した注文番号が、直近の注文ID以上の場合
def test_cancelAgreement_error_3(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # Take注文（買）：投資家
    order_id = bond_exchange.latestOrderId()
    _amount_take = 50
    bond_exchange.executeOrder.transact(order_id, _amount_take, True, {"from": _trader})

    agreement_id = bond_exchange.latestAgreementId(order_id)

    # 決済非承認：決済業者
    order_id_error = bond_exchange.latestOrderId() + 1
    bond_exchange.cancelAgreement.transact(
        order_id_error, agreement_id, {"from": _agent}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    agreement = bond_exchange.getAgreement(order_id, agreement_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price,
        False,
        _agent,
        False,
    ]
    assert agreement[0:5] == [_trader, _amount_take, _price, False, False]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系4
# 指定した約定IDが、直近の約定ID以上の場合
def test_cancelAgreement_error_4(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # Take注文（買）：投資家
    order_id = bond_exchange.latestOrderId()
    _amount_take = 50
    bond_exchange.executeOrder.transact(order_id, _amount_take, True, {"from": _trader})

    agreement_id = bond_exchange.latestAgreementId(order_id)

    # 決済非承認：決済業者
    agreement_id_error = bond_exchange.latestAgreementId(order_id) + 1
    bond_exchange.cancelAgreement.transact(
        order_id, agreement_id_error, {"from": _agent}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    agreement = bond_exchange.getAgreement(order_id, agreement_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price,
        False,
        _agent,
        False,
    ]
    assert agreement[0:5] == [_trader, _amount_take, _price, False, False]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系5
# すでに決済承認済み（支払済み）の場合
def test_cancelAgreement_error_5(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # Take注文（買）：投資家
    order_id = bond_exchange.latestOrderId()
    _amount_take = 50
    bond_exchange.executeOrder.transact(order_id, _amount_take, True, {"from": _trader})

    agreement_id = bond_exchange.latestAgreementId(order_id)

    # 決済承認：決済業者
    bond_exchange.confirmAgreement.transact(order_id, agreement_id, {"from": _agent})

    # 決済非承認：決済業者
    bond_exchange.cancelAgreement.transact(
        order_id, agreement_id, {"from": _agent}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    agreement = bond_exchange.getAgreement(order_id, agreement_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price,
        False,
        _agent,
        False,
    ]
    assert agreement[0:5] == [_trader, _amount_take, _price, False, True]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == _amount_take
    assert commitment == _amount_make - _amount_take


# エラー系6
# msg.senderが、決済代行（agent）以外の場合
def test_cancelAgreement_error_6(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # Take注文（買）：投資家
    order_id = bond_exchange.latestOrderId()
    _amount_take = 50
    bond_exchange.executeOrder.transact(order_id, _amount_take, True, {"from": _trader})

    agreement_id = bond_exchange.latestAgreementId(order_id)

    # 決済非承認：投資家（決済業者以外）
    bond_exchange.cancelAgreement.transact(
        order_id, agreement_id, {"from": _trader}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    agreement = bond_exchange.getAgreement(order_id, agreement_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price,
        False,
        _agent,
        False,
    ]
    assert agreement[0:5] == [_trader, _amount_take, _price, False, False]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系5
# すでに決済非承認済み（キャンセル済み）の場合
def test_cancelAgreement_error_7(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Make注文（売）：発行体
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # Take注文（買）：投資家
    order_id = bond_exchange.latestOrderId()
    _amount_take = 50
    bond_exchange.executeOrder.transact(order_id, _amount_take, True, {"from": _trader})

    agreement_id = bond_exchange.latestAgreementId(order_id)

    # 決済非承認：決済業者
    bond_exchange.cancelAgreement.transact(order_id, agreement_id, {"from": _agent})

    # 決済非承認：決済業者（2回目）
    bond_exchange.cancelAgreement.transact(
        order_id, agreement_id, {"from": _agent}
    )  # エラーになる

    orderbook = bond_exchange.getOrder(order_id)
    agreement = bond_exchange.getAgreement(order_id, agreement_id)
    balance_maker = bond_token.balanceOf(_issuer)
    balance_taker = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer,
        to_checksum_address(bond_token.address),
        _amount_make,
        _price,
        False,
        _agent,
        False,
    ]
    assert agreement[0:5] == [_trader, _amount_take, _price, True, False]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


"""
TEST_引き出し（withdrawAll）
"""


# 正常系1
# ＜発行体＞新規発行 -> ＜発行体＞デポジット -> ＜発行体＞引き出し
def test_withdrawAll_normal_1(users, bond_exchange, personal_info):
    _issuer = users["issuer"]

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # 引き出し：発行体
    bond_exchange.withdrawAll.transact(bond_token.address, {"from": _issuer})

    balance_exchange = bond_exchange.balanceOf(_issuer, bond_token.address)
    balance_token = bond_token.balanceOf(_issuer)

    assert balance_exchange == 0
    assert balance_token == deploy_args[2]


# 正常系2
# ＜発行体＞新規発行 -> ＜発行体＞デポジット（2回） -> ＜発行体＞引き出し
def test_withdrawAll_normal_2(users, bond_exchange, personal_info):
    _issuer = users["issuer"]

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # Exchangeへのデポジット（2回目）：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # 引き出し：発行体
    bond_exchange.withdrawAll.transact(bond_token.address, {"from": _issuer})

    balance_exchange = bond_exchange.balanceOf(_issuer, bond_token.address)
    balance_token = bond_token.balanceOf(_issuer)

    assert balance_exchange == 0
    assert balance_token == deploy_args[2]


# 正常系3
# ＜発行体＞新規発行 -> ＜発行体＞Make注文（売） ※売注文中状態
#  -> ＜発行体＞引き出し
def test_withdrawAll_normal_3(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_transfer = 100
    bond_token.transfer.transact(
        bond_exchange.address, _amount_transfer, {"from": _issuer}
    )

    # Make注文（売）：発行体
    _amount_make = 70  # 100のうち70だけ売注文
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # 引き出し：発行体
    bond_exchange.withdrawAll.transact(bond_token.address, {"from": _issuer})

    balance_exchange = bond_exchange.balanceOf(_issuer, bond_token.address)
    balance_token = bond_token.balanceOf(_issuer)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert balance_exchange == 0
    assert balance_token == deploy_args[2] - _amount_make
    assert commitment == _amount_make


# 正常系4
# ＜発行体＞新規発行 -> ＜発行体＞Make注文（売） -> ＜投資家＞Take注文（買）
#  -> ＜発行体＞引き出し
def test_withdrawAll_normal_4(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_transfer = 100
    bond_token.transfer.transact(
        bond_exchange.address, _amount_transfer, {"from": _issuer}
    )

    # Make注文（売）：発行体
    _amount_make = 70  # 100のうち70だけ売注文
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # Take注文（買）：投資家
    order_id = bond_exchange.latestOrderId()
    _amount_take = 50  # 70の売注文に対して、50のTake
    bond_exchange.executeOrder.transact(order_id, _amount_take, True, {"from": _trader})

    # 引き出し：発行体
    bond_exchange.withdrawAll.transact(bond_token.address, {"from": _issuer})

    balance_exchange = bond_exchange.balanceOf(_issuer, bond_token.address)
    balance_token = bond_token.balanceOf(_issuer)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert balance_exchange == 0
    assert balance_token == deploy_args[2] - _amount_make
    assert commitment == _amount_make


# 正常系5
# ＜発行体＞新規発行 -> ＜発行体＞Make注文（売） -> ＜投資家＞Take注文（買）
#  -> ＜決済業者＞決済承認 -> ＜発行体＞引き出し
def test_withdrawAll_normal_5(users, bond_exchange, personal_info, payment_gateway):
    _issuer = users["issuer"]
    _trader = users["trader"]
    _agent = users["agent"]

    personalinfo_register(personal_info, _issuer, _issuer)
    payment_gateway_register(payment_gateway, _issuer, _agent)
    payment_gateway_approve(payment_gateway, _issuer, _agent)

    personalinfo_register(personal_info, _trader, _issuer)
    payment_gateway_register(payment_gateway, _trader, _agent)
    payment_gateway_approve(payment_gateway, _trader, _agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_transfer = 100
    bond_token.transfer.transact(
        bond_exchange.address, _amount_transfer, {"from": _issuer}
    )

    # Make注文（売）：発行体
    _amount_make = 70  # 100のうち70だけ売注文
    _price = 123
    bond_exchange.createOrder.transact(
        bond_token.address, _amount_make, _price, False, _agent, {"from": _issuer}
    )

    # Take注文（買）：投資家
    order_id = bond_exchange.latestOrderId()
    _amount_take = 50  # 70の売注文に対して、50のTake
    bond_exchange.executeOrder.transact(order_id, _amount_take, True, {"from": _trader})

    agreement_id = bond_exchange.latestAgreementId(order_id)

    # 決済承認：決済業者
    bond_exchange.confirmAgreement.transact(order_id, agreement_id, {"from": _agent})

    # 引き出し：発行体
    bond_exchange.withdrawAll.transact(bond_token.address, {"from": _issuer})

    balance_issuer_exchange = bond_exchange.balanceOf(_issuer, bond_token.address)
    balance_issuer_token = bond_token.balanceOf(_issuer)
    balance_trader_exchange = bond_exchange.balanceOf(_trader, bond_token.address)
    balance_trader_token = bond_token.balanceOf(_trader)
    commitment = bond_exchange.commitmentOf(_issuer, bond_token.address)

    assert balance_issuer_exchange == 0
    assert balance_issuer_token == deploy_args[2] - _amount_make
    assert balance_trader_exchange == 0
    assert balance_trader_token == _amount_take
    assert commitment == _amount_make - _amount_take


# エラー系１
# 入力値の型誤り（_token）
def test_withdrawAll_error_1(users, bond_exchange):
    _issuer = users["issuer"]

    # 引き出し：発行体

    with pytest.raises(ValueError):
        bond_exchange.withdrawAll.transact(1234, {"from": _issuer})

    with pytest.raises(ValueError):
        bond_exchange.withdrawAll.transact("1234", {"from": _issuer})


# エラー系2-1
# 残高がゼロの場合
# ＜発行体＞新規発行 -> ＜発行体＞デポジット -> ＜発行体＞引き出し（2回）
def test_withdrawAll_error_2_1(users, bond_exchange, personal_info):
    _issuer = users["issuer"]

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    bond_token.transfer.transact(bond_exchange.address, _amount_make, {"from": _issuer})

    # 引き出し：発行体
    bond_exchange.withdrawAll.transact(bond_token.address, {"from": _issuer})

    # 引き出し（2回目)：発行体
    bond_exchange.withdrawAll.transact(
        bond_token.address, {"from": _issuer}
    )  # エラーになる

    balance_exchange = bond_exchange.balanceOf(_issuer, bond_token.address)
    balance_token = bond_token.balanceOf(_issuer)

    assert balance_exchange == 0
    assert balance_token == deploy_args[2]


# エラー系2-2
# 残高がゼロの場合
# ＜発行体＞新規発行 -> ＜発行体＞デポジット -> 異なるアドレスからの引き出し
def test_withdrawAll_error_2_2(users, bond_exchange, personal_info):
    _issuer = users["issuer"]
    _trader = users["trader"]

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット：発行体
    _amount_transfer = 100
    bond_token.transfer.transact(
        bond_exchange.address, _amount_transfer, {"from": _issuer}
    )

    # 引き出し：異なるアドレス
    bond_exchange.withdrawAll.transact(
        bond_token.address, {"from": _trader}
    )  # エラーになる

    balance_exchange = bond_exchange.balanceOf(_issuer, bond_token.address)
    balance_token = bond_token.balanceOf(_issuer)

    assert balance_exchange == _amount_transfer
    assert balance_token == deploy_args[2] - _amount_transfer


"""
TEST_Exchange切替
"""


# 正常系
def test_updateExchange_normal_1(
    users,
    bond_exchange,
    bond_exchange_storage,
    personal_info,
    payment_gateway,
    IbetStraightBondExchange,
    exchange_regulator_service,
):
    issuer = users["issuer"]
    agent = users["agent"]
    admin = users["admin"]

    personalinfo_register(personal_info, issuer, issuer)
    payment_gateway_register(payment_gateway, issuer, agent)
    payment_gateway_approve(payment_gateway, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(
        users, bond_exchange.address, personal_info.address
    )

    # Exchangeへのデポジット
    bond_token.transfer.transact(bond_exchange.address, 100, {"from": issuer})

    # 新規注文（売）
    bond_exchange.createOrder.transact(
        bond_token.address, 10, 123, False, agent, {"from": issuer}
    )

    # Exchange（新）
    bond_exchange_new = admin.deploy(
        IbetStraightBondExchange,
        payment_gateway.address,
        personal_info.address,
        bond_exchange_storage.address,
        exchange_regulator_service.address,
    )
    bond_exchange_storage.upgradeVersion.transact(
        bond_exchange_new.address, {"from": admin}
    )

    # Exchange（新）からの情報参照
    order_id = bond_exchange_new.latestOrderId()
    orderbook = bond_exchange_new.getOrder(order_id)
    commitment = bond_exchange_new.commitmentOf(issuer, bond_token.address)
    balance_exchange = bond_exchange_new.balanceOf(issuer, bond_token.address)
    balance_token = bond_token.balanceOf(issuer)

    assert orderbook == [
        issuer.address,
        to_checksum_address(bond_token.address),
        10,
        123,
        False,
        agent.address,
        False,
    ]
    assert balance_token == deploy_args[2] - 100
    assert balance_exchange == 90
    assert commitment == 10
