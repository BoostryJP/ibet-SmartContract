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
from collections import OrderedDict

import pytest
import utils
from eth_utils import to_checksum_address

zero_address = '0x0000000000000000000000000000000000000000'


def init_args():
    name = 'test_share'
    symbol = 'IBS'
    issue_price = 10000
    total_supply = 10000
    devidends = 1000
    devidend_record_date = '20200829'
    devidend_payment_date = '20200831'
    cancellation_date = '20191231'
    principal_value = 10000

    deploy_args = [
        name,
        symbol,
        issue_price,
        total_supply,
        devidends,
        devidend_record_date,
        devidend_payment_date,
        cancellation_date,
        principal_value
    ]
    return deploy_args


# TEST_deploy
class TestDeploy:

    # 正常系1: deploy
    def test_deploy_normal_1(self, IbetShare, users):
        account_address = users['issuer']
        deploy_args = init_args()

        share_contract = account_address.deploy(
            IbetShare,
            *deploy_args
        )

        owner_address = share_contract.owner()
        name = share_contract.name()
        symbol = share_contract.symbol()
        issue_price = share_contract.issuePrice()
        total_supply = share_contract.totalSupply()
        dividend_information = share_contract.dividendInformation()
        cancellation_date = share_contract.cancellationDate()

        assert owner_address == account_address
        assert name == deploy_args[0]
        assert symbol == deploy_args[1]
        assert issue_price == deploy_args[2]
        assert total_supply == deploy_args[3]
        assert dividend_information[0] == deploy_args[4]
        assert dividend_information[1] == deploy_args[5]
        assert dividend_information[2] == deploy_args[6]
        assert cancellation_date == deploy_args[7]

    # エラー系1: 入力値の型誤り（name）
    def test_deploy_error_1(self, users, IbetShare):
        deploy_args = init_args()
        deploy_args[0] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'
        with pytest.raises(ValueError):
            users['admin'].deploy(IbetShare, *deploy_args)

    # エラー系2: 入力値の型誤り（symbol）
    def test_deploy_error_2(self, users, IbetShare):
        deploy_args = init_args()
        deploy_args[1] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'
        with pytest.raises(ValueError):
            users['admin'].deploy(IbetShare, *deploy_args)

    # エラー系3: 入力値の型誤り（issuePrice）
    def test_deploy_error_3(self, users, IbetShare):
        deploy_args = init_args()
        deploy_args[2] = "a10000"
        with pytest.raises(TypeError):
            users['admin'].deploy(IbetShare, *deploy_args)

    # エラー系4: 入力値の型誤り（totalSupply）
    def test_deploy_error_4(self, users, IbetShare):
        deploy_args = init_args()
        deploy_args[3] = "a10000"
        with pytest.raises(TypeError):
            users['admin'].deploy(IbetShare, *deploy_args)

    # エラー系5: 入力値の型誤り（dividends）
    def test_deploy_error_5(self, users, IbetShare):
        deploy_args = init_args()
        deploy_args[4] = "a1000"
        with pytest.raises(TypeError):
            users['admin'].deploy(IbetShare, *deploy_args)

    # エラー系6: 入力値の型誤り（dividendRecordDate）
    def test_deploy_error_6(self, users, IbetShare):
        deploy_args = init_args()
        deploy_args[5] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'
        with pytest.raises(ValueError):
            users['admin'].deploy(IbetShare, *deploy_args)

    # エラー系7: 入力値の型誤り（dividendPaymentDate）
    def test_deploy_error_7(self, users, IbetShare):
        deploy_args = init_args()
        deploy_args[6] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'
        with pytest.raises(ValueError):
            users['admin'].deploy(IbetShare, *deploy_args)

    # エラー系8: 入力値の型誤り（cancellationDate）
    def test_deploy_error_8(self, users, IbetShare):
        deploy_args = init_args()
        deploy_args[7] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'
        with pytest.raises(ValueError):
            users['admin'].deploy(IbetShare, *deploy_args)


# TEST_setPrincipalValue
class TestSetPrincipalValue:

    # Normal_1
    def test_setPrincipalValue_normal_1(self, users):
        issuer = users["issuer"]

        # issue token
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=zero_address
        )

        # update principal value
        share_token.setPrincipalValue.transact(
            9000,
            {"from": issuer}
        )

        # assertion
        assert share_token.principalValue() == 9000

    # Error_1
    # type error
    def test_setPrincipalValue_error_1(self, users):
        issuer = users["issuer"]

        # issue token (from issuer)
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=zero_address
        )

        # update principal value
        with pytest.raises(TypeError):
            share_token.setPrincipalValue.transact(
                "invalid type",
                {"from": issuer}
            )

    # Error_2
    # authorization error
    def test_setPrincipalValue_error_2(self, users):
        trader = users['trader']

        # issue token (form issuer)
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=zero_address
        )

        # update principal value
        share_token.setPrincipalValue.transact(
            9000,
            {"from": trader}
        )

        # assertion
        assert share_token.principalValue() == 10000


# TEST_setTradableExchange
class TestSetTradableExchange:

    # 正常系1: 発行 -> Exchangeの更新
    def test_setTradableExchange_normal_1(self, users, share_exchange, personal_info,
                                          coupon_exchange_storage, payment_gateway,
                                          IbetCouponExchange):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # その他Exchange
        other_exchange = users['admin'].deploy(
            IbetCouponExchange,  # IbetShareExchange以外を読み込む必要がある
            payment_gateway.address,
            coupon_exchange_storage.address
        )

        # Exchangeの更新
        share_token.setTradableExchange.transact(other_exchange.address, {'from': issuer})

        assert share_token.tradableExchange() == to_checksum_address(other_exchange.address)

    # エラー系1: 発行 -> Exchangeの更新（入力値の型誤り）
    def test_setTradableExchange_error_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # Exchangeの更新
        with pytest.raises(ValueError):
            share_token.setTradableExchange.transact('0xaaaa', {'from': issuer})

    # エラー系2: 発行 -> Exchangeの更新（権限エラー）
    def test_setTradableExchange_error_2(self, users, share_exchange, personal_info,
                                         coupon_exchange_storage, payment_gateway,
                                         IbetCouponExchange):
        trader = users['trader']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # その他Exchange
        other_exchange = users['admin'].deploy(
            IbetCouponExchange,  # IbetShareExchange以外を読み込む必要がある
            payment_gateway.address,
            coupon_exchange_storage.address
        )

        # Exchangeの更新
        share_token.setTradableExchange.transact(other_exchange.address, {'from': trader})  # エラーになる

        assert share_token.tradableExchange() == to_checksum_address(share_exchange.address)


# TEST_setPersonalInfoAddress
class TestSetPersonalInfoAddress:

    # 正常系1: トークン発行 -> 更新
    def test_setPersonalInfoAddress_normal_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 更新
        share_token.setPersonalInfoAddress.transact('0x0000000000000000000000000000000000000000', {'from': issuer})

        assert share_token.personalInfoAddress() == '0x0000000000000000000000000000000000000000'

    # エラー系1: トークン発行 -> 更新（入力値の型誤り）
    def test_setPersonalInfoAddress_error_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 更新
        with pytest.raises(ValueError):
            share_token.setPersonalInfoAddress.transact('0xaaaa', {'from': issuer})

    # エラー系2: トークン発行 -> 更新（権限エラー）
    def test_setPersonalInfoAddress_error_2(self, users, share_exchange, personal_info):
        attacker = users['trader']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 更新
        share_token.setPersonalInfoAddress.transact('0x0000000000000000000000000000000000000000', {'from': attacker})

        assert share_token.personalInfoAddress() == to_checksum_address(personal_info.address)


# TEST_setDividendInformation
class TestSetDividendInformation:

    # 正常系1: 発行（デプロイ） -> 修正
    def test_setDividendInformation_normal_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 修正 -> Success
        share_token.setDividendInformation.transact(22000, '20200829', '20200831', {'from': issuer})

        dividend_information = share_token.dividendInformation()
        assert dividend_information[0] == 22000
        assert dividend_information[1] == '20200829'
        assert dividend_information[2] == '20200831'

    # エラー系1: 入力値の型誤り
    def test_setDividendInformation_error_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        invalid_str = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'
        with pytest.raises(TypeError):
            share_token.setDividendInformation.transact("abcd", '20200829', '20200831', {'from': issuer})
        with pytest.raises(ValueError):
            share_token.setDividendInformation.transact(1234, invalid_str, '20200831', {'from': issuer})
        with pytest.raises(ValueError):
            share_token.setDividendInformation.transact(1234, '20200829', invalid_str, {'from': issuer})

    # エラー系2: 権限エラー
    def test_setDividendInformation_error_2(self, users, share_exchange, personal_info):
        other = users['admin']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # Owner以外のアドレスから更新 -> Failure
        share_token.setDividendInformation.transact(33000, '20200830', '20200901', {'from': other})

        dividend_information = share_token.dividendInformation()
        assert dividend_information[0] == 1000
        assert dividend_information[1] == '20200830'
        assert dividend_information[2] == '20200831'


# TEST_setCancellationDate
class TestSetCancellationDate:

    # 正常系1: 発行（デプロイ） -> 修正
    def test_setCancellationDate_normal_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 修正 -> Success
        share_token.setCancellationDate.transact('20200831', {'from': issuer})

        cancellation_date = share_token.cancellationDate()
        assert cancellation_date == '20200831'

    # エラー系1: 入力値の型誤り
    def test_setCancellationDate_error_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        with pytest.raises(ValueError):
            share_token.setCancellationDate.transact('0x1596Ff8ED308a83897a731F3C1e814B19E11D68c', {'from': issuer})

    # エラー系2: 権限エラー
    def test_setCancellationDate_error_2(self, users, share_exchange, personal_info):
        other = users['admin']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # Owner以外のアドレスから更新 -> Failure
        share_token.setCancellationDate.transact('20200930', {'from': other})

        cancellation_date = share_token.cancellationDate()
        assert cancellation_date == '20211231'


