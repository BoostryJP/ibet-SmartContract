import pytest
from eth_utils import to_checksum_address
import utils

"""
TEST1_取引参加者登録（register）
"""


# 正常系1: 新規登録
def test_register_normal_1(web3, chain, users, membership_exchange):
    admin = users['admin']
    issuer = users['issuer']
    participant = users['trader']

    # TokenRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    token_regulator_service, _ = chain.provider.get_or_deploy_contract('TokenRegulatorService')

    # トークン新規発行
    # NOTE:StandardTokenInterfaceを継承している会員権トークンを発行
    web3.eth.defaultAccount = issuer
    membership, deploy_args = \
        utils.issue_transferable_membership(web3, chain, membership_exchange.address)
    token_address = membership.address

    # 購入可能者リストに登録
    web3.eth.defaultAccount = issuer
    txn_hash = token_regulator_service.transact(). \
        register(token_address, participant, False)
    chain.wait.for_receipt(txn_hash)

    # Whitelist情報の参照
    whitelist = token_regulator_service.call().getWhitelist(token_address, participant)

    # 検証
    assert whitelist[0] == to_checksum_address(token_address)
    assert whitelist[1] == to_checksum_address(participant)
    assert whitelist[2] == False


# 正常系2: 変更登録
def test_register_normal_2(web3, chain, users, membership_exchange):
    admin = users['admin']
    issuer = users['issuer']
    participant = users['trader']

    # TokenRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    token_regulator_service, _ = chain.provider.get_or_deploy_contract('TokenRegulatorService')

    # トークン新規発行
    # NOTE:StandardTokenInterfaceを継承している会員権トークンを発行
    web3.eth.defaultAccount = issuer
    membership, deploy_args = \
        utils.issue_transferable_membership(web3, chain, membership_exchange.address)
    token_address = membership.address

    # 購入可能者リストに登録：１回目
    web3.eth.defaultAccount = issuer
    txn_hash = token_regulator_service.transact(). \
        register(token_address, participant, False)
    chain.wait.for_receipt(txn_hash)

    # 購入可能者リストに登録：２回目
    web3.eth.defaultAccount = issuer
    txn_hash = token_regulator_service.transact(). \
        register(token_address, participant, True)  # Trueに変更
    chain.wait.for_receipt(txn_hash)

    # Whitelist情報の参照
    whitelist = token_regulator_service.call().getWhitelist(token_address, participant)

    # 検証
    assert whitelist[0] == to_checksum_address(token_address)
    assert whitelist[1] == to_checksum_address(participant)
    assert whitelist[2] == True


# エラー系1: 権限なしアカウントからの登録
def test_register_error_1(web3, chain, users, membership_exchange):
    admin = users['admin']
    issuer = users['issuer']
    participant = users['trader']

    # TokenRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    token_regulator_service, _ = chain.provider.get_or_deploy_contract('TokenRegulatorService')

    # トークン新規発行
    # NOTE:StandardTokenInterfaceを継承している会員権トークンを発行
    web3.eth.defaultAccount = issuer
    membership, deploy_args = \
        utils.issue_transferable_membership(web3, chain, membership_exchange.address)
    token_address = membership.address

    # 購入可能者リストに登録：権限なしアカウントからの登録 -> 登録不可
    web3.eth.defaultAccount = participant
    txn_hash = token_regulator_service.transact(). \
        register(token_address, participant, False)
    chain.wait.for_receipt(txn_hash)

    # Whitelist情報の参照
    whitelist = token_regulator_service.call().getWhitelist(token_address, participant)

    assert whitelist[0] == to_checksum_address("0x0000000000000000000000000000000000000000")
    assert whitelist[1] == to_checksum_address("0x0000000000000000000000000000000000000000")
    assert whitelist[2] == False


