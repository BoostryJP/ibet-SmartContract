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


# PaymentGatewayアカウント認可
def payment_gateway_approve(web3, chain, payment_gateway, trader, agent):
    web3.eth.defaultAccount = agent
    txn_hash = payment_gateway.transact().approve(trader)
    chain.wait.for_receipt(txn_hash)


# Bondトークンを取引所にデポジット
def bond_transfer(web3, chain, bond_token, bond_exchange, trader, amount):
    web3.eth.defaultAccount = trader
    txn_hash = bond_token.transact().transfer(
        bond_exchange.address, amount)
    chain.wait.for_receipt(txn_hash)


'''
TEST_デプロイ
'''


# ＜正常系1＞
# Deploy　→　正常
def test_deploy_normal_1(users, bond_exchange, bond_exchange_storage,
                         personal_info, payment_gateway):
    owner = bond_exchange.call().owner()
    personal_info_address = bond_exchange.call().personalInfoAddress()
    payment_gateway_address = bond_exchange.call().paymentGatewayAddress()
    storage_address = bond_exchange.call().storageAddress()

    assert owner == users['admin']
    assert personal_info_address == to_checksum_address(personal_info.address)
    assert payment_gateway_address == to_checksum_address(payment_gateway.address)
    assert storage_address == to_checksum_address(bond_exchange_storage.address)


# ＜エラー系1＞
# 入力値の型誤り（PaymentGatewayアドレス）
def test_deploy_error_1(web3, users, chain, personal_info):
    exchange_owner = users['admin']
    web3.eth.defaultAccount = exchange_owner

    deploy_args = [
        1234,
        personal_info.address
    ]

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetStraightBondExchange',
            deploy_args=deploy_args
        )


# ＜エラー系2＞
# 入力値の型誤り（PersonalInfoアドレス）
def test_deploy_error_2(web3, users, chain, payment_gateway):
    exchange_owner = users['admin']
    web3.eth.defaultAccount = exchange_owner
    deploy_args = [
        payment_gateway.address,
        1234
    ]
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetStraightBondExchange', deploy_args=deploy_args)


'''
TEST_Make注文（createOrder）
'''


# 正常系１
# ＜発行体＞新規発行 -> ＜投資家＞新規注文（買）
def test_createorder_normal_1(web3, chain, users, bond_exchange, personal_info, payment_gateway):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文（買）
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    _isBuy = True
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId()
    orderbook = bond_exchange.call().getOrder(order_id)

    assert orderbook == [
        issuer, to_checksum_address(bond_token.address), _amount, _price,
        _isBuy, agent, False
    ]
    assert bond_token.call().balanceOf(issuer) == deploy_args[2]


# 正常系2
# ＜発行体＞新規発行 -> ＜発行体＞新規注文（売）
def test_createorder_normal_2(web3, chain, users,
                              bond_exchange, personal_info, payment_gateway):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文（売）
    web3.eth.defaultAccount = issuer
    _price = 123
    _isBuy = False
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId()
    orderbook = bond_exchange.call().getOrder(order_id)
    commitment = bond_exchange.call().commitmentOf(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert orderbook == [
        issuer, to_checksum_address(bond_token.address), _amount, _price,
        _isBuy, agent, False
    ]
    assert balance == deploy_args[2] - _amount
    assert commitment == _amount


# エラー系1
# 入力値の型誤り（_token）
def test_createorder_error_1(web3, users, bond_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規注文
    web3.eth.defaultAccount = issuer
    _price = 123
    _isBuy = False
    _amount = 100

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder('1234', _amount, _price, _isBuy, agent)

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(1234, _amount, _price, _isBuy, agent)


# エラー系2
# 入力値の型誤り（_amount）
def test_createorder_error_2(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _price = 123
    _isBuy = False

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, -1, _price, _isBuy, agent)

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, 2 ** 256, _price, _isBuy, agent)

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, '0', _price, _isBuy, agent)

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, 0.1, _price, _isBuy, agent)


# エラー系3
# 入力値の型誤り（_price）
def test_createorder_error_3(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _amount = 100
    _isBuy = False

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, _amount, -1, _isBuy, agent)

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, _amount, 2 ** 256, _isBuy, agent)

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, _amount, '0', _isBuy, agent)

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, _amount, 0.1, _isBuy, agent)


# エラー系4
# 入力値の型誤り（_isBuy）
def test_createorder_error_4(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, _amount, _price, 1234, agent)

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, _amount, _price, 'True', agent)


# エラー系5
# 入力値の型誤り（_agent）
def test_createorder_error_5(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _price = 123
    _isBuy = False
    _amount = 100

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, _amount, _price, _isBuy, '1234')

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, _amount, _price, _isBuy, 1234)


