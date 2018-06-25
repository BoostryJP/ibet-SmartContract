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

# WhiteList登録
def whitelist_register(web3, chain, whitelist, trader, agent):
    web3.eth.defaultAccount = trader
    message = 'some_message'
    txn_hash = whitelist.transact().register(agent, message)
    chain.wait.for_receipt(txn_hash)

# WhiteList認可
def whitelist_approve(web3, chain, whitelist, trader, agent):
    web3.eth.defaultAccount = agent
    txn_hash = whitelist.transact().approve(trader)
    chain.wait.for_receipt(txn_hash)

# Bondトークンを取引所にデポジット
def bond_transfer(web3, chain, bond_token, bond_exchange, trader, amount):
    web3.eth.defaultAccount = trader
    txn_hash = bond_token.transact().transfer(
        bond_exchange.address, amount)
    chain.wait.for_receipt(txn_hash)

'''
TEST1_デプロイ
'''
# ＜正常系1＞
# Deploy　→　正常
def test_deploy_normal_1(users, bond_exchange, personal_info, white_list):
    owner = bond_exchange.call().owner()
    personalInfoAddress = bond_exchange.call().personalInfoAddress()
    whiteListAddress = bond_exchange.call().whiteListAddress()

    assert owner == users['admin']
    assert personalInfoAddress == to_checksum_address(personal_info.address)
    assert whiteListAddress == to_checksum_address(white_list.address)

# ＜エラー系1＞
# 入力値の型誤り（WhiteListアドレス）
def test_deploy_error_1(web3, users, chain, white_list, personal_info):
    exchange_owner = users['admin']
    web3.eth.defaultAccount = exchange_owner

    deploy_args = [
        1234,
        personal_info.address
    ]

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetStraightBondExchange',
            deploy_args = deploy_args
        )

# ＜エラー系2＞
# 入力値の型誤り（PersonalInfoアドレス）
def test_deploy_error_2(web3, users, chain, white_list, personal_info):
    exchange_owner = users['admin']
    web3.eth.defaultAccount = exchange_owner
    deploy_args = [
        white_list.address,
        1234
    ]
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetStraightBondExchange', deploy_args = deploy_args)

'''
TEST2_Make注文（createOrder）
'''
# 正常系１
# ＜発行体＞新規発行 -> ＜投資家＞新規注文（買）
def test_createorder_normal_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    whitelist_register(web3, chain, white_list, issuer, agent)
    whitelist_approve(web3, chain, white_list, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # 新規注文（買）
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    _isBuy = True
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId() - 1
    orderbook = bond_exchange.call().orderBook(order_id)

    assert orderbook == [
        issuer, to_checksum_address(bond_token.address), _amount, _price,
        _isBuy, agent, False
    ]
    assert bond_token.call().balanceOf(issuer) == deploy_args[2]

# 正常系2
# ＜発行体＞新規発行 -> ＜発行体＞新規注文（売）
def test_createorder_normal_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    whitelist_register(web3, chain, white_list, issuer, agent)
    whitelist_approve(web3, chain, white_list, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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

    order_id = bond_exchange.call().latestOrderId() - 1
    orderbook = bond_exchange.call().orderBook(order_id)
    commitment = bond_exchange.call().commitments(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert orderbook == [
        issuer, to_checksum_address(bond_token.address), _amount, _price,
        _isBuy, agent, False
    ]
    assert balance == deploy_args[2] - _amount
    assert commitment == _amount

# エラー系1
# 入力値の型誤り（_token）
def test_createorder_error_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
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
def test_createorder_error_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _price = 123
    _isBuy = False

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, -1, _price, _isBuy, agent)

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, 2**256, _price, _isBuy, agent)

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, '0', _price, _isBuy, agent)

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, 0.1, _price, _isBuy, agent)

# エラー系3
# 入力値の型誤り（_price）
def test_createorder_error_3(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # 新規注文
    web3.eth.defaultAccount = issuer
    _amount = 100
    _isBuy = False

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, _amount, -1, _isBuy, agent)

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, _amount, 2**256, _isBuy, agent)

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, _amount, '0', _isBuy, agent)

    with pytest.raises(TypeError):
        bond_exchange.transact().createOrder(
            bond_token.address, _amount, 0.1, _isBuy, agent)

# エラー系4
# 入力値の型誤り（_isBuy）
def test_createorder_error_4(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
def test_createorder_error_5(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    whitelist_register(web3, chain, white_list, issuer, agent)
    whitelist_approve(web3, chain, white_list, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # 新規注文（買）
    web3.eth.defaultAccount = issuer
    _amount = 0
    _price = 123
    _isBuy = True
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent) # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = bond_exchange.call().commitments(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0

# エラー系6-2
# 売注文数量が0の場合
def test_createorder_error_6_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    whitelist_register(web3, chain, white_list, issuer, agent)
    whitelist_approve(web3, chain, white_list, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
        bond_token.address, _amount, _price, _isBuy, agent) # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = bond_exchange.call().commitments(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0

# エラー系7-1
# 未認可のアカウントアドレスからの注文（買）
def test_createorder_error_7_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    whitelist_register(web3, chain, white_list, issuer, agent) # 未認可状態

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # 新規注文（買）
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    _isBuy = False
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent) # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = bond_exchange.call().commitments(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0

# エラー系7-2
# 未認可のアカウントアドレスからの注文（買）
def test_createorder_error_7_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer) # 未認可状態

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
        bond_token.address, _amount, _price, _isBuy, agent) # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = bond_exchange.call().commitments(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0

