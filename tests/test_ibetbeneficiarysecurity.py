import pytest
import utils
from eth_utils import to_checksum_address

zero_address = '0x0000000000000000000000000000000000000000'

def init_args(exchange_address, personal_info_address):
    name = 'test_bs'
    symbol = 'IBS'
    issue_price = 10000
    total_supply = 10000
    devidends = 1000
    devidend_record_date = '20200829'
    devidend_payment_date = '20200831'
    cansellation_date = '20191231'
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'
    memo = 'some_memo'
    transferable = True

    deploy_args = [
        name, symbol, exchange_address, personal_info_address, issue_price, total_supply,
        devidends, devidend_record_date, devidend_payment_date, cansellation_date,
        contact_information, privacy_policy, memo, transferable
    ]
    return deploy_args


'''
TEST_デプロイ
'''


# 正常系1: deploy
def test_deploy_normal_1(web3, chain, users, bs_exchange, personal_info):
    account_address = users['issuer']
    deploy_args = init_args(bs_exchange.address, personal_info.address)

    web3.eth.defaultAccount = account_address
    beneficiary_security_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetBeneficiarySecurity',
        deploy_args=deploy_args
    )

    owner_address = beneficiary_security_contract.call().owner()
    name = beneficiary_security_contract.call().name()
    symbol = beneficiary_security_contract.call().symbol()
    tradable_exchange = beneficiary_security_contract.call().tradableExchange()
    personal_info_address = beneficiary_security_contract.call().personalInfoAddress()
    issue_price = beneficiary_security_contract.call().issuePrice()
    total_supply = beneficiary_security_contract.call().totalSupply()
    dividend_infomation = beneficiary_security_contract.call().dividendInfomation()
    cansellation_date = beneficiary_security_contract.call().cansellationDate()
    contact_information = beneficiary_security_contract.call().contactInformation()
    privacy_policy = beneficiary_security_contract.call().privacyPolicy()
    memo = beneficiary_security_contract.call().memo()
    transferable = beneficiary_security_contract.call().transferable()

    assert owner_address == account_address
    assert name == deploy_args[0]
    assert symbol == deploy_args[1]
    assert tradable_exchange == to_checksum_address(deploy_args[2])
    assert personal_info_address == to_checksum_address(deploy_args[3])
    assert issue_price == deploy_args[4]
    assert total_supply == deploy_args[5]
    assert dividend_infomation[0] == deploy_args[6]
    assert dividend_infomation[1] == deploy_args[7]
    assert dividend_infomation[2] == deploy_args[8]
    assert cansellation_date == deploy_args[9]
    assert contact_information == deploy_args[10]
    assert privacy_policy == deploy_args[11]
    assert memo == deploy_args[12]
    assert transferable == deploy_args[13]


# エラー系1: 入力値の型誤り（name）
def test_deploy_error_1(chain, bs_exchange, personal_info):
    deploy_args = init_args(bs_exchange.address, personal_info.address)
    deploy_args[0] = 1234
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetBeneficiarySecurity', deploy_args=deploy_args)


# エラー系2: 入力値の型誤り（symbol）
def test_deploy_error_2(chain, bs_exchange, personal_info):
    deploy_args = init_args(bs_exchange.address, personal_info.address)
    deploy_args[1] = 1234
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetBeneficiarySecurity', deploy_args=deploy_args)


# エラー系13: 入力値の型誤り（tradableExchange）
def test_deploy_error_3(chain, bs_exchange, personal_info):
    deploy_args = init_args(bs_exchange.address, personal_info.address)
    deploy_args[5] = '0xaaaa'
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetBeneficiarySecurity', deploy_args=deploy_args)


# エラー系16: 入力値の型誤り（personalInfoAddress）
def test_deploy_error_4(chain, bs_exchange, personal_info):
    deploy_args = init_args(bs_exchange.address, personal_info.address)
    deploy_args[3] = '0xaaaa'
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetBeneficiarySecurity', deploy_args=deploy_args)


# エラー系4: 入力値の型誤り（issuePrice）
def test_deploy_error_5(chain, bs_exchange, personal_info):
    deploy_args = init_args(bs_exchange.address, personal_info.address)
    deploy_args[4] = "10000"
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetBeneficiarySecurity', deploy_args=deploy_args)


# エラー系3: 入力値の型誤り（totalSupply）
def test_deploy_error_6(chain, bs_exchange, personal_info):
    deploy_args = init_args(bs_exchange.address, personal_info.address)
    deploy_args[5] = "10000"
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetBeneficiarySecurity', deploy_args=deploy_args)


# エラー系5: 入力値の型誤り（dividends）
def test_deploy_error_7(chain, bs_exchange, personal_info):
    deploy_args = init_args(bs_exchange.address, personal_info.address)
    deploy_args[6] = "1000"
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetBeneficiarySecurity', deploy_args=deploy_args)


# エラー系6: 入力値の型誤り（dividendRecordDate）
def test_deploy_error_8(chain, bs_exchange, personal_info):
    deploy_args = init_args(bs_exchange.address, personal_info.address)
    deploy_args[7] = 1231
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetBeneficiarySecurity', deploy_args=deploy_args)


