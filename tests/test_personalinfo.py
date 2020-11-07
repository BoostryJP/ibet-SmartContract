"""
Copyright BOOSTRY Co., Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed onan "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
"""

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


# エラー系2: 入力値の型誤り（暗号化情報）
def test_register_error_2(users, personal_info):
    account = users['trader']
    link = users['issuer']  # issuerのアドレスに公開する

    # 登録 -> Failure
    with pytest.raises(ValueError):
        invalid_str = '0x66aB6D9362d4F35596279692F0251Db635165871'
        personal_info.register.transact(link.address, invalid_str, {'from': account})


# 正常系1: 登録情報修正
def test_modify_normal_1(users, personal_info):
    account = users['trader']
    link = users['issuer']  # issuerのアドレスに公開する

    # 登録
    personal_info.register.transact(link, encrypted_message, {'from': account})

    # 修正
    personal_info.modify.transact(account, encrypted_message_after, {'from': link})

    # 登録情報の内容が正しいことを確認
    modified_personal_info = personal_info.personal_info(account, link, {'from': account})
    assert modified_personal_info[0] == account
    assert modified_personal_info[1] == link
    assert modified_personal_info[2] == encrypted_message_after


# 正常系2: 登録情報修正（登録情報削除）
def test_modify_normal_2(users, personal_info):
    account = users['trader']
    link = users['issuer']  # issuerのアドレスに公開する

    # 登録
    personal_info.register.transact(link, encrypted_message, {'from': account})

    # 修正
    personal_info.modify.transact(account, '', {'from': link})

    # 登録情報の内容が正しいことを確認
    modified_personal_info = personal_info.personal_info(account, link, {'from': account})
    assert modified_personal_info[0] == account
    assert modified_personal_info[1] == link
    assert modified_personal_info[2] == ''


# エラー系1: 入力値の型誤り（アカウントアドレス）
def test_modify_error_1(users, personal_info):
    account = users['trader']
    link = users['issuer']  # issuerのアドレスに公開する

    # 登録
    personal_info.register.transact(link, encrypted_message, {'from': account})

    # 修正
    invalid_account = 'aaaa'
    with pytest.raises(ValueError):
        personal_info.modify.transact(invalid_account, encrypted_message_after, {'from': link})


# エラー系2: 入力値の型誤り（暗号化情報）
def test_modify_error_2(users, personal_info):
    account = users['trader']
    link = users['issuer']  # issuerのアドレスに公開する

    # 登録
    personal_info.register.transact(link, encrypted_message, {'from': account})

    # 修正
    invalid_str = '0x66aB6D9362d4F35596279692F0251Db635165871'
    with pytest.raises(ValueError):
        personal_info.modify.transact(account, invalid_str, {'from': link})


# エラー系3: 未登録情報に対して修正
def test_modify_error_3(users, personal_info):
    account = users['trader']
    link = users['issuer']  # issuerのアドレスに公開する

    # 修正
    personal_info.modify.transact(account, encrypted_message_after, {'from': link})

    actual_personal_info = personal_info.personal_info(account, link, {'from': link})
    is_registered = personal_info.isRegistered(account, link, {'from': link})

    # 登録情報の内容が正しいことを確認
    assert actual_personal_info[0] == '0x0000000000000000000000000000000000000000'
    assert actual_personal_info[1] == '0x0000000000000000000000000000000000000000'
    assert actual_personal_info[2] == ''

    # 登録状態が未登録のままであることを確認
    assert is_registered is False


# エラー系4: 通知先アカウント以外からの修正
def test_modify_error_4(users, personal_info):
    account = users['trader']
    link = users['issuer']  # issuerのアドレスに公開する
    modifier = users['admin']

    # accountによる登録
    personal_info.register.transact(link, encrypted_message, {'from': account})

    # 通知先アカウント以外 (modifier) による修正 -> Failure
    personal_info.modify.transact(account, encrypted_message_after, {'from': modifier})

    actual_personal_info = personal_info.personal_info(account, link, {'from': link})

    # 登録情報の内容が正しいことを確認
    assert actual_personal_info[0] == account
    assert actual_personal_info[1] == link
    assert actual_personal_info[2] == encrypted_message