# エラー系6-1
# 買注文数量が0の場合
def test_createorder_error_6_1(web3, chain, users,
                               bond_exchange, personal_info, payment_gateway):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文（買）
    web3.eth.defaultAccount = issuer
    _amount = 0
    _price = 123
    _isBuy = True
    try:
        txn_hash = bond_exchange.transact().createOrder(bond_token.address, _amount, _price, _isBuy, agent)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    commitment = bond_exchange.call().commitmentOf(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系6-2
# 売注文数量が0の場合
def test_createorder_error_6_2(web3, chain, users,
                               bond_exchange, personal_info, payment_gateway):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文（売）
    web3.eth.defaultAccount = issuer
    _amount = 0
    _price = 123
    _isBuy = False
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = bond_exchange.call().commitmentOf(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系7-1
# 未認可のアカウントアドレスからの注文（買）
def test_createorder_error_7_1(web3, chain, users,
                               bond_exchange, personal_info, payment_gateway):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)  # 未認可状態

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文（買）
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    _isBuy = False
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = bond_exchange.call().commitmentOf(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系7-2
# 未認可のアカウントアドレスからの注文（買）
def test_createorder_error_7_2(web3, chain, users,
                               bond_exchange, personal_info):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)  # 未認可状態

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文（売）
    web3.eth.defaultAccount = issuer
    _amount = 0
    _price = 123
    _isBuy = False
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = bond_exchange.call().commitmentOf(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系8-1
# 名簿用個人情報が登録されていない場合（買注文）
def test_createorder_error_8_1(web3, chain, users,
                               bond_exchange, payment_gateway, personal_info):
    issuer = users['issuer']
    agent = users['agent']

    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文（買）
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    _isBuy = True
    try:
        txn_hash = bond_exchange.transact().createOrder(bond_token.address, _amount, _price, _isBuy, agent)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    commitment = bond_exchange.call().commitmentOf(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系8-2
# 名簿用個人情報が登録されていない場合（売注文）
def test_createorder_error_8_2(web3, chain, users,
                               bond_exchange, payment_gateway, personal_info):
    issuer = users['issuer']
    agent = users['agent']

    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文（売）
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    _isBuy = False
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = bond_exchange.call().commitmentOf(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系9-1
# 償還済みフラグがTrueの場合
# ＜発行体＞新規発行 -> ＜発行体＞償還設定 -> ＜発行体＞新規注文（買）
def test_createorder_error_9_1(web3, chain, users,
                               bond_exchange, personal_info, payment_gateway):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 償還設定
    web3.eth.defaultAccount = issuer
    txn_hash = bond_token.transact().redeem()
    chain.wait.for_receipt(txn_hash)

    # 新規注文（買）
    web3.eth.defaultAccount = issuer
    _price = 123
    _isBuy = False
    _amount = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = bond_exchange.call().commitmentOf(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系9-2
# 償還済みフラグがTrueの場合
# ＜発行体＞新規発行 -> ＜発行体＞償還設定 -> ＜発行体＞新規注文（売）
def test_createorder_error_9_2(web3, chain, users,
                               bond_exchange, personal_info, payment_gateway):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 償還設定
    web3.eth.defaultAccount = issuer
    txn_hash = bond_token.transact().redeem()
    chain.wait.for_receipt(txn_hash)

    # 新規注文（売）
    web3.eth.defaultAccount = issuer
    _price = 123
    _isBuy = False
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = bond_exchange.call().commitmentOf(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系10
# 残高不足
def test_createorder_error_10(web3, chain, users,
                              bond_exchange, personal_info, payment_gateway):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文（売）
    web3.eth.defaultAccount = issuer
    _price = 123
    _isBuy = False
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount + 1, _price, _isBuy, agent)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = bond_exchange.call().commitmentOf(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系11-1
# 無効な収納代行業者（Agent）の指定（買）
def test_createorder_error_11_1(web3, chain, users,
                                bond_exchange, personal_info, payment_gateway):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文（買）
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    _isBuy = True
    invalid_agent = users['trader']
    try:
        txn_hash = bond_exchange.transact().createOrder(bond_token.address, _amount, _price, _isBuy, invalid_agent)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    commitment = bond_exchange.call().commitmentOf(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


# エラー系11-2
# 無効な収納代行業者（Agent）の指定（売）
def test_createorder_error_11_2(web3, chain, users,
                                bond_exchange, payment_gateway, personal_info):
    issuer = users['issuer']
    agent = users['agent']

    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文（売）
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    _isBuy = False
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = bond_exchange.call().commitmentOf(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


'''
TEST_注文キャンセル（cancelOrder）
'''


# 正常系1
# ＜発行体＞新規発行 -> ＜投資家（発行体）＞新規注文（買）
#  -> ＜投資家（発行体）＞注文キャンセル
def test_cancelOrder_normal_1(web3, chain, users,
                              bond_exchange, personal_info, payment_gateway):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文（買）
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    _isBuy = True
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent)
    chain.wait.for_receipt(txn_hash)

    # 注文キャンセル
    web3.eth.defaultAccount = issuer
    order_id = bond_exchange.call().latestOrderId()
    txn_hash = bond_exchange.transact().cancelOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().getOrder(order_id)

    assert orderbook == [
        issuer, to_checksum_address(bond_token.address), _amount, _price,
        _isBuy, agent, True
    ]
    assert bond_token.call().balanceOf(issuer) == deploy_args[2]


# 正常系2
# ＜発行体＞新規発行 -> ＜投資家（発行体）＞新規注文（売）
#  -> ＜投資家（発行体）＞注文キャンセル
def test_cancelOrder_normal_2(web3, chain, users,
                              bond_exchange, personal_info, payment_gateway):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文（売）
    web3.eth.defaultAccount = issuer
    _price = 123
    _isBuy = False
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent)
    chain.wait.for_receipt(txn_hash)

    # 注文キャンセル
    web3.eth.defaultAccount = issuer
    order_id = bond_exchange.call().latestOrderId()
    txn_hash = bond_exchange.transact().cancelOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().getOrder(order_id)
    commitment = bond_exchange.call().commitmentOf(issuer, bond_token.address)

    assert orderbook == [
        issuer, to_checksum_address(bond_token.address), _amount, _price,
        _isBuy, agent, True
    ]
    assert bond_token.call().balanceOf(issuer) == deploy_args[2]
    assert commitment == 0


# エラー系1
# 入力値の型誤り（_orderId）
def test_cancelOrder_error_1(web3, users, bond_exchange):
    issuer = users['issuer']

    # 注文キャンセル
    web3.eth.defaultAccount = issuer

    with pytest.raises(TypeError):
        bond_exchange.transact().cancelOrder(-1)

    with pytest.raises(TypeError):
        bond_exchange.transact().cancelOrder(2 ** 256)

    with pytest.raises(TypeError):
        bond_exchange.transact().cancelOrder('0')

    with pytest.raises(TypeError):
        bond_exchange.transact().cancelOrder(0.1)


# エラー系2
# 指定した注文IDが直近の注文IDを超えている場合
def test_cancelOrder_error_2(web3, chain, users,
                             bond_exchange, personal_info, payment_gateway):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文（買）
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    _isBuy = True
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent)
    chain.wait.for_receipt(txn_hash)

    # 注文キャンセル
    web3.eth.defaultAccount = issuer
    order_id = bond_exchange.call().latestOrderId() + 1
    try:
        txn_hash = bond_exchange.transact().cancelOrder(order_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id - 1)
    assert orderbook == [
        issuer, to_checksum_address(bond_token.address), _amount, _price,
        _isBuy, agent, False
    ]
    assert bond_token.call().balanceOf(issuer) == deploy_args[2]


# エラー系3-1
# 注文がキャンセル済みの場合（買注文）
def test_cancelOrder_error_3_1(web3, chain, users,
                               bond_exchange, personal_info, payment_gateway):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文（買）
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    _isBuy = True
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent)
    chain.wait.for_receipt(txn_hash)

    # 注文キャンセル
    web3.eth.defaultAccount = issuer
    order_id = bond_exchange.call().latestOrderId()
    txn_hash = bond_exchange.transact().cancelOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    # 注文キャンセル（2回目）
    web3.eth.defaultAccount = issuer
    try:
        txn_hash = bond_exchange.transact().cancelOrder(order_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)

    assert orderbook == [
        issuer, to_checksum_address(bond_token.address), _amount, _price,
        _isBuy, agent, True
    ]
    assert bond_token.call().balanceOf(issuer) == deploy_args[2]


# エラー系3-2
# 注文がキャンセル済みの場合（売注文）
def test_cancelOrder_error_3_2(web3, chain, users,
                               bond_exchange, personal_info, payment_gateway):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文（売）
    web3.eth.defaultAccount = issuer
    _price = 123
    _isBuy = False
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent)
    chain.wait.for_receipt(txn_hash)

    # 注文キャンセル
    web3.eth.defaultAccount = issuer
    order_id = bond_exchange.call().latestOrderId()
    txn_hash = bond_exchange.transact().cancelOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    # 注文キャンセル（2回目）
    web3.eth.defaultAccount = issuer
    try:
        txn_hash = bond_exchange.transact().cancelOrder(order_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(bond_token.address), _amount, _price,
        _isBuy, agent, True
    ]
    assert bond_token.call().balanceOf(issuer) == deploy_args[2]


# エラー系4-1
# 元注文の発注者と、注文キャンセルの実施者が異なる場合（買注文）
def test_cancelOrder_error_4_1(web3, chain, users,
                               bond_exchange, personal_info, payment_gateway):
    issuer = users['issuer']
    other = users['trader']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文（買）
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    _isBuy = True
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent)
    chain.wait.for_receipt(txn_hash)

    # 注文キャンセル
    web3.eth.defaultAccount = other
    order_id = bond_exchange.call().latestOrderId()
    try:
        txn_hash = bond_exchange.transact().cancelOrder(order_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(bond_token.address), _amount, _price,
        _isBuy, agent, False
    ]
    assert bond_token.call().balanceOf(issuer) == deploy_args[2]


# エラー系4-2
# 元注文の発注者と、注文キャンセルの実施者が異なる場合（売注文）
def test_cancelOrder_error_4_2(web3, chain, users,
                               bond_exchange, personal_info, payment_gateway):
    issuer = users['issuer']
    other = users['trader']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    _amount = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount)
    chain.wait.for_receipt(txn_hash)

    # 新規注文（売）
    web3.eth.defaultAccount = issuer
    _price = 123
    _isBuy = False
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent)
    chain.wait.for_receipt(txn_hash)

    # 注文キャンセル
    web3.eth.defaultAccount = other
    order_id = bond_exchange.call().latestOrderId()
    try:
        txn_hash = bond_exchange.transact().cancelOrder(order_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    balance = bond_token.call().balanceOf(issuer)
    commitment = bond_exchange.call().commitmentOf(issuer, bond_token.address)

    assert orderbook == [
        issuer, to_checksum_address(bond_token.address), _amount, _price,
        _isBuy, agent, False
    ]
    assert balance == deploy_args[2] - _amount
    assert commitment == _amount


'''
TEST_Take注文（executeOrder）
'''


# 正常系1
# ＜発行体＞新規発行 -> ＜発行体＞新規注文（売） -> ＜投資家＞Take注文（買）
def test_executeOrder_normal_1(web3, chain, users,
                               bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # 新規注文（売）
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId()
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementId(order_id)

    orderbook = bond_exchange.call().getOrder(order_id)
    agree = bond_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, False, _agent, False
    ]

    assert agree[0:5] == [_trader, _amount_take, _price, False, False]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# 正常系2
# ＜発行体＞新規発行 -> ＜投資家＞新規注文（買） -> ＜発行体＞Take注文（売）
def test_executeOrder_normal_2(web3, chain, users,
                               bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId()

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_take = 50
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_take)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(order_id, _amount_take, False)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementId(order_id)

    orderbook = bond_exchange.call().getOrder(order_id)
    agree = bond_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, True, _agent, False
    ]

    assert agree[0:5] == [_issuer, _amount_take, _price, False, False]
    assert balance_maker == 0
    assert balance_taker == deploy_args[2] - _amount_take
    assert commitment == _amount_take


