import pytest

encrypted_message = 'encrypted_message'
encrypted_message_after = 'encrypted_message_after'

'''
TEST1_個人情報を登録（register）
'''

# 正常系1: 新規登録
def test_register_normal_1(web3,chain):
    account_address = web3.eth.accounts[0]
    issuer_address = web3.eth.accounts[1]

    personalinfo_contract, _ = chain.provider.get_or_deploy_contract('PersonalInfo')
    txn_hash = personalinfo_contract.transact().register(issuer_address, encrypted_message)
    chain.wait.for_receipt(txn_hash)

    personal_info = personalinfo_contract.call().personal_info(account_address, issuer_address)
    is_registered = personalinfo_contract.call().isRegistered(account_address, issuer_address)

    # 登録情報の内容が正しいことを確認
    assert personal_info[0] == account_address
    assert personal_info[1] == issuer_address
    assert personal_info[2] == encrypted_message

    # 登録状態が登録済みの状態であることを確認
    assert is_registered == True


# 正常系2: 上書き登録
def test_register_normal_2(web3,chain):
    account_address = web3.eth.accounts[0]
    issuer_address = web3.eth.accounts[1]

    personalinfo_contract, _ = chain.provider.get_or_deploy_contract('PersonalInfo')

    # 登録（1回目） -> Success
    txn_hash_1 = personalinfo_contract.transact().register(issuer_address, encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # 登録（2回目） -> Success
    txn_hash_2 = personalinfo_contract.transact().register(issuer_address, encrypted_message_after)
    chain.wait.for_receipt(txn_hash_2)

    personal_info = personalinfo_contract.call().personal_info(account_address, issuer_address)
    is_registered = personalinfo_contract.call().isRegistered(account_address, issuer_address)

    # 登録情報の内容が正しいことを確認
    assert personal_info[0] == account_address
    assert personal_info[1] == issuer_address
    assert personal_info[2] == encrypted_message_after

    # 登録状態が登録済みの状態であることを確認
    assert is_registered == True


# 正常系3: 未登録のアドレスの情報参照
def test_register_normal_3(web3,chain):
    account_address = web3.eth.accounts[0]
    issuer_address = web3.eth.accounts[1]

    personalinfo_contract, _ = chain.provider.get_or_deploy_contract('PersonalInfo')

    personal_info = personalinfo_contract.call().personal_info(account_address, issuer_address)
    is_registered = personalinfo_contract.call().isRegistered(account_address, issuer_address)

    # 登録情報の内容が正しいことを確認
    assert personal_info[0] == '0x0000000000000000000000000000000000000000'
    assert personal_info[1] == '0x0000000000000000000000000000000000000000'
    assert personal_info[2] == ''

    # 登録状態が登録済みの状態であることを確認
    assert is_registered == False


# エラー系1: 入力値の型誤り（発行体アドレス）
def test_register_error_1(web3,chain):
    account_address = web3.eth.accounts[0]
    issuer_address = 'aaaa'

    personalinfo_contract, _ = chain.provider.get_or_deploy_contract('PersonalInfo')

    # 登録 -> Failure
    with pytest.raises(TypeError):
        personalinfo_contract.transact().register(issuer_address,encrypted_message)


# エラー系2: 入力値の型誤り（暗号化情報）
def test_register_error_2(web3,chain):
    account_address = web3.eth.accounts[0]
    issuer_address = web3.eth.accounts[1]
    encrypted_message = 1234

    personalinfo_contract, _ = chain.provider.get_or_deploy_contract('PersonalInfo')

    # 登録 -> Failure
    with pytest.raises(TypeError):
        personalinfo_contract.transact().register(issuer_address,encrypted_message)