# エラー系6: 入力値の型誤り（dividendPaymentDate）
def test_deploy_error_9(chain, bs_exchange, personal_info):
    deploy_args = init_args(bs_exchange.address, personal_info.address)
    deploy_args[8] = 1231
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetBeneficiarySecurity', deploy_args=deploy_args)


# エラー系7: 入力値の型誤り（cansellationDate）
def test_deploy_error_10(chain, bs_exchange, personal_info):
    deploy_args = init_args(bs_exchange.address, personal_info.address)
    deploy_args[9] = 20191231
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetBeneficiarySecurity', deploy_args=deploy_args)


# エラー系14: 入力値の型誤り（contactInformation）
def test_deploy_error_11(chain, bs_exchange, personal_info):
    deploy_args = init_args(bs_exchange.address, personal_info.address)
    deploy_args[10] = 1234
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetBeneficiarySecurity', deploy_args=deploy_args)


# エラー系15: 入力値の型誤り（privacyPolicy）
def test_deploy_error_12(chain, bs_exchange, personal_info):
    deploy_args = init_args(bs_exchange.address, personal_info.address)
    deploy_args[11] = 1234
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetBeneficiarySecurity', deploy_args=deploy_args)


# エラー系12: 入力値の型誤り（memo）
def test_deploy_error_13(chain, bs_exchange, personal_info):
    deploy_args = init_args(bs_exchange.address, personal_info.address)
    deploy_args[12] = 1234
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetBeneficiarySecurity', deploy_args=deploy_args)


# エラー系12: 入力値の型誤り（transferable）
def test_deploy_error_14(chain, bs_exchange, personal_info):
    deploy_args = init_args(bs_exchange.address, personal_info.address)
    deploy_args[13] = "True"
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetBeneficiarySecurity', deploy_args=deploy_args)


'''
TEST_取引可能Exchangeの更新（setTradableExchange）
'''


# 正常系1: 発行 -> Exchangeの更新
def test_setTradableExchange_normal_1(web3, chain, users, bs_exchange, personal_info,
                                      coupon_exchange_storage, payment_gateway):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # その他Exchange
    web3.eth.defaultAccount = users['admin']
    other_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetCouponExchange',  # IbetBeneficiarySecurityExchange以外を読み込む必要がある
        deploy_args=[
            payment_gateway.address,
            coupon_exchange_storage.address
        ]
    )

    # Exchangeの更新
    web3.eth.defaultAccount = issuer
    txn_hash = bs_token.transact().setTradableExchange(other_exchange.address)
    chain.wait.for_receipt(txn_hash)

    assert bs_token.call().tradableExchange() == to_checksum_address(other_exchange.address)


# エラー系1: 発行 -> Exchangeの更新（入力値の型誤り）
def test_setTradableExchange_error_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # Exchangeの更新
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        bs_token.transact().setTradableExchange('0xaaaa')


# エラー系2: 発行 -> Exchangeの更新（権限エラー）
def test_setTradableExchange_error_2(web3, chain, users, bs_exchange, personal_info,
                                     coupon_exchange_storage, payment_gateway):
    issuer = users['issuer']
    trader = users['trader']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # その他Exchange
    web3.eth.defaultAccount = users['admin']
    other_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetCouponExchange',  # IbetBeneficiarySecurityExchange以外を読み込む必要がある
        deploy_args=[
            payment_gateway.address,
            coupon_exchange_storage.address
        ]
    )

    # Exchangeの更新
    web3.eth.defaultAccount = trader
    try:
        txn_hash = bs_token.transact().setTradableExchange(other_exchange.address)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    assert bs_token.call().tradableExchange() == to_checksum_address(bs_exchange.address)


'''
TEST_個人情報記帳コントラクトの更新（setPersonalInfoAddress）
'''


# 正常系1: トークン発行 -> 更新
def test_setPersonalInfoAddress_normal_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 更新
    web3.eth.defaultAccount = issuer
    txn_hash = bs_token.transact().setPersonalInfoAddress('0x0000000000000000000000000000000000000000')
    chain.wait.for_receipt(txn_hash)

    assert bs_token.call().personalInfoAddress() == '0x0000000000000000000000000000000000000000'


# エラー系1: トークン発行 -> 更新（入力値の型誤り）
def test_setPersonalInfoAddress_error_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 更新
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        bs_token.transact().setPersonalInfoAddress('0xaaaa')


