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


def init_args(exchange_address):
    name = 'test_membership'
    symbol = 'MEM'
    initial_supply = 10000
    tradable_exchange = exchange_address
    details = 'some_details'
    return_details = 'some_return'
    expiration_date = '20191231'
    memo = 'some_memo'
    transferable = True
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'

    deploy_args = [
        name, symbol, initial_supply, tradable_exchange,
        details, return_details,
        expiration_date, memo, transferable,
        contact_information, privacy_policy
    ]
    return deploy_args


'''
TEST_デプロイ
'''


# 正常系1: deploy
def test_deploy_normal_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    owner_address = membership_contract.owner()
    name = membership_contract.name()
    symbol = membership_contract.symbol()
    total_supply = membership_contract.totalSupply()
    tradable_exchange = membership_contract.tradableExchange()
    details = membership_contract.details()
    return_details = membership_contract.returnDetails()
    expiration_date = membership_contract.expirationDate()
    memo = membership_contract.memo()
    transferable = membership_contract.transferable()
    status = membership_contract.status()
    balance = membership_contract.balanceOf(issuer)
    contact_information = membership_contract.contactInformation()
    privacy_policy = membership_contract.privacyPolicy()

    assert owner_address == issuer
    assert name == deploy_args[0]
    assert symbol == deploy_args[1]
    assert total_supply == deploy_args[2]
    assert tradable_exchange == to_checksum_address(deploy_args[3])
    assert details == deploy_args[4]
    assert return_details == deploy_args[5]
    assert expiration_date == deploy_args[6]
    assert memo == deploy_args[7]
    assert transferable == deploy_args[8]
    assert status is True
    assert balance == deploy_args[2]
    assert contact_information == deploy_args[9]
    assert privacy_policy == deploy_args[10]


# エラー系1: 入力値の型誤り（name）
def test_deploy_error_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    deploy_args = init_args(membership_exchange.address)
    deploy_args[0] = '0x66aB6D9362d4F35596279692F0251Db635165871'  # stringに変換できないデータ

    with pytest.raises(ValueError):
        issuer.deploy(IbetMembership, *deploy_args)


# エラー系2: 入力値の型誤り（symbol）
def test_deploy_error_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    deploy_args = init_args(membership_exchange.address)
    deploy_args[1] = '0x66aB6D9362d4F35596279692F0251Db635165871'  # stringに変換できないデータ

    with pytest.raises(ValueError):
        issuer.deploy(IbetMembership, *deploy_args)


