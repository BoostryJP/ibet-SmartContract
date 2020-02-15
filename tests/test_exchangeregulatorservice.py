import pytest
from eth_utils import to_checksum_address


"""
TEST_取引参加者登録（register）
"""


# 正常系1: 新規登録
def test_register_normal_1(web3, chain, users):
    admin = users['admin']
    participant = users['trader']

    # ExchangeRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    exchange_regulator_service, _ = chain.provider.get_or_deploy_contract('ExchangeRegulatorService')

    # 取引参加者リストに登録
    web3.eth.defaultAccount = admin
    txn_hash = exchange_regulator_service.transact().register(participant, False)
    chain.wait.for_receipt(txn_hash)

    # Whitelist情報の参照
    whitelist = exchange_regulator_service.call().getWhitelist(participant)

    # 検証
    assert whitelist[0] == to_checksum_address(participant)
    assert whitelist[1] == False


# 正常系2: 変更登録
def test_register_normal_2(web3, chain, users):
    admin = users['admin']
    participant = users['trader']

    # ExchangeRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    exchange_regulator_service, _ = chain.provider.get_or_deploy_contract('ExchangeRegulatorService')

    # 取引参加者リストに登録：１回目
    web3.eth.defaultAccount = admin
    txn_hash = exchange_regulator_service.transact().register(participant, False)
    chain.wait.for_receipt(txn_hash)

    # 取引参加者リストに登録：２回目
    web3.eth.defaultAccount = admin
    txn_hash = exchange_regulator_service.transact().register(participant, True)
    chain.wait.for_receipt(txn_hash)

    # Whitelist情報の参照
    whitelist = exchange_regulator_service.call().getWhitelist(participant)

    # 検証
    assert whitelist[0] == to_checksum_address(participant)
    assert whitelist[1] == True


# エラー系1: 権限なしアカウントからの登録
def test_register_error_1(web3, chain, users):
    admin = users['admin']
    participant = users['trader']

    # ExchangeRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    exchange_regulator_service, _ = chain.provider.get_or_deploy_contract('ExchangeRegulatorService')

    # 取引参加者リストに登録：権限なしアカウントからの登録 -> 登録不可
    web3.eth.defaultAccount = participant
    try:
        txn_hash = exchange_regulator_service.transact().register(participant, False)
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    # Whitelist情報の参照
    whitelist = exchange_regulator_service.call().getWhitelist(participant)
    assert whitelist[0] == to_checksum_address("0x0000000000000000000000000000000000000000")
    assert whitelist[1] == False


# エラー系2: コントラクトアドレスの登録
def test_register_error_2(web3, chain, users, membership_exchange):
    admin = users['admin']
    sample_contract = membership_exchange.address

    # ExchangeRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    exchange_regulator_service, _ = chain.provider.get_or_deploy_contract('ExchangeRegulatorService')

    # 取引参加者リストに登録：コントラクトアドレスの登録 -> 登録不可
    # NOTE:コントラクトアドレスとして、membership_exchangeのアドレスを登録する
    web3.eth.defaultAccount = admin
    try:
        txn_hash = exchange_regulator_service.transact().register(sample_contract, False)
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    # Whitelist情報の参照
    whitelist = exchange_regulator_service.call().getWhitelist(sample_contract)

    assert whitelist[0] == to_checksum_address("0x0000000000000000000000000000000000000000")
    assert whitelist[1] == False


# エラー系3: 入力値の型誤り
def test_register_error_3(web3, chain, users):
    admin = users['admin']
    participant = users['trader']

    # ExchangeRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    exchange_regulator_service, _ = chain.provider.get_or_deploy_contract('ExchangeRegulatorService')

    # 取引参加者リストに登録
    web3.eth.defaultAccount = admin

    # アカウントアドレスの型誤り
    with pytest.raises(TypeError):
        exchange_regulator_service.transact().register(1234, False)

    # ロック状態の型誤り
    with pytest.raises(TypeError):
        exchange_regulator_service.transact().register(participant, 'True')


