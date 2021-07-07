"""
Copyright BOOSTRY Co., Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
"""

import pytest
from eth_utils import to_checksum_address
import utils

token_template = 'some_template'

'''
TEST_トークン情報を登録（register）
'''


# 正常系1: 新規登録(普通社債Token)
def test_register_normal_1(TokenList, users, otc_exchange, personal_info):
    admin = users['admin']
    issuer = users['issuer']

    # TokenListコントラクト作成
    tokenlist_contract = admin.deploy(TokenList)

    # Token新規発行
    share_token, deploy_args = \
        utils.issue_share_token(users, otc_exchange.address, personal_info.address)
    token_address = share_token.address

    # TokenListに追加
    tokenlist_contract.register.transact(token_address, token_template, {'from': issuer})

    # Owner Address が正しいことを確認
    owner_address = tokenlist_contract.getOwnerAddress(token_address)
    assert owner_address == issuer

    # 登録後のリストの長さが正しいことを確認
    list_length = tokenlist_contract.getListLength()
    assert list_length == 1

    # 登録情報の内容が正しいことを確認（アドレス検索）
    token_by_address = tokenlist_contract.getTokenByAddress(token_address)
    assert token_by_address[0] == to_checksum_address(token_address)
    assert token_by_address[1] == token_template
    assert token_by_address[2] == to_checksum_address(issuer.address)

    # 登録情報の内容が正しいことを確認（リスト番号指定）
    token_by_num = tokenlist_contract.getTokenByNum(0)
    assert token_by_num[0] == to_checksum_address(token_address)
    assert token_by_num[1] == token_template
    assert token_by_num[2] == to_checksum_address(issuer.address)


# 正常系2: 新規登録（クーポンToken）
def test_register_normal_2(TokenList, users, coupon_exchange):
    admin = users['admin']
    issuer = users['issuer']

    # TokenListコントラクト作成
    tokenlist_contract = admin.deploy(TokenList)

    # Token新規発行
    token, deploy_args = \
        utils.issue_transferable_coupon(issuer, coupon_exchange.address)
    token_address = token.address

    # TokenListに追加
    tokenlist_contract.register.transact(token_address, token_template, {'from': issuer})

    # Owner Address が正しいことを確認
    owner_address = tokenlist_contract.getOwnerAddress(token_address)
    assert owner_address == issuer

    # 登録後のリストの長さが正しいことを確認
    list_length = tokenlist_contract.getListLength()
    assert list_length == 1

    # 登録情報の内容が正しいことを確認（アドレス検索）
    token_by_address = tokenlist_contract.getTokenByAddress(token_address)
    assert token_by_address[0] == to_checksum_address(token_address)
    assert token_by_address[1] == token_template
    assert token_by_address[2] == to_checksum_address(issuer.address)

    # 登録情報の内容が正しいことを確認（リスト番号指定）
    token_by_num = tokenlist_contract.getTokenByNum(0)
    assert token_by_num[0] == to_checksum_address(token_address)
    assert token_by_num[1] == token_template
    assert token_by_num[2] == to_checksum_address(issuer.address)


# エラー系1: トークンアドレスの型（address）が正しくない場合
def test_register_error_1(TokenList, users):
    admin = users['admin']
    issuer = users['issuer']

    # TokenListコントラクト作成
    tokenlist_contract = admin.deploy(TokenList)

    # 新規登録 -> Failure
    token_address = 'some_token_address'
    with pytest.raises(ValueError):
        tokenlist_contract.register.transact(token_address, token_template, {'from': issuer})


# エラー系2: トークンテンプレートの型（string）が正しくない場合
def test_register_error_2(TokenList, users, share_exchange, personal_info):
    admin = users['admin']
    issuer = users['issuer']

    # TokenListコントラクト作成
    tokenlist_contract = admin.deploy(TokenList)

    # Token新規発行
    share_token, deploy_args = \
        utils.issue_share_token(users, share_exchange.address, personal_info.address)
    token_address = share_token.address

    # 新規登録 -> Failure
    with pytest.raises(ValueError):
        tokenlist_contract.register. \
            transact(token_address, '0xb6286fAFd0451320ad6A8143089b216C2152c025', {'from': issuer})


# エラー系3: 同一トークンを複数回登録
def test_register_error_3(TokenList, users, share_exchange, personal_info):
    admin = users['admin']
    issuer = users['issuer']

    # TokenListコントラクト作成
    tokenlist_contract = admin.deploy(TokenList)

    # Token新規発行
    share_token, deploy_args = \
        utils.issue_share_token(users, share_exchange.address, personal_info.address)
    token_address = share_token.address

    # 新規登録（1回目） -> Success
    tokenlist_contract.register.transact(token_address, token_template, {'from': issuer})

    # 新規登録（2回目） -> Failure
    tokenlist_contract.register.transact(token_address, token_template, {'from': issuer})

    # 登録後のリストの長さが正しいことを確認
    list_length = tokenlist_contract.getListLength()
    assert list_length == 1

    # 登録情報の内容が正しいことを確認（アドレス検索）
    token_by_address = tokenlist_contract.getTokenByAddress(token_address)
    assert token_by_address[0] == to_checksum_address(token_address)
    assert token_by_address[1] == token_template
    assert token_by_address[2] == to_checksum_address(issuer.address)

    # 登録情報の内容が正しいことを確認（リスト番号指定）
    token_by_num = tokenlist_contract.getTokenByNum(0)
    assert token_by_num[0] == to_checksum_address(token_address)
    assert token_by_num[1] == token_template
    assert token_by_num[2] == to_checksum_address(issuer.address)