# TEST_SetReferenceUrls
class TestSetReferenceUrls:

    # 正常系1: 発行（デプロイ） -> 商品画像の設定
    def test_setReferenceUrls_normal_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        reference_url = 'https://some_reference_url.com/image.png'

        # 商品画像の設定 -> Success
        share_token.setReferenceUrls.transact(0, reference_url, {'from': issuer})

        reference_urls = share_token.referenceUrls(0)
        assert reference_urls == 'https://some_reference_url.com/image.png'

    # 正常系2: 発行（デプロイ） -> 商品画像の設定（複数設定）
    def test_setReferenceUrls_normal_2(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        reference_url = 'https://some_reference_url.com/image.png'

        # 商品画像の設定（1つ目） -> Success
        share_token.setReferenceUrls.transact(0, reference_url, {'from': issuer})

        # 商品画像の設定（2つ目） -> Success
        share_token.setReferenceUrls.transact(1, reference_url, {'from': issuer})

        reference_url_0 = share_token.referenceUrls(0)
        reference_url_1 = share_token.referenceUrls(1)
        assert reference_url_0 == 'https://some_reference_url.com/image.png'
        assert reference_url_1 == 'https://some_reference_url.com/image.png'

    # 正常系3: 発行（デプロイ） -> 商品画像の設定（上書き登録）
    def test_setReferenceUrls_normal_3(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        reference_url = 'https://some_reference_url.com/image.png'
        reference_url_after = 'https://some_reference_url.com/image_after.png'

        # 商品画像の設定（1回目） -> Success
        share_token.setReferenceUrls.transact(0, reference_url, {'from': issuer})

        # 商品画像の設定（2回目：上書き） -> Success
        share_token.setReferenceUrls.transact(0, reference_url_after, {'from': issuer})

        reference_url = share_token.referenceUrls(0)
        assert reference_url == 'https://some_reference_url.com/image_after.png'

    # エラー系1: 入力値の型誤り（Class）
    def test_setReferenceUrls_error_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        reference_url = 'https://some_reference_url.com/image.png'

        with pytest.raises(OverflowError):
            share_token.setReferenceUrls.transact(-1, reference_url, {'from': issuer})

        with pytest.raises(OverflowError):
            share_token.setReferenceUrls.transact(256, reference_url, {'from': issuer})

        with pytest.raises(TypeError):
            share_token.setReferenceUrls.transact('a', reference_url, {'from': issuer})

    # エラー系2: 入力値の型誤り（referenceUrl）
    def test_setReferenceUrls_error_2(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        reference_url = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'

        with pytest.raises(ValueError):
            share_token.setReferenceUrls.transact(0, reference_url, {'from': issuer})

    # エラー系3: Issuer以外のアドレスからリファレンス設定を実施した場合
    def test_setReferenceUrls_error_3(self, users, share_exchange, personal_info):
        other = users['admin']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        reference_url = 'https://some_reference_url.com/image.png'

        # Owner以外のアドレスからリファレンス設定を実施 -> Failure
        share_token.setReferenceUrls.transact(0, reference_url, {'from': other})

        reference_url = share_token.referenceUrls(0)
        assert reference_url == ''


# TEST_setContactInformation
class TestSetContactInformation:

    # 正常系1: 発行（デプロイ） -> 修正
    def test_setContactInformation_normal_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 修正 -> Success
        share_token.setContactInformation.transact('updated contact information', {'from': issuer})

        contact_information = share_token.contactInformation()
        assert contact_information == 'updated contact information'

    # エラー系1: 入力値の型誤り
    def test_setContactInformation_error_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        with pytest.raises(ValueError):
            share_token.setContactInformation.transact('0x1596Ff8ED308a83897a731F3C1e814B19E11D68c', {'from': issuer})

    # エラー系2: 権限エラー
    def test_setContactInformation_error_2(self, users, share_exchange, personal_info):
        other = users['admin']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # Owner以外のアドレスから更新 -> Failure
        share_token.setContactInformation.transact('updated contact information', {'from': other})

        contact_information = share_token.contactInformation()
        assert contact_information == 'some_contact_information'


# TEST_setPrivacyPolicy
class TestSetPrivacyPolicy:

    # 正常系1: 発行（デプロイ） -> 修正
    def test_setPrivacyPolicy_normal_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 修正 -> Success
        share_token.setPrivacyPolicy.transact('updated privacy policy', {'from': issuer})

        privacy_policy = share_token.privacyPolicy()
        assert privacy_policy == 'updated privacy policy'

    # エラー系1: 入力値の型誤り
    def test_setPrivacyPolicy_error_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        with pytest.raises(ValueError):
            share_token.setPrivacyPolicy.transact('0x1596Ff8ED308a83897a731F3C1e814B19E11D68c', {'from': issuer})

    # エラー系2: 権限エラー
    def test_setPrivacyPolicy_error_2(self, users, share_exchange, personal_info):
        other = users['admin']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # Owner以外のアドレスから更新 -> Failure
        share_token.setPrivacyPolicy.transact('updated privacy policy', {'from': other})

        privacy_policy = share_token.privacyPolicy()
        assert privacy_policy == 'some_privacy_policy'


# TEST_setMemo
class TestSetMemo:

    # 正常系1: 発行（デプロイ） -> メモ欄の修正
    def test_setMemo_normal_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # メモ欄の修正 -> Success
        share_token.setMemo.transact('updated memo', {'from': issuer})

        memo = share_token.memo()
        assert memo == 'updated memo'

    # エラー系1: 入力値の型誤り
    def test_setMemo_error_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        with pytest.raises(ValueError):
            share_token.setMemo.transact('0x1596Ff8ED308a83897a731F3C1e814B19E11D68c', {'from': issuer})

    # エラー系2: Owner以外のアドレスからメモ欄の修正を実施した場合
    def test_setMemo_error_2(self, users, share_exchange, personal_info):
        other = users['admin']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # Owner以外のアドレスからメモ欄の修正を実施 -> Failure
        share_token.setMemo.transact('updated memo', {'from': other})

        memo = share_token.memo()
        assert memo == 'some_memo'


# TEST_setTransferable
class TestSetTransferable:

    # 正常系1: 発行 -> 譲渡可能更新
    def test_setTransferable_normal_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']
        after_transferable = False

        # 新規発行
        share_contract, deploy_args = \
            utils.issue_share_token(users, share_exchange.address, personal_info.address)

        # 譲渡可能更新
        share_contract.setTransferable.transact(after_transferable, {'from': issuer})

        transferable = share_contract.transferable()
        assert after_transferable == transferable

    # エラー系1: 入力値の型誤り
    def test_setTransferable_error_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 新規発行
        share_contract, deploy_args = \
            utils.issue_share_token(users, share_exchange.address, personal_info.address)

        # 型誤り
        with pytest.raises(ValueError):
            share_contract.setTransferable.transact('False', {'from': issuer})

    # エラー系2: 権限エラー
    def test_setTransferable_error_2(self, users, share_exchange, personal_info):
        attacker = users['trader']
        after_transferable = False

        # 新規発行
        share_contract, deploy_args = \
            utils.issue_share_token(users, share_exchange.address, personal_info.address)

        # 譲渡可能更新
        share_contract.setTransferable.transact(after_transferable, {'from': attacker})  # エラーになる

        transferable = share_contract.transferable()
        assert transferable == True


# TEST_setOfferingStatus
class TestSetOfferingStatus:

    # 正常系1: 発行 -> 新規募集ステータス更新（False→True）
    def test_setOfferingStatus_normal_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # トークン新規発行
        share_token, deploy_args = \
            utils.issue_share_token(users, share_exchange.address, personal_info.address)

        # 初期状態 == False
        assert share_token.offeringStatus() is False

        # 新規募集ステータスの更新
        share_token.setOfferingStatus.transact(True, {'from': issuer})

        assert share_token.offeringStatus() is True

    # 正常系2:
    #   発行 -> 新規募集ステータス更新（False→True） -> 2回目更新（True→False）
    def test_setOfferingStatus_normal_2(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # トークン新規発行
        share_token, deploy_args = \
            utils.issue_share_token(users, share_exchange.address, personal_info.address)

        # 新規募集ステータスの更新
        share_token.setOfferingStatus.transact(True, {'from': issuer})

        # 新規募集ステータスの更新（2回目）
        share_token.setOfferingStatus.transact(False, {'from': issuer})

        assert share_token.offeringStatus() is False

    # エラー系1: 発行 -> 新規募集ステータス更新（入力値の型誤り）
    def test_setOfferingStatus_error_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # トークン新規発行
        share_token, deploy_args = \
            utils.issue_share_token(users, share_exchange.address, personal_info.address)

        # 新規募集ステータスの更新（エラー）：文字型
        with pytest.raises(ValueError):
            share_token.setOfferingStatus.transact('True', {'from': issuer})


# TEST_balanceOf
class TestBalanceOf:

    # 正常系1: 商品コントラクト作成 -> 残高確認
    def test_balanceOf_normal_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        balance = share_token.balanceOf(issuer)
        assert balance == 10000

    # エラー系1: 入力値の型誤り（Owner）
    def test_balanceOf_error_1(self, users, share_exchange, personal_info):
        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        account_address = 1234

        with pytest.raises(ValueError):
            share_token.balanceOf(account_address)


# TEST_authorize
class TestAuthorize:

    # 正常系1: 商品コントラクト作成 -> アドレス認可 -> 認可情報変更
    def test_authorize_normal_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']
        trader = users['trader']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 認可
        share_token.authorize.transact(trader, True, {'from': issuer})

        auth_trader = share_token.authorizedAddress(trader)
        auth_issuer = share_token.authorizedAddress(issuer)
        assert auth_trader == True
        assert auth_issuer == False

        # 変更
        share_token.authorize.transact(trader, False, {'from': issuer})

        auth_trader = share_token.authorizedAddress(trader)
        assert auth_trader == False

    # エラー系1: 入力値の型誤り（address, auth）
    def test_authorize_error_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # アドレス指定誤り
        with pytest.raises(ValueError):
            share_token.authorize.transact('0x1234', True, {'from': issuer})

        # アドレス指定誤り
        with pytest.raises(ValueError):
            share_token.authorize.transact(issuer, 'True', {'from': issuer})


# TEST_lock
class TestLock:

    # 正常系1: 認可済みアドレスに対するロック（商品コントラクト作成 -> 移管 -> 認可 -> ロック）
    def test_lock_normal_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']
        transfer_amount = 30
        lock_amount = 10

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 投資家に移管
        share_token.transferFrom.transact(issuer, trader, transfer_amount, {'from': issuer})

        # agentを認可
        share_token.authorize.transact(agent, True, {'from': issuer})

        # agentに対してtraderが自身の保有をロック
        share_token.lock.transact(agent, lock_amount, {'from': trader})

        trader_amount = share_token.balanceOf(trader)
        trader_locked_amount = share_token.lockedOf(agent, trader)

        assert trader_amount == transfer_amount - lock_amount
        assert trader_locked_amount == lock_amount

    # 正常系2: 発行体に対するロック（商品コントラクト作成 -> 移管 -> ロック）
    def test_lock_normal_2(self, users, share_exchange, personal_info):
        issuer = users['issuer']
        trader = users['trader']

        transfer_amount = 30
        lock_amount = 10

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 投資家に移管
        share_token.transferFrom.transact(issuer, trader, transfer_amount, {'from': issuer})

        # issuerに対してtraderが自身の保有をロック
        share_token.lock.transact(issuer, lock_amount, {'from': trader})

        trader_amount = share_token.balanceOf(trader)
        trader_locked_amount = share_token.lockedOf(issuer, trader)

        assert trader_amount == transfer_amount - lock_amount
        assert trader_locked_amount == lock_amount

    # 異常系1: 入力値の型誤り
    def test_lock_error_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']
        trader = users['trader']

        transfer_amount = 30
        lock_amount = 10

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 投資家に移管
        share_token.transferFrom.transact(issuer, trader, transfer_amount, {'from': issuer})

        # アドレス指定誤り
        with pytest.raises(ValueError):
            share_token.lock.transact('0x1234', lock_amount, {'from': trader})

        # 数量指定誤り
        with pytest.raises(TypeError):
            share_token.lock.transact(issuer, 'A', {'from': trader})

        trader_amount = share_token.balanceOf(trader)
        trader_locked_amount = share_token.lockedOf(issuer, trader)

        assert trader_amount == transfer_amount
        assert trader_locked_amount == 0

    # 異常系2: 数量超過
    def test_lock_error_2(self, users, share_exchange, personal_info):
        issuer = users['issuer']
        trader = users['trader']

        transfer_amount = 30
        lock_amount = 40

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 投資家に移管
        share_token.transferFrom.transact(issuer, trader, transfer_amount, {'from': issuer})

        share_token.lock.transact(issuer, lock_amount, {'from': trader})

        trader_amount = share_token.balanceOf(trader)
        trader_locked_amount = share_token.lockedOf(issuer, trader)

        assert trader_amount == transfer_amount
        assert trader_locked_amount == 0

    # 異常系3: 認可外アドレスに対するlock（認可はあるがFalse）
    def test_lock_error_3(self, users, share_exchange, personal_info):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']
        transfer_amount = 30
        lock_amount = 10

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 投資家に移管
        share_token.transferFrom.transact(issuer, trader, transfer_amount, {'from': issuer})

        # agentを非認可
        share_token.authorize.transact(agent, False, {'from': issuer})

        # agentに対してtraderが自身の保有をロック
        share_token.lock.transact(agent, lock_amount, {'from': trader})

        trader_amount = share_token.balanceOf(trader)
        trader_locked_amount = share_token.lockedOf(agent, trader)

        assert trader_amount == transfer_amount
        assert trader_locked_amount == 0

    # 異常系4: 認可外アドレスに対するlock（認可が存在しない）
    def test_lock_error_4(self, users, share_exchange, personal_info):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']
        transfer_amount = 30
        lock_amount = 10

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 投資家に移管
        share_token.transferFrom.transact(issuer, trader, transfer_amount, {'from': issuer})

        # agentに対してtraderが自身の保有をロック
        share_token.lock.transact(agent, lock_amount, {'from': trader})

        trader_amount = share_token.balanceOf(trader)
        trader_locked_amount = share_token.lockedOf(agent, trader)

        assert trader_amount == transfer_amount
        assert trader_locked_amount == 0


# TEST_lockedOf
class TestLockedOf:

    # 異常系1: 型エラー
    def test_lockedOf_error_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']
        trader = users['trader']
        transfer_amount = 30
        lock_amount = 10

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 投資家に移管
        share_token.transferFrom.transact(issuer, trader, transfer_amount, {'from': issuer})

        # issuerに対してtraderが自身の保有をロック
        share_token.lock.transact(issuer, lock_amount, {'from': trader})

        # アドレス指定誤り
        with pytest.raises(ValueError):
            share_token.lockedOf.transact('0x1234', trader, {'from': trader})

        # アドレス指定誤り
        with pytest.raises(ValueError):
            share_token.lockedOf.transact(issuer, '0x1234', {'from': trader})


# TEST_unlock
class TestUnlock:

    # 正常系1: 認可済みアドレスによるアンロック（商品コントラクト作成 -> 移管 -> 認可 -> ロック -> アンロック）
    def test_unlock_normal_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']
        transfer_amount = 30
        lock_amount = 10
        unlock_amount = 3

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 投資家に移管
        share_token.transferFrom.transact(issuer, trader, transfer_amount, {'from': issuer})

        # agentを認可
        share_token.authorize.transact(agent, True, {'from': issuer})

        # agentに対してtraderが自身の保有をロック
        share_token.lock.transact(agent, lock_amount, {'from': trader})

        # agentによりtraderの保有をアンロック（agentへ）
        share_token.unlock.transact(trader, agent, unlock_amount, {'from': agent})

        # agentによりtraderの保有をアンロック（traderへ）
        share_token.unlock.transact(trader, trader, unlock_amount, {'from': agent})

        trader_amount = share_token.balanceOf(trader)
        agent_amount = share_token.balanceOf(agent)
        trader_locked_amount = share_token.lockedOf(agent, trader)

        assert trader_amount == transfer_amount - lock_amount + unlock_amount
        assert agent_amount == unlock_amount
        assert trader_locked_amount == lock_amount - unlock_amount - unlock_amount

    # 正常系2: 発行体によるアンロック（商品コントラクト作成 -> 移管 -> 認可 -> ロック -> アンロック）
    def test_unlock_normal_2(self, users, share_exchange, personal_info):
        issuer = users['issuer']
        trader = users['trader']

        transfer_amount = 30
        lock_amount = 10
        unlock_amount = 3

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 投資家に移管
        share_token.transferFrom.transact(issuer, trader, transfer_amount, {'from': issuer})

        # issuerに対してtraderが自身の保有をロック
        share_token.lock.transact(issuer, lock_amount, {'from': trader})

        # issuerによりtraderの保有をアンロック（issuerへ）
        share_token.unlock.transact(trader, issuer, unlock_amount, {'from': issuer})

        # issuerによりtraderの保有をアンロック（traderへ）
        share_token.unlock.transact(trader, trader, unlock_amount, {'from': issuer})

        trader_amount = share_token.balanceOf(trader)
        issuer_amount = share_token.balanceOf(issuer)
        trader_locked_amount = share_token.lockedOf(issuer, trader)

        assert trader_amount == transfer_amount - lock_amount + unlock_amount
        assert issuer_amount == deploy_args[3] - transfer_amount + unlock_amount
        assert trader_locked_amount == lock_amount - unlock_amount - unlock_amount

    # 異常系1: 入力値の型誤り
    def test_unlock_error_1(self, users, share_exchange, personal_info):
        issuer = users['issuer']
        trader = users['trader']

        transfer_amount = 30
        lock_amount = 10
        unlock_amount = 3

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 投資家に移管
        share_token.transferFrom.transact(issuer, trader, transfer_amount, {'from': issuer})

        # issuerに対してtraderが自身の保有をロック
        share_token.lock.transact(issuer, lock_amount, {'from': trader})

        # アドレス誤り
        with pytest.raises(ValueError):
            share_token.unlock.transact('0x1111', issuer, unlock_amount, {'from': trader})

        # アドレス誤り
        with pytest.raises(ValueError):
            share_token.unlock.transact(trader, '0x1234', unlock_amount, {'from': trader})

        # 数量指定誤り
        with pytest.raises(TypeError):
            share_token.unlock.transact(trader, issuer, 'three', {'from': trader})

        trader_amount = share_token.balanceOf(trader)
        trader_locked_amount = share_token.lockedOf(issuer, trader)

        assert trader_amount == transfer_amount - lock_amount
        assert trader_locked_amount == lock_amount

    # 異常系2: 数量超過
    def test_unlock_error_2(self, users, share_exchange, personal_info):
        issuer = users['issuer']
        trader = users['trader']

        transfer_amount = 30
        lock_amount = 10
        unlock_amount = 11

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 投資家に移管
        share_token.transferFrom.transact(issuer, trader, transfer_amount, {'from': issuer})

        # issuerに対してtraderが自身の保有をロック
        share_token.lock.transact(issuer, lock_amount, {'from': trader})

        # lock数量よりも多いunlockをする
        share_token.unlock.transact(trader, issuer, unlock_amount, {'from': issuer})

        trader_amount = share_token.balanceOf(trader)
        trader_locked_amount = share_token.lockedOf(issuer, trader)

        assert trader_amount == transfer_amount - lock_amount
        assert trader_locked_amount == lock_amount

    # 異常系3: 認可外アドレスによるunlock（認可はあるがFalse）
    def test_unlock_error_3(self, users, share_exchange, personal_info):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        transfer_amount = 30
        lock_amount = 10
        unlock_amount = 3

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 投資家に移管
        share_token.transferFrom.transact(issuer, trader, transfer_amount, {'from': issuer})

        # agentを非認可
        share_token.authorize.transact(agent, False, {'from': issuer})

        # issuerに対してtraderが自身の保有をロック
        share_token.lock.transact(issuer, lock_amount, {'from': trader})

        # 非認可アドレスからアンロック
        share_token.unlock.transact(trader, agent, unlock_amount, {'from': agent})

        trader_amount = share_token.balanceOf(trader)
        trader_locked_amount = share_token.lockedOf(issuer, trader)

        assert trader_amount == transfer_amount - lock_amount
        assert trader_locked_amount == lock_amount

    # 異常系4: 認可外アドレスによるunlock（認可がない）
    def test_unlock_error_4(self, users, share_exchange, personal_info):
        issuer = users['issuer']
        trader = users['trader']
        agent = users['agent']

        transfer_amount = 30
        lock_amount = 10
        unlock_amount = 3

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 投資家に移管
        share_token.transferFrom.transact(issuer, trader, transfer_amount, {'from': issuer})

        # issuerに対してtraderが自身の保有をロック
        share_token.lock.transact(issuer, lock_amount, {'from': trader})

        # 認可のないアドレスからアンロック
        share_token.unlock.transact(trader, agent, unlock_amount, {'from': agent})

        trader_amount = share_token.balanceOf(trader)
        trader_locked_amount = share_token.lockedOf(issuer, trader)

        assert trader_amount == transfer_amount - lock_amount
        assert trader_locked_amount == lock_amount


# TEST_transfer
class TestTransfer:

    ################################################################
    # Normal Case
    ################################################################

    # Normal_1
    # Transfer to EOA
    def test_normal_1(self, users, share_exchange, personal_info):
        from_address = users["issuer"]
        to_address = users["trader"]
        transfer_amount = 100

        # prepare the initial state
        share_contract, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=share_exchange.address,
            personal_info_address=personal_info.address
        )
        utils.register_personal_info(
            from_account=to_address,
            personal_info=personal_info,
            link_address=from_address
        )

        # transfer
        tx = share_contract.transfer.transact(
            to_address,
            transfer_amount,
            {"from": from_address}
        )

        # assertion
        from_balance = share_contract.balanceOf(from_address)
        to_balance = share_contract.balanceOf(to_address)
        assert from_balance == deploy_args[3] - transfer_amount
        assert to_balance == transfer_amount
        assert tx.events["Transfer"] == OrderedDict([
            ("from", from_address),
            ("to", to_address),
            ("value", transfer_amount)
        ])

    # Normal_2
    # Transfer to contract address
    def test_normal_2(self, users, share_exchange, personal_info):
        from_address = users["issuer"]
        transfer_amount = 100

        # prepare the initial state
        share_contract, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=share_exchange.address,
            personal_info_address=personal_info.address
        )

        # transfer
        to_address = share_exchange.address
        tx = share_contract.transfer.transact(
            to_address,
            transfer_amount,
            {"from": from_address}
        )

        # assertion
        from_balance = share_contract.balanceOf(from_address)
        to_balance = share_contract.balanceOf(to_address)
        assert from_balance == deploy_args[3] - transfer_amount
        assert to_balance == transfer_amount
        assert tx.events["Transfer"] == OrderedDict([
            ("from", from_address),
            ("to", to_address),
            ("value", transfer_amount)
        ])

    ################################################################
    # Error Case
    ################################################################

    # Error_1
    # Insufficient balance
    def test_error_1(self, users, share_exchange, personal_info):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["trader"]

        # prepare the initial state
        share_contract, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=share_exchange.address,
            personal_info_address=personal_info.address
        )
        utils.register_personal_info(
            from_account=to_address,
            personal_info=personal_info,
            link_address=from_address
        )

        # transfer
        transfer_amount = deploy_args[3] + 1
        share_contract.transfer.transact(
            to_address,
            transfer_amount,
            {"from": issuer}
        )

        # assertion
        assert share_contract.balanceOf(issuer) == deploy_args[3]
        assert share_contract.balanceOf(to_address) == 0

    # Error_2
    # Cannot access private function
    def test_error_2(self, users, share_exchange, personal_info):
        issuer = users["issuer"]
        from_address = issuer
        to_address = users["trader"]

        transfer_amount = 100
        data = 0

        # prepare the initial state
        share_contract, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=share_exchange.address,
            personal_info_address=personal_info.address
        )

        with pytest.raises(AttributeError):
            share_contract.isContract(to_address)

        with pytest.raises(AttributeError):
            share_contract.transferToAddress.transact(
                to_address,
                transfer_amount,
                data,
                {"from": from_address}
            )

        with pytest.raises(AttributeError):
            share_contract.transferToContract.transact(
                to_address,
                transfer_amount,
                data,
                {"from": from_address}
            )

    # Error_3
    # Transfer to non-tradable exchange
    def test_error_3(
            self, users,
            share_exchange, personal_info,
            coupon_exchange_storage, payment_gateway,
            IbetCouponExchange
    ):
        from_address = users["issuer"]
        transfer_amount = 100

        # prepare the initial state
        share_contract, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=share_exchange.address,
            personal_info_address=personal_info.address
        )
        non_tradable_exchange = users["admin"].deploy(
            IbetCouponExchange,
            payment_gateway.address,
            coupon_exchange_storage.address
        )

        # transfer
        to_address = non_tradable_exchange.address
        share_contract.transfer.transact(
            to_address,
            transfer_amount,
            {"from": users["admin"]}
        )

        from_balance = share_contract.balanceOf(from_address)
        to_balance = share_contract.balanceOf(to_address)
        assert from_balance == deploy_args[3]
        assert to_balance == 0

    # Error_4
    # Not transferable token
    def test_error_4(self, users, share_exchange, personal_info):
        issuer = users["issuer"]
        to_address = users["trader"]
        transfer_amount = 100

        # prepare the initial state
        share_contract, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=share_exchange.address,
            personal_info_address=personal_info.address
        )
        utils.register_personal_info(
            from_account=to_address,
            personal_info=personal_info,
            link_address=issuer
        )

        # set to non-transferable
        share_contract.setTransferable.transact(
            False,
            {"from": issuer}
        )

        # transfer
        share_contract.transfer.transact(
            to_address,
            transfer_amount,
            {"from": issuer}
        )

        # assertion
        from_balance = share_contract.balanceOf(issuer)
        to_balance = share_contract.balanceOf(to_address)
        assert from_balance == deploy_args[3]
        assert to_balance == 0

    # Error_5
    # Transfer to an address with personal information not registered
    def test_error_5(self, users, share_exchange, personal_info):
        issuer = users["issuer"]
        to_address = users["trader"]
        transfer_amount = 100

        # prepare the initial state
        share_contract, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=share_exchange.address,
            personal_info_address=personal_info.address
        )

        # transfer
        share_contract.transfer.transact(
            to_address,  # personal information not registered
            transfer_amount,
            {"from": issuer}
        )

        # assertion
        from_balance = share_contract.balanceOf(issuer)
        to_balance = share_contract.balanceOf(to_address)
        assert from_balance == deploy_args[3]
        assert to_balance == 0

    # Error_6
    # Tokens that require transfer approval
    def test_error_6(self, users, share_exchange, personal_info):
        issuer = users["issuer"]
        to_address = users["trader"]
        transfer_amount = 100

        # prepare the initial state
        share_contract, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=share_exchange.address,
            personal_info_address=personal_info.address
        )
        share_contract.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # transfer
        share_contract.transfer.transact(
            to_address,
            transfer_amount,
            {"from": issuer}
        )

        # assertion
        from_balance = share_contract.balanceOf(issuer)
        to_balance = share_contract.balanceOf(to_address)
        assert from_balance == deploy_args[3]
        assert to_balance == 0