# エラー系1
# 入力値の型誤り（_orderId）
def test_executeOrder_error_1(web3, users, bond_exchange):
    _trader = users['trader']

    web3.eth.defaultAccount = _trader
    _amount = 50
    _is_buy = True

    with pytest.raises(TypeError):
        bond_exchange.transact().executeOrder(-1, _amount, _is_buy)

    with pytest.raises(TypeError):
        bond_exchange.transact().executeOrder(2 ** 256, _amount, _is_buy)

    with pytest.raises(TypeError):
        bond_exchange.transact().executeOrder('0', _amount, _is_buy)

    with pytest.raises(TypeError):
        bond_exchange.transact().executeOrder(0.1, _amount, _is_buy)


# エラー系2
# 入力値の型誤り（_amount）
def test_executeOrder_error_2(web3, users, bond_exchange):
    _trader = users['trader']

    web3.eth.defaultAccount = _trader
    _order_id = 1000
    _is_buy = True

    with pytest.raises(TypeError):
        bond_exchange.transact().executeOrder(_order_id, -1, _is_buy)

    with pytest.raises(TypeError):
        bond_exchange.transact().executeOrder(_order_id, 2 ** 256, _is_buy)

    with pytest.raises(TypeError):
        bond_exchange.transact().executeOrder(_order_id, '0', _is_buy)

    with pytest.raises(TypeError):
        bond_exchange.transact().executeOrder(_order_id, 0.1, _is_buy)


