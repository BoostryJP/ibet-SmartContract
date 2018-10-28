import pytest
from eth_utils import to_checksum_address

'''
共通処理
'''
def init_args(exchange_address):
    name = 'test_membership'
    symbol = 'MEM'
    initial_supply = 10000
    tradable_exchange = exchange_address
    details = 'some_details'
    return_details = 'some_return'
    expiration_date = '20191231'
    memo = 'some_memo'
    transferable = True

    deploy_args = [
        name, symbol, initial_supply, tradable_exchange,
        details, return_details,
        expiration_date, memo, transferable
    ]
    return deploy_args

def deploy(chain, deploy_args):
    membership_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetMembership',
        deploy_args = deploy_args
    )
    return membership_contract

# deposit
def deposit(web3, chain, token, exchange, account, amount):
    web3.eth.defaultAccount = account
    txn_hash = token.transact().transfer(exchange.address, amount)
    chain.wait.for_receipt(txn_hash)

# make order
def make_order(web3, chain, token, exchange, account,
    amount, price, isBuy, agent):
    web3.eth.defaultAccount = account
    txn_hash = exchange.transact().createOrder(
        token.address, amount, price, isBuy, agent)
    chain.wait.for_receipt(txn_hash)

# take order
def take_order(web3, chain, token, exchange, account,
    order_id, amount, isBuy):
    web3.eth.defaultAccount = account
    txn_hash = exchange.transact().executeOrder(
        order_id, amount, isBuy)
    chain.wait.for_receipt(txn_hash)

# settlement
def settlement(web3, chain, token, exchange, account,
    order_id, agreement_id):
    web3.eth.defaultAccount = account
    txn_hash = exchange.transact().confirmAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

# settlement_ng
def settlement_ng(web3, chain, token, exchange, account,
    order_id, agreement_id):
    web3.eth.defaultAccount = account
    txn_hash = exchange.transact().cancelAgreement(
        order_id, agreement_id)
    chain.wait.for_receipt(txn_hash)

'''
TEST1_デプロイ
'''
# 正常系1: Deploy　→　正常
def test_deploy_normal_1(users, membership_exchange):
    owner = membership_exchange.call().owner()
    assert owner == users['admin']

'''
TEST2_Make注文（createOrder）
'''
# 正常系１
#   ＜発行体＞新規発行 -> ＜投資家＞Make注文（買）
def test_createorder_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    _amount = 100
    _price = 123
    _isBuy = True
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, _amount, _price, _isBuy, agent
    )

    order_id = membership_exchange.call().latestOrderId() - 1
    orderbook = membership_exchange.call().orderBook(order_id)

    assert orderbook == [
        trader, to_checksum_address(membership_token.address),
        _amount, _price, _isBuy, agent, False
    ]
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0

# 正常系2
#   ＜発行体＞新規発行 -> ＜発行体＞Make注文（売）
def test_createorder_normal_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    _amount = 100
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, _amount
    )

    # Make注文（売）
    _price = 123
    _isBuy = False
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, _amount, _price, _isBuy, agent
    )

    order_id = membership_exchange.call().latestOrderId() - 1
    orderbook = membership_exchange.call().orderBook(order_id)
    issuer_commitment = membership_exchange.call().\
        commitments(issuer, membership_token.address)
    issuer_balance = membership_token.call().balanceOf(issuer)

    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        _amount, _price, _isBuy, agent, False
    ]
    assert issuer_balance == deploy_args[2] - _amount
    assert issuer_commitment == _amount

# 正常系3-1
#   限界値（買注文）
def test_createorder_normal_3_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2**256 - 1
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    _amount = 2**256 - 1
    _price = 123
    _isBuy = True
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, _amount, _price, _isBuy, agent
    )

    order_id = membership_exchange.call().latestOrderId() - 1
    orderbook = membership_exchange.call().orderBook(order_id)

    assert orderbook == [
        trader, to_checksum_address(membership_token.address),
        _amount, _price, _isBuy, agent, False
    ]
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0

# 正常系3-2
#   限界値（売注文）
def test_createorder_normal_3_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2**256 - 1
    membership_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    _amount = 2**256 - 1
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, _amount
    )

    # Make注文（売）
    _price = 2**256 - 1
    _isBuy = False
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, _amount, _price, _isBuy, agent
    )

    order_id = membership_exchange.call().latestOrderId() - 1
    orderbook = membership_exchange.call().orderBook(order_id)
    issuer_commitment = membership_exchange.call().\
        commitments(issuer, membership_token.address)
    issuer_balance = membership_token.call().balanceOf(issuer)

    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        _amount, _price, _isBuy, agent, False
    ]
    assert issuer_balance == deploy_args[2] - _amount
    assert issuer_commitment == _amount

# エラー系1
#   入力値の型誤り（_token）
def test_createorder_error_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # Make注文
    _price = 123
    _isBuy = False
    _amount = 100

    with pytest.raises(TypeError):
        membership_exchange.transact().createOrder('1234', _amount, _price, _isBuy, agent)

    with pytest.raises(TypeError):
        membership_exchange.transact().createOrder(1234, _amount, _price, _isBuy, agent)

