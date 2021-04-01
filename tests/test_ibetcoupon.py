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
    name = 'test_coupon'
    symbol = 'CPN'
    total_supply = 1000000
    tradable_exchange = exchange_address
    details = 'some_details'
    return_details = 'some_return_details'
    memo = 'some_memo'
    expiration_date = '20201231'
    transferable = True
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'

    deploy_args = [
        name, symbol, total_supply, tradable_exchange,
        details, return_details,
        memo, expiration_date, transferable,
        contact_information, privacy_policy
    ]
    return deploy_args


# TEST_deploy
class TestDeploy:

    # 正常系1: deploy
    def test_deploy_normal_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        owner_address = coupon.owner()
        name = coupon.name()
        symbol = coupon.symbol()
        total_supply = coupon.totalSupply()
        tradable_exchange = coupon.tradableExchange()
        details = coupon.details()
        return_details = coupon.returnDetails()
        memo = coupon.memo()
        expiration_date = coupon.expirationDate()
        is_valid = coupon.status()
        transferable = coupon.transferable()
        contact_information = coupon.contactInformation()
        privacy_policy = coupon.privacyPolicy()

        assert owner_address == issuer
        assert name == deploy_args[0]
        assert symbol == deploy_args[1]
        assert total_supply == deploy_args[2]
        assert tradable_exchange == to_checksum_address(deploy_args[3])
        assert details == deploy_args[4]
        assert return_details == deploy_args[5]
        assert memo == deploy_args[6]
        assert expiration_date == deploy_args[7]
        assert is_valid is True
        assert transferable == deploy_args[8]
        assert contact_information == deploy_args[9]
        assert privacy_policy == deploy_args[10]

    # エラー系1: 入力値の型誤り（name）
    def test_deploy_error_1(self, users, IbetCoupon, coupon_exchange):
        deploy_args = init_args(coupon_exchange.address)
        deploy_args[0] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'

        with pytest.raises(ValueError):
            users['admin'].deploy(
                IbetCoupon, *deploy_args)

    # エラー系2: 入力値の型誤り（symbol）
    def test_deploy_error_2(self, users, IbetCoupon, coupon_exchange):
        deploy_args = init_args(coupon_exchange.address)
        deploy_args[1] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'

        with pytest.raises(ValueError):
            users['admin'].deploy(
                IbetCoupon, *deploy_args)

    # エラー系3: 入力値の型誤り（totalSupply）
    def test_deploy_error_3(self, users, IbetCoupon, coupon_exchange):
        deploy_args = init_args(coupon_exchange.address)
        deploy_args[2] = "a10000"

        with pytest.raises(TypeError):
            users['admin'].deploy(
                IbetCoupon, *deploy_args)

    # エラー系4: 入力値の型誤り（tradableExchange）
    def test_deploy_error_4(self, users, IbetCoupon, coupon_exchange):
        deploy_args = init_args(coupon_exchange.address)
        deploy_args[3] = '0xaaa'

        with pytest.raises(ValueError):
            users['admin'].deploy(
                IbetCoupon, *deploy_args)

    # エラー系5: 入力値の型誤り（details）
    def test_deploy_error_5(self, users, IbetCoupon, coupon_exchange):
        deploy_args = init_args(coupon_exchange.address)
        deploy_args[4] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'

        with pytest.raises(ValueError):
            users['admin'].deploy(
                IbetCoupon, *deploy_args)

    # エラー系6: 入力値の型誤り（returnDetails）
    def test_deploy_error_6(self, users, IbetCoupon, coupon_exchange):
        deploy_args = init_args(coupon_exchange.address)
        deploy_args[5] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'

        with pytest.raises(ValueError):
            users['admin'].deploy(
                IbetCoupon, *deploy_args)

    # エラー系7: 入力値の型誤り（memo）
    def test_deploy_error_7(self, users, IbetCoupon, coupon_exchange):
        deploy_args = init_args(coupon_exchange.address)
        deploy_args[6] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'

        with pytest.raises(ValueError):
            users['admin'].deploy(
                IbetCoupon, *deploy_args)

    # エラー系8: 入力値の型誤り（expirationDate）
    def test_deploy_error_8(self, users, IbetCoupon, coupon_exchange):
        deploy_args = init_args(coupon_exchange.address)
        deploy_args[7] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'

        with pytest.raises(ValueError):
            users['admin'].deploy(
                IbetCoupon, *deploy_args)

    # エラー系9: 入力値の型誤り（transferable）
    def test_deploy_error_9(self, users, IbetCoupon, coupon_exchange):
        deploy_args = init_args(coupon_exchange.address)
        deploy_args[8] = 'True'

        with pytest.raises(ValueError):
            users['admin'].deploy(
                IbetCoupon, *deploy_args)

    # エラー系10: 入力値の型誤り（contactInformation）
    def test_deploy_error_10(self, users, IbetCoupon, coupon_exchange):
        deploy_args = init_args(coupon_exchange.address)
        deploy_args[9] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'

        with pytest.raises(ValueError):
            users['admin'].deploy(
                IbetCoupon, *deploy_args)

    # エラー系11: 入力値の型誤り（privacyPolicy）
    def test_deploy_error_11(self, users, IbetCoupon, coupon_exchange):
        deploy_args = init_args(coupon_exchange.address)
        deploy_args[10] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'

        with pytest.raises(ValueError):
            users['admin'].deploy(
                IbetCoupon, *deploy_args)


