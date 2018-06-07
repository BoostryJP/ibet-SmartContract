import pytest
from ethereum.tester import TransactionFailed
from eth_utils import to_checksum_address
import utils

token_template = 'some_template'

'''
TEST1_トークン情報を登録（register）
　※本来は"register"ファンクションに対するテストが正しいが、populusでのテストが実行できないため、
　一部機能を削った"test_register"ファンクションに対してテストを実施している。
'''

# 正常系1: 新規登録
def test_register_normal_1(web3, chain, users):
    admin = users['admin']
    issuer = users['issuer']

    # TokenListコントラクト作成
    web3.eth.defaultAccount = admin
    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')

    # Token新規発行
    web3.eth.defaultAccount = issuer
    bond_token = utils.issue_bond_token(web3, chain, users)
    token_address = bond_token.address

    # TokenListに追加
    txn_hash = tokenlist_contract.transact().register(token_address, token_template)
    chain.wait.for_receipt(txn_hash)

    # Owner Address が正しいことを確認
    owner_address = tokenlist_contract.call().getOwnerAddress(token_address)
    assert owner_address == issuer

    # 登録後のリストの長さが正しいことを確認
    list_length = tokenlist_contract.call().getListLength()
    assert list_length == 1

    # 登録情報の内容が正しいことを確認（アドレス検索）
    token_by_address = tokenlist_contract.call().getTokenByAddress(token_address)
    assert token_by_address[0] == to_checksum_address(token_address)
    assert token_by_address[1] == token_template
    assert token_by_address[2] == to_checksum_address(issuer)

    # 登録情報の内容が正しいことを確認（リスト番号指定）
    token_by_num = tokenlist_contract.call().getTokenByNum(0)
    assert token_by_num[0] == to_checksum_address(token_address)
    assert token_by_num[1] == token_template
    assert token_by_num[2] == to_checksum_address(issuer)


# エラー系1: トークンアドレスの型（address）が正しくない場合
def test_register_error_1(web3, chain, users):
    admin = users['admin']
    issuer = users['issuer']

    # TokenListコントラクト作成
    web3.eth.defaultAccount = admin
    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')

    # 新規登録 -> Failure
    web3.eth.defaultAccount = issuer
    token_address = 'some_token_address'
    with pytest.raises(TypeError):
        tokenlist_contract.transact().register(token_address, token_template)


# エラー系2: トークンテンプレートの型（string）が正しくない場合
def test_register_error_2(web3, chain, users):
    admin = users['admin']
    issuer = users['issuer']

    # TokenListコントラクト作成
    web3.eth.defaultAccount = admin
    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')

    # Token新規発行
    web3.eth.defaultAccount = issuer
    bond_token = utils.issue_bond_token(web3, chain, users)
    token_address = bond_token.address

    # 新規登録 -> Failure
    web3.eth.defaultAccount = issuer
    token_template = 1234
    with pytest.raises(TypeError):
        tokenlist_contract.transact().register(token_address, token_template)


# エラー系3: 同一トークンを複数回登録
def test_register_error_3(web3, chain, users):
    admin = users['admin']
    issuer = users['issuer']

    # TokenListコントラクト作成
    web3.eth.defaultAccount = admin
    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')

    # Token新規発行
    web3.eth.defaultAccount = issuer
    bond_token = utils.issue_bond_token(web3, chain, users)
    token_address = bond_token.address

    # 新規登録（1回目） -> Success
    web3.eth.defaultAccount = issuer
    txn_hash = tokenlist_contract.transact().register(token_address, token_template)
    chain.wait.for_receipt(txn_hash)

    # 新規登録（2回目） -> Failure
    web3.eth.defaultAccount = issuer
    txn_hash = tokenlist_contract.transact().register(token_address, token_template)
    chain.wait.for_receipt(txn_hash)

    # 登録後のリストの長さが正しいことを確認
    list_length = tokenlist_contract.call().getListLength()
    assert list_length == 1

    # 登録情報の内容が正しいことを確認（アドレス検索）
    token_by_address = tokenlist_contract.call().getTokenByAddress(token_address)
    assert token_by_address[0] == to_checksum_address(token_address)
    assert token_by_address[1] == token_template
    assert token_by_address[2] == to_checksum_address(issuer)

    # 登録情報の内容が正しいことを確認（リスト番号指定）
    token_by_num = tokenlist_contract.call().getTokenByNum(0)
    assert token_by_num[0] == to_checksum_address(token_address)
    assert token_by_num[1] == token_template
    assert token_by_num[2] == to_checksum_address(issuer)