# エラー系2
#   入力値の型誤り（_amount）
def test_createorder_error_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文
    web3.eth.defaultAccount = issuer
    _price = 123
    _isBuy = False

    with pytest.raises(TypeError):
        membership_exchange.transact().createOrder(
            membership_token.address, -1, _price, _isBuy, agent)

    with pytest.raises(TypeError):
        membership_exchange.transact().createOrder(
            membership_token.address, 2**256, _price, _isBuy, agent)

    with pytest.raises(TypeError):
        membership_exchange.transact().createOrder(
            membership_token.address, '0', _price, _isBuy, agent)

    with pytest.raises(TypeError):
        membership_exchange.transact().createOrder(
            membership_token.address, 0.1, _price, _isBuy, agent)

# エラー系3
#   入力値の型誤り（_price）
def test_createorder_error_3(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文
    web3.eth.defaultAccount = issuer
    _amount = 100
    _isBuy = False

    with pytest.raises(TypeError):
        membership_exchange.transact().createOrder(
            membership_token.address, _amount, -1, _isBuy, agent)

    with pytest.raises(TypeError):
        membership_exchange.transact().createOrder(
            membership_token.address, _amount, 2**256, _isBuy, agent)

    with pytest.raises(TypeError):
        membership_exchange.transact().createOrder(
            membership_token.address, _amount, '0', _isBuy, agent)

    with pytest.raises(TypeError):
        membership_exchange.transact().createOrder(
            membership_token.address, _amount, 0.1, _isBuy, agent)

# エラー系4
#   入力値の型誤り（_isBuy）
def test_createorder_error_4(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123

    with pytest.raises(TypeError):
        membership_exchange.transact().createOrder(
            membership_token.address, _amount, _price, 1234, agent)

    with pytest.raises(TypeError):
        membership_exchange.transact().createOrder(
            membership_token.address, _amount, _price, 'True', agent)

# エラー系5
#   入力値の型誤り（_agent）
def test_createorder_error_5(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文
    web3.eth.defaultAccount = issuer
    _price = 123
    _isBuy = False
    _amount = 100

    with pytest.raises(TypeError):
        membership_exchange.transact().createOrder(
            membership_token.address, _amount, _price, _isBuy, '1234')

    with pytest.raises(TypeError):
        membership_exchange.transact().createOrder(
            membership_token.address, _amount, _price, _isBuy, 1234)

# エラー系6-1
#   買注文に対するチェック
#   1) 注文数量が0の場合
def test_createorder_error_6_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）：エラー
    order_id_before = membership_exchange.call().latestOrderId()
    _amount = 0
    _price = 123
    _isBuy = True
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, _amount, _price, _isBuy, agent
    ) # エラーになる
    order_id_after = membership_exchange.call().latestOrderId()

    trader_commitment = membership_exchange.call().\
        commitments(trader, membership_token.address)
    assert trader_commitment == 0
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0
    assert order_id_before == order_id_after

# エラー系6-2
#   買注文に対するチェック
#   2) 取扱ステータスがFalseの場合
def test_createorder_error_6_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # 取扱ステータス更新
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(
        membership_token.transact().setStatus(False)
    )

    # Make注文（買）：エラー
    order_id_before = membership_exchange.call().latestOrderId()
    _amount = 0
    _price = 123
    _isBuy = True
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, _amount, _price, _isBuy, agent
    ) # エラーになる
    order_id_after = membership_exchange.call().latestOrderId()

    trader_commitment = membership_exchange.call().\
        commitments(trader, membership_token.address)
    assert trader_commitment == 0
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0
    assert order_id_before == order_id_after

# エラー系7-1
#   売注文に対するチェック
#   1) 注文数量が0の場合
def test_createorder_error_7_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    _amount = 100
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, _amount
    )

    # Make注文（売）：エラー
    web3.eth.defaultAccount = issuer
    _amount = 0
    _price = 123
    _isBuy = False
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, _amount, _price, _isBuy, agent
    ) # エラーになる

    issuer_commitment = membership_exchange.call().\
        commitments(issuer, membership_token.address)
    assert issuer_commitment == 0
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]

# エラー系7-2
#   売注文に対するチェック
#   2) 残高数量が発注数量に満たない場合
def test_createorder_error_7_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    _amount = 100
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, _amount
    )

    # Make注文（売）：エラー
    web3.eth.defaultAccount = issuer
    _amount = 101
    _price = 123
    _isBuy = False
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, _amount, _price, _isBuy, agent
    ) # エラーになる

    issuer_commitment = membership_exchange.call().\
        commitments(issuer, membership_token.address)
    assert issuer_commitment == 0
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]

# エラー系7-3
#   売注文に対するチェック
#   3) 取扱ステータスがFalseの場合
def test_createorder_error_7_3(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    _amount = 100
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, _amount
    )

    # 取扱ステータス更新
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(
        membership_token.transact().setStatus(False)
    )

    # Make注文（売）：エラー
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    _isBuy = False
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, _amount, _price, _isBuy, agent
    ) # エラーになる

    issuer_commitment = membership_exchange.call().\
        commitments(issuer, membership_token.address)
    assert issuer_commitment == 0
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]

