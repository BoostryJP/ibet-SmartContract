import pytest
from eth_utils import to_checksum_address
import utils

'''
共通処理
'''


# PersonalInfo登録
def personalinfo_register(web3, chain, personalinfo, trader, issuer):
    web3.eth.defaultAccount = trader
    message = 'some_message'
    txn_hash = personalinfo.transact().register(issuer, message)
    chain.wait.for_receipt(txn_hash)


# PaymentGatewayアカウント登録
def payment_gateway_register(web3, chain, payment_gateway, trader, agent):
    web3.eth.defaultAccount = trader
    message = 'some_message'
    txn_hash = payment_gateway.transact().register(agent, message)
    chain.wait.for_receipt(txn_hash)


# トークンを取引所にデポジット
def transfer(web3, chain, token, otc_exchange, trader, amount):
    web3.eth.defaultAccount = trader
    txn_hash = token.transact().transfer(
        otc_exchange.address, amount)
    chain.wait.for_receipt(txn_hash)


'''
TEST_デプロイ
'''


# ＜正常系1＞
# Deploy　→　正常
def test_deploy_normal_1(users, otc_exchange, otc_exchange_storage, personal_info, payment_gateway):
    owner = otc_exchange.call().owner()
    personal_info_address = otc_exchange.call().personalInfoAddress()
    payment_gateway_address = otc_exchange.call().paymentGatewayAddress()
    storage_address = otc_exchange.call().storageAddress()

    assert owner == users['admin']
    assert personal_info_address == to_checksum_address(personal_info.address)
    assert payment_gateway_address == to_checksum_address(payment_gateway.address)
    assert storage_address == to_checksum_address(otc_exchange_storage.address)


# ＜エラー系1＞
# 入力値の型誤り（PaymentGatewayアドレス）
def test_deploy_error_1(web3, users, chain, personal_info, otc_exchange_storage):
    exchange_owner = users['admin']
    web3.eth.defaultAccount = exchange_owner

    deploy_args = [
        1234,
        personal_info.address,
        otc_exchange_storage.address
    ]

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetOTCExchange',
            deploy_args=deploy_args
        )


# ＜エラー系2＞
# 入力値の型誤り（PersonalInfoアドレス）
def test_deploy_error_2(web3, users, chain, payment_gateway, otc_exchange_storage):
    exchange_owner = users['admin']
    web3.eth.defaultAccount = exchange_owner
    deploy_args = [
        payment_gateway.address,
        1234,
        otc_exchange_storage.address
    ]
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetOTCExchange', deploy_args=deploy_args)


# ＜エラー系3＞
# 入力値の型誤り（Storageアドレス）
def test_deploy_error_3(web3, users, chain, payment_gateway, personal_info):
    exchange_owner = users['admin']
    web3.eth.defaultAccount = exchange_owner
    deploy_args = [
        payment_gateway.address,
        personal_info.address,
        1234
    ]
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetOTCExchange', deploy_args=deploy_args)


'''
TEST_Make注文（createOrder）
'''


# 正常系１
# ＜発行体＞新規発行 -> ＜発行体＞新規注文
def test_createorder_normal_1(web3, chain, users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)

    # 新規発行
    web3.eth.defaultAccount = issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    _amount = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文
    _amount = 100
    _price = 123
    txn_hash = otc_exchange.transact().createOrder(trader, share_token.address, _amount, _price, agent)
    chain.wait.for_receipt(txn_hash)

    order_id = otc_exchange.call().latestOrderId()
    orderbook = otc_exchange.call().getOrder(order_id)
    commitment = otc_exchange.call().commitmentOf(issuer, share_token.address)

    assert orderbook == [
        issuer, trader, to_checksum_address(share_token.address), _amount, _price,
        agent, False
    ]
    assert share_token.call().balanceOf(issuer) == deploy_args[5] - _amount
    assert commitment == _amount


# エラー系1
# 入力値の型誤り（_counterpart）
def test_createorder_error_1(web3, chain, users, otc_exchange, personal_info):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _price = 123
    _amount = 100

    with pytest.raises(TypeError):
        otc_exchange.transact().createOrder('1234', share_token.address, _amount, _price, agent)

    with pytest.raises(TypeError):
        otc_exchange.transact().createOrder(1234, share_token.address, _amount, _price, agent)