# TEST_bulkTransfer
class TestBulkTransfer:

    ################################################################
    # Normal Case
    ################################################################

    # Normal_1
    # Bulk transfer to account address (1 data)
    def test_normal_1(self, users, share_exchange, personal_info):
        from_address = users["issuer"]
        to_address = users["trader"]

        # issue share token
        share_contract, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=share_exchange.address,
            personal_info_address=personal_info.address
        )

        # register personal info (to_address)
        utils.register_personal_info(to_address, personal_info, from_address)

        # bulk transfer
        to_address_list = [to_address]
        amount_list = [1]
        share_contract.bulkTransfer.transact(to_address_list, amount_list, {"from": from_address})

        # assertion
        from_balance = share_contract.balanceOf(from_address)
        to_balance = share_contract.balanceOf(to_address)
        assert from_balance == deploy_args[2] - 1
        assert to_balance == 1

    # Normal_2
    # Bulk transfer to account address (multiple data)
    def test_normal_2(self, users, share_exchange, personal_info):
        from_address = users["issuer"]
        to_address = users["trader"]

        # issue share token
        share_contract, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=share_exchange.address,
            personal_info_address=personal_info.address
        )

        # register personal info (to_address)
        utils.register_personal_info(to_address, personal_info, from_address)

        # bulk transfer
        to_address_list = []
        amount_list = []
        for i in range(100):
            to_address_list.append(to_address)
            amount_list.append(1)

        share_contract.bulkTransfer.transact(
            to_address_list,
            amount_list,
            {"from": from_address}
        )

        # assertion
        from_balance = share_contract.balanceOf(from_address)
        to_balance = share_contract.balanceOf(to_address)
        assert from_balance == deploy_args[2] - 100
        assert to_balance == 100

    # Normal_3
    # Bulk transfer to contract address
    def test_normal_3(self, users, share_exchange, personal_info):
        from_address = users["issuer"]

        # issue share token
        share_contract, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=share_exchange.address,
            personal_info_address=personal_info.address
        )

        # bulk transfer
        to_address_list = [share_exchange.address]
        amount_list = [1]
        share_contract.bulkTransfer.transact(
            to_address_list,
            amount_list,
            {"from": from_address}
        )

        # assertion
        from_balance = share_contract.balanceOf(from_address)
        to_balance = share_contract.balanceOf(share_exchange.address)
        assert from_balance == deploy_args[2] - 1
        assert to_balance == 1

    ################################################################
    # Error Case
    ################################################################

    # Error_1_1
    # Input value type error (to_list)
    def test_error_1_1(self, users, share_exchange, personal_info):
        from_address = users["issuer"]
        to_address = 1234
        transfer_amount = 1

        # issue share token
        share_contract, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=share_exchange.address,
            personal_info_address=personal_info.address
        )

        # bulk transfer
        with pytest.raises(ValueError):
            share_contract.bulkTransfer.transact(
                [to_address],
                [transfer_amount],
                {"from": from_address}
            )

    # Error_1_2
    # Input value type error (value_list)
    def test_error_1_2(self, users, share_exchange, personal_info):
        from_address = users["issuer"]
        to_address = users["trader"]
        transfer_amount = "abc"

        # issue share token
        share_contract, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=share_exchange.address,
            personal_info_address=personal_info.address
        )

        # bulk transfer
        with pytest.raises(TypeError):
            share_contract.bulkTransfer.transact(
                [to_address],
                [transfer_amount],
                {"from": from_address}
            )

    # Error_2
    # Over/Under the limit
    def test_error_2(self, users, share_exchange, personal_info):
        from_address = users['issuer']
        to_address = users['trader']

        # issue share token
        share_contract, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=share_exchange.address,
            personal_info_address=personal_info.address
        )

        # over the upper limit
        share_contract.bulkTransfer.transact(
            [to_address, to_address],
            [2 ** 256 - 1, 1],
            {'from': from_address}
        )  # error
        from_balance = share_contract.balanceOf(from_address)
        to_balance = share_contract.balanceOf(to_address)
        assert from_balance == deploy_args[2]
        assert to_balance == 0

        # under the lower limit
        with pytest.raises(OverflowError):
            share_contract.bulkTransfer.transact(
                [to_address],
                [-1],
                {'from': from_address}
            )

    # Error_3
    # Insufficient balance
    def test_error_3(self, users, share_exchange, personal_info):
        issuer = users['issuer']
        from_address = issuer
        to_address = users['trader']

        # issue share token
        share_contract, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=share_exchange.address,
            personal_info_address=personal_info.address
        )

        # register personal info (to_address)
        utils.register_personal_info(to_address, personal_info, from_address)

        # bulk transfer
        share_contract.bulkTransfer.transact(
            [to_address, to_address],
            [10000, 1],
            {'from': issuer}
        )  # error
        assert share_contract.balanceOf(issuer) == 10000
        assert share_contract.balanceOf(to_address) == 0

    # Error_4
    # Non-transferable token
    def test_error_4(self, users, share_exchange, personal_info):
        issuer = users["issuer"]
        to_address = users["trader"]

        # issue share token
        share_contract, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=share_exchange.address,
            personal_info_address=personal_info.address
        )

        # register personal info (to_address)
        utils.register_personal_info(to_address, personal_info, issuer)

        # change to non-transferable
        share_contract.setTransferable.transact(False, {"from": issuer})

        # bulk transfer
        share_contract.bulkTransfer.transact(
            [to_address],
            [1],
            {"from": issuer}
        )  # error

        # assertion
        from_balance = share_contract.balanceOf(issuer)
        to_balance = share_contract.balanceOf(to_address)
        assert from_balance == deploy_args[2]
        assert to_balance == 0

    # Error_5
    # Transfer to an address with no personal information registered
    def test_error_5(self, users, share_exchange, personal_info):
        issuer = users["issuer"]
        to_address = users["trader"]

        # issue share token
        share_contract, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=share_exchange.address,
            personal_info_address=personal_info.address
        )

        # bulk transfer
        share_contract.bulkTransfer.transact(
            [to_address],
            [1],
            {'from': issuer}
        )  # error

        # assertion
        from_balance = share_contract.balanceOf(issuer)
        to_balance = share_contract.balanceOf(to_address)
        assert from_balance == deploy_args[2]
        assert to_balance == 0

    # Error_6
    # Tokens that require transfer approval
    def test_error_6(self, users, share_exchange, personal_info):
        issuer = users["issuer"]
        to_address = users["trader"]

        # prepare the initial state
        share_contract, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=share_exchange.address,
            personal_info_address=personal_info.address
        )
        share_contract.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # bulk transfer
        share_contract.bulkTransfer.transact(
            [to_address],
            [1],
            {'from': issuer}
        )

        # assertion
        from_balance = share_contract.balanceOf(issuer)
        to_balance = share_contract.balanceOf(to_address)
        assert from_balance == deploy_args[3]
        assert to_balance == 0