'''
TEST3_注文キャンセル（cancelOrder）
'''
# 正常系１
#   ＜発行体＞新規発行 -> ＜投資家＞Make注文（買）
#       -> ＜投資家＞注文キャンセル
def test_cancelorder_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    _amount = 100
    _price = 123
    _isBuy = True
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, _amount, _price, _isBuy, agent
    )

    # 注文キャンセル
    order_id = membership_exchange.call().latestOrderId() - 1
    chain.wait.for_receipt(
        membership_exchange.transact().cancelOrder(order_id)
    )

    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        trader, to_checksum_address(membership_token.address),
        _amount, _price, _isBuy, agent, True
    ]
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0

# 正常系2
#   ＜発行体＞新規発行 -> ＜発行体＞Make注文（売）
#       -> ＜発行体＞注文キャンセル
def test_cancelorder_normal_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    _amount = 100
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, _amount
    )

    # Make注文（売）
    _amount = 100
    _price = 123
    _isBuy = False
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, _amount, _price, _isBuy, agent
    )

    # 注文キャンセル
    order_id = membership_exchange.call().latestOrderId() - 1
    chain.wait.for_receipt(
        membership_exchange.transact().cancelOrder(order_id)
    )

    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        _amount, _price, _isBuy, agent, True
    ]
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 0

# 正常系3-1
#   限界値（買注文）
def test_cancelorder_normal_3_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2**256 - 1
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    _amount = 2**256 - 1
    _price = 123
    _isBuy = True
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, _amount, _price, _isBuy, agent
    )

    # 注文キャンセル
    order_id = membership_exchange.call().latestOrderId() - 1
    chain.wait.for_receipt(
        membership_exchange.transact().cancelOrder(order_id)
    )

    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        trader, to_checksum_address(membership_token.address),
        _amount, _price, _isBuy, agent, True
    ]
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]

# 正常系3-2
#   限界値（売注文）
def test_cancelorder_normal_3_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2**256 - 1
    membership_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    _amount = 2**256 - 1
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, _amount
    )

    # Make注文（売）
    _price = 2**256 - 1
    _isBuy = False
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, _amount, _price, _isBuy, agent
    )

    # 注文キャンセル
    order_id = membership_exchange.call().latestOrderId() - 1
    chain.wait.for_receipt(
        membership_exchange.transact().cancelOrder(order_id)
    )

    orderbook = membership_exchange.call().orderBook(order_id)
    issuer_commitment = membership_exchange.call().\
        commitments(issuer, membership_token.address)
    issuer_balance = membership_token.call().balanceOf(issuer)

    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        _amount, _price, _isBuy, agent, True
    ]
    assert issuer_balance == deploy_args[2]
    assert issuer_commitment == 0

# エラー系1
#   入力値の型誤り（_orderId）
def test_cancelorder_error_1(web3, users, membership_exchange):
    issuer = users['issuer']

    # 注文キャンセル
    web3.eth.defaultAccount = issuer

    with pytest.raises(TypeError):
        membership_exchange.transact().cancelOrder(-1)

    with pytest.raises(TypeError):
        membership_exchange.transact().cancelOrder(2**256)

    with pytest.raises(TypeError):
        membership_exchange.transact().cancelOrder('0')

    with pytest.raises(TypeError):
        membership_exchange.transact().cancelOrder(0.1)

# エラー系2
#   指定した注文番号が、直近の注文ID以上の場合
def test_cancelorder_error_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    _amount = 100
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, _amount
    )

    # Make注文（売）
    _amount = 100
    _price = 123
    _isBuy = False
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, _amount, _price, _isBuy, agent
    )

    # 注文キャンセル：エラー
    wrong_order_id = membership_exchange.call().\
        latestOrderId() # 誤った order_id
    correct_order_id = membership_exchange.call().\
        latestOrderId() - 1 # 正しい order_id
    chain.wait.for_receipt(
        membership_exchange.transact().cancelOrder(wrong_order_id)
    ) # エラーになる

    orderbook = membership_exchange.call().orderBook(correct_order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        _amount, _price, _isBuy, agent, False
    ]
    assert membership_token.call().balanceOf(issuer) == \
        deploy_args[2] - _amount
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == _amount

# エラー系3-1
#   1) 元注文の残注文数量が0の場合
def test_cancelorder_error_3_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, 100, 123, True, agent
    )

    # Take注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, order_id, 100, False
    )

    # 決済承認
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, agreement_id
    )

    # 注文キャンセル：エラー
    chain.wait.for_receipt(
        membership_exchange.transact().cancelOrder(order_id)
    ) # エラーになる

    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        trader, to_checksum_address(membership_token.address),
        0, 123, True, agent, False
    ]
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert membership_token.call().balanceOf(trader) == 100

# エラー系3-2
#   2) 注文がキャンセル済みの場合
def test_cancelorder_error_3_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, 100, 123, True, agent
    )

    # 注文キャンセル１回目：正常
    web3.eth.defaultAccount = trader
    order_id = membership_exchange.call().latestOrderId() - 1
    chain.wait.for_receipt(
        membership_exchange.transact().cancelOrder(order_id)
    )

    # 注文キャンセル２回目：エラー
    chain.wait.for_receipt(
        membership_exchange.transact().cancelOrder(order_id)
    ) # エラーになる

    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        trader, to_checksum_address(membership_token.address),
        100, 123, True, agent, True
    ]
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0

