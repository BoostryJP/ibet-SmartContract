import pytest
import utils
from eth_utils import to_checksum_address
import brownie_utils

zero_address = '0x0000000000000000000000000000000000000000'


def init_args(exchange_address, personal_info_address):
    name = 'test_bond'
    symbol = 'BND'
    total_supply = 10000
    face_value = 10000
    interest_rate = 1000
    interest_payment_date = '{"interestPaymentDate1":"0331","interestPaymentDate2":"0930"}'
    redemption_date = '20191231'
    redemption_value = 100
    return_date = '20191231'
    return_amount = 'some_return'
    purpose = 'some_purpose'
    memo = 'some_memo'
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'

    deploy_args = [
        name, symbol, total_supply, exchange_address, face_value,
        interest_rate, interest_payment_date, redemption_date,
        redemption_value, return_date, return_amount,
        purpose, memo,
        contact_information, privacy_policy,
        personal_info_address
    ]
    return deploy_args


'''
TEST_デプロイ
'''


# 正常系1: deploy
def test_deploy_normal_1(users, IbetStraightBond, bond_exchange, personal_info):
    account_address = users['issuer']
    deploy_args = init_args(bond_exchange.address, personal_info.address)

    bond_contract = brownie_utils.force_deploy(
        account_address,
        IbetStraightBond,
        *deploy_args
    )

    owner_address = bond_contract.owner()
    name = bond_contract.name()
    symbol = bond_contract.symbol()
    total_supply = bond_contract.totalSupply()
    tradable_exchange = bond_contract.tradableExchange()
    face_value = bond_contract.faceValue()
    interest_rate = bond_contract.interestRate()
    interest_payment_date = bond_contract.interestPaymentDate()
    redemption_date = bond_contract.redemptionDate()
    redemption_value = bond_contract.redemptionValue()
    return_date = bond_contract.returnDate()
    return_amount = bond_contract.returnAmount()
    purpose = bond_contract.purpose()
    memo = bond_contract.memo()
    transferable = bond_contract.transferable()
    contact_information = bond_contract.contactInformation()
    privacy_policy = bond_contract.privacyPolicy()
    personal_info_address = bond_contract.personalInfoAddress()

    assert owner_address == account_address
    assert name == deploy_args[0]
    assert symbol == deploy_args[1]
    assert total_supply == deploy_args[2]
    assert tradable_exchange == to_checksum_address(deploy_args[3])
    assert face_value == deploy_args[4]
    assert interest_rate == deploy_args[5]
    assert interest_payment_date == deploy_args[6]
    assert redemption_date == deploy_args[7]
    assert redemption_value == deploy_args[8]
    assert return_date == deploy_args[9]
    assert return_amount == deploy_args[10]
    assert purpose == deploy_args[11]
    assert memo == deploy_args[12]
    assert contact_information == deploy_args[13]
    assert privacy_policy == deploy_args[14]
    assert transferable == True
    assert personal_info_address == to_checksum_address(deploy_args[15])