# TEST_transferFrom
class TestTransferFrom:

    # 正常系1: アカウントアドレスへの移転
    def test_transferFrom_normal_1(self, users, share_exchange, personal_info):
        _issuer = users['issuer']
        _from = users['admin']
        _to = users['trader']
        _value = 100

        # 株式トークン新規発行
        share_contract, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 振替先の個人情報登録（_from）
        utils.register_personal_info(_from, personal_info, _issuer)

        # 譲渡（issuer -> _from）
        share_contract.transfer.transact(_from, _value, {'from': _issuer})

        # 移転（_from -> _to）
        share_contract.transferFrom.transact(_from, _to, _value, {'from': _issuer})

        issuer_balance = share_contract.balanceOf(_issuer)
        from_balance = share_contract.balanceOf(_from)
        to_balance = share_contract.balanceOf(_to)

        assert issuer_balance == deploy_args[3] - _value
        assert from_balance == 0
        assert to_balance == _value

    # エラー系1: 入力値の型誤り（From）
    def test_transferFrom_error_1(self, users, share_exchange, personal_info):
        _issuer = users['issuer']
        _to = users['trader']
        _value = 100

        # 株式トークン新規発行
        share_contract, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 移転（_from -> _to）

        with pytest.raises(ValueError):
            share_contract.transferFrom.transact('1234', _to, _value, {'from': _issuer})

        with pytest.raises(ValueError):
            share_contract.transferFrom.transact(1234, _to, _value, {'from': _issuer})

    # エラー系2: 入力値の型誤り（To）
    def test_transferFrom_error_2(self, users, share_exchange, personal_info):
        _issuer = users['issuer']
        _from = users['admin']
        _value = 100

        # 株式トークン新規発行
        share_contract, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 移転（_from -> _to）

        with pytest.raises(ValueError):
            share_contract.transferFrom.transact(_from, '1234', _value, {'from': _issuer})

        with pytest.raises(ValueError):
            share_contract.transferFrom.transact(_from, 1234, _value, {'from': _issuer})

    # エラー系3: 入力値の型誤り（Value）
    def test_transferFrom_error_3(self, users, share_exchange, personal_info):
        _issuer = users['issuer']
        _from = users['admin']
        _to = users['trader']

        # 株式トークン新規発行
        share_contract, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 移転（_from -> _to）

        with pytest.raises(OverflowError):
            share_contract.transferFrom.transact(_from, _to, -1, {'from': _issuer})

        with pytest.raises(OverflowError):
            share_contract.transferFrom.transact(_from, _to, 2 ** 256, {'from': _issuer})

        with pytest.raises(TypeError):
            share_contract.transferFrom.transact(_from, _to, 'zero', {'from': _issuer})

    # エラー系4: 残高不足
    def test_transferFrom_error_4(self, users, share_exchange, personal_info):
        _issuer = users['issuer']
        _from = users['admin']
        _to = users['trader']
        _value = 100

        # 株式トークン新規発行
        share_contract, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 振替先の個人情報登録（_from）
        utils.register_personal_info(_from, personal_info, _issuer)

        # 譲渡（issuer -> _from）
        share_contract.transfer.transact(_from, _value, {'from': _issuer})

        # 移転（_from -> _to）
        share_contract.transferFrom.transact(_from, _to, 101, {'from': _issuer})  # エラーになる

        issuer_balance = share_contract.balanceOf(_issuer)
        from_balance = share_contract.balanceOf(_from)
        to_balance = share_contract.balanceOf(_to)

        assert issuer_balance == deploy_args[3] - _value
        assert from_balance == _value
        assert to_balance == 0

    # エラー系5: 権限エラー
    def test_transferFrom_error_5(self, users, share_exchange, personal_info):
        _issuer = users['issuer']
        _from = users['admin']
        _to = users['trader']
        _value = 100

        # 株式トークン新規発行
        share_contract, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, personal_info.address)

        # 振替先の個人情報登録（_from）
        utils.register_personal_info(_from, personal_info, _issuer)

        # 譲渡（issuer -> _from）
        share_contract.transfer.transact(_from, _value, {'from': _issuer})

        # 移転（_from -> _to）
        share_contract.transferFrom.transact(_from, _to, _value, {'from': _from})  # エラーになる

        issuer_balance = share_contract.balanceOf(_issuer)
        from_balance = share_contract.balanceOf(_from)
        to_balance = share_contract.balanceOf(_to)

        assert issuer_balance == deploy_args[3] - _value
        assert from_balance == _value
        assert to_balance == 0