# エラー系2: コントラクトアドレスの登録
def test_register_error_2(web3, chain, users, membership_exchange):
    admin = users['admin']
    issuer = users['issuer']
    sample_contract = membership_exchange.address

    # TokenRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    token_regulator_service, _ = chain.provider.get_or_deploy_contract('TokenRegulatorService')

    # トークン新規発行
    # NOTE:StandardTokenInterfaceを継承している会員権トークンを発行
    web3.eth.defaultAccount = issuer
    membership, deploy_args = \
        utils.issue_transferable_membership(web3, chain, membership_exchange.address)
    token_address = membership.address

    # 購入可能者リストに登録：コントラクトアドレスの登録 -> 登録不可
    # NOTE:コントラクトアドレスとして、membership_exchangeのアドレスを登録する
    web3.eth.defaultAccount = issuer
    txn_hash = token_regulator_service.transact(). \
        register(token_address, sample_contract, False)
    chain.wait.for_receipt(txn_hash)

    # Whitelist情報の参照
    whitelist = token_regulator_service.call().getWhitelist(token_address, sample_contract)

    assert whitelist[0] == to_checksum_address("0x0000000000000000000000000000000000000000")
    assert whitelist[1] == to_checksum_address("0x0000000000000000000000000000000000000000")
    assert whitelist[2] == False


# エラー系3: 入力値の型誤り
def test_register_error_3(web3, chain, users, membership_exchange):
    admin = users['admin']
    issuer = users['issuer']
    participant = users['trader']

    # TokenRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    token_regulator_service, _ = chain.provider.get_or_deploy_contract('TokenRegulatorService')

    # トークン新規発行
    # NOTE:StandardTokenInterfaceを継承している会員権トークンを発行
    web3.eth.defaultAccount = issuer
    membership, deploy_args = \
        utils.issue_transferable_membership(web3, chain, membership_exchange.address)
    token_address = membership.address

    # 購入可能者リストに登録
    web3.eth.defaultAccount = issuer

    # トークンアドレスの型誤り
    with pytest.raises(TypeError):
        token_regulator_service.transact(). \
            register(1234, participant, False)

    # アカウントアドレスの型誤り
    with pytest.raises(TypeError):
        token_regulator_service.transact(). \
            register(token_address, 1234, False)

    # ロック状態の型誤り
    with pytest.raises(TypeError):
        token_regulator_service.transact(). \
            register(token_address, participant, 'True')


"""
TEST2_取引参加者参照（getWhitelist）
"""


# 正常系1: 取引参加者参照（データあり）
def test_getWhitelist_normal_1(web3, chain, users, membership_exchange):
    admin = users['admin']
    issuer = users['issuer']
    participant = users['trader']

    # TokenRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    token_regulator_service, _ = chain.provider.get_or_deploy_contract('TokenRegulatorService')

    # トークン新規発行
    # NOTE:StandardTokenInterfaceを継承している会員権トークンを発行
    web3.eth.defaultAccount = issuer
    membership, deploy_args = \
        utils.issue_transferable_membership(web3, chain, membership_exchange.address)
    token_address = membership.address

    # 購入可能者リストに登録
    web3.eth.defaultAccount = issuer
    txn_hash = token_regulator_service.transact(). \
        register(token_address, participant, False)
    chain.wait.for_receipt(txn_hash)

    # Whitelist情報の参照
    whitelist = token_regulator_service.call().getWhitelist(token_address, participant)

    # 検証
    assert whitelist[0] == to_checksum_address(token_address)
    assert whitelist[1] == to_checksum_address(participant)
    assert whitelist[2] == False


# 正常系2: 取引参加者参照（データなし）
def test_getWhitelist_normal_2(web3, chain, users):
    admin = users['admin']
    participant = users['trader']

    # TokenRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    token_regulator_service, _ = chain.provider.get_or_deploy_contract('TokenRegulatorService')

    token_address = "0x0000000000000000000000000000000000000000"

    # Whitelist情報の参照
    whitelist = token_regulator_service.call().getWhitelist(token_address, participant)

    # 検証
    assert whitelist[0] == "0x0000000000000000000000000000000000000000"
    assert whitelist[1] == "0x0000000000000000000000000000000000000000"
    assert whitelist[2] == False