"""
TEST_取引参加者参照（getWhitelist）
"""


# 正常系1: 取引参加者参照（データあり）
def test_getWhitelist_normal_1(web3, chain, users):
    admin = users['admin']
    participant = users['trader']

    # ExchangeRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    exchange_regulator_service, _ = chain.provider.get_or_deploy_contract('ExchangeRegulatorService')

    # 取引参加者リストに登録
    web3.eth.defaultAccount = admin
    txn_hash = exchange_regulator_service.transact().register(participant, False)
    chain.wait.for_receipt(txn_hash)

    # Whitelist情報の参照
    whitelist = exchange_regulator_service.call().getWhitelist(participant)

    # 検証
    assert whitelist[0] == to_checksum_address(participant)
    assert whitelist[1] == False


# 正常系2: 取引参加者参照（データなし）
def test_getWhitelist_normal_2(web3, chain, users):
    admin = users['admin']
    participant = '0x0000000000000000000000000000000000000000'

    # ExchangeRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    exchange_regulator_service, _ = chain.provider.get_or_deploy_contract('ExchangeRegulatorService')

    # Whitelist情報の参照
    whitelist = exchange_regulator_service.call().getWhitelist(participant)

    # 検証
    assert whitelist[0] == "0x0000000000000000000000000000000000000000"
    assert whitelist[1] == False


# エラー系1: 入力値の型誤り
def test_getWhitelist_error_1(web3, chain, users):
    admin = users['admin']

    # ExchangeRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    exchange_regulator_service, _ = chain.provider.get_or_deploy_contract('ExchangeRegulatorService')

    # アカウントアドレスの型誤り
    with pytest.raises(TypeError):
        exchange_regulator_service.call().getWhitelist(1234)


"""
TEST_取引可否チェック（check）
"""


# 正常系1: 取引可否チェック（取引可）
def test_check_normal_1(web3, chain, users):
    admin = users['admin']
    participant = users['trader']

    # ExchangeRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    exchange_regulator_service, _ = chain.provider.get_or_deploy_contract('ExchangeRegulatorService')

    # 取引参加者リストに登録
    web3.eth.defaultAccount = admin
    txn_hash = exchange_regulator_service.transact().register(participant, False)
    chain.wait.for_receipt(txn_hash)

    # 取引可否チェック
    result = exchange_regulator_service.call().check(participant)

    # 検証
    assert result == 0


# 正常系2: 取引可否チェック（取引不可：ロック状態）
def test_check_normal_2(web3, chain, users):
    admin = users['admin']
    participant = users['trader']

    # ExchangeRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    exchange_regulator_service, _ = chain.provider.get_or_deploy_contract('ExchangeRegulatorService')

    # 取引参加者リストに登録
    web3.eth.defaultAccount = admin
    txn_hash = exchange_regulator_service.transact().register(participant, True)  # Trueで登録（ロック状態）
    chain.wait.for_receipt(txn_hash)

    # 取引可否チェック：取引不可（アカウントロック）
    result = exchange_regulator_service.call().check(participant)

    # 検証
    assert result == 1


# 正常系3: 取引可否チェック（取引不可：アカウント未登録）
def test_check_normal_3(web3, chain, users):
    admin = users['admin']
    participant = users['trader']

    # ExchangeRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    exchange_regulator_service, _ = chain.provider.get_or_deploy_contract('ExchangeRegulatorService')

    # 取引可否チェック：取引不可（アカウント未登録）
    result = exchange_regulator_service.call().check(participant)

    # 検証
    assert result == 2


# エラー系1: 入力値の型誤り
def test_check_error_1(web3, chain, users):
    admin = users['admin']

    # ExchangeRegulatorServiceコントラクト作成
    web3.eth.defaultAccount = admin
    exchange_regulator_service, _ = chain.provider.get_or_deploy_contract('ExchangeRegulatorService')

    # 取引可否チェック
    web3.eth.defaultAccount = admin

    # アカウントアドレスの型誤り
    with pytest.raises(TypeError):
        exchange_regulator_service.call().check(1234)