# エラー系4: 異なるアドレスから同一トークンを登録
def test_register_error_4(web3, chain, users):
    admin = users['admin']
    issuer = users['issuer']

    # TokenListコントラクト作成
    web3.eth.defaultAccount = admin
    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')

    # Token新規発行
    web3.eth.defaultAccount = issuer
    bond_token = utils.issue_bond_token(web3, chain, users)
    token_address = bond_token.address

    # 新規登録（account_1） -> Success
    web3.eth.defaultAccount = issuer
    txn_hash = tokenlist_contract.transact().register(token_address, token_template)
    chain.wait.for_receipt(txn_hash)

    # 新規登録（account_2） -> Failure
    web3.eth.defaultAccount = admin
    txn_hash = tokenlist_contract.transact().register(token_address, token_template)
    chain.wait.for_receipt(txn_hash)

    # 登録後のリストの長さが正しいことを確認
    list_length = tokenlist_contract.call().getListLength()
    assert list_length == 1

    # 登録情報の内容が正しいことを確認（アドレス検索）
    token_by_address = tokenlist_contract.call().getTokenByAddress(token_address)
    assert token_by_address[0] == to_checksum_address(token_address)
    assert token_by_address[1] == token_template
    assert token_by_address[2] == to_checksum_address(issuer)

    # 登録情報の内容が正しいことを確認（リスト番号指定）
    token_by_num = tokenlist_contract.call().getTokenByNum(0)
    assert token_by_num[0] == to_checksum_address(token_address)
    assert token_by_num[1] == token_template
    assert token_by_num[2] == to_checksum_address(issuer)


'''
TEST2_オーナーを変更（changeOwner）
'''

# 正常系1: オーナー変更
def test_changeOwner_normal_1(web3, chain, users):
    admin = users['admin']
    issuer = users['issuer']
    new_owner_address = admin

    # TokenListコントラクト作成
    web3.eth.defaultAccount = admin
    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')

    # Token新規発行
    web3.eth.defaultAccount = issuer
    bond_token = utils.issue_bond_token(web3, chain, users)
    token_address = bond_token.address

    # 新規登録 -> Success
    web3.eth.defaultAccount = issuer
    txn_hash_1 = tokenlist_contract.transact().register(token_address, token_template)
    chain.wait.for_receipt(txn_hash_1)

    # オーナー変更 -> Success
    web3.eth.defaultAccount = issuer
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
    assert token_by_address[0] == to_checksum_address(token_address)
    assert token_by_address[1] == token_template
    assert token_by_address[2] == to_checksum_address(new_owner_address)

    # 登録情報の内容が正しいことを確認（リスト番号指定）
    token_by_num = tokenlist_contract.call().getTokenByNum(0)
    assert token_by_num[0] == to_checksum_address(token_address)
    assert token_by_num[1] == token_template
    assert token_by_num[2] == to_checksum_address(new_owner_address)


# エラー系1: トークンアドレスの型（address）が正しくない場合
def test_changeOwner_error_1(web3, chain, users):
    admin = users['admin']
    issuer = users['issuer']
    new_owner_address = admin

    # TokenListコントラクト作成
    web3.eth.defaultAccount = admin
    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')

    token_address = 'some_token_address'

    # 新規登録 -> Failure
    with pytest.raises(TypeError):
        tokenlist_contract.transact().changeOwner(token_address, new_owner_address)


# エラー系2: オーナーアドレスの型（address）が正しくない場合
def test_changeOwner_error_2(web3, chain, users):
    admin = users['admin']
    issuer = users['issuer']
    new_owner_address = admin

    # TokenListコントラクト作成
    web3.eth.defaultAccount = admin
    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')

    # Token新規発行
    web3.eth.defaultAccount = issuer
    bond_token = utils.issue_bond_token(web3, chain, users)
    token_address = bond_token.address

    new_owner_address = 'some_address'

    # 新規登録 -> Failure
    with pytest.raises(TypeError):
        tokenlist_contract.transact().changeOwner(token_address, new_owner_address)


# エラー系3: 登録なし -> オーナー変更
def test_changeOwner_error_3(web3, chain, users):
    admin = users['admin']
    issuer = users['issuer']
    new_owner_address = users['issuer']

    # TokenListコントラクト作成
    web3.eth.defaultAccount = admin
    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')

    # Token新規発行
    web3.eth.defaultAccount = issuer
    bond_token = utils.issue_bond_token(web3, chain, users)
    token_address = bond_token.address

    # オーナー変更 -> Failure
    web3.eth.defaultAccount = issuer
    txn_hash = tokenlist_contract.transact().changeOwner(token_address, new_owner_address)
    chain.wait.for_receipt(txn_hash)

    owner_address = tokenlist_contract.call().getOwnerAddress(token_address)
    assert owner_address == '0x0000000000000000000000000000000000000000'


# エラー系4: オーナー権限のないアドレスでオーナー変更を実施した場合
def test_changeOwner_error_4(web3, chain, users):
    admin = users['admin']
    issuer = users['issuer']
    new_owner_address = users['issuer']

    # TokenListコントラクト作成
    web3.eth.defaultAccount = admin
    tokenlist_contract, _ = chain.provider.get_or_deploy_contract('TokenList')

    # Token新規発行
    web3.eth.defaultAccount = issuer
    bond_token = utils.issue_bond_token(web3, chain, users)
    token_address = bond_token.address

    # 新規登録 -> Success
    web3.eth.defaultAccount = issuer
    txn_hash_1 = tokenlist_contract.transact().register(token_address, token_template)
    chain.wait.for_receipt(txn_hash_1)

    # オーナー変更 -> Failure
    web3.eth.defaultAccount = admin
    txn_hash = tokenlist_contract.transact().changeOwner(token_address, new_owner_address)
    chain.wait.for_receipt(txn_hash)

    owner_address = tokenlist_contract.call().getOwnerAddress(token_address)
    assert owner_address == to_checksum_address(issuer)
