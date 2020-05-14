import brownie
import pytest

encrypted_message = 'encrypted_message'
encrypted_message_after = 'encrypted_message_after'

'''
TEST_個人情報を登録（register）
'''


# 正常系1: 新規登録
def test_register_normal_1(users, personal_info):
    account = users['trader']
    link = users['issuer']  # issuerのアドレスに公開する

    personal_info.register.transact(link, encrypted_message, {'from': account})

    registered_personal_info = personal_info.personal_info(account, link, {'from': account})
    is_registered = personal_info.isRegistered(account, link, {'from': account})

    # 登録情報の内容が正しいことを確認
    assert registered_personal_info[0] == account
    assert registered_personal_info[1] == link
    assert registered_personal_info[2] == encrypted_message

    # 登録状態が登録済みの状態であることを確認
    assert is_registered is True


# 正常系2: 上書き登録
def test_register_normal_2(users, personal_info):
    account = users['trader']
    link = users['issuer']  # issuerのアドレスに公開する

    # 登録（1回目） -> Success
    personal_info.register.transact(link.address, encrypted_message, {'from': account})

    # 登録（2回目） -> Success
    personal_info.register.transact(link, encrypted_message_after, {'from': account})

    registered_personal_info = personal_info.personal_info(account, link, {'from': account})
    is_registered = personal_info.isRegistered(account, link, {'from': account})

    # 登録情報の内容が正しいことを確認
    assert registered_personal_info[0] == account
    assert registered_personal_info[1] == link
    assert registered_personal_info[2] == encrypted_message_after

    # 登録状態が登録済みの状態であることを確認
    assert is_registered is True


# 正常系3: 未登録のアドレスの情報参照
def test_register_normal_3(users, personal_info):
    account = users['trader']
    link = users['issuer']  # issuerのアドレスに公開する

    registered_personal_info = personal_info.personal_info(account, link, {'from': account})
    is_registered = personal_info.isRegistered(account, link, {'from': account})

    # 登録情報の内容が正しいことを確認
    assert registered_personal_info[0] == '0x0000000000000000000000000000000000000000'
    assert registered_personal_info[1] == '0x0000000000000000000000000000000000000000'
    assert registered_personal_info[2] == ''

    # 登録状態が登録済みの状態でないことを確認
    assert is_registered is False


# エラー系1: 入力値の型誤り（発行体アドレス）
def test_register_error_1(users, personal_info):
    account = users['trader']
    link = 'aaaa'

    # 登録 -> Failure
    with pytest.raises(ValueError):
        personal_info.register.transact(link, encrypted_message, {'from': account})