# TEST_transfer
class TestTransfer:

    # 正常系1: アカウントアドレスへの譲渡
    def test_transfer_normal_1(self, IbetCoupon, users, coupon_exchange):
        _from = users['issuer']
        _to = users['trader']
        _value = 100

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = _from.deploy(IbetCoupon, *deploy_args)

        # 譲渡
        coupon.transfer.transact(_to, _value, {'from': _from})

        from_balance = coupon.balanceOf(_from)
        to_balance = coupon.balanceOf(_to)

        assert from_balance == deploy_args[2] - _value
        assert to_balance == _value

    # 正常系2: クーポン取引コントラクトへの譲渡
    def test_transfer_normal_2(self, IbetCoupon, users, coupon_exchange):
        _from = users['issuer']
        _to = coupon_exchange.address
        _value = 100

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = _from.deploy(IbetCoupon, *deploy_args)

        # 譲渡
        coupon.transfer.transact(_to, _value, {'from': _from})

        from_balance = coupon.balanceOf(_from)
        to_balance = coupon.balanceOf(_to)

        assert from_balance == deploy_args[2] - _value
        assert to_balance == _value

    # エラー系1: 入力値の型誤り（To）
    def test_transfer_error_1(self, IbetCoupon, users, coupon_exchange):
        _from = users['issuer']
        _to = 1234
        _value = 100

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = _from.deploy(IbetCoupon, *deploy_args)

        # 譲渡
        with pytest.raises(ValueError):
            coupon.transfer.transact(_to, _value, {'from': _from})

    # エラー系2: 入力値の型誤り（Value）
    def test_transfer_error_2(self, IbetCoupon, users, coupon_exchange):
        _from = users['issuer']
        _to = users['trader']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = _from.deploy(IbetCoupon, *deploy_args)

        # 譲渡
        with pytest.raises(TypeError):
            coupon.transfer.transact(_to, 'zero', {'from': _from})

        with pytest.raises(OverflowError):
            coupon.transfer.transact(_to, 2 ** 256, {'from': _from})

        with pytest.raises(OverflowError):
            coupon.transfer.transact(_to, -1, {'from': _from})

    # エラー系3: 残高不足
    def test_transfer_error_3(self, IbetCoupon, users, coupon_exchange):
        _from = users['issuer']
        _to = users['trader']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = _from.deploy(IbetCoupon, *deploy_args)

        # 譲渡（残高超）
        _value = deploy_args[2] + 1
        coupon.transfer.transact(_to, _value, {'from': _from})  # エラーになる

        assert coupon.balanceOf(_from) == deploy_args[2]
        assert coupon.balanceOf(_to) == 0

    # エラー系4: 譲渡不可クーポンの譲渡
    def test_transfer_error_4(self, IbetCoupon, users, coupon_exchange):
        _from = users['issuer']
        _to = users['trader']

        # 新規発行（譲渡不可クーポン）
        deploy_args = init_args(coupon_exchange.address)
        deploy_args[8] = False
        coupon = _from.deploy(IbetCoupon, *deploy_args)

        # 譲渡（譲渡不可）
        _value = 1
        coupon.transfer.transact(_to, _value, {'from': _from})  # エラーになる

        assert coupon.balanceOf(_from) == deploy_args[2]
        assert coupon.balanceOf(_to) == 0

    # エラー系5: 取引不可Exchangeへの振替
    def test_transfer_error_5(self, IbetCoupon, users, coupon_exchange, coupon_exchange_storage,
                              payment_gateway, IbetMembershipExchange):
        _issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = _issuer.deploy(IbetCoupon, *deploy_args)

        # 取引不可Exchange
        dummy_exchange = users['admin'].deploy(
            IbetMembershipExchange,  # IbetCouponExchange以外を読み込む必要がある
            payment_gateway.address,
            coupon_exchange_storage.address)

        # 譲渡
        _value = deploy_args[2]
        coupon.transfer.transact(dummy_exchange.address, _value, {'from': _issuer})  # エラーになる

        assert coupon.balanceOf(_issuer) == deploy_args[2]
        assert coupon.balanceOf(dummy_exchange.address) == 0