# TEST_applyForOffering
class TestApplyForOffering:

    # 正常系1
    #   発行：発行体 -> （申込なし）初期データ参照
    def test_applyForOffering_normal_1(self, users):
        trader = users['trader']

        # トークン新規発行
        share_token, deploy_args = \
            utils.issue_share_token(users, zero_address, zero_address)

        application = share_token.applications(trader)
        assert application[0] == 0
        assert application[1] == 0
        assert application[2] == ''

    # 正常系2
    #   発行：発行体 -> 投資家：募集申込
    def test_applyForOffering_normal_2(self, users, personal_info):
        issuer = users['issuer']
        trader = users['trader']

        # トークン新規発行
        share_token, deploy_args = \
            utils.issue_share_token(users, zero_address, personal_info.address)

        # 新規募集ステータスの更新
        share_token.setOfferingStatus.transact(True, {'from': issuer})

        # 個人情報登録
        utils.register_personal_info(trader, personal_info, issuer)

        # 募集申込
        share_token.applyForOffering.transact(10, 'abcdefgh', {'from': trader})

        application = share_token.applications(trader)
        assert application[0] == 10
        assert application[1] == 0
        assert application[2] == 'abcdefgh'

    # 正常系3
    #   発行：発行体 -> 投資家：募集申込（複数回）
    def test_applyForOffering_normal_3(self, users, personal_info):
        issuer = users['issuer']
        trader = users['trader']

        # トークン新規発行
        share_token, deploy_args = \
            utils.issue_share_token(users, zero_address, personal_info.address)

        # 新規募集ステータスの更新
        share_token.setOfferingStatus.transact(True, {'from': issuer})

        # 個人情報登録
        utils.register_personal_info(trader, personal_info, issuer)

        # 募集申込
        share_token.applyForOffering.transact(10, 'abcdefgh', {'from': trader})

        # 募集申込：２回目
        share_token.applyForOffering.transact(20, 'vwxyz', {'from': trader})

        application = share_token.applications(trader)
        assert application[0] == 20
        assert application[1] == 0
        assert application[2] == 'vwxyz'

    # エラー系1:
    #   発行：発行体 -> 投資家：募集申込（入力値の型誤り）
    def test_applyForOffering_error_1(self, users):
        trader = users['trader']

        # トークン新規発行
        share_token, deploy_args = \
            utils.issue_share_token(users, zero_address, zero_address)

        # 募集申込（エラー）：amount 文字型
        with pytest.raises(TypeError):
            share_token.applyForOffering.transact("ten", "1234", {'from': trader})

        # 募集申込（エラー）：data 数値型
        with pytest.raises(ValueError):
            share_token.applyForOffering.transact(
                10,
                '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c',
                {'from': trader}
            )

    # エラー系2:
    #   発行：発行体 -> 投資家：募集申込（申込ステータスが停止中）
    def test_applyForOffering_error_2(self, users):
        trader = users['trader']

        # トークン新規発行
        share_token, deploy_args = \
            utils.issue_share_token(users, zero_address, zero_address)

        # 募集申込（エラー）：募集申込ステータスFalse状態での申込
        share_token.applyForOffering.transact(10, 'abcdefgh', {'from': trader})

        application = share_token.applications(trader)
        assert application[0] == 0
        assert application[1] == 0
        assert application[2] == ''

    # エラー系3
    #   発行：発行体 -> 投資家：募集申込（個人情報未登録）
    def test_applyForOffering_error_3(self, users, personal_info):
        issuer = users['issuer']
        trader = users['trader']

        # トークン新規発行
        share_token, deploy_args = \
            utils.issue_share_token(users, zero_address, personal_info.address)

        # 新規募集ステータスの更新
        share_token.setOfferingStatus.transact(True, {'from': issuer})

        # 個人情報未登録

        # 募集申込（エラーになる）
        share_token.applyForOffering.transact(10, 'abcdefgh', {'from': trader})

        application = share_token.applications(trader)
        assert application[0] == 0
        assert application[1] == 0
        assert application[2] == ''


