import pytest
import utils
from eth_utils import to_checksum_address

zero_address = '0x0000000000000000000000000000000000000000'


def init_args(exchange_address, personal_info_address):
    name = 'test_share'
    symbol = 'IBS'
    issue_price = 10000
    total_supply = 10000
    devidends = 1000
    devidend_record_date = '20200829'
    devidend_payment_date = '20200831'
    cancellation_date = '20191231'
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'
    memo = 'some_memo'
    transferable = True

    deploy_args = [
        name, symbol, exchange_address, personal_info_address, issue_price, total_supply,
        devidends, devidend_record_date, devidend_payment_date, cancellation_date,
        contact_information, privacy_policy, memo, transferable
    ]
    return deploy_args


'''
TEST_デプロイ
'''


# 正常系1: deploy
def test_deploy_normal_1(IbetShare, users, share_exchange, personal_info):
    account_address = users['issuer']
    deploy_args = init_args(share_exchange.address, personal_info.address)

    share_contract = account_address.deploy(
        IbetShare,
        *deploy_args
    )

    owner_address = share_contract.owner()
    name = share_contract.name()
    symbol = share_contract.symbol()
    tradable_exchange = share_contract.tradableExchange()
    personal_info_address = share_contract.personalInfoAddress()
    issue_price = share_contract.issuePrice()
    total_supply = share_contract.totalSupply()
    dividend_information = share_contract.dividendInformation()
    cancellation_date = share_contract.cancellationDate()
    contact_information = share_contract.contactInformation()
    privacy_policy = share_contract.privacyPolicy()
    memo = share_contract.memo()
    transferable = share_contract.transferable()

    assert owner_address == account_address
    assert name == deploy_args[0]
    assert symbol == deploy_args[1]
    assert tradable_exchange == to_checksum_address(deploy_args[2])
    assert personal_info_address == to_checksum_address(deploy_args[3])
    assert issue_price == deploy_args[4]
    assert total_supply == deploy_args[5]
    assert dividend_information[0] == deploy_args[6]
    assert dividend_information[1] == deploy_args[7]
    assert dividend_information[2] == deploy_args[8]
    assert cancellation_date == deploy_args[9]
    assert contact_information == deploy_args[10]
    assert privacy_policy == deploy_args[11]
    assert memo == deploy_args[12]
    assert transferable == deploy_args[13]


# エラー系1: 入力値の型誤り（name）
def test_deploy_error_1(users, IbetShare, share_exchange, personal_info):
    deploy_args = init_args(share_exchange.address, personal_info.address)
    deploy_args[0] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'
    with pytest.raises(ValueError):
        users['admin'].deploy(IbetShare, *deploy_args)


# エラー系2: 入力値の型誤り（symbol）
def test_deploy_error_2(users, IbetShare, share_exchange, personal_info):
    deploy_args = init_args(share_exchange.address, personal_info.address)
    deploy_args[1] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'
    with pytest.raises(ValueError):
        users['admin'].deploy(IbetShare, *deploy_args)


# エラー系13: 入力値の型誤り（tradableExchange）
def test_deploy_error_3(users, IbetShare, share_exchange, personal_info):
    deploy_args = init_args(share_exchange.address, personal_info.address)
    deploy_args[2] = '0xaaaa'
    with pytest.raises(ValueError):
        users['admin'].deploy(IbetShare, *deploy_args)


# エラー系16: 入力値の型誤り（personalInfoAddress）
def test_deploy_error_4(users, IbetShare, share_exchange, personal_info):
    deploy_args = init_args(share_exchange.address, personal_info.address)
    deploy_args[3] = '0xaaaa'
    with pytest.raises(ValueError):
        users['admin'].deploy(IbetShare, *deploy_args)


# エラー系4: 入力値の型誤り（issuePrice）
def test_deploy_error_5(users, IbetShare, share_exchange, personal_info):
    deploy_args = init_args(share_exchange.address, personal_info.address)
    deploy_args[4] = "a10000"
    with pytest.raises(TypeError):
        users['admin'].deploy(IbetShare, *deploy_args)