# エラー系3-3-1
#   3) 元注文の発注者と、注文キャンセルの実施者が異なる場合
#   ※買注文の場合
def test_cancelorder_error_3_3_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, 100, 123, True, agent
    )

    # 注文キャンセル：エラー
    web3.eth.defaultAccount = issuer # 注文実施者と異なる
    order_id = membership_exchange.call().latestOrderId() - 1
    chain.wait.for_receipt(
        membership_exchange.transact().cancelOrder(order_id)
    ) # エラーになる

    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        trader, to_checksum_address(membership_token.address),
        100, 123, True, agent, False
    ]
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0

# エラー系3-3-2
#   3) 元注文の発注者と、注文キャンセルの実施者が異なる場合
#   ※売注文の場合
def test_cancelorder_error_3_3_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )

    # Make注文（売）
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # 注文キャンセル：エラー
    web3.eth.defaultAccount = trader # 注文実施者と異なる
    order_id = membership_exchange.call().latestOrderId() - 1
    chain.wait.for_receipt(
        membership_exchange.transact().cancelOrder(order_id)
    ) # エラーになる

    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        100, 123, False, agent, False
    ]
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 100

'''
TEST4_Take注文（executeOrder）
'''
# 正常系1
#   ＜発行体＞新規発行 -> ＜発行体＞Make注文（売）
#       -> ＜投資家＞Take注文（買）
def test_executeOrder_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 30, True
    )

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 100

    # Assert: agreement
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, False
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 123

# 正常系2
#   ＜発行体＞新規発行 -> ＜投資家＞Make注文（買）
#       -> ＜発行体＞Take注文（売）
def test_executeOrder_normal_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, 100, 123, True, agent
    )

    # Take注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 50
    )
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, order_id, 30, False
    )

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        trader, to_checksum_address(membership_token.address),
        70, 123, True, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 50
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 30

    # Assert: agreement
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        issuer, 30, 123, False, False
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 123

# 正常系3-1
#   限界値（買注文）
def test_executeOrder_normal_3_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2**256 - 1
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 2**256 - 1
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 2**256 - 1, 2**256 - 1, False, agent
    )

    # Take注文（買）
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 2**256 - 1, True
    )

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        0, 2**256 - 1, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == 0
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 2**256 - 1

    # Assert: agreement
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 2**256 - 1, 2**256 - 1, False, False
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 2**256 - 1

# 正常系3-2
#   限界値（売注文）
def test_executeOrder_normal_3_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2**256 - 1
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, 2**256 - 1, 2**256 - 1, True, agent
    )

    # Take注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 2**256 - 1
    )
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, order_id, 2**256 - 1, False
    )

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        trader, to_checksum_address(membership_token.address),
        0, 2**256 - 1, True, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == 0
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 2**256 - 1

    # Assert: agreement
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        issuer, 2**256 - 1, 2**256 - 1, False, False
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 2**256 - 1

# エラー系1
#   入力値の型誤り（orderId）
def test_executeOrder_error_1(web3, users, membership_exchange):
    trader = users['trader']

    web3.eth.defaultAccount = trader
    amount = 50
    is_buy = True

    with pytest.raises(TypeError):
        membership_exchange.transact().executeOrder(-1, amount, is_buy)

    with pytest.raises(TypeError):
        membership_exchange.transact().executeOrder(2**256, amount, is_buy)

    with pytest.raises(TypeError):
        membership_exchange.transact().executeOrder('0', amount, is_buy)

    with pytest.raises(TypeError):
        membership_exchange.transact().executeOrder(0.1, amount, is_buy)

# エラー系2
#   入力値の型誤り（amount）
def test_executeOrder_error_2(web3, users, membership_exchange):
    trader = users['trader']

    web3.eth.defaultAccount = trader
    order_id = 1000
    is_buy = True

    with pytest.raises(TypeError):
        membership_exchange.transact().executeOrder(order_id, -1, is_buy)

    with pytest.raises(TypeError):
        membership_exchange.transact().executeOrder(order_id, 2**256, is_buy)

    with pytest.raises(TypeError):
        membership_exchange.transact().executeOrder(order_id, '0', is_buy)

    with pytest.raises(TypeError):
        membership_exchange.transact().executeOrder(order_id, 0.1, is_buy)

# エラー系3
#   入力値の型誤り（isBuy）
def test_executeOrder_error_3(web3, users, membership_exchange):
    trader = users['trader']

    web3.eth.defaultAccount = trader
    order_id = 1000
    amount = 123

    with pytest.raises(TypeError):
        membership_exchange.transact().executeOrder(order_id, amount, 'True')

    with pytest.raises(TypeError):
        membership_exchange.transact().executeOrder(order_id, amount, 111)