# エラー系8-1
# 名簿用個人情報が登録されていない場合（買注文）
def test_createorder_error_8_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    whitelist_register(web3, chain, white_list, issuer, agent)
    whitelist_approve(web3, chain, white_list, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # 新規注文（買）
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    _isBuy = True
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount, _price, _isBuy, agent) # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = bond_exchange.call().commitments(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0

# エラー系8-2
# 名簿用個人情報が登録されていない場合（売注文）
def test_createorder_error_8_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    whitelist_register(web3, chain, white_list, issuer, agent)
    whitelist_approve(web3, chain, white_list, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
        bond_token.address, _amount, _price, _isBuy, agent) # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = bond_exchange.call().commitments(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0

# エラー系9-1
# 償還済みフラグがTrueの場合
# ＜発行体＞新規発行 -> ＜発行体＞償還設定 -> ＜発行体＞新規注文（買）
def test_createorder_error_9_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    whitelist_register(web3, chain, white_list, issuer, agent)
    whitelist_approve(web3, chain, white_list, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
        bond_token.address, _amount, _price, _isBuy, agent) # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = bond_exchange.call().commitments(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0

# エラー系9-2
# 償還済みフラグがTrueの場合
# ＜発行体＞新規発行 -> ＜発行体＞償還設定 -> ＜発行体＞新規注文（売）
def test_createorder_error_9_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    whitelist_register(web3, chain, white_list, issuer, agent)
    whitelist_approve(web3, chain, white_list, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
        bond_token.address, _amount, _price, _isBuy, agent) # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = bond_exchange.call().commitments(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0

# エラー系10
# 残高不足
def test_createorder_error_10(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    whitelist_register(web3, chain, white_list, issuer, agent)
    whitelist_approve(web3, chain, white_list, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
        bond_token.address, _amount + 1, _price, _isBuy, agent) # エラーになる
    chain.wait.for_receipt(txn_hash)

    commitment = bond_exchange.call().commitments(issuer, bond_token.address)
    balance = bond_token.call().balanceOf(issuer)

    assert balance == deploy_args[2]
    assert commitment == 0


'''
TEST3_注文キャンセル（cancelOrder）
'''
# 正常系1
# ＜発行体＞新規発行 -> ＜投資家（発行体）＞新規注文（買）
#  -> ＜投資家（発行体）＞注文キャンセル
def test_cancelOrder_normal_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    whitelist_register(web3, chain, white_list, issuer, agent)
    whitelist_approve(web3, chain, white_list, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    txn_hash = bond_exchange.transact().cancelOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)

    assert orderbook == [
        issuer, to_checksum_address(bond_token.address), _amount, _price,
        _isBuy, agent, True
    ]
    assert bond_token.call().balanceOf(issuer) == deploy_args[2]

# 正常系2
# ＜発行体＞新規発行 -> ＜投資家（発行体）＞新規注文（売）
#  -> ＜投資家（発行体）＞注文キャンセル
def test_cancelOrder_normal_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    whitelist_register(web3, chain, white_list, issuer, agent)
    whitelist_approve(web3, chain, white_list, issuer, agent)

    # 新規発行
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    txn_hash = bond_exchange.transact().cancelOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance = bond_token.call().balanceOf(issuer)
    commitment = bond_exchange.call().commitments(issuer, bond_token.address)

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
    order_id = bond_exchange.call().latestOrderId()

    with pytest.raises(TypeError):
        bond_exchange.transact().cancelOrder(-1)

    with pytest.raises(TypeError):
        bond_exchange.transact().cancelOrder(2**256)

    with pytest.raises(TypeError):
        bond_exchange.transact().cancelOrder('0')

    with pytest.raises(TypeError):
        bond_exchange.transact().cancelOrder(0.1)

# エラー系2
# 指定した注文IDが直近の注文IDを超えている場合
def test_cancelOrder_error_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    whitelist_register(web3, chain, white_list, issuer, agent)
    whitelist_approve(web3, chain, white_list, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    txn_hash = bond_exchange.transact().cancelOrder(order_id) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id - 1)

    assert orderbook == [
        issuer, to_checksum_address(bond_token.address), _amount, _price,
        _isBuy, agent, False
    ]
    assert bond_token.call().balanceOf(issuer) == deploy_args[2]

# エラー系3-1
# 注文がキャンセル済みの場合（買注文）
def test_cancelOrder_error_3_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    whitelist_register(web3, chain, white_list, issuer, agent)
    whitelist_approve(web3, chain, white_list, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    txn_hash = bond_exchange.transact().cancelOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    # 注文キャンセル（2回目）
    web3.eth.defaultAccount = issuer
    txn_hash = bond_exchange.transact().cancelOrder(order_id) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)

    assert orderbook == [
        issuer, to_checksum_address(bond_token.address), _amount, _price,
        _isBuy, agent, True
    ]
    assert bond_token.call().balanceOf(issuer) == deploy_args[2]

# エラー系3-2
# 注文がキャンセル済みの場合（売注文）
def test_cancelOrder_error_3_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    whitelist_register(web3, chain, white_list, issuer, agent)
    whitelist_approve(web3, chain, white_list, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    txn_hash = bond_exchange.transact().cancelOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    # 注文キャンセル（2回目）
    web3.eth.defaultAccount = issuer
    txn_hash = bond_exchange.transact().cancelOrder(order_id) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)

    assert orderbook == [
        issuer, to_checksum_address(bond_token.address), _amount, _price,
        _isBuy, agent, True
    ]
    assert bond_token.call().balanceOf(issuer) == deploy_args[2]

# エラー系4-1
# 元注文の発注者と、注文キャンセルの実施者が異なる場合（買注文）
def test_cancelOrder_error_4_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    other = users['trader']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    whitelist_register(web3, chain, white_list, issuer, agent)
    whitelist_approve(web3, chain, white_list, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    txn_hash = bond_exchange.transact().cancelOrder(order_id) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)

    assert orderbook == [
        issuer, to_checksum_address(bond_token.address), _amount, _price,
        _isBuy, agent, False
    ]
    assert bond_token.call().balanceOf(issuer) == deploy_args[2]

# エラー系4-2
# 元注文の発注者と、注文キャンセルの実施者が異なる場合（売注文）
def test_cancelOrder_error_4_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    issuer = users['issuer']
    other = users['trader']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, issuer, issuer)
    whitelist_register(web3, chain, white_list, issuer, agent)
    whitelist_approve(web3, chain, white_list, issuer, agent)

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    txn_hash = bond_exchange.transact().cancelOrder(order_id) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance = bond_token.call().balanceOf(issuer)
    commitment = bond_exchange.call().commitments(issuer, bond_token.address)

    assert orderbook == [
        issuer, to_checksum_address(bond_token.address), _amount, _price,
        _isBuy, agent, False
    ]
    assert balance == deploy_args[2] - _amount
    assert commitment == _amount


