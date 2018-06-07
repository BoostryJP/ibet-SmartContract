import pytest
from ethereum.tester import TransactionFailed
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
TEST2_新規注文（買）：createOrder
'''
def test_createorder_buy_normal_1(web3, chain, users,
    bond_exchange, personal_info, white_list):
    trader = users['issuer']
    issuer = users['issuer']
    agent = users['agent']

    personalinfo_register(web3, chain, personal_info, trader, issuer)
    whitelist_register(web3, chain, white_list, trader, agent)
    whitelist_approve(web3, chain, white_list, trader, agent)

    bond_token = utils.issue_bond_token(web3, chain, users)

    web3.eth.defaultAccount = trader

    txn_hash = bond_exchange.transact().createOrder(
        bond_token.address,
        100, 123, True, agent
        )

    chain.wait.for_receipt(txn_hash)
