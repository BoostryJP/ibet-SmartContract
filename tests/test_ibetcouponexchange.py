import pytest
import utils

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
    coupon, deploy_args = utils.\
        issue_transferable_coupon(web3, chain, coupon_exchange.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().allocate(coupon_exchange.address, _value)
    chain.wait.for_receipt(txn_hash)

    balance_coupon = coupon.call().balanceOf(_issuer)
    balance_exchange = coupon_exchange.call().balances(_issuer, coupon.address)

    assert balance_coupon == deploy_args[2] - _value
    assert balance_exchange == _value

'''
TEST2_クーポントークンの割当（Transfer）
'''
# 正常系1
# ＜発行体＞新規発行 -> ＜発行体＞Exchangeへのデポジット
#  -> ＜発行体＞アカウントアドレスへの割当（Transfer）
def test_transfer_normal_1(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _consumer = users['trader']
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.\
        issue_transferable_coupon(web3, chain, coupon_exchange.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().allocate(coupon_exchange.address, _value)
    chain.wait.for_receipt(txn_hash)

    # アカウントアドレスへの割当（Transfer)
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon_exchange.transact().transfer(
        coupon.address, _consumer, _value)
    chain.wait.for_receipt(txn_hash)

    issuer_balance_coupon = coupon.call().balanceOf(_issuer)
    issuer_balance_exchange = coupon_exchange.call().balances(_issuer, coupon.address)
    consumer_balance_coupon = coupon.call().balanceOf(_consumer)
    consumer_balance_exchange = coupon_exchange.call().balances(_consumer, coupon.address)

    assert issuer_balance_coupon == deploy_args[2] - _value
    assert issuer_balance_exchange == 0
    assert consumer_balance_coupon == _value
    assert consumer_balance_exchange == 0

# 正常系２
# ＜発行体＞新規発行 -> ＜発行体＞Exchangeへのデポジット（２回）
#  -> ＜発行体＞アカウントアドレスへの割当（Transfer）
def test_transfer_normal_2(web3, chain, users, coupon_exchange):
    _admin = users['admin']
    _issuer = users['issuer']
    _consumer = users['trader']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.\
        issue_transferable_coupon(web3, chain, coupon_exchange.address)

    # Exchangeへのデポジット（１回目）
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().allocate(coupon_exchange.address, 100)
    chain.wait.for_receipt(txn_hash)

    # Exchangeへのデポジット（２回目）
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().allocate(coupon_exchange.address, 200)
    chain.wait.for_receipt(txn_hash)

    # アカウントアドレスへの割当（Transfer)
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon_exchange.transact().transfer(
        coupon.address, _consumer, 250)
    chain.wait.for_receipt(txn_hash)

    issuer_balance_coupon = coupon.call().balanceOf(_issuer)
    issuer_balance_exchange = coupon_exchange.call().balances(_issuer, coupon.address)
    consumer_balance_coupon = coupon.call().balanceOf(_consumer)
    consumer_balance_exchange = coupon_exchange.call().balances(_consumer, coupon.address)

    assert issuer_balance_coupon == deploy_args[2] - 100 - 200
    assert issuer_balance_exchange == 100 + 200 - 250
    assert consumer_balance_coupon == 250
    assert consumer_balance_exchange == 0

# エラー系１：入力値の型誤り（Token）
def test_transfer_error_1(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _consumer = users['trader']
    _value = 100

    # アカウントアドレスへの割当（Transfer)
    web3.eth.defaultAccount = _issuer

    with pytest.raises(TypeError):
        coupon_exchange.transact().transfer(1234, _consumer, _value)

    with pytest.raises(TypeError):
        coupon_exchange.transact().transfer('1234', _consumer, _value)

# エラー系２：入力値の型誤り（To）
def test_transfer_error_2(web3, chain, users, coupon_exchange):
    _admin = users['admin']
    _issuer = users['issuer']
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.\
        issue_transferable_coupon(web3, chain, coupon_exchange.address)

    # アカウントアドレスへの割当（Transfer)
    web3.eth.defaultAccount = _issuer

    with pytest.raises(TypeError):
        coupon_exchange.transact().transfer(coupon.address, 1234, _value)

    with pytest.raises(TypeError):
        coupon_exchange.transact().transfer(coupon.address, '1234', _value)

# エラー系３：入力値の型誤り（To）
def test_transfer_error_3(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _consumer = users['trader']
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.\
        issue_transferable_coupon(web3, chain, coupon_exchange.address)

    # アカウントアドレスへの割当（Transfer)
    web3.eth.defaultAccount = _issuer

    with pytest.raises(TypeError):
        coupon_exchange.transact().transfer(coupon.address, _consumer, '1244')

    with pytest.raises(TypeError):
        coupon_exchange.transact().transfer(coupon.address, _consumer, -1)

    with pytest.raises(TypeError):
        coupon_exchange.transact().transfer(coupon.address, _consumer, 2**265)

    with pytest.raises(TypeError):
        coupon_exchange.transact().transfer(coupon.address, _consumer, 0.1)

# エラー系４
# ＜発行体＞新規発行 -> ＜発行体＞Exchangeへのデポジット
#  -> ＜発行体＞アカウントアドレスへの割当（Transfer）　残高超過
def test_transfer_error_4(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _consumer = users['trader']
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.\
        issue_transferable_coupon(web3, chain, coupon_exchange.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().allocate(coupon_exchange.address, _value)
    chain.wait.for_receipt(txn_hash)

    # アカウントアドレスへの割当（Transfer)
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon_exchange.transact().transfer(
        coupon.address, _consumer, _value + 1) # エラーになる
    chain.wait.for_receipt(txn_hash)

    issuer_balance_coupon = coupon.call().balanceOf(_issuer)
    issuer_balance_exchange = coupon_exchange.call().balances(_issuer, coupon.address)
    consumer_balance_coupon = coupon.call().balanceOf(_consumer)
    consumer_balance_exchange = coupon_exchange.call().balances(_consumer, coupon.address)

    assert issuer_balance_coupon == deploy_args[2]
    assert issuer_balance_exchange == 0
    assert consumer_balance_coupon == 0
    assert consumer_balance_exchange == 0

# エラー系5
# ＜発行体＞新規発行 -> ＜発行体＞Exchangeへのデポジット
#  -> ＜発行体＞アカウントアドレスへの割当（Transfer）　数量0指定
def test_transfer_error_5(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _consumer = users['trader']
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.\
        issue_transferable_coupon(web3, chain, coupon_exchange.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().allocate(coupon_exchange.address, _value)
    chain.wait.for_receipt(txn_hash)

    # アカウントアドレスへの割当（Transfer)
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon_exchange.transact().transfer(coupon.address, _consumer, 0) # エラーになる
    chain.wait.for_receipt(txn_hash)

    issuer_balance_coupon = coupon.call().balanceOf(_issuer)
    issuer_balance_exchange = coupon_exchange.call().balances(_issuer, coupon.address)
    consumer_balance_coupon = coupon.call().balanceOf(_consumer)
    consumer_balance_exchange = coupon_exchange.call().balances(_consumer, coupon.address)

    assert issuer_balance_coupon == deploy_args[2]
    assert issuer_balance_exchange == 0
    assert consumer_balance_coupon == 0
    assert consumer_balance_exchange == 0

# エラー系6
# ＜発行体＞新規発行 -> ＜発行体＞Exchangeへのデポジット
#  -> ＜発行体＞クーポントークンを無効化
#  -> ＜発行体＞アカウントアドレスへの割当（Transfer）
def test_transfer_error_6(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _consumer = users['trader']
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.\
        issue_transferable_coupon(web3, chain, coupon_exchange.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().allocate(coupon_exchange.address, _value)
    chain.wait.for_receipt(txn_hash)

    # ステータスの修正
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().updateStatus(False)
    chain.wait.for_receipt(txn_hash)

    # アカウントアドレスへの割当（Transfer)
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon_exchange.transact().transfer(coupon.address, _consumer, _value) # エラーになる
    chain.wait.for_receipt(txn_hash)

    issuer_balance_coupon = coupon.call().balanceOf(_issuer)
    issuer_balance_exchange = coupon_exchange.call().balances(_issuer, coupon.address)
    consumer_balance_coupon = coupon.call().balanceOf(_consumer)
    consumer_balance_exchange = coupon_exchange.call().balances(_consumer, coupon.address)

    assert issuer_balance_coupon == deploy_args[2] - _value
    assert issuer_balance_exchange == _value
    assert consumer_balance_coupon == 0
    assert consumer_balance_exchange == 0

'''
TEST3_全ての残高の引き出し（withdrawAll）
'''
# 正常系1
# ＜発行体＞新規発行 -> ＜発行体＞Exchangeへのデポジット
#  -> ＜発行体＞引き出し（withdrawAll）
def test_withdrawAll_normal_1(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.\
        issue_transferable_coupon(web3, chain, coupon_exchange.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().allocate(coupon_exchange.address, _value)
    chain.wait.for_receipt(txn_hash)

    # 引き出し（withdrawAll)
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon_exchange.transact().withdrawAll(coupon.address)
    chain.wait.for_receipt(txn_hash)

    balance_coupon = coupon.call().balanceOf(_issuer)
    balance_exchange = coupon_exchange.call().balances(_issuer, coupon.address)

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
    coupon, deploy_args = utils.\
        issue_transferable_coupon(web3, chain, coupon_exchange.address)

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
    balance_exchange = coupon_exchange.call().balances(_issuer, coupon.address)

    assert balance_coupon == deploy_args[2]
    assert balance_exchange == 0

# エラー系１：入力値の型誤り
def test_withdrawAll_error_1(web3, chain, users, coupon_exchange):
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
    coupon, deploy_args = utils.\
        issue_transferable_coupon(web3, chain, coupon_exchange.address)

    # 引き出し（withdrawAll)
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon_exchange.transact().withdrawAll(coupon.address) # エラーになる
    chain.wait.for_receipt(txn_hash)

    balance_coupon = coupon.call().balanceOf(_issuer)
    balance_exchange = coupon_exchange.call().balances(_issuer, coupon.address)

    assert balance_coupon == deploy_args[2]
    assert balance_exchange == 0

# エラー系2-2：残高がゼロ（デポジットあり）
def test_withdrawAll_error_2_2(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _consumer = users['trader']
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.\
        issue_transferable_coupon(web3, chain, coupon_exchange.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().allocate(coupon_exchange.address, _value)
    chain.wait.for_receipt(txn_hash)

    # アカウントアドレスへの割当（Transfer)
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon_exchange.transact().transfer(
        coupon.address, _consumer, _value)
    chain.wait.for_receipt(txn_hash)

    # 引き出し（withdrawAll)
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon_exchange.transact().withdrawAll(coupon.address) # エラーになる
    chain.wait.for_receipt(txn_hash)

    balance_coupon = coupon.call().balanceOf(_issuer)
    balance_exchange = coupon_exchange.call().balances(_issuer, coupon.address)

    assert balance_coupon == deploy_args[2] - _value
    assert balance_exchange == 0

# エラー系3：クーポントークンが無効化
def test_withdrawAll_error_3(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _consumer = users['trader']
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.\
        issue_transferable_coupon(web3, chain, coupon_exchange.address)

    # Exchangeへのデポジット
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().allocate(coupon_exchange.address, _value)
    chain.wait.for_receipt(txn_hash)

    # ステータスを「無効」に変更
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().updateStatus(False)
    chain.wait.for_receipt(txn_hash)

    # 引き出し（withdrawAll)
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon_exchange.transact().withdrawAll(coupon.address) # エラーになる
    chain.wait.for_receipt(txn_hash)

    balance_coupon = coupon.call().balanceOf(_issuer)
    balance_exchange = coupon_exchange.call().balances(_issuer, coupon.address)

    assert balance_coupon == deploy_args[2] - _value
    assert balance_exchange == _value