# TEST_allot
class TestAllot:

    # 正常系1
    #   発行：発行体 -> 投資家：募集申込 -> 発行体：募集割当
    def test_allot_normal_1(self, users, personal_info):
        issuer = users['issuer']
        trader = users['trader']

        # トークン新規発行
        share_token, deploy_args = utils.issue_share_token(users, zero_address, personal_info.address)

        # 新規募集ステータスの更新
        share_token.setOfferingStatus.transact(True, {'from': issuer})

        # 個人情報登録
        utils.register_personal_info(trader, personal_info, issuer)

        # 募集申込
        share_token.applyForOffering.transact(10, 'abcdefgh', {'from': trader})

        # 割当
        share_token.allot.transact(trader, 5, {'from': issuer})

        application = share_token.applications(trader)
        assert application[0] == 10
        assert application[1] == 5
        assert application[2] == 'abcdefgh'

    # エラー系1
    #   発行：発行体 -> 投資家：募集申込 -> 発行体：募集割当（入力値の型誤り）
    def test_allot_error_1(self, users):
        issuer = users['issuer']
        trader = users['trader']

        # トークン新規発行
        share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

        # 新規募集ステータスの更新
        share_token.setOfferingStatus.transact(True, {'from': issuer})

        # 割当（エラー）：address 数値型
        with pytest.raises(ValueError):
            share_token.allot.transact(1234, 5, {'from': issuer})

        # 割当（エラー）：amount 文字型
        with pytest.raises(TypeError):
            share_token.allot.transact(trader, "five", {'from': issuer})

    # エラー系2
    #   発行：発行体 -> 投資家：募集申込 -> 発行体：募集割当（権限エラー）
    def test_allot_error_2(self, users):
        issuer = users['issuer']
        trader = users['trader']

        # トークン新規発行
        share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

        # 新規募集ステータスの更新
        share_token.setOfferingStatus.transact(True, {'from': issuer})

        # 割当（エラー）：権限エラー
        share_token.allot.transact(trader, 5, {'from': trader})

        application = share_token.applications(trader)
        assert application[0] == 0
        assert application[1] == 0
        assert application[2] == ''


# TEST_issueFrom
class TestIssueFrom:

    # 正常系1: 発行 -> 増資（発行体自身のアドレスに増資）
    def test_issueFrom_normal_1(self, users):
        issuer = users['issuer']
        value = 10

        # トークン新規発行
        share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

        # 増資
        share_token.issueFrom.transact(issuer, zero_address, value, {'from': issuer})

        total_supply = share_token.totalSupply()
        balance = share_token.balanceOf(issuer)

        assert total_supply == deploy_args[3] + value
        assert balance == deploy_args[3] + value

    # 正常系2: 発行 -> 増資（投資家想定のEOAアドレスのアドレスを増資）
    def test_issueFrom_normal_2(self, users):
        issuer = users['issuer']
        trader = users['trader']
        value = 10

        # トークン新規発行
        share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

        # 増資
        share_token.issueFrom.transact(trader, zero_address, value, {'from': issuer})

        total_supply = share_token.totalSupply()
        balance_issuer = share_token.balanceOf(issuer)
        balance_trader = share_token.balanceOf(trader)

        assert total_supply == deploy_args[3] + value
        assert balance_issuer == deploy_args[3]
        assert balance_trader == value

    # 正常系3: 発行 -> 譲渡 -> ロック -> ロック済み数量の増資（from issuer）
    def test_issueFrom_normal_3(self, users, share_exchange):
        issuer = users['issuer']
        trader = users['trader']

        transfer_amount = 30
        lock_amount = 10

        value = 5

        # 株式トークン新規発行
        share_token, deploy_args = utils. \
            issue_share_token(users, share_exchange.address, zero_address)

        # 投資家に移管
        share_token.transferFrom.transact(issuer, trader, transfer_amount, {'from': issuer})

        # issuerに対してtraderが自身の保有をロック
        share_token.lock.transact(issuer, lock_amount, {'from': trader})

        # 増資
        share_token.issueFrom.transact(issuer, trader, value, {'from': issuer})

        trader_amount = share_token.balanceOf(trader)
        trader_locked_amount = share_token.lockedOf(issuer, trader)

        assert trader_amount == transfer_amount - lock_amount
        assert trader_locked_amount == lock_amount + value

    # エラー系1: 入力値の型誤り
    def test_issueFrom_error_1(self, users):
        issuer = users['issuer']

        # トークン新規発行
        share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

        # String
        with pytest.raises(TypeError):
            share_token.issueFrom.transact(issuer, zero_address, "a", {'from': issuer})

        # アドレス不正
        with pytest.raises(ValueError):
            share_token.issueFrom.transact("0x00", zero_address, 1, {'from': issuer})

        # アドレス不正（locked_address）
        with pytest.raises(ValueError):
            share_token.issueFrom.transact(issuer, "0x00", 1, {'from': issuer})

    # エラー系2: 限界値超（balance）
    def test_issueFrom_error_2(self, users):
        issuer = users['issuer']

        # トークン新規発行
        share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

        # 上限値超
        with pytest.raises(OverflowError):
            share_token.issueFrom.transact(issuer, zero_address, 2 ** 256, {'from': issuer})

        # 下限値超
        with pytest.raises(OverflowError):
            share_token.issueFrom.transact(issuer, zero_address, -1, {'from': issuer})

    # エラー系3 限界値超（locked）
    def test_issueFrom_error_3(self, users):
        issuer = users['issuer']
        trader = users['trader']

        # トークン新規発行
        share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

        # 上限値超
        with pytest.raises(OverflowError):
            share_token.issueFrom.transact(issuer, trader, 2 ** 256, {'from': issuer})

        # 下限値超
        with pytest.raises(OverflowError):
            share_token.issueFrom.transact(issuer, trader, -1, {'from': issuer})

    # エラー系4: 発行→増資→上限界値超
    def test_issueFrom_error_4(self, users):
        issuer = users['issuer']
        trader = users['trader']

        # トークン新規発行
        share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

        issue_amount = 2 ** 256 - deploy_args[3]

        # 増資（限界値超）
        share_token.issueFrom.transact(issuer, zero_address, issue_amount, {'from': issuer})  # エラーになる

        share_token.issueFrom.transact(issuer, trader, issue_amount, {'from': issuer})  # エラーになる

        total_supply = share_token.totalSupply()
        balance = share_token.balanceOf(issuer)

        assert total_supply == deploy_args[3]
        assert balance == deploy_args[3]

    # エラー系5: 権限エラー
    def test_issueFrom_error_5(self, users):
        issuer = users['issuer']
        attacker = users['trader']

        # トークン新規発行
        share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

        # 増資：権限エラー
        share_token.issueFrom.transact(attacker, zero_address, 1, {'from': attacker})  # エラーになる

        total_supply = share_token.totalSupply()
        balance = share_token.balanceOf(issuer)

        assert total_supply == deploy_args[3]
        assert balance == deploy_args[3]