# エラー系3: 入力値の型誤り（totalSupply）
def test_deploy_error_6(users, IbetShare, share_exchange, personal_info):
    deploy_args = init_args(share_exchange.address, personal_info.address)
    deploy_args[5] = "a10000"
    with pytest.raises(TypeError):
        users['admin'].deploy(IbetShare, *deploy_args)


# エラー系5: 入力値の型誤り（dividends）
def test_deploy_error_7(users, IbetShare, share_exchange, personal_info):
    deploy_args = init_args(share_exchange.address, personal_info.address)
    deploy_args[6] = "a1000"
    with pytest.raises(TypeError):
        users['admin'].deploy(IbetShare, *deploy_args)


# エラー系6: 入力値の型誤り（dividendRecordDate）
def test_deploy_error_8(users, IbetShare, share_exchange, personal_info):
    deploy_args = init_args(share_exchange.address, personal_info.address)
    deploy_args[7] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'
    with pytest.raises(ValueError):
        users['admin'].deploy(IbetShare, *deploy_args)


# エラー系6: 入力値の型誤り（dividendPaymentDate）
def test_deploy_error_9(users, IbetShare, share_exchange, personal_info):
    deploy_args = init_args(share_exchange.address, personal_info.address)
    deploy_args[8] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'
    with pytest.raises(ValueError):
        users['admin'].deploy(IbetShare, *deploy_args)


# エラー系7: 入力値の型誤り（cancellationDate）
def test_deploy_error_10(users, IbetShare, share_exchange, personal_info):
    deploy_args = init_args(share_exchange.address, personal_info.address)
    deploy_args[9] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'
    with pytest.raises(ValueError):
        users['admin'].deploy(IbetShare, *deploy_args)


# エラー系14: 入力値の型誤り（contactInformation）
def test_deploy_error_11(users, IbetShare, share_exchange, personal_info):
    deploy_args = init_args(share_exchange.address, personal_info.address)
    deploy_args[10] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'
    with pytest.raises(ValueError):
        users['admin'].deploy(IbetShare, *deploy_args)


# エラー系15: 入力値の型誤り（privacyPolicy）
def test_deploy_error_12(users, IbetShare, share_exchange, personal_info):
    deploy_args = init_args(share_exchange.address, personal_info.address)
    deploy_args[11] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'
    with pytest.raises(ValueError):
        users['admin'].deploy(IbetShare, *deploy_args)


# エラー系12: 入力値の型誤り（memo）
def test_deploy_error_13(users, IbetShare, share_exchange, personal_info):
    deploy_args = init_args(share_exchange.address, personal_info.address)
    deploy_args[12] = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'
    with pytest.raises(ValueError):
        users['admin'].deploy(IbetShare, *deploy_args)


# エラー系12: 入力値の型誤り（transferable）
def test_deploy_error_14(users, IbetShare, share_exchange, personal_info):
    deploy_args = init_args(share_exchange.address, personal_info.address)
    deploy_args[13] = "True"
    with pytest.raises(ValueError):
        users['admin'].deploy(IbetShare, *deploy_args)


'''
TEST_取引可能Exchangeの更新（setTradableExchange）
'''


