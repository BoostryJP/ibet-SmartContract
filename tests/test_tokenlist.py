import pytest
from ethereum.tester import TransactionFailed
from eth_utils import to_checksum_address

token_template = 'some_template'
token_address = to_checksum_address('0xd950a0ba53af3f4f295500eee692598e31166ad9')

'''
TEST1_トークン情報を登録（register）
'''

# 正常系1: 新規登録
def test_register_normal_1(web3,chain):
    account_address = web3.eth.accounts[0]

    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')
    txn_hash = tokenlist_contract.transact().register(token_address, token_template)
    chain.wait.for_receipt(txn_hash)

    # Owner Address が正しいことを確認
    owner_address = tokenlist_contract.call().getOwnerAddress(token_address)
    assert owner_address == account_address

    # 登録後のリストの長さが正しいことを確認
    list_length = tokenlist_contract.call().getListLength()
    assert list_length == 1

    # 登録情報の内容が正しいことを確認（アドレス検索）
    token_by_address = tokenlist_contract.call().getTokenByAddress(token_address)
    assert token_by_address[0] == token_address
    assert token_by_address[1] == token_template
    assert token_by_address[2] == account_address

    # 登録情報の内容が正しいことを確認（リスト番号指定）
    token_by_num = tokenlist_contract.call().getTokenByNum(0)
    assert token_by_num[0] == token_address
    assert token_by_num[1] == token_template
    assert token_by_num[2] == account_address


# 正常系2: 新規登録（複数トークンの登録）
def test_register_normal_2(web3,chain):
    account_address = web3.eth.accounts[0]

    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')

    # 新規登録（1回目）
    txn_hash_1 = tokenlist_contract.transact().register(token_address, token_template)
    chain.wait.for_receipt(txn_hash_1)

    # 新規登録（2回目）
    token_address_2 = to_checksum_address('0xd950a0ba53af3f4f295500eee692598e31166ad8')
    txn_hash_2 = tokenlist_contract.transact().register(token_address_2, token_template)
    chain.wait.for_receipt(txn_hash_2)

    # Owner Address が正しいことを確認
    owner_address = tokenlist_contract.call().getOwnerAddress(token_address_2)
    assert owner_address == account_address

    # 登録後のリストの長さが正しいことを確認
    list_length = tokenlist_contract.call().getListLength()
    assert list_length == 2

    # 登録情報の内容が正しいことを確認（アドレス検索）
    token_by_address = tokenlist_contract.call().getTokenByAddress(token_address_2)
    assert token_by_address[0] == token_address_2
    assert token_by_address[1] == token_template
    assert token_by_address[2] == account_address

    # 登録情報の内容が正しいことを確認（リスト番号指定）
    token_by_num = tokenlist_contract.call().getTokenByNum(1)
    assert token_by_num[0] == token_address_2
    assert token_by_num[1] == token_template
    assert token_by_num[2] == account_address


# エラー系1: トークンアドレスの型（address）が正しくない場合
def test_register_error_1(web3,chain):
    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')
    token_address = 'some_token_address'

    # 新規登録 -> Failure
    with pytest.raises(TypeError):
        tokenlist_contract.transact().register(token_address, token_template)


# エラー系2: トークンテンプレートの型（string）が正しくない場合
def test_register_error_2(web3,chain):
    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')
    token_template = 1234

    # 新規登録 -> Failure
    with pytest.raises(TypeError):
        tokenlist_contract.transact().register(token_address, token_template)


# エラー系3: 同一トークンを複数回登録
def test_register_error_3(web3,chain):
    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')

    # 新規登録（1回目） -> Success
    txn_hash = tokenlist_contract.transact().register(token_address, token_template)
    chain.wait.for_receipt(txn_hash)

    # 新規登録（2回目） -> Failure
    with pytest.raises(TransactionFailed):
        tokenlist_contract.transact().register(token_address, token_template)


# エラー系4: 異なるアドレスから同一トークンを登録
def test_register_error_4(web3,chain):
    account_address_1 = web3.eth.accounts[0]
    account_address_2 = web3.eth.accounts[1]

    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')

    # 新規登録（account_1） -> Success
    web3.eth.defaultAccount = account_address_1
    txn_hash = tokenlist_contract.transact().register(token_address, token_template)
    chain.wait.for_receipt(txn_hash)

    # 新規登録（account_2） -> Failure
    web3.eth.defaultAccount = account_address_2
    with pytest.raises(TransactionFailed):
        tokenlist_contract.transact().register(token_address, token_template)


'''
TEST2_オーナーを変更（changeOwner）
'''

# 正常系1: オーナー変更
def test_changeOwner_normal_1(web3,chain):
    account_address = web3.eth.accounts[0]
    new_owner_address = web3.eth.accounts[1]

    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')

    # 新規登録 -> Success
    txn_hash_1 = tokenlist_contract.transact().register(token_address, token_template)
    chain.wait.for_receipt(txn_hash_1)

    # オーナー変更 -> Success
    txn_hash_2 = tokenlist_contract.transact().changeOwner(token_address, new_owner_address)
    chain.wait.for_receipt(txn_hash_2)

    # Owner Address が正しいことを確認
    owner_address = tokenlist_contract.call().getOwnerAddress(token_address)
    assert owner_address == new_owner_address

    # 登録後のリストの長さが正しいことを確認
    list_length = tokenlist_contract.call().getListLength()
    assert list_length == 1

    # 登録情報の内容が正しいことを確認（アドレス検索）
    token_by_address = tokenlist_contract.call().getTokenByAddress(token_address)
    assert token_by_address[0] == token_address
    assert token_by_address[1] == token_template
    assert token_by_address[2] == new_owner_address

    # 登録情報の内容が正しいことを確認（リスト番号指定）
    token_by_num = tokenlist_contract.call().getTokenByNum(0)
    assert token_by_num[0] == token_address
    assert token_by_num[1] == token_template
    assert token_by_num[2] == new_owner_address


# エラー系1: トークンアドレスの型（address）が正しくない場合
def test_changeOwner_error_1(web3,chain):
    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')
    new_owner_address = web3.eth.accounts[1]
    token_address = 'some_token_address'

    # 新規登録 -> Failure
    with pytest.raises(TypeError):
        tokenlist_contract.transact().changeOwner(token_address, new_owner_address)


# エラー系2: オーナーアドレスの型（address）が正しくない場合
def test_changeOwner_error_2(web3,chain):
    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')
    new_owner_address = 'some_address'

    # 新規登録 -> Failure
    with pytest.raises(TypeError):
        tokenlist_contract.transact().changeOwner(token_address, new_owner_address)


# エラー系3: 登録なし -> オーナー変更
def test_changeOwner_error_3(web3,chain):
    new_owner_address = web3.eth.accounts[1]

    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')

    # オーナー変更 -> Failure
    with pytest.raises(TransactionFailed):
        tokenlist_contract.transact().changeOwner(token_address, new_owner_address)


# エラー系4: オーナー権限のないアドレスでオーナー変更を実施した場合
def test_changeOwner_error_4(web3,chain):
    account_address = web3.eth.accounts[0]
    account_address_other = web3.eth.accounts[1]
    new_owner_address = web3.eth.accounts[2]

    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')

    # 新規登録 -> Success
    web3.eth.defaultAccount = account_address
    txn_hash_1 = tokenlist_contract.transact().register(token_address, token_template)
    chain.wait.for_receipt(txn_hash_1)

    # オーナー変更 -> Failure
    web3.eth.defaultAccount = account_address_other
    with pytest.raises(TransactionFailed):
        tokenlist_contract.transact().changeOwner(token_address, new_owner_address)
