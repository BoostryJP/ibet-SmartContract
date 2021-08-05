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


"""
TEST_取引参加者登録（register）
"""


# 正常系1: 新規登録
def test_register_normal_1(ExchangeRegulatorService, users):
    admin = users['admin']
    participant = users['trader']

    # ExchangeRegulatorServiceコントラクト作成
    exchange_regulator_service = admin.deploy(ExchangeRegulatorService)

    # 取引参加者リストに登録
    exchange_regulator_service.register.transact(participant, False, {'from': admin})

    # Whitelist情報の参照
    whitelist = exchange_regulator_service.getWhitelist(participant)

    # 検証
    assert whitelist[0] == to_checksum_address(participant.address)
    assert whitelist[1] == False


# 正常系2: 変更登録
def test_register_normal_2(ExchangeRegulatorService, users):
    admin = users['admin']
    participant = users['trader']

    # ExchangeRegulatorServiceコントラクト作成
    exchange_regulator_service = admin.deploy(ExchangeRegulatorService)

    # 取引参加者リストに登録：１回目
    exchange_regulator_service.register.transact(participant, False, {'from': admin})

    # 取引参加者リストに登録：２回目
    exchange_regulator_service.register.transact(participant, True, {'from': admin})

    # Whitelist情報の参照
    whitelist = exchange_regulator_service.getWhitelist(participant)

    # 検証
    assert whitelist[0] == to_checksum_address(participant.address)
    assert whitelist[1] == True


# エラー系1: 権限なしアカウントからの登録
def test_register_error_1(ExchangeRegulatorService, users):
    admin = users['admin']
    participant = users['trader']

    # ExchangeRegulatorServiceコントラクト作成
    exchange_regulator_service = admin.deploy(ExchangeRegulatorService)

    # 取引参加者リストに登録：権限なしアカウントからの登録 -> 登録不可
    try:
        exchange_regulator_service.register.transact(participant, False, {'from': participant})
    except ValueError:
        pass

    # Whitelist情報の参照
    whitelist = exchange_regulator_service.getWhitelist(participant)
    assert whitelist[0] == to_checksum_address("0x0000000000000000000000000000000000000000")
    assert whitelist[1] == False


# エラー系2: コントラクトアドレスの登録
def test_register_error_2(ExchangeRegulatorService, users, membership_exchange):
    admin = users['admin']
    sample_contract = membership_exchange.address

    # ExchangeRegulatorServiceコントラクト作成
    exchange_regulator_service = admin.deploy(ExchangeRegulatorService)

    # 取引参加者リストに登録：コントラクトアドレスの登録 -> 登録不可
    # NOTE:コントラクトアドレスとして、membership_exchangeのアドレスを登録する
    try:
        exchange_regulator_service.register.transact(sample_contract, False, {'from': admin})
    except ValueError:
        pass

    # Whitelist情報の参照
    whitelist = exchange_regulator_service.getWhitelist(sample_contract)

    assert whitelist[0] == to_checksum_address("0x0000000000000000000000000000000000000000")
    assert whitelist[1] == False


# エラー系3: 入力値の型誤り
def test_register_error_3(ExchangeRegulatorService, users):
    admin = users['admin']
    participant = users['trader']

    # ExchangeRegulatorServiceコントラクト作成
    exchange_regulator_service = admin.deploy(ExchangeRegulatorService)

    # 取引参加者リストに登録

    # アカウントアドレスの型誤り
    with pytest.raises(ValueError):
        exchange_regulator_service.register.transact(1234, False, {'from': admin})

    # ロック状態の型誤り
    with pytest.raises(ValueError):
        exchange_regulator_service.register.transact(participant, 'True', {'from': admin})


"""
TEST_取引参加者参照（getWhitelist）
"""


# 正常系1: 取引参加者参照（データあり）
def test_getWhitelist_normal_1(ExchangeRegulatorService, users):
    admin = users['admin']
    participant = users['trader']

    # ExchangeRegulatorServiceコントラクト作成
    exchange_regulator_service = admin.deploy(ExchangeRegulatorService)

    # 取引参加者リストに登録
    exchange_regulator_service.register.transact(participant, False, {'from': admin})

    # Whitelist情報の参照
    whitelist = exchange_regulator_service.getWhitelist(participant)

    # 検証
    assert whitelist[0] == to_checksum_address(participant.address)
    assert whitelist[1] == False


# 正常系2: 取引参加者参照（データなし）
def test_getWhitelist_normal_2(ExchangeRegulatorService, users):
    admin = users['admin']
    participant = '0x0000000000000000000000000000000000000000'

    # ExchangeRegulatorServiceコントラクト作成
    exchange_regulator_service = admin.deploy(ExchangeRegulatorService)

    # Whitelist情報の参照
    whitelist = exchange_regulator_service.getWhitelist(participant)

    # 検証
    assert whitelist[0] == "0x0000000000000000000000000000000000000000"
    assert whitelist[1] == False


# エラー系1: 入力値の型誤り
def test_getWhitelist_error_1(ExchangeRegulatorService, users):
    admin = users['admin']

    # ExchangeRegulatorServiceコントラクト作成
    exchange_regulator_service = admin.deploy(ExchangeRegulatorService)

    # アカウントアドレスの型誤り
    with pytest.raises(ValueError):
        exchange_regulator_service.getWhitelist(1234)


"""
TEST_取引可否チェック（check）
"""


# 正常系1: 取引可否チェック（取引可）
def test_check_normal_1(ExchangeRegulatorService, users):
    admin = users['admin']
    participant = users['trader']

    # ExchangeRegulatorServiceコントラクト作成
    exchange_regulator_service = admin.deploy(ExchangeRegulatorService)

    # 取引参加者リストに登録
    exchange_regulator_service.register.transact(participant, False, {'from': admin})

    # 取引可否チェック
    result = exchange_regulator_service.check(participant)

    # 検証
    assert result == 0


# 正常系2: 取引可否チェック（取引不可：ロック状態）
def test_check_normal_2(ExchangeRegulatorService, users):
    admin = users['admin']
    participant = users['trader']

    # ExchangeRegulatorServiceコントラクト作成
    exchange_regulator_service = admin.deploy(ExchangeRegulatorService)

    # 取引参加者リストに登録
    exchange_regulator_service.register.transact(participant, True, {'from': admin})  # Trueで登録（ロック状態）

    # 取引可否チェック：取引不可（アカウントロック）
    result = exchange_regulator_service.check(participant)

    # 検証
    assert result == 1


# 正常系3: 取引可否チェック（取引不可：アカウント未登録）
def test_check_normal_3(ExchangeRegulatorService, users):
    admin = users['admin']
    participant = users['trader']

    # ExchangeRegulatorServiceコントラクト作成
    exchange_regulator_service = admin.deploy(ExchangeRegulatorService)

    # 取引可否チェック：取引不可（アカウント未登録）
    result = exchange_regulator_service.check(participant)

    # 検証
    assert result == 2


# エラー系1: 入力値の型誤り
def test_check_error_1(ExchangeRegulatorService, users):
    admin = users['admin']

    # ExchangeRegulatorServiceコントラクト作成
    exchange_regulator_service = admin.deploy(ExchangeRegulatorService)

    # 取引可否チェック

    # アカウントアドレスの型誤り
    with pytest.raises(ValueError):
        exchange_regulator_service.check(1234)
