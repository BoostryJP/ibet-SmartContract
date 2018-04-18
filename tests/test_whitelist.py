import pytest
from ethereum.tester import TransactionFailed
from populus.config import Web3Config

encrypted_message = 'encrypted_message'
encrypted_message_after = 'encrypted_message_after'

'''
TEST1_支払情報を登録（register）
'''

# 正常系1: 新規登録
def test_register_normal_1(web3,chain):
    account_address = web3.eth.accounts[0]
    agent_address = web3.eth.accounts[1]

    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')
    txn_hash = whitelist_contract.transact().register(agent_address,encrypted_message)
    chain.wait.for_receipt(txn_hash)

    payment_account = whitelist_contract.call().payment_accounts(account_address, agent_address)
    is_registered = whitelist_contract.call().isRegistered(account_address, agent_address)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == account_address
    assert payment_account[1] == agent_address
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert is_registered == False


# エラー系1: 既に登録済みのアカウントの場合
def test_register_error_1(web3,chain):
    account_address = web3.eth.accounts[0]
    agent_address = web3.eth.accounts[1]

    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 新規登録 -> Success
    txn_hash = whitelist_contract.transact().register(agent_address,encrypted_message)
    chain.wait.for_receipt(txn_hash)

    # 2回目登録 -> Failure
    with pytest.raises(TransactionFailed):
        whitelist_contract.transact().register(agent_address,encrypted_message)


'''
TEST2_支払情報の更新(changeInfo)
'''