# エラー系1: 入力値の型誤り（name）
def test_deploy_error_1(users, bond_exchange, IbetStraightBond, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[0] = '0x66aB6D9362d4F35596279692F0251Db635165871'
    with pytest.raises(ValueError):
        brownie_utils.force_deploy(users['issuer'], IbetStraightBond, *deploy_args)


# エラー系2: 入力値の型誤り（symbol）
def test_deploy_error_2(users, bond_exchange, IbetStraightBond, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[1] = '0x66aB6D9362d4F35596279692F0251Db635165871'
    with pytest.raises(ValueError):
        brownie_utils.force_deploy(users['issuer'], IbetStraightBond, *deploy_args)


# エラー系3: 入力値の型誤り（totalSupply）
def test_deploy_error_3(users, bond_exchange, IbetStraightBond, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[2] = "abc"
    with pytest.raises(TypeError):
        brownie_utils.force_deploy(users['issuer'], IbetStraightBond, *deploy_args)


# エラー系4: 入力値の型誤り（faceValue）
def test_deploy_error_4(users, bond_exchange, IbetStraightBond, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[4] = "abc"
    with pytest.raises(TypeError):
        brownie_utils.force_deploy(users['issuer'], IbetStraightBond, *deploy_args)


# エラー系5: 入力値の型誤り（interestRate）
def test_deploy_error_5(users, bond_exchange, IbetStraightBond, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[5] = "abc"
    with pytest.raises(TypeError):
        brownie_utils.force_deploy(users['issuer'], IbetStraightBond, *deploy_args)


# エラー系6: 入力値の型誤り（interestPaymentDate）
def test_deploy_error_6(users, bond_exchange, IbetStraightBond, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[6] = '0x66aB6D9362d4F35596279692F0251Db635165871'
    with pytest.raises(ValueError):
        brownie_utils.force_deploy(users['issuer'], IbetStraightBond, *deploy_args)


# エラー系7: 入力値の型誤り（redemptionDate）
def test_deploy_error_7(users, bond_exchange, IbetStraightBond, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[7] = '0x66aB6D9362d4F35596279692F0251Db635165871'
    with pytest.raises(ValueError):
        brownie_utils.force_deploy(users['issuer'], IbetStraightBond, *deploy_args)


# エラー系8: 入力値の型誤り（redemptionValue）
def test_deploy_error_8(users, bond_exchange, IbetStraightBond, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[8] = "abc"
    with pytest.raises(TypeError):
        brownie_utils.force_deploy(users['issuer'], IbetStraightBond, *deploy_args)


# エラー系9: 入力値の型誤り（returnDate）
def test_deploy_error_9(users, bond_exchange, IbetStraightBond, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[9] = '0x66aB6D9362d4F35596279692F0251Db635165871'
    with pytest.raises(ValueError):
        brownie_utils.force_deploy(users['issuer'], IbetStraightBond, *deploy_args)


# エラー系10: 入力値の型誤り（returnAmount）
def test_deploy_error_10(users, bond_exchange, IbetStraightBond, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[10] = '0x66aB6D9362d4F35596279692F0251Db635165871'
    with pytest.raises(ValueError):
        brownie_utils.force_deploy(users['issuer'], IbetStraightBond, *deploy_args)


# エラー系11: 入力値の型誤り（purpose）
def test_deploy_error_11(users, bond_exchange, IbetStraightBond, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[11] = '0x66aB6D9362d4F35596279692F0251Db635165871'
    with pytest.raises(ValueError):
        brownie_utils.force_deploy(users['issuer'], IbetStraightBond, *deploy_args)


# エラー系12: 入力値の型誤り（memo）
def test_deploy_error_12(users, bond_exchange, IbetStraightBond, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[12] = '0x66aB6D9362d4F35596279692F0251Db635165871'
    with pytest.raises(ValueError):
        brownie_utils.force_deploy(users['issuer'], IbetStraightBond, *deploy_args)


# エラー系13: 入力値の型誤り（tradableExchange）
def test_deploy_error_13(users, bond_exchange, IbetStraightBond, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[3] = '0xaaaa'
    with pytest.raises(ValueError):
        brownie_utils.force_deploy(users['issuer'], IbetStraightBond, *deploy_args)


# エラー系14: 入力値の型誤り（contactInformation）
def test_deploy_error_14(users, bond_exchange, IbetStraightBond, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[13] = '0x66aB6D9362d4F35596279692F0251Db635165871'
    with pytest.raises(ValueError):
        brownie_utils.force_deploy(users['issuer'], IbetStraightBond, *deploy_args)


# エラー系15: 入力値の型誤り（privacyPolicy）
def test_deploy_error_15(users, bond_exchange, IbetStraightBond, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[14] = '0x66aB6D9362d4F35596279692F0251Db635165871'
    with pytest.raises(ValueError):
        brownie_utils.force_deploy(users['issuer'], IbetStraightBond, *deploy_args)


# エラー系16: 入力値の型誤り（personalInfoAddress）
def test_deploy_error_16(users, bond_exchange, IbetStraightBond, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[15] = '0xaaaa'
    with pytest.raises(ValueError):
        brownie_utils.force_deploy(users['issuer'], IbetStraightBond, *deploy_args)


'''
TEST_譲渡可能更新（setTransferable）
'''


# 正常系1: 発行 -> 譲渡可能更新
def test_setTransferable_normal_1(users, bond_exchange, personal_info):
    issuer = users['issuer']
    after_transferable = False

    # 新規発行
    bond_contract, deploy_args = \
        utils.issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 譲渡可能更新
    bond_contract.setTransferable.transact(after_transferable, {'from': issuer})

    transferable = bond_contract.transferable()
    assert after_transferable == transferable


# エラー系1: 入力値の型誤り
def test_setTransferable_error_1(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 新規発行
    bond_contract, deploy_args = \
        utils.issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 型誤り
    with pytest.raises(ValueError):
        bond_contract.setTransferable.transact('False', {'from': issuer})


# エラー系2: 権限エラー
def test_setTransferable_error_2(users, bond_exchange, personal_info):
    attacker = users['trader']
    after_transferable = False

    # 新規発行
    bond_contract, deploy_args = \
        utils.issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 譲渡可能更新
    bond_contract.setTransferable.transact(after_transferable, {'from': attacker})  # エラーになる

    transferable = bond_contract.transferable()
    assert transferable == True


'''
TEST_トークンの振替（transfer）
'''


# 正常系1: アカウントアドレスへの振替
def test_transfer_normal_1(users, bond_exchange, personal_info):
    from_address = users['issuer']
    to_address = users['trader']
    transfer_amount = 100

    # 債券トークン新規発行
    bond_contract, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 振替先の個人情報登録
    utils.register_personal_info(to_address, personal_info, from_address)

    # 振替
    bond_contract.transfer.transact(to_address, transfer_amount, {'from': from_address})

    from_balance = bond_contract.balanceOf(from_address)
    to_balance = bond_contract.balanceOf(to_address)

    assert from_balance == deploy_args[2] - transfer_amount
    assert to_balance == transfer_amount


# 正常系2: 債券取引コントラクトへの振替
def test_transfer_normal_2(users, bond_exchange, personal_info):
    from_address = users['issuer']
    transfer_amount = 100

    # 債券トークン新規発行
    bond_contract, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    to_address = bond_exchange.address
    bond_contract.transfer.transact(to_address, transfer_amount, {'from': from_address})

    from_balance = bond_contract.balanceOf(from_address)
    to_balance = bond_contract.balanceOf(to_address)

    assert from_balance == deploy_args[2] - transfer_amount
    assert to_balance == transfer_amount


# エラー系1: 入力値の型誤り（To）
def test_transfer_error_1(users, bond_exchange, personal_info):
    from_address = users['issuer']
    to_address = 1234
    transfer_amount = 100

    # 債券トークン新規発行
    bond_contract, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    with pytest.raises(ValueError):
        bond_contract.transfer.transact(to_address, transfer_amount, {'from': from_address})


# エラー系2: 入力値の型誤り（Value）
def test_transfer_error_2(users, bond_exchange, personal_info):
    from_address = users['issuer']
    to_address = users['trader']
    transfer_amount = 'abc'

    # 債券トークン新規発行
    bond_contract, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    with pytest.raises(TypeError):
        bond_contract.transfer.transact(to_address, transfer_amount, {'from': from_address})


# エラー系3: 残高不足
def test_transfer_error_3(users, bond_exchange, personal_info):
    issuer = users['issuer']
    from_address = issuer
    to_address = users['trader']

    # 債券トークン新規発行
    bond_contract, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 個人情報登録
    utils.register_personal_info(to_address, personal_info, from_address)

    # 債券トークン振替（残高超）
    transfer_amount = 10000000000
    bond_contract.transfer.transact(to_address, transfer_amount, {'from': issuer})  # エラーになる

    assert bond_contract.balanceOf(issuer) == 10000
    assert bond_contract.balanceOf(to_address) == 0


# エラー系4: private functionにアクセスできない
def test_transfer_error_4(users, bond_exchange, personal_info):
    issuer = users['issuer']
    from_address = issuer
    to_address = users['trader']

    transfer_amount = 100
    data = 0

    # 債券トークン新規発行
    bond_contract, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    with pytest.raises(AttributeError):
        bond_contract.isContract(to_address)

    with pytest.raises(AttributeError):
        bond_contract.transferToAddress.transact(to_address, transfer_amount, data, {'from': from_address})

    with pytest.raises(AttributeError):
        bond_contract.transferToContract.transact(to_address, transfer_amount, data, {'from': from_address})


# エラー系5: 取引不可Exchangeへの振替
def test_transfer_error_5(users, bond_exchange, personal_info,
                          coupon_exchange_storage, payment_gateway,
                          IbetCouponExchange):
    from_address = users['issuer']
    transfer_amount = 100

    # 債券トークン新規発行
    bond_contract, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 取引不可Exchange
    dummy_exchange = users['admin'].deploy(
        IbetCouponExchange,  # IbetStraightBondExchange以外を読み込む必要がある
        payment_gateway.address,
        coupon_exchange_storage.address
    )

    to_address = dummy_exchange.address
    bond_contract.transfer.transact(to_address, transfer_amount, {'from': users['admin']})  # エラーになる

    from_balance = bond_contract.balanceOf(from_address)
    to_balance = bond_contract.balanceOf(to_address)

    assert from_balance == deploy_args[2]
    assert to_balance == 0


# エラー系6: 譲渡不可トークンの振替
def test_transfer_error_6(users, bond_exchange, personal_info):
    issuer = users['issuer']
    to_address = users['trader']
    transfer_amount = 100

    # 債券トークン新規発行
    bond_contract, deploy_args = \
        utils.issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 個人情報登録
    utils.register_personal_info(to_address, personal_info, issuer)

    # 譲渡不可設定
    bond_contract.setTransferable.transact(False, {'from': issuer})

    # 譲渡実行
    bond_contract.transfer.transact(to_address, transfer_amount, {'from': issuer})  # エラーになる

    from_balance = bond_contract.balanceOf(issuer)
    to_balance = bond_contract.balanceOf(to_address)

    assert from_balance == deploy_args[2]
    assert to_balance == 0


# エラー系7: 個人情報未登録アドレスへの振替
def test_transfer_error_7(users, bond_exchange, personal_info):
    issuer = users['issuer']
    to_address = users['trader']
    transfer_amount = 100

    # 債券トークン新規発行
    bond_contract, deploy_args = \
        utils.issue_bond_token(users, bond_exchange.address, personal_info.address)

    # NOTE:個人情報未登録（to_address）

    # 譲渡実行
    bond_contract.transfer.transact(to_address, transfer_amount, {'from': issuer})  # エラーになる

    from_balance = bond_contract.balanceOf(issuer)
    to_balance = bond_contract.balanceOf(to_address)

    assert from_balance == deploy_args[2]
    assert to_balance == 0


'''
TEST_残高確認（balanceOf）
'''


# 正常系1: 商品コントラクト作成 -> 残高確認
def test_balanceOf_normal_1(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    balance = bond_token.balanceOf(issuer)
    assert balance == 10000


# エラー系1: 入力値の型誤り（Owner）
def test_balanceOf_error_1(users, bond_exchange, personal_info):
    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    account_address = 1234

    with pytest.raises(ValueError):
        bond_token.balanceOf(account_address)


'''
TEST_認定リクエスト（requestSignature）
'''


# 正常系1: 初期値が0
def test_requestSignature_normal_1(users, bond_exchange, personal_info):
    signer = users['admin']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    signature = bond_token.functions.signatures(signer)
    assert signature == 0


# 正常系2: 認定リクエスト
def test_requestSignature_normal_2(users, bond_exchange, personal_info):
    issuer = users['issuer']
    signer = users['admin']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    bond_token.requestSignature.transact(signer, {'from': issuer})

    signature = bond_token.functions.signatures(signer)
    assert signature == 1


# エラー系1: 入力値の型誤り（Signer）
def test_requestSignature_error_1(users, bond_exchange, personal_info):
    issuer = users['issuer']
    signer = 1234

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    with pytest.raises(ValueError):
        bond_token.requestSignature.transact(signer, {'from': issuer})


'''
TEST_認定（sign）
'''


# 正常系1: 認定リクエスト -> 認定
def test_sign_normal_1(users, bond_exchange, personal_info):
    issuer = users['issuer']
    signer = users['admin']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 認定リクエスト -> Success
    bond_token.requestSignature.transact(signer, {'from': issuer})

    # 認定 -> Success
    bond_token.sign.transact({'from': signer})

    signature = bond_token.functions.signatures(signer)
    assert signature == 2


# エラー系1: 認定リクエスト未実施 -> 認定
def test_sign_error_1(users, bond_exchange, personal_info):
    signer = users['admin']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 認定 -> Failure
    bond_token.sign.transact({'from': signer})
    signature = bond_token.functions.signatures(signer)
    assert signature == 0


# エラー系2: 認定リクエスト-> 異なるSinerから認定をした場合
def test_sign_error_2(users, bond_exchange, personal_info):
    issuer = users['issuer']
    signer = users['admin']
    signer_other = users['trader']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 認定リクエスト -> Success
    bond_token.requestSignature.transact(signer, {'from': issuer})

    # 異なるSignerが認定 -> Failure
    bond_token.sign.transact({'from': signer_other})
    signature = bond_token.functions.signatures(signer)
    assert signature == 1


'''
TEST_認定取消（unsign）
'''


# 正常系1: 認定リクエスト -> 認定 -> 認定取消
def test_unsign_normal_1(users, bond_exchange, personal_info):
    issuer = users['issuer']
    signer = users['admin']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 認定リクエスト -> Success
    bond_token.requestSignature.transact(signer, {'from': issuer})

    # 認定 -> Success
    bond_token.sign.transact({'from': signer})

    # 認定取消 -> Success
    bond_token.unsign.transact({'from': signer})

    signature = bond_token.functions.signatures(signer)
    assert signature == 0


# エラー系1: 認定リクエスト未実施 -> 認定取消
def test_unsign_error_1(users, bond_exchange, personal_info):
    signer = users['admin']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 認定取消 -> Failure
    bond_token.unsign.transact({'from': signer})
    signature = bond_token.functions.signatures(signer)
    assert signature == 0


# エラー系2: 認定リクエスト -> （認定未実施） -> 認定取消
def test_unsign_error_2(users, bond_exchange, personal_info):
    issuer = users['issuer']
    signer = users['admin']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 認定リクエスト -> Success
    bond_token.requestSignature.transact(signer, {'from': issuer})

    # 認定取消 -> Failure
    bond_token.unsign.transact({'from': signer})
    signature = bond_token.functions.signatures(signer)
    assert signature == 1


# エラー系3: 認定リクエスト-> 認定 -> 異なるSinerから認定取消を実施した場合
def test_unsign_error_3(users, bond_exchange, personal_info):
    issuer = users['issuer']
    signer = users['admin']
    signer_other = users['trader']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 認定リクエスト -> Success
    bond_token.requestSignature.transact(signer, {'from': issuer})

    # 認定 -> Success
    bond_token.sign.transact({'from': signer})

    # 異なるSignerが認定取消を実施 -> Failure
    bond_token.unsign.transact({'from': signer_other})
    signature = bond_token.functions.signatures(signer)
    assert signature == 2


'''
TEST_償還（redeem）
'''


# 正常系1: 発行（デプロイ） -> 償還
def test_redeem_normal_1(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    bond_token, deploy_args = utils.issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 償還 -> Success
    bond_token.redeem.transact({'from': issuer})

    is_redeemed = bond_token.isRedeemed()
    assert is_redeemed is True


# エラー系1: issuer以外のアドレスから償還を実施した場合
def test_redeem_error_1(users, bond_exchange, personal_info):
    other = users['admin']

    # 債券トークン新規発行
    bond_token, deploy_args = utils.issue_bond_token(users, bond_exchange.address, personal_info.address)

    # Owner以外のアドレスから償還を実施 -> Failure
    bond_token.redeem.transact({'from': other})
    is_redeemed = bond_token.isRedeemed()
    assert is_redeemed is False


'''
TEST_商品画像の設定（setImageURL, getImageURL）
'''


# 正常系1: 発行（デプロイ） -> 商品画像の設定
def test_setImageURL_normal_1(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    image_url = 'https://some_image_url.com/image.png'

    # 商品画像の設定 -> Success
    bond_token.setImageURL.transact(0, image_url, {'from': issuer})

    image_url_0 = bond_token.getImageURL(0)
    assert image_url_0 == image_url


# 正常系2: 発行（デプロイ） -> 商品画像の設定（複数設定）
def test_setImageURL_normal_2(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    image_url = 'https://some_image_url.com/image.png'

    # 商品画像の設定（1つ目） -> Success
    bond_token.setImageURL.transact(0, image_url, {'from': issuer})

    # 商品画像の設定（2つ目） -> Success
    bond_token.setImageURL.transact(1, image_url, {'from': issuer})

    image_url_0 = bond_token.getImageURL(0)
    image_url_1 = bond_token.getImageURL(1)
    assert image_url_0 == image_url
    assert image_url_1 == image_url


# 正常系3: 発行（デプロイ） -> 商品画像の設定（上書き登録）
def test_setImageURL_normal_3(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    image_url = 'https://some_image_url.com/image.png'
    image_url_after = 'https://some_image_url.com/image_after.png'

    # 商品画像の設定（1回目） -> Success
    bond_token.setImageURL.transact(0, image_url, {'from': issuer})

    # 商品画像の設定（2回目：上書き） -> Success
    bond_token.setImageURL.transact(0, image_url_after, {'from': issuer})

    image_url_0 = bond_token.getImageURL(0)
    assert image_url_0 == image_url_after


# エラー系1: 入力値の型誤り（Class）
def test_setImageURL_error_1(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    image_url = 'https://some_image_url.com/image.png'

    with pytest.raises(OverflowError):
        bond_token.setImageURL.transact(-1, image_url, {'from': issuer})

    with pytest.raises(OverflowError):
        bond_token.setImageURL.transact(256, image_url, {'from': issuer})

    with pytest.raises(TypeError):
        bond_token.setImageURL.transact('a', image_url, {'from': issuer})


# エラー系2: 入力値の型誤り（ImageURL）
def test_setImageURL_error_2(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    image_url = '0x66aB6D9362d4F35596279692F0251Db635165871'

    with pytest.raises(ValueError):
        bond_token.setImageURL.transact(0, image_url, {'from': issuer})


# エラー系3: Issuer以外のアドレスから画像設定を実施した場合
def test_setImageURL_error_3(users, bond_exchange, personal_info):
    other = users['admin']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    image_url = 'https://some_image_url.com/image.png'

    # Owner以外のアドレスから画像設定を実施 -> Failure
    bond_token.setImageURL.transact(0, image_url, {'from': other})
    image_url_0 = bond_token.getImageURL(0)
    assert image_url_0 == ''


'''
TEST_メモの更新（updateMemo）
'''


# 正常系1: 発行（デプロイ） -> メモ欄の修正
def test_updateMemo_normal_1(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # メモ欄の修正 -> Success
    bond_token.updateMemo.transact('updated memo', {'from': issuer})

    memo = bond_token.memo()
    assert memo == 'updated memo'


# エラー系1: 入力値の型誤り
def test_updateMemo_error_1(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    with pytest.raises(ValueError):
        bond_token.updateMemo.transact('0x66aB6D9362d4F35596279692F0251Db635165871', {'from': issuer})


# エラー系2: Owner以外のアドレスからメモ欄の修正を実施した場合
def test_updateMemo_error_2(users, bond_exchange, personal_info):
    other = users['admin']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # Owner以外のアドレスからメモ欄の修正を実施 -> Failure
    bond_token.updateMemo.transact('updated memo', {'from': other})
    memo = bond_token.memo()
    assert memo == 'some_memo'


'''
TEST_トークンの移転（transferFrom）
'''


# 正常系1: アカウントアドレスへの移転
def test_transferFrom_normal_1(users, bond_exchange, personal_info):
    _issuer = users['issuer']
    _from = users['admin']
    _to = users['trader']
    _value = 100

    # 債券トークン新規発行
    bond_contract, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 振替先の個人情報登録（_from）
    utils.register_personal_info(_from, personal_info, _issuer)

    # 譲渡（issuer -> _from）
    bond_contract.transfer.transact(_from, _value, {'from': _issuer})

    # 移転（_from -> _to）
    bond_contract.transferFrom.transact(_from, _to, _value, {'from': _issuer})

    issuer_balance = bond_contract.balanceOf(_issuer)
    from_balance = bond_contract.balanceOf(_from)
    to_balance = bond_contract.balanceOf(_to)

    assert issuer_balance == deploy_args[2] - _value
    assert from_balance == 0
    assert to_balance == _value


# エラー系1: 入力値の型誤り（From）
def test_transferFrom_error_1(users, bond_exchange, personal_info):
    _issuer = users['issuer']
    _to = users['trader']
    _value = 100

    # 債券トークン新規発行
    bond_contract, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 移転（_from -> _to）

    with pytest.raises(ValueError):
        bond_contract.transferFrom.transact('1234', _to, _value, {'from': _issuer})

    with pytest.raises(ValueError):
        bond_contract.transferFrom.transact(1234, _to, _value, {'from': _issuer})


# エラー系2: 入力値の型誤り（To）
def test_transferFrom_error_2(users, bond_exchange, personal_info):
    _issuer = users['issuer']
    _from = users['admin']
    _value = 100

    # 債券トークン新規発行
    bond_contract, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 移転（_from -> _to）

    with pytest.raises(ValueError):
        bond_contract.transferFrom.transact(_from, '1234', _value, {'from': _issuer})

    with pytest.raises(ValueError):
        bond_contract.transferFrom.transact(_from, 1234, _value, {'from': _issuer})


# エラー系3: 入力値の型誤り（Value）
def test_transferFrom_error_3(users, bond_exchange, personal_info):
    _issuer = users['issuer']
    _from = users['admin']
    _to = users['trader']

    # 債券トークン新規発行
    bond_contract, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 移転（_from -> _to）

    with pytest.raises(OverflowError):
        bond_contract.transferFrom.transact(_from, _to, -1, {'from': _issuer})

    with pytest.raises(OverflowError):
        bond_contract.transferFrom.transact(_from, _to, 2 ** 256, {'from': _issuer})

    with pytest.raises(TypeError):
        bond_contract.transferFrom.transact(_from, _to, 'abc', {'from': _issuer})


# エラー系4: 残高不足
def test_transferFrom_error_4(users, bond_exchange, personal_info):
    _issuer = users['issuer']
    _from = users['admin']
    _to = users['trader']
    _value = 100

    # 債券トークン新規発行
    bond_contract, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 振替先の個人情報登録（_from）
    utils.register_personal_info(_from, personal_info, _issuer)

    # 譲渡（issuer -> _from）
    bond_contract.transfer.transact(_from, _value, {'from': _issuer})

    # 移転（_from -> _to）
    bond_contract.transferFrom.transact(_from, _to, 101, {'from': _issuer})  # エラーになる

    issuer_balance = bond_contract.balanceOf(_issuer)
    from_balance = bond_contract.balanceOf(_from)
    to_balance = bond_contract.balanceOf(_to)

    assert issuer_balance == deploy_args[2] - _value
    assert from_balance == _value
    assert to_balance == 0


# エラー系5: 権限エラー
def test_transferFrom_error_5(users, bond_exchange, personal_info):
    _issuer = users['issuer']
    _from = users['admin']
    _to = users['trader']
    _value = 100

    # 債券トークン新規発行
    bond_contract, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 振替先の個人情報登録（_from）
    utils.register_personal_info(_from, personal_info, _issuer)

    # 譲渡（issuer -> _from）
    bond_contract.transfer.transact(_from, _value, {'from': _issuer})

    # 移転（_from -> _to）
    bond_contract.transferFrom.transact(_from, _to, _value, {'from': _from})  # エラーになる

    issuer_balance = bond_contract.balanceOf(_issuer)
    from_balance = bond_contract.balanceOf(_from)
    to_balance = bond_contract.balanceOf(_to)

    assert issuer_balance == deploy_args[2] - _value
    assert from_balance == _value
    assert to_balance == 0


'''
TEST_取引可能Exchangeの更新（setTradableExchange）
'''


# 正常系1: 発行 -> Exchangeの更新
def test_setTradableExchange_normal_1(users, bond_exchange, personal_info,
                                      coupon_exchange_storage, payment_gateway,
                                      IbetCouponExchange):
    issuer = users['issuer']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # その他Exchange
    other_exchange = users['admin'].deploy(
        IbetCouponExchange,  # IbetStraightBondExchange以外を読み込む必要がある
        payment_gateway.address,
        coupon_exchange_storage.address
    )

    # Exchangeの更新
    bond_token.setTradableExchange.transact(other_exchange.address, {'from': issuer})

    assert bond_token.tradableExchange() == to_checksum_address(other_exchange.address)


# エラー系1: 発行 -> Exchangeの更新（入力値の型誤り）
def test_setTradableExchange_error_1(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # Exchangeの更新
    with pytest.raises(ValueError):
        bond_token.setTradableExchange.transact('0xaaaa', {'from': issuer})


# エラー系2: 発行 -> Exchangeの更新（権限エラー）
def test_setTradableExchange_error_2(users, bond_exchange, personal_info,
                                     coupon_exchange_storage, payment_gateway,
                                     IbetCouponExchange):
    trader = users['trader']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # その他Exchange
    other_exchange = users['admin'].deploy(
        IbetCouponExchange,  # IbetStraightBondExchange以外を読み込む必要がある
        payment_gateway.address,
        coupon_exchange_storage.address
    )

    # Exchangeの更新
    bond_token.setTradableExchange.transact(other_exchange.address, {'from': trader})  # エラーになる

    assert bond_token.tradableExchange() == to_checksum_address(bond_exchange.address)


'''
TEST_問い合わせ先情報の更新（setContactInformation）
'''


# 正常系1: 発行（デプロイ） -> 修正
def test_setContactInformation_normal_1(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 修正 -> Success
    bond_token.setContactInformation.transact('updated contact information', {'from': issuer})

    contact_information = bond_token.contactInformation()
    assert contact_information == 'updated contact information'


# エラー系1: 入力値の型誤り
def test_setContactInformation_error_1(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    with pytest.raises(ValueError):
        bond_token.setContactInformation.transact('0x66aB6D9362d4F35596279692F0251Db635165871', {'from': issuer})


# エラー系2: 権限エラー
def test_setContactInformation_error_2(users, bond_exchange, personal_info):
    other = users['admin']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # Owner以外のアドレスから更新 -> Failure
    bond_token.setContactInformation.transact('updated contact information', {'from': other})
    contact_information = bond_token.contactInformation()
    assert contact_information == 'some_contact_information'


'''
TEST_プライバシーポリシーの更新（setPrivacyPolicy）
'''


# 正常系1: 発行（デプロイ） -> 修正
def test_setPrivacyPolicy_normal_1(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 修正 -> Success
    bond_token.setPrivacyPolicy.transact('updated privacy policy', {'from': issuer})

    privacy_policy = bond_token.privacyPolicy()
    assert privacy_policy == 'updated privacy policy'


# エラー系1: 入力値の型誤り
def test_setPrivacyPolicy_error_1(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    with pytest.raises(ValueError):
        bond_token.setPrivacyPolicy.transact('0x66aB6D9362d4F35596279692F0251Db635165871', {'from': issuer})


# エラー系2: 権限エラー
def test_setPrivacyPolicy_error_2(users, bond_exchange, personal_info):
    other = users['admin']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # Owner以外のアドレスから更新 -> Failure
    bond_token.setPrivacyPolicy.transact('updated privacy policy', {'from': other})
    privacy_policy = bond_token.privacyPolicy()
    assert privacy_policy == 'some_privacy_policy'


'''
TEST_個人情報記帳コントラクトの更新（setPersonalInfoAddress）
'''


# 正常系1: トークン発行 -> 更新
def test_setPersonalInfoAddress_normal_1(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 更新
    bond_token.setPersonalInfoAddress.transact('0x0000000000000000000000000000000000000000', {'from': issuer})

    assert bond_token.personalInfoAddress() == '0x0000000000000000000000000000000000000000'


# エラー系1: トークン発行 -> 更新（入力値の型誤り）
def test_setPersonalInfoAddress_error_1(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 更新
    with pytest.raises(ValueError):
        bond_token.setPersonalInfoAddress.transact('0xaaaa', {'from': issuer})


# エラー系2: トークン発行 -> 更新（権限エラー）
def test_setPersonalInfoAddress_error_2(users, bond_exchange, personal_info):
    attacker = users['trader']

    # 債券トークン新規発行
    bond_token, deploy_args = utils. \
        issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 更新
    bond_token.setPersonalInfoAddress.transact('0x0000000000000000000000000000000000000000', {'from': attacker})
    assert bond_token.personalInfoAddress() == to_checksum_address(personal_info.address)


'''
TEST_新規募集ステータス更新（setInitialOfferingStatus）
'''


# 正常系1: 発行 -> 新規募集ステータス更新（False→True）
def test_setInitialOfferingStatus_normal_1(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # トークン新規発行
    bond_token, deploy_args = \
        utils.issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 初期状態 == False
    assert bond_token.initialOfferingStatus() is False

    # 新規募集ステータスの更新
    bond_token.setInitialOfferingStatus.transact(True, {'from': issuer})

    assert bond_token.initialOfferingStatus() is True


# 正常系2:
#   発行 -> 新規募集ステータス更新（False→True） -> 2回目更新（True→False）
def test_setInitialOfferingStatus_normal_2(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # トークン新規発行
    bond_token, deploy_args = \
        utils.issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 新規募集ステータスの更新
    bond_token.setInitialOfferingStatus.transact(True, {'from': issuer})

    # 新規募集ステータスの更新（2回目）
    bond_token.setInitialOfferingStatus.transact(False, {'from': issuer})

    assert bond_token.initialOfferingStatus() is False


# エラー系1: 発行 -> 新規募集ステータス更新（入力値の型誤り）
def test_setInitialOfferingStatus_error_1(users, bond_exchange, personal_info):
    issuer = users['issuer']

    # トークン新規発行
    bond_token, deploy_args = \
        utils.issue_bond_token(users, bond_exchange.address, personal_info.address)

    # 新規募集ステータスの更新（エラー）：文字型
    with pytest.raises(ValueError):
        bond_token.setInitialOfferingStatus.transact('True', {'from': issuer})


'''
TEST_募集申込（applyForOffering）
'''


# 正常系1
#   発行：発行体 -> （申込なし）初期データ参照
def test_applyForOffering_normal_1(users):
    trader = users['trader']

    # トークン新規発行
    bond_token, deploy_args = \
        utils.issue_bond_token(users, zero_address, zero_address)

    application = bond_token.applications(trader)
    assert application[0] == 0
    assert application[1] == 0
    assert application[2] == ''


# 正常系2
#   発行：発行体 -> 投資家：募集申込
def test_applyForOffering_normal_2(users, personal_info):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    bond_token, deploy_args = \
        utils.issue_bond_token(users, zero_address, personal_info.address)

    # 新規募集ステータスの更新
    bond_token.setInitialOfferingStatus.transact(True, {'from': issuer})

    # 個人情報登録
    utils.register_personal_info(trader, personal_info, issuer)

    # 募集申込
    bond_token.applyForOffering.transact(10, 'abcdefgh', {'from': trader})

    application = bond_token.applications(trader)
    assert application[0] == 10
    assert application[1] == 0
    assert application[2] == 'abcdefgh'


# 正常系3
#   発行：発行体 -> 投資家：募集申込（複数回）
def test_applyForOffering_normal_3(users, personal_info):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    bond_token, deploy_args = \
        utils.issue_bond_token(users, zero_address, personal_info.address)

    # 新規募集ステータスの更新
    bond_token.setInitialOfferingStatus.transact(True, {'from': issuer})

    # 個人情報登録
    utils.register_personal_info(trader, personal_info, issuer)

    # 募集申込
    bond_token.applyForOffering.transact(10, 'abcdefgh', {'from': trader})

    # 募集申込：２回目
    bond_token.applyForOffering.transact(20, 'vwxyz', {'from': trader})

    application = bond_token.applications(trader)
    assert application[0] == 20
    assert application[1] == 0
    assert application[2] == 'vwxyz'


# エラー系1:
#   発行：発行体 -> 投資家：募集申込（入力値の型誤り）
def test_applyForOffering_error_1(users):
    trader = users['trader']

    # トークン新規発行
    bond_token, deploy_args = \
        utils.issue_bond_token(users, zero_address, zero_address)

    # 募集申込（エラー）：amount 文字型
    with pytest.raises(TypeError):
        bond_token.applyForOffering.transact("abc", "1234", {'from': trader})

    # 募集申込（エラー）：data 数値型
    with pytest.raises(ValueError):
        bond_token.applyForOffering.transact(10, '0x66aB6D9362d4F35596279692F0251Db635165871', {'from': trader})


# エラー系2:
#   発行：発行体 -> 投資家：募集申込（申込ステータスが停止中）
def test_applyForOffering_error_2(users):
    trader = users['trader']

    # トークン新規発行
    bond_token, deploy_args = \
        utils.issue_bond_token(users, zero_address, zero_address)

    # 募集申込（エラー）：募集申込ステータスFalse状態での申込
    bond_token.applyForOffering.transact(10, 'abcdefgh', {'from': trader})
    application = bond_token.applications(trader)
    assert application[0] == 0
    assert application[1] == 0
    assert application[2] == ''


# エラー系3
#   発行：発行体 -> 投資家：募集申込（個人情報未登録）
def test_applyForOffering_error_3(users, personal_info):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    bond_token, deploy_args = \
        utils.issue_bond_token(users, zero_address, personal_info.address)

    # 新規募集ステータスの更新
    bond_token.setInitialOfferingStatus.transact(True, {'from': issuer})

    # 個人情報未登録

    # 募集申込（エラーになる）
    bond_token.applyForOffering.transact(10, 'abcdefgh', {'from': trader})
    application = bond_token.applications(trader)
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
    bond_token, deploy_args = utils.issue_bond_token(users, zero_address, personal_info.address)

    # 新規募集ステータスの更新
    bond_token.setInitialOfferingStatus.transact(True, {'from': issuer})

    # 個人情報登録
    utils.register_personal_info(trader, personal_info, issuer)

    # 募集申込
    bond_token.applyForOffering.transact(10, 'abcdefgh', {'from': trader})

    # 割当
    bond_token.allot.transact(trader, 5, {'from': issuer})

    application = bond_token.applications(trader)
    assert application[0] == 10
    assert application[1] == 5
    assert application[2] == 'abcdefgh'


# エラー系1
#   発行：発行体 -> 投資家：募集申込 -> 発行体：募集割当（入力値の型誤り）
def test_allot_error_1(users):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    bond_token, deploy_args = utils.issue_bond_token(users, zero_address, zero_address)

    # 新規募集ステータスの更新
    bond_token.setInitialOfferingStatus.transact(True, {'from': issuer})

    # 割当（エラー）：address 数値型
    with pytest.raises(ValueError):
        bond_token.allot.transact(1234, 5, {'from': issuer})

    # 割当（エラー）：amount 文字型
    with pytest.raises(TypeError):
        bond_token.allot.transact(trader, "abc", {'from': issuer})


# エラー系2
#   発行：発行体 -> 投資家：募集申込 -> 発行体：募集割当（権限エラー）
def test_allot_error_2(users):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    bond_token, deploy_args = utils.issue_bond_token(users, zero_address, zero_address)

    # 新規募集ステータスの更新
    bond_token.setInitialOfferingStatus.transact(True, {'from': issuer})

    # 割当（エラー）：権限エラー
    bond_token.allot.transact(trader, 5, {'from': trader})
    application = bond_token.applications(trader)
    assert application[0] == 0
    assert application[1] == 0
    assert application[2] == ''


'''
TEST_追加発行（issue）
'''


# 正常系1: 発行 -> 追加発行
def test_issue_normal_1(users):
    issuer = users['issuer']
    value = 10

    # トークン新規発行
    bond_token, deploy_args = utils.issue_bond_token(users, zero_address, zero_address)

    # 追加発行
    bond_token.issue.transact(value, {'from': issuer})

    total_supply = bond_token.totalSupply()
    balance = bond_token.balanceOf(issuer)

    assert total_supply == deploy_args[2] + value
    assert balance == deploy_args[2] + value


# エラー系1: 入力値の型誤り
def test_issue_error_1(users):
    issuer = users['issuer']

    # トークン新規発行
    bond_token, deploy_args = utils.issue_bond_token(users, zero_address, zero_address)

    # String
    with pytest.raises(TypeError):
        bond_token.issue.transact("abc", {'from': issuer})


# エラー系2: 限界値超
def test_issue_error_2(users):
    issuer = users['issuer']

    # トークン新規発行
    bond_token, deploy_args = utils.issue_bond_token(users, zero_address, zero_address)

    # 上限値超
    with pytest.raises(OverflowError):
        bond_token.issue.transact(2 ** 256, {'from': issuer})

    # 下限値超
    with pytest.raises(OverflowError):
        bond_token.issue.transact(-1, {'from': issuer})


# エラー系3: 発行→追加発行→上限界値超
def test_issue_error_3(users):
    issuer = users['issuer']

    # トークン新規発行
    bond_token, deploy_args = utils.issue_bond_token(users, zero_address, zero_address)

    issue_amount = 2 ** 256 - deploy_args[2]

    # 追加発行（限界値超）
    bond_token.issue.transact(issue_amount, {'from': issuer})  # エラーになる

    total_supply = bond_token.totalSupply()
    balance = bond_token.balanceOf(issuer)

    assert total_supply == deploy_args[2]
    assert balance == deploy_args[2]


# エラー系4: 権限エラー
def test_issue_error_4(users):
    issuer = users['issuer']
    attacker = users['trader']

    # トークン新規発行
    bond_token, deploy_args = utils.issue_bond_token(users, zero_address, zero_address)

    # 追加発行：権限エラー
    bond_token.issue.transact(1, {'from': attacker})  # エラーになる

    total_supply = bond_token.totalSupply()
    balance = bond_token.balanceOf(issuer)

    assert total_supply == deploy_args[2]
    assert balance == deploy_args[2]