# TEST_redeemFrom
class TestRedeemFrom:

    # 正常系1: 発行 -> 減資（発行体自身のアドレスの保有を減資）
    def test_redeemFrom_normal_1(self, users):
        issuer = users['issuer']
        value = 10

        # トークン新規発行
        share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

        # 減資
        share_token.redeemFrom.transact(issuer, zero_address, value, {'from': issuer})

        total_supply = share_token.totalSupply()
        balance = share_token.balanceOf(issuer)

        assert total_supply == deploy_args[3] - value
        assert balance == deploy_args[3] - value

    # 正常系2: 発行 -> 減資（投資家想定のEOAアドレスの保有を減資）
    def test_redeemFrom_normal_2(self, users):
        issuer = users['issuer']
        trader = users['trader']
        transfer_amount = 30
        value = 10

        # トークン新規発行
        share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

        # traderとexchangeに譲渡
        share_token.transferFrom.transact(issuer, trader, transfer_amount, {'from': issuer})

        # 減資
        share_token.redeemFrom.transact(trader, zero_address, value, {'from': issuer})

        total_supply = share_token.totalSupply()
        balance_issuer = share_token.balanceOf(issuer)
        balance_trader = share_token.balanceOf(trader)

        assert total_supply == deploy_args[3] - value
        assert balance_issuer == deploy_args[3] - transfer_amount
        assert balance_trader == transfer_amount - value

    # 正常系3: 発行 -> ロック -> 減資（投資家想定のEOAアドレスのロック数量を減資）
    def test_redeemFrom_normal_3(self, users):
        issuer = users['issuer']
        trader = users['trader']
        transfer_amount = 30
        lock_amount = 10
        value = 5

        # トークン新規発行
        share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

        # traderに譲渡
        share_token.transferFrom.transact(issuer, trader, transfer_amount, {'from': issuer})

        # issuerに対してtraderが自身の保有をロック
        share_token.lock.transact(issuer, lock_amount, {'from': trader})

        # 減資
        share_token.redeemFrom.transact(issuer, trader, value, {'from': issuer})

        total_supply = share_token.totalSupply()
        balance_issuer = share_token.balanceOf(issuer)
        balance_trader = share_token.balanceOf(trader)
        balance_trader_lock = share_token.locked(issuer, trader)

        assert total_supply == deploy_args[3] - value
        assert balance_issuer == deploy_args[3] - transfer_amount
        assert balance_trader == transfer_amount - lock_amount
        assert balance_trader_lock == lock_amount - value

    # エラー系1: 入力値の型誤り
    def test_redeemFrom_error_1(self, users):
        issuer = users['issuer']

        # トークン新規発行
        share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

        # String
        with pytest.raises(TypeError):
            share_token.redeemFrom.transact(issuer, zero_address, "a", {'from': issuer})

        # アドレス不正
        with pytest.raises(ValueError):
            share_token.redeemFrom.transact("0x00", zero_address, 1, {'from': issuer})

        # アドレス不正
        with pytest.raises(ValueError):
            share_token.redeemFrom.transact(issuer, "0x00", 1, {'from': issuer})

    # エラー系2: 限界値超
    def test_redeemFrom_error_2(self, users):
        issuer = users['issuer']

        # トークン新規発行
        share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

        # 下限値超
        with pytest.raises(OverflowError):
            share_token.redeemFrom.transact(issuer, zero_address, -1, {'from': issuer})

    # エラー系3: 発行→減資→発行数量より下限を超過
    def test_redeemFrom_error_3(self, users):
        issuer = users['issuer']

        # トークン新規発行
        share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

        redeem_amount = deploy_args[3] + 1

        # 減資（限界値超）
        share_token.redeemFrom.transact(issuer, zero_address, redeem_amount, {'from': issuer})  # エラーになる

        total_supply = share_token.totalSupply()
        balance = share_token.balanceOf(issuer)

        assert total_supply == deploy_args[3]
        assert balance == deploy_args[3]

    # エラー系4: 発行→ロック→減資→ロック数量より下限を超過
    def test_redeemFrom_error_4(self, users):
        issuer = users['issuer']
        trader = users['trader']
        transfer_amount = 30
        lock_amount = 10
        redeem_amount = lock_amount + 1

        # トークン新規発行
        share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

        # traderに譲渡
        share_token.transferFrom.transact(issuer, trader, transfer_amount, {'from': issuer})

        # issuerに対してtraderが自身の保有をロック
        share_token.lock.transact(issuer, lock_amount, {'from': trader})

        # 減資（限界値超）
        share_token.redeemFrom.transact(issuer, trader, redeem_amount, {'from': issuer})  # エラーになる

        total_supply = share_token.totalSupply()
        issuer_balance = share_token.balanceOf(issuer)
        trader_balance = share_token.balanceOf(trader)
        trader_locked = share_token.locked(issuer, trader)

        assert total_supply == deploy_args[3]
        assert issuer_balance == deploy_args[3] - transfer_amount
        assert trader_balance == transfer_amount - lock_amount
        assert trader_locked == lock_amount

    # エラー系5: 権限エラー
    def test_redeemFrom_error_5(self, users):
        issuer = users['issuer']
        attacker = users['trader']

        # トークン新規発行
        share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

        # 減資：権限エラー
        share_token.redeemFrom.transact(attacker, zero_address, 1, {'from': attacker})  # エラーになる

        total_supply = share_token.totalSupply()
        balance = share_token.balanceOf(issuer)

        assert total_supply == deploy_args[3]
        assert balance == deploy_args[3]


# TEST_applyForTransfer
class TestApplyForTransfer:

    ################################################################
    # Normal Case
    ################################################################

    # Normal_1
    def test_normal_1(self, users, personal_info):
        issuer = users["issuer"]
        to_address = users["user1"]

        # prepare data
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=personal_info.address
        )
        share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )
        utils.register_personal_info(
            from_account=to_address,
            personal_info=personal_info,
            link_address=issuer
        )

        # apply for transfer
        tx = share_token.applyForTransfer(
            to_address,
            100,
            "test_data",
            {"from": issuer}
        )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - 100
        assert share_token.balances(to_address) == 0
        assert share_token.pendingTransfer(issuer) == 100
        assert share_token.applicationsForTransfer(0) == \
               (issuer, to_address, 100, True)
        assert tx.events["ApplyForTransfer"] == OrderedDict([
            ("index", 0),
            ("from", issuer),
            ("to", to_address),
            ("value", 100),
            ("data", "test_data")
        ])

    # Normal_2
    # Multiple execution
    def test_normal_2(self, users, personal_info):
        issuer = users["issuer"]
        to_address = users["user1"]

        # prepare data
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=personal_info.address
        )
        share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )
        utils.register_personal_info(
            from_account=to_address,
            personal_info=personal_info,
            link_address=issuer
        )

        # apply for transfer
        for i in range(2):
            share_token.applyForTransfer(
                to_address,
                100,
                "test_data",
                {"from": issuer}
            )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - 200
        assert share_token.balances(to_address) == 0
        assert share_token.pendingTransfer(issuer) == 200
        for i in range(2):
            assert share_token.applicationsForTransfer(i) == \
                   (issuer, to_address, 100, True)

    # Normal_3
    # Transfer to the issuer
    # No need to register personal information
    def test_normal_3(self, users, personal_info):
        issuer = users["issuer"]
        to_address = users["issuer"]

        # prepare data
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=personal_info.address
        )
        share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # apply for transfer
        share_token.applyForTransfer(
            to_address,
            100,
            "test_data",
            {"from": issuer}
        )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - 100
        assert share_token.pendingTransfer(issuer) == 100
        assert share_token.applicationsForTransfer(0) == \
               (issuer, to_address, 100, True)

    ################################################################
    # Error Case
    ################################################################

    # Error_1
    # transferApprovalRequired = false
    def test_error_1(self, users):
        issuer = users["issuer"]
        to_address = users["user1"]

        # prepare data
        # default value: transferApprovalRequired = false
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=zero_address
        )

        # apply for transfer
        share_token.applyForTransfer(
            to_address,
            100,
            "test_data",
            {"from": issuer}
        )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3]
        assert share_token.balances(to_address) == 0
        assert share_token.pendingTransfer(issuer) == 0

    # Error_2
    # Insufficient balance
    def test_error_2(self, users):
        issuer = users["issuer"]
        to_address = users["user1"]

        # prepare data
        # default value: transferApprovalRequired = false
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=zero_address
        )
        share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # apply for transfer
        share_token.applyForTransfer(
            to_address,
            deploy_args[3] + 1,
            "test_data",
            {"from": issuer}
        )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3]
        assert share_token.balances(to_address) == 0
        assert share_token.pendingTransfer(issuer) == 0

    # Error_3
    # Personal information is not registered
    def test_error_3(self, users):
        issuer = users["issuer"]
        to_address = users["user1"]

        # prepare data
        # default value: transferApprovalRequired = false
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=zero_address
        )
        share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # apply for transfer
        share_token.applyForTransfer(
            to_address,
            100,
            "test_data",
            {"from": issuer}
        )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3]
        assert share_token.balances(to_address) == 0
        assert share_token.pendingTransfer(issuer) == 0