# 正常系1: 新規登録 -> 更新
def test_changeInfo_normal_1(web3,chain):
    account_address = web3.eth.accounts[0]
    agent_address = web3.eth.accounts[1]

    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 新規登録 -> Success
    txn_hash_1 = whitelist_contract.transact().register(agent_address,encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # 更新 -> Success
    txn_hash_2 = whitelist_contract.transact().changeInfo(agent_address,encrypted_message_after)
    chain.wait.for_receipt(txn_hash_2)

    payment_account = whitelist_contract.call().payment_accounts(account_address, agent_address)
    is_registered = whitelist_contract.call().isRegistered(account_address, agent_address)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == account_address
    assert payment_account[1] == agent_address
    assert payment_account[2] == encrypted_message_after
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert is_registered == False


# 正常系2: 新規登録 -> 承認 -> 更新
# 認可状態が未認可の状態に戻る
def test_changeInfo_normal_2(web3,chain):
    account_address = web3.eth.accounts[0]
    agent_address = web3.eth.accounts[1]

    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 新規登録 -> Success
    txn_hash_1 = whitelist_contract.transact().register(agent_address,encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # 承認 -> Success
    web3.eth.defaultAccount = agent_address
    txn_hash_2 = whitelist_contract.transact().approve(account_address)
    chain.wait.for_receipt(txn_hash_2)

    # 更新 -> Success
    web3.eth.defaultAccount = account_address
    txn_hash_3 = whitelist_contract.transact().changeInfo(agent_address,encrypted_message_after)
    chain.wait.for_receipt(txn_hash_3)

    payment_account = whitelist_contract.call().payment_accounts(account_address, agent_address)
    is_registered = whitelist_contract.call().isRegistered(account_address, agent_address)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == account_address
    assert payment_account[1] == agent_address
    assert payment_account[2] == encrypted_message_after
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert is_registered == False


# エラー系1: 登録なし -> 更新
def test_changeInfo_error_1(web3,chain):
    agent_address = web3.eth.accounts[1]

    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 更新 -> Failure
    with pytest.raises(TransactionFailed):
        whitelist_contract.transact().changeInfo(agent_address,encrypted_message_after)


'''
TEST3_支払情報を承認する(approve)
'''

# 正常系1: 新規登録 -> 承認
def test_approve_normal_1(web3,chain):
    account_address = web3.eth.accounts[0]
    agent_address = web3.eth.accounts[1]

    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 新規登録 -> Success
    txn_hash_1 = whitelist_contract.transact().register(agent_address, encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # 承認 -> Success
    web3.eth.defaultAccount = agent_address
    txn_hash_2 = whitelist_contract.transact().approve(account_address)
    chain.wait.for_receipt(txn_hash_2)

    payment_account = whitelist_contract.call().payment_accounts(account_address, agent_address)
    is_registered = whitelist_contract.call().isRegistered(account_address, agent_address)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == account_address
    assert payment_account[1] == agent_address
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 2

    # 認可状態が認可の状態であることを確認
    assert is_registered == True


# エラー系1: 登録なし -> 承認
def test_approve_error_1(web3,chain):
    account_address = web3.eth.accounts[0]

    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 承認 -> Failure
    with pytest.raises(TransactionFailed):
        whitelist_contract.transact().approve(account_address)


'''
TEST4_支払情報を警告状態にする(warn)
'''

# 正常系1: 新規登録 -> 警告
def test_warn_normal_1(web3,chain):
    account_address = web3.eth.accounts[0]
    agent_address = web3.eth.accounts[1]

    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 新規登録 -> Success
    txn_hash_1 = whitelist_contract.transact().register(agent_address, encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # 承認 -> Success
    web3.eth.defaultAccount = agent_address
    txn_hash_2 = whitelist_contract.transact().warn(account_address)
    chain.wait.for_receipt(txn_hash_2)

    payment_account = whitelist_contract.call().payment_accounts(account_address, agent_address)
    is_registered = whitelist_contract.call().isRegistered(account_address, agent_address)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == account_address
    assert payment_account[1] == agent_address
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 3

    # 認可状態が未認可の状態であることを確認
    assert is_registered == False


# エラー系1: 登録なし -> 警告
def test_warn_error_1(web3,chain):
    account_address = web3.eth.accounts[0]

    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 承認 -> Failure
    with pytest.raises(TransactionFailed):
        whitelist_contract.transact().warn(account_address)


'''
TEST5_支払情報を非承認にする(unapprove)
'''

# 正常系1: 新規登録 -> 非承認
def test_unapprove_normal_1(web3,chain):
    account_address = web3.eth.accounts[0]
    agent_address = web3.eth.accounts[1]

    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 新規登録 -> Success
    txn_hash_1 = whitelist_contract.transact().register(agent_address, encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # 非承認 -> Success
    web3.eth.defaultAccount = agent_address
    txn_hash_2 = whitelist_contract.transact().unapprove(account_address)
    chain.wait.for_receipt(txn_hash_2)

    payment_account = whitelist_contract.call().payment_accounts(account_address, agent_address)
    is_registered = whitelist_contract.call().isRegistered(account_address, agent_address)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == account_address
    assert payment_account[1] == agent_address
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert is_registered == False


# 正常系2: 新規登録 -> 承認 -> 非承認
# 認可状態が未認可の状態に戻る
def test_unapprove_normal_2(web3,chain):
    account_address = web3.eth.accounts[0]
    agent_address = web3.eth.accounts[1]

    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 新規登録 -> Success
    txn_hash_1 = whitelist_contract.transact().register(agent_address, encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # 承認 -> Success、　認可状態
    web3.eth.defaultAccount = agent_address
    txn_hash_2 = whitelist_contract.transact().approve(account_address)
    chain.wait.for_receipt(txn_hash_2)

    # 非承認 -> Success。　未認可状態
    txn_hash_3 = whitelist_contract.transact().unapprove(account_address)
    chain.wait.for_receipt(txn_hash_3)

    payment_account = whitelist_contract.call().payment_accounts(account_address, agent_address)
    is_registered = whitelist_contract.call().isRegistered(account_address, agent_address)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == account_address
    assert payment_account[1] == agent_address
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert is_registered == False


# エラー系1: 登録なし -> 非承認
def test_unapprove_error_1(web3,chain):
    account_address = web3.eth.accounts[0]

    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 承認 -> Failure
    with pytest.raises(TransactionFailed):
        whitelist_contract.transact().unapprove(account_address)
