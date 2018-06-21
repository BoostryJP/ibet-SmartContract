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
TEST2_新規注文（createOrder）
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

# 正常系２
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

# エラー系１
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