# TEST_bulkTransfer
class TestBulkTransfer:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Bulk transfer to account address (1 data)
    def test_bulk_transfer_normal_1(self, IbetCoupon, users, coupon_exchange):
        from_address = users["issuer"]
        to_address = users["trader"]

        # issue coupon token
        deploy_args = init_args(coupon_exchange.address)
        coupon_contract = from_address.deploy(IbetCoupon, *deploy_args)

        # bulk transfer
        to_address_list = [to_address]
        amount_list = [1]
        coupon_contract.bulkTransfer.transact(
            to_address_list,
            amount_list,
            {"from": from_address}
        )

        # assertion
        from_balance = coupon_contract.balanceOf(from_address)
        to_balance = coupon_contract.balanceOf(to_address)
        assert from_balance == deploy_args[2] - 1
        assert to_balance == 1

    # Normal_2
    # Bulk transfer to account address (multiple data)
    def test_bulk_transfer_normal_2(self, IbetCoupon, users, coupon_exchange):
        from_address = users["issuer"]
        to_address = users["trader"]

        # issue coupon token
        deploy_args = init_args(coupon_exchange.address)
        coupon_contract = from_address.deploy(IbetCoupon, *deploy_args)

        # bulk transfer
        to_address_list = []
        amount_list = []
        for i in range(100):
            to_address_list.append(to_address)
            amount_list.append(1)
        coupon_contract.bulkTransfer.transact(
            to_address_list,
            amount_list,
            {"from": from_address}
        )

        # assertion
        from_balance = coupon_contract.balanceOf(from_address)
        to_balance = coupon_contract.balanceOf(to_address)
        assert from_balance == deploy_args[2] - 100
        assert to_balance == 100

    # Normal_3
    # Bulk transfer to contract address
    def test_bulk_transfer_normal_3(self, IbetCoupon, users, coupon_exchange):
        from_address = users["issuer"]

        # issue coupon token
        deploy_args = init_args(coupon_exchange.address)
        coupon_contract = from_address.deploy(IbetCoupon, *deploy_args)

        # bulk transfer
        to_address_list = [coupon_exchange.address]
        amount_list = [1]
        coupon_contract.bulkTransfer.transact(
            to_address_list,
            amount_list,
            {"from": from_address}
        )

        # assertion
        from_balance = coupon_contract.balanceOf(from_address)
        to_balance = coupon_contract.balanceOf(coupon_exchange.address)
        assert from_balance == deploy_args[2] - 1
        assert to_balance == 1

    #######################################
    # Error
    #######################################

    # Error_1_1
    # Input value type error (to_list)
    def test_bulk_transfer_error_1_1(self, IbetCoupon, users, coupon_exchange):
        from_address = users["issuer"]
        to_address = 1234
        transfer_amount = 1

        # issue coupon token
        deploy_args = init_args(coupon_exchange.address)
        coupon_contract = from_address.deploy(IbetCoupon, *deploy_args)

        # bulk transfer
        with pytest.raises(ValueError):
            coupon_contract.bulkTransfer.transact(
                [to_address],
                [transfer_amount],
                {"from": from_address}
            )

    # Error_1_2
    # Input value type error (value_list)
    def test_bulk_transfer_error_1_2(self, IbetCoupon, users, coupon_exchange):
        from_address = users["issuer"]
        to_address = users["trader"]
        transfer_amount = "abc"

        # issue coupon token
        deploy_args = init_args(coupon_exchange.address)
        coupon_contract = from_address.deploy(IbetCoupon, *deploy_args)

        # bulk transfer
        with pytest.raises(TypeError):
            coupon_contract.bulkTransfer.transact(
                [to_address],
                [transfer_amount],
                {"from": from_address}
            )

    # Error_2
    # Over/Under the limit
    def test_bulk_transfer_error_2(self, IbetCoupon, users, coupon_exchange):
        from_address = users['issuer']
        to_address = users['trader']

        # issue coupon token
        deploy_args = init_args(coupon_exchange.address)
        deploy_args[2] = 2 ** 256 - 1
        coupon_contract = from_address.deploy(IbetCoupon, *deploy_args)

        # over the upper limit
        coupon_contract.bulkTransfer.transact(
            [to_address, to_address],
            [2 ** 256 - 1, 1],
            {'from': from_address}
        )  # error
        from_balance = coupon_contract.balanceOf(from_address)
        to_balance = coupon_contract.balanceOf(to_address)
        assert from_balance == deploy_args[2]
        assert to_balance == 0

        # under the lower limit
        with pytest.raises(OverflowError):
            coupon_contract.bulkTransfer.transact(
                [to_address],
                [-1],
                {'from': from_address}
            )

    # Error_3
    # Insufficient balance
    def test_bulk_transfer_error_3(self, IbetCoupon, users, coupon_exchange):
        from_address = users["issuer"]
        to_address = users["trader"]

        # issue coupon token
        deploy_args = init_args(coupon_exchange.address)
        coupon_contract = from_address.deploy(IbetCoupon, *deploy_args)

        # bulk transfer
        coupon_contract.bulkTransfer.transact(
            [to_address, to_address],
            [deploy_args[2], 1],
            {'from': from_address}
        )  # error

        assert coupon_contract.balanceOf(from_address) == deploy_args[2]
        assert coupon_contract.balanceOf(to_address) == 0

    # Error_4
    # Non-transferable token
    def test_bulk_transfer_error_4(self, IbetCoupon, users, coupon_exchange):
        from_address = users["issuer"]
        to_address = users["trader"]

        # issue coupon token
        deploy_args = init_args(coupon_exchange.address)
        coupon_contract = from_address.deploy(IbetCoupon, *deploy_args)

        # change to non-transferable
        coupon_contract.setTransferable.transact(False, {"from": from_address})

        # bulk transfer
        coupon_contract.bulkTransfer.transact(
            [to_address],
            [1],
            {"from": from_address}
        )  # error

        # assertion
        from_balance = coupon_contract.balanceOf(from_address)
        to_balance = coupon_contract.balanceOf(to_address)
        assert from_balance == deploy_args[2]
        assert to_balance == 0


