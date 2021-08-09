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
from eth_utils import to_checksum_address

import utils

'''
共通処理
'''


# PersonalInfo登録
def personalinfo_register(personalinfo, trader, issuer):
    message = 'some_message'
    personalinfo.register.transact(issuer, message, {'from': trader})


# PaymentGatewayアカウント登録
def payment_gateway_register(payment_gateway, trader, agent):
    message = 'some_message'
    payment_gateway.register.transact(agent, message, {'from': trader})


# トークンを取引所にデポジット
def transfer(token, otc_exchange, trader, amount):
    token.transfer.transact(
        otc_exchange.address, amount, {'from': trader})


'''
TEST_デプロイ
'''


# ＜正常系1＞
# Deploy　→　正常
def test_deploy_normal_1(users, otc_exchange, otc_exchange_storage, personal_info, payment_gateway):
    owner = otc_exchange.owner()
    personal_info_address = otc_exchange.personalInfoAddress()
    payment_gateway_address = otc_exchange.paymentGatewayAddress()
    storage_address = otc_exchange.storageAddress()

    assert owner == users['admin']
    assert personal_info_address == to_checksum_address(personal_info.address)
    assert payment_gateway_address == to_checksum_address(payment_gateway.address)
    assert storage_address == to_checksum_address(otc_exchange_storage.address)


# ＜エラー系1＞
# 入力値の型誤り（PaymentGatewayアドレス）
def test_deploy_error_1(users, IbetOTCExchange, personal_info, otc_exchange_storage):
    exchange_owner = users['admin']

    deploy_args = [
        1234,
        personal_info.address,
        otc_exchange_storage.address
    ]

    with pytest.raises(ValueError):
        exchange_owner.deploy(
            IbetOTCExchange,
            *deploy_args
        )


# ＜エラー系2＞
# 入力値の型誤り（PersonalInfoアドレス）
def test_deploy_error_2(users, IbetOTCExchange, payment_gateway, otc_exchange_storage):
    exchange_owner = users['admin']
    deploy_args = [
        payment_gateway.address,
        1234,
        otc_exchange_storage.address
    ]
    with pytest.raises(ValueError):
        exchange_owner.deploy(
            IbetOTCExchange, *deploy_args)


# ＜エラー系3＞
# 入力値の型誤り（Storageアドレス）
def test_deploy_error_3(users, IbetOTCExchange, payment_gateway, personal_info):
    exchange_owner = users['admin']
    deploy_args = [
        payment_gateway.address,
        personal_info.address,
        1234
    ]
    with pytest.raises(ValueError):
        exchange_owner.deploy(
            IbetOTCExchange, *deploy_args)


'''
TEST_Make注文（createOrder）
'''