'''
TEST4_Take注文（executeOrder）
'''
# 正常系1
# ＜発行体＞新規発行 -> ＜発行体＞新規注文（売） -> ＜投資家＞Take注文（買）
def test_executeOrder_normal_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementIds(order_id) - 1

    orderbook = bond_exchange.call().orderBook(order_id)
    agree = bond_exchange.call().agreements(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

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
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # 新規注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId() - 1

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_take = 50
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_take)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(order_id, _amount_take, False)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementIds(order_id) - 1

    orderbook = bond_exchange.call().orderBook(order_id)
    agree = bond_exchange.call().agreements(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

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
        txn_hash = bond_exchange.transact().executeOrder(
            -1, _amount, _is_buy)

    with pytest.raises(TypeError):
        txn_hash = bond_exchange.transact().executeOrder(
            2**256, _amount, _is_buy)

    with pytest.raises(TypeError):
        txn_hash = bond_exchange.transact().executeOrder(
            '0', _amount, _is_buy)

    with pytest.raises(TypeError):
        txn_hash = bond_exchange.transact().executeOrder(
            0.1, _amount, _is_buy)

# エラー系2
# 入力値の型誤り（_amount）
def test_executeOrder_error_2(web3, users, bond_exchange):
    _trader = users['trader']

    web3.eth.defaultAccount = _trader
    _order_id = 1000
    _is_buy = True

    with pytest.raises(TypeError):
        txn_hash = bond_exchange.transact().executeOrder(
            _order_id, -1, _is_buy)

    with pytest.raises(TypeError):
        txn_hash = bond_exchange.transact().executeOrder(
            _order_id, 2**256, _is_buy)

    with pytest.raises(TypeError):
        txn_hash = bond_exchange.transact().executeOrder(
            _order_id, '0', _is_buy)

    with pytest.raises(TypeError):
        txn_hash = bond_exchange.transact().executeOrder(
            _order_id, 0.1, _is_buy)

# エラー系3
# 入力値の型誤り（_isBuy）
def test_executeOrder_error_3(web3, users, bond_exchange):
    _trader = users['trader']

    web3.eth.defaultAccount = _trader
    _order_id = 1000
    _amount = 123

    with pytest.raises(TypeError):
        txn_hash = bond_exchange.transact().executeOrder(
            _order_id, _amount, 'True')

    with pytest.raises(TypeError):
        txn_hash = bond_exchange.transact().executeOrder(
            _order_id, _amount, 111)

# エラー系4
# 指定した注文IDが直近の注文IDを超えている場合
def test_executeOrder_error_4(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # Make注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    latest_order_id = bond_exchange.call().latestOrderId()

    # Take注文（売）
    web3.eth.defaultAccount = _issuer
    order_id = latest_order_id
    _amount = 123

    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount, False) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(latest_order_id - 1)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make, # Make注文の件数から減っていない状態
        _price, True, _agent, False
    ]

    assert balance_maker == 0
    assert balance_taker == deploy_args[2]

