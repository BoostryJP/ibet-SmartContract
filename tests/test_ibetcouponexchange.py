import pytest
import utils

'''
TEST1_クーポントークンのデポジット
'''
# 正常系1
# ＜発行体＞新規発行 -> ＜発行体＞Exchangeへのデポジット
def test_deposit_normal_1(web3, chain, users):
    _admin = users['admin']
    _issuer = users['issuer']
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # Exchange
    web3.eth.defaultAccount = _admin
    coupon_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetCouponExchange', deploy_args = [])

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
def test_transfer_normal_1(web3, chain, users):
    _admin = users['admin']
    _issuer = users['issuer']
    _consumer = users['trader']
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # Exchange
    web3.eth.defaultAccount = _admin
    coupon_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetCouponExchange', deploy_args = [])

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