# 正常系１
# ＜発行体＞新規発行 -> ＜発行体＞新規注文
def test_createorder_normal_1(users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    personalinfo_register(personal_info, issuer, issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    _amount = 100
    share_token.transfer.transact(otc_exchange.address, _amount, {'from': issuer})

    # 新規注文
    _amount = 100
    _price = 123
    otc_exchange.createOrder.transact(trader, share_token.address, _amount, _price, agent, {'from': issuer})

    order_id = otc_exchange.latestOrderId()
    orderbook = otc_exchange.getOrder(order_id)
    commitment = otc_exchange.commitmentOf(issuer, share_token.address)

    assert orderbook == [
        issuer.address, trader.address, to_checksum_address(share_token.address), _amount, _price,
        agent.address, False
    ]
    assert share_token.balanceOf(issuer) == deploy_args[3] - _amount
    assert commitment == _amount


# エラー系1
# 入力値の型誤り（_counterpart）
def test_createorder_error_1(users, otc_exchange, personal_info):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # 新規注文
    _price = 123
    _amount = 100

    with pytest.raises(ValueError):
        otc_exchange.createOrder.transact('1234', share_token.address, _amount, _price, agent, {'from': issuer})

    with pytest.raises(ValueError):
        otc_exchange.createOrder.transact(1234, share_token.address, _amount, _price, agent, {'from': issuer})


# エラー系2
# 入力値の型誤り（_token）
def test_createorder_error_2(users, otc_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規注文
    _price = 123
    _amount = 100

    with pytest.raises(ValueError):
        otc_exchange.createOrder.transact(trader, '1234', _amount, _price, agent, {'from': issuer})

    with pytest.raises(ValueError):
        otc_exchange.createOrder.transact(trader, 1234, _amount, _price, agent, {'from': issuer})


# エラー系3
# 入力値の型誤り（_amount）
def test_createorder_error_3(users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # 新規注文
    _price = 123

    with pytest.raises(OverflowError):
        otc_exchange.createOrder.transact(
            trader, share_token.address, -1, _price, agent, {'from': issuer})

    with pytest.raises(OverflowError):
        otc_exchange.createOrder.transact(
            trader, share_token.address, 2 ** 256, _price, agent, {'from': issuer})

    with pytest.raises(TypeError):
        otc_exchange.createOrder.transact(
            trader, share_token.address, 'A', _price, agent, {'from': issuer})


# エラー系4
# 入力値の型誤り（_price）
def test_createorder_error_4(users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # 新規注文
    _amount = 100

    with pytest.raises(OverflowError):
        otc_exchange.createOrder.transact(
            trader, share_token.address, _amount, -1, agent, {'from': issuer})

    with pytest.raises(OverflowError):
        otc_exchange.createOrder.transact(
            trader, share_token.address, _amount, 2 ** 256, agent, {'from': issuer})

    with pytest.raises(TypeError):
        otc_exchange.createOrder.transact(
            trader, share_token.address, _amount, 'G', agent, {'from': issuer})


# エラー系5
# 入力値の型誤り（_agent）
def test_createorder_error_5(users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # 新規注文
    _price = 123
    _amount = 100

    with pytest.raises(ValueError):
        otc_exchange.createOrder.transact(
            trader, share_token.address, _amount, _price, '1234', {'from': issuer})

    with pytest.raises(ValueError):
        otc_exchange.createOrder.transact(
            trader, share_token.address, _amount, _price, 1234, {'from': issuer})


# エラー系6
# 売注文数量が0の場合
def test_createorder_error_6(users, otc_exchange, personal_info):
    issuer = users['issuer']
    agent = users['agent']
    trader = users['trader']

    personalinfo_register(personal_info, issuer, issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    _amount = 100
    share_token.transfer.transact(otc_exchange.address, _amount, {'from': issuer})

    # 新規注文
    _amount = 0
    _price = 123
    otc_exchange.createOrder.transact(trader, share_token.address, _amount, _price, agent,
                                      {'from': issuer})  # エラーになる

    commitment = otc_exchange.commitmentOf(issuer, share_token.address)
    balance = share_token.balanceOf(issuer)

    assert balance == deploy_args[3]
    assert commitment == 0


# エラー系7
# 名簿用個人情報が登録されていない場合
def test_createorder_error_7(users, otc_exchange, personal_info):
    issuer = users['issuer']
    agent = users['agent']
    trader = users['trader']

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    _amount = 100
    share_token.transfer.transact(otc_exchange.address, _amount, {'from': issuer})

    # 新規注文
    _amount = 100
    _price = 123
    otc_exchange.createOrder.transact(trader, share_token.address, _amount, _price, agent,
                                      {'from': issuer})  # エラーになる

    commitment = otc_exchange.commitmentOf(issuer, share_token.address)
    balance = share_token.balanceOf(issuer)

    assert balance == deploy_args[3]
    assert commitment == 0


# エラー系8
# 残高不足
def test_createorder_error_8(users, otc_exchange, personal_info):
    issuer = users['issuer']
    agent = users['agent']
    trader = users['trader']

    personalinfo_register(personal_info, issuer, issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    _amount = 100
    share_token.transfer.transact(otc_exchange.address, _amount, {'from': issuer})

    # 新規注文
    _price = 123
    otc_exchange.createOrder.transact(trader, share_token.address, _amount + 1, _price, agent,
                                      {'from': issuer})  # エラーになる

    commitment = otc_exchange.commitmentOf(issuer, share_token.address)
    balance = share_token.balanceOf(issuer)

    assert balance == deploy_args[3]
    assert commitment == 0


# エラー系9
# 無効な収納代行業者（Agent）の指定
def test_createorder_error_9(users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    attacker = users['admin']

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    _amount = 100
    share_token.transfer.transact(otc_exchange.address, _amount, {'from': issuer})

    # 新規注文
    _amount = 100
    _price = 123
    otc_exchange.createOrder.transact(trader, share_token.address, _amount, _price, attacker,
                                      {'from': issuer})  # エラーになる

    commitment = otc_exchange.commitmentOf(issuer, share_token.address)
    balance = share_token.balanceOf(issuer)

    assert balance == deploy_args[3]
    assert commitment == 0


# エラー系10
# 取扱ステータスがFalseの場合
def test_createorder_error_10(users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    personalinfo_register(personal_info, issuer, issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # ステータス変更
    share_token.setStatus.transact(False, {'from': issuer})

    # Exchangeへのデポジット
    _amount = 100
    share_token.transfer.transact(otc_exchange.address, _amount, {'from': issuer})

    # 新規注文
    _price = 123
    otc_exchange.createOrder.transact(trader, share_token.address, _amount, _price, agent,
                                      {'from': issuer})  # エラーになる

    commitment = otc_exchange.commitmentOf(issuer, share_token.address)
    balance = share_token.balanceOf(issuer)
    assert balance == deploy_args[3]
    assert commitment == 0


'''
TEST_getOrder
'''


# エラー系1
# 入力値の型誤り（orderId）
def test_getOrder_error_1(users, otc_exchange):
    issuer = users['issuer']

    with pytest.raises(TypeError):
        otc_exchange.getOrder.transact("One", {'from': issuer})
    with pytest.raises(OverflowError):
        otc_exchange.getOrder.transact(-1, {'from': issuer})
    with pytest.raises(OverflowError):
        otc_exchange.getOrder.transact(2 ** 256, {'from': issuer})


'''
TEST_注文キャンセル（cancelOrder）
'''


# 正常系1
# ＜発行体＞新規発行 -> ＜投資家（発行体）＞新規注文
#  -> ＜投資家（発行体）＞注文キャンセル
def test_cancelOrder_normal_1(users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    personalinfo_register(personal_info, issuer, issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    _amount = 100
    share_token.transfer.transact(otc_exchange.address, _amount, {'from': issuer})

    # 新規注文
    _price = 123
    otc_exchange.createOrder.transact(trader, share_token.address, _amount, _price, agent, {'from': issuer})

    # 注文キャンセル
    order_id = otc_exchange.latestOrderId()
    otc_exchange.cancelOrder.transact(order_id, {'from': issuer})

    orderbook = otc_exchange.getOrder(order_id)
    commitment = otc_exchange.commitmentOf(issuer, share_token.address)

    assert orderbook == [
        issuer.address, trader.address, to_checksum_address(share_token.address), _amount, _price, agent.address, True
    ]
    assert share_token.balanceOf(issuer) == deploy_args[3]
    assert commitment == 0


# エラー系1
# 入力値の型誤り（_orderId）
def test_cancelOrder_error_1(users, otc_exchange):
    issuer = users['issuer']

    # 注文キャンセル

    with pytest.raises(OverflowError):
        otc_exchange.cancelOrder.transact(-1, {'from': issuer})

    with pytest.raises(OverflowError):
        otc_exchange.cancelOrder.transact(2 ** 256, {'from': issuer})

    with pytest.raises(TypeError):
        otc_exchange.cancelOrder.transact('One', {'from': issuer})


# エラー系2
# 指定した注文IDが直近の注文IDを超えている場合
def test_cancelOrder_error_2(users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    personalinfo_register(personal_info, issuer, issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    _amount = 100
    share_token.transfer.transact(otc_exchange.address, _amount, {'from': issuer})

    # 新規注文
    _amount = 100
    _price = 123
    otc_exchange.createOrder.transact(trader, share_token.address, _amount, _price, agent, {'from': issuer})

    # 注文キャンセル
    order_id = otc_exchange.latestOrderId() + 1
    commitment = otc_exchange.commitmentOf(issuer, share_token.address)

    otc_exchange.cancelOrder.transact(order_id, {'from': issuer})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id - 1)
    assert orderbook == [
        issuer.address, trader.address, to_checksum_address(share_token.address), _amount, _price, agent.address, False
    ]
    # キャンセルがエラーとなっているため、注文中の状態

    assert share_token.balanceOf(issuer) == deploy_args[3] - _amount
    assert commitment == 100


# エラー系3
# 注文がキャンセル済みの場合
def test_cancelOrder_error_3(users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    personalinfo_register(personal_info, issuer, issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    _amount = 100
    share_token.transfer.transact(otc_exchange.address, _amount, {'from': issuer})

    # 新規注文
    _amount = 100
    _price = 123
    otc_exchange.createOrder.transact(trader, share_token.address, _amount, _price, agent, {'from': issuer})

    # 注文キャンセル
    order_id = otc_exchange.latestOrderId()
    otc_exchange.cancelOrder.transact(order_id, {'from': issuer})

    # 注文キャンセル（2回目）
    otc_exchange.cancelOrder.transact(order_id, {'from': issuer})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    commitment = otc_exchange.commitmentOf(issuer, share_token.address)

    assert orderbook == [
        issuer.address, trader.address, to_checksum_address(share_token.address), _amount, _price, agent.address, True
    ]
    assert share_token.balanceOf(issuer) == deploy_args[3]
    assert commitment == 0


# エラー系4
# 元注文の発注者と、注文キャンセルの実施者が異なる場合
def test_cancelOrder_error_4(users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    other = users['admin']
    agent = users['agent']

    personalinfo_register(personal_info, issuer, issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    _amount = 100
    share_token.transfer.transact(otc_exchange.address, _amount, {'from': issuer})

    # 新規注文
    _price = 123
    otc_exchange.createOrder.transact(trader, share_token.address, _amount, _price, agent, {'from': issuer})

    # 注文キャンセル
    order_id = otc_exchange.latestOrderId()
    otc_exchange.cancelOrder.transact(order_id, {'from': other})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    balance = share_token.balanceOf(issuer)
    commitment = otc_exchange.commitmentOf(issuer, share_token.address)

    assert orderbook == [
        issuer.address, trader.address, to_checksum_address(share_token.address), _amount, _price, agent.address, False
    ]
    assert balance == deploy_args[3] - _amount
    assert commitment == _amount


# エラー系5
# トークンのstatusが取扱不可となっている場合
def test_cancelOrder_error_5(users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    other = users['admin']
    agent = users['agent']

    personalinfo_register(personal_info, issuer, issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    _amount = 100
    share_token.transfer.transact(otc_exchange.address, _amount, {'from': issuer})

    # 新規注文
    _price = 123
    otc_exchange.createOrder.transact(trader, share_token.address, _amount, _price, agent, {'from': issuer})

    # トークンの取扱不可
    share_token.setStatus.transact(False, {'from': issuer})

    # 注文キャンセル
    order_id = otc_exchange.latestOrderId()
    otc_exchange.cancelOrder.transact(order_id, {'from': other})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    balance = share_token.balanceOf(issuer)
    commitment = otc_exchange.commitmentOf(issuer, share_token.address)

    assert orderbook == [
        issuer.address, trader.address, to_checksum_address(share_token.address), _amount, _price, agent.address, False
    ]
    assert balance == deploy_args[3] - _amount
    assert commitment == _amount


'''
TEST_Take注文（executeOrder）
'''


# 正常系1
# ＜発行体＞新規発行 -> ＜発行体＞新規注文 -> ＜投資家＞Take注文
def test_executeOrder_normal_1(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # make
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # take
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    agreement_id = otc_exchange.latestAgreementId(order_id)

    orderbook = otc_exchange.getOrder(order_id)
    agree = otc_exchange.getAgreement(order_id, agreement_id)

    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]

    assert agree[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系1
# 入力値の型誤り（_orderId）
def test_executeOrder_error_1(users, otc_exchange):
    _trader = users['trader']

    with pytest.raises(OverflowError):
        otc_exchange.executeOrder.transact(-1, {'from': _trader})

    with pytest.raises(OverflowError):
        otc_exchange.executeOrder.transact(2 ** 256, {'from': _trader})

    with pytest.raises(TypeError):
        otc_exchange.executeOrder.transact('a', {'from': _trader})


# エラー系2
# 指定した注文IDが直近の注文IDを超えている場合
def test_executeOrder_error_2(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # make
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    latest_order_id_error = otc_exchange.latestOrderId() + 1
    latest_order_id = otc_exchange.latestOrderId()

    # Take注文
    order_id = latest_order_id_error
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})  # エラーになる

    orderbook = otc_exchange.getOrder(latest_order_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, _agent, False
    ]

    assert balance_maker == deploy_args[3] - _amount_make
    assert commitment == _amount_make

    assert balance_taker == 0


# エラー系3
# 元注文の発注者と同一のアドレスからの発注の場合
# Take買注文
def test_executeOrder_error_3(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # 預かりをExchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # Take注文：発行体
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _issuer})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    balance_maker = share_token.balanceOf(_issuer)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, _agent, False
    ]

    assert balance_maker == deploy_args[3] - _amount_make
    assert commitment == _amount_make


# エラー系4
# 元注文がキャンセル済の場合
# Take買注文
def test_executeOrder_error_4(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # 預かりをExchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(
        _trader, share_token.address, _amount_make, _price, _agent, {'from': _issuer})

    order_id = otc_exchange.latestOrderId()

    # Make注文取消：発行体
    otc_exchange.cancelOrder.transact(order_id, {'from': _issuer})

    # Take注文：投資家
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, _agent, True  # 取消済み状態
    ]
    assert balance_maker == deploy_args[3]
    assert balance_taker == 0
    assert commitment == 0


# エラー系5
# 名簿用個人情報が登録されていない場合
# Take買注文
def test_executeOrder_error_5(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # 預かりをExchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    order_id = otc_exchange.latestOrderId()

    # Take注文：投資家
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, _agent, False
    ]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系6
# 取扱ステータスがFalseの場合
def test_executeOrder_error_6(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # 預かりをExchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent, {'from': _issuer})

    order_id = otc_exchange.latestOrderId()

    # ステータス変更：発行体
    share_token.setStatus.transact(False, {'from': _issuer})

    # Take注文：投資家
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, _agent, False
    ]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系7
# 第三者からtake注文があった場合
def test_executeOrder_error_7(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _attacker = users['admin']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # 預かりをExchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent, {'from': _issuer})

    order_id = otc_exchange.latestOrderId()

    # ステータス変更：発行体
    share_token.setStatus.transact(False, {'from': _issuer})

    # Take注文：第三者
    otc_exchange.executeOrder.transact(order_id, {'from': _attacker})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    balance_attacker = share_token.balanceOf(_attacker)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, _agent, False
    ]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == 0
    assert balance_attacker == 0
    assert commitment == _amount_make


# エラー系8
# 複数回take注文があった場合
def test_executeOrder_error_8(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # make
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # take (1回目)
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    first_agreement_id = otc_exchange.latestAgreementId(order_id)

    # take (2回目)
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    agreement_id = otc_exchange.latestAgreementId(order_id)
    orderbook = otc_exchange.getOrder(order_id)
    agree = otc_exchange.getAgreement(order_id, agreement_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert agreement_id == first_agreement_id

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]

    assert agree[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


'''
TEST_決済承認（confirmAgreement）
'''


# 正常系1
# ＜発行体＞新規発行 -> ＜発行体＞Make注文
#  -> ＜投資家＞Take注文 -> ＜決済業者＞決済処理
def test_confirmAgreement_normal_1(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # Take注文：投資家
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    agreement_id = otc_exchange.latestAgreementId(order_id)

    # 決済承認：決済業者
    otc_exchange.confirmAgreement.transact(order_id, agreement_id, {'from': _agent})

    orderbook = otc_exchange.getOrder(order_id)
    agreement = otc_exchange.getAgreement(order_id, agreement_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]

    assert agreement[0:5] == [_trader, _amount_make, _price, False, True]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == _amount_make
    assert commitment == 0


# エラー系1
# 入力値の型誤り（_orderId）
def test_confirmAgreement_error_1(users, otc_exchange):
    _agent = users['agent']

    # 決済承認：決済業者

    with pytest.raises(OverflowError):
        otc_exchange.confirmAgreement.transact(-1, 0, {'from': _agent})

    with pytest.raises(OverflowError):
        otc_exchange.confirmAgreement.transact(2 ** 256, 0, {'from': _agent})

    with pytest.raises(TypeError):
        otc_exchange.confirmAgreement.transact('a', 0, {'from': _agent})


# エラー系2
# 入力値の型誤り（_agreementId）
def test_confirmAgreement_error_2(users, otc_exchange):
    _agent = users['agent']

    # 決済承認：決済業者

    with pytest.raises(OverflowError):
        otc_exchange.confirmAgreement.transact(0, -1, {'from': _agent})

    with pytest.raises(OverflowError):
        otc_exchange.confirmAgreement.transact(0, 2 ** 256, {'from': _agent})

    with pytest.raises(TypeError):
        otc_exchange.confirmAgreement.transact(0, 'a', {'from': _agent})


# エラー系3
# 指定した注文番号が、直近の注文ID以上の場合
def test_confirmAgreement_error_3(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # Take注文：投資家
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    agreement_id = otc_exchange.latestAgreementId(order_id)

    # 決済承認：決済業者
    order_id_error = otc_exchange.latestOrderId() + 1
    otc_exchange.confirmAgreement.transact(order_id_error, agreement_id, {'from': _agent})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    agreement = otc_exchange.getAgreement(order_id, agreement_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]

    assert agreement[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系4
# 指定した約定IDが、直近の約定ID以上の場合
def test_confirmAgreement_error_4(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # Take注文：投資家
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    agreement_id = otc_exchange.latestAgreementId(order_id)

    # 決済承認：決済業者
    agreement_id_error = otc_exchange.latestAgreementId(order_id) + 1
    otc_exchange.confirmAgreement.transact(order_id, agreement_id_error, {'from': _agent})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    agreement = otc_exchange.getAgreement(order_id, agreement_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]

    assert agreement[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系5
# 指定した約定明細がすでに支払い済みの状態の場合
def test_confirmAgreement_error_5(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # Take注文：投資家
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    agreement_id = otc_exchange.latestAgreementId(order_id)

    # 決済承認：決済業者
    otc_exchange.confirmAgreement.transact(
        order_id, agreement_id, {'from': _agent})

    # 決済承認：決済業者（2回目）
    otc_exchange.confirmAgreement.transact(order_id, agreement_id, {'from': _agent})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    agreement = otc_exchange.getAgreement(order_id, agreement_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, False, True]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == _amount_make
    assert commitment == 0


# エラー系6
# 元注文で指定した決済業者ではない場合
def test_confirmAgreement_error_6(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # Take注文：投資家
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    agreement_id = otc_exchange.latestAgreementId(order_id)

    # 決済承認：投資家（指定した決済業者ではない）
    otc_exchange.confirmAgreement.transact(order_id, agreement_id, {'from': _trader})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    agreement = otc_exchange.getAgreement(order_id, agreement_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]

    assert agreement[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系7
# 既に決済非承認済み（キャンセル済み）の場合
def test_confirmAgreement_error_7(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # Take注文：投資家
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    agreement_id = otc_exchange.latestAgreementId(order_id)

    # 決済非承認：決済業者
    otc_exchange.cancelAgreement.transact(
        order_id, agreement_id, {'from': _agent})

    # 決済承認：決済業者
    otc_exchange.confirmAgreement.transact(order_id, agreement_id, {'from': _agent})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    agreement = otc_exchange.getAgreement(order_id, agreement_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        _amount_make, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, True, False]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系8
# トークンの取扱ステータスがFalse（不可）の場合
def test_confirmAgreement_error_8(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # Take注文：投資家
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    agreement_id = otc_exchange.latestAgreementId(order_id)

    # トークンの取扱不可
    share_token.setStatus.transact(False, {'from': _issuer})

    # 決済承認：決済業者
    otc_exchange.confirmAgreement.transact(order_id, agreement_id, {'from': _agent})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    agreement = otc_exchange.getAgreement(order_id, agreement_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


'''
TEST_getAgreement
'''


# 異常系1
# 入力値の型誤り（orderId, agreementId）
def test_getAgreement_error_1(users, otc_exchange):
    issuer = users['issuer']

    with pytest.raises(TypeError):
        otc_exchange.getAgreement.transact("A", 1, {'from': issuer})
    with pytest.raises(OverflowError):
        otc_exchange.getAgreement.transact(-1, 1, {'from': issuer})
    with pytest.raises(OverflowError):
        otc_exchange.getAgreement.transact(2 ** 256, 1, {'from': issuer})
    with pytest.raises(TypeError):
        otc_exchange.getAgreement.transact(1, "Z", {'from': issuer})
    with pytest.raises(OverflowError):
        otc_exchange.getAgreement.transact(1, -1, {'from': issuer})
    with pytest.raises(OverflowError):
        otc_exchange.getAgreement.transact(1, 2 ** 256, {'from': issuer})


'''
TEST_決済非承認（cancelAgreement）
'''


# 正常系1
# Make売、Take買
# ＜発行体＞新規発行 -> ＜発行体＞Make注文
#  -> ＜投資家＞Take注文-> ＜決済業者＞決済非承認
def test_cancelAgreement_normal_1(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # Take注文：投資家
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    agreement_id = otc_exchange.latestAgreementId(order_id)

    # 決済非承認：決済業者
    otc_exchange.cancelAgreement.transact(
        order_id, agreement_id, {'from': _agent})

    orderbook = otc_exchange.getOrder(order_id)
    agreement = otc_exchange.getAgreement(order_id, agreement_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        _amount_make, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, True, False]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系1
# 入力値の型誤り（_orderId）
def test_cancelAgreement_error_1(users, otc_exchange):
    _agent = users['agent']

    # 決済非承認：決済業者

    with pytest.raises(OverflowError):
        otc_exchange.cancelAgreement.transact(-1, 0, {'from': _agent})

    with pytest.raises(OverflowError):
        otc_exchange.cancelAgreement.transact(2 ** 256, 0, {'from': _agent})

    with pytest.raises(TypeError):
        otc_exchange.cancelAgreement.transact('A', 0, {'from': _agent})


# エラー系2
# 入力値の型誤り（_agreementId）
def test_cancelAgreement_error_2(users, otc_exchange):
    _agent = users['agent']

    # 決済非承認：決済業者

    with pytest.raises(OverflowError):
        otc_exchange.cancelAgreement.transact(0, -1, {'from': _agent})

    with pytest.raises(OverflowError):
        otc_exchange.cancelAgreement.transact(0, 2 ** 256, {'from': _agent})

    with pytest.raises(TypeError):
        otc_exchange.cancelAgreement.transact(0, 'A', {'from': _agent})


# エラー系3
# 指定した注文番号が、直近の注文ID以上の場合
def test_cancelAgreement_error_3(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # Take注文：投資家
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    agreement_id = otc_exchange.latestAgreementId(order_id)

    # 決済非承認：決済業者
    order_id_error = otc_exchange.latestOrderId() + 1
    otc_exchange.cancelAgreement.transact(order_id_error, agreement_id, {'from': _agent})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    agreement = otc_exchange.getAgreement(order_id, agreement_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系4
# 指定した約定IDが、直近の約定ID以上の場合
def test_cancelAgreement_error_4(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # Take注文：投資家
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    agreement_id = otc_exchange.latestAgreementId(order_id)

    # 決済非承認：決済業者
    agreement_id_error = otc_exchange.latestAgreementId(order_id) + 1
    otc_exchange.cancelAgreement.transact(order_id, agreement_id_error, {'from': _agent})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    agreement = otc_exchange.getAgreement(order_id, agreement_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系5
# すでに決済承認済み（支払済み）の場合
def test_cancelAgreement_error_5(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # Take注文：投資家
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    agreement_id = otc_exchange.latestAgreementId(order_id)

    # 決済承認：決済業者
    otc_exchange.confirmAgreement.transact(
        order_id, agreement_id, {'from': _agent})

    # 決済非承認：決済業者
    otc_exchange.cancelAgreement.transact(order_id, agreement_id, {'from': _agent})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    agreement = otc_exchange.getAgreement(order_id, agreement_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, False, True]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == _amount_make
    assert commitment == 0


# エラー系6
# msg.senderが、決済代行（agent）以外の場合
def test_cancelAgreement_error_6(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # Take注文：投資家
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    agreement_id = otc_exchange.latestAgreementId(order_id)

    # 決済非承認：投資家（決済業者以外）
    otc_exchange.cancelAgreement.transact(order_id, agreement_id, {'from': _trader})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    agreement = otc_exchange.getAgreement(order_id, agreement_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系7
# すでに決済非承認済み（キャンセル済み）の場合
def test_cancelAgreement_error_7(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(
        _trader, share_token.address, _amount_make, _price, _agent, {'from': _issuer})

    # Take注文：投資家
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    agreement_id = otc_exchange.latestAgreementId(order_id)

    # 決済非承認：決済業者
    otc_exchange.cancelAgreement.transact(
        order_id, agreement_id, {'from': _agent})

    # 決済非承認：決済業者（2回目）
    otc_exchange.cancelAgreement.transact(order_id, agreement_id, {'from': _agent})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    agreement = otc_exchange.getAgreement(order_id, agreement_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        _amount_make, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, True, False]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系8
# トークンが取扱不可の場合
def test_cancelAgreement_error_8(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Make注文：発行体
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # Take注文：投資家
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    agreement_id = otc_exchange.latestAgreementId(order_id)

    # トークンの取扱不可
    share_token.setStatus.transact(False, {'from': _issuer})

    # 決済非承認
    otc_exchange.cancelAgreement.transact(order_id, agreement_id, {'from': _agent})  # エラーになる

    orderbook = otc_exchange.getOrder(order_id)
    agreement = otc_exchange.getAgreement(order_id, agreement_id)
    balance_maker = share_token.balanceOf(_issuer)
    balance_taker = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[3] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


'''
TEST_引き出し（withdrawAll）
'''


# 正常系1
# ＜発行体＞新規発行 -> ＜発行体＞デポジット -> ＜発行体＞引き出し
def test_withdrawAll_normal_1(users, otc_exchange, personal_info):
    _issuer = users['issuer']

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # 引き出し：発行体
    otc_exchange.withdrawAll.transact(share_token.address, {'from': _issuer})

    balance_exchange = otc_exchange.balanceOf(_issuer, share_token.address)
    balance_token = share_token.balanceOf(_issuer)

    assert balance_exchange == 0
    assert balance_token == deploy_args[3]


# 正常系2
# ＜発行体＞新規発行 -> ＜発行体＞デポジット（2回） -> ＜発行体＞引き出し
def test_withdrawAll_normal_2(users, otc_exchange, personal_info):
    _issuer = users['issuer']

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # Exchangeへのデポジット（2回目）：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # 引き出し：発行体
    otc_exchange.withdrawAll.transact(share_token.address, {'from': _issuer})

    balance_exchange = otc_exchange.balanceOf(_issuer, share_token.address)
    balance_token = share_token.balanceOf(_issuer)

    assert balance_exchange == 0
    assert balance_token == deploy_args[3]


# 正常系3
# ＜発行体＞新規発行 -> ＜発行体＞Make注文 ※売注文中状態
#  -> ＜発行体＞引き出し
def test_withdrawAll_normal_3(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_transfer = 100
    share_token.transfer.transact(otc_exchange.address, _amount_transfer, {'from': _issuer})

    # Make注文：発行体
    _amount_make = 70  # 100のうち70だけ売注文
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # 引き出し：発行体
    otc_exchange.withdrawAll.transact(share_token.address, {'from': _issuer})

    balance_exchange = otc_exchange.balanceOf(_issuer, share_token.address)
    balance_token = share_token.balanceOf(_issuer)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert balance_exchange == 0
    assert balance_token == deploy_args[3] - _amount_make
    assert commitment == _amount_make


# 正常系4
# ＜発行体＞新規発行 -> ＜発行体＞Make注文 -> ＜投資家＞Take注文
#  -> ＜発行体＞引き出し
def test_withdrawAll_normal_4(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_transfer = 100
    share_token.transfer.transact(otc_exchange.address, _amount_transfer, {'from': _issuer})

    # Make注文：発行体
    _amount_make = 70  # 100のうち70だけ売注文
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # Take注文：投資家
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    # 引き出し：発行体
    otc_exchange.withdrawAll.transact(share_token.address, {'from': _issuer})

    balance_exchange = otc_exchange.balanceOf(_issuer, share_token.address)
    balance_issuer = share_token.balanceOf(_issuer)
    balance_trader = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    # 約定済みのトークンはそのまま。
    assert balance_exchange == 0
    assert balance_issuer == deploy_args[3] - _amount_make
    assert balance_trader == 0
    assert commitment == _amount_make


# 正常系5
# ＜発行体＞新規発行 -> ＜発行体＞Make注文 -> ＜投資家＞Take注文
#  -> ＜決済業者＞決済承認 -> ＜発行体＞引き出し
def test_withdrawAll_normal_5(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(personal_info, _issuer, _issuer)
    personalinfo_register(personal_info, _trader, _issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_transfer = 100
    share_token.transfer.transact(otc_exchange.address, _amount_transfer, {'from': _issuer})

    # Make注文：発行体
    _amount_make = 70  # 100のうち70だけ売注文
    _price = 123
    otc_exchange.createOrder.transact(_trader, share_token.address, _amount_make, _price, _agent,
                                      {'from': _issuer})

    # Take注文：投資家
    order_id = otc_exchange.latestOrderId()
    otc_exchange.executeOrder.transact(order_id, {'from': _trader})

    agreement_id = otc_exchange.latestAgreementId(order_id)

    # 決済承認：決済業者
    otc_exchange.confirmAgreement.transact(
        order_id, agreement_id, {'from': _agent})

    # 引き出し：発行体
    otc_exchange.withdrawAll.transact(share_token.address, {'from': _issuer})

    balance_issuer_exchange = otc_exchange.balanceOf(_issuer, share_token.address)
    balance_issuer_token = share_token.balanceOf(_issuer)
    balance_trader_exchange = otc_exchange.balanceOf(_trader, share_token.address)
    balance_trader_token = share_token.balanceOf(_trader)
    commitment = otc_exchange.commitmentOf(_issuer, share_token.address)

    assert balance_issuer_exchange == 0
    assert balance_issuer_token == deploy_args[3] - _amount_make
    assert balance_trader_exchange == 0
    assert balance_trader_token == _amount_make
    assert commitment == 0


# エラー系１
# 入力値の型誤り（_token）
def test_withdrawAll_error_1(users, otc_exchange):
    _issuer = users['issuer']

    # 引き出し：発行体

    with pytest.raises(ValueError):
        otc_exchange.withdrawAll.transact(1234, {'from': _issuer})

    with pytest.raises(ValueError):
        otc_exchange.withdrawAll.transact('1234', {'from': _issuer})


# エラー系2-1
# 残高がゼロの場合
# ＜発行体＞新規発行 -> ＜発行体＞デポジット -> ＜発行体＞引き出し（2回）
def test_withdrawAll_error_2_1(users, otc_exchange, personal_info):
    _issuer = users['issuer']

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_make = 100
    share_token.transfer.transact(otc_exchange.address, _amount_make, {'from': _issuer})

    # 引き出し：発行体
    otc_exchange.withdrawAll.transact(share_token.address, {'from': _issuer})

    # 引き出し（2回目)：発行体
    otc_exchange.withdrawAll.transact(share_token.address, {'from': _issuer})  # エラーになる

    balance_exchange = otc_exchange.balanceOf(_issuer, share_token.address)
    balance_token = share_token.balanceOf(_issuer)

    assert balance_exchange == 0
    assert balance_token == deploy_args[3]


# エラー系2-2
# 残高がゼロの場合
# ＜発行体＞新規発行 -> ＜発行体＞デポジット -> 異なるアドレスからの引き出し
def test_withdrawAll_error_2_2(users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_transfer = 100
    share_token.transfer.transact(
        otc_exchange.address, _amount_transfer, {'from': _issuer})

    # 引き出し：異なるアドレス
    otc_exchange.withdrawAll.transact(share_token.address, {'from': _trader})  # エラーになる

    balance_exchange = otc_exchange.balanceOf(_issuer, share_token.address)
    balance_token = share_token.balanceOf(_issuer)

    assert balance_exchange == _amount_transfer
    assert balance_token == deploy_args[3] - _amount_transfer


# エラー系3
# トークンの取扱が不可の場合
# ＜発行体＞新規発行 -> ＜発行体＞取扱不可設定 -> 引き出し
def test_withdrawAll_error_3(users, otc_exchange, personal_info):
    _issuer = users['issuer']

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    _amount_transfer = 100
    share_token.transfer.transact(otc_exchange.address, _amount_transfer, {'from': _issuer})

    # トークンの取扱不可設定
    share_token.setStatus.transact(False, {'from': _issuer})

    # 引き出し
    otc_exchange.withdrawAll.transact(share_token.address, {'from': _issuer})  # エラーになる

    balance_exchange = otc_exchange.balanceOf(_issuer, share_token.address)
    balance_token = share_token.balanceOf(_issuer)

    assert balance_exchange == _amount_transfer
    assert balance_token == deploy_args[3] - _amount_transfer


'''
TEST_Exchange切替
'''


# 正常系
def test_updateExchange_normal_1(
        users,
        otc_exchange, otc_exchange_storage,
        personal_info, payment_gateway, exchange_regulator_service,
        IbetOTCExchange):
    issuer = users['issuer']
    agent = users['agent']
    trader = users['trader']
    admin = users['admin']

    personalinfo_register(personal_info, issuer, issuer)

    # 新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    deposit_amount = 100
    share_token.transfer.transact(otc_exchange.address, deposit_amount, {'from': issuer})

    # 新規注文
    amount_make = 10
    price = 123
    otc_exchange.createOrder.transact(trader, share_token.address, amount_make, price, agent,
                                      {'from': issuer})

    # Exchange（新）のデプロイ
    otc_exchange_new = admin.deploy(
        IbetOTCExchange,
        payment_gateway.address,
        personal_info.address,
        otc_exchange_storage.address,
        exchange_regulator_service.address
    )
    # ストレージの切り替え
    otc_exchange_storage.upgradeVersion.transact(otc_exchange_new.address, {'from': admin})

    # Exchange（新）からの情報参照
    order_id = otc_exchange_new.latestOrderId()
    orderbook = otc_exchange_new.getOrder(order_id)
    commitment = otc_exchange_new.commitmentOf(issuer, share_token.address)
    balance_exchange = otc_exchange_new.balanceOf(issuer, share_token.address)
    balance_token = share_token.balanceOf(issuer)

    assert orderbook == [
        issuer.address, trader.address, to_checksum_address(share_token.address),
        amount_make, price, agent.address, False
    ]
    assert balance_token == deploy_args[3] - deposit_amount
    assert balance_exchange == deposit_amount - amount_make
    assert commitment == amount_make