# TEST_transferFrom
class TestTransferFrom:

    #######################################
    # Normal
    #######################################

    # Normal_1
    # Transfer to account address
    def test_transferFrom_normal_1(self, users, IbetCoupon, coupon_exchange):
        issuer = users['issuer']
        from_address = users['admin']
        to_address = users['trader']
        value = 100

        # issue coupon token
        deploy_args = init_args(coupon_exchange.address)
        coupon_contract = issuer.deploy(IbetCoupon, *deploy_args)

        # transfer to account address
        coupon_contract.transfer.transact(
            from_address,
            value,
            {'from': issuer}
        )
        coupon_contract.transferFrom.transact(
            from_address,
            to_address,
            value,
            {'from': issuer}
        )

        # assertion
        issuer_balance = coupon_contract.balanceOf(issuer)
        from_balance = coupon_contract.balanceOf(from_address)
        to_balance = coupon_contract.balanceOf(to_address)
        assert issuer_balance == deploy_args[2] - value
        assert from_balance == 0
        assert to_balance == value

    # Normal_2
    # Transfer to contract address
    def test_transferFrom_normal_2(self, users, IbetCoupon, coupon_exchange):
        issuer = users['issuer']
        from_address = users['trader']
        value = 100

        # issue coupon token
        deploy_args = init_args(coupon_exchange.address)
        coupon_contract = issuer.deploy(IbetCoupon, *deploy_args)

        # transfer to contract address
        coupon_contract.transfer.transact(
            from_address,
            value,
            {'from': issuer}
        )
        to_address = coupon_exchange.address
        coupon_contract.transferFrom.transact(
            from_address,
            to_address,
            value,
            {'from': issuer}
        )

        # assertion
        issuer_balance = coupon_contract.balanceOf(issuer)
        from_balance = coupon_contract.balanceOf(from_address)
        to_balance = coupon_contract.balanceOf(to_address)
        assert issuer_balance == deploy_args[2] - value
        assert from_balance == 0
        assert to_balance == value

    # Normal_3_1
    # Upper limit
    def test_transferFrom_normal_3_1(self, users, IbetCoupon, coupon_exchange):
        issuer = users['issuer']
        from_address = users['admin']
        to_address = users['trader']
        max_value = 2 ** 256 - 1

        # issuer coupon token
        deploy_args = init_args(coupon_exchange.address)
        deploy_args[2] = max_value
        coupon_contract = issuer.deploy(IbetCoupon, *deploy_args)

        # transfer
        coupon_contract.transfer.transact(
            from_address,
            max_value,
            {'from': issuer}
        )
        coupon_contract.transferFrom.transact(
            from_address,
            to_address,
            max_value,
            {'from': issuer}
        )

        # assertion
        issuer_balance = coupon_contract.balanceOf(issuer)
        from_balance = coupon_contract.balanceOf(from_address)
        to_balance = coupon_contract.balanceOf(to_address)
        assert issuer_balance == 0
        assert from_balance == 0
        assert to_balance == max_value

    # Normal_3_2
    # Lower limit
    def test_transferFrom_normal_3_2(self, users, IbetCoupon, coupon_exchange):
        issuer = users['issuer']
        from_address = users['admin']
        to_address = users['trader']
        min_value = 0

        # issue coupon token
        deploy_args = init_args(coupon_exchange.address)
        deploy_args[2] = min_value
        coupon_contract = issuer.deploy(IbetCoupon, *deploy_args)

        # transfer
        coupon_contract.transfer.transact(
            from_address,
            min_value,
            {'from': issuer}
        )
        coupon_contract.transferFrom.transact(
            from_address,
            to_address,
            min_value,
            {'from': issuer}
        )

        # assertion
        issuer_balance = coupon_contract.balanceOf(issuer)
        from_balance = coupon_contract.balanceOf(from_address)
        to_balance = coupon_contract.balanceOf(to_address)
        assert issuer_balance == 0
        assert from_balance == 0
        assert to_balance == 0

    #######################################
    # Error
    #######################################

    # Error_1_1
    # Input value type error (from_address)
    def test_transferFrom_error_1_1(self, users, IbetCoupon, coupon_exchange):
        issuer = users['issuer']
        to_address = users['trader']
        value = 100

        # issue coupon token
        deploy_args = init_args(coupon_exchange.address)
        coupon_contract = issuer.deploy(IbetCoupon, *deploy_args)

        # transfer
        with pytest.raises(ValueError):
            coupon_contract.transferFrom.transact(
                '1234',  # string
                to_address,
                value,
                {'from': issuer}
            )
        with pytest.raises(ValueError):
            coupon_contract.transferFrom.transact(
                1234,  # integer
                to_address,
                value,
                {'from': issuer}
            )

    # Error_1_2
    # Input value type error (to_address)
    def test_transferFrom_error_1_2(self, users, IbetCoupon, coupon_exchange):
        issuer = users['issuer']
        value = 100

        # issuer coupon token
        deploy_args = init_args(coupon_exchange.address)
        coupon_contract = issuer.deploy(IbetCoupon, *deploy_args)

        # transfer
        with pytest.raises(ValueError):
            coupon_contract.transferFrom.transact(
                issuer,
                '1234',  # string
                value,
                {'from': issuer}
            )
        with pytest.raises(ValueError):
            coupon_contract.transferFrom.transact(
                issuer,
                1234,  # integer
                value,
                {'from': issuer}
            )

    # Error_1_3
    # Input value type error (value)
    def test_transferFrom_error_1_3(self, users, IbetCoupon, coupon_exchange):
        issuer = users['issuer']
        to_address = users['trader']

        # issue coupon token
        deploy_args = init_args(coupon_exchange.address)
        coupon_contract = issuer.deploy(IbetCoupon, *deploy_args)

        # transfer
        with pytest.raises(TypeError):
            coupon_contract.transferFrom.transact(
                issuer,
                to_address,
                'hundred',  # string
                {'from': issuer}
            )
        with pytest.raises(OverflowError):
            coupon_contract.transferFrom.transact(
                issuer,
                to_address,
                -1,  # minus value
                {'from': issuer}
            )

    # Error_2
    # Over/Under the limit
    def test_transferFrom_error_2(self, users, IbetCoupon, coupon_exchange):
        issuer = users['issuer']
        to_address = users['trader']

        # issue coupon token
        deploy_args = init_args(coupon_exchange.address)
        coupon_contract = issuer.deploy(IbetCoupon, *deploy_args)

        # transfer
        with pytest.raises(OverflowError):
            coupon_contract.transferFrom.transact(
                issuer,
                to_address,
                2 ** 256,  # over the upper limit
                {'from': issuer}
            )
        with pytest.raises(OverflowError):
            coupon_contract.transferFrom.transact(
                issuer,
                to_address,
                -1,  # under the lower limit
                {'from': issuer}
            )

    # Error_3
    # Insufficient balance
    def test_transferFrom_error_3(self, users, IbetCoupon, coupon_exchange):
        issuer = users['issuer']
        to_address = users['trader']

        # issue coupon token
        deploy_args = init_args(coupon_exchange.address)
        coupon_contract = issuer.deploy(IbetCoupon, *deploy_args)

        # transfer
        transfer_amount = 10000000000
        coupon_contract.transferFrom.transact(
            issuer,
            to_address,
            transfer_amount,
            {'from': issuer}
        )  # error

        assert coupon_contract.balanceOf(issuer) == deploy_args[2]
        assert coupon_contract.balanceOf(to_address) == 0

    # Error_4
    # Unauthorized
    def test_transferFrom_error_4(self, users, IbetCoupon, coupon_exchange):
        issuer = users['issuer']
        admin = users['admin']
        to_address = users['trader']
        transfer_amount = 100

        # issue coupon token
        deploy_args = init_args(coupon_exchange.address)
        coupon_contract = issuer.deploy(IbetCoupon, *deploy_args)

        # transfer
        coupon_contract.transferFrom.transact(
            issuer,
            to_address,
            transfer_amount,
            {'from': admin}  # unauthorized account
        )  # error

        assert coupon_contract.balanceOf(issuer) == deploy_args[2]
        assert coupon_contract.balanceOf(to_address) == 0