# エラー系5-1
# 注文数量が0の場合
# Take買注文
def test_executeOrder_error_5_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    txn_hash = bond_exchange.transact().executeOrder(order_id, 0, True) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make, # Make注文の件数から減っていない状態
        _price, False, _agent, False
    ]

    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make

# エラー系5-2
# 注文数量が0の場合
# Take売注文
def test_executeOrder_error_5_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(order_id, 0, False) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make, # Make注文の件数から減っていない状態
        _price, True, _agent, False
    ]

    assert balance_maker == 0
    assert balance_taker == deploy_args[2]
    assert commitment == 0

# エラー系6-1
# 元注文と、発注する注文が同一の売買区分の場合
# Take買注文
def test_executeOrder_error_6_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, False) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make, # Make注文の件数から減っていない状態
        _price, False, _agent, False
    ]

    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make

# エラー系6-2
# 元注文と、発注する注文が同一の売買区分の場合
# Take売注文
def test_executeOrder_error_6_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # 新規注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：発行体
    order_id = bond_exchange.call().latestOrderId() - 1
    web3.eth.defaultAccount = _issuer
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make, # Make注文の件数から減っていない状態
        _price, True, _agent, False
    ]

    assert balance_maker == 0
    assert balance_taker == deploy_args[2]
    assert commitment == 0

# エラー系7-1
# 元注文の発注者と同一のアドレスからの発注の場合
# Take買注文
def test_executeOrder_error_7_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make, # Make注文の件数から減っていない状態
        _price, False, _agent, False
    ]

    assert balance_maker == deploy_args[2] - _amount_make
    assert commitment == _amount_make

# エラー系7-2
# 元注文の発注者と同一のアドレスからの発注の場合
# Take売注文
def test_executeOrder_error_7_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, False) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make, # Make注文の件数から減っていない状態
        _price, True, _agent, False
    ]
    assert commitment == 0
    assert balance_taker == deploy_args[2]

# エラー系8-1
# 元注文がキャンセル済の場合
# Take買注文
def test_executeOrder_error_8_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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

    order_id = bond_exchange.call().latestOrderId() - 1

    # Make注文取消：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().cancelOrder(order_id)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make, # Make注文の件数から減っていない状態
        _price, False, _agent, True # 取消済み状態
    ]
    assert balance_maker == deploy_args[2]
    assert balance_taker == 0
    assert commitment == 0

# エラー系8-2
# 元注文の発注者と同一のアドレスからの発注の場合
# Take売注文
def test_executeOrder_error_8_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # Make注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId() - 1

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
        order_id, _amount_take, False) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make, # Make注文の件数から減っていない状態
        _price, True, _agent, True # 取り消し済み状態
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]

# エラー系9-1
# 認可されたアドレスではない場合
# Take買注文
def test_executeOrder_error_9_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent) # 未認可状態

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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

    order_id = bond_exchange.call().latestOrderId() - 1

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make, # Make注文の件数から減っていない状態
        _price, False, _agent, False
    ]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make

# エラー系9-2
# 元注文の発注者と同一のアドレスからの発注の場合
# Take売注文
def test_executeOrder_error_9_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent) # 未認可状態

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # Make注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId() - 1

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_take = 50
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_take)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, False) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make, # Make注文の件数から減っていない状態
        _price, True, _agent, False
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]

# エラー系10-1
# 名簿用個人情報が登録されていない場合
# Take買注文
def test_executeOrder_error_10_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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

    order_id = bond_exchange.call().latestOrderId() - 1

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make, # Make注文の件数から減っていない状態
        _price, False, _agent, False
    ]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make

# エラー系10-2
# 名簿用個人情報が登録されていない場合
# Take売注文
def test_executeOrder_error_10_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # Make注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId() - 1

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_take = 50
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_take)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, False) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make, # Make注文の件数から減っていない状態
        _price, True, _agent, False
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]

# エラー系11-1
# 償還済みフラグがTrueの場合
# Take買注文
def test_executeOrder_error_11_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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

    order_id = bond_exchange.call().latestOrderId() - 1

    # 償還処理：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_token.transact().redeem()
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make, # Make注文の件数から減っていない状態
        _price, False, _agent, False
    ]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make

# エラー系11-2
# 償還済みフラグがTrueの場合
# Take売注文
def test_executeOrder_error_11_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # Make注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId() - 1

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
        order_id, _amount_take, False) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make, # Make注文の件数から減っていない状態
        _price, True, _agent, False
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]