# エラー系3: 入力値の型誤り（initialSupply）
def test_deploy_error_3(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = "a10000"

    with pytest.raises(TypeError):
        issuer.deploy(IbetMembership, *deploy_args)


# エラー系4: 入力値の型誤り（details）
def test_deploy_error_4(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    deploy_args = init_args(membership_exchange.address)
    deploy_args[4] = '0x66aB6D9362d4F35596279692F0251Db635165871'  # stringに変換できないデータ

    with pytest.raises(ValueError):
        issuer.deploy(IbetMembership, *deploy_args)


# エラー系5: 入力値の型誤り（returnDetails）
def test_deploy_error_5(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    deploy_args = init_args(membership_exchange.address)
    deploy_args[5] = '0x66aB6D9362d4F35596279692F0251Db635165871'  # stringに変換できないデータ

    with pytest.raises(ValueError):
        issuer.deploy(IbetMembership, *deploy_args)


# エラー系6: 入力値の型誤り（expirationDate）
def test_deploy_error_6(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    deploy_args = init_args(membership_exchange.address)
    deploy_args[6] = '0x66aB6D9362d4F35596279692F0251Db635165871'  # stringに変換できないデータ

    with pytest.raises(ValueError):
        issuer.deploy(IbetMembership, *deploy_args)


# エラー系7: 入力値の型誤り（memo）
def test_deploy_error_7(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    deploy_args = init_args(membership_exchange.address)
    deploy_args[7] = '0x66aB6D9362d4F35596279692F0251Db635165871'  # stringに変換できないデータ

    with pytest.raises(ValueError):
        issuer.deploy(IbetMembership, *deploy_args)


# エラー系8: 入力値の型誤り（transferable）
def test_deploy_error_8(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    deploy_args = init_args(membership_exchange.address)
    deploy_args[8] = 'True'

    with pytest.raises(ValueError):
        issuer.deploy(IbetMembership, *deploy_args)


# エラー系9: 入力値の型誤り（tradableExchange）
def test_deploy_error_9(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    deploy_args = init_args(membership_exchange.address)
    deploy_args[3] = '0xaaaa'

    with pytest.raises(ValueError):
        issuer.deploy(IbetMembership, *deploy_args)


# エラー系10: 入力値の型誤り（contactInformation）
def test_deploy_error_10(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    deploy_args = init_args(membership_exchange.address)
    deploy_args[9] = '0x66aB6D9362d4F35596279692F0251Db635165871'  # stringに変換できないデータ

    with pytest.raises(ValueError):
        issuer.deploy(IbetMembership, *deploy_args)


# エラー系10: 入力値の型誤り（privacyPolicy）
def test_deploy_error_11(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    deploy_args = init_args(membership_exchange.address)
    deploy_args[10] = '0x66aB6D9362d4F35596279692F0251Db635165871'  # stringに変換できないデータ

    with pytest.raises(ValueError):
        issuer.deploy(IbetMembership, *deploy_args)


'''
TEST_トークンの振替（transfer）
'''


# 正常系1: アカウントアドレスへの振替
def test_transfer_normal_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    transfer_amount = 100

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 振替
    membership_contract.transfer.transact(trader, transfer_amount, {'from': issuer})

    # 振替後の残高取得
    issuer_balance = membership_contract.balanceOf(issuer)
    trader_balance = membership_contract.balanceOf(trader)

    assert issuer_balance == deploy_args[2] - transfer_amount
    assert trader_balance == transfer_amount


# 正常系2: 会員権取引コントラクトへの振替
def test_transfer_normal_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    transfer_amount = 100

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    exchange_address = membership_exchange.address
    membership_contract.transfer.transact(exchange_address, transfer_amount, {'from': issuer})

    issuer_balance = membership_contract.balanceOf(issuer)
    exchange_balance = membership_contract.balanceOf(exchange_address)

    assert issuer_balance == deploy_args[2] - transfer_amount
    assert exchange_balance == transfer_amount


# 正常系3-1: 限界値：上限値
# アカウントアドレスへの振替
def test_transfer_normal_3_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 発行
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2 ** 256 - 1  # 上限まで発行する
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 振替
    transfer_amount = 2 ** 256 - 1
    membership_contract.transfer.transact(trader, transfer_amount, {'from': issuer})

    assert membership_contract.balanceOf(issuer) == 0
    assert membership_contract.balanceOf(trader) == 2 ** 256 - 1


# 正常系3-2: 限界値：下限値
# アカウントアドレスへの振替
def test_transfer_normal_3_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 発行
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 0
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 振替
    transfer_amount = 0
    membership_contract.transfer.transact(trader, transfer_amount, {'from': issuer})

    assert membership_contract.balanceOf(issuer) == 0
    assert membership_contract.balanceOf(trader) == 0


# 正常系3-3: 限界値：上限値
# コントラクトアドレスへの振替
def test_transfer_normal_3_3(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 発行
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2 ** 256 - 1  # 上限まで発行する
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 振替
    exchange_address = membership_exchange.address
    transfer_amount = 2 ** 256 - 1
    membership_contract. \
        transfer.transact(exchange_address, transfer_amount, {'from': issuer})

    assert membership_contract.balanceOf(issuer) == 0
    assert membership_contract.balanceOf(exchange_address) == 2 ** 256 - 1


# 正常系3-4: 限界値：下限値
# コントラクトアドレスへの振替
def test_transfer_normal_3_4(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 発行
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 0
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 振替
    exchange_address = membership_exchange.address
    transfer_amount = 0
    membership_contract. \
        transfer.transact(exchange_address, transfer_amount, {'from': issuer})

    assert membership_contract.balanceOf(issuer) == 0
    assert membership_contract.balanceOf(exchange_address) == 0


# エラー系1-1: 入力値の型誤り（to）
def test_transfer_error_1_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    to = 1234
    transfer_amount = 100

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 振替
    with pytest.raises(ValueError):
        membership_contract.transfer.transact(to, transfer_amount, {'from': issuer})


# エラー系1-2: 入力値の型誤り（value）
def test_transfer_error_1_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    to = users['trader'].address

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 振替（String）
    with pytest.raises(TypeError):
        membership_contract.transfer.transact(to, 'ABC', {'from': issuer})

    # 振替（負の値）
    with pytest.raises(OverflowError):
        membership_contract.transfer.transact(to, -1, {'from': issuer})


# エラー系2: 限界値超
def test_transfer_error_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    to = users['trader']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 振替（上限値超え）
    with pytest.raises(OverflowError):
        membership_contract.transfer.transact(to, 2 ** 256, {'from': issuer})

    # 振替（下限値超え）
    with pytest.raises(OverflowError):
        membership_contract.transfer.transact(to, -1, {'from': issuer})


# エラー系3: 残高不足
def test_transfer_error_3(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 振替（残高超）
    transfer_amount = 10000000000
    membership_contract.transfer.transact(trader, transfer_amount, {'from': issuer, 'gas': 4})

    assert membership_contract.balanceOf(issuer) == deploy_args[2]
    assert membership_contract.balanceOf(trader) == 0


# エラー系4: private functionにアクセスできない
def test_transfer_error_4(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    transfer_amount = 100
    data = 0

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    with pytest.raises(AttributeError):
        membership_contract.isContract(trader, {'from': issuer})

    with pytest.raises(AttributeError):
        membership_contract.transferToAddress.transact(trader, transfer_amount, data, {'from': issuer})

    with pytest.raises(AttributeError):
        membership_contract.transferToContract.transact(trader, transfer_amount, data, {'from': issuer})


# エラー系5: 譲渡不可
def test_transfer_error_5(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    deploy_args[8] = False
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 振替：譲渡不可
    transfer_amount = 10
    membership_contract.transfer(trader, transfer_amount, {'from': issuer})  # エラーになる

    assert membership_contract.balanceOf(issuer) == deploy_args[2]
    assert membership_contract.balanceOf(trader) == 0


# エラー系6: 取引不可Exchangeへの振替
def test_transfer_error_6(users, IbetMembership, membership_exchange,
                          membership_exchange_storage, payment_gateway,
                          IbetCouponExchange):
    issuer = users['issuer']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 取引不可Exchange
    dummy_exchange = users['admin'].deploy(
        IbetCouponExchange,  # IbetMembershipExchange以外を読み込む必要がある
        payment_gateway.address, membership_exchange_storage.address
    )

    # 振替
    transfer_amount = 10
    membership_contract.transfer.transact(dummy_exchange.address, transfer_amount, {'from': issuer})  # エラーになる

    assert membership_contract.balanceOf(issuer) == deploy_args[2]
    assert membership_contract.balanceOf(dummy_exchange.address) == 0


'''
TEST_トークンの移転（transferFrom）
'''


# 正常系1: アカウントアドレスへの移転
def test_transferFrom_normal_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    from_address = users['admin']
    to_address = users['trader']
    value = 100

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 譲渡（issuer -> from_address）
    membership_contract. \
        transfer.transact(from_address, value, {'from': issuer})

    # 移転（_from -> _to）
    membership_contract. \
        transferFrom.transact(from_address, to_address, value, {'from': issuer})

    issuer_balance = membership_contract.balanceOf(issuer)
    from_balance = membership_contract.balanceOf(from_address)
    to_balance = membership_contract.balanceOf(to_address)

    assert issuer_balance == deploy_args[2] - value
    assert from_balance == 0
    assert to_balance == value


# 正常系2: コントラクトアドレスへの移転
def test_transferFrom_normal_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    from_address = users['trader']
    value = 100

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)
    to_address = membership_exchange.address

    # 譲渡（issuer -> from_address）
    membership_contract. \
        transfer.transact(from_address, value, {'from': issuer})

    # 移転（_from -> _to）
    membership_contract. \
        transferFrom.transact(from_address, to_address, value, {'from': issuer})

    issuer_balance = membership_contract.balanceOf(issuer)
    from_balance = membership_contract.balanceOf(from_address)
    to_balance = membership_contract.balanceOf(to_address)

    assert issuer_balance == deploy_args[2] - value
    assert from_balance == 0
    assert to_balance == value


# 正常系3-1: 限界値：上限値
#  アカウントアドレスへの移転
def test_transferFrom_normal_3_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    from_address = users['admin']
    to_address = users['trader']
    max_value = 2 ** 256 - 1

    # 発行
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = max_value
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 譲渡（issuer -> from_address）
    membership_contract. \
        transfer.transact(from_address, max_value, {'from': issuer})

    # 移転（from -> to）
    membership_contract. \
        transferFrom.transact(from_address, to_address, max_value, {'from': issuer})

    issuer_balance = membership_contract.balanceOf(issuer)
    from_balance = membership_contract.balanceOf(from_address)
    to_balance = membership_contract.balanceOf(to_address)

    assert issuer_balance == 0
    assert from_balance == 0
    assert to_balance == max_value


# 正常系3-2: 限界値：下限値
#  アカウントアドレスへの移転
def test_transferFrom_normal_3_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    from_address = users['admin']
    to_address = users['trader']
    min_value = 0

    # 発行
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = min_value
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 譲渡（issuer -> from_address）
    membership_contract. \
        transfer.transact(from_address, min_value, {'from': issuer})

    # 移転（from -> to）
    membership_contract. \
        transferFrom.transact(from_address, to_address, min_value, {'from': issuer})

    issuer_balance = membership_contract.balanceOf(issuer)
    from_balance = membership_contract.balanceOf(from_address)
    to_balance = membership_contract.balanceOf(to_address)

    assert issuer_balance == 0
    assert from_balance == 0
    assert to_balance == 0


# 正常系3-3: 限界値：上限値
#  コントラクトアドレスへの移転
def test_transferFrom_normal_3_3(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    from_address = users['admin']
    to_address = membership_exchange.address
    max_value = 2 ** 256 - 1

    # 発行
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = max_value
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 譲渡（issuer -> from_address）
    membership_contract.transfer.transact(from_address, max_value, {'from': issuer})

    # 移転（from -> to）
    membership_contract.transferFrom.transact(from_address, to_address, max_value, {'from': issuer})

    issuer_balance = membership_contract.balanceOf(issuer)
    from_balance = membership_contract.balanceOf(from_address)
    to_balance = membership_contract.balanceOf(to_address)
    assert issuer_balance == 0
    assert from_balance == 0
    assert to_balance == max_value


# 正常系3-4: 限界値：下限値
#  コントラクトアドレスへの移転
def test_transferFrom_normal_3_4(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    from_address = users['admin']
    to_address = membership_exchange.address
    min_value = 0

    # 発行
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = min_value
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 譲渡（issuer -> from_address）
    membership_contract.transfer.transact(from_address, min_value, {'from': issuer})

    # 移転（from -> to）
    membership_contract.transferFrom.transact(from_address, to_address, min_value, {'from': issuer})

    issuer_balance = membership_contract.balanceOf(issuer)
    from_balance = membership_contract.balanceOf(from_address)
    to_balance = membership_contract.balanceOf(to_address)
    assert issuer_balance == 0
    assert from_balance == 0
    assert to_balance == 0


# エラー系1-1: 入力値の型誤り（from_address）
def test_transferFrom_error_1_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    to_address = users['trader']
    value = 100

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # String
    with pytest.raises(ValueError):
        membership_contract. \
            transferFrom.transact('1234', to_address, value, {'from': issuer})

    # Int
    with pytest.raises(ValueError):
        membership_contract. \
            transferFrom.transact(1234, to_address, value, {'from': issuer})


# エラー系1-2: 入力値の型誤り（to_address）
def test_transferFrom_error_1_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    value = 100

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # String
    with pytest.raises(ValueError):
        membership_contract. \
            transferFrom.transact(issuer, '1234', value, {'from': issuer})

    # Int
    with pytest.raises(ValueError):
        membership_contract. \
            transferFrom.transact(issuer, 1234, value, {'from': issuer})


# エラー系1-3: 入力値の型誤り（value）
def test_transferFrom_error_1_3(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    to_address = users['trader']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # String
    with pytest.raises(TypeError):
        membership_contract. \
            transferFrom.transact(issuer, to_address, 'hundred', {'from': issuer})

    # 負の値
    with pytest.raises(OverflowError):
        membership_contract. \
            transferFrom.transact(issuer, to_address, -1, {'from': issuer})


# エラー系2: 限界値超
def test_transferFrom_error_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    to_address = users['trader']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 上限値超
    with pytest.raises(OverflowError):
        membership_contract. \
            transferFrom.transact(issuer, to_address, 2 ** 256, {'from': issuer})

    # 下限値超
    with pytest.raises(OverflowError):
        membership_contract. \
            transferFrom.transact(issuer, to_address, -1, {'from': issuer})


# エラー系3: 残高不足
def test_transferFrom_error_3(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    to_address = users['trader']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 残高超
    transfer_amount = 10000000000
    membership_contract.transferFrom.transact(issuer, to_address, transfer_amount, {'from': issuer})

    assert membership_contract.balanceOf(issuer) == deploy_args[2]
    assert membership_contract.balanceOf(to_address) == 0


# エラー系4: 権限エラー（発行者以外が実行）
def test_transferFrom_error_4(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    admin = users['admin']
    to_address = users['trader']
    transfer_amount = 100

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 残高超
    membership_contract.transferFrom.transact(issuer, to_address, transfer_amount, {'from': admin})  # エラーになる

    assert membership_contract.balanceOf(issuer) == deploy_args[2]
    assert membership_contract.balanceOf(to_address) == 0


'''
TEST_残高確認（balanceOf）
'''


# 正常系1: 発行 -> 残高確認
def test_balanceOf_normal_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    balance = membership_contract.balanceOf(issuer)
    assert balance == deploy_args[2]


# 正常系2: データなし -> 残高ゼロ
def test_balanceOf_normal_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    balance = membership_contract.balanceOf(trader)
    assert balance == 0


# エラー系1: 入力値の型誤り
def test_balanceOf_error_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 型誤り：String
    with pytest.raises(ValueError):
        membership_contract.balanceOf('1234')

    # 型誤り：Int
    with pytest.raises(ValueError):
        membership_contract.balanceOf(1234)


'''
TEST_会員権詳細更新（setDetails）
'''


# 正常系1: 発行 -> 詳細更新
def test_setDetails_normal_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    after_details = 'after_details'

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 会員権詳細更新
    membership_contract. \
        setDetails.transact(after_details, {'from': issuer})

    details = membership_contract.details()
    assert after_details == details


# エラー系1: 入力値の型誤り
def test_setDetails_error_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 型誤り
    with pytest.raises(ValueError):
        membership_contract.setDetails.transact('0x66aB6D9362d4F35596279692F0251Db635165871', {'from': issuer})


# エラー系2: 権限エラー
def test_setDetails_error_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    attacker = users['trader']
    after_details = 'after_details'

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 会員権詳細更新
    membership_contract.setDetails.transact(after_details, {'from': attacker})  # エラーになる

    details = membership_contract.details()
    assert details == deploy_args[4]


'''
TEST_リターン詳細更新（setReturnDetails）
'''


# 正常系1: 発行 -> 詳細更新
def test_setReturnDetails_normal_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    after_return_details = 'after_return_details'

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # リターン詳細更新
    membership_contract. \
        setReturnDetails.transact(after_return_details, {'from': issuer})

    return_details = membership_contract.returnDetails()
    assert after_return_details == return_details


# エラー系1: 入力値の型誤り
def test_setReturnDetails_error_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 型誤り
    with pytest.raises(ValueError):
        membership_contract.setReturnDetails.transact('0x66aB6D9362d4F35596279692F0251Db635165871', {'from': issuer})


# エラー系2: 権限エラー
def test_setReturnDetails_error_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    attacker = users['trader']
    after_return_details = 'after_return_details'

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # リターン詳細更新：権限エラー
    membership_contract.setReturnDetails.transact(after_return_details, {'from': attacker})  # エラーになる

    return_details = membership_contract.returnDetails()
    assert return_details == deploy_args[5]


'''
TEST_有効期限更新（setExpirationDate）
'''


# 正常系1: 発行 -> 有効期限更新
def test_setExpirationDate_normal_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    after_expiration_date = 'after_expiration_date'

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 有効期限更新
    membership_contract. \
        setExpirationDate.transact(after_expiration_date, {'from': issuer})

    expiration_date = membership_contract.expirationDate()
    assert after_expiration_date == expiration_date


# エラー系1: 入力値の型誤り
def test_setExpirationDate_errors_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 型誤り
    with pytest.raises(ValueError):
        membership_contract.setExpirationDate.transact('0x66aB6D9362d4F35596279692F0251Db635165871', {'from': issuer})


# エラー系2: 権限エラー
def test_setExpirationDate_error_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    attacker = users['trader']
    after_expiration_date = 'after_expiration_date'

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 有効期限更新：権限エラー
    membership_contract.setExpirationDate.transact(after_expiration_date, {'from': attacker})  # エラーになる

    expiration_date = membership_contract.expirationDate()
    assert expiration_date == deploy_args[6]


'''
TEST_メモ欄更新（setMemo）
'''


# 正常系1: 発行 -> メモ欄更新
def test_setMemo_normal_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    after_memo = 'after_memo'

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # メモ欄更新
    membership_contract.setMemo.transact(after_memo, {'from': issuer})

    memo = membership_contract.memo()
    assert after_memo == memo


# エラー系1: 入力値の型誤り
def test_setMemo_error_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 型誤り
    with pytest.raises(ValueError):
        membership_contract.setMemo.transact('0x66aB6D9362d4F35596279692F0251Db635165871', {'from': issuer})


# エラー系1: 権限エラー
def test_setMemo_error_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    attacker = users['trader']
    after_memo = 'after_memo'

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # メモ欄更新：権限エラー
    membership_contract.setMemo.transact(after_memo, {'from': attacker})  # エラーになる

    memo = membership_contract.memo()
    assert memo == deploy_args[7]


'''
TEST_譲渡可能更新（setTransferable）
'''


# 正常系1: 発行 -> 譲渡可能更新
def test_setTransferable_normal_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    after_transferable = False

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 譲渡可能更新
    membership_contract.setTransferable.transact(after_transferable, {'from': issuer})

    transferable = membership_contract.transferable()
    assert after_transferable == transferable


# エラー系1: 入力値の型誤り
def test_setTransferable_error_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 型誤り
    with pytest.raises(ValueError):
        membership_contract.setTransferable.transact('True', {'from': issuer})


# エラー系2: 権限エラー
def test_setTransferable_error_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    attacker = users['trader']
    after_transferable = False

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 譲渡可能更新
    membership_contract.setTransferable.transact(after_transferable, {'from': attacker})  # エラーになる

    transferable = membership_contract.transferable()
    assert transferable == deploy_args[8]


'''
TEST_取扱ステータス更新（setStatus）
'''


# 正常系1: 発行 -> 取扱ステータス更新
def test_setStatus_normal_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    after_status = False

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 取扱ステータス更新
    membership_contract.setStatus.transact(after_status, {'from': issuer})

    status = membership_contract.status()
    assert after_status == status


# エラー系1: 入力値の型誤り
def test_setStatus_error_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 型誤り
    with pytest.raises(ValueError):
        membership_contract.setStatus.transact('True', {'from': issuer})


# エラー系2: 権限エラー
def test_setStatus_error_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    attacker = users['trader']
    after_status = False

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 取扱ステータス更新
    membership_contract.setStatus.transact(after_status, {'from': attacker})  # エラーになる

    status = membership_contract.status()
    assert status is True


'''
TEST_商品画像更新（setImageURL, getImageURL）
'''


# 正常系1: 発行 -> 商品画像更新
def test_setImageURL_normal_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    after_url = 'http://hoge.com'

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 商品画像更新
    membership_contract.setImageURL.transact(0, after_url, {'from': issuer})

    url = membership_contract.getImageURL(0)
    assert after_url == url


# エラー系1-1: 入力値の型誤り：Class
def test_setImageURL_error_1_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 型誤り
    with pytest.raises(TypeError):
        membership_contract.setImageURL.transact('A', 'after_url', {'from': issuer})


# エラー系1-2: 入力値の型誤り：ImageURL
def test_setImageURL_error_1_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 型誤り
    with pytest.raises(ValueError):
        membership_contract.setImageURL.transact(0, '0x66aB6D9362d4F35596279692F0251Db635165871', {'from': issuer})


# エラー系2: 権限エラー
def test_setImageURL_error_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    attacker = users['trader']
    after_url = 'http://hoge.com'

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 商品画像更新
    membership_contract.setImageURL.transact(0, after_url, {'from': attacker})  # エラーになる

    url = membership_contract.getImageURL(0)
    assert url == ''


'''
TEST_追加発行（issue）
'''


# 正常系1: 発行 -> 追加発行
def test_issue_normal_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    value = 10

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 追加発行
    membership_contract.issue.transact(value, {'from': issuer})

    total_supply = membership_contract.totalSupply()
    balance = membership_contract.balanceOf(issuer)

    assert total_supply == deploy_args[2] + value
    assert balance == deploy_args[2] + value


# 正常系2: 限界値
def test_issue_normal_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 発行
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2 ** 256 - 2
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 追加発行（限界値）
    membership_contract.issue.transact(1, {'from': issuer})

    total_supply = membership_contract.totalSupply()
    balance = membership_contract.balanceOf(issuer)

    assert total_supply == 2 ** 256 - 1
    assert balance == 2 ** 256 - 1


# エラー系1: 入力値の型誤り
def test_issue_error_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # String
    with pytest.raises(TypeError):
        membership_contract.issue.transact("abc", {'from': issuer})


# エラー系2: 限界値超
def test_issue_error_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 上限値超
    with pytest.raises(OverflowError):
        membership_contract.issue.transact(2 ** 256, {'from': issuer})

    # 下限値超
    with pytest.raises(OverflowError):
        membership_contract.issue.transact(-1, {'from': issuer})


# エラー系3: 発行→追加発行→上限界値超
def test_issue_error_3(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 発行
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2 ** 256 - 1  # 限界値
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 追加発行（限界値超）
    membership_contract.issue.transact(1, {'from': issuer})  # エラーになる

    total_supply = membership_contract.totalSupply()
    balance = membership_contract.balanceOf(issuer)

    assert total_supply == deploy_args[2]
    assert balance == deploy_args[2]


# エラー系4: 権限エラー
def test_issue_error_4(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    attacker = users['trader']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 追加発行：権限エラー
    membership_contract.issue.transact(1, {'from': attacker})  # エラーになる

    total_supply = membership_contract.totalSupply()
    balance = membership_contract.balanceOf(issuer)

    assert total_supply == deploy_args[2]
    assert balance == deploy_args[2]


'''
TEST_取引可能Exchangeの更新（setTradableExchange）
'''


# 正常系1: 発行 -> Exchangeの更新
def test_setTradableExchange_normal_1(users, IbetMembership, membership_exchange,
                                      membership_exchange_storage, payment_gateway, IbetCouponExchange):
    issuer = users['issuer']

    # トークン新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # その他Exchange
    other_exchange = users['admin'].deploy(
        IbetCouponExchange,  # IbetMembershipExchange以外を読み込む必要がある
        payment_gateway.address,
        membership_exchange_storage.address
    )

    # Exchangeの更新
    membership_contract. \
        setTradableExchange.transact(other_exchange.address, {'from': issuer})

    assert membership_contract.tradableExchange() == to_checksum_address(other_exchange.address)


# エラー系1: 発行 -> Exchangeの更新（入力値の型誤り）
def test_setTradableExchange_error_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # トークン新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # Exchangeの更新
    with pytest.raises(ValueError):
        membership_contract.setTradableExchange.transact('0xaaaa', {'from': issuer})


# エラー系2: 発行 -> Exchangeの更新（権限エラー）
def test_setTradableExchange_error_2(users, IbetMembership, membership_exchange,
                                     membership_exchange_storage, payment_gateway, IbetCouponExchange):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # その他Exchange
    other_exchange = users['admin'].deploy(
        IbetCouponExchange,  # IbetMembershipExchange以外を読み込む必要がある
        payment_gateway.address,
        membership_exchange_storage.address
    )

    # Exchangeの更新
    membership_contract.setTradableExchange.transact(other_exchange.address, {'from': trader})  # エラーになる

    assert membership_contract.tradableExchange() == to_checksum_address(membership_exchange.address)


'''
TEST_新規募集ステータス更新（setInitialOfferingStatus）
'''


# 正常系1: 発行 -> 新規募集ステータス更新（False→True）
def test_setInitialOfferingStatus_normal_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # トークン新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 初期状態 == False
    assert membership_contract.initialOfferingStatus() is False

    # 新規募集ステータスの更新
    membership_contract.setInitialOfferingStatus.transact(True, {'from': issuer})

    assert membership_contract.initialOfferingStatus() is True


# 正常系2:
#   発行 -> 新規募集ステータス更新（False→True） -> 2回目更新（True→False）
def test_setInitialOfferingStatus_normal_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # トークン新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 新規募集ステータスの更新
    membership_contract.setInitialOfferingStatus.transact(True, {'from': issuer})

    # 新規募集ステータスの更新（2回目）
    membership_contract.setInitialOfferingStatus.transact(False, {'from': issuer})

    assert membership_contract.initialOfferingStatus() is False


# エラー系1: 発行 -> 新規募集ステータス更新（入力値の型誤り）
def test_setInitialOfferingStatus_error_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # トークン新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 新規募集ステータスの更新
    with pytest.raises(ValueError):
        membership_contract.setInitialOfferingStatus.transact('True', {'from': issuer})


'''
TEST_募集申込（applyForOffering）
'''


# 正常系1
#   発行：発行体 -> 投資家：募集申込
def test_applyForOffering_normal_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 新規募集ステータスの更新
    membership_contract.setInitialOfferingStatus.transact(True, {'from': issuer})

    # 募集申込
    membership_contract.applyForOffering.transact('abcdefgh', {'from': trader})

    assert membership_contract.applications(trader) == 'abcdefgh'


# 正常系2
#   発行：発行体 -> （申込なし）初期データ参照
def test_applyForOffering_normal_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 新規募集ステータスの更新
    membership_contract.setInitialOfferingStatus.transact(True, {'from': issuer})

    assert membership_contract.applications(trader) == ''


# エラー系1:
#   発行：発行体 -> 投資家：募集申込（入力値の型誤り）
def test_applyForOffering_error_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 新規募集ステータスの更新
    membership_contract.setInitialOfferingStatus.transact(True, {'from': issuer})

    # 募集申込
    with pytest.raises(ValueError):
        membership_contract.applyForOffering.transact("0x66aB6D9362d4F35596279692F0251Db635165871", {'from': trader})


# エラー系2:
#   発行：発行体 -> 投資家：募集申込（申込ステータスが停止中）
def test_applyForOffering_error_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 募集申込
    membership_contract.applyForOffering.transact('abcdefgh', {'from': trader})

    assert membership_contract.applications(trader) == ''


'''
TEST_問い合わせ先情報の更新（setContactInformation）
'''


# 正常系1
# ＜発行者＞発行 -> ＜発行者＞問い合わせ先情報の修正
def test_setContactInformation_normal_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 修正
    membership_contract.setContactInformation.transact('updated contact information', {'from': issuer})

    contact_information = membership_contract.contactInformation()
    assert contact_information == 'updated contact information'


# エラー系1: 入力値の型誤り
def test_setContactInformation_error_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 修正
    with pytest.raises(ValueError):
        membership_contract.setContactInformation.transact('0x66aB6D9362d4F35596279692F0251Db635165871',
                                                           {'from': issuer})


# エラー系2: 権限エラー
def test_setContactInformation_error_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    other = users['trader']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 修正
    membership_contract.setContactInformation.transact('updated contact information', {'from': other})

    contact_information = membership_contract.contactInformation()
    assert contact_information == 'some_contact_information'


'''
TEST_プライバシーポリシーの更新（setPrivacyPolicy）
'''


# 正常系1
# ＜発行者＞発行 -> ＜発行者＞プライバシーポリシーの修正
def test_setPrivacyPolicy_normal_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 修正
    membership_contract.setPrivacyPolicy.transact('updated privacy policy', {'from': issuer})

    privacy_policy = membership_contract.privacyPolicy()
    assert privacy_policy == 'updated privacy policy'


# エラー系1: 入力値の型誤り
def test_setPrivacyPolicy_error_1(users, IbetMembership, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 修正
    with pytest.raises(ValueError):
        membership_contract.setPrivacyPolicy.transact('0x66aB6D9362d4F35596279692F0251Db635165871', {'from': issuer})


# エラー系2: 権限エラー
def test_setPrivacyPolicy_error_2(users, IbetMembership, membership_exchange):
    issuer = users['issuer']
    other = users['trader']

    # 新規発行
    deploy_args = init_args(membership_exchange.address)
    membership_contract = issuer.deploy(IbetMembership, *deploy_args)

    # 修正
    membership_contract.setPrivacyPolicy.transact('updated privacy policy', {'from': other})

    privacy_policy = membership_contract.privacyPolicy()
    assert privacy_policy == 'some_privacy_policy'