# TEST_consume
class TestConsume:

    # 正常系1
    # ＜発行者＞発行　->　＜発行者＞消費
    def test_consume_normal_1(self, IbetCoupon, users, coupon_exchange):
        _user = users['issuer']
        _value = 1

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = _user.deploy(IbetCoupon, *deploy_args)

        # 消費
        coupon.consume.transact(_value, {'from': _user})

        balance = coupon.balanceOf(_user)
        used = coupon.usedOf(_user)

        assert balance == deploy_args[2] - _value
        assert used == _value

    # 正常系2
    # ＜発行者＞発行　->　＜発行者＞割当　-> ＜消費者＞消費
    def test_consume_normal_2(self, IbetCoupon, users, coupon_exchange):
        _issuer = users['issuer']
        _consumer = users['trader']
        _value = 1

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = _issuer.deploy(IbetCoupon, *deploy_args)

        # 割当
        coupon.transferFrom.transact(_issuer, _consumer, _value, {'from': _issuer})

        # 消費
        coupon.consume.transact(_value, {'from': _consumer})

        balance_issuer = coupon.balanceOf(_issuer)
        balance_consumer = coupon.balanceOf(_consumer)
        used_consumer = coupon.usedOf(_consumer)

        assert balance_issuer == deploy_args[2] - _value
        assert balance_consumer == 0
        assert used_consumer == _value

    # エラー系1: 入力値の型誤り（Value）
    def test_consume_error_1(self, IbetCoupon, users, coupon_exchange):
        _issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = _issuer.deploy(IbetCoupon, *deploy_args)

        # 消費
        with pytest.raises(TypeError):
            coupon.consume.transact('Z', {'from': _issuer})

        with pytest.raises(OverflowError):
            coupon.consume.transact(2 ** 256, {'from': _issuer})

        with pytest.raises(OverflowError):
            coupon.consume.transact(-1, {'from': _issuer})

    # エラー系2: 残高不足
    def test_consume_error_2(self, IbetCoupon, users, coupon_exchange):
        _issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = _issuer.deploy(IbetCoupon, *deploy_args)

        # 消費
        _value = deploy_args[2] + 1
        coupon.consume.transact(_value, {'from': _issuer})  # エラーになる

        assert coupon.balanceOf(_issuer) == deploy_args[2]
        assert coupon.usedOf(_issuer) == 0

    # エラー系3: 無効化されたクーポンの消費
    def test_consume_error_3(self, IbetCoupon, users, coupon_exchange):
        _issuer = users['issuer']
        _value = 1

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = _issuer.deploy(IbetCoupon, *deploy_args)

        # クーポンの無効化
        coupon.setStatus.transact(False, {'from': _issuer})

        # 消費
        coupon.consume.transact(_value, {'from': _issuer})  # エラーになる

        assert coupon.balanceOf(_issuer) == deploy_args[2]
        assert coupon.usedOf(_issuer) == 0


# TEST_issue
class TestIssue:

    # 正常系1
    # ＜発行者＞発行　->　＜発行者＞追加発行
    def test_issue_normal_1(self, IbetCoupon, users, coupon_exchange):
        _issuer = users['issuer']
        _value = 1

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = _issuer.deploy(IbetCoupon, *deploy_args)

        # 追加発行
        coupon.issue.transact(_value, {'from': _issuer})

        balance = coupon.balanceOf(_issuer)
        total_supply = coupon.totalSupply()

        assert balance == deploy_args[2] + _value
        assert total_supply == deploy_args[2] + _value

    # 正常系2
    # ＜発行者＞発行　->　＜発行者＞割当 -> ＜発行者＞追加発行
    def test_issue_normal_2(self, IbetCoupon, users, coupon_exchange):
        _issuer = users['issuer']
        _consumer = users['trader']
        _allocated = 1
        _value = 10

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = _issuer.deploy(IbetCoupon, *deploy_args)

        # 割当
        coupon.transferFrom.transact(_issuer, _consumer, _allocated, {'from': _issuer})

        # 追加発行
        coupon.issue.transact(_value, {'from': _issuer})

        balance = coupon.balanceOf(_issuer)
        total_supply = coupon.totalSupply()

        assert balance == deploy_args[2] + _value - _allocated
        assert total_supply == deploy_args[2] + _value

    # エラー系1: 入力値の型誤り（Value）
    def test_issue_error_1(self, IbetCoupon, users, coupon_exchange):
        _issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = _issuer.deploy(IbetCoupon, *deploy_args)

        # 追加発行
        with pytest.raises(TypeError):
            coupon.issue.transact('ABC', {'from': _issuer})

        with pytest.raises(OverflowError):
            coupon.issue.transact(2 ** 256, {'from': _issuer})

        with pytest.raises(OverflowError):
            coupon.issue.transact(-1, {'from': _issuer})

    # エラー系2
    # ＜発行者＞発行　->　＜発行者＞追加発行（uint最大値超）
    def test_issue_error_2(self, IbetCoupon, users, coupon_exchange):
        _issuer = users['issuer']
        _consumer = users['trader']
        _allocated = 999999
        _value = 2 ** 256 - 1

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = _issuer.deploy(IbetCoupon, *deploy_args)

        # 割当
        coupon.transferFrom.transact(_issuer, _consumer, _allocated, {'from': _issuer})

        # 追加発行（uint最大値超）
        coupon.issue.transact(_value, {'from': _issuer})  # エラーになる（2**256 -1 +1）

        balance = coupon.balanceOf(_issuer)
        total_supply = coupon.totalSupply()

        assert balance == deploy_args[2] - _allocated
        assert total_supply == deploy_args[2]

    # エラー系3
    # ＜発行者＞発行　->　＜発行者以外＞追加発行
    def test_issue_error_3(self, IbetCoupon, users, coupon_exchange):
        _issuer = users['issuer']
        _other = users['trader']
        _value = 1000

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = _issuer.deploy(IbetCoupon, *deploy_args)

        # 追加発行（uint最大値超）
        coupon.issue.transact(_value, {'from': _other})  # エラーになる

        balance = coupon.balanceOf(_issuer)
        total_supply = coupon.totalSupply()

        assert balance == deploy_args[2]
        assert total_supply == deploy_args[2]