# エラー系12-1
# Take数量が元注文の残数量を超過している場合
# Take買注文
def test_executeOrder_error_12_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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

    order_id = bond_exchange.call().latestOrderId() - 1

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _amount_take = 101 # Make注文の数量を超過
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make, # Make注文の件数から減っていない状態
        _price, False, _agent, False
    ]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make

# エラー系12-2
# Take数量が元注文の残数量を超過している場合
# Take売注文
def test_executeOrder_error_12_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # Make注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId() - 1

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_take = 101 # Make注文の数量を超過
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_take)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, False) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make, # Make注文の件数から減っていない状態
        _price, True, _agent, False
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]

# エラー系13
# Take注文の発注者の残高が発注数量を下回っている場合
def test_executeOrder_error_13(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # Make注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId() - 1

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_take = 50
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_take)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take + 1, False) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make, # Make注文の件数から減っていない状態
        _price, True, _agent, False
    ]
    assert commitment == 0
    assert balance_maker == 0
    assert balance_taker == deploy_args[2]

'''
TEST5_決済承認（confirmAgreement）
'''
# 正常系1
# Make売、Take買
# ＜発行体＞新規発行 -> ＜発行体＞Make注文（売）
#  -> ＜投資家＞Take注文（買） -> ＜決済業者＞決済処理
def test_confirmAgreement_normal_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementIds(order_id) - 1

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().confirmAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    agreement = bond_exchange.call().agreements(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, False, _agent, False
    ]

    assert agreement[0:5] == [_trader, _amount_take, _price, False, True]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == _amount_take
    assert commitment == _amount_make - _amount_take

# 正常系2
# Make買、Take売
# ＜発行体＞新規発行 -> ＜投資家＞Make注文（買）
#  -> ＜発行体＞Take注文（売） -> ＜決済業者＞決済処理
def test_confirmAgreement_normal_2(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # 新規注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId() - 1

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_take = 50
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_take)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(order_id, _amount_take, False)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementIds(order_id) - 1

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().confirmAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    agree = bond_exchange.call().agreements(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _trader, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, True, _agent, False
    ]
    assert agree[0:5] == [_issuer, _amount_take, _price, False, True]
    assert balance_maker == _amount_take
    assert balance_taker == deploy_args[2] - _amount_take
    assert commitment == 0

# エラー系1
# 入力値の型誤り（_orderId）
def test_confirmAgreement_error_1(web3, users, bond_exchange):
    _agent = users['agent']

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent

    with pytest.raises(TypeError):
        bond_exchange.transact().confirmAgreement(-1,0)

    with pytest.raises(TypeError):
        bond_exchange.transact().confirmAgreement(2**256,0)

    with pytest.raises(TypeError):
        bond_exchange.transact().confirmAgreement('0',0)

    with pytest.raises(TypeError):
        bond_exchange.transact().confirmAgreement(0.1,0)

# エラー系2
# 入力値の型誤り（_agreementId）
def test_confirmAgreement_error_2(web3, users, bond_exchange):
    _agent = users['agent']

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent

    with pytest.raises(TypeError):
        bond_exchange.transact().confirmAgreement(0,-1)

    with pytest.raises(TypeError):
        bond_exchange.transact().confirmAgreement(0,2**256)

    with pytest.raises(TypeError):
        bond_exchange.transact().confirmAgreement(0,'0')

    with pytest.raises(TypeError):
        bond_exchange.transact().confirmAgreement(0,0.1)