# エラー系3
# 入力値の型誤り（_isBuy）
def test_executeOrder_error_3(web3, users, bond_exchange):
    _trader = users['trader']

    web3.eth.defaultAccount = _trader
    _order_id = 1000
    _amount = 123

    with pytest.raises(TypeError):
        bond_exchange.transact().executeOrder(_order_id, _amount, 'True')

    with pytest.raises(TypeError):
        bond_exchange.transact().executeOrder(_order_id, _amount, 111)


# エラー系4
# 指定した注文IDが直近の注文IDを超えている場合
def test_executeOrder_error_4(web3, chain, users,
                              bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Make注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    latest_order_id_error = bond_exchange.call().latestOrderId() + 1
    latest_order_id = bond_exchange.call().latestOrderId()

    # Take注文（売）
    web3.eth.defaultAccount = _issuer
    order_id = latest_order_id_error
    _amount = 123
    try:
        txn_hash = bond_exchange.transact().executeOrder(order_id, _amount, False)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(latest_order_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, True, _agent, False
    ]

    assert balance_maker == 0
    assert balance_taker == deploy_args[2]


# エラー系5-1
# 注文数量が0の場合
# Take買注文
def test_executeOrder_error_5_1(web3, chain, users,
                                bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId()
    try:
        txn_hash = bond_exchange.transact().executeOrder(order_id, 0, True)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, False, _agent, False
    ]

    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系5-2
# 注文数量が0の場合
# Take売注文
def test_executeOrder_error_5_2(web3, chain, users,
                                bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_take = 50
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_take)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：発行体
    order_id = bond_exchange.call().latestOrderId()
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(order_id, 0, False)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().getOrder(order_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, True, _agent, False
    ]

    assert balance_maker == 0
    assert balance_taker == deploy_args[2]
    assert commitment == 0


# エラー系6-1
# 元注文と、発注する注文が同一の売買区分の場合
# Take買注文
def test_executeOrder_error_6_1(web3, chain, users,
                                bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：投資家
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId()
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, False)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().getOrder(order_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, False, _agent, False
    ]

    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系6-2
# 元注文と、発注する注文が同一の売買区分の場合
# Take売注文
def test_executeOrder_error_6_2(web3, chain, users,
                                bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：発行体
    order_id = bond_exchange.call().latestOrderId()
    web3.eth.defaultAccount = _issuer
    _amount_take = 50
    try:
        txn_hash = bond_exchange.transact().executeOrder(order_id, _amount_take, True)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, True, _agent, False
    ]

    assert balance_maker == 0
    assert balance_taker == deploy_args[2]
    assert commitment == 0


# エラー系7-1
# 元注文の発注者と同一のアドレスからの発注の場合
# Take買注文
def test_executeOrder_error_7_1(web3, chain, users,
                                bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：発行体
    web3.eth.defaultAccount = _issuer
    order_id = bond_exchange.call().latestOrderId()
    _amount_take = 50
    try:
        txn_hash = bond_exchange.transact().executeOrder(order_id, _amount_take, True)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, False, _agent, False
    ]

    assert balance_maker == deploy_args[2] - _amount_make
    assert commitment == _amount_make


# エラー系7-2
# 元注文の発注者と同一のアドレスからの発注の場合
# Take売注文
def test_executeOrder_error_7_2(web3, chain, users,
                                bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文（買）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_take = 50
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_take)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：発行体
    order_id = bond_exchange.call().latestOrderId()
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, False)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().getOrder(order_id)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, True, _agent, False
    ]
    assert commitment == 0
    assert balance_taker == deploy_args[2]


# エラー系8-1
# 元注文がキャンセル済の場合
# Take買注文
def test_executeOrder_error_8_1(web3, chain, users,
                                bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId()

    # Make注文取消：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().cancelOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _amount_take = 50
    try:
        txn_hash = bond_exchange.transact().executeOrder(order_id, _amount_take, True)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, False, _agent, True  # 取消済み状態
    ]
    assert balance_maker == deploy_args[2]
    assert balance_taker == 0
    assert commitment == 0