# エラー系4
#   指定した注文IDが直近の注文IDを超えている場合
def test_executeOrder_error_4(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）：エラー
    wrong_order_id = membership_exchange.call().latestOrderId() # 誤ったID
    correct_order_id = membership_exchange.call().latestOrderId() - 1 # 正しいID
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, wrong_order_id, 30, True
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(correct_order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        100, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 100

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 0

# エラー系5-1
#   Take買注文
#   1) 注文数量が0の場合
def test_executeOrder_error_5_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）：エラー
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 0, True # 注文数量が0
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        100, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 100

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 0

# エラー系5-2
#   Take買注文
#   2) 元注文と、発注する注文が同一の売買区分の場合
def test_executeOrder_error_5_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, True, agent
    )

    # Take注文（買）：エラー
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 30, True # 同一売買区分
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        100, 123, True, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 0

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 0

# エラー系5-3
#   Take買注文
#   3) 元注文の発注者と同一のアドレスからの発注の場合
def test_executeOrder_error_5_3(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）：エラー
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, order_id, 30, True # 同一アドレスからの発注
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        100, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 100

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 0

# エラー系5-4
#   Take買注文
#   4) 元注文がキャンセル済の場合
def test_executeOrder_error_5_4(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Make注文のキャンセル
    web3.eth.defaultAccount = issuer
    order_id = membership_exchange.call().latestOrderId() - 1
    chain.wait.for_receipt(
        membership_exchange.transact().cancelOrder(order_id)
    )

    # Take注文（買）：エラー
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 30, True
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        100, 123, False, agent, True
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 0

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 0

# エラー系5-5
#   Take買注文
#   5) 取扱ステータスがFalseの場合
def test_executeOrder_error_5_5(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # 取扱ステータス更新（Falseへ更新）
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(
        membership_token.transact().setStatus(False)
    )

    # Take注文（買）：エラー
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 30, True
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        100, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 100

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 0

# エラー系5-6
#   Take買注文
#   6) 数量が元注文の残数量を超過している場合
def test_executeOrder_error_5_6(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）：エラー
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 101, True # Make注文の数量を超過
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        100, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 100

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 0

# エラー系6-1
#   Take売注文
#   1) 注文数量が0の場合
def test_executeOrder_error_6_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, 100, 123, True, agent
    )

    # Take注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 50
    )
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, order_id, 0, False # 注文数量が0
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        trader, to_checksum_address(membership_token.address),
        100, 123, True, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 0

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 0

# エラー系6-2
#   Take売注文
#   2) 元注文と、発注する注文が同一の売買区分の場合
def test_executeOrder_error_6_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（売）：エラー
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 30, False # 同一売買区分
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        100, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 100

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 0

# エラー系6-3
#   Take売注文
#   3) 元注文の発注者と同一のアドレスからの発注の場合
def test_executeOrder_error_6_3(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, True, agent
    )

    # Take注文（売）：エラー
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 50
    )
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, order_id, 30, False # Make注文と同一アドレスからの発注
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        100, 123, True, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 0

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 0

# エラー系6-4
#   Take売注文
#   4) 元注文がキャンセル済の場合
def test_executeOrder_error_6_4(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, 100, 123, True, agent
    )

    # Make注文のキャンセル
    web3.eth.defaultAccount = trader
    order_id = membership_exchange.call().latestOrderId() - 1
    chain.wait.for_receipt(
        membership_exchange.transact().cancelOrder(order_id)
    )

    # Take注文（売）：エラー
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 50
    )
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, order_id, 30, False
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        trader, to_checksum_address(membership_token.address),
        100, 123, True, agent, True
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 0

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 0

# エラー系6-5
#   Take売注文
#   5) 取扱ステータスがFalseの場合
def test_executeOrder_error_6_5(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, 100, 123, True, agent
    )

    # 取扱ステータス更新（Falseへ更新）
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(
        membership_token.transact().setStatus(False)
    )

    # Take注文（売）：エラー
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 50
    )
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, order_id, 30, False
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        trader, to_checksum_address(membership_token.address),
        100, 123, True, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 0

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 0

# エラー系6-6
#   Take売注文
#   6) 発注者の残高が発注数量を下回っている場合
def test_executeOrder_error_6_6(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, 100, 123, True, agent
    )

    # Take注文（売）：エラー
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 50
    )
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, order_id, 51, False # balanceを超える注文数量
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        trader, to_checksum_address(membership_token.address),
        100, 123, True, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 0

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 0

# エラー系6-7
#   Take売注文
#   7) 数量が元注文の残数量を超過している場合
def test_executeOrder_error_6_7(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, 100, 123, True, agent
    )

    # Take注文（売）：エラー
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 101
    )
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, order_id, 101, False
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        trader, to_checksum_address(membership_token.address),
        100, 123, True, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 0

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 0

'''
TEST5_決済承認（confirmAgreement）
'''
# 正常系1
#   Make売、Take買
#       ＜発行体＞新規発行 -> ＜発行体＞Make注文（売）
#           -> ＜投資家＞Take注文（買） -> ＜決済業者＞決済処理
def test_confirmAgreement_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 30, True
    )

    # 決済処理
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, agreement_id
    )

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert membership_token.call().balanceOf(trader) == 30

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 70

    # Assert: agreement
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, True
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 123

# 正常系2
#   Make買、Take売
#       ＜発行体＞新規発行 -> ＜投資家＞Make注文（買）
#           -> ＜発行体＞Take注文（売） -> ＜決済業者＞決済処理
def test_confirmAgreement_normal_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, 100, 123, True, agent
    )

    # Take注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 50
    )
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, order_id, 30, False
    )

    # 決済処理
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, agreement_id
    )

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        trader, to_checksum_address(membership_token.address),
        70, 123, True, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 50
    assert membership_token.call().balanceOf(trader) == 30

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 0

    # Assert: agreement
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        issuer, 30, 123, False, True
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 123