# TEST_setDetails
class TestSetDetails:

    # 正常系1
    # ＜発行者＞発行 -> ＜発行者＞詳細欄の修正
    def test_setDetails_normal_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 詳細欄の修正
        coupon.setDetails.transact('updated details', {'from': issuer})

        details = coupon.details()
        assert details == 'updated details'

    # エラー系1: 入力値の型誤り
    def test_setDetails_error_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 詳細欄の修正
        with pytest.raises(ValueError):
            coupon.setDetails.transact('0x66aB6D9362d4F35596279692F0251Db635165871', {'from': issuer})

    # エラー系2: 権限エラー
    def test_setDetails_error_2(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']
        other = users['trader']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 詳細欄の修正
        coupon.setDetails.transact('updated details', {'from': other})

        details = coupon.details()
        assert details == 'some_details'


# TEST_setMemo
class TestSetMemo:

    # 正常系1
    # ＜発行者＞発行 -> ＜発行者＞メモ欄の修正
    def test_setMemo_normal_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # メモ欄の修正
        coupon.setMemo.transact('updated memo', {'from': issuer})

        details = coupon.memo()
        assert details == 'updated memo'

    # エラー系1: 入力値の型誤り
    def test_setMemo_error_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # メモ欄の修正
        with pytest.raises(ValueError):
            coupon.setMemo.transact('0x66aB6D9362d4F35596279692F0251Db635165871', {'from': issuer})

    # エラー系2: 権限エラー
    def test_setMemo_error_2(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']
        other = users['trader']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # メモ欄の修正
        coupon.setMemo.transact('updated memo', {'from': other})

        details = coupon.memo()
        assert details == 'some_memo'


# TEST_balanceOf
class TestBalanceOf:

    # 正常系1: クーポン新規作成 -> 残高確認
    def test_balanceOf_normal_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        balance = coupon.balanceOf(issuer)
        assert balance == deploy_args[2]

    # エラー系1: 入力値の型誤り（Owner）
    def test_balanceOf_error_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        account_address = 1234

        with pytest.raises(ValueError):
            coupon.balanceOf(account_address)


# TEST_usedOf
class TestUsedOf:

    # 正常系1: クーポン作成 -> 消費 -> 使用済数量確認
    def test_usedOf_normal_1(self, IbetCoupon, users, coupon_exchange):
        _issuer = users['issuer']
        _value = 1

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = _issuer.deploy(IbetCoupon, *deploy_args)

        # 消費
        coupon.consume.transact(_value, {'from': _issuer})

        # 使用済み数量確認
        used = coupon.usedOf(_issuer)

        assert used == _value

    # エラー系1: 入力値の型誤り（Owner）
    def test_usedOf_error_1(self, IbetCoupon, users, coupon_exchange):
        _issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = _issuer.deploy(IbetCoupon, *deploy_args)

        account_address = 1234

        with pytest.raises(ValueError):
            coupon.usedOf(account_address)


# TEST_setImageURL, getImageURL
class TestSetImageUrl:

    # 正常系1: 発行 -> 商品画像の設定
    def test_setImageURL_normal_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 商品画像の設定
        image_url = 'https://some_image_url.com/image.png'
        coupon.setImageURL.transact(0, image_url, {'from': issuer})

        image_url_0 = coupon.getImageURL(0)
        assert image_url_0 == image_url

    # 正常系2: 発行 -> 商品画像の設定（複数設定）
    def test_setImageURL_normal_2(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        image_url = 'https://some_image_url.com/image1.png'

        # 商品画像の設定（1つ目）
        coupon.setImageURL.transact(0, image_url, {'from': issuer})

        # 商品画像の設定（2つ目）
        coupon.setImageURL.transact(1, image_url, {'from': issuer})

        image_url_0 = coupon.getImageURL(0)
        image_url_1 = coupon.getImageURL(1)
        assert image_url_0 == image_url
        assert image_url_1 == image_url

    # 正常系3: 発行（デプロイ） -> 商品画像の設定（上書き登録）
    def test_setImageURL_normal_3(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        image_url = 'https://some_image_url.com/image.png'
        image_url_after = 'https://some_image_url.com/image_after.png'

        # 商品画像の設定（1回目）
        coupon.setImageURL.transact(0, image_url, {'from': issuer})

        # 商品画像の設定（2回目：上書き）
        coupon.setImageURL.transact(0, image_url_after, {'from': issuer})

        image_url_0 = coupon.getImageURL(0)
        assert image_url_0 == image_url_after

    # エラー系1: 入力値の型誤り（Class）
    def test_setImageURL_error_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        image_url = 'https://some_image_url.com/image.png'

        with pytest.raises(OverflowError):
            coupon.setImageURL.transact(-1, image_url, {'from': issuer})

        with pytest.raises(OverflowError):
            coupon.setImageURL.transact(256, image_url, {'from': issuer})

        with pytest.raises(TypeError):
            coupon.setImageURL.transact('a', image_url, {'from': issuer})

        with pytest.raises(OverflowError):
            coupon.getImageURL.transact(-1, {'from': issuer})

        with pytest.raises(OverflowError):
            coupon.getImageURL.transact(256, {'from': issuer})

        with pytest.raises(TypeError):
            coupon.getImageURL.transact('a', {'from': issuer})

    # エラー系2: 入力値の型誤り（ImageURL）
    def test_setImageURL_error_2(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        image_url = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'

        with pytest.raises(ValueError):
            coupon.setImageURL.transact(0, image_url, {'from': issuer})

    # エラー系3: 権限エラー
    def test_setImageURL_error_3(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']
        other = users['admin']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        image_url = 'https://some_image_url.com/image.png'

        # 画像設定
        coupon.setImageURL.transact(0, image_url, {'from': other})  # エラーになる

        image_url_0 = coupon.getImageURL(0)
        assert image_url_0 == ''


# TEST_setStatus
class TestSetStatus:

    # 正常系1
    # ＜発行者＞発行 -> ＜発行者＞ステータスの修正
    def test_setStatus_normal_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # ステータスの修正
        coupon.setStatus.transact(False, {'from': issuer})

        assert coupon.status() is False

    # エラー系1: 入力値の型誤り
    def test_setStatus_error_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # ステータスの修正
        with pytest.raises(ValueError):
            coupon.setStatus.transact('False', {'from': issuer})

    # エラー系2: 権限エラー
    def test_setStatus_error_2(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']
        other = users['trader']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # メモ欄の修正
        coupon.setStatus.transact(False, {'from': other})

        assert coupon.status() is True


# TEST_setTradableExchange
class TestSetTradableExchange:

    # 正常系1: 発行 -> Exchangeの更新
    def test_setTradableExchange_normal_1(self, IbetCoupon, users, coupon_exchange,
                                          coupon_exchange_storage, payment_gateway,
                                          IbetMembershipExchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # Exchange（新）
        other_exchange = users['admin'].deploy(
            IbetMembershipExchange,  # IbetCouponExchange以外を読み込む必要がある
            payment_gateway.address,
            coupon_exchange_storage.address)

        # Exchangeの更新
        coupon.setTradableExchange.transact(other_exchange.address, {'from': issuer})

        assert coupon.tradableExchange() == to_checksum_address(other_exchange.address)

    # エラー系1: 発行 -> Exchangeの更新（入力値の型誤り）
    def test_setTradableExchange_error_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # Exchangeの更新
        with pytest.raises(ValueError):
            coupon.setTradableExchange.transact('0xaaaa', {'from': issuer})

    # エラー系2: 発行 -> Exchangeの更新（権限エラー）
    def test_setTradableExchange_error_2(self, IbetCoupon, users, coupon_exchange, IbetCouponExchange):
        issuer = users['issuer']
        trader = users['trader']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # その他Exchange
        other_exchange = users['admin'].deploy(
            IbetCouponExchange,  # IbetCouponExchange以外を読み込む必要がある
            '0x0000000000000000000000000000000000000000',
            '0x0000000000000000000000000000000000000000'
        )

        # Exchangeの更新
        coupon.setTradableExchange.transact(other_exchange.address, {'from': trader})  # エラーになる

        assert coupon.tradableExchange() == to_checksum_address(coupon_exchange.address)


# TEST_setExpirationDate
class TestSetExpirationDate:

    # 正常系1: 発行 -> 有効期限更新
    def test_setExpirationDate_normal_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']
        after_expiration_date = 'after_expiration_date'

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 有効期限更新
        coupon.setExpirationDate.transact(after_expiration_date, {'from': issuer})

        expiration_date = coupon.expirationDate()
        assert after_expiration_date == expiration_date

    # エラー系1: 入力値の型誤り
    def test_setExpirationDate_errors_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 型誤り
        with pytest.raises(ValueError):
            coupon.setExpirationDate.transact('0x66aB6D9362d4F35596279692F0251Db635165871', {'from': issuer})

    # エラー系2: 権限エラー
    def test_setExpirationDate_error_2(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']
        attacker = users['trader']
        after_expiration_date = 'after_expiration_date'

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 有効期限更新：権限エラー
        coupon.setExpirationDate.transact(after_expiration_date, {'from': attacker})  # エラーになる

        expiration_date = coupon.expirationDate()
        assert expiration_date == deploy_args[7]


# TEST_setTransferable
class TestSetTransferable:

    # 正常系1: 発行 -> 譲渡可能更新
    def test_setTransferable_normal_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']
        after_transferable = False

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 譲渡可能更新
        coupon.setTransferable.transact(after_transferable, {'from': issuer})

        transferable = coupon.transferable()
        assert after_transferable == transferable

    # エラー系1: 入力値の型誤り
    def test_setTransferable_error_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 型誤り
        with pytest.raises(ValueError):
            coupon.setTransferable.transact('True', {'from': issuer})

    # エラー系2: 権限エラー
    def test_setTransferable_error_2(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']
        attacker = users['trader']
        after_transferable = False

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 譲渡可能更新
        coupon.setTransferable.transact(after_transferable, {'from': attacker})  # エラーになる

        transferable = coupon.transferable()
        assert transferable == deploy_args[8]


# TEST_setInitialOfferingStatus
class TestSetInitialOfferingStatus:

    # 正常系1: 発行 -> 新規募集ステータス更新（False→True）
    def test_setInitialOfferingStatus_normal_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # トークン新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 初期状態 == False
        assert coupon.initialOfferingStatus() is False

        # 新規募集ステータスの更新
        coupon.setInitialOfferingStatus.transact(True, {'from': issuer})

        assert coupon.initialOfferingStatus() is True

    # 正常系2:
    #   発行 -> 新規募集ステータス更新（False→True） -> 2回目更新（True→False）
    def test_setInitialOfferingStatus_normal_2(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # トークン新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 新規募集ステータスの更新
        coupon.setInitialOfferingStatus.transact(True, {'from': issuer})

        # 新規募集ステータスの更新（2回目）
        coupon.setInitialOfferingStatus.transact(False, {'from': issuer})

        assert coupon.initialOfferingStatus() is False

    # エラー系1: 発行 -> 新規募集ステータス更新（入力値の型誤り）
    def test_setInitialOfferingStatus_error_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # トークン新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 新規募集ステータスの更新
        with pytest.raises(ValueError):
            coupon.setInitialOfferingStatus.transact('True', {'from': issuer})


# TEST_applyForOffering
class TestApplyForOffering:

    # 正常系1
    #   発行：発行体 -> 投資家：募集申込
    def test_applyForOffering_normal_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']

        # トークン新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 新規募集ステータスの更新
        coupon.setInitialOfferingStatus.transact(True, {'from': issuer})

        # 募集申込
        coupon.applyForOffering.transact('abcdefgh', {'from': trader})

        assert coupon.applications(trader) == 'abcdefgh'

    # 正常系2
    #   発行：発行体 -> （申込なし）初期データ参照
    def test_applyForOffering_normal_2(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']

        # トークン新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 新規募集ステータスの更新
        coupon.setInitialOfferingStatus.transact(True, {'from': issuer})

        assert coupon.applications(trader) == ''

    # エラー系1:
    #   発行：発行体 -> 投資家：募集申込（入力値の型誤り）
    def test_applyForOffering_error_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']

        # トークン新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 新規募集ステータスの更新
        coupon.setInitialOfferingStatus.transact(True, {'from': issuer})

        # 募集申込
        with pytest.raises(ValueError):
            coupon.applyForOffering.transact('0x66aB6D9362d4F35596279692F0251Db635165871', {'from': trader})

    # エラー系2:
    #   発行：発行体 -> 投資家：募集申込（申込ステータスが停止中）
    def test_applyForOffering_error_2(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']
        trader = users['trader']

        # トークン新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 募集申込
        coupon.applyForOffering.transact('abcdefgh', {'from': trader})

        assert coupon.applications(trader) == ''


# TEST_setReturnDetails
class TestSetReturnDetails:

    # 正常系1: 発行 -> 詳細更新
    def test_setReturnDetails_normal_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']
        after_return_details = 'after_return_details'

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # リターン詳細更新
        coupon.setReturnDetails.transact(after_return_details, {'from': issuer})

        return_details = coupon.returnDetails()
        assert after_return_details == return_details

    # エラー系1: 入力値の型誤り
    def test_setReturnDetails_error_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 型誤り
        with pytest.raises(ValueError):
            coupon.setReturnDetails.transact('0x66aB6D9362d4F35596279692F0251Db635165871', {'from': issuer})

    # エラー系2: 権限エラー
    def test_setReturnDetails_error_2(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']
        attacker = users['trader']
        after_return_details = 'after_return_details'

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # リターン詳細更新：権限エラー
        coupon.setReturnDetails.transact(after_return_details, {'from': attacker})  # エラーになる

        return_details = coupon.returnDetails()
        assert return_details == deploy_args[5]


# TEST_setContactInformation
class TestSetContactInformation:

    # 正常系1
    # ＜発行者＞発行 -> ＜発行者＞問い合わせ先情報の修正
    def test_setContactInformation_normal_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 修正
        coupon.setContactInformation.transact('updated contact information', {'from': issuer})

        contact_information = coupon.contactInformation()
        assert contact_information == 'updated contact information'

    # エラー系1: 入力値の型誤り
    def test_setContactInformation_error_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 修正
        with pytest.raises(ValueError):
            coupon.setContactInformation.transact('0x66aB6D9362d4F35596279692F0251Db635165871', {'from': issuer})

    # エラー系2: 権限エラー
    def test_setContactInformation_error_2(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']
        other = users['trader']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 修正
        coupon.setContactInformation.transact('updated contact information', {'from': other})

        contact_information = coupon.contactInformation()
        assert contact_information == 'some_contact_information'


# TEST_setPrivacyPolicy
class TestSetPrivacyPolicy:

    # 正常系1
    # ＜発行者＞発行 -> ＜発行者＞プライバシーポリシーの修正
    def test_setPrivacyPolicy_normal_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 修正
        coupon.setPrivacyPolicy.transact('updated privacy policy', {'from': issuer})

        privacy_policy = coupon.privacyPolicy()
        assert privacy_policy == 'updated privacy policy'

    # エラー系1: 入力値の型誤り
    def test_setPrivacyPolicy_error_1(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 修正
        with pytest.raises(ValueError):
            coupon.setPrivacyPolicy.transact('0x66aB6D9362d4F35596279692F0251Db635165871', {'from': issuer})

    # エラー系2: 権限エラー
    def test_setPrivacyPolicy_error_2(self, IbetCoupon, users, coupon_exchange):
        issuer = users['issuer']
        other = users['trader']

        # 新規発行
        deploy_args = init_args(coupon_exchange.address)
        coupon = issuer.deploy(IbetCoupon, *deploy_args)

        # 修正
        coupon.setPrivacyPolicy.transact('updated privacy policy', {'from': other})

        privacy_policy = coupon.privacyPolicy()
        assert privacy_policy == 'some_privacy_policy'