# エラー系2: トークン発行 -> 更新（権限エラー）
def test_setPersonalInfoAddress_error_2(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']
    attacker = users['trader']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 更新
    web3.eth.defaultAccount = attacker
    try:
        txn_hash = bs_token.transact().setPersonalInfoAddress('0x0000000000000000000000000000000000000000')
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    assert bs_token.call().personalInfoAddress() == to_checksum_address(personal_info.address)


'''
TEST_配当情報の更新（setDividendInfomation）
'''


# 正常系1: 発行（デプロイ） -> 修正
def test_setDividendInfomation_normal_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 修正 -> Success
    web3.eth.defaultAccount = issuer
    txn_hash = bs_token.transact().setDividendInfomation(22000, '20200829', '20200831')
    chain.wait.for_receipt(txn_hash)

    dividend_infomation = bs_token.call().dividendInfomation()
    assert dividend_infomation[0] == 22000
    assert dividend_infomation[1] == '20200829'
    assert dividend_infomation[2] == '20200831'


# エラー系1: 入力値の型誤り
def test_setDividendInfomation_error_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        bs_token.transact().setDividendInfomation("1234", '20200829', '20200831')
    with pytest.raises(TypeError):
        bs_token.transact().setDividendInfomation(1234, 20200829, '20200831')
    with pytest.raises(TypeError):
        bs_token.transact().setDividendInfomation(1234, '20200829', 20200831)


# エラー系2: 権限エラー
def test_setDividendInfomation_error_2(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']
    other = users['admin']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # Owner以外のアドレスから更新 -> Failure
    web3.eth.defaultAccount = other
    try:
        chain.wait.for_receipt(bs_token.transact().setDividendInfomation(33000, '20200830', '20200901'))
    except ValueError:
        pass

    dividend_infomation = bs_token.call().dividendInfomation()
    assert dividend_infomation[0] == 1000
    assert dividend_infomation[1] == '20200830'
    assert dividend_infomation[2] == '20200831'

'''
TEST_消却日の更新（setCansellationDate）
'''


# 正常系1: 発行（デプロイ） -> 修正
def test_setCansellationDate_normal_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 修正 -> Success
    web3.eth.defaultAccount = issuer
    txn_hash = bs_token.transact().setCansellationDate('20200831')
    chain.wait.for_receipt(txn_hash)

    cansellation_date = bs_token.call().cansellationDate()
    assert cansellation_date == '20200831'


# エラー系1: 入力値の型誤り
def test_setCansellationDate_error_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        bs_token.transact().setCansellationDate(1234)


# エラー系2: 権限エラー
def test_setCansellationDate_error_2(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']
    other = users['admin']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # Owner以外のアドレスから更新 -> Failure
    web3.eth.defaultAccount = other
    try:
        chain.wait.for_receipt(bs_token.transact().setCansellationDate('20200930'))
    except ValueError:
        pass

    cansellation_date = bs_token.call().cansellationDate()
    assert cansellation_date == '20211231'


'''
TEST_商品画像の設定（setReferenceUrls）
'''


# 正常系1: 発行（デプロイ） -> 商品画像の設定
def test_setReferenceUrls_normal_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    reference_url = 'https://some_reference_url.com/image.png'

    # 商品画像の設定 -> Success
    web3.eth.defaultAccount = issuer
    txn_hash = bs_token.transact().setReferenceUrls(0, reference_url)
    chain.wait.for_receipt(txn_hash)

    reference_urls = bs_token.call().referenceUrls(0)
    assert reference_urls == 'https://some_reference_url.com/image.png'


# 正常系2: 発行（デプロイ） -> 商品画像の設定（複数設定）
def test_setReferenceUrls_normal_2(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    reference_url = 'https://some_reference_url.com/image.png'

    # 商品画像の設定（1つ目） -> Success
    web3.eth.defaultAccount = issuer
    txn_hash_1 = bs_token.transact().setReferenceUrls(0, reference_url)
    chain.wait.for_receipt(txn_hash_1)

    # 商品画像の設定（2つ目） -> Success
    web3.eth.defaultAccount = issuer
    txn_hash_2 = bs_token.transact().setReferenceUrls(1, reference_url)
    chain.wait.for_receipt(txn_hash_2)

    reference_url_0 = bs_token.call().referenceUrls(0)
    reference_url_1 = bs_token.call().referenceUrls(1)
    assert reference_url_0 == 'https://some_reference_url.com/image.png'
    assert reference_url_1 == 'https://some_reference_url.com/image.png'


# 正常系3: 発行（デプロイ） -> 商品画像の設定（上書き登録）
def test_setReferenceUrls_normal_3(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    reference_url = 'https://some_reference_url.com/image.png'
    reference_url_after = 'https://some_reference_url.com/image_after.png'

    # 商品画像の設定（1回目） -> Success
    web3.eth.defaultAccount = issuer
    txn_hash_1 = bs_token.transact().setReferenceUrls(0, reference_url)
    chain.wait.for_receipt(txn_hash_1)

    # 商品画像の設定（2回目：上書き） -> Success
    web3.eth.defaultAccount = issuer
    txn_hash_2 = bs_token.transact().setReferenceUrls(0, reference_url_after)
    chain.wait.for_receipt(txn_hash_2)

    reference_url = bs_token.call().referenceUrls(0)
    assert reference_url == 'https://some_reference_url.com/image_after.png'


# エラー系1: 入力値の型誤り（Class）
def test_setReferenceUrls_error_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    reference_url = 'https://some_reference_url.com/image.png'

    web3.eth.defaultAccount = issuer

    with pytest.raises(TypeError):
        bs_token.transact().setReferenceUrls(-1, reference_url)

    with pytest.raises(TypeError):
        bs_token.transact().setReferenceUrls(256, reference_url)

    with pytest.raises(TypeError):
        bs_token.transact().setReferenceUrls('0', reference_url)


# エラー系2: 入力値の型誤り（referenceUrl）
def test_setReferenceUrls_error_2(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    reference_url = 1234

    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        bs_token.transact().setReferenceUrls(0, reference_url)


# エラー系3: Issuer以外のアドレスからリファレンス設定を実施した場合
def test_setReferenceUrls_error_3(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']
    other = users['admin']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    reference_url = 'https://some_reference_url.com/image.png'

    # Owner以外のアドレスからリファレンス設定を実施 -> Failure
    web3.eth.defaultAccount = other
    try:
        txn_hash = bs_token.transact().setReferenceUrls(0, reference_url)
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    reference_url = bs_token.call().referenceUrls(0)
    assert reference_url == ''


'''
TEST_問い合わせ先情報の更新（setContactInformation）
'''


# 正常系1: 発行（デプロイ） -> 修正
def test_setContactInformation_normal_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 修正 -> Success
    web3.eth.defaultAccount = issuer
    txn_hash = bs_token.transact().setContactInformation('updated contact information')
    chain.wait.for_receipt(txn_hash)

    contact_information = bs_token.call().contactInformation()
    assert contact_information == 'updated contact information'


# エラー系1: 入力値の型誤り
def test_setContactInformation_error_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        bs_token.transact().setContactInformation(1234)


# エラー系2: 権限エラー
def test_setContactInformation_error_2(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']
    other = users['admin']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # Owner以外のアドレスから更新 -> Failure
    web3.eth.defaultAccount = other
    try:
        chain.wait.for_receipt(bs_token.transact().setContactInformation('updated contact information'))
    except ValueError:
        pass

    contact_information = bs_token.call().contactInformation()
    assert contact_information == 'some_contact_information'


'''
TEST_プライバシーポリシーの更新（setPrivacyPolicy）
'''


# 正常系1: 発行（デプロイ） -> 修正
def test_setPrivacyPolicy_normal_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 修正 -> Success
    web3.eth.defaultAccount = issuer
    txn_hash = bs_token.transact().setPrivacyPolicy('updated privacy policy')
    chain.wait.for_receipt(txn_hash)

    privacy_policy = bs_token.call().privacyPolicy()
    assert privacy_policy == 'updated privacy policy'


# エラー系1: 入力値の型誤り
def test_setPrivacyPolicy_error_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        bs_token.transact().setPrivacyPolicy(1234)


# エラー系2: 権限エラー
def test_setPrivacyPolicy_error_2(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']
    other = users['admin']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # Owner以外のアドレスから更新 -> Failure
    web3.eth.defaultAccount = other
    try:
        chain.wait.for_receipt(bs_token.transact().setPrivacyPolicy('updated privacy policy'))
    except ValueError:
        pass

    privacy_policy = bs_token.call().privacyPolicy()
    assert privacy_policy == 'some_privacy_policy'


'''
TEST_メモの更新（setMemo）
'''


# 正常系1: 発行（デプロイ） -> メモ欄の修正
def test_setMemo_normal_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # メモ欄の修正 -> Success
    web3.eth.defaultAccount = issuer
    txn_hash = bs_token.transact().setMemo('updated memo')
    chain.wait.for_receipt(txn_hash)

    memo = bs_token.call().memo()
    assert memo == 'updated memo'


# エラー系1: 入力値の型誤り
def test_setMemo_error_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        bs_token.transact().setMemo(1234)


# エラー系2: Owner以外のアドレスからメモ欄の修正を実施した場合
def test_setMemo_error_2(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']
    other = users['admin']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # Owner以外のアドレスからメモ欄の修正を実施 -> Failure
    web3.eth.defaultAccount = other
    try:
        chain.wait.for_receipt(bs_token.transact().setMemo('updated memo'))
    except ValueError:
        pass

    memo = bs_token.call().memo()
    assert memo == 'some_memo'


'''
TEST_譲渡可能更新（setTransferable）
'''


# 正常系1: 発行 -> 譲渡可能更新
def test_setTransferable_normal_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']
    after_transferable = False

    # 新規発行
    web3.eth.defaultAccount = issuer
    beneficiary_security_contract, deploy_args = \
        utils.issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 譲渡可能更新
    web3.eth.defaultAccount = issuer
    txn_hash = beneficiary_security_contract.transact().setTransferable(after_transferable)
    chain.wait.for_receipt(txn_hash)

    transferable = beneficiary_security_contract.call().transferable()
    assert after_transferable == transferable


# エラー系1: 入力値の型誤り
def test_setTransferable_error_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    beneficiary_security_contract, deploy_args = \
        utils.issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 型誤り
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        beneficiary_security_contract.transact().setTransferable('False')


# エラー系2: 権限エラー
def test_setTransferable_error_2(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']
    attacker = users['trader']
    after_transferable = False

    # 新規発行
    web3.eth.defaultAccount = issuer
    beneficiary_security_contract, deploy_args = \
        utils.issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 譲渡可能更新
    web3.eth.defaultAccount = attacker
    try:
        txn_hash = beneficiary_security_contract.transact().setTransferable(after_transferable)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    transferable = beneficiary_security_contract.call().transferable()
    assert transferable == True


'''
TEST_募集ステータス更新（setOfferingStatus）
'''


# 正常系1: 発行 -> 新規募集ステータス更新（False→True）
def test_setOfferingStatus_normal_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = \
        utils.issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 初期状態 == False
    assert bs_token.call().offeringStatus() is False

    # 新規募集ステータスの更新
    web3.eth.defaultAccount = issuer
    txn_hash = bs_token.transact().setOfferingStatus(True)
    chain.wait.for_receipt(txn_hash)

    assert bs_token.call().offeringStatus() is True


# 正常系2:
#   発行 -> 新規募集ステータス更新（False→True） -> 2回目更新（True→False）
def test_setOfferingStatus_normal_2(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = \
        utils.issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 新規募集ステータスの更新
    web3.eth.defaultAccount = issuer
    txn_hash = bs_token.transact().setOfferingStatus(True)
    chain.wait.for_receipt(txn_hash)

    # 新規募集ステータスの更新（2回目）
    web3.eth.defaultAccount = issuer
    txn_hash = bs_token.transact().setOfferingStatus(False)
    chain.wait.for_receipt(txn_hash)

    assert bs_token.call().offeringStatus() is False


# エラー系1: 発行 -> 新規募集ステータス更新（入力値の型誤り）
def test_setOfferingStatus_error_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = \
        utils.issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 新規募集ステータスの更新（エラー）：文字型
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        bs_token.transact().setOfferingStatus('True')


'''
TEST_残高確認（balanceOf）
'''


# 正常系1: 商品コントラクト作成 -> 残高確認
def test_balanceOf_normal_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    balance = bs_token.call().balanceOf(issuer)
    assert balance == 10000


# エラー系1: 入力値の型誤り（Owner）
def test_balanceOf_error_1(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    account_address = 1234

    with pytest.raises(TypeError):
        bs_token.call().balanceOf(account_address)


'''
TEST_トークンの振替（transfer）
'''


# 正常系1: アカウントアドレスへの振替
def test_transfer_normal_1(web3, chain, users, bs_exchange, personal_info):
    from_address = users['issuer']
    to_address = users['trader']
    transfer_amount = 100

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = from_address
    beneficiary_security_contract, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 振替先の個人情報登録
    web3.eth.defaultAccount = to_address
    utils.register_personal_info(chain, personal_info, from_address)

    # 振替
    web3.eth.defaultAccount = from_address
    txn_hash = beneficiary_security_contract.transact().transfer(to_address, transfer_amount)
    chain.wait.for_receipt(txn_hash)

    from_balance = beneficiary_security_contract.call().balanceOf(from_address)
    to_balance = beneficiary_security_contract.call().balanceOf(to_address)

    assert from_balance == deploy_args[5] - transfer_amount
    assert to_balance == transfer_amount


# 正常系2: 受益証券取引コントラクトへの振替
def test_transfer_normal_2(web3, chain, users, bs_exchange, personal_info):
    from_address = users['issuer']
    transfer_amount = 100

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = from_address
    beneficiary_security_contract, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    to_address = bs_exchange.address
    txn_hash = beneficiary_security_contract.transact().transfer(to_address, transfer_amount)
    chain.wait.for_receipt(txn_hash)

    from_balance = beneficiary_security_contract.call().balanceOf(from_address)
    to_balance = beneficiary_security_contract.call().balanceOf(to_address)

    assert from_balance == deploy_args[5] - transfer_amount
    assert to_balance == transfer_amount


# エラー系1: 入力値の型誤り（To）
def test_transfer_error_1(web3, chain, users, bs_exchange, personal_info):
    from_address = users['issuer']
    to_address = 1234
    transfer_amount = 100

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = from_address
    beneficiary_security_contract, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    with pytest.raises(TypeError):
        beneficiary_security_contract.transact().transfer(to_address, transfer_amount)


# エラー系2: 入力値の型誤り（Value）
def test_transfer_error_2(web3, chain, users, bs_exchange, personal_info):
    from_address = users['issuer']
    to_address = users['trader']
    transfer_amount = '100'

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = from_address
    beneficiary_security_contract, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    with pytest.raises(TypeError):
        beneficiary_security_contract.transact().transfer(to_address, transfer_amount)


# エラー系3: 残高不足
def test_transfer_error_3(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']
    from_address = issuer
    to_address = users['trader']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = from_address
    beneficiary_security_contract, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 個人情報登録
    web3.eth.defaultAccount = to_address
    utils.register_personal_info(chain, personal_info, from_address)

    # 受益証券トークン振替（残高超）
    web3.eth.defaultAccount = issuer
    transfer_amount = 10000000000
    try:
        beneficiary_security_contract.transact().transfer(to_address, transfer_amount)  # エラーになる
    except ValueError:
        pass

    assert beneficiary_security_contract.call().balanceOf(issuer) == 10000
    assert beneficiary_security_contract.call().balanceOf(to_address) == 0


# エラー系4: private functionにアクセスできない
def test_transfer_error_4(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']
    from_address = issuer
    to_address = users['trader']

    transfer_amount = 100
    data = 0

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = from_address
    beneficiary_security_contract, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    with pytest.raises(ValueError):
        beneficiary_security_contract.call().isContract(to_address)

    with pytest.raises(ValueError):
        beneficiary_security_contract.transact().transferToAddress(to_address, transfer_amount, data)

    with pytest.raises(ValueError):
        beneficiary_security_contract.transact().transferToContract(to_address, transfer_amount, data)


# エラー系5: 取引不可Exchangeへの振替
def test_transfer_error_5(web3, chain, users, bs_exchange, personal_info,
                          coupon_exchange_storage, payment_gateway):
    from_address = users['issuer']
    transfer_amount = 100

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = from_address
    beneficiary_security_contract, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 取引不可Exchange
    web3.eth.defaultAccount = users['admin']
    dummy_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetCouponExchange',  # IbetBeneficiarySecurityExchange以外を読み込む必要がある
        deploy_args=[
            payment_gateway.address,
            coupon_exchange_storage.address
        ]
    )

    to_address = dummy_exchange.address
    try:
        txn_hash = beneficiary_security_contract.transact().transfer(to_address, transfer_amount)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    from_balance = beneficiary_security_contract.call().balanceOf(from_address)
    to_balance = beneficiary_security_contract.call().balanceOf(to_address)

    assert from_balance == deploy_args[5]
    assert to_balance == 0


# エラー系6: 譲渡不可トークンの振替
def test_transfer_error_6(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']
    to_address = users['trader']
    transfer_amount = 100

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    beneficiary_security_contract, deploy_args = \
        utils.issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 個人情報登録
    web3.eth.defaultAccount = to_address
    utils.register_personal_info(chain, personal_info, issuer)

    # 譲渡不可設定
    web3.eth.defaultAccount = issuer
    txn_hash = beneficiary_security_contract.transact().setTransferable(False)
    chain.wait.for_receipt(txn_hash)

    # 譲渡実行
    web3.eth.defaultAccount = issuer
    try:
        txn_hash = beneficiary_security_contract.transact().transfer(to_address, transfer_amount)  # エラーとなる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    from_balance = beneficiary_security_contract.call().balanceOf(issuer)
    to_balance = beneficiary_security_contract.call().balanceOf(to_address)

    assert from_balance == deploy_args[5]
    assert to_balance == 0


# エラー系7: 個人情報未登録アドレスへの振替
def test_transfer_error_7(web3, chain, users, bs_exchange, personal_info):
    issuer = users['issuer']
    to_address = users['trader']
    transfer_amount = 100

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = issuer
    beneficiary_security_contract, deploy_args = \
        utils.issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # NOTE:個人情報未登録（to_address）

    # 譲渡実行
    web3.eth.defaultAccount = issuer
    try:
        txn_hash = beneficiary_security_contract.transact().transfer(to_address, transfer_amount)  # エラーとなる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    from_balance = beneficiary_security_contract.call().balanceOf(issuer)
    to_balance = beneficiary_security_contract.call().balanceOf(to_address)

    assert from_balance == deploy_args[5]
    assert to_balance == 0


'''
TEST_トークンの移転（transferFrom）
'''


# 正常系1: アカウントアドレスへの移転
def test_transferFrom_normal_1(web3, chain, users, bs_exchange, personal_info):
    _issuer = users['issuer']
    _from = users['admin']
    _to = users['trader']
    _value = 100

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = _issuer
    beneficiary_security_contract, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 振替先の個人情報登録（_from）
    web3.eth.defaultAccount = _from
    utils.register_personal_info(chain, personal_info, _issuer)

    # 譲渡（issuer -> _from）
    web3.eth.defaultAccount = _issuer
    txn_hash = beneficiary_security_contract.transact().transfer(_from, _value)
    chain.wait.for_receipt(txn_hash)

    # 移転（_from -> _to）
    web3.eth.defaultAccount = _issuer
    txn_hash = beneficiary_security_contract.transact().transferFrom(_from, _to, _value)
    chain.wait.for_receipt(txn_hash)

    issuer_balance = beneficiary_security_contract.call().balanceOf(_issuer)
    from_balance = beneficiary_security_contract.call().balanceOf(_from)
    to_balance = beneficiary_security_contract.call().balanceOf(_to)

    assert issuer_balance == deploy_args[5] - _value
    assert from_balance == 0
    assert to_balance == _value


# エラー系1: 入力値の型誤り（From）
def test_transferFrom_error_1(web3, chain, users, bs_exchange, personal_info):
    _issuer = users['issuer']
    _to = users['trader']
    _value = 100

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = _issuer
    beneficiary_security_contract, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 移転（_from -> _to）
    web3.eth.defaultAccount = _issuer

    with pytest.raises(TypeError):
        beneficiary_security_contract.transact().transferFrom('1234', _to, _value)

    with pytest.raises(TypeError):
        beneficiary_security_contract.transact().transferFrom(1234, _to, _value)


# エラー系2: 入力値の型誤り（To）
def test_transferFrom_error_2(web3, chain, users, bs_exchange, personal_info):
    _issuer = users['issuer']
    _from = users['admin']
    _value = 100

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = _issuer
    beneficiary_security_contract, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 移転（_from -> _to）
    web3.eth.defaultAccount = _issuer

    with pytest.raises(TypeError):
        beneficiary_security_contract.transact().transferFrom(_from, '1234', _value)

    with pytest.raises(TypeError):
        beneficiary_security_contract.transact().transferFrom(_from, 1234, _value)


# エラー系3: 入力値の型誤り（Value）
def test_transferFrom_error_3(web3, chain, users, bs_exchange, personal_info):
    _issuer = users['issuer']
    _from = users['admin']
    _to = users['trader']

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = _issuer
    beneficiary_security_contract, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 移転（_from -> _to）
    web3.eth.defaultAccount = _issuer

    with pytest.raises(TypeError):
        beneficiary_security_contract.transact().transferFrom(_from, _to, -1)

    with pytest.raises(TypeError):
        beneficiary_security_contract.transact().transferFrom(_from, _to, 2 ** 256)

    with pytest.raises(TypeError):
        beneficiary_security_contract.transact().transferFrom(_from, _to, '0')

    with pytest.raises(TypeError):
        beneficiary_security_contract.transact().transferFrom(_from, _to, 0.1)


# エラー系4: 残高不足
def test_transferFrom_error_4(web3, chain, users, bs_exchange, personal_info):
    _issuer = users['issuer']
    _from = users['admin']
    _to = users['trader']
    _value = 100

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = _issuer
    beneficiary_security_contract, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 振替先の個人情報登録（_from）
    web3.eth.defaultAccount = _from
    utils.register_personal_info(chain, personal_info, _issuer)

    # 譲渡（issuer -> _from）
    web3.eth.defaultAccount = _issuer
    txn_hash = beneficiary_security_contract.transact().transfer(_from, _value)
    chain.wait.for_receipt(txn_hash)

    # 移転（_from -> _to）
    web3.eth.defaultAccount = _issuer
    try:
        txn_hash = beneficiary_security_contract.transact().transferFrom(_from, _to, 101)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    issuer_balance = beneficiary_security_contract.call().balanceOf(_issuer)
    from_balance = beneficiary_security_contract.call().balanceOf(_from)
    to_balance = beneficiary_security_contract.call().balanceOf(_to)

    assert issuer_balance == deploy_args[5] - _value
    assert from_balance == _value
    assert to_balance == 0


# エラー系5: 権限エラー
def test_transferFrom_error_5(web3, chain, users, bs_exchange, personal_info):
    _issuer = users['issuer']
    _from = users['admin']
    _to = users['trader']
    _value = 100

    # 受益証券トークン新規発行
    web3.eth.defaultAccount = _issuer
    beneficiary_security_contract, deploy_args = utils. \
        issue_bs_token(web3, chain, users, bs_exchange.address, personal_info.address)

    # 振替先の個人情報登録（_from）
    web3.eth.defaultAccount = _from
    utils.register_personal_info(chain, personal_info, _issuer)

    # 譲渡（issuer -> _from）
    web3.eth.defaultAccount = _issuer
    txn_hash = beneficiary_security_contract.transact().transfer(_from, _value)
    chain.wait.for_receipt(txn_hash)

    # 移転（_from -> _to）
    web3.eth.defaultAccount = _from
    try:
        txn_hash = beneficiary_security_contract.transact().transferFrom(_from, _to, _value)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    issuer_balance = beneficiary_security_contract.call().balanceOf(_issuer)
    from_balance = beneficiary_security_contract.call().balanceOf(_from)
    to_balance = beneficiary_security_contract.call().balanceOf(_to)

    assert issuer_balance == deploy_args[5] - _value
    assert from_balance == _value
    assert to_balance == 0


'''
TEST_募集申込（applyForOffering）
'''


# 正常系1
#   発行：発行体 -> （申込なし）初期データ参照
def test_applyForOffering_normal_1(web3, chain, users):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = \
        utils.issue_bs_token(web3, chain, users, zero_address, zero_address)

    application = bs_token.call().applications(trader)
    assert application[0] == 0
    assert application[1] == ''

# 正常系2
#   発行：発行体 -> 投資家：募集申込
def test_applyForOffering_normal_2(web3, chain, users, personal_info):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = \
        utils.issue_bs_token(web3, chain, users, zero_address, personal_info.address)

    # 新規募集ステータスの更新
    web3.eth.defaultAccount = issuer
    txn_hash = bs_token.transact().setOfferingStatus(True)
    chain.wait.for_receipt(txn_hash)

    # 個人情報登録
    web3.eth.defaultAccount = trader
    utils.register_personal_info(chain, personal_info, issuer)

    # 募集申込
    web3.eth.defaultAccount = trader
    txn_hash = bs_token.transact().applyForOffering(10, 'abcdefgh')
    chain.wait.for_receipt(txn_hash)

    application = bs_token.call().applications(trader)
    assert application[0] == 10
    assert application[1] == 'abcdefgh'


# 正常系3
#   発行：発行体 -> 投資家：募集申込（複数回）
def test_applyForOffering_normal_3(web3, chain, users, personal_info):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = \
        utils.issue_bs_token(web3, chain, users, zero_address, personal_info.address)

    # 新規募集ステータスの更新
    web3.eth.defaultAccount = issuer
    txn_hash = bs_token.transact().setOfferingStatus(True)
    chain.wait.for_receipt(txn_hash)

    # 個人情報登録
    web3.eth.defaultAccount = trader
    utils.register_personal_info(chain, personal_info, issuer)

    # 募集申込
    web3.eth.defaultAccount = trader
    txn_hash = bs_token.transact().applyForOffering(10, 'abcdefgh')
    chain.wait.for_receipt(txn_hash)

    # 募集申込：２回目
    web3.eth.defaultAccount = trader
    txn_hash = bs_token.transact().applyForOffering(20, 'vwxyz')
    chain.wait.for_receipt(txn_hash)

    application = bs_token.call().applications(trader)
    assert application[0] == 20
    assert application[1] == 'vwxyz'


# エラー系1:
#   発行：発行体 -> 投資家：募集申込（入力値の型誤り）
def test_applyForOffering_error_1(web3, chain, users):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = \
        utils.issue_bs_token(web3, chain, users, zero_address, zero_address)

    # 募集申込（エラー）：amount 文字型
    web3.eth.defaultAccount = trader
    with pytest.raises(TypeError):
        bs_token.transact().applyForOffering("10", "1234")

    # 募集申込（エラー）：data 数値型
    web3.eth.defaultAccount = trader
    with pytest.raises(TypeError):
        bs_token.transact().applyForOffering(10, 1234)


# エラー系2:
#   発行：発行体 -> 投資家：募集申込（申込ステータスが停止中）
def test_applyForOffering_error_2(web3, chain, users):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = \
        utils.issue_bs_token(web3, chain, users, zero_address, zero_address)

    # 募集申込（エラー）：募集申込ステータスFalse状態での申込
    web3.eth.defaultAccount = trader
    try:
        txn_hash = bs_token.transact().applyForOffering(10, 'abcdefgh')
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    application = bs_token.call().applications(trader)
    assert application[0] == 0
    assert application[1] == ''


# エラー系3
#   発行：発行体 -> 投資家：募集申込（個人情報未登録）
def test_applyForOffering_error_3(web3, chain, users, personal_info):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = \
        utils.issue_bs_token(web3, chain, users, zero_address, personal_info.address)

    # 新規募集ステータスの更新
    web3.eth.defaultAccount = issuer
    txn_hash = bs_token.transact().setOfferingStatus(True)
    chain.wait.for_receipt(txn_hash)

    # 個人情報未登録

    # 募集申込（エラーになる）
    web3.eth.defaultAccount = trader
    try:
        txn_hash = bs_token.transact().applyForOffering(10, 'abcdefgh')
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    application = bs_token.call().applications(trader)
    assert application[0] == 0
    assert application[1] == ''


'''
TEST_追加発行（issue）
'''


# 正常系1: 発行 -> 追加発行
def test_issue_normal_1(web3, chain, users):
    issuer = users['issuer']
    value = 10

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils.issue_bs_token(web3, chain, users, zero_address, zero_address)

    # 追加発行
    web3.eth.defaultAccount = issuer
    txn_hash = bs_token.transact().issue(value)
    chain.wait.for_receipt(txn_hash)

    total_supply = bs_token.call().totalSupply()
    balance = bs_token.call().balanceOf(issuer)

    assert total_supply == deploy_args[5] + value
    assert balance == deploy_args[5] + value


# エラー系1: 入力値の型誤り
def test_issue_error_1(web3, chain, users):
    issuer = users['issuer']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils.issue_bs_token(web3, chain, users, zero_address, zero_address)

    # String
    with pytest.raises(TypeError):
        bs_token.transact().issue("1")

    # 小数
    with pytest.raises(TypeError):
        bs_token.transact().issue(1.0)


# エラー系2: 限界値超
def test_issue_error_2(web3, chain, users):
    issuer = users['issuer']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils.issue_bs_token(web3, chain, users, zero_address, zero_address)

    # 上限値超
    with pytest.raises(TypeError):
        bs_token.transact().issue(2 ** 256)

    # 下限値超
    with pytest.raises(TypeError):
        bs_token.transact().issue(-1)


# エラー系3: 発行→追加発行→上限界値超
def test_issue_error_3(web3, chain, users):
    issuer = users['issuer']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils.issue_bs_token(web3, chain, users, zero_address, zero_address)

    issue_amount = 2**256 - deploy_args[5]

    # 追加発行（限界値超）
    web3.eth.defaultAccount = issuer
    try:
        txn_hash = bs_token.transact().issue(issue_amount)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    total_supply = bs_token.call().totalSupply()
    balance = bs_token.call().balanceOf(issuer)

    assert total_supply == deploy_args[5]
    assert balance == deploy_args[5]


# エラー系4: 権限エラー
def test_issue_error_4(web3, chain, users):
    issuer = users['issuer']
    attacker = users['trader']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    bs_token, deploy_args = utils.issue_bs_token(web3, chain, users, zero_address, zero_address)

    # 追加発行：権限エラー
    web3.eth.defaultAccount = attacker
    try:
        txn_hash = bs_token.transact().issue(1)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    total_supply = bs_token.call().totalSupply()
    balance = bs_token.call().balanceOf(issuer)

    assert total_supply == deploy_args[5]
    assert balance == deploy_args[5]