# エラー系1: 入力値の型誤り
def test_getWhitelist_error_1(web3, chain, users):
    admin = users['admin']
    participant = users['trader']

    # TokenRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    token_regulator_service, _ = chain.provider.get_or_deploy_contract('TokenRegulatorService')

    token_address = "0x0000000000000000000000000000000000000000"

    # トークンアドレスの型誤り
    with pytest.raises(TypeError):
        token_regulator_service.call().getWhitelist(1234, participant)

    # アカウントアドレスの型誤り
    with pytest.raises(TypeError):
        token_regulator_service.call().getWhitelist(token_address, 1234)


"""
TEST3_取引可否チェック（check）
"""


# 正常系1: 取引可否チェック（取引可）
def test_check_normal_1(web3, chain, users, membership_exchange):
    admin = users['admin']
    issuer = users['issuer']
    participant = users['trader']

    # TokenRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    token_regulator_service, _ = chain.provider.get_or_deploy_contract('TokenRegulatorService')

    # トークン新規発行
    # NOTE:StandardTokenInterfaceを継承している会員権トークンを発行
    web3.eth.defaultAccount = issuer
    membership, deploy_args = \
        utils.issue_transferable_membership(web3, chain, membership_exchange.address)
    token_address = membership.address

    # 購入可能者リストに登録
    web3.eth.defaultAccount = issuer
    txn_hash = token_regulator_service.transact(). \
        register(token_address, participant, False)
    chain.wait.for_receipt(txn_hash)

    # 取引可否チェック
    result = token_regulator_service.call().check(token_address, participant)

    # 検証
    assert result == 0


# 正常系2: 取引可否チェック（取引不可：ロック状態）
def test_check_normal_2(web3, chain, users, membership_exchange):
    admin = users['admin']
    issuer = users['issuer']
    participant = users['trader']

    # TokenRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    token_regulator_service, _ = chain.provider.get_or_deploy_contract('TokenRegulatorService')

    # トークン新規発行
    # NOTE:StandardTokenInterfaceを継承している会員権トークンを発行
    web3.eth.defaultAccount = issuer
    membership, deploy_args = \
        utils.issue_transferable_membership(web3, chain, membership_exchange.address)
    token_address = membership.address

    # 購入可能者リストに登録
    web3.eth.defaultAccount = issuer
    txn_hash = token_regulator_service.transact(). \
        register(token_address, participant, True)  # Trueで登録（ロック状態）
    chain.wait.for_receipt(txn_hash)

    # 取引可否チェック：取引不可（アカウントロック）
    result = token_regulator_service.call().check(token_address, participant)

    # 検証
    assert result == 1


# 正常系3: 取引可否チェック（取引不可：アカウント未登録）
def test_check_normal_3(web3, chain, users, membership_exchange):
    admin = users['admin']
    issuer = users['issuer']
    participant = users['trader']

    # TokenRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    token_regulator_service, _ = chain.provider.get_or_deploy_contract('TokenRegulatorService')

    # トークン新規発行
    # NOTE:StandardTokenInterfaceを継承している会員権トークンを発行
    web3.eth.defaultAccount = issuer
    membership, deploy_args = \
        utils.issue_transferable_membership(web3, chain, membership_exchange.address)
    token_address = membership.address

    # 取引可否チェック：取引不可（アカウント未登録）
    result = token_regulator_service.call().check(token_address, participant)

    # 検証
    assert result == 2


# エラー系1: 入力値の型誤り
def test_check_error_1(web3, chain, users, membership_exchange):
    admin = users['admin']
    issuer = users['issuer']
    participant = users['trader']

    # TokenRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    token_regulator_service, _ = chain.provider.get_or_deploy_contract('TokenRegulatorService')

    # トークン新規発行
    # NOTE:StandardTokenInterfaceを継承している会員権トークンを発行
    web3.eth.defaultAccount = issuer
    membership, deploy_args = \
        utils.issue_transferable_membership(web3, chain, membership_exchange.address)
    token_address = membership.address

    # 取引可否チェック
    web3.eth.defaultAccount = issuer

    # トークンアドレスの型誤り
    with pytest.raises(TypeError):
        token_regulator_service.call().check(1234, participant)

    # アカウントアドレスの型誤り
    with pytest.raises(TypeError):
        token_regulator_service.call().check(token_address, 1234)