# 正常系3-1
#   Make売、Take買
#   限界値
def test_confirmAgreement_normal_3_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2**256 - 1 #上限値
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 2**256 - 1
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 2**256 - 1, 2**256 - 1, False, agent
    )

    # Take注文（買）
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 2**256 - 1, True
    )

    # 決済処理
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, agreement_id
    )

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        0, 2**256 - 1, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == 0
    assert membership_token.call().balanceOf(trader) == 2**256 - 1

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 0

    # Assert: agreement
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 2**256 - 1, 2**256 - 1, False, True
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 2**256 - 1

# 正常系3-2
#   Make買、Take売
#   限界値
def test_confirmAgreement_normal_3_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2**256 - 1 #上限値
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, 2**256 - 1, 2**256 - 1, True, agent
    )

    # Take注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 2**256 - 1
    )
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, order_id, 2**256 - 1, False
    )

    # 決済処理
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, agreement_id
    )

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        trader, to_checksum_address(membership_token.address),
        0, 2**256 - 1, True, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == 0
    assert membership_token.call().balanceOf(trader) == 2**256 - 1

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 0

    # Assert: agreement
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        issuer, 2**256 - 1, 2**256 - 1, False, True
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 2**256 - 1

# エラー系1
#   入力値の型誤り（orderId）
def test_confirmAgreement_error_1(web3, users, membership_exchange):
    agent = users['agent']

    # 決済承認：決済業者
    web3.eth.defaultAccount = agent

    with pytest.raises(TypeError):
        membership_exchange.transact().confirmAgreement(-1,0)

    with pytest.raises(TypeError):
        membership_exchange.transact().confirmAgreement(2**256,0)

    with pytest.raises(TypeError):
        membership_exchange.transact().confirmAgreement('0',0)

    with pytest.raises(TypeError):
        membership_exchange.transact().confirmAgreement(0.1,0)

# エラー系2
#   入力値の型誤り（agreementId）
def test_confirmAgreement_error_2(web3, users, membership_exchange):
    agent = users['agent']

    # 決済承認：決済業者
    web3.eth.defaultAccount = agent

    with pytest.raises(TypeError):
        membership_exchange.transact().confirmAgreement(0,-1)

    with pytest.raises(TypeError):
        membership_exchange.transact().confirmAgreement(0,2**256)

    with pytest.raises(TypeError):
        membership_exchange.transact().confirmAgreement(0,'0')

    with pytest.raises(TypeError):
        membership_exchange.transact().confirmAgreement(0,0.1)

# エラー系3
#   指定した注文番号が、直近の注文ID以上の場合
def test_confirmAgreement_error_3(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 30, True
    )

    # 決済処理：エラー
    wrong_order_id = membership_exchange.call().latestOrderId() # 誤ったID
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement(
        web3, chain,
        membership_token, membership_exchange,
        agent, wrong_order_id, agreement_id
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 100

    # Assert: agreement
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, False
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 123

# エラー系4
#   指定した約定IDが、直近の約定ID以上の場合
def test_confirmAgreement_error_4(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 30, True
    )

    # 決済処理：エラー
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    wrong_agreement_id = membership_exchange.call().\
        latestAgreementIds(order_id) # 誤ったID
    settlement(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, wrong_agreement_id
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 100

    # Assert: agreement
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, False
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 123

# エラー系5
#   すでに決済承認済み（支払い済み）の場合
def test_confirmAgreement_error_5(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 30, True
    )

    # 決済処理1回目
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, agreement_id
    )

    # 決済処理２回目：エラー
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, agreement_id
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert membership_token.call().balanceOf(trader) == 30

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 70

    # Assert: agreement
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, True
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 123

# エラー系6
#   すでに決済非承認済み（キャンセル済み）の場合
def test_confirmAgreement_error_6(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 30, True
    )

    # 決済非承認
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement_ng(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, agreement_id
    )

    # 決済処理：エラー
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, agreement_id
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 70
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 70

    # Assert: agreement
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, True, False
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 123

# エラー系7
#   元注文で指定した決済業者ではない場合
def test_confirmAgreement_error_7(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 30, True
    )

    # 決済処理：エラー
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, agreement_id # 元注文で指定した決済業者ではない
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 100

    # Assert: agreement
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, False
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 123

'''
TEST6_決済非承認（cancelAgreement）
'''
# 正常系1
#   Make売、Take買
#       ＜発行体＞新規発行 -> ＜発行体＞Make注文（売）
#           -> ＜投資家＞Take注文（買） -> ＜決済業者＞決済非承認
def test_cancelAgreement_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 30, True
    )

    # 決済非承認
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement_ng(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, agreement_id
    )

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 70
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 70

    # Assert: agreement
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, True, False
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 123

# 正常系2
#   Make買、Take売
#       ＜発行体＞新規発行 -> ＜投資家＞Make注文（買）
#           -> ＜発行体＞Take注文（売） -> ＜決済業者＞決済非承認
def test_cancelAgreement_normal_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, 100, 123, True, agent
    )

    # Take注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 50
    )
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, order_id, 30, False
    )

    # 決済非承認
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement_ng(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, agreement_id
    )

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        trader, to_checksum_address(membership_token.address),
        70, 123, True, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 20
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 0

    # Assert: agreement
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        issuer, 30, 123, True, False
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 123