# エラー系4: 異なるアドレスから同一トークンを登録
def test_register_error_4(TokenList, users, share_exchange, personal_info):
    admin = users['admin']
    issuer = users['issuer']

    # TokenListコントラクト作成
    tokenlist_contract = admin.deploy(TokenList)

    # Token新規発行
    share_token, deploy_args = \
        utils.issue_share_token(users, share_exchange.address, personal_info.address)
    token_address = share_token.address

    # 新規登録（account_1） -> Success
    tokenlist_contract.register.transact(token_address, token_template, {'from': issuer})

    # 新規登録（account_2） -> Failure
    tokenlist_contract.register.transact(token_address, token_template, {'from': admin})

    # 登録後のリストの長さが正しいことを確認
    list_length = tokenlist_contract.getListLength()
    assert list_length == 1

    # 登録情報の内容が正しいことを確認（アドレス検索）
    token_by_address = tokenlist_contract.getTokenByAddress(token_address)
    assert token_by_address[0] == to_checksum_address(token_address)
    assert token_by_address[1] == token_template
    assert token_by_address[2] == to_checksum_address(issuer.address)

    # 登録情報の内容が正しいことを確認（リスト番号指定）
    token_by_num = tokenlist_contract.getTokenByNum(0)
    assert token_by_num[0] == to_checksum_address(token_address)
    assert token_by_num[1] == token_template
    assert token_by_num[2] == to_checksum_address(issuer.address)


'''
TEST_オーナーを変更（changeOwner）
'''


# 正常系1: オーナー変更
def test_changeOwner_normal_1(TokenList, users, share_exchange, personal_info):
    admin = users['admin']
    issuer = users['issuer']
    new_owner_address = admin.address

    # TokenListコントラクト作成
    tokenlist_contract = admin.deploy(TokenList)

    # Token新規発行
    share_token, deploy_args = \
        utils.issue_share_token(users, share_exchange.address, personal_info.address)
    token_address = share_token.address

    # 新規登録 -> Success
    tokenlist_contract.register.transact(token_address, token_template, {'from': issuer})

    # オーナー変更 -> Success
    tokenlist_contract.changeOwner.transact(token_address, new_owner_address, {'from': issuer})

    # Owner Address が正しいことを確認
    owner_address = tokenlist_contract.getOwnerAddress(token_address)
    assert owner_address == new_owner_address

    # 登録後のリストの長さが正しいことを確認
    list_length = tokenlist_contract.getListLength()
    assert list_length == 1

    # 登録情報の内容が正しいことを確認（アドレス検索）
    token_by_address = tokenlist_contract.getTokenByAddress(token_address)
    assert token_by_address[0] == to_checksum_address(token_address)
    assert token_by_address[1] == token_template
    assert token_by_address[2] == to_checksum_address(new_owner_address)

    # 登録情報の内容が正しいことを確認（リスト番号指定）
    token_by_num = tokenlist_contract.getTokenByNum(0)
    assert token_by_num[0] == to_checksum_address(token_address)
    assert token_by_num[1] == token_template
    assert token_by_num[2] == to_checksum_address(new_owner_address)


# エラー系1: トークンアドレスの型（address）が正しくない場合
def test_changeOwner_error_1(TokenList, users):
    admin = users['admin']
    new_owner_address = admin

    # TokenListコントラクト作成
    tokenlist_contract = admin.deploy(TokenList)

    token_address = 'some_token_address'

    # 新規登録 -> Failure
    with pytest.raises(ValueError):
        tokenlist_contract.changeOwner.transact(token_address, new_owner_address, {'from': admin})


# エラー系2: オーナーアドレスの型（address）が正しくない場合
def test_changeOwner_error_2(TokenList, users, share_exchange, personal_info):
    admin = users['admin']
    issuer = users['issuer']

    # TokenListコントラクト作成
    tokenlist_contract = admin.deploy(TokenList)

    # Token新規発行
    share_token, deploy_args = \
        utils.issue_share_token(users, share_exchange.address, personal_info.address)
    token_address = share_token.address

    new_owner_address = 'some_address'

    # 新規登録 -> Failure
    with pytest.raises(ValueError):
        tokenlist_contract.changeOwner.transact(token_address, new_owner_address, {'from': issuer})


# エラー系3: 登録なし -> オーナー変更
def test_changeOwner_error_3(TokenList, users, share_exchange, personal_info):
    admin = users['admin']
    issuer = users['issuer']
    new_owner_address = users['issuer']

    # TokenListコントラクト作成
    tokenlist_contract = admin.deploy(TokenList)

    # Token新規発行
    share_token, deploy_args = \
        utils.issue_share_token(users, share_exchange.address, personal_info.address)
    token_address = share_token.address

    # オーナー変更 -> Failure
    tokenlist_contract.changeOwner.transact(token_address, new_owner_address, {'from': issuer})

    owner_address = tokenlist_contract.getOwnerAddress(token_address)
    assert owner_address == '0x0000000000000000000000000000000000000000'


# エラー系4: オーナー権限のないアドレスでオーナー変更を実施した場合
def test_changeOwner_error_4(TokenList, users, share_exchange, personal_info):
    admin = users['admin']
    issuer = users['issuer']
    new_owner_address = users['issuer']

    # TokenListコントラクト作成
    tokenlist_contract = admin.deploy(TokenList)

    # Token新規発行
    share_token, deploy_args = \
        utils.issue_share_token(users, share_exchange.address, personal_info.address)
    token_address = share_token.address

    # 新規登録 -> Success
    tokenlist_contract.register.transact(token_address, token_template, {'from': issuer})

    # オーナー変更 -> Failure
    tokenlist_contract.changeOwner.transact(token_address, new_owner_address, {'from': admin})

    owner_address = tokenlist_contract.getOwnerAddress(token_address)
    assert owner_address == to_checksum_address(issuer.address)