# エラー系3
# 指定した注文番号が、直近の注文ID以上の場合
def test_confirmAgreement_error_3(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementIds(order_id) - 1

    # 決済承認：決済業者
    order_id_error = bond_exchange.call().latestOrderId()
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().confirmAgreement(
        order_id_error, agreement_id) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    agreement = bond_exchange.call().agreements(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

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
def test_confirmAgreement_error_4(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementIds(order_id) - 1

    # 決済承認：決済業者
    agreement_id_error = bond_exchange.call().latestAgreementIds(order_id)
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().confirmAgreement(
        order_id, agreement_id_error) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    agreement = bond_exchange.call().agreements(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

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
# 指定した約定明細がすでに支払い済みの状態の場合
def test_confirmAgreement_error_5(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementIds(order_id) - 1

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().confirmAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    # 決済承認：決済業者（2回目）
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().confirmAgreement(
        order_id, agreement_id) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    agreement = bond_exchange.call().agreements(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

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
# 元注文で指定した決済業者ではない場合
def test_confirmAgreement_error_6(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementIds(order_id) - 1

    # 決済承認：投資家（指定した決済業者ではない）
    web3.eth.defaultAccount = _trader
    txn_hash = bond_exchange.transact().confirmAgreement(
        order_id, agreement_id) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    agreement = bond_exchange.call().agreements(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert orderbook == [
        _issuer, to_checksum_address(bond_token.address),
        _amount_make - _amount_take,
        _price, False, _agent, False
    ]

    assert agreement[0:5] == [_trader, _amount_take, _price, False, False]
    assert balance_maker == deploy_args[2] - _amount_make
    assert balance_taker == 0
    assert commitment == _amount_make

# エラー系7
# 既に決済非承認済み（キャンセル済み）の場合
def test_confirmAgreement_error_7(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementIds(order_id) - 1

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().cancelAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().confirmAgreement(
        order_id, agreement_id) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    agreement = bond_exchange.call().agreements(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

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
TEST6_決済非承認（cancelAgreement）
'''
# 正常系1
# Make売、Take買
# ＜発行体＞新規発行 -> ＜発行体＞Make注文（売）
#  -> ＜投資家＞Take注文（買） -> ＜決済業者＞決済非承認
def test_cancelAgreement_normal_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementIds(order_id) - 1

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().cancelAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    agreement = bond_exchange.call().agreements(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

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
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # 新規注文（買）：投資家
    web3.eth.defaultAccount = _trader
    _price = 123
    _amount_make = 100
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, True, _agent)
    chain.wait.for_receipt(txn_hash)

    order_id = bond_exchange.call().latestOrderId() - 1

    # 預かりをExchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_take = 50
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_take)
    chain.wait.for_receipt(txn_hash)

    # Take注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().executeOrder(order_id, _amount_take, False)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementIds(order_id) - 1

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().cancelAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    agree = bond_exchange.call().agreements(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_trader)
    balance_taker = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

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
        bond_exchange.transact().cancelAgreement(2**256, 0)

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
        bond_exchange.transact().cancelAgreement(0, 2**256)

    with pytest.raises(TypeError):
        bond_exchange.transact().cancelAgreement(0, '0')

    with pytest.raises(TypeError):
        bond_exchange.transact().cancelAgreement(0, 0.1)

# エラー系3
# 指定した注文番号が、直近の注文ID以上の場合
def test_cancelAgreement_error_3(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementIds(order_id) - 1

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    order_id_error = bond_exchange.call().latestOrderId()
    txn_hash = bond_exchange.transact().cancelAgreement(
        order_id_error, agreement_id) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    agreement = bond_exchange.call().agreements(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

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
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementIds(order_id) - 1

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    agreement_id_error = bond_exchange.call().latestAgreementIds(order_id)
    txn_hash = bond_exchange.transact().cancelAgreement(
        order_id, agreement_id_error) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    agreement = bond_exchange.call().agreements(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

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
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementIds(order_id) - 1

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().confirmAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().cancelAgreement(
        order_id, agreement_id) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    agreement = bond_exchange.call().agreements(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

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
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementIds(order_id) - 1

    # 決済非承認：投資家（決済業者以外）
    web3.eth.defaultAccount = _trader
    txn_hash = bond_exchange.transact().cancelAgreement(
        order_id, agreement_id) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    agreement = bond_exchange.call().agreements(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

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
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    order_id = bond_exchange.call().latestOrderId() - 1
    _amount_take = 50
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementIds(order_id) - 1

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().cancelAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    # 決済非承認：決済業者（2回目）
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().cancelAgreement(
        order_id, agreement_id) # エラーになる
    chain.wait.for_receipt(txn_hash)

    orderbook = bond_exchange.call().orderBook(order_id)
    agreement = bond_exchange.call().agreements(order_id, agreement_id)
    balance_maker = bond_token.call().balanceOf(_issuer)
    balance_taker = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

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
TEST7_引き出し（withdrawAll）
'''
# 正常系1
# ＜発行体＞新規発行 -> ＜発行体＞デポジット -> ＜発行体＞引き出し
def test_withdrawAll_normal_1(web3, chain, users, bond_exchange):
    _issuer = users['issuer']

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_make)
    chain.wait.for_receipt(txn_hash)

    # 引き出し：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().withdrawAll(bond_token.address)
    chain.wait.for_receipt(txn_hash)

    balance_exchange = bond_exchange.call().balances(_issuer, bond_token.address)
    balance_token = bond_token.call().balanceOf(_issuer)

    assert balance_exchange == 0
    assert balance_token == deploy_args[2]

# 正常系2
# ＜発行体＞新規発行 -> ＜発行体＞デポジット（2回） -> ＜発行体＞引き出し
def test_withdrawAll_normal_2(web3, chain, users, bond_exchange):
    _issuer = users['issuer']

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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

    balance_exchange = bond_exchange.call().balances(_issuer, bond_token.address)
    balance_token = bond_token.call().balanceOf(_issuer)

    assert balance_exchange == 0
    assert balance_token == deploy_args[2]

# 正常系3
# ＜発行体＞新規発行 -> ＜発行体＞Make注文（売） ※売注文中状態
#  -> ＜発行体＞引き出し
def test_withdrawAll_normal_3(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_transfer = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_transfer)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 70 # 100のうち70だけ売注文
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # 引き出し：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().withdrawAll(bond_token.address)
    chain.wait.for_receipt(txn_hash)

    balance_exchange = bond_exchange.call().balances(_issuer, bond_token.address)
    balance_token = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert balance_exchange == 0
    assert balance_token == deploy_args[2] - _amount_make
    assert commitment == _amount_make

# 正常系4
# ＜発行体＞新規発行 -> ＜発行体＞Make注文（売） -> ＜投資家＞Take注文（買）
#  -> ＜発行体＞引き出し
def test_withdrawAll_normal_4(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_transfer = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_transfer)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 70 # 100のうち70だけ売注文
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId() - 1
    _amount_take = 50 # 70の売注文に対して、50のTake
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementIds(order_id) - 1

    # 引き出し：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().withdrawAll(bond_token.address)
    chain.wait.for_receipt(txn_hash)

    balance_exchange = bond_exchange.call().balances(_issuer, bond_token.address)
    balance_token = bond_token.call().balanceOf(_issuer)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

    assert balance_exchange == 0
    assert balance_token == deploy_args[2] - _amount_make
    assert commitment == _amount_make

# 正常系5
# ＜発行体＞新規発行 -> ＜発行体＞Make注文（売） -> ＜投資家＞Take注文（買）
#  -> ＜決済業者＞決済承認 -> ＜発行体＞引き出し
def test_withdrawAll_normal_5(web3, chain, users,
    bond_exchange, personal_info, white_list):
    _issuer = users['issuer']
    _trader = users['trader']
    _agent = users['agent']

    personalinfo_register(web3, chain, personal_info, _issuer, _issuer)
    whitelist_register(web3, chain, white_list, _issuer, _agent)
    whitelist_approve(web3, chain, white_list, _issuer, _agent)

    personalinfo_register(web3, chain, personal_info, _trader, _issuer)
    whitelist_register(web3, chain, white_list, _trader, _agent)
    whitelist_approve(web3, chain, white_list, _trader, _agent)

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_transfer = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_transfer)
    chain.wait.for_receipt(txn_hash)

    # Make注文（売）：発行体
    web3.eth.defaultAccount = _issuer
    _amount_make = 70 # 100のうち70だけ売注文
    _price = 123
    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address, _amount_make, _price, False, _agent)
    chain.wait.for_receipt(txn_hash)

    # Take注文（買）：投資家
    web3.eth.defaultAccount = _trader
    order_id = bond_exchange.call().latestOrderId() - 1
    _amount_take = 50 # 70の売注文に対して、50のTake
    txn_hash = bond_exchange.transact().executeOrder(
        order_id, _amount_take, True)
    chain.wait.for_receipt(txn_hash)

    agreement_id = bond_exchange.call().latestAgreementIds(order_id) - 1

    # 決済承認：決済業者
    web3.eth.defaultAccount = _agent
    txn_hash = bond_exchange.transact().confirmAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

    # 引き出し：発行体
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_exchange.transact().withdrawAll(bond_token.address)
    chain.wait.for_receipt(txn_hash)

    balance_issuer_exchange = bond_exchange.call().balances(_issuer, bond_token.address)
    balance_issuer_token = bond_token.call().balanceOf(_issuer)
    balance_trader_exchange = bond_exchange.call().balances(_trader, bond_token.address)
    balance_trader_token = bond_token.call().balanceOf(_trader)
    commitment = bond_exchange.call().commitments(_issuer, bond_token.address)

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
def test_withdrawAll_error_2_1(web3, chain, users, bond_exchange):
    _issuer = users['issuer']

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

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
    txn_hash = bond_exchange.transact().withdrawAll(bond_token.address) # エラーになる
    chain.wait.for_receipt(txn_hash)

    balance_exchange = bond_exchange.call().balances(_issuer, bond_token.address)
    balance_token = bond_token.call().balanceOf(_issuer)

    assert balance_exchange == 0
    assert balance_token == deploy_args[2]

# エラー系2-2
# 残高がゼロの場合
# ＜発行体＞新規発行 -> ＜発行体＞デポジット -> 異なるアドレスからの引き出し
def test_withdrawAll_error_2_2(web3, chain, users, bond_exchange):
    _issuer = users['issuer']
    _trader = users['trader']

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_transfer = 100
    txn_hash = bond_token.transact().transfer(
        bond_exchange.address, _amount_transfer)
    chain.wait.for_receipt(txn_hash)

    # 引き出し：異なるアドレス
    web3.eth.defaultAccount = _trader
    txn_hash = bond_exchange.transact().withdrawAll(bond_token.address) # エラーになる
    chain.wait.for_receipt(txn_hash)

    balance_exchange = bond_exchange.call().balances(_issuer, bond_token.address)
    balance_token = bond_token.call().balanceOf(_issuer)

    assert balance_exchange == _amount_transfer
    assert balance_token == deploy_args[2] - _amount_transfer


'''
TEST8_送信（transfer）
'''
# 正常系1
# ＜発行体＞新規発行 -> ＜発行体＞デポジット
#  -> ＜発行体＞送信（投資家向け)
def test_transfer_normal_1(web3, chain, users, bond_exchange):
    _issuer = users['issuer']
    _trader = users['trader']

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_deposit = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_deposit)
    chain.wait.for_receipt(txn_hash)

    # トークン送信：発行体 -> 投資家
    web3.eth.defaultAccount = _issuer
    _amount_transfer = 30 # 100のうち30を送信
    txn_hash = bond_exchange.transact().transfer(
        bond_token.address, _trader, _amount_transfer)
    chain.wait.for_receipt(txn_hash)

    balance_issuer_exchange = bond_exchange.call().balances(_issuer, bond_token.address)
    balance_trader_exchange = bond_exchange.call().balances(_trader, bond_token.address)
    balance_issuer_token = bond_token.call().balanceOf(_issuer)
    balance_trader_token = bond_token.call().balanceOf(_trader)

    assert balance_issuer_exchange == _amount_deposit - _amount_transfer
    assert balance_trader_exchange == 0
    assert balance_issuer_token == deploy_args[2] - _amount_deposit
    assert balance_trader_token == _amount_transfer

# エラー系１
# 入力値の型誤り（_token）
def test_transfer_error_1(web3, chain, users, bond_exchange):
    _issuer = users['issuer']
    _trader = users['trader']

    # 送信：発行体
    web3.eth.defaultAccount = _issuer

    with pytest.raises(TypeError):
        bond_exchange.transact().transfer(1234, _trader, 100)

    with pytest.raises(TypeError):
        bond_exchange.transact().transfer('1234', _trader, 100)

# エラー系2
# 入力値の型誤り（_to）
def test_transfer_error_2(web3, chain, users, bond_exchange):
    _issuer = users['issuer']

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # 送信：発行体
    web3.eth.defaultAccount = _issuer

    with pytest.raises(TypeError):
        bond_exchange.transact().transfer(bond_token.address, 1234, 100)

    with pytest.raises(TypeError):
        bond_exchange.transact().transfer(bond_token.address, '1234', 100)

# エラー系3
# 入力値の型誤り（_value）
def test_transfer_error_3(web3, chain, users, bond_exchange):
    _issuer = users['issuer']
    _trader = users['trader']

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # 送信：発行体
    web3.eth.defaultAccount = _issuer

    with pytest.raises(TypeError):
        bond_exchange.transact().transfer(bond_token.address, _trader, -1)

    with pytest.raises(TypeError):
        bond_exchange.transact().transfer(bond_token.address, _trader, 2**256)

    with pytest.raises(TypeError):
        bond_exchange.transact().transfer(bond_token.address, _trader, '0')

    with pytest.raises(TypeError):
        bond_exchange.transact().transfer(bond_token.address, _trader, 0.1)

# エラー系4
# 残高超過
def test_transfer_error_4(web3, chain, users, bond_exchange):
    _issuer = users['issuer']
    _trader = users['trader']

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_deposit = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_deposit)
    chain.wait.for_receipt(txn_hash)

    # トークン送信：発行体 -> 投資家
    web3.eth.defaultAccount = _issuer
    _amount_transfer = 101
    txn_hash = bond_exchange.transact().transfer(
        bond_token.address, _trader, _amount_transfer) # エラーになる
    chain.wait.for_receipt(txn_hash)

    balance_issuer_exchange = bond_exchange.call().balances(_issuer, bond_token.address)
    balance_trader_exchange = bond_exchange.call().balances(_trader, bond_token.address)
    balance_issuer_token = bond_token.call().balanceOf(_issuer)
    balance_trader_token = bond_token.call().balanceOf(_trader)

    assert balance_issuer_exchange == 0
    assert balance_trader_exchange == 0
    assert balance_issuer_token == deploy_args[2]
    assert balance_trader_token == 0

# エラー系5
# 送信数量がゼロ
def test_transfer_error_5(web3, chain, users, bond_exchange):
    _issuer = users['issuer']
    _trader = users['trader']

    # 新規発行：発行体
    web3.eth.defaultAccount = _issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users)

    # Exchangeへのデポジット：発行体
    web3.eth.defaultAccount = _issuer
    _amount_deposit = 100
    txn_hash = bond_token.transact().transfer(bond_exchange.address, _amount_deposit)
    chain.wait.for_receipt(txn_hash)

    # トークン送信：発行体 -> 投資家
    web3.eth.defaultAccount = _issuer
    _amount_transfer = 0
    txn_hash = bond_exchange.transact().transfer(
        bond_token.address, _trader, _amount_transfer) # エラーになる
    chain.wait.for_receipt(txn_hash)

    balance_issuer_exchange = bond_exchange.call().balances(_issuer, bond_token.address)
    balance_trader_exchange = bond_exchange.call().balances(_trader, bond_token.address)
    balance_issuer_token = bond_token.call().balanceOf(_issuer)
    balance_trader_token = bond_token.call().balanceOf(_trader)

    assert balance_issuer_exchange == 0
    assert balance_trader_exchange == 0
    assert balance_issuer_token == deploy_args[2]
    assert balance_trader_token == 0