# 正常系3-1
#   Make売、Take買
#   限界値
def test_cancelAgreement_normal_3_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2**256 - 1 #上限値
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 2**256 - 1
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 2**256 - 1, 2**256 - 1, False, agent
    )

    # Take注文（買）
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 2**256 - 1, True
    )

    # 決済非承認
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement_ng(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, agreement_id
    )

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        0, 2**256 - 1, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 0

    # Assert: agreement
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 2**256 - 1, 2**256 - 1, True, False
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 2**256 - 1

# 正常系3-2
#   Make買、Take売
#   限界値
def test_cancelAgreement_normal_3_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2**256 - 1 #上限値
    membership_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, 2**256 - 1, 2**256 - 1, True, agent
    )

    # Take注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 2**256 - 1
    )
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, order_id, 2**256 - 1, False
    )

    # 決済非承認
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement_ng(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, agreement_id
    )

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        trader, to_checksum_address(membership_token.address),
        0, 2**256 - 1, True, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 0

    # Assert: agreement
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        issuer, 2**256 - 1, 2**256 - 1, True, False
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 2**256 - 1

# エラー系1
#   入力値の型誤り（orderId）
def test_cancelAgreement_error_1(web3, users, membership_exchange):
    agent = users['agent']

    # 決済非承認：決済業者
    web3.eth.defaultAccount = agent

    with pytest.raises(TypeError):
        membership_exchange.transact().cancelAgreement(-1, 0)

    with pytest.raises(TypeError):
        membership_exchange.transact().cancelAgreement(2**256, 0)

    with pytest.raises(TypeError):
        membership_exchange.transact().cancelAgreement('0', 0)

    with pytest.raises(TypeError):
        membership_exchange.transact().cancelAgreement(0.1, 0)

# エラー系2
#   入力値の型誤り（_agreementId）
def test_cancelAgreement_error_2(web3, users, membership_exchange):
    _agent = users['agent']

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent

    with pytest.raises(TypeError):
        membership_exchange.transact().cancelAgreement(0, -1)

    with pytest.raises(TypeError):
        membership_exchange.transact().cancelAgreement(0, 2**256)

    with pytest.raises(TypeError):
        membership_exchange.transact().cancelAgreement(0, '0')

    with pytest.raises(TypeError):
        membership_exchange.transact().cancelAgreement(0, 0.1)

