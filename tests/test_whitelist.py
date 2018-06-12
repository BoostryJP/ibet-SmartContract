import pytest
from ethereum.tester import TransactionFailed

encrypted_message = 'encrypted_message'
encrypted_message_after = 'encrypted_message_after'

'''
TEST1_支払情報を登録（register）
'''

# 正常系1: 新規登録
def test_register_normal_1(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # WhiteList登録
    web3.eth.defaultAccount = trader
    txn_hash = whitelist_contract.transact().register(agent,encrypted_message)
    chain.wait.for_receipt(txn_hash)

    payment_account = whitelist_contract.call().payment_accounts(trader, agent)
    is_registered = whitelist_contract.call().isRegistered(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert is_registered == False


# エラー系1:入力値の型誤り（agent address）
def test_register_error_1(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = 1234

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # WhiteList登録 -> Failure
    web3.eth.defaultAccount = trader
    with pytest.raises(TypeError):
        whitelist_contract.transact().register(agent,encrypted_message)


# エラー系2:入力値の型誤り（encrypted_info）
def test_register_error_2(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # WhiteList登録 -> Failure
    web3.eth.defaultAccount = trader
    encrypted_message = 1234
    with pytest.raises(TypeError):
        whitelist_contract.transact().register(agent,encrypted_message)


# エラー系3: 既に登録済みのアカウントの場合
def test_register_error_3(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 新規登録 -> Success
    web3.eth.defaultAccount = trader
    txn_hash = whitelist_contract.transact().register(agent,encrypted_message)
    chain.wait.for_receipt(txn_hash)

    # 2回目登録 -> Failure
    web3.eth.defaultAccount = trader
    txn_hash = whitelist_contract.transact().register(agent,encrypted_message_after)
    chain.wait.for_receipt(txn_hash)

    payment_account = whitelist_contract.call().payment_accounts(trader, agent)
    is_registered = whitelist_contract.call().isRegistered(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert is_registered == False


'''
TEST2_支払情報の更新(changeInfo)
'''

# 正常系1: 新規登録 -> 更新
def test_changeInfo_normal_1(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 新規登録 -> Success
    web3.eth.defaultAccount = trader
    txn_hash_1 = whitelist_contract.transact().register(agent,encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # 更新 -> Success
    web3.eth.defaultAccount = trader
    txn_hash_2 = whitelist_contract.transact().changeInfo(agent,encrypted_message_after)
    chain.wait.for_receipt(txn_hash_2)

    payment_account = whitelist_contract.call().payment_accounts(trader, agent)
    is_registered = whitelist_contract.call().isRegistered(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message_after
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert is_registered == False


# 正常系2: 新規登録 -> 承認 -> 更新
# 認可状態が未認可の状態に戻る
def test_changeInfo_normal_2(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 新規登録 -> Success
    web3.eth.defaultAccount = trader
    txn_hash_1 = whitelist_contract.transact().register(agent,encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # 承認 -> Success
    web3.eth.defaultAccount = agent
    txn_hash_2 = whitelist_contract.transact().approve(trader)
    chain.wait.for_receipt(txn_hash_2)

    # 更新 -> Success
    web3.eth.defaultAccount = trader
    txn_hash_3 = whitelist_contract.transact().changeInfo(agent,encrypted_message_after)
    chain.wait.for_receipt(txn_hash_3)

    payment_account = whitelist_contract.call().payment_accounts(trader, agent)
    is_registered = whitelist_contract.call().isRegistered(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message_after
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert is_registered == False


# エラー系1: 登録なし -> 更新
def test_changeInfo_error_1(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 更新 -> Success
    web3.eth.defaultAccount = trader
    txn_hash = whitelist_contract.transact().changeInfo(agent,encrypted_message_after)
    chain.wait.for_receipt(txn_hash)

    payment_account = whitelist_contract.call().payment_accounts(trader, agent)
    assert payment_account[0] == '0x0000000000000000000000000000000000000000'


# エラー系2: 新規登録 -> BAN -> 更新
def test_changeInfo_error_2(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 新規登録 -> Success
    web3.eth.defaultAccount = trader
    txn_hash_1 = whitelist_contract.transact().register(agent,encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # BAN -> Success
    web3.eth.defaultAccount = agent
    txn_hash_2 = whitelist_contract.transact().ban(trader)
    chain.wait.for_receipt(txn_hash_2)

    # 更新 -> Failure
    web3.eth.defaultAccount = trader
    txn_hash_3 = whitelist_contract.transact().changeInfo(agent,encrypted_message_after)
    chain.wait.for_receipt(txn_hash_3)

    payment_account = whitelist_contract.call().payment_accounts(trader, agent)
    is_registered = whitelist_contract.call().isRegistered(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 4

    # 認可状態が未認可の状態であることを確認
    assert is_registered == False


'''
TEST3_支払情報を承認する(approve)
'''

# 正常系1: 新規登録 -> 承認
def test_approve_normal_1(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 新規登録 -> Success
    web3.eth.defaultAccount = trader
    txn_hash_1 = whitelist_contract.transact().register(agent,encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # 承認 -> Success
    web3.eth.defaultAccount = agent
    txn_hash_2 = whitelist_contract.transact().approve(trader)
    chain.wait.for_receipt(txn_hash_2)

    payment_account = whitelist_contract.call().payment_accounts(trader, agent)
    is_registered = whitelist_contract.call().isRegistered(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 2

    # 認可状態が認可の状態であることを確認
    assert is_registered == True


# エラー系1: 入力値の型誤り
def test_approve_error_1(web3, chain, users):
    admin = users['admin']
    trader = 1234
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 承認 -> Failure
    web3.eth.defaultAccount = agent
    with pytest.raises(TypeError):
        whitelist_contract.transact().approve(trader)


# エラー系2: 登録なし -> 承認
def test_approve_error_2(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 承認 -> Failure
    web3.eth.defaultAccount = agent
    txn_hash = whitelist_contract.transact().approve(trader)

    payment_account = whitelist_contract.call().payment_accounts(trader, agent)

    assert payment_account[0] == '0x0000000000000000000000000000000000000000'


'''
TEST4_支払情報を警告状態にする(warn)
'''

# 正常系1: 新規登録 -> 警告
def test_warn_normal_1(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 新規登録 -> Success
    web3.eth.defaultAccount = trader
    txn_hash_1 = whitelist_contract.transact().register(agent, encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # 警告 -> Success
    web3.eth.defaultAccount = agent
    txn_hash_2 = whitelist_contract.transact().warn(trader)
    chain.wait.for_receipt(txn_hash_2)

    payment_account = whitelist_contract.call().payment_accounts(trader, agent)
    is_registered = whitelist_contract.call().isRegistered(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 3

    # 認可状態が未認可の状態であることを確認
    assert is_registered == False


# エラー系1: 入力値の型誤り
def test_warn_error_1(web3, chain, users):
    admin = users['admin']
    trader = 1234
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 承認 -> Failure
    web3.eth.defaultAccount = agent
    with pytest.raises(TypeError):
        whitelist_contract.transact().warn(trader)


# エラー系2: 登録なし -> 警告
def test_warn_error_2(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 警告 -> Failure
    web3.eth.defaultAccount = agent
    txn_hash = whitelist_contract.transact().warn(trader)

    payment_account = whitelist_contract.call().payment_accounts(trader, agent)

    assert payment_account[0] == '0x0000000000000000000000000000000000000000'


'''
TEST5_支払情報を非承認にする(unapprove)
'''

# 正常系1: 新規登録 -> 非承認
def test_unapprove_normal_1(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 新規登録 -> Success
    web3.eth.defaultAccount = trader
    txn_hash_1 = whitelist_contract.transact().register(agent, encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # 非承認 -> Success
    web3.eth.defaultAccount = agent
    txn_hash_2 = whitelist_contract.transact().unapprove(trader)
    chain.wait.for_receipt(txn_hash_2)

    payment_account = whitelist_contract.call().payment_accounts(trader, agent)
    is_registered = whitelist_contract.call().isRegistered(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert is_registered == False


# 正常系2: 新規登録 -> 承認 -> 非承認
# 認可状態が未認可の状態に戻る
def test_unapprove_normal_2(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 新規登録 -> Success
    web3.eth.defaultAccount = trader
    txn_hash_1 = whitelist_contract.transact().register(agent, encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # 承認 -> Success、　認可状態
    web3.eth.defaultAccount = agent
    txn_hash_2 = whitelist_contract.transact().approve(trader)
    chain.wait.for_receipt(txn_hash_2)

    # 非承認 -> Success。　未認可状態
    web3.eth.defaultAccount = agent
    txn_hash_3 = whitelist_contract.transact().unapprove(trader)
    chain.wait.for_receipt(txn_hash_3)

    payment_account = whitelist_contract.call().payment_accounts(trader, agent)
    is_registered = whitelist_contract.call().isRegistered(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert is_registered == False


# エラー系1: 入力値の型誤り
def test_unapprove_error_1(web3, chain, users):
    admin = users['admin']
    trader = 1234
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 非承認 -> Failure
    web3.eth.defaultAccount = agent
    with pytest.raises(TypeError):
        whitelist_contract.transact().unapprove(trader)


# エラー系2: 登録なし -> 非承認
def test_unapprove_error_2(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 非承認 -> Failure
    web3.eth.defaultAccount = agent
    txn_hash = whitelist_contract.transact().unapprove(trader)

    payment_account = whitelist_contract.call().payment_accounts(trader, agent)

    assert payment_account[0] == '0x0000000000000000000000000000000000000000'


'''
TEST5_支払情報をBAN状態にする(ban)
'''

# 正常系1: 新規登録 -> BAN
def test_ban_normal_1(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 新規登録 -> Success
    web3.eth.defaultAccount = trader
    txn_hash_1 = whitelist_contract.transact().register(agent, encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # BAN -> Success
    web3.eth.defaultAccount = agent
    txn_hash_2 = whitelist_contract.transact().ban(trader)
    chain.wait.for_receipt(txn_hash_2)

    payment_account = whitelist_contract.call().payment_accounts(trader, agent)
    is_registered = whitelist_contract.call().isRegistered(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 4

    # 認可状態が未認可の状態であることを確認
    assert is_registered == False


# エラー系1: 入力値の型誤り
def test_ban_error_1(web3, chain, users):
    admin = users['admin']
    trader = 1234
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # 承認 -> Failure
    web3.eth.defaultAccount = agent
    with pytest.raises(TypeError):
        whitelist_contract.transact().ban(trader)


# エラー系2: 登録なし -> BAN
def test_ban_error_2(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # WhiteListデプロイ
    web3.eth.defaultAccount = admin
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    # BAN -> Failure
    web3.eth.defaultAccount = agent
    txn_hash = whitelist_contract.transact().ban(trader)

    payment_account = whitelist_contract.call().payment_accounts(trader, agent)

    assert payment_account[0] == '0x0000000000000000000000000000000000000000'