# 正常系1: 発行 -> Exchangeの更新
def test_setTradableExchange_normal_1(users, share_exchange, personal_info,
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
def test_setTradableExchange_error_1(users, share_exchange, personal_info):
    issuer = users['issuer']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    # Exchangeの更新
    with pytest.raises(ValueError):
        share_token.setTradableExchange.transact('0xaaaa', {'from': issuer})


# エラー系2: 発行 -> Exchangeの更新（権限エラー）
def test_setTradableExchange_error_2(users, share_exchange, personal_info,
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


'''
TEST_個人情報記帳コントラクトの更新（setPersonalInfoAddress）
'''


# 正常系1: トークン発行 -> 更新
def test_setPersonalInfoAddress_normal_1(users, share_exchange, personal_info):
    issuer = users['issuer']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    # 更新
    share_token.setPersonalInfoAddress.transact('0x0000000000000000000000000000000000000000', {'from': issuer})

    assert share_token.personalInfoAddress() == '0x0000000000000000000000000000000000000000'


# エラー系1: トークン発行 -> 更新（入力値の型誤り）
def test_setPersonalInfoAddress_error_1(users, share_exchange, personal_info):
    issuer = users['issuer']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    # 更新
    with pytest.raises(ValueError):
        share_token.setPersonalInfoAddress.transact('0xaaaa', {'from': issuer})


# エラー系2: トークン発行 -> 更新（権限エラー）
def test_setPersonalInfoAddress_error_2(users, share_exchange, personal_info):
    attacker = users['trader']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    # 更新
    share_token.setPersonalInfoAddress.transact('0x0000000000000000000000000000000000000000', {'from': attacker})

    assert share_token.personalInfoAddress() == to_checksum_address(personal_info.address)


'''
TEST_配当情報の更新（setDividendInformation）
'''


# 正常系1: 発行（デプロイ） -> 修正
def test_setDividendInformation_normal_1(users, share_exchange, personal_info):
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
def test_setDividendInformation_error_1(users, share_exchange, personal_info):
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
def test_setDividendInformation_error_2(users, share_exchange, personal_info):
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


'''
TEST_消却日の更新（setCancellationDate）
'''


# 正常系1: 発行（デプロイ） -> 修正
def test_setCancellationDate_normal_1(users, share_exchange, personal_info):
    issuer = users['issuer']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    # 修正 -> Success
    share_token.setCancellationDate.transact('20200831', {'from': issuer})

    cancellation_date = share_token.cancellationDate()
    assert cancellation_date == '20200831'


# エラー系1: 入力値の型誤り
def test_setCancellationDate_error_1(users, share_exchange, personal_info):
    issuer = users['issuer']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    with pytest.raises(ValueError):
        share_token.setCancellationDate.transact('0x1596Ff8ED308a83897a731F3C1e814B19E11D68c', {'from': issuer})


# エラー系2: 権限エラー
def test_setCancellationDate_error_2(users, share_exchange, personal_info):
    other = users['admin']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    # Owner以外のアドレスから更新 -> Failure
    share_token.setCancellationDate.transact('20200930', {'from': other})

    cancellation_date = share_token.cancellationDate()
    assert cancellation_date == '20211231'


'''
TEST_商品画像の設定（setReferenceUrls）
'''


# 正常系1: 発行（デプロイ） -> 商品画像の設定
def test_setReferenceUrls_normal_1(users, share_exchange, personal_info):
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
def test_setReferenceUrls_normal_2(users, share_exchange, personal_info):
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
def test_setReferenceUrls_normal_3(users, share_exchange, personal_info):
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
def test_setReferenceUrls_error_1(users, share_exchange, personal_info):
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
def test_setReferenceUrls_error_2(users, share_exchange, personal_info):
    issuer = users['issuer']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    reference_url = '0x1596Ff8ED308a83897a731F3C1e814B19E11D68c'

    with pytest.raises(ValueError):
        share_token.setReferenceUrls.transact(0, reference_url, {'from': issuer})


# エラー系3: Issuer以外のアドレスからリファレンス設定を実施した場合
def test_setReferenceUrls_error_3(users, share_exchange, personal_info):
    other = users['admin']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    reference_url = 'https://some_reference_url.com/image.png'

    # Owner以外のアドレスからリファレンス設定を実施 -> Failure
    share_token.setReferenceUrls.transact(0, reference_url, {'from': other})

    reference_url = share_token.referenceUrls(0)
    assert reference_url == ''


'''
TEST_問い合わせ先情報の更新（setContactInformation）
'''


# 正常系1: 発行（デプロイ） -> 修正
def test_setContactInformation_normal_1(users, share_exchange, personal_info):
    issuer = users['issuer']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    # 修正 -> Success
    share_token.setContactInformation.transact('updated contact information', {'from': issuer})

    contact_information = share_token.contactInformation()
    assert contact_information == 'updated contact information'


# エラー系1: 入力値の型誤り
def test_setContactInformation_error_1(users, share_exchange, personal_info):
    issuer = users['issuer']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    with pytest.raises(ValueError):
        share_token.setContactInformation.transact('0x1596Ff8ED308a83897a731F3C1e814B19E11D68c', {'from': issuer})


# エラー系2: 権限エラー
def test_setContactInformation_error_2(users, share_exchange, personal_info):
    other = users['admin']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    # Owner以外のアドレスから更新 -> Failure
    share_token.setContactInformation.transact('updated contact information', {'from': other})

    contact_information = share_token.contactInformation()
    assert contact_information == 'some_contact_information'


'''
TEST_プライバシーポリシーの更新（setPrivacyPolicy）
'''


# 正常系1: 発行（デプロイ） -> 修正
def test_setPrivacyPolicy_normal_1(users, share_exchange, personal_info):
    issuer = users['issuer']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    # 修正 -> Success
    share_token.setPrivacyPolicy.transact('updated privacy policy', {'from': issuer})

    privacy_policy = share_token.privacyPolicy()
    assert privacy_policy == 'updated privacy policy'


# エラー系1: 入力値の型誤り
def test_setPrivacyPolicy_error_1(users, share_exchange, personal_info):
    issuer = users['issuer']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    with pytest.raises(ValueError):
        share_token.setPrivacyPolicy.transact('0x1596Ff8ED308a83897a731F3C1e814B19E11D68c', {'from': issuer})


# エラー系2: 権限エラー
def test_setPrivacyPolicy_error_2(users, share_exchange, personal_info):
    other = users['admin']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    # Owner以外のアドレスから更新 -> Failure
    share_token.setPrivacyPolicy.transact('updated privacy policy', {'from': other})

    privacy_policy = share_token.privacyPolicy()
    assert privacy_policy == 'some_privacy_policy'


'''
TEST_メモの更新（setMemo）
'''


# 正常系1: 発行（デプロイ） -> メモ欄の修正
def test_setMemo_normal_1(users, share_exchange, personal_info):
    issuer = users['issuer']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    # メモ欄の修正 -> Success
    share_token.setMemo.transact('updated memo', {'from': issuer})

    memo = share_token.memo()
    assert memo == 'updated memo'


# エラー系1: 入力値の型誤り
def test_setMemo_error_1(users, share_exchange, personal_info):
    issuer = users['issuer']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    with pytest.raises(ValueError):
        share_token.setMemo.transact('0x1596Ff8ED308a83897a731F3C1e814B19E11D68c', {'from': issuer})


# エラー系2: Owner以外のアドレスからメモ欄の修正を実施した場合
def test_setMemo_error_2(users, share_exchange, personal_info):
    other = users['admin']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    # Owner以外のアドレスからメモ欄の修正を実施 -> Failure
    share_token.setMemo.transact('updated memo', {'from': other})

    memo = share_token.memo()
    assert memo == 'some_memo'


'''
TEST_譲渡可能更新（setTransferable）
'''


# 正常系1: 発行 -> 譲渡可能更新
def test_setTransferable_normal_1(users, share_exchange, personal_info):
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
def test_setTransferable_error_1(users, share_exchange, personal_info):
    issuer = users['issuer']

    # 新規発行
    share_contract, deploy_args = \
        utils.issue_share_token(users, share_exchange.address, personal_info.address)

    # 型誤り
    with pytest.raises(ValueError):
        share_contract.setTransferable.transact('False', {'from': issuer})


# エラー系2: 権限エラー
def test_setTransferable_error_2(users, share_exchange, personal_info):
    attacker = users['trader']
    after_transferable = False

    # 新規発行
    share_contract, deploy_args = \
        utils.issue_share_token(users, share_exchange.address, personal_info.address)

    # 譲渡可能更新
    share_contract.setTransferable.transact(after_transferable, {'from': attacker})  # エラーになる

    transferable = share_contract.transferable()
    assert transferable == True


'''
TEST_募集ステータス更新（setOfferingStatus）
'''


# 正常系1: 発行 -> 新規募集ステータス更新（False→True）
def test_setOfferingStatus_normal_1(users, share_exchange, personal_info):
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
def test_setOfferingStatus_normal_2(users, share_exchange, personal_info):
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
def test_setOfferingStatus_error_1(users, share_exchange, personal_info):
    issuer = users['issuer']

    # トークン新規発行
    share_token, deploy_args = \
        utils.issue_share_token(users, share_exchange.address, personal_info.address)

    # 新規募集ステータスの更新（エラー）：文字型
    with pytest.raises(ValueError):
        share_token.setOfferingStatus.transact('True', {'from': issuer})


'''
TEST_残高確認（balanceOf）
'''


# 正常系1: 商品コントラクト作成 -> 残高確認
def test_balanceOf_normal_1(users, share_exchange, personal_info):
    issuer = users['issuer']

    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    balance = share_token.balanceOf(issuer)
    assert balance == 10000


# エラー系1: 入力値の型誤り（Owner）
def test_balanceOf_error_1(users, share_exchange, personal_info):
    # 株式トークン新規発行
    share_token, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    account_address = 1234

    with pytest.raises(ValueError):
        share_token.balanceOf(account_address)


'''
TEST_アドレス認可（authorize）
'''


# 正常系1: 商品コントラクト作成 -> アドレス認可 -> 認可情報変更
def test_authorize_normal_1(users, share_exchange, personal_info):
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
def test_authorize_error_1(users, share_exchange, personal_info):
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


'''
TEST_ロック（lock）、ロック数量参照（lockedOf）
'''


# 正常系1: 認可済みアドレスに対するロック（商品コントラクト作成 -> 移管 -> 認可 -> ロック）
def test_lock_normal_1(users, share_exchange, personal_info):
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
def test_lock_normal_2(users, share_exchange, personal_info):
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
def test_lock_error_1(users, share_exchange, personal_info):
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
def test_lock_error_2(users, share_exchange, personal_info):
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
def test_lock_error_3(users, share_exchange, personal_info):
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
def test_lock_error_4(users, share_exchange, personal_info):
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


'''
TEST_ロック数量参照（lockedOf）
'''


# 異常系1: 型エラー
def test_lockedOf_error_1(users, share_exchange, personal_info):
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


'''
TEST_アンロック（unlock）
'''


# 正常系1: 認可済みアドレスによるアンロック（商品コントラクト作成 -> 移管 -> 認可 -> ロック -> アンロック）
def test_unlock_normal_1(users, share_exchange, personal_info):
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
def test_unlock_normal_2(users, share_exchange, personal_info):
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
    assert issuer_amount == deploy_args[5] - transfer_amount + unlock_amount
    assert trader_locked_amount == lock_amount - unlock_amount - unlock_amount


# 異常系1: 入力値の型誤り
def test_unlock_error_1(users, share_exchange, personal_info):
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
def test_unlock_error_2(users, share_exchange, personal_info):
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
def test_unlock_error_3(users, share_exchange, personal_info):
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
def test_unlock_error_4(users, share_exchange, personal_info):
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


'''
TEST_トークンの振替（transfer）
'''


# 正常系1: アカウントアドレスへの振替
def test_transfer_normal_1(users, share_exchange, personal_info):
    from_address = users['issuer']
    to_address = users['trader']
    transfer_amount = 100

    # 株式トークン新規発行
    share_contract, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    # 振替先の個人情報登録
    utils.register_personal_info(to_address, personal_info, from_address)

    # 振替
    share_contract.transfer.transact(to_address, transfer_amount, {'from': from_address})

    from_balance = share_contract.balanceOf(from_address)
    to_balance = share_contract.balanceOf(to_address)

    assert from_balance == deploy_args[5] - transfer_amount
    assert to_balance == transfer_amount


# 正常系2: 株式取引コントラクトへの振替
def test_transfer_normal_2(users, share_exchange, personal_info):
    from_address = users['issuer']
    transfer_amount = 100

    # 株式トークン新規発行
    share_contract, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    to_address = share_exchange.address
    share_contract.transfer.transact(to_address, transfer_amount, {'from': from_address})

    from_balance = share_contract.balanceOf(from_address)
    to_balance = share_contract.balanceOf(to_address)

    assert from_balance == deploy_args[5] - transfer_amount
    assert to_balance == transfer_amount


# エラー系1: 入力値の型誤り（To）
def test_transfer_error_1(users, share_exchange, personal_info):
    from_address = users['issuer']
    to_address = 1234
    transfer_amount = 100

    # 株式トークン新規発行
    share_contract, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    with pytest.raises(ValueError):
        share_contract.transfer.transact(to_address, transfer_amount, {'from': from_address})


# エラー系2: 入力値の型誤り（Value）
def test_transfer_error_2(users, share_exchange, personal_info):
    from_address = users['issuer']
    to_address = users['trader']
    transfer_amount = 'M'

    # 株式トークン新規発行
    share_contract, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    with pytest.raises(TypeError):
        share_contract.transfer.transact(to_address, transfer_amount, {'from': from_address})


# エラー系3: 残高不足
def test_transfer_error_3(users, share_exchange, personal_info):
    issuer = users['issuer']
    from_address = issuer
    to_address = users['trader']

    # 株式トークン新規発行
    share_contract, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    # 個人情報登録
    utils.register_personal_info(from_address, personal_info, from_address)

    # 株式トークン振替（残高超）
    transfer_amount = 10000000000
    share_contract.transfer.transact(to_address, transfer_amount, {'from': issuer})  # エラーになる

    assert share_contract.balanceOf(issuer) == 10000
    assert share_contract.balanceOf(to_address) == 0


# エラー系4: private functionにアクセスできない
def test_transfer_error_4(users, share_exchange, personal_info):
    issuer = users['issuer']
    from_address = issuer
    to_address = users['trader']

    transfer_amount = 100
    data = 0

    # 株式トークン新規発行
    share_contract, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    with pytest.raises(AttributeError):
        share_contract.isContract(to_address)

    with pytest.raises(AttributeError):
        share_contract.transferToAddress.transact(to_address, transfer_amount, data, {'from': from_address})

    with pytest.raises(AttributeError):
        share_contract.transferToContract.transact(to_address, transfer_amount, data, {'from': from_address})


# エラー系5: 取引不可Exchangeへの振替
def test_transfer_error_5(users, share_exchange, personal_info,
                          coupon_exchange_storage, payment_gateway,
                          IbetCouponExchange):
    from_address = users['issuer']
    transfer_amount = 100

    # 株式トークン新規発行
    share_contract, deploy_args = utils. \
        issue_share_token(users, share_exchange.address, personal_info.address)

    # 取引不可Exchange
    dummy_exchange = users['admin'].deploy(
        IbetCouponExchange,  # IbetShareExchange以外を読み込む必要がある
        payment_gateway.address,
        coupon_exchange_storage.address
    )

    to_address = dummy_exchange.address
    share_contract.transfer.transact(to_address, transfer_amount, {'from': users['admin']})  # エラーになる

    from_balance = share_contract.balanceOf(from_address)
    to_balance = share_contract.balanceOf(to_address)

    assert from_balance == deploy_args[5]
    assert to_balance == 0


# エラー系6: 譲渡不可トークンの振替
def test_transfer_error_6(users, share_exchange, personal_info):
    issuer = users['issuer']
    to_address = users['trader']
    transfer_amount = 100

    # 株式トークン新規発行
    share_contract, deploy_args = \
        utils.issue_share_token(users, share_exchange.address, personal_info.address)

    # 個人情報登録
    utils.register_personal_info(to_address, personal_info, issuer)

    # 譲渡不可設定
    share_contract.setTransferable.transact(False, {'from': issuer})

    # 譲渡実行
    share_contract.transfer.transact(to_address, transfer_amount, {'from': issuer})  # エラーとなる

    from_balance = share_contract.balanceOf(issuer)
    to_balance = share_contract.balanceOf(to_address)

    assert from_balance == deploy_args[5]
    assert to_balance == 0


# エラー系7: 個人情報未登録アドレスへの振替
def test_transfer_error_7(users, share_exchange, personal_info):
    issuer = users['issuer']
    to_address = users['trader']
    transfer_amount = 100

    # 株式トークン新規発行
    share_contract, deploy_args = \
        utils.issue_share_token(users, share_exchange.address, personal_info.address)

    # NOTE:個人情報未登録（to_address）

    # 譲渡実行
    share_contract.transfer.transact(to_address, transfer_amount, {'from': issuer})  # エラーとなる

    from_balance = share_contract.balanceOf(issuer)
    to_balance = share_contract.balanceOf(to_address)

    assert from_balance == deploy_args[5]
    assert to_balance == 0


'''
TEST_トークンの移転（transferFrom）
'''


# 正常系1: アカウントアドレスへの移転
def test_transferFrom_normal_1(users, share_exchange, personal_info):
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

    assert issuer_balance == deploy_args[5] - _value
    assert from_balance == 0
    assert to_balance == _value


# エラー系1: 入力値の型誤り（From）
def test_transferFrom_error_1(users, share_exchange, personal_info):
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
def test_transferFrom_error_2(users, share_exchange, personal_info):
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
def test_transferFrom_error_3(users, share_exchange, personal_info):
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
def test_transferFrom_error_4(users, share_exchange, personal_info):
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

    assert issuer_balance == deploy_args[5] - _value
    assert from_balance == _value
    assert to_balance == 0


# エラー系5: 権限エラー
def test_transferFrom_error_5(users, share_exchange, personal_info):
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

    assert issuer_balance == deploy_args[5] - _value
    assert from_balance == _value
    assert to_balance == 0


'''
TEST_募集申込（applyForOffering）
'''


# 正常系1
#   発行：発行体 -> （申込なし）初期データ参照
def test_applyForOffering_normal_1(users):
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
def test_applyForOffering_normal_2(users, personal_info):
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
def test_applyForOffering_normal_3(users, personal_info):
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
def test_applyForOffering_error_1(users):
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
def test_applyForOffering_error_2(users):
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
def test_applyForOffering_error_3(users, personal_info):
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


'''
TEST_募集割当（allot）
'''


# 正常系1
#   発行：発行体 -> 投資家：募集申込 -> 発行体：募集割当
def test_allot_normal_1(users, personal_info):
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
def test_allot_error_1(users):
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
def test_allot_error_2(users):
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


'''
TEST_増資（issueFrom）
'''


# 正常系1: 発行 -> 増資（発行体自身のアドレスに増資）
def test_issueFrom_normal_1(users):
    issuer = users['issuer']
    value = 10

    # トークン新規発行
    share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

    # 増資
    share_token.issueFrom.transact(issuer, zero_address, value, {'from': issuer})

    total_supply = share_token.totalSupply()
    balance = share_token.balanceOf(issuer)

    assert total_supply == deploy_args[5] + value
    assert balance == deploy_args[5] + value


# 正常系2: 発行 -> 増資（投資家想定のEOAアドレスのアドレスを増資）
def test_issueFrom_normal_2(users):
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

    assert total_supply == deploy_args[5] + value
    assert balance_issuer == deploy_args[5]
    assert balance_trader == value


# 正常系3: 発行 -> 譲渡 -> ロック -> ロック済み数量の増資（from issuer）
def test_issueFrom_normal_3(users, share_exchange):
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
def test_issueFrom_error_1(users):
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
def test_issueFrom_error_2(users):
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
def test_issueFrom_error_3(users):
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
def test_issueFrom_error_4(users):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

    issue_amount = 2 ** 256 - deploy_args[5]

    # 増資（限界値超）
    share_token.issueFrom.transact(issuer, zero_address, issue_amount, {'from': issuer})  # エラーになる

    share_token.issueFrom.transact(issuer, trader, issue_amount, {'from': issuer})  # エラーになる

    total_supply = share_token.totalSupply()
    balance = share_token.balanceOf(issuer)

    assert total_supply == deploy_args[5]
    assert balance == deploy_args[5]


# エラー系5: 権限エラー
def test_issueFrom_error_5(users):
    issuer = users['issuer']
    attacker = users['trader']

    # トークン新規発行
    share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

    # 増資：権限エラー
    share_token.issueFrom.transact(attacker, zero_address, 1, {'from': attacker})  # エラーになる

    total_supply = share_token.totalSupply()
    balance = share_token.balanceOf(issuer)

    assert total_supply == deploy_args[5]
    assert balance == deploy_args[5]


'''
TEST_減資（redeemFrom）
'''


# 正常系1: 発行 -> 減資（発行体自身のアドレスの保有を減資）
def test_redeemFrom_normal_1(users):
    issuer = users['issuer']
    value = 10

    # トークン新規発行
    share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

    # 減資
    share_token.redeemFrom.transact(issuer, zero_address, value, {'from': issuer})

    total_supply = share_token.totalSupply()
    balance = share_token.balanceOf(issuer)

    assert total_supply == deploy_args[5] - value
    assert balance == deploy_args[5] - value


# 正常系2: 発行 -> 減資（投資家想定のEOAアドレスの保有を減資）
def test_redeemFrom_normal_2(users):
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

    assert total_supply == deploy_args[5] - value
    assert balance_issuer == deploy_args[5] - transfer_amount
    assert balance_trader == transfer_amount - value


# 正常系3: 発行 -> ロック -> 減資（投資家想定のEOAアドレスのロック数量を減資）
def test_redeemFrom_normal_3(users):
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

    assert total_supply == deploy_args[5] - value
    assert balance_issuer == deploy_args[5] - transfer_amount
    assert balance_trader == transfer_amount - lock_amount
    assert balance_trader_lock == lock_amount - value


# エラー系1: 入力値の型誤り
def test_redeemFrom_error_1(users):
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
def test_redeemFrom_error_2(users):
    issuer = users['issuer']

    # トークン新規発行
    share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

    # 下限値超
    with pytest.raises(OverflowError):
        share_token.redeemFrom.transact(issuer, zero_address, -1, {'from': issuer})


# エラー系3: 発行→減資→発行数量より下限を超過
def test_redeemFrom_error_3(users):
    issuer = users['issuer']

    # トークン新規発行
    share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

    redeem_amount = deploy_args[5] + 1

    # 減資（限界値超）
    share_token.redeemFrom.transact(issuer, zero_address, redeem_amount, {'from': issuer})  # エラーになる

    total_supply = share_token.totalSupply()
    balance = share_token.balanceOf(issuer)

    assert total_supply == deploy_args[5]
    assert balance == deploy_args[5]


# エラー系4: 発行→ロック→減資→ロック数量より下限を超過
def test_redeemFrom_error_4(users):
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

    assert total_supply == deploy_args[5]
    assert issuer_balance == deploy_args[5] - transfer_amount
    assert trader_balance == transfer_amount - lock_amount
    assert trader_locked == lock_amount


# エラー系5: 権限エラー
def test_redeemFrom_error_5(users):
    issuer = users['issuer']
    attacker = users['trader']

    # トークン新規発行
    share_token, deploy_args = utils.issue_share_token(users, zero_address, zero_address)

    # 減資：権限エラー
    share_token.redeemFrom.transact(attacker, zero_address, 1, {'from': attacker})  # エラーになる

    total_supply = share_token.totalSupply()
    balance = share_token.balanceOf(issuer)

    assert total_supply == deploy_args[5]
    assert balance == deploy_args[5]