# エラー系3
#   指定した注文番号が、直近の注文ID以上の場合
def test_cancelAgreement_error_3(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 30, True
    )

    # 決済非承認：エラー
    wrong_order_id = membership_exchange.call().latestOrderId() # 誤ったID
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement_ng(
        web3, chain,
        membership_token, membership_exchange,
        agent, wrong_order_id, agreement_id
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 100

    # Assert: agreement
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, False
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 123

# エラー系4
#   指定した約定IDが、直近の約定ID以上の場合
def test_cancelAgreement_error_4(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 30, True
    )

    # 決済非承認：エラー
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    wrong_agreement_id = membership_exchange.call().\
        latestAgreementIds(order_id) # 誤ったID
    settlement_ng(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, wrong_agreement_id
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 100

    # Assert: agreement
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, False
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 123

# エラー系5
#   すでに決済承認済み（支払い済み）の場合
def test_cancelAgreement_error_5(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 30, True
    )

    # 決済処理
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, agreement_id
    )

    # 決済非承認：エラー
    settlement_ng(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, agreement_id
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert membership_token.call().balanceOf(trader) == 30

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 70

    # Assert: agreement
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, True
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 123

# エラー系6
#   すでに決済非承認済み（キャンセル済み）の場合
def test_cancelAgreement_error_6(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 30, True
    )

    # 決済非承認１回目
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement_ng(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, agreement_id
    )

    # 決済非承認２回目：エラー
    settlement_ng(
        web3, chain,
        membership_token, membership_exchange,
        agent, order_id, agreement_id
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 70
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 70

    # Assert: agreement
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, True, False
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 123

# エラー系7
#   元注文で指定した決済業者ではない場合
def test_cancelAgreement_error_7(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = membership_exchange.call().latestOrderId() - 1
    take_order(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, 30, True
    )

    # 決済非承認１回目
    agreement_id = membership_exchange.call().latestAgreementIds(order_id) - 1
    settlement_ng(
        web3, chain,
        membership_token, membership_exchange,
        trader, order_id, agreement_id # 元注文で指定した決済業者ではない
    ) # エラーになる

    # Assert: orderbook
    orderbook = membership_exchange.call().orderBook(order_id)
    assert orderbook == [
        issuer, to_checksum_address(membership_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert membership_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 100

    # Assert: agreement
    agreement = membership_exchange.call().agreements(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, False
    ]

    # Assert: last_price
    assert membership_exchange.call().\
        lastPrice(membership_token.address) == 123

'''
TEST7_引き出し（withdrawAll）
'''
# 正常系1
#   ＜発行体＞新規発行 -> ＜発行体＞デポジット
#       -> ＜発行体＞引き出し
def test_withdrawAll_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # デポジット
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )

    # 引き出し
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(
        membership_exchange.transact().withdrawAll(membership_token.address)
    )

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_exchange.call().\
        balances(issuer, membership_token.address) == 0

# 正常系2
#   ＜発行体＞新規発行 -> ＜発行体＞デポジット（２回）
#       -> ＜発行体＞引き出し
def test_withdrawAll_normal_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # デポジット１回目
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )

    # デポジット２回目
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )

    # 引き出し
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(
        membership_exchange.transact().withdrawAll(membership_token.address)
    )

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_exchange.call().\
        balances(issuer, membership_token.address) == 0

# 正常系3
#   ＜発行体＞新規発行 -> ＜発行体＞デポジット
#       -> ＜発行体＞Make売注文（※注文中拘束状態） -> ＜発行体＞引き出し
def test_withdrawAll_normal_3(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # デポジット
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )

    # Make売注文
    make_order(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 70, 123, False, agent
    )

    # 引き出し
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(
        membership_exchange.transact().withdrawAll(membership_token.address)
    )

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 70
    assert membership_exchange.call().\
        balances(issuer, membership_token.address) == 0

    # Assert: commitment
    assert membership_exchange.call().\
        commitments(issuer, membership_token.address) == 70

# 正常系4
#   限界値
def test_withdrawAll_normal_4(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2**256 - 1
    membership_token = deploy(chain, deploy_args)

    # デポジット
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 2**256 - 1
    )

    # 引き出し
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(
        membership_exchange.transact().withdrawAll(membership_token.address)
    )

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_exchange.call().\
        balances(issuer, membership_token.address) == 0

# エラー系１
#   入力値の型誤り（token）
def test_withdrawAll_error_1(web3, users, membership_exchange):
    issuer = users['issuer']

    # 引き出し：発行体
    web3.eth.defaultAccount = issuer

    with pytest.raises(TypeError):
        membership_exchange.transact().withdrawAll(1234)

    with pytest.raises(TypeError):
        membership_exchange.transact().withdrawAll('1234')

# エラー系2
#   残高がゼロの場合
def test_withdrawAll_error_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # 引き出し：エラー
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(
        membership_exchange.transact().withdrawAll(membership_token.address)
    ) # エラーになる

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_exchange.call().\
        balances(issuer, membership_token.address) == 0

'''
TEST8_送信（transfer）
'''
# 正常系1
#   ＜発行体＞新規発行 -> ＜発行体＞デポジット
#       -> ＜発行体＞送信
def test_transfer_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # デポジット
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )

    # 送信
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(
        membership_exchange.transact().\
            transfer(membership_token.address, trader, 30)
    )

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert membership_token.call().balanceOf(trader) == 30
    assert membership_exchange.call().\
        balances(issuer, membership_token.address) == 70

# 正常系2
#   限界値
def test_transfer_normal_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2**256 - 1
    membership_token = deploy(chain, deploy_args)

    # デポジット
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 2**256 - 1
    )

    # 送信
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(
        membership_exchange.transact().\
            transfer(membership_token.address, trader, 2**256 - 1)
    )

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == 0
    assert membership_token.call().balanceOf(trader) == 2**256 - 1
    assert membership_exchange.call().\
        balances(issuer, membership_token.address) == 0

# エラー系１
#   入力値の型誤り（token）
def test_transfer_error_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 送信：発行体
    web3.eth.defaultAccount = issuer

    with pytest.raises(TypeError):
        membership_exchange.transact().transfer(1234, trader, 100)

    with pytest.raises(TypeError):
        membership_exchange.transact().transfer('1234', trader, 100)

# エラー系2
#   入力値の型誤り（to）
def test_transfer_error_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # 送信：発行体
    web3.eth.defaultAccount = issuer

    with pytest.raises(TypeError):
        membership_exchange.transact().\
            transfer(membership_token.address, 1234, 100)

    with pytest.raises(TypeError):
        membership_exchange.transact().\
            transfer(membership_token.address, '1234', 100)

# エラー系3
#   入力値の型誤り（_value）
def test_transfer_error_3(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # 送信：発行体
    web3.eth.defaultAccount = issuer

    with pytest.raises(TypeError):
        membership_exchange.transact().\
            transfer(membership_token.address, trader, -1)

    with pytest.raises(TypeError):
        membership_exchange.transact().\
            transfer(membership_token.address, trader, 2**256)

    with pytest.raises(TypeError):
        membership_exchange.transact().\
            transfer(membership_token.address, trader, '0')

    with pytest.raises(TypeError):
        membership_exchange.transact().\
            transfer(membership_token.address, trader, 0.1)

# エラー系4
#   送信数量が0の場合
def test_transfer_error_4(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # デポジット
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )

    # 送信：エラー
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(
        membership_exchange.transact().\
            transfer(membership_token.address, trader, 0)
    ) # エラーになる

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0
    assert membership_exchange.call().\
        balances(issuer, membership_token.address) == 0

# エラー系5
#   残高数量が送信数量に満たない場合
def test_transfer_error_5(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_token = deploy(chain, deploy_args)

    # デポジット
    deposit(
        web3, chain,
        membership_token, membership_exchange,
        issuer, 100
    )

    # 送信：エラー
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(
        membership_exchange.transact().\
            transfer(membership_token.address, trader, 101)
    ) # エラーになる

    # Assert: balance
    assert membership_token.call().balanceOf(issuer) == deploy_args[2]
    assert membership_token.call().balanceOf(trader) == 0
    assert membership_exchange.call().\
        balances(issuer, membership_token.address) == 0
