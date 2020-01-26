import pytest
from eth_utils import to_checksum_address

'''
共通処理
'''


def init_args(exchange_address):
    name = 'test_coupon'
    symbol = 'CPN'
    total_supply = 1000000
    tradable_exchange = exchange_address
    details = 'some_details'
    return_details = 'some_return_details'
    memo = 'some_memo'
    expiration_date = '20201231'
    transferable = True
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'

    deploy_args = [
        name, symbol, total_supply, tradable_exchange,
        details, return_details,
        memo, expiration_date, transferable,
        contact_information, privacy_policy
    ]
    return deploy_args


def deploy(chain, deploy_args):
    coupon_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetCoupon',
        deploy_args=deploy_args
    )
    return coupon_contract


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
TEST0_デプロイ
'''


# 正常系1: Deploy　→　正常
def test_deploy_normal_1(users, coupon_exchange, coupon_exchange_storage,
                         payment_gateway):
    owner = coupon_exchange.call().owner()
    payment_gateway_address = coupon_exchange.call().paymentGatewayAddress()
    storage_address = coupon_exchange.call().storageAddress()

    assert owner == users['admin']
    assert payment_gateway_address == to_checksum_address(payment_gateway.address)
    assert storage_address == to_checksum_address(coupon_exchange_storage.address)


'''
TEST1_クーポントークンのデポジット
'''


# 正常系1
# ＜発行体＞新規発行 -> ＜発行体＞Exchangeへのデポジット
def test_deposit_normal_1(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().allocate(coupon_exchange.address, _value)
    chain.wait.for_receipt(txn_hash)

    balance_coupon = coupon.call().balanceOf(_issuer)
    balance_exchange = coupon_exchange.call().balanceOf(_issuer, coupon.address)

    assert balance_coupon == deploy_args[2] - _value
    assert balance_exchange == _value


'''
TEST2_全ての残高の引き出し（withdrawAll）
'''


# 正常系1
# ＜発行体＞新規発行 -> ＜発行体＞Exchangeへのデポジット
#  -> ＜発行体＞引き出し（withdrawAll）
def test_withdrawAll_normal_1(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().allocate(coupon_exchange.address, _value)
    chain.wait.for_receipt(txn_hash)

    # 引き出し（withdrawAll)
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon_exchange.transact().withdrawAll(coupon.address)
    chain.wait.for_receipt(txn_hash)

    balance_coupon = coupon.call().balanceOf(_issuer)
    balance_exchange = coupon_exchange.call().balanceOf(_issuer, coupon.address)

    assert balance_coupon == deploy_args[2]
    assert balance_exchange == 0


# 正常系2
# ＜発行体＞新規発行 -> ＜発行体＞Exchangeへのデポジット（２回）
#  -> ＜発行体＞引き出し（withdrawAll）
def test_withdrawAll_normal_2(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # Exchangeへのデポジット（１回目）
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().allocate(coupon_exchange.address, _value)
    chain.wait.for_receipt(txn_hash)

    # Exchangeへのデポジット（２回目）
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().allocate(coupon_exchange.address, _value)
    chain.wait.for_receipt(txn_hash)

    # 引き出し（withdrawAll)
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon_exchange.transact().withdrawAll(coupon.address)
    chain.wait.for_receipt(txn_hash)

    balance_coupon = coupon.call().balanceOf(_issuer)
    balance_exchange = coupon_exchange.call().balanceOf(_issuer, coupon.address)

    assert balance_coupon == deploy_args[2]
    assert balance_exchange == 0


# エラー系１：入力値の型誤り
def test_withdrawAll_error_1(web3, users, coupon_exchange):
    _issuer = users['issuer']

    # 引き出し（withdrawAll)
    web3.eth.defaultAccount = _issuer

    with pytest.raises(TypeError):
        coupon_exchange.transact().withdrawAll(1234)

    with pytest.raises(TypeError):
        coupon_exchange.transact().withdrawAll('1234')


# エラー系2-1：残高がゼロ（デポジットなし）
def test_withdrawAll_error_2_1(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 引き出し（withdrawAll)
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon_exchange.transact().withdrawAll(coupon.address)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    balance_coupon = coupon.call().balanceOf(_issuer)
    balance_exchange = coupon_exchange.call().balanceOf(_issuer, coupon.address)

    assert balance_coupon == deploy_args[2]
    assert balance_exchange == 0


'''
TEST3_Make注文（createOrder）
'''


# 正常系１
#   ＜発行体＞新規発行 -> ＜投資家＞Make注文（買）
def test_createorder_normal_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    _amount = 100
    _price = 123
    _isBuy = True
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, _amount, _price, _isBuy, agent
    )

    order_id = coupon_exchange.call().latestOrderId()
    orderbook = coupon_exchange.call().getOrder(order_id)

    assert orderbook == [
        trader, to_checksum_address(coupon_token.address),
        _amount, _price, _isBuy, agent, False
    ]
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_token.call().balanceOf(trader) == 0


# 正常系2
#   ＜発行体＞新規発行 -> ＜発行体＞Make注文（売）
def test_createorder_normal_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    _amount = 100
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, _amount
    )

    # Make注文（売）
    _price = 123
    _isBuy = False
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, _amount, _price, _isBuy, agent
    )

    order_id = coupon_exchange.call().latestOrderId()
    orderbook = coupon_exchange.call().getOrder(order_id)
    issuer_commitment = coupon_exchange.call(). \
        commitmentOf(issuer, coupon_token.address)
    issuer_balance = coupon_token.call().balanceOf(issuer)

    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        _amount, _price, _isBuy, agent, False
    ]
    assert issuer_balance == deploy_args[2] - _amount
    assert issuer_commitment == _amount


# 正常系3-1
#   限界値（買注文）
def test_createorder_normal_3_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[2] = 2 ** 256 - 1
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    _amount = 2 ** 256 - 1
    _price = 123
    _isBuy = True
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, _amount, _price, _isBuy, agent
    )

    order_id = coupon_exchange.call().latestOrderId()
    orderbook = coupon_exchange.call().getOrder(order_id)

    assert orderbook == [
        trader, to_checksum_address(coupon_token.address),
        _amount, _price, _isBuy, agent, False
    ]
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_token.call().balanceOf(trader) == 0


# 正常系3-2
#   限界値（売注文）
def test_createorder_normal_3_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[2] = 2 ** 256 - 1
    coupon_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    _amount = 2 ** 256 - 1
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, _amount
    )

    # Make注文（売）
    _price = 2 ** 256 - 1
    _isBuy = False
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, _amount, _price, _isBuy, agent
    )

    order_id = coupon_exchange.call().latestOrderId()
    orderbook = coupon_exchange.call().getOrder(order_id)
    issuer_commitment = coupon_exchange.call(). \
        commitmentOf(issuer, coupon_token.address)
    issuer_balance = coupon_token.call().balanceOf(issuer)

    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        _amount, _price, _isBuy, agent, False
    ]
    assert issuer_balance == deploy_args[2] - _amount
    assert issuer_commitment == _amount


# エラー系1
#   入力値の型誤り（_token）
def test_createorder_error_1(web3, users, coupon_exchange):
    agent = users['agent']

    # Make注文
    _price = 123
    _isBuy = False
    _amount = 100

    with pytest.raises(TypeError):
        coupon_exchange.transact().createOrder('1234', _amount, _price, _isBuy, agent)

    with pytest.raises(TypeError):
        coupon_exchange.transact().createOrder(1234, _amount, _price, _isBuy, agent)


# エラー系2
#   入力値の型誤り（_amount）
def test_createorder_error_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文
    web3.eth.defaultAccount = issuer
    _price = 123
    _isBuy = False

    with pytest.raises(TypeError):
        coupon_exchange.transact().createOrder(
            coupon_token.address, -1, _price, _isBuy, agent)

    with pytest.raises(TypeError):
        coupon_exchange.transact().createOrder(
            coupon_token.address, 2 ** 256, _price, _isBuy, agent)

    with pytest.raises(TypeError):
        coupon_exchange.transact().createOrder(
            coupon_token.address, '0', _price, _isBuy, agent)

    with pytest.raises(TypeError):
        coupon_exchange.transact().createOrder(
            coupon_token.address, 0.1, _price, _isBuy, agent)


# エラー系3
#   入力値の型誤り（_price）
def test_createorder_error_3(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文
    web3.eth.defaultAccount = issuer
    _amount = 100
    _isBuy = False

    with pytest.raises(TypeError):
        coupon_exchange.transact().createOrder(
            coupon_token.address, _amount, -1, _isBuy, agent)

    with pytest.raises(TypeError):
        coupon_exchange.transact().createOrder(
            coupon_token.address, _amount, 2 ** 256, _isBuy, agent)

    with pytest.raises(TypeError):
        coupon_exchange.transact().createOrder(
            coupon_token.address, _amount, '0', _isBuy, agent)

    with pytest.raises(TypeError):
        coupon_exchange.transact().createOrder(
            coupon_token.address, _amount, 0.1, _isBuy, agent)


# エラー系4
#   入力値の型誤り（_isBuy）
def test_createorder_error_4(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123

    with pytest.raises(TypeError):
        coupon_exchange.transact().createOrder(
            coupon_token.address, _amount, _price, 1234, agent)

    with pytest.raises(TypeError):
        coupon_exchange.transact().createOrder(
            coupon_token.address, _amount, _price, 'True', agent)


# エラー系5
#   入力値の型誤り（_agent）
def test_createorder_error_5(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文
    web3.eth.defaultAccount = issuer
    _price = 123
    _isBuy = False
    _amount = 100

    with pytest.raises(TypeError):
        coupon_exchange.transact().createOrder(
            coupon_token.address, _amount, _price, _isBuy, '1234')

    with pytest.raises(TypeError):
        coupon_exchange.transact().createOrder(
            coupon_token.address, _amount, _price, _isBuy, 1234)


# エラー系6-1
#   買注文に対するチェック
#   1) 注文数量が0の場合
def test_createorder_error_6_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）：エラー
    order_id_before = coupon_exchange.call().latestOrderId()
    _amount = 0
    _price = 123
    _isBuy = True
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, _amount, _price, _isBuy, agent
    )  # エラーになる
    order_id_after = coupon_exchange.call().latestOrderId()

    trader_commitment = coupon_exchange.call(). \
        commitmentOf(trader, coupon_token.address)
    assert trader_commitment == 0
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_token.call().balanceOf(trader) == 0
    assert order_id_before == order_id_after


# エラー系6-2
#   買注文に対するチェック
#   2) 取扱ステータスがFalseの場合
def test_createorder_error_6_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # 取扱ステータス更新
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(
        coupon_token.transact().setStatus(False)
    )

    # Make注文（買）：エラー
    order_id_before = coupon_exchange.call().latestOrderId()
    _amount = 0
    _price = 123
    _isBuy = True
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, _amount, _price, _isBuy, agent
    )  # エラーになる
    order_id_after = coupon_exchange.call().latestOrderId()

    trader_commitment = coupon_exchange.call(). \
        commitmentOf(trader, coupon_token.address)
    assert trader_commitment == 0
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_token.call().balanceOf(trader) == 0
    assert order_id_before == order_id_after


# エラー系6-3
#   買注文に対するチェック
#   3) 無効な収納代行業者（Agent）の指定
def test_createorder_error_6_3(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）：エラー
    order_id_before = coupon_exchange.call().latestOrderId()
    _amount = 0
    _price = 123
    _isBuy = True
    invalid_agent = users['trader']
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, _amount, _price, _isBuy, invalid_agent
    )  # エラーになる

    order_id_after = coupon_exchange.call().latestOrderId()
    trader_commitment = coupon_exchange.call(). \
        commitmentOf(trader, coupon_token.address)

    assert trader_commitment == 0
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_token.call().balanceOf(trader) == 0
    assert order_id_before == order_id_after


# エラー系7-1
#   売注文に対するチェック
#   1) 注文数量が0の場合
def test_createorder_error_7_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    _amount = 100
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, _amount
    )

    # Make注文（売）：エラー
    web3.eth.defaultAccount = issuer
    _amount = 0
    _price = 123
    _isBuy = False
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, _amount, _price, _isBuy, agent
    )  # エラーになる

    issuer_commitment = coupon_exchange.call(). \
        commitmentOf(issuer, coupon_token.address)
    assert issuer_commitment == 0
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]


# エラー系7-2
#   売注文に対するチェック
#   2) 残高数量が発注数量に満たない場合
def test_createorder_error_7_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    _amount = 100
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, _amount
    )

    # Make注文（売）：エラー
    web3.eth.defaultAccount = issuer
    _amount = 101
    _price = 123
    _isBuy = False
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, _amount, _price, _isBuy, agent
    )  # エラーになる

    issuer_commitment = coupon_exchange.call(). \
        commitmentOf(issuer, coupon_token.address)
    assert issuer_commitment == 0
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]


# エラー系7-3
#   売注文に対するチェック
#   3) 取扱ステータスがFalseの場合
def test_createorder_error_7_3(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    _amount = 100
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, _amount
    )

    # 取扱ステータス更新
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(
        coupon_token.transact().setStatus(False)
    )

    # Make注文（売）：エラー
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    _isBuy = False
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, _amount, _price, _isBuy, agent
    )  # エラーになる

    issuer_commitment = coupon_exchange.call(). \
        commitmentOf(issuer, coupon_token.address)
    assert issuer_commitment == 0
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]


# エラー系7-4
#   売注文に対するチェック
#   4) 無効な収納代行業者（Agent）の指定
def test_createorder_error_7_4(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    _amount = 100
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, _amount
    )

    # Make注文（売）：エラー
    web3.eth.defaultAccount = issuer
    _amount = 100
    _price = 123
    _isBuy = False
    invalid_agent = users['trader']
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, _amount, _price, _isBuy, invalid_agent
    )  # エラーになる

    issuer_commitment = coupon_exchange.call(). \
        commitmentOf(issuer, coupon_token.address)
    assert issuer_commitment == 0
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]


'''
TEST4_注文キャンセル（cancelOrder）
'''


# 正常系１
#   ＜発行体＞新規発行 -> ＜投資家＞Make注文（買）
#       -> ＜投資家＞注文キャンセル
def test_cancelorder_normal_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    _amount = 100
    _price = 123
    _isBuy = True
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, _amount, _price, _isBuy, agent
    )

    # 注文キャンセル
    order_id = coupon_exchange.call().latestOrderId()
    chain.wait.for_receipt(
        coupon_exchange.transact().cancelOrder(order_id)
    )

    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        trader, to_checksum_address(coupon_token.address),
        _amount, _price, _isBuy, agent, True
    ]
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_token.call().balanceOf(trader) == 0


# 正常系2
#   ＜発行体＞新規発行 -> ＜発行体＞Make注文（売）
#       -> ＜発行体＞注文キャンセル
def test_cancelorder_normal_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    _amount = 100
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, _amount
    )

    # Make注文（売）
    _amount = 100
    _price = 123
    _isBuy = False
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, _amount, _price, _isBuy, agent
    )

    # 注文キャンセル
    order_id = coupon_exchange.call().latestOrderId()
    chain.wait.for_receipt(
        coupon_exchange.transact().cancelOrder(order_id)
    )

    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        _amount, _price, _isBuy, agent, True
    ]
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 0


# 正常系3-1
#   限界値（買注文）
def test_cancelorder_normal_3_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[2] = 2 ** 256 - 1
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    _amount = 2 ** 256 - 1
    _price = 123
    _isBuy = True
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, _amount, _price, _isBuy, agent
    )

    # 注文キャンセル
    order_id = coupon_exchange.call().latestOrderId()
    chain.wait.for_receipt(
        coupon_exchange.transact().cancelOrder(order_id)
    )

    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        trader, to_checksum_address(coupon_token.address),
        _amount, _price, _isBuy, agent, True
    ]
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]


# 正常系3-2
#   限界値（売注文）
def test_cancelorder_normal_3_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[2] = 2 ** 256 - 1
    coupon_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    _amount = 2 ** 256 - 1
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, _amount
    )

    # Make注文（売）
    _price = 2 ** 256 - 1
    _isBuy = False
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, _amount, _price, _isBuy, agent
    )

    # 注文キャンセル
    order_id = coupon_exchange.call().latestOrderId()
    chain.wait.for_receipt(
        coupon_exchange.transact().cancelOrder(order_id)
    )

    orderbook = coupon_exchange.call().getOrder(order_id)
    issuer_commitment = coupon_exchange.call(). \
        commitmentOf(issuer, coupon_token.address)
    issuer_balance = coupon_token.call().balanceOf(issuer)

    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        _amount, _price, _isBuy, agent, True
    ]
    assert issuer_balance == deploy_args[2]
    assert issuer_commitment == 0


# エラー系1
#   入力値の型誤り（_orderId）
def test_cancelorder_error_1(web3, users, coupon_exchange):
    issuer = users['issuer']

    # 注文キャンセル
    web3.eth.defaultAccount = issuer

    with pytest.raises(TypeError):
        coupon_exchange.transact().cancelOrder(-1)

    with pytest.raises(TypeError):
        coupon_exchange.transact().cancelOrder(2 ** 256)

    with pytest.raises(TypeError):
        coupon_exchange.transact().cancelOrder('0')

    with pytest.raises(TypeError):
        coupon_exchange.transact().cancelOrder(0.1)


# エラー系2
#   指定した注文番号が、直近の注文ID以上の場合
def test_cancelorder_error_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    _amount = 100
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, _amount
    )

    # Make注文（売）
    _amount = 100
    _price = 123
    _isBuy = False
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, _amount, _price, _isBuy, agent
    )

    # 注文キャンセル：エラー
    wrong_order_id = coupon_exchange.call().latestOrderId() - 1  # 誤った order_id
    correct_order_id = coupon_exchange.call().latestOrderId()  # 正しい order_id
    chain.wait.for_receipt(
        coupon_exchange.transact().cancelOrder(wrong_order_id)
    )  # エラーになる

    orderbook = coupon_exchange.call().getOrder(correct_order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        _amount, _price, _isBuy, agent, False
    ]
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - _amount
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == _amount


# エラー系3-1
#   1) 元注文の残注文数量が0の場合
def test_cancelorder_error_3_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, 100, 123, True, agent
    )

    # Take注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, order_id, 100, False
    )

    # 決済承認
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, agreement_id
    )

    # 注文キャンセル：エラー
    chain.wait.for_receipt(
        coupon_exchange.transact().cancelOrder(order_id)
    )  # エラーになる

    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        trader, to_checksum_address(coupon_token.address),
        0, 123, True, agent, False
    ]
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert coupon_token.call().balanceOf(trader) == 100


# エラー系3-2
#   2) 注文がキャンセル済みの場合
def test_cancelorder_error_3_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, 100, 123, True, agent
    )

    # 注文キャンセル１回目：正常
    web3.eth.defaultAccount = trader
    order_id = coupon_exchange.call().latestOrderId()
    chain.wait.for_receipt(
        coupon_exchange.transact().cancelOrder(order_id)
    )

    # 注文キャンセル２回目：エラー
    chain.wait.for_receipt(
        coupon_exchange.transact().cancelOrder(order_id)
    )  # エラーになる

    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        trader, to_checksum_address(coupon_token.address),
        100, 123, True, agent, True
    ]
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_token.call().balanceOf(trader) == 0


# エラー系3-3-1
#   3) 元注文の発注者と、注文キャンセルの実施者が異なる場合
#   ※買注文の場合
def test_cancelorder_error_3_3_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, 100, 123, True, agent
    )

    # 注文キャンセル：エラー
    web3.eth.defaultAccount = issuer  # 注文実施者と異なる
    order_id = coupon_exchange.call().latestOrderId()
    chain.wait.for_receipt(
        coupon_exchange.transact().cancelOrder(order_id)
    )  # エラーになる

    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        trader, to_checksum_address(coupon_token.address),
        100, 123, True, agent, False
    ]
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_token.call().balanceOf(trader) == 0


# エラー系3-3-2
#   3) 元注文の発注者と、注文キャンセルの実施者が異なる場合
#   ※売注文の場合
def test_cancelorder_error_3_3_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )

    # Make注文（売）
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # 注文キャンセル：エラー
    web3.eth.defaultAccount = trader  # 注文実施者と異なる
    order_id = coupon_exchange.call().latestOrderId()
    chain.wait.for_receipt(
        coupon_exchange.transact().cancelOrder(order_id)
    )  # エラーになる

    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        100, 123, False, agent, False
    ]
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 100


'''
TEST5_Take注文（executeOrder）
'''


# 正常系1
#   ＜発行体＞新規発行 -> ＜発行体＞Make注文（売）
#       -> ＜投資家＞Take注文（買）
def test_executeOrder_normal_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 30, True
    )

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 100

    # Assert: agreement
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, False
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 123


# 正常系2
#   ＜発行体＞新規発行 -> ＜投資家＞Make注文（買）
#       -> ＜発行体＞Take注文（売）
def test_executeOrder_normal_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, 100, 123, True, agent
    )

    # Take注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 50
    )
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, order_id, 30, False
    )

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        trader, to_checksum_address(coupon_token.address),
        70, 123, True, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 50
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 30

    # Assert: agreement
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        issuer, 30, 123, False, False
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 123


# 正常系3-1
#   限界値（買注文）
def test_executeOrder_normal_3_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[2] = 2 ** 256 - 1
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 2 ** 256 - 1
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 2 ** 256 - 1, 2 ** 256 - 1, False, agent
    )

    # Take注文（買）
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 2 ** 256 - 1, True
    )

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        0, 2 ** 256 - 1, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == 0
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 2 ** 256 - 1

    # Assert: agreement
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 2 ** 256 - 1, 2 ** 256 - 1, False, False
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 2 ** 256 - 1


# 正常系3-2
#   限界値（売注文）
def test_executeOrder_normal_3_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[2] = 2 ** 256 - 1
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, 2 ** 256 - 1, 2 ** 256 - 1, True, agent
    )

    # Take注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 2 ** 256 - 1
    )
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, order_id, 2 ** 256 - 1, False
    )

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        trader, to_checksum_address(coupon_token.address),
        0, 2 ** 256 - 1, True, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == 0
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 2 ** 256 - 1

    # Assert: agreement
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        issuer, 2 ** 256 - 1, 2 ** 256 - 1, False, False
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 2 ** 256 - 1


# エラー系1
#   入力値の型誤り（orderId）
def test_executeOrder_error_1(web3, users, coupon_exchange):
    trader = users['trader']

    web3.eth.defaultAccount = trader
    amount = 50
    is_buy = True

    with pytest.raises(TypeError):
        coupon_exchange.transact().executeOrder(-1, amount, is_buy)

    with pytest.raises(TypeError):
        coupon_exchange.transact().executeOrder(2 ** 256, amount, is_buy)

    with pytest.raises(TypeError):
        coupon_exchange.transact().executeOrder('0', amount, is_buy)

    with pytest.raises(TypeError):
        coupon_exchange.transact().executeOrder(0.1, amount, is_buy)


# エラー系2
#   入力値の型誤り（amount）
def test_executeOrder_error_2(web3, users, coupon_exchange):
    trader = users['trader']

    web3.eth.defaultAccount = trader
    order_id = 1000
    is_buy = True

    with pytest.raises(TypeError):
        coupon_exchange.transact().executeOrder(order_id, -1, is_buy)

    with pytest.raises(TypeError):
        coupon_exchange.transact().executeOrder(order_id, 2 ** 256, is_buy)

    with pytest.raises(TypeError):
        coupon_exchange.transact().executeOrder(order_id, '0', is_buy)

    with pytest.raises(TypeError):
        coupon_exchange.transact().executeOrder(order_id, 0.1, is_buy)


# エラー系3
#   入力値の型誤り（isBuy）
def test_executeOrder_error_3(web3, users, coupon_exchange):
    trader = users['trader']

    web3.eth.defaultAccount = trader
    order_id = 1000
    amount = 123

    with pytest.raises(TypeError):
        coupon_exchange.transact().executeOrder(order_id, amount, 'True')

    with pytest.raises(TypeError):
        coupon_exchange.transact().executeOrder(order_id, amount, 111)


# エラー系4
#   指定した注文IDが直近の注文IDを超えている場合
def test_executeOrder_error_4(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）：エラー
    wrong_order_id = coupon_exchange.call().latestOrderId() + 1  # 誤ったID
    correct_order_id = coupon_exchange.call().latestOrderId()  # 正しいID
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, wrong_order_id, 30, True
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(correct_order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        100, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 100

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 0


# エラー系5-1
#   Take買注文
#   1) 注文数量が0の場合
def test_executeOrder_error_5_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）：エラー
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 0, True  # 注文数量が0
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        100, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 100

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 0


# エラー系5-2
#   Take買注文
#   2) 元注文と、発注する注文が同一の売買区分の場合
def test_executeOrder_error_5_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, True, agent
    )

    # Take注文（買）：エラー
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 30, True  # 同一売買区分
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        100, 123, True, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 0

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 0


# エラー系5-3
#   Take買注文
#   3) 元注文の発注者と同一のアドレスからの発注の場合
def test_executeOrder_error_5_3(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）：エラー
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, order_id, 30, True  # 同一アドレスからの発注
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        100, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 100

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 100

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 0


# エラー系5-4
#   Take買注文
#   4) 元注文がキャンセル済の場合
def test_executeOrder_error_5_4(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Make注文のキャンセル
    web3.eth.defaultAccount = issuer
    order_id = coupon_exchange.call().latestOrderId()
    chain.wait.for_receipt(
        coupon_exchange.transact().cancelOrder(order_id)
    )

    # Take注文（買）：エラー
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 30, True
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        100, 123, False, agent, True
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 0

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 0


# エラー系5-5
#   Take買注文
#   5) 取扱ステータスがFalseの場合
def test_executeOrder_error_5_5(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # 取扱ステータス更新（Falseへ更新）
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(
        coupon_token.transact().setStatus(False)
    )

    # Take注文（買）：エラー
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 30, True
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        100, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 100

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 0


# エラー系5-6
#   Take買注文
#   6) 数量が元注文の残数量を超過している場合
def test_executeOrder_error_5_6(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）：エラー
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 101, True  # Make注文の数量を超過
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        100, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 100

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 0


# エラー系6-1
#   Take売注文
#   1) 注文数量が0の場合
def test_executeOrder_error_6_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, 100, 123, True, agent
    )

    # Take注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 50
    )
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, order_id, 0, False  # 注文数量が0
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        trader, to_checksum_address(coupon_token.address),
        100, 123, True, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 0

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 0


# エラー系6-2
#   Take売注文
#   2) 元注文と、発注する注文が同一の売買区分の場合
def test_executeOrder_error_6_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（売）：エラー
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 30, False  # 同一売買区分
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        100, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 100

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 0


# エラー系6-3
#   Take売注文
#   3) 元注文の発注者と同一のアドレスからの発注の場合
def test_executeOrder_error_6_3(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, True, agent
    )

    # Take注文（売）：エラー
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 50
    )
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, order_id, 30, False  # Make注文と同一アドレスからの発注
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        100, 123, True, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 0

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 0


# エラー系6-4
#   Take売注文
#   4) 元注文がキャンセル済の場合
def test_executeOrder_error_6_4(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, 100, 123, True, agent
    )

    # Make注文のキャンセル
    web3.eth.defaultAccount = trader
    order_id = coupon_exchange.call().latestOrderId()
    chain.wait.for_receipt(
        coupon_exchange.transact().cancelOrder(order_id)
    )

    # Take注文（売）：エラー
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 50
    )
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, order_id, 30, False
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        trader, to_checksum_address(coupon_token.address),
        100, 123, True, agent, True
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 0

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 0


# エラー系6-5
#   Take売注文
#   5) 取扱ステータスがFalseの場合
def test_executeOrder_error_6_5(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, 100, 123, True, agent
    )

    # 取扱ステータス更新（Falseへ更新）
    web3.eth.defaultAccount = issuer
    chain.wait.for_receipt(
        coupon_token.transact().setStatus(False)
    )

    # Take注文（売）：エラー
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 50
    )
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, order_id, 30, False
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        trader, to_checksum_address(coupon_token.address),
        100, 123, True, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 0

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 0


# エラー系6-6
#   Take売注文
#   6) 発注者の残高が発注数量を下回っている場合
def test_executeOrder_error_6_6(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, 100, 123, True, agent
    )

    # Take注文（売）：エラー
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 50
    )
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, order_id, 51, False  # balanceを超える注文数量
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        trader, to_checksum_address(coupon_token.address),
        100, 123, True, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 0

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 0


# エラー系6-7
#   Take売注文
#   7) 数量が元注文の残数量を超過している場合
def test_executeOrder_error_6_7(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, 100, 123, True, agent
    )

    # Take注文（売）：エラー
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 101
    )
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, order_id, 101, False
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        trader, to_checksum_address(coupon_token.address),
        100, 123, True, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 0

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 0


'''
TEST6_決済承認（confirmAgreement）
'''


# 正常系1
#   Make売、Take買
#       ＜発行体＞新規発行 -> ＜発行体＞Make注文（売）
#           -> ＜投資家＞Take注文（買） -> ＜決済業者＞決済処理
def test_confirmAgreement_normal_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 30, True
    )

    # 決済処理
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, agreement_id
    )

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert coupon_token.call().balanceOf(trader) == 30

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 70

    # Assert: agreement
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, True
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 123


# 正常系2
#   Make買、Take売
#       ＜発行体＞新規発行 -> ＜投資家＞Make注文（買）
#           -> ＜発行体＞Take注文（売） -> ＜決済業者＞決済処理
def test_confirmAgreement_normal_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, 100, 123, True, agent
    )

    # Take注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 50
    )
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, order_id, 30, False
    )

    # 決済処理
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, agreement_id
    )

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        trader, to_checksum_address(coupon_token.address),
        70, 123, True, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 50
    assert coupon_token.call().balanceOf(trader) == 30

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 0

    # Assert: agreement
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        issuer, 30, 123, False, True
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 123


# 正常系3-1
#   Make売、Take買
#   限界値
def test_confirmAgreement_normal_3_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[2] = 2 ** 256 - 1  # 上限値
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 2 ** 256 - 1
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 2 ** 256 - 1, 2 ** 256 - 1, False, agent
    )

    # Take注文（買）
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 2 ** 256 - 1, True
    )

    # 決済処理
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, agreement_id
    )

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        0, 2 ** 256 - 1, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == 0
    assert coupon_token.call().balanceOf(trader) == 2 ** 256 - 1

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 0

    # Assert: agreement
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 2 ** 256 - 1, 2 ** 256 - 1, False, True
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 2 ** 256 - 1


# 正常系3-2
#   Make買、Take売
#   限界値
def test_confirmAgreement_normal_3_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[2] = 2 ** 256 - 1  # 上限値
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, 2 ** 256 - 1, 2 ** 256 - 1, True, agent
    )

    # Take注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 2 ** 256 - 1
    )
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, order_id, 2 ** 256 - 1, False
    )

    # 決済処理
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, agreement_id
    )

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        trader, to_checksum_address(coupon_token.address),
        0, 2 ** 256 - 1, True, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == 0
    assert coupon_token.call().balanceOf(trader) == 2 ** 256 - 1

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 0

    # Assert: agreement
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        issuer, 2 ** 256 - 1, 2 ** 256 - 1, False, True
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 2 ** 256 - 1


# エラー系1
#   入力値の型誤り（orderId）
def test_confirmAgreement_error_1(web3, users, coupon_exchange):
    agent = users['agent']

    # 決済承認：決済業者
    web3.eth.defaultAccount = agent

    with pytest.raises(TypeError):
        coupon_exchange.transact().confirmAgreement(-1, 0)

    with pytest.raises(TypeError):
        coupon_exchange.transact().confirmAgreement(2 ** 256, 0)

    with pytest.raises(TypeError):
        coupon_exchange.transact().confirmAgreement('0', 0)

    with pytest.raises(TypeError):
        coupon_exchange.transact().confirmAgreement(0.1, 0)


# エラー系2
#   入力値の型誤り（agreementId）
def test_confirmAgreement_error_2(web3, users, coupon_exchange):
    agent = users['agent']

    # 決済承認：決済業者
    web3.eth.defaultAccount = agent

    with pytest.raises(TypeError):
        coupon_exchange.transact().confirmAgreement(0, -1)

    with pytest.raises(TypeError):
        coupon_exchange.transact().confirmAgreement(0, 2 ** 256)

    with pytest.raises(TypeError):
        coupon_exchange.transact().confirmAgreement(0, '0')

    with pytest.raises(TypeError):
        coupon_exchange.transact().confirmAgreement(0, 0.1)


# エラー系3
#   指定した注文番号が、直近の注文ID以上の場合
def test_confirmAgreement_error_3(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 30, True
    )

    # 決済処理：エラー
    wrong_order_id = coupon_exchange.call().latestOrderId() + 1  # 誤ったID
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, wrong_order_id, agreement_id
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 100

    # Assert: agreement
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, False
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 123


# エラー系4
#   指定した約定IDが、直近の約定ID以上の場合
def test_confirmAgreement_error_4(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 30, True
    )

    # 決済処理：エラー
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    wrong_agreement_id = coupon_exchange.call().latestAgreementId(order_id) + 1  # 誤ったID
    settlement(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, wrong_agreement_id
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 100

    # Assert: agreement
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, False
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 123


# エラー系5
#   すでに決済承認済み（支払い済み）の場合
def test_confirmAgreement_error_5(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 30, True
    )

    # 決済処理1回目
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, agreement_id
    )

    # 決済処理２回目：エラー
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, agreement_id
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert coupon_token.call().balanceOf(trader) == 30

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 70

    # Assert: agreement
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, True
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 123


# エラー系6
#   すでに決済非承認済み（キャンセル済み）の場合
def test_confirmAgreement_error_6(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 30, True
    )

    # 決済非承認
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement_ng(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, agreement_id
    )

    # 決済処理：エラー
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, agreement_id
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 70
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 70

    # Assert: agreement
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, True, False
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 123


# エラー系7
#   元注文で指定した決済業者ではない場合
def test_confirmAgreement_error_7(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 30, True
    )

    # 決済処理：エラー
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, agreement_id  # 元注文で指定した決済業者ではない
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 100

    # Assert: agreement
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, False
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 123


'''
TEST7_決済非承認（cancelAgreement）
'''


# 正常系1
#   Make売、Take買
#       ＜発行体＞新規発行 -> ＜発行体＞Make注文（売）
#           -> ＜投資家＞Take注文（買） -> ＜決済業者＞決済非承認
def test_cancelAgreement_normal_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 30, True
    )

    # 決済非承認
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement_ng(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, agreement_id
    )

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 70
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 70

    # Assert: agreement
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, True, False
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 123


# 正常系2
#   Make買、Take売
#       ＜発行体＞新規発行 -> ＜投資家＞Make注文（買）
#           -> ＜発行体＞Take注文（売） -> ＜決済業者＞決済非承認
def test_cancelAgreement_normal_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, 100, 123, True, agent
    )

    # Take注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 50
    )
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, order_id, 30, False
    )

    # 決済非承認
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement_ng(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, agreement_id
    )

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        trader, to_checksum_address(coupon_token.address),
        70, 123, True, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 20
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 0

    # Assert: agreement
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        issuer, 30, 123, True, False
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 123


# 正常系3-1
#   Make売、Take買
#   限界値
def test_cancelAgreement_normal_3_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[2] = 2 ** 256 - 1  # 上限値
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 2 ** 256 - 1
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 2 ** 256 - 1, 2 ** 256 - 1, False, agent
    )

    # Take注文（買）
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 2 ** 256 - 1, True
    )

    # 決済非承認
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement_ng(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, agreement_id
    )

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        0, 2 ** 256 - 1, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 0

    # Assert: agreement
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 2 ** 256 - 1, 2 ** 256 - 1, True, False
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 2 ** 256 - 1


# 正常系3-2
#   Make買、Take売
#   限界値
def test_cancelAgreement_normal_3_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[2] = 2 ** 256 - 1  # 上限値
    coupon_token = deploy(chain, deploy_args)

    # Make注文（買）
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, 2 ** 256 - 1, 2 ** 256 - 1, True, agent
    )

    # Take注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 2 ** 256 - 1
    )
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, order_id, 2 ** 256 - 1, False
    )

    # 決済非承認
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement_ng(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, agreement_id
    )

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        trader, to_checksum_address(coupon_token.address),
        0, 2 ** 256 - 1, True, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2]
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 0

    # Assert: agreement
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        issuer, 2 ** 256 - 1, 2 ** 256 - 1, True, False
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 2 ** 256 - 1


# エラー系1
#   入力値の型誤り（orderId）
def test_cancelAgreement_error_1(web3, users, coupon_exchange):
    agent = users['agent']

    # 決済非承認：決済業者
    web3.eth.defaultAccount = agent

    with pytest.raises(TypeError):
        coupon_exchange.transact().cancelAgreement(-1, 0)

    with pytest.raises(TypeError):
        coupon_exchange.transact().cancelAgreement(2 ** 256, 0)

    with pytest.raises(TypeError):
        coupon_exchange.transact().cancelAgreement('0', 0)

    with pytest.raises(TypeError):
        coupon_exchange.transact().cancelAgreement(0.1, 0)


# エラー系2
#   入力値の型誤り（_agreementId）
def test_cancelAgreement_error_2(web3, users, coupon_exchange):
    _agent = users['agent']

    # 決済非承認：決済業者
    web3.eth.defaultAccount = _agent

    with pytest.raises(TypeError):
        coupon_exchange.transact().cancelAgreement(0, -1)

    with pytest.raises(TypeError):
        coupon_exchange.transact().cancelAgreement(0, 2 ** 256)

    with pytest.raises(TypeError):
        coupon_exchange.transact().cancelAgreement(0, '0')

    with pytest.raises(TypeError):
        coupon_exchange.transact().cancelAgreement(0, 0.1)


# エラー系3
#   指定した注文番号が、直近の注文ID以上の場合
def test_cancelAgreement_error_3(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 30, True
    )

    # 決済非承認：エラー
    wrong_order_id = coupon_exchange.call().latestOrderId() + 1  # 誤ったID
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement_ng(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, wrong_order_id, agreement_id
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 100

    # Assert: agreement
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, False
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 123


# エラー系4
#   指定した約定IDが、直近の約定ID以上の場合
def test_cancelAgreement_error_4(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 30, True
    )

    # 決済非承認：エラー
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    wrong_agreement_id = coupon_exchange.call().latestAgreementId(order_id) + 1  # 誤ったID
    settlement_ng(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, wrong_agreement_id
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 100

    # Assert: agreement
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, False
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 123


# エラー系5
#   すでに決済承認済み（支払い済み）の場合
def test_cancelAgreement_error_5(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 30, True
    )

    # 決済処理
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, agreement_id
    )

    # 決済非承認：エラー
    settlement_ng(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, agreement_id
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert coupon_token.call().balanceOf(trader) == 30

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 70

    # Assert: agreement
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, True
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 123


# エラー系6
#   すでに決済非承認済み（キャンセル済み）の場合
def test_cancelAgreement_error_6(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 30, True
    )

    # 決済非承認１回目
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement_ng(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, agreement_id
    )

    # 決済非承認２回目：エラー
    settlement_ng(
        web3, chain,
        coupon_token, coupon_exchange,
        agent, order_id, agreement_id
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 70
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 70

    # Assert: agreement
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, True, False
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 123


# エラー系7
#   元注文で指定した決済業者ではない場合
def test_cancelAgreement_error_7(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']
    agent = users['agent']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Make注文（売）
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100, 123, False, agent
    )

    # Take注文（買）
    order_id = coupon_exchange.call().latestOrderId()
    take_order(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, 30, True
    )

    # 決済非承認１回目
    agreement_id = coupon_exchange.call().latestAgreementId(order_id)
    settlement_ng(
        web3, chain,
        coupon_token, coupon_exchange,
        trader, order_id, agreement_id  # 元注文で指定した決済業者ではない
    )  # エラーになる

    # Assert: orderbook
    orderbook = coupon_exchange.call().getOrder(order_id)
    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        70, 123, False, agent, False
    ]

    # Assert: balance
    assert coupon_token.call().balanceOf(issuer) == deploy_args[2] - 100
    assert coupon_token.call().balanceOf(trader) == 0

    # Assert: commitment
    assert coupon_exchange.call().commitmentOf(issuer, coupon_token.address) == 100

    # Assert: agreement
    agreement = coupon_exchange.call().getAgreement(order_id, agreement_id)
    assert agreement[0:5] == [
        trader, 30, 123, False, False
    ]

    # Assert: last_price
    assert coupon_exchange.call().lastPrice(coupon_token.address) == 123


'''
TEST8_Exchange切替
'''


# 正常系
def test_updateExchange_normal_1(web3, chain, users, coupon_exchange,
                                 coupon_exchange_storage, payment_gateway):
    issuer = users['issuer']
    agent = users['agent']
    admin = users['admin']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon_token = deploy(chain, deploy_args)

    # Exchangeへのデポジット
    deposit(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 100
    )

    # Make注文（売）
    _price = 123
    _isBuy = False
    make_order(
        web3, chain,
        coupon_token, coupon_exchange,
        issuer, 10, _price, _isBuy, agent
    )

    # Exchange（新）
    web3.eth.defaultAccount = admin
    coupon_exchange_new, _ = chain.provider.get_or_deploy_contract(
        'IbetCouponExchange',
        deploy_args=[payment_gateway.address, coupon_exchange_storage.address]
    )
    txn_hash = coupon_exchange_storage.transact().\
        upgradeVersion(coupon_exchange_new.address)
    chain.wait.for_receipt(txn_hash)

    # Exchange（新）からの情報参照
    web3.eth.defaultAccount = issuer
    order_id = coupon_exchange_new.call().latestOrderId()
    orderbook = coupon_exchange_new.call().getOrder(order_id)
    issuer_commitment = coupon_exchange_new.call(). \
        commitmentOf(issuer, coupon_token.address)
    issuer_balance_exchange = coupon_exchange_new.call(). \
        balanceOf(issuer, coupon_token.address)
    issuer_balance_token = coupon_token.call().balanceOf(issuer)

    assert orderbook == [
        issuer, to_checksum_address(coupon_token.address),
        10, _price, _isBuy, agent, False
    ]
    assert issuer_balance_token == deploy_args[2] - 100
    assert issuer_balance_exchange == 90
    assert issuer_commitment == 10