# エラー系8-2
# 元注文の発注者と同一のアドレスからの発注の場合
# Take売注文
def test_executeOrder_error_8_2(web3, chain, users,
                                bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Make注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId()

    # Make注文取消：投資家
    web3.eth.defaultAccount = _trader
    txn_hash = bond_exchange.transact().cancelOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_take = 50
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_take)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, False)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().getOrder(order_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, True, _agent, True  # 取り消し済み状態
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]


# エラー系9-1
# 認可されたアドレスではない場合
# Take買注文
def test_executeOrder_error_9_1(web3, chain, users,
                                bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)  # 未認可状態

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId()

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _amount_take = 50
    try:
        txn_hash = bond_exchange.transact().executeOrder(order_id, _amount_take, True)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, False, _agent, False
    ]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系9-2
# 認可されたアドレスではない場合
# Take売注文
def test_executeOrder_error_9_2(web3, chain, users,
                                bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)  # 未認可状態

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Make注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId()

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_take = 50
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_take)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, False)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().getOrder(order_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, True, _agent, False
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]


# エラー系10-1
# 名簿用個人情報が登録されていない場合
# Take買注文
def test_executeOrder_error_10_1(web3, chain, users,
                                 bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId()

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _amount_take = 50
    try:
        txn_hash = bond_exchange.transact().executeOrder(order_id, _amount_take, True)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, False, _agent, False
    ]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系10-2
# 名簿用個人情報が登録されていない場合
# Take売注文
def test_executeOrder_error_10_2(web3, chain, users,
                                 bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Make注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId()

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_take = 50
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_take)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, False)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().getOrder(order_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, True, _agent, False
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]


# エラー系11-1
# 償還済みフラグがTrueの場合
# Take買注文
def test_executeOrder_error_11_1(web3, chain, users,
                                 bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId()

    # 償還処理：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_token.transact().redeem()
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _amount_take = 50
    try:
        txn_hash = bond_exchange.transact().executeOrder(order_id, _amount_take, True)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, False, _agent, False
    ]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系11-2
# 償還済みフラグがTrueの場合
# Take売注文
def test_executeOrder_error_11_2(web3, chain, users,
                                 bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Make注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId()

    # 償還処理：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_token.transact().redeem()
    chain.wait.for_receipt(txn_hash)

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_take = 50
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_take)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, False)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().getOrder(order_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, True, _agent, False
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]


# エラー系12-1
# Take数量が元注文の残数量を超過している場合
# Take買注文
def test_executeOrder_error_12_1(web3, chain, users,
                                 bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId()

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _amount_take = 101  # Make注文の数量を超過
    try:
        txn_hash = bond_exchange.transact().executeOrder(order_id, _amount_take, True)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, False, _agent, False
    ]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系12-2
# Take数量が元注文の残数量を超過している場合
# Take売注文
def test_executeOrder_error_12_2(web3, chain, users,
                                 bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Make注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId()

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_take = 101  # Make注文の数量を超過
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_take)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, False)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().getOrder(order_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, True, _agent, False
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]


# エラー系13
# Take注文の発注者の残高が発注数量を下回っている場合
def test_executeOrder_error_13(web3, chain, users,
                               bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Make注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId()

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_take = 50
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_take)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take + 1, False)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().getOrder(order_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make,  # Make注文の件数から減っていない状態
        _price, True, _agent, False
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]


'''
TEST_決済承認（confirmAgreement）
'''


# 正常系1
# Make売、Take買
# ＜発行体＞新規発行 -> ＜発行体＞Make注文（売）
#  -> ＜投資家＞Take注文（買） -> ＜決済業者＞決済処理
def test_confirmAgreement_normal_1(web3, chain, users,
                                   bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId()
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementId(order_id)

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().confirmAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().getOrder(order_id)
    agreement = bond_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, False, _agent, False
    ]

    assert agreement[0:5] == [_trader, _amount_take, _price, False, True]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == _amount_take
    assert commitment == _amount_make - _amount_take

    # Assert: last_price
    assert bond_exchange.call().lastPrice(bond_token.address) == 123


# 正常系2
# Make買、Take売
# ＜発行体＞新規発行 -> ＜投資家＞Make注文（買）
#  -> ＜発行体＞Take注文（売） -> ＜決済業者＞決済処理
def test_confirmAgreement_normal_2(web3, chain, users,
                                   bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId()

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_take = 50
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_take)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(order_id, _amount_take, False)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementId(order_id)

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().confirmAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().getOrder(order_id)
    agree = bond_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, True, _agent, False
    ]
    assert agree[0:5] == [_issuer, _amount_take, _price, False, True]
    assert balance_maker == _amount_take
    assert balance_taker == deploy_args[2] - _amount_take
    assert commitment == 0

    # Assert: last_price
    assert bond_exchange.call().lastPrice(bond_token.address) == 123


# エラー系1
# 入力値の型誤り（_orderId）
def test_confirmAgreement_error_1(web3, users, bond_exchange):
    _agent = users['agent']

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent

    with pytest.raises(TypeError):
        bond_exchange.transact().confirmAgreement(-1, 0)

    with pytest.raises(TypeError):
        bond_exchange.transact().confirmAgreement(2 ** 256, 0)

    with pytest.raises(TypeError):
        bond_exchange.transact().confirmAgreement('0', 0)

    with pytest.raises(TypeError):
        bond_exchange.transact().confirmAgreement(0.1, 0)