# TEST_cancelTransfer
class TestCancelTransfer:

    ################################################################
    # Normal Case
    ################################################################

    # Normal_1
    # Applicant
    def test_normal_1(self, users, personal_info):
        issuer = users["issuer"]
        user1 = users["user1"]
        user2 = users["user2"]

        # prepare data
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=personal_info.address
        )
        share_token.transferFrom(
            issuer,
            user1,
            100,
            {"from": issuer}
        )
        share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )
        utils.register_personal_info(
            from_account=user2,
            personal_info=personal_info,
            link_address=issuer
        )
        share_token.applyForTransfer(
            user2,
            100,
            "test_data",
            {"from": user1}  # from user1 to user2
        )

        # cancel transfer (from applicant)
        tx = share_token.cancelTransfer(
            0,
            "test_data",
            {"from": user1}
        )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - 100
        assert share_token.balances(user1) == 100
        assert share_token.pendingTransfer(user1) == 0
        assert share_token.applicationsForTransfer(0) == \
               (user1, user2, 100, False)
        assert tx.events["CancelTransfer"] == OrderedDict([
            ("index", 0),
            ("from", user1),
            ("to", user2),
            ("data", "test_data")
        ])

    # Normal_2
    # Issuer
    def test_normal_2(self, users, personal_info):
        issuer = users["issuer"]
        user1 = users["user1"]
        user2 = users["user2"]

        # prepare data
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=personal_info.address
        )
        share_token.transferFrom(
            issuer,
            user1,
            100,
            {"from": issuer}
        )
        share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )
        utils.register_personal_info(
            from_account=user2,
            personal_info=personal_info,
            link_address=issuer
        )
        share_token.applyForTransfer(
            user2,
            100,
            "test_data",
            {"from": user1}  # from user1 to user2
        )

        # cancel transfer (from issuer)
        tx = share_token.cancelTransfer(
            0,
            "test_data",
            {"from": issuer}
        )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - 100
        assert share_token.balances(user1) == 100
        assert share_token.pendingTransfer(user1) == 0
        assert share_token.applicationsForTransfer(0) == \
               (user1, user2, 100, False)
        assert tx.events["CancelTransfer"] == OrderedDict([
            ("index", 0),
            ("from", user1),
            ("to", user2),
            ("data", "test_data")
        ])

    ################################################################
    # Error Case
    ################################################################

    # Error_1
    # No execute permission
    def test_error_1(self, users, personal_info):
        issuer = users["issuer"]
        user1 = users["user1"]
        user2 = users["user2"]

        # prepare data
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=personal_info.address
        )
        share_token.transferFrom(
            issuer,
            user1,
            100,
            {"from": issuer}
        )
        share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )
        utils.register_personal_info(
            from_account=user2,
            personal_info=personal_info,
            link_address=issuer
        )
        share_token.applyForTransfer(
            user2,
            100,
            "test_data",
            {"from": user1}  # from user1 to user2
        )

        # cancel transfer
        share_token.cancelTransfer(
            0,
            "test_data",
            {"from": user2}
        )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - 100
        assert share_token.balances(user1) == 0
        assert share_token.pendingTransfer(user1) == 100
        assert share_token.applicationsForTransfer(0) == \
               (user1, user2, 100, True)

    # Error_2
    # Invalid application
    def test_error_2(self, users, personal_info):
        issuer = users["issuer"]
        user1 = users["user1"]
        user2 = users["user2"]

        # prepare data
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=personal_info.address
        )
        share_token.transferFrom(
            issuer,
            user1,
            100,
            {"from": issuer}
        )
        share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )
        utils.register_personal_info(
            from_account=user2,
            personal_info=personal_info,
            link_address=issuer
        )
        share_token.applyForTransfer(
            user2,
            100,
            "test_data",
            {"from": user1}  # from user1 to user2
        )

        # cancel transfer -> Success
        share_token.cancelTransfer(
            0,
            "test_data",
            {"from": user1}
        )

        # assertion (1)
        assert share_token.balances(issuer) == deploy_args[3] - 100
        assert share_token.balances(user1) == 100
        assert share_token.pendingTransfer(user1) == 0
        assert share_token.applicationsForTransfer(0) == \
               (user1, user2, 100, False)

        # cancel transfer -> Revert
        share_token.cancelTransfer(
            0,
            "test_data",
            {"from": user1}
        )

        # assertion (2)
        assert share_token.balances(issuer) == deploy_args[3] - 100
        assert share_token.balances(user1) == 100
        assert share_token.pendingTransfer(user1) == 0
        assert share_token.applicationsForTransfer(0) == \
               (user1, user2, 100, False)


# TEST_approveTransfer
class TestApproveTransfer:

    ################################################################
    # Normal Case
    ################################################################

    # Normal_1
    def test_normal_1(self, users, personal_info):
        issuer = users["issuer"]
        user1 = users["user1"]

        # prepare data
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=personal_info.address
        )
        share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )
        utils.register_personal_info(
            from_account=user1,
            personal_info=personal_info,
            link_address=issuer
        )
        share_token.applyForTransfer(
            user1,
            100,
            "test_data",
            {"from": issuer}  # from issuer to user1
        )

        # approve transfer
        tx = share_token.approveTransfer(
            0,
            "test_data",
            {"from": issuer}
        )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - 100
        assert share_token.balances(user1) == 100
        assert share_token.pendingTransfer(issuer) == 0
        assert share_token.applicationsForTransfer(0) == \
               (issuer, user1, 100, False)
        assert tx.events["ApproveTransfer"] == OrderedDict([
            ("index", 0),
            ("from", issuer),
            ("to", user1),
            ("data", "test_data")
        ])
        assert tx.events["Transfer"] == OrderedDict([
            ("from", issuer),
            ("to", user1),
            ("value", 100)
        ])

    ################################################################
    # Error Case
    ################################################################

    # Error_1
    # No execute permission
    def test_error_1(self, users, personal_info):
        issuer = users["issuer"]
        user1 = users["user1"]

        # prepare data
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=personal_info.address
        )
        share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )
        utils.register_personal_info(
            from_account=user1,
            personal_info=personal_info,
            link_address=issuer
        )
        share_token.applyForTransfer(
            user1,
            100,
            "test_data",
            {"from": issuer}  # from issuer to user1
        )

        # approve transfer
        share_token.approveTransfer(
            0,
            "test_data",
            {"from": user1}
        )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - 100
        assert share_token.balances(user1) == 0
        assert share_token.pendingTransfer(issuer) == 100
        assert share_token.applicationsForTransfer(0) == \
               (issuer, user1, 100, True)

    # Error_2
    # Invalid application
    def test_error_2(self, users, personal_info):
        issuer = users["issuer"]
        user1 = users["user1"]

        # prepare data
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=personal_info.address
        )
        share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )
        utils.register_personal_info(
            from_account=user1,
            personal_info=personal_info,
            link_address=issuer
        )
        share_token.applyForTransfer(
            user1,
            100,
            "test_data",
            {"from": issuer}  # from issuer to user1
        )

        # approve transfer (1) -> Success
        share_token.approveTransfer(
            0,
            "test_data",
            {"from": issuer}
        )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - 100
        assert share_token.balances(user1) == 100
        assert share_token.pendingTransfer(issuer) == 0
        assert share_token.applicationsForTransfer(0) == \
               (issuer, user1, 100, False)

        # approve transfer (2) -> Revert
        share_token.approveTransfer(
            0,
            "test_data",
            {"from": issuer}
        )

        # assertion
        assert share_token.balances(issuer) == deploy_args[3] - 100
        assert share_token.balances(user1) == 100
        assert share_token.pendingTransfer(issuer) == 0
        assert share_token.applicationsForTransfer(0) == \
               (issuer, user1, 100, False)


# TEST_setTransferApprovalRequired
class TestSetTransferApprovalRequired:

    ################################################################
    # Normal Case
    ################################################################

    # Normal_1
    # Default value
    def test_normal_1(self, users, personal_info):
        # prepare data
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=personal_info.address
        )

        # assertion
        assert share_token.transferApprovalRequired() == False

    # Normal_2
    def test_normal_2(self, users, personal_info):
        issuer = users["issuer"]

        # prepare data
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=personal_info.address
        )

        # set required to True
        tx = share_token.setTransferApprovalRequired(
            True,
            {"from": issuer}
        )

        # assertion
        assert share_token.transferApprovalRequired() == True
        assert tx.events["ChangeTransferApprovalRequired"] == OrderedDict([("required", True)])

    ################################################################
    # Error Case
    ################################################################

    # Error_1
    # No execute permission
    def test_error_1(self, users, personal_info):
        user1 = users["user1"]

        # prepare data
        share_token, deploy_args = utils.issue_share_token(
            users=users,
            exchange_address=zero_address,
            personal_info_address=personal_info.address
        )  # issued by issuer

        # set required to True
        share_token.setTransferApprovalRequired(
            True,
            {"from": user1}
        )

        # assertion
        assert share_token.transferApprovalRequired() == False