# エラー系2
# 入力値の型誤り（_token）
def test_createorder_error_2(web3, users, otc_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規注文
    web3.eth.defaultAccount = issuer
    _price = 123
    _amount = 100

    with pytest.raises(TypeError):
        otc_exchange.transact().createOrder(trader, '1234', _amount, _price, agent)

    with pytest.raises(TypeError):
        otc_exchange.transact().createOrder(trader, 1234, _amount, _price, agent)


# エラー系3
# 入力値の型誤り（_amount）
def test_createorder_error_3(web3, chain, users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _price = 123

    with pytest.raises(TypeError):
        otc_exchange.transact().createOrder(
            trader, share_token.address, -1, _price, agent)

    with pytest.raises(TypeError):
        otc_exchange.transact().createOrder(
            trader, share_token.address, 2 ** 256, _price, agent)

    with pytest.raises(TypeError):
        otc_exchange.transact().createOrder(
            trader, share_token.address, '0', _price, agent)

    with pytest.raises(TypeError):
        otc_exchange.transact().createOrder(
            trader, share_token.address, 0.1, _price, agent)


# エラー系4
# 入力値の型誤り（_price）
def test_createorder_error_4(web3, chain, users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _amount = 100

    with pytest.raises(TypeError):
        otc_exchange.transact().createOrder(
            trader, share_token.address, _amount, -1, agent)

    with pytest.raises(TypeError):
        otc_exchange.transact().createOrder(
            trader, share_token.address, _amount, 2 ** 256, agent)

    with pytest.raises(TypeError):
        otc_exchange.transact().createOrder(
            trader, share_token.address, _amount, '0', agent)

    with pytest.raises(TypeError):
        otc_exchange.transact().createOrder(
            trader, share_token.address, _amount, 0.1, agent)


# エラー系5
# 入力値の型誤り（_agent）
def test_createorder_error_5(web3, chain, users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _price = 123
    _amount = 100

    with pytest.raises(TypeError):
        otc_exchange.transact().createOrder(
            trader, share_token.address, _amount, _price, '1234')

    with pytest.raises(TypeError):
        otc_exchange.transact().createOrder(
            trader, share_token.address, _amount, _price, 1234)


# エラー系6
# 売注文数量が0の場合
def test_createorder_error_6(web3, chain, users, otc_exchange, personal_info):
    issuer = users['issuer']
    agent = users['agent']
    trader = users['trader']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)

    # 新規発行
    web3.eth.defaultAccount = issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _amount = 0
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(trader, share_token.address, _amount, _price, agent)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = otc_exchange.call().commitmentOf(issuer, share_token.address)
    balance = share_token.call().balanceOf(issuer)

    assert balance == deploy_args[5]
    assert commitment == 0


# エラー系7
# 名簿用個人情報が登録されていない場合
def test_createorder_error_7(web3, chain, users, otc_exchange, personal_info):
    issuer = users['issuer']
    agent = users['agent']
    trader = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(trader, share_token.address, _amount, _price, agent)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = otc_exchange.call().commitmentOf(issuer, share_token.address)
    balance = share_token.call().balanceOf(issuer)

    assert balance == deploy_args[5]
    assert commitment == 0


# エラー系8
# 残高不足
def test_createorder_error_8(web3, chain, users, otc_exchange, personal_info):
    issuer = users['issuer']
    agent = users['agent']
    trader = users['trader']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)

    # 新規発行
    web3.eth.defaultAccount = issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(trader, share_token.address, _amount + 1, _price, agent)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = otc_exchange.call().commitmentOf(issuer, share_token.address)
    balance = share_token.call().balanceOf(issuer)

    assert balance == deploy_args[5]
    assert commitment == 0


# エラー系9
# 無効な収納代行業者（Agent）の指定
def test_createorder_error_9(web3, chain, users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    attacker = users['admin']

    # 新規発行
    web3.eth.defaultAccount = issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(trader, share_token.address, _amount, _price, attacker)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = otc_exchange.call().commitmentOf(issuer, share_token.address)
    balance = share_token.call().balanceOf(issuer)

    assert balance == deploy_args[5]
    assert commitment == 0


# エラー系10
# 取扱ステータスがFalseの場合
def test_createorder_error_10(web3, chain, users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)

    # 新規発行
    web3.eth.defaultAccount = issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # ステータス変更
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(share_token.transact().setStatus(False))

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(trader, share_token.address, _amount, _price, agent)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = otc_exchange.call().commitmentOf(issuer, share_token.address)
    balance = share_token.call().balanceOf(issuer)
    assert balance == deploy_args[5]
    assert commitment == 0


'''
TEST_getOrder
'''


# エラー系1
# 入力値の型誤り（orderId）
def test_getOrder_error_1(web3, users, otc_exchange):
    issuer = users['issuer']

    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        otc_exchange.transact().getOrder("1")
    with pytest.raises(TypeError):
        otc_exchange.transact().getOrder(1.0)
    with pytest.raises(TypeError):
        otc_exchange.transact().getOrder(-1)
    with pytest.raises(TypeError):
        otc_exchange.transact().getOrder(2 ** 256)


'''
TEST_注文キャンセル（cancelOrder）
'''


# 正常系1
# ＜発行体＞新規発行 -> ＜投資家（発行体）＞新規注文
#  -> ＜投資家（発行体）＞注文キャンセル
def test_cancelOrder_normal_1(web3, chain, users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)

    # 新規発行
    web3.eth.defaultAccount = issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(trader, share_token.address, _amount, _price, agent)
    chain.wait.for_receipt(txn_hash)

    # 注文キャンセル
    web3.eth.defaultAccount = issuer
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().cancelOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    orderbook = otc_exchange.call().getOrder(order_id)
    commitment = otc_exchange.call().commitmentOf(issuer, share_token.address)

    assert orderbook == [
        issuer, trader, to_checksum_address(share_token.address), _amount, _price, agent, True
    ]
    assert share_token.call().balanceOf(issuer) == deploy_args[5]
    assert commitment == 0


# エラー系1
# 入力値の型誤り（_orderId）
def test_cancelOrder_error_1(web3, users, otc_exchange):
    issuer = users['issuer']

    # 注文キャンセル
    web3.eth.defaultAccount = issuer

    with pytest.raises(TypeError):
        otc_exchange.transact().cancelOrder(-1)

    with pytest.raises(TypeError):
        otc_exchange.transact().cancelOrder(2 ** 256)

    with pytest.raises(TypeError):
        otc_exchange.transact().cancelOrder('0')

    with pytest.raises(TypeError):
        otc_exchange.transact().cancelOrder(0.1)


# エラー系2
# 指定した注文IDが直近の注文IDを超えている場合
def test_cancelOrder_error_2(web3, chain, users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)

    # 新規発行
    web3.eth.defaultAccount = issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(trader, share_token.address, _amount, _price, agent)
    chain.wait.for_receipt(txn_hash)

    # 注文キャンセル
    web3.eth.defaultAccount = issuer
    order_id = otc_exchange.call().latestOrderId() + 1
    commitment = otc_exchange.call().commitmentOf(issuer, share_token.address)

    try:
        txn_hash = otc_exchange.transact().cancelOrder(order_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(order_id - 1)
    assert orderbook == [
        issuer, trader, to_checksum_address(share_token.address), _amount, _price, agent, False
    ]
    # キャンセルがエラーとなっているため、注文中の状態

    assert share_token.call().balanceOf(issuer) == deploy_args[5] - _amount
    assert commitment == 100


# エラー系3
# 注文がキャンセル済みの場合
def test_cancelOrder_error_3(web3, chain, users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)

    # 新規発行
    web3.eth.defaultAccount = issuer
    share_token, deploy_args = utils.\
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(trader, share_token.address, _amount, _price, agent)
    chain.wait.for_receipt(txn_hash)

    # 注文キャンセル
    web3.eth.defaultAccount = issuer
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().cancelOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    # 注文キャンセル（2回目）
    web3.eth.defaultAccount = issuer
    try:
        txn_hash = otc_exchange.transact().cancelOrder(order_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(order_id)
    commitment = otc_exchange.call().commitmentOf(issuer, share_token.address)

    assert orderbook == [
        issuer, trader, to_checksum_address(share_token.address), _amount, _price, agent, True
    ]
    assert share_token.call().balanceOf(issuer) == deploy_args[5]
    assert commitment == 0


# エラー系4
# 元注文の発注者と、注文キャンセルの実施者が異なる場合
def test_cancelOrder_error_4(web3, chain, users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    other = users['admin']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)

    # 新規発行
    web3.eth.defaultAccount = issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(trader, share_token.address, _amount, _price, agent)
    chain.wait.for_receipt(txn_hash)

    # 注文キャンセル
    web3.eth.defaultAccount = other
    order_id = otc_exchange.call().latestOrderId()
    try:
        txn_hash = otc_exchange.transact().cancelOrder(order_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    # assert
    web3.eth.defaultAccount = issuer
    orderbook = otc_exchange.call().getOrder(order_id)
    balance = share_token.call().balanceOf(issuer)
    commitment = otc_exchange.call().commitmentOf(issuer, share_token.address)

    assert orderbook == [
        issuer, trader, to_checksum_address(share_token.address), _amount, _price, agent, False
    ]
    assert balance == deploy_args[5] - _amount
    assert commitment == _amount


# エラー系5
# トークンのstatusが取扱不可となっている場合
def test_cancelOrder_error_5(web3, chain, users, otc_exchange, personal_info):
    issuer = users['issuer']
    trader = users['trader']
    other = users['admin']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)

    # 新規発行
    web3.eth.defaultAccount = issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(trader, share_token.address, _amount, _price, agent)
    chain.wait.for_receipt(txn_hash)

    # トークンの取扱不可
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(share_token.transact().setStatus(False))

    # 注文キャンセル
    web3.eth.defaultAccount = other
    order_id = otc_exchange.call().latestOrderId()
    try:
        txn_hash = otc_exchange.transact().cancelOrder(order_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    # assert
    web3.eth.defaultAccount = issuer
    orderbook = otc_exchange.call().getOrder(order_id)
    balance = share_token.call().balanceOf(issuer)
    commitment = otc_exchange.call().commitmentOf(issuer, share_token.address)

    assert orderbook == [
        issuer, trader, to_checksum_address(share_token.address), _amount, _price, agent, False
    ]
    assert balance == deploy_args[5] - _amount
    assert commitment == _amount


'''
TEST_Take注文（executeOrder）
'''


# 正常系1
# ＜発行体＞新規発行 -> ＜発行体＞新規注文 -> ＜投資家＞Take注文
def test_executeOrder_normal_1(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # make
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # take
    web3.eth.defaultAccount = _trader
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().executeOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    agreement_id = otc_exchange.call().latestAgreementId(order_id)

    orderbook = otc_exchange.call().getOrder(order_id)
    agree = otc_exchange.call().getAgreement(order_id, agreement_id)

    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]

    assert agree[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[5] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系1
# 入力値の型誤り（_orderId）
def test_executeOrder_error_1(web3, users, otc_exchange):
    _trader = users['trader']

    web3.eth.defaultAccount = _trader

    with pytest.raises(TypeError):
        otc_exchange.transact().executeOrder(-1)

    with pytest.raises(TypeError):
        otc_exchange.transact().executeOrder(2 ** 256)

    with pytest.raises(TypeError):
        otc_exchange.transact().executeOrder('0')

    with pytest.raises(TypeError):
        otc_exchange.transact().executeOrder(0.1)


# エラー系2
# 指定した注文IDが直近の注文IDを超えている場合
def test_executeOrder_error_2(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # make
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    latest_order_id_error = otc_exchange.call().latestOrderId() + 1
    latest_order_id = otc_exchange.call().latestOrderId()

    # Take注文
    web3.eth.defaultAccount = _trader
    order_id = latest_order_id_error
    _amount = 123
    try:
        txn_hash = otc_exchange.transact().executeOrder(order_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(latest_order_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, _agent, False
    ]

    assert balance_maker == deploy_args[5] - _amount_make
    assert commitment == _amount_make

    assert balance_taker == 0


# エラー系3
# 元注文の発注者と同一のアドレスからの発注の場合
# Take買注文
def test_executeOrder_error_3(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文：発行体
    web3.eth.defaultAccount = _issuer
    order_id = otc_exchange.call().latestOrderId()
    try:
        txn_hash = otc_exchange.transact().executeOrder(order_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(order_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, _agent, False
    ]

    assert balance_maker == deploy_args[5] - _amount_make
    assert commitment == _amount_make


# エラー系4
# 元注文がキャンセル済の場合
# Take買注文
def test_executeOrder_error_4(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().createOrder(
        _trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = otc_exchange.call().latestOrderId()

    # Make注文取消：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = otc_exchange.transact().cancelOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    try:
        txn_hash = otc_exchange.transact().executeOrder(order_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(order_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, _agent, True  # 取消済み状態
    ]
    assert balance_maker == deploy_args[5]
    assert balance_taker == 0
    assert commitment == 0


# エラー系5
# 名簿用個人情報が登録されていない場合
# Take買注文
def test_executeOrder_error_5(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = otc_exchange.call().latestOrderId()

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    try:
        txn_hash = otc_exchange.transact().executeOrder(order_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(order_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, _agent, False
    ]
    assert balance_maker == deploy_args[5] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系6
# 取扱ステータスがFalseの場合
def test_executeOrder_error_6(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    chain.wait.for_receipt(share_token.transact().transfer(otc_exchange.address, _amount_make))

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    chain.wait.for_receipt(
        otc_exchange.transact().createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    )

    order_id = otc_exchange.call().latestOrderId()

    # ステータス変更：発行体
    web3.eth.defaultAccount = _issuer
    chain.wait.for_receipt(share_token.transact().setStatus(False))

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    try:
        txn_hash = otc_exchange.transact().executeOrder(order_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(order_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, _agent, False
    ]
    assert balance_maker == deploy_args[5] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系7
# 第三者からtake注文があった場合
def test_executeOrder_error_7(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _attacker = users['admin']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    chain.wait.for_receipt(share_token.transact().transfer(otc_exchange.address, _amount_make))

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    chain.wait.for_receipt(
        otc_exchange.transact().createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    )

    order_id = otc_exchange.call().latestOrderId()

    # ステータス変更：発行体
    web3.eth.defaultAccount = _issuer
    chain.wait.for_receipt(share_token.transact().setStatus(False))

    # Take注文：第三者
    web3.eth.defaultAccount = _attacker
    try:
        txn_hash = otc_exchange.transact().executeOrder(order_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    web3.eth.defaultAccount = _issuer
    orderbook = otc_exchange.call().getOrder(order_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    balance_attacker = share_token.call().balanceOf(_attacker)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, _agent, False
    ]
    assert balance_maker == deploy_args[5] - _amount_make
    assert balance_taker == 0
    assert balance_attacker == 0
    assert commitment == _amount_make


'''
TEST_決済承認（confirmAgreement）
'''


# 正常系1
# ＜発行体＞新規発行 -> ＜発行体＞Make注文
#  -> ＜投資家＞Take注文 -> ＜決済業者＞決済処理
def test_confirmAgreement_normal_1(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().executeOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    agreement_id = otc_exchange.call().latestAgreementId(order_id)

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = otc_exchange.transact().confirmAgreement(order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    orderbook = otc_exchange.call().getOrder(order_id)
    agreement = otc_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]

    assert agreement[0:5] == [_trader, _amount_make, _price, False, True]
    assert balance_maker == deploy_args[5] - _amount_make
    assert balance_taker == _amount_make
    assert commitment == 0


# エラー系1
# 入力値の型誤り（_orderId）
def test_confirmAgreement_error_1(web3, users, otc_exchange):
    _agent = users['agent']

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent

    with pytest.raises(TypeError):
        otc_exchange.transact().confirmAgreement(-1, 0)

    with pytest.raises(TypeError):
        otc_exchange.transact().confirmAgreement(2 ** 256, 0)

    with pytest.raises(TypeError):
        otc_exchange.transact().confirmAgreement('0', 0)

    with pytest.raises(TypeError):
        otc_exchange.transact().confirmAgreement(0.1, 0)


# エラー系2
# 入力値の型誤り（_agreementId）
def test_confirmAgreement_error_2(web3, users, otc_exchange):
    _agent = users['agent']

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent

    with pytest.raises(TypeError):
        otc_exchange.transact().confirmAgreement(0, -1)

    with pytest.raises(TypeError):
        otc_exchange.transact().confirmAgreement(0, 2 ** 256)

    with pytest.raises(TypeError):
        otc_exchange.transact().confirmAgreement(0, '0')

    with pytest.raises(TypeError):
        otc_exchange.transact().confirmAgreement(0, 0.1)


# エラー系3
# 指定した注文番号が、直近の注文ID以上の場合
def test_confirmAgreement_error_3(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().executeOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    agreement_id = otc_exchange.call().latestAgreementId(order_id)

    # 決済承認：決済業者
    order_id_error = otc_exchange.call().latestOrderId() + 1
    web3.eth.defaultAccount = _agent
    try:
        txn_hash = otc_exchange.transact().confirmAgreement(order_id_error, agreement_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(order_id)
    agreement = otc_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]

    assert agreement[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[5] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系4
# 指定した約定IDが、直近の約定ID以上の場合
def test_confirmAgreement_error_4(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().executeOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    agreement_id = otc_exchange.call().latestAgreementId(order_id)

    # 決済承認：決済業者
    agreement_id_error = otc_exchange.call().latestAgreementId(order_id) + 1
    web3.eth.defaultAccount = _agent
    try:
        txn_hash = otc_exchange.transact().confirmAgreement(order_id, agreement_id_error)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(order_id)
    agreement = otc_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]

    assert agreement[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[5] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系5
# 指定した約定明細がすでに支払い済みの状態の場合
def test_confirmAgreement_error_5(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().executeOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    agreement_id = otc_exchange.call().latestAgreementId(order_id)

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = otc_exchange.transact().confirmAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    # 決済承認：決済業者（2回目）
    web3.eth.defaultAccount = _agent
    try:
        txn_hash = otc_exchange.transact().confirmAgreement(order_id, agreement_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(order_id)
    agreement = otc_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, False, True]
    assert balance_maker == deploy_args[5] - _amount_make
    assert balance_taker == _amount_make
    assert commitment == 0


# エラー系6
# 元注文で指定した決済業者ではない場合
def test_confirmAgreement_error_6(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().executeOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    agreement_id = otc_exchange.call().latestAgreementId(order_id)

    # 決済承認：投資家（指定した決済業者ではない）
    web3.eth.defaultAccount = _trader
    try:
        txn_hash = otc_exchange.transact().confirmAgreement(order_id, agreement_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(order_id)
    agreement = otc_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]

    assert agreement[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[5] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系7
# 既に決済非承認済み（キャンセル済み）の場合
def test_confirmAgreement_error_7(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().executeOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    agreement_id = otc_exchange.call().latestAgreementId(order_id)

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = otc_exchange.transact().cancelAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent
    try:
        txn_hash = otc_exchange.transact().confirmAgreement(order_id, agreement_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(order_id)
    agreement = otc_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, True, False]
    assert balance_maker == deploy_args[5]
    assert balance_taker == 0
    assert commitment == 0


# エラー系8
# トークンの取扱ステータスがFalse（不可）の場合
def test_confirmAgreement_error_8(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().executeOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    agreement_id = otc_exchange.call().latestAgreementId(order_id)

    # トークンの取扱不可
    web3.eth.defaultAccount = _issuer
    chain.wait.for_receipt(share_token.transact().setStatus(False))

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent
    try:
        txn_hash = otc_exchange.transact().confirmAgreement(order_id, agreement_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(order_id)
    agreement = otc_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[5] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


'''
TEST_getAgreement
'''


# 異常系1
# 入力値の型誤り（orderId, agreementId）
def test_getAgreement_error_1(web3, users, otc_exchange):
    issuer = users['issuer']

    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        otc_exchange.transact().getAgreement("1", 1)
    with pytest.raises(TypeError):
        otc_exchange.transact().getAgreement(1.0, 1)
    with pytest.raises(TypeError):
        otc_exchange.transact().getAgreement(-1, 1)
    with pytest.raises(TypeError):
        otc_exchange.transact().getAgreement(2 ** 256, 1)
    with pytest.raises(TypeError):
        otc_exchange.transact().getAgreement(1, "1")
    with pytest.raises(TypeError):
        otc_exchange.transact().getAgreement(1, 1.0)
    with pytest.raises(TypeError):
        otc_exchange.transact().getAgreement(1, -1)
    with pytest.raises(TypeError):
        otc_exchange.transact().getAgreement(1, 2 ** 256)


'''
TEST_決済非承認（cancelAgreement）
'''


# 正常系1
# Make売、Take買
# ＜発行体＞新規発行 -> ＜発行体＞Make注文
#  -> ＜投資家＞Take注文-> ＜決済業者＞決済非承認
def test_cancelAgreement_normal_1(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().executeOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    agreement_id = otc_exchange.call().latestAgreementId(order_id)

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = otc_exchange.transact().cancelAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    orderbook = otc_exchange.call().getOrder(order_id)
    agreement = otc_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, True, False]
    assert balance_maker == deploy_args[5]
    assert balance_taker == 0
    assert commitment == 0


# エラー系1
# 入力値の型誤り（_orderId）
def test_cancelAgreement_error_1(web3, users, otc_exchange):
    _agent = users['agent']

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent

    with pytest.raises(TypeError):
        otc_exchange.transact().cancelAgreement(-1, 0)

    with pytest.raises(TypeError):
        otc_exchange.transact().cancelAgreement(2 ** 256, 0)

    with pytest.raises(TypeError):
        otc_exchange.transact().cancelAgreement('0', 0)

    with pytest.raises(TypeError):
        otc_exchange.transact().cancelAgreement(0.1, 0)


# エラー系2
# 入力値の型誤り（_agreementId）
def test_cancelAgreement_error_2(web3, users, otc_exchange):
    _agent = users['agent']

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent

    with pytest.raises(TypeError):
        otc_exchange.transact().cancelAgreement(0, -1)

    with pytest.raises(TypeError):
        otc_exchange.transact().cancelAgreement(0, 2 ** 256)

    with pytest.raises(TypeError):
        otc_exchange.transact().cancelAgreement(0, '0')

    with pytest.raises(TypeError):
        otc_exchange.transact().cancelAgreement(0, 0.1)


# エラー系3
# 指定した注文番号が、直近の注文ID以上の場合
def test_cancelAgreement_error_3(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().executeOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    agreement_id = otc_exchange.call().latestAgreementId(order_id)

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    order_id_error = otc_exchange.call().latestOrderId() + 1
    try:
        txn_hash = otc_exchange.transact().cancelAgreement(order_id_error, agreement_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(order_id)
    agreement = otc_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[5] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系4
# 指定した約定IDが、直近の約定ID以上の場合
def test_cancelAgreement_error_4(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().executeOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    agreement_id = otc_exchange.call().latestAgreementId(order_id)

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    agreement_id_error = otc_exchange.call().latestAgreementId(order_id) + 1
    try:
        txn_hash = otc_exchange.transact().cancelAgreement(order_id, agreement_id_error)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(order_id)
    agreement = otc_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[5] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系5
# すでに決済承認済み（支払済み）の場合
def test_cancelAgreement_error_5(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().executeOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    agreement_id = otc_exchange.call().latestAgreementId(order_id)

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = otc_exchange.transact().confirmAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    try:
        txn_hash = otc_exchange.transact().cancelAgreement(order_id, agreement_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(order_id)
    agreement = otc_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, False, True]
    assert balance_maker == deploy_args[5] - _amount_make
    assert balance_taker == _amount_make
    assert commitment == 0


# エラー系6
# msg.senderが、決済代行（agent）以外の場合
def test_cancelAgreement_error_6(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().executeOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    agreement_id = otc_exchange.call().latestAgreementId(order_id)

    # 決済非承認：投資家（決済業者以外）
    web3.eth.defaultAccount = _trader
    try:
        txn_hash = otc_exchange.transact().cancelAgreement(order_id, agreement_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(order_id)
    agreement = otc_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[5] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系7
# すでに決済非承認済み（キャンセル済み）の場合
def test_cancelAgreement_error_7(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().createOrder(
        _trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().executeOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    agreement_id = otc_exchange.call().latestAgreementId(order_id)

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = otc_exchange.transact().cancelAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    # 決済非承認：決済業者（2回目）
    web3.eth.defaultAccount = _agent
    try:
        txn_hash = otc_exchange.transact().cancelAgreement(order_id, agreement_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(order_id)
    agreement = otc_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, True, False]
    assert balance_maker == deploy_args[5]
    assert balance_taker == 0
    assert commitment == 0


# エラー系8
# トークンが取扱不可の場合
def test_cancelAgreement_error_8(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().executeOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    agreement_id = otc_exchange.call().latestAgreementId(order_id)

    # トークンの取扱不可
    web3.eth.defaultAccount = _issuer
    chain.wait.for_receipt(share_token.transact().setStatus(False))

    # 決済非承認
    web3.eth.defaultAccount = _agent
    try:
        txn_hash = otc_exchange.transact().cancelAgreement(order_id, agreement_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = otc_exchange.call().getOrder(order_id)
    agreement = otc_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = share_token.call().balanceOf(_issuer)
    balance_taker = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert orderbook == [
        _issuer, _trader, to_checksum_address(share_token.address),
        0, _price, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_make, _price, False, False]
    assert balance_maker == deploy_args[5] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


'''
TEST_引き出し（withdrawAll）
'''


# 正常系1
# ＜発行体＞新規発行 -> ＜発行体＞デポジット -> ＜発行体＞引き出し
def test_withdrawAll_normal_1(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # 引き出し：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = otc_exchange.transact().withdrawAll(share_token.address)
    chain.wait.for_receipt(txn_hash)

    balance_exchange = otc_exchange.call().balanceOf(_issuer, share_token.address)
    balance_token = share_token.call().balanceOf(_issuer)

    assert balance_exchange == 0
    assert balance_token == deploy_args[5]


# 正常系2
# ＜発行体＞新規発行 -> ＜発行体＞デポジット（2回） -> ＜発行体＞引き出し
def test_withdrawAll_normal_2(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Exchangeへのデポジット（2回目）：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # 引き出し：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = otc_exchange.transact().withdrawAll(share_token.address)
    chain.wait.for_receipt(txn_hash)

    balance_exchange = otc_exchange.call().balanceOf(_issuer, share_token.address)
    balance_token = share_token.call().balanceOf(_issuer)

    assert balance_exchange == 0
    assert balance_token == deploy_args[5]


# 正常系3
# ＜発行体＞新規発行 -> ＜発行体＞Make注文 ※売注文中状態
#  -> ＜発行体＞引き出し
def test_withdrawAll_normal_3(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_transfer = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_transfer)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 70  # 100のうち70だけ売注文
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # 引き出し：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = otc_exchange.transact().withdrawAll(share_token.address)
    chain.wait.for_receipt(txn_hash)

    balance_exchange = otc_exchange.call().balanceOf(_issuer, share_token.address)
    balance_token = share_token.call().balanceOf(_issuer)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert balance_exchange == 0
    assert balance_token == deploy_args[5] - _amount_make
    assert commitment == _amount_make


# 正常系4
# ＜発行体＞新規発行 -> ＜発行体＞Make注文 -> ＜投資家＞Take注文
#  -> ＜発行体＞引き出し
def test_withdrawAll_normal_4(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_transfer = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_transfer)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 70  # 100のうち70だけ売注文
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().executeOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    # 引き出し：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = otc_exchange.transact().withdrawAll(share_token.address)
    chain.wait.for_receipt(txn_hash)

    balance_exchange = otc_exchange.call().balanceOf(_issuer, share_token.address)
    balance_issuer = share_token.call().balanceOf(_issuer)
    balance_trader = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    # 約定済みのトークンはそのまま。
    assert balance_exchange == 0
    assert balance_issuer == deploy_args[5] - _amount_make
    assert balance_trader == 0
    assert commitment == _amount_make


# 正常系5
# ＜発行体＞新規発行 -> ＜発行体＞Make注文 -> ＜投資家＞Take注文
#  -> ＜決済業者＞決済承認 -> ＜発行体＞引き出し
def test_withdrawAll_normal_5(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    personalinfo_register(web3, chain, personal_info, _trader, _issuer)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_transfer = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_transfer)
    chain.wait.for_receipt(txn_hash)

    # Make注文：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 70  # 100のうち70だけ売注文
    _price = 123
    txn_hash = otc_exchange.transact().\
        createOrder(_trader, share_token.address, _amount_make, _price, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文：投資家
    web3.eth.defaultAccount = _trader
    order_id = otc_exchange.call().latestOrderId()
    txn_hash = otc_exchange.transact().executeOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    agreement_id = otc_exchange.call().latestAgreementId(order_id)

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = otc_exchange.transact().confirmAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    # 引き出し：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = otc_exchange.transact().withdrawAll(share_token.address)
    chain.wait.for_receipt(txn_hash)

    balance_issuer_exchange = otc_exchange.call().balanceOf(_issuer, share_token.address)
    balance_issuer_token = share_token.call().balanceOf(_issuer)
    balance_trader_exchange = otc_exchange.call().balanceOf(_trader, share_token.address)
    balance_trader_token = share_token.call().balanceOf(_trader)
    commitment = otc_exchange.call().commitmentOf(_issuer, share_token.address)

    assert balance_issuer_exchange == 0
    assert balance_issuer_token == deploy_args[5] - _amount_make
    assert balance_trader_exchange == 0
    assert balance_trader_token == _amount_make
    assert commitment == 0


# エラー系１
# 入力値の型誤り（_token）
def test_withdrawAll_error_1(web3, users, otc_exchange):
    _issuer = users['issuer']

    # 引き出し：発行体
    web3.eth.defaultAccount = _issuer

    with pytest.raises(TypeError):
        otc_exchange.transact().withdrawAll(1234)

    with pytest.raises(TypeError):
        otc_exchange.transact().withdrawAll('1234')


# エラー系2-1
# 残高がゼロの場合
# ＜発行体＞新規発行 -> ＜発行体＞デポジット -> ＜発行体＞引き出し（2回）
def test_withdrawAll_error_2_1(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # 引き出し：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = otc_exchange.transact().withdrawAll(share_token.address)
    chain.wait.for_receipt(txn_hash)

    # 引き出し（2回目)：発行体
    web3.eth.defaultAccount = _issuer
    try:
        txn_hash = otc_exchange.transact().withdrawAll(share_token.address)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    balance_exchange = otc_exchange.call().balanceOf(_issuer, share_token.address)
    balance_token = share_token.call().balanceOf(_issuer)

    assert balance_exchange == 0
    assert balance_token == deploy_args[5]


# エラー系2-2
# 残高がゼロの場合
# ＜発行体＞新規発行 -> ＜発行体＞デポジット -> 異なるアドレスからの引き出し
def test_withdrawAll_error_2_2(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_transfer = 100
    txn_hash = share_token.transact().transfer(
        otc_exchange.address, _amount_transfer)
    chain.wait.for_receipt(txn_hash)

    # 引き出し：異なるアドレス
    web3.eth.defaultAccount = _trader
    try:
        txn_hash = otc_exchange.transact().withdrawAll(share_token.address)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    balance_exchange = otc_exchange.call().balanceOf(_issuer, share_token.address)
    balance_token = share_token.call().balanceOf(_issuer)

    assert balance_exchange == _amount_transfer
    assert balance_token == deploy_args[5] - _amount_transfer


# エラー系3
# トークンの取扱が不可の場合
# ＜発行体＞新規発行 -> ＜発行体＞取扱不可設定 -> 引き出し
def test_withdrawAll_error_3(web3, chain, users, otc_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_transfer = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, _amount_transfer)
    chain.wait.for_receipt(txn_hash)

    # トークンの取扱不可設定
    web3.eth.defaultAccount = _issuer
    chain.wait.for_receipt(share_token.transact().setStatus(False))

    # 引き出し
    web3.eth.defaultAccount = _issuer
    try:
        txn_hash = otc_exchange.transact().withdrawAll(share_token.address)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    balance_exchange = otc_exchange.call().balanceOf(_issuer, share_token.address)
    balance_token = share_token.call().balanceOf(_issuer)

    assert balance_exchange == _amount_transfer
    assert balance_token == deploy_args[5] - _amount_transfer


'''
TEST_Exchange切替
'''


# 正常系
def test_updateExchange_normal_1(web3, chain, users,
                                 otc_exchange, otc_exchange_storage,
                                 personal_info, payment_gateway):
    issuer = users['issuer']
    agent = users['agent']
    trader = users['trader']
    admin = users['admin']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)

    # 新規発行
    web3.eth.defaultAccount = issuer
    share_token, deploy_args = utils. \
        issue_share_token(web3, chain, users, otc_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    deposit_amount = 100
    txn_hash = share_token.transact().transfer(otc_exchange.address, deposit_amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文
    web3.eth.defaultAccount = issuer
    amount_make = 10
    price = 123
    txn_hash = otc_exchange.transact(). \
        createOrder(trader, share_token.address, amount_make, price, agent)
    chain.wait.for_receipt(txn_hash)

    # Exchange（新）のデプロイ
    web3.eth.defaultAccount = admin
    otc_exchange_new, _ = chain.provider.get_or_deploy_contract(
        'IbetOTCExchange',
        deploy_args=[
            payment_gateway.address,
            personal_info.address,
            otc_exchange_storage.address
        ]
    )
    # ストレージの切り替え
    txn_hash = otc_exchange_storage.transact().upgradeVersion(otc_exchange_new.address)
    chain.wait.for_receipt(txn_hash)

    # Exchange（新）からの情報参照
    web3.eth.defaultAccount = issuer
    order_id = otc_exchange_new.call().latestOrderId()
    orderbook = otc_exchange_new.call().getOrder(order_id)
    commitment = otc_exchange_new.call().commitmentOf(issuer, share_token.address)
    balance_exchange = otc_exchange_new.call().balanceOf(issuer, share_token.address)
    balance_token = share_token.call().balanceOf(issuer)

    assert orderbook == [
        issuer, trader, to_checksum_address(share_token.address),
        amount_make, price, agent, False
    ]
    assert balance_token == deploy_args[5] - deposit_amount
    assert balance_exchange == deposit_amount - amount_make
    assert commitment == amount_make