# エラー系2
# 入力値の型誤り（_agreementId）
def test_confirmAgreement_error_2(web3, users, bond_exchange):
    _agent = users['agent']

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent

    with pytest.raises(TypeError):
        bond_exchange.transact().confirmAgreement(0, -1)

    with pytest.raises(TypeError):
        bond_exchange.transact().confirmAgreement(0, 2 ** 256)

    with pytest.raises(TypeError):
        bond_exchange.transact().confirmAgreement(0, '0')

    with pytest.raises(TypeError):
        bond_exchange.transact().confirmAgreement(0, 0.1)


# エラー系3
# 指定した注文番号が、直近の注文ID以上の場合
def test_confirmAgreement_error_3(web3, chain, users,
                                  bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId()
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementId(order_id)

    # 決済承認：決済業者
    order_id_error = bond_exchange.call().latestOrderId() + 1
    web3.eth.defaultAccount = _agent
    try:
        txn_hash = bond_exchange.transact().confirmAgreement(order_id_error, agreement_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    agreement = bond_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, False, _agent, False
    ]

    assert agreement[0:5] == [_trader, _amount_take, _price, False, False]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make

    # Assert: last_price
    assert bond_exchange.call().lastPrice(bond_token.address) == 0


# エラー系4
# 指定した約定IDが、直近の約定ID以上の場合
def test_confirmAgreement_error_4(web3, chain, users,
                                  bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId()
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementId(order_id)

    # 決済承認：決済業者
    agreement_id_error = bond_exchange.call().latestAgreementId(order_id) + 1
    web3.eth.defaultAccount = _agent
    try:
        txn_hash = bond_exchange.transact().confirmAgreement(order_id, agreement_id_error)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    agreement = bond_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, False, _agent, False
    ]

    assert agreement[0:5] == [_trader, _amount_take, _price, False, False]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make

    # Assert: last_price
    assert bond_exchange.call().lastPrice(bond_token.address) == 0


# エラー系5
# 指定した約定明細がすでに支払い済みの状態の場合
def test_confirmAgreement_error_5(web3, chain, users,
                                  bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId()
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementId(order_id)

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().confirmAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    # 決済承認：決済業者（2回目）
    web3.eth.defaultAccount = _agent
    try:
        txn_hash = bond_exchange.transact().confirmAgreement(order_id, agreement_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    agreement = bond_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, False, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_take, _price, False, True]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == _amount_take
    assert commitment == _amount_make - _amount_take

    # Assert: last_price
    assert bond_exchange.call().lastPrice(bond_token.address) == 123


# エラー系6
# 元注文で指定した決済業者ではない場合
def test_confirmAgreement_error_6(web3, chain, users,
                                  bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId()
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementId(order_id)

    # 決済承認：投資家（指定した決済業者ではない）
    web3.eth.defaultAccount = _trader
    try:
        txn_hash = bond_exchange.transact().confirmAgreement(order_id, agreement_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    agreement = bond_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, False, _agent, False
    ]

    assert agreement[0:5] == [_trader, _amount_take, _price, False, False]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make

    # Assert: last_price
    assert bond_exchange.call().lastPrice(bond_token.address) == 0


# エラー系7
# 既に決済非承認済み（キャンセル済み）の場合
def test_confirmAgreement_error_7(web3, chain, users,
                                  bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId()
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementId(order_id)

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().cancelAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent
    try:
        txn_hash = bond_exchange.transact().confirmAgreement(order_id, agreement_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    agreement = bond_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, False, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_take, _price, True, False]
    assert balance_maker == deploy_args[2] - _amount_make + _amount_take
    assert balance_taker == 0
    assert commitment == _amount_make - _amount_take

    # Assert: last_price
    assert bond_exchange.call().lastPrice(bond_token.address) == 0


'''
TEST_決済非承認（cancelAgreement）
'''


# 正常系1
# Make売、Take買
# ＜発行体＞新規発行 -> ＜発行体＞Make注文（売）
#  -> ＜投資家＞Take注文（買） -> ＜決済業者＞決済非承認
def test_cancelAgreement_normal_1(web3, chain, users,
                                  bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId()
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementId(order_id)

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().cancelAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().getOrder(order_id)
    agreement = bond_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, False, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_take, _price, True, False]
    assert balance_maker == deploy_args[2] - _amount_make + _amount_take
    assert balance_taker == 0
    assert commitment == _amount_make - _amount_take


# 正常系2
# Make買、Take売
# ＜発行体＞新規発行 -> ＜投資家＞Make注文（買）
#  -> ＜発行体＞Take注文（売） -> ＜決済業者＞決済非承認
def test_cancelAgreement_normal_2(web3, chain, users,
                                  bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 新規注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId()

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_take = 50
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_take)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(order_id, _amount_take, False)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementId(order_id)

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().cancelAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().getOrder(order_id)
    agree = bond_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, True, _agent, False
    ]
    assert agree[0:5] == [_issuer, _amount_take, _price, True, False]
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]
    assert commitment == 0


# エラー系1
# 入力値の型誤り（_orderId）
def test_cancelAgreement_error_1(web3, users, bond_exchange):
    _agent = users['agent']

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent

    with pytest.raises(TypeError):
        bond_exchange.transact().cancelAgreement(-1, 0)

    with pytest.raises(TypeError):
        bond_exchange.transact().cancelAgreement(2 ** 256, 0)

    with pytest.raises(TypeError):
        bond_exchange.transact().cancelAgreement('0', 0)

    with pytest.raises(TypeError):
        bond_exchange.transact().cancelAgreement(0.1, 0)


# エラー系2
# 入力値の型誤り（_agreementId）
def test_cancelAgreement_error_2(web3, users, bond_exchange):
    _agent = users['agent']

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent

    with pytest.raises(TypeError):
        bond_exchange.transact().cancelAgreement(0, -1)

    with pytest.raises(TypeError):
        bond_exchange.transact().cancelAgreement(0, 2 ** 256)

    with pytest.raises(TypeError):
        bond_exchange.transact().cancelAgreement(0, '0')

    with pytest.raises(TypeError):
        bond_exchange.transact().cancelAgreement(0, 0.1)


# エラー系3
# 指定した注文番号が、直近の注文ID以上の場合
def test_cancelAgreement_error_3(web3, chain, users,
                                 bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId()
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementId(order_id)

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    order_id_error = bond_exchange.call().latestOrderId() + 1
    try:
        txn_hash = bond_exchange.transact().cancelAgreement(order_id_error, agreement_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    agreement = bond_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, False, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_take, _price, False, False]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系4
# 指定した約定IDが、直近の約定ID以上の場合
def test_cancelAgreement_error_4(web3, chain, users,
                                 bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId()
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementId(order_id)

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    agreement_id_error = bond_exchange.call().latestAgreementId(order_id) + 1
    try:
        txn_hash = bond_exchange.transact().cancelAgreement(order_id, agreement_id_error)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    agreement = bond_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, False, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_take, _price, False, False]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系5
# すでに決済承認済み（支払済み）の場合
def test_cancelAgreement_error_5(web3, chain, users,
                                 bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId()
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementId(order_id)

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().confirmAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    try:
        txn_hash = bond_exchange.transact().cancelAgreement(order_id, agreement_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    agreement = bond_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, False, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_take, _price, False, True]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == _amount_take
    assert commitment == _amount_make - _amount_take


# エラー系6
# msg.senderが、決済代行（agent）以外の場合
def test_cancelAgreement_error_6(web3, chain, users,
                                 bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId()
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementId(order_id)

    # 決済非承認：投資家（決済業者以外）
    web3.eth.defaultAccount = _trader
    try:
        txn_hash = bond_exchange.transact().cancelAgreement(order_id, agreement_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    agreement = bond_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, False, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_take, _price, False, False]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make


# エラー系5
# すでに決済非承認済み（キャンセル済み）の場合
def test_cancelAgreement_error_7(web3, chain, users,
                                 bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId()
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementId(order_id)

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().cancelAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    # 決済非承認：決済業者（2回目）
    web3.eth.defaultAccount = _agent
    try:
        txn_hash = bond_exchange.transact().cancelAgreement(order_id, agreement_id)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    orderbook = bond_exchange.call().getOrder(order_id)
    agreement = bond_exchange.call().getAgreement(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, False, _agent, False
    ]
    assert agreement[0:5] == [_trader, _amount_take, _price, True, False]
    assert balance_maker == deploy_args[2] - _amount_make + _amount_take
    assert balance_taker == 0
    assert commitment == _amount_make - _amount_take


'''
TEST_引き出し（withdrawAll）
'''


# 正常系1
# ＜発行体＞新規発行 -> ＜発行体＞デポジット -> ＜発行体＞引き出し
def test_withdrawAll_normal_1(web3, chain, users, bond_exchange, personal_info):
    _issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # 引き出し：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().withdrawAll(bond_token.address)
    chain.wait.for_receipt(txn_hash)

    balance_exchange = bond_exchange.call().balanceOf(_issuer, bond_token.address)
    balance_token = bond_token.call().balanceOf(_issuer)

    assert balance_exchange == 0
    assert balance_token == deploy_args[2]


# 正常系2
# ＜発行体＞新規発行 -> ＜発行体＞デポジット（2回） -> ＜発行体＞引き出し
def test_withdrawAll_normal_2(web3, chain, users, bond_exchange, personal_info):
    _issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # Exchangeへのデポジット（2回目）：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # 引き出し：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().withdrawAll(bond_token.address)
    chain.wait.for_receipt(txn_hash)

    balance_exchange = bond_exchange.call().balanceOf(_issuer, bond_token.address)
    balance_token = bond_token.call().balanceOf(_issuer)

    assert balance_exchange == 0
    assert balance_token == deploy_args[2]


# 正常系3
# ＜発行体＞新規発行 -> ＜発行体＞Make注文（売） ※売注文中状態
#  -> ＜発行体＞引き出し
def test_withdrawAll_normal_3(web3, chain, users,
                              bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_transfer = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_transfer)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 70  # 100のうち70だけ売注文
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # 引き出し：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().withdrawAll(bond_token.address)
    chain.wait.for_receipt(txn_hash)

    balance_exchange = bond_exchange.call().balanceOf(_issuer, bond_token.address)
    balance_token = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert balance_exchange == 0
    assert balance_token == deploy_args[2] - _amount_make
    assert commitment == _amount_make


# 正常系4
# ＜発行体＞新規発行 -> ＜発行体＞Make注文（売） -> ＜投資家＞Take注文（買）
#  -> ＜発行体＞引き出し
def test_withdrawAll_normal_4(web3, chain, users,
                              bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_transfer = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_transfer)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 70  # 100のうち70だけ売注文
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId()
    _amount_take = 50  # 70の売注文に対して、50のTake
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    # 引き出し：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().withdrawAll(bond_token.address)
    chain.wait.for_receipt(txn_hash)

    balance_exchange = bond_exchange.call().balanceOf(_issuer, bond_token.address)
    balance_token = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert balance_exchange == 0
    assert balance_token == deploy_args[2] - _amount_make
    assert commitment == _amount_make


# 正常系5
# ＜発行体＞新規発行 -> ＜発行体＞Make注文（売） -> ＜投資家＞Take注文（買）
#  -> ＜決済業者＞決済承認 -> ＜発行体＞引き出し
def test_withdrawAll_normal_5(web3, chain, users,
                              bond_exchange, personal_info, payment_gateway):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _issuer, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    payment_gateway_register(web3, chain, payment_gateway, _trader, _agent)
    payment_gateway_approve(web3, chain, payment_gateway, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_transfer = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_transfer)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 70  # 100のうち70だけ売注文
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId()
    _amount_take = 50  # 70の売注文に対して、50のTake
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementId(order_id)

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().confirmAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    # 引き出し：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().withdrawAll(bond_token.address)
    chain.wait.for_receipt(txn_hash)

    balance_issuer_exchange = bond_exchange.call().balanceOf(_issuer, bond_token.address)
    balance_issuer_token = bond_token.call().balanceOf(_issuer)
    balance_trader_exchange = bond_exchange.call().balanceOf(_trader, bond_token.address)
    balance_trader_token = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitmentOf(_issuer, bond_token.address)

    assert balance_issuer_exchange == 0
    assert balance_issuer_token == deploy_args[2] - _amount_make
    assert balance_trader_exchange == 0
    assert balance_trader_token == _amount_take
    assert commitment == _amount_make - _amount_take


# エラー系１
# 入力値の型誤り（_token）
def test_withdrawAll_error_1(web3, users, bond_exchange):
    _issuer = users['issuer']

    # 引き出し：発行体
    web3.eth.defaultAccount = _issuer

    with pytest.raises(TypeError):
        bond_exchange.transact().withdrawAll(1234)

    with pytest.raises(TypeError):
        bond_exchange.transact().withdrawAll('1234')


# エラー系2-1
# 残高がゼロの場合
# ＜発行体＞新規発行 -> ＜発行体＞デポジット -> ＜発行体＞引き出し（2回）
def test_withdrawAll_error_2_1(web3, chain, users, bond_exchange, personal_info):
    _issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # 引き出し：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().withdrawAll(bond_token.address)
    chain.wait.for_receipt(txn_hash)

    # 引き出し（2回目)：発行体
    web3.eth.defaultAccount = _issuer
    try:
        txn_hash = bond_exchange.transact().withdrawAll(bond_token.address)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    balance_exchange = bond_exchange.call().balanceOf(_issuer, bond_token.address)
    balance_token = bond_token.call().balanceOf(_issuer)

    assert balance_exchange == 0
    assert balance_token == deploy_args[2]


# エラー系2-2
# 残高がゼロの場合
# ＜発行体＞新規発行 -> ＜発行体＞デポジット -> 異なるアドレスからの引き出し
def test_withdrawAll_error_2_2(web3, chain, users, bond_exchange, personal_info):
    _issuer = users['issuer']
    _trader = users['trader']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_transfer = 100
    txn_hash = bond_token.transact().transfer(
        bond_exchange.address, _amount_transfer)
    chain.wait.for_receipt(txn_hash)

    # 引き出し：異なるアドレス
    web3.eth.defaultAccount = _trader
    try:
        txn_hash = bond_exchange.transact().withdrawAll(bond_token.address)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    balance_exchange = bond_exchange.call().balanceOf(_issuer, bond_token.address)
    balance_token = bond_token.call().balanceOf(_issuer)

    assert balance_exchange == _amount_transfer
    assert balance_token == deploy_args[2] - _amount_transfer


'''
TEST_Exchange切替
'''


# 正常系
def test_updateExchange_normal_1(web3, chain, users,
                                 bond_exchange, bond_exchange_storage,
                                 personal_info, payment_gateway):
    issuer = users['issuer']
    agent = users['agent']
    admin = users['admin']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    payment_gateway_register(web3, chain, payment_gateway, issuer, agent)
    payment_gateway_approve(web3, chain, payment_gateway, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = issuer
    txn_hash = bond_token.transact().transfer(bond_exchange.address, 100)
    chain.wait.for_receipt(txn_hash)

    # 新規注文（売）
    web3.eth.defaultAccount = issuer
    txn_hash = bond_exchange.transact().\
        createOrder(bond_token.address, 10, 123, False, agent)
    chain.wait.for_receipt(txn_hash)

    # Exchange（新）
    web3.eth.defaultAccount = admin
    bond_exchange_new, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBondExchange',
        deploy_args=[
            payment_gateway.address,
            personal_info.address,
            bond_exchange_storage.address
        ]
    )
    txn_hash = bond_exchange_storage.transact().\
        upgradeVersion(bond_exchange_new.address)
    chain.wait.for_receipt(txn_hash)

    # Exchange（新）からの情報参照
    web3.eth.defaultAccount = issuer
    order_id = bond_exchange_new.call().latestOrderId()
    orderbook = bond_exchange_new.call().getOrder(order_id)
    commitment = bond_exchange_new.call().commitmentOf(issuer, bond_token.address)
    balance_exchange = bond_exchange_new.call().balanceOf(issuer, bond_token.address)
    balance_token = bond_token.call().balanceOf(issuer)

    assert orderbook == [
        issuer, to_checksum_address(bond_token.address),
        10, 123, False, agent, False
    ]
    assert balance_token == deploy_args[2] - 100
    assert balance_exchange == 90
    assert commitment == 10
