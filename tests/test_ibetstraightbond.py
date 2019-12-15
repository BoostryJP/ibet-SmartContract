import pytest
import utils
from eth_utils import to_checksum_address


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
TEST1_デプロイ
'''


# 正常系1: deploy
def test_deploy_normal_1(web3, chain, users, bond_exchange, personal_info):
    account_address = users['issuer']
    deploy_args = init_args(bond_exchange.address, personal_info.address)

    web3.eth.defaultAccount = account_address
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args=deploy_args
    )

    owner_address = bond_contract.call().owner()
    name = bond_contract.call().name()
    symbol = bond_contract.call().symbol()
    total_supply = bond_contract.call().totalSupply()
    tradable_exchange = bond_contract.call().tradableExchange()
    face_value = bond_contract.call().faceValue()
    interest_rate = bond_contract.call().interestRate()
    interest_payment_date = bond_contract.call().interestPaymentDate()
    redemption_date = bond_contract.call().redemptionDate()
    redemption_value = bond_contract.call().redemptionValue()
    return_date = bond_contract.call().returnDate()
    return_amount = bond_contract.call().returnAmount()
    purpose = bond_contract.call().purpose()
    memo = bond_contract.call().memo()
    transferable = bond_contract.call().transferable()
    contact_information = bond_contract.call().contactInformation()
    privacy_policy = bond_contract.call().privacyPolicy()
    personal_info_address = bond_contract.call().personalInfoAddress()

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
def test_deploy_error_1(chain, bond_exchange, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[0] = 1234
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args=deploy_args)


# エラー系2: 入力値の型誤り（symbol）
def test_deploy_error_2(chain, bond_exchange, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[1] = 1234
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args=deploy_args)


# エラー系3: 入力値の型誤り（totalSupply）
def test_deploy_error_3(chain, bond_exchange, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[2] = "10000"
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args=deploy_args)


# エラー系4: 入力値の型誤り（faceValue）
def test_deploy_error_4(chain, bond_exchange, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[4] = "10000"
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args=deploy_args)


# エラー系5: 入力値の型誤り（interestRate）
def test_deploy_error_5(chain, bond_exchange, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[5] = "1000"
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args=deploy_args)


# エラー系6: 入力値の型誤り（interestPaymentDate）
def test_deploy_error_6(chain, bond_exchange, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[6] = 1231
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args=deploy_args)


# エラー系7: 入力値の型誤り（redemptionDate）
def test_deploy_error_7(chain, bond_exchange, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[7] = 20191231
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args=deploy_args)


# エラー系8: 入力値の型誤り（redemptionValue）
def test_deploy_error_8(chain, bond_exchange, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[8] = "100"
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args=deploy_args)


# エラー系9: 入力値の型誤り（returnDate）
def test_deploy_error_9(chain, bond_exchange, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[9] = 20191231
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args=deploy_args)


# エラー系10: 入力値の型誤り（returnAmount）
def test_deploy_error_10(chain, bond_exchange, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[10] = 1234
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args=deploy_args)


# エラー系11: 入力値の型誤り（purpose）
def test_deploy_error_11(chain, bond_exchange, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[11] = 1234
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args=deploy_args)


# エラー系12: 入力値の型誤り（memo）
def test_deploy_error_12(chain, bond_exchange, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[12] = 1234
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args=deploy_args)


# エラー系13: 入力値の型誤り（tradableExchange）
def test_deploy_error_13(chain, bond_exchange, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[3] = '0xaaaa'
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args=deploy_args)


# エラー系14: 入力値の型誤り（contactInformation）
def test_deploy_error_14(chain, bond_exchange, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[13] = 1234
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args=deploy_args)


# エラー系15: 入力値の型誤り（privacyPolicy）
def test_deploy_error_15(chain, bond_exchange, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[14] = 1234
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args=deploy_args)


# エラー系16: 入力値の型誤り（personalInfoAddress）
def test_deploy_error_16(chain, bond_exchange, personal_info):
    deploy_args = init_args(bond_exchange.address, personal_info.address)
    deploy_args[15] = '0xaaaa'
    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args=deploy_args)


'''
TEST2_譲渡可能更新（setTransferable）
'''


# 正常系1: 発行 -> 譲渡可能更新
def test_setTransferable_normal_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    after_transferable = False

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_contract, deploy_args = \
        utils.issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 譲渡可能更新
    web3.eth.defaultAccount = issuer
    txn_hash = bond_contract.transact().setTransferable(after_transferable)
    chain.wait.for_receipt(txn_hash)

    transferable = bond_contract.call().transferable()
    assert after_transferable == transferable


# エラー系1: 入力値の型誤り
def test_setTransferable_error_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_contract, deploy_args = \
        utils.issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 型誤り
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        bond_contract.transact().setTransferable('False')


# エラー系2: 権限エラー
def test_setTransferable_error_2(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    attacker = users['trader']
    after_transferable = False

    # 新規発行
    web3.eth.defaultAccount = issuer
    bond_contract, deploy_args = \
        utils.issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 譲渡可能更新
    web3.eth.defaultAccount = attacker
    txn_hash = bond_contract.transact().setTransferable(after_transferable)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    transferable = bond_contract.call().transferable()
    assert transferable == True


'''
TEST3_トークンの振替（transfer）
'''


# 正常系1: アカウントアドレスへの振替
def test_transfer_normal_1(web3, chain, users, bond_exchange, personal_info):
    from_address = users['issuer']
    to_address = users['trader']
    transfer_amount = 100

    # 債券トークン新規発行
    web3.eth.defaultAccount = from_address
    bond_contract, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 振替先の個人情報登録
    web3.eth.defaultAccount = to_address
    utils.register_personal_info(chain, personal_info, from_address)

    # 振替
    web3.eth.defaultAccount = from_address
    txn_hash = bond_contract.transact().transfer(to_address, transfer_amount)
    chain.wait.for_receipt(txn_hash)

    from_balance = bond_contract.call().balanceOf(from_address)
    to_balance = bond_contract.call().balanceOf(to_address)

    assert from_balance == deploy_args[2] - transfer_amount
    assert to_balance == transfer_amount


# 正常系2: 債券取引コントラクトへの振替
def test_transfer_normal_2(web3, chain, users, bond_exchange, personal_info):
    from_address = users['issuer']
    transfer_amount = 100

    # 債券トークン新規発行
    web3.eth.defaultAccount = from_address
    bond_contract, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    to_address = bond_exchange.address
    txn_hash = bond_contract.transact().transfer(to_address, transfer_amount)
    chain.wait.for_receipt(txn_hash)

    from_balance = bond_contract.call().balanceOf(from_address)
    to_balance = bond_contract.call().balanceOf(to_address)

    assert from_balance == deploy_args[2] - transfer_amount
    assert to_balance == transfer_amount


# エラー系1: 入力値の型誤り（To）
def test_transfer_error_1(web3, chain, users, bond_exchange, personal_info):
    from_address = users['issuer']
    to_address = 1234
    transfer_amount = 100

    # 債券トークン新規発行
    web3.eth.defaultAccount = from_address
    bond_contract, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    with pytest.raises(TypeError):
        bond_contract.transact().transfer(to_address, transfer_amount)


# エラー系2: 入力値の型誤り（Value）
def test_transfer_error_2(web3, chain, users, bond_exchange, personal_info):
    from_address = users['issuer']
    to_address = users['trader']
    transfer_amount = '100'

    # 債券トークン新規発行
    web3.eth.defaultAccount = from_address
    bond_contract, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    with pytest.raises(TypeError):
        bond_contract.transact().transfer(to_address, transfer_amount)


# エラー系3: 残高不足
def test_transfer_error_3(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    from_address = issuer
    to_address = users['trader']

    # 債券トークン新規発行
    web3.eth.defaultAccount = from_address
    bond_contract, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 個人情報登録
    web3.eth.defaultAccount = to_address
    utils.register_personal_info(chain, personal_info, from_address)

    # 債券トークン振替（残高超）
    web3.eth.defaultAccount = issuer
    transfer_amount = 10000000000
    bond_contract.transact().transfer(to_address, transfer_amount)

    assert bond_contract.call().balanceOf(issuer) == 10000
    assert bond_contract.call().balanceOf(to_address) == 0


# エラー系4: private functionにアクセスできない
def test_transfer_error_4(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    from_address = issuer
    to_address = users['trader']

    transfer_amount = 100
    data = 0

    # 債券トークン新規発行
    web3.eth.defaultAccount = from_address
    bond_contract, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    with pytest.raises(ValueError):
        bond_contract.call().isContract(to_address)

    with pytest.raises(ValueError):
        bond_contract.transact().transferToAddress(to_address, transfer_amount, data)

    with pytest.raises(ValueError):
        bond_contract.transact().transferToContract(to_address, transfer_amount, data)


# エラー系5: 取引不可Exchangeへの振替
def test_transfer_error_5(web3, chain, users, bond_exchange, personal_info,
                          coupon_exchange_storage, payment_gateway):
    from_address = users['issuer']
    transfer_amount = 100

    # 債券トークン新規発行
    web3.eth.defaultAccount = from_address
    bond_contract, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 取引不可Exchange
    web3.eth.defaultAccount = users['admin']
    dummy_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetCouponExchange',  # IbetStraightBondExchange以外を読み込む必要がある
        deploy_args=[
            payment_gateway.address,
            coupon_exchange_storage.address
        ]
    )

    to_address = dummy_exchange.address
    txn_hash = bond_contract.transact().transfer(to_address, transfer_amount)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    from_balance = bond_contract.call().balanceOf(from_address)
    to_balance = bond_contract.call().balanceOf(to_address)

    assert from_balance == deploy_args[2]
    assert to_balance == 0


# エラー系6: 譲渡不可トークンの振替
def test_transfer_error_6(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    to_address = users['trader']
    transfer_amount = 100

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_contract, deploy_args = \
        utils.issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 個人情報登録
    web3.eth.defaultAccount = to_address
    utils.register_personal_info(chain, personal_info, issuer)

    # 譲渡不可設定
    web3.eth.defaultAccount = issuer
    txn_hash = bond_contract.transact().setTransferable(False)
    chain.wait.for_receipt(txn_hash)

    # 譲渡実行
    web3.eth.defaultAccount = issuer
    txn_hash = bond_contract.transact().transfer(to_address, transfer_amount)  # エラーとなる
    chain.wait.for_receipt(txn_hash)

    from_balance = bond_contract.call().balanceOf(issuer)
    to_balance = bond_contract.call().balanceOf(to_address)

    assert from_balance == deploy_args[2]
    assert to_balance == 0


# エラー系7: 個人情報未登録アドレスへの振替
def test_transfer_error_7(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    to_address = users['trader']
    transfer_amount = 100

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_contract, deploy_args = \
        utils.issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # NOTE:個人情報未登録（to_address）

    # 譲渡実行
    web3.eth.defaultAccount = issuer
    txn_hash = bond_contract.transact().transfer(to_address, transfer_amount)  # エラーとなる
    chain.wait.for_receipt(txn_hash)

    from_balance = bond_contract.call().balanceOf(issuer)
    to_balance = bond_contract.call().balanceOf(to_address)

    assert from_balance == deploy_args[2]
    assert to_balance == 0


'''
TEST4_残高確認（balanceOf）
'''


# 正常系1: 商品コントラクト作成 -> 残高確認
def test_balanceOf_normal_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    balance = bond_token.call().balanceOf(issuer)
    assert balance == 10000


# エラー系1: 入力値の型誤り（Owner）
def test_balanceOf_error_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    account_address = 1234

    with pytest.raises(TypeError):
        bond_token.call().balanceOf(account_address)


'''
TEST5_認定リクエスト（requestSignature）
'''


# 正常系1: 初期値が0
def test_requestSignature_normal_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    signer = users['admin']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    signature = bond_token.call().signatures(signer)
    assert signature == 0


# 正常系2: 認定リクエスト
def test_requestSignature_normal_2(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    signer = users['admin']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    txn_hash = bond_token.transact().requestSignature(signer)
    chain.wait.for_receipt(txn_hash)

    signature = bond_token.call().signatures(signer)
    assert signature == 1


# エラー系1: 入力値の型誤り（Signer）
def test_requestSignature_error_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    signer = 1234

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    with pytest.raises(TypeError):
        bond_token.transact().requestSignature(signer)


'''
TEST6_認定（sign）
'''


# 正常系1: 認定リクエスト -> 認定
def test_sign_normal_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    signer = users['admin']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 認定リクエスト -> Success
    web3.eth.defaultAccount = issuer
    txn_hash_1 = bond_token.transact().requestSignature(signer)
    chain.wait.for_receipt(txn_hash_1)

    # 認定 -> Success
    web3.eth.defaultAccount = signer
    txn_hash_2 = bond_token.transact().sign()
    chain.wait.for_receipt(txn_hash_2)

    signature = bond_token.call().signatures(signer)
    assert signature == 2


# エラー系1: 認定リクエスト未実施 -> 認定
def test_sign_error_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    signer = users['admin']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 認定 -> Failure
    web3.eth.defaultAccount = signer
    bond_token.transact().sign()

    signature = bond_token.call().signatures(signer)
    assert signature == 0


# エラー系2: 認定リクエスト-> 異なるSinerから認定をした場合
def test_sign_error_2(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    signer = users['admin']
    signer_other = users['trader']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 認定リクエスト -> Success
    web3.eth.defaultAccount = issuer
    txn_hash_1 = bond_token.transact().requestSignature(signer)
    chain.wait.for_receipt(txn_hash_1)

    # 異なるSignerが認定 -> Failure
    web3.eth.defaultAccount = signer_other
    txn_hash_2 = bond_token.transact().sign()
    chain.wait.for_receipt(txn_hash_2)

    signature = bond_token.call().signatures(signer)
    assert signature == 1


'''
TEST7_認定取消（unsign）
'''


# 正常系1: 認定リクエスト -> 認定 -> 認定取消
def test_unsign_normal_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    signer = users['admin']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 認定リクエスト -> Success
    web3.eth.defaultAccount = issuer
    txn_hash_1 = bond_token.transact().requestSignature(signer)
    chain.wait.for_receipt(txn_hash_1)

    # 認定 -> Success
    web3.eth.defaultAccount = signer
    txn_hash_2 = bond_token.transact().sign()
    chain.wait.for_receipt(txn_hash_2)

    # 認定取消 -> Success
    web3.eth.defaultAccount = signer
    txn_hash_3 = bond_token.transact().unsign()
    chain.wait.for_receipt(txn_hash_3)

    signature = bond_token.call().signatures(signer)
    assert signature == 0


# エラー系1: 認定リクエスト未実施 -> 認定取消
def test_unsign_error_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    signer = users['admin']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 認定取消 -> Failure
    web3.eth.defaultAccount = signer
    txn_hash = bond_token.transact().unsign()
    chain.wait.for_receipt(txn_hash)

    signature = bond_token.call().signatures(signer)
    assert signature == 0


# エラー系2: 認定リクエスト -> （認定未実施） -> 認定取消
def test_unsign_error_2(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    signer = users['admin']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 認定リクエスト -> Success
    web3.eth.defaultAccount = issuer
    txn_hash_1 = bond_token.transact().requestSignature(signer)
    chain.wait.for_receipt(txn_hash_1)

    # 認定取消 -> Failure
    web3.eth.defaultAccount = signer
    txn_hash_2 = bond_token.transact().unsign()
    chain.wait.for_receipt(txn_hash_2)

    signature = bond_token.call().signatures(signer)
    assert signature == 1


# エラー系3: 認定リクエスト-> 認定 -> 異なるSinerから認定取消を実施した場合
def test_unsign_error_3(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    signer = users['admin']
    signer_other = users['trader']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 認定リクエスト -> Success
    web3.eth.defaultAccount = issuer
    txn_hash_1 = bond_token.transact().requestSignature(signer)
    chain.wait.for_receipt(txn_hash_1)

    # 認定 -> Success
    web3.eth.defaultAccount = signer
    txn_hash_2 = bond_token.transact().sign()
    chain.wait.for_receipt(txn_hash_2)

    # 異なるSignerが認定取消を実施 -> Failure
    web3.eth.defaultAccount = signer_other
    txn_hash_3 = bond_token.transact().unsign()
    chain.wait.for_receipt(txn_hash_3)

    signature = bond_token.call().signatures(signer)
    assert signature == 2


'''
TEST8_償還（redeem）
'''


# 正常系1: 発行（デプロイ） -> 償還
def test_redeem_normal_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 償還 -> Success
    web3.eth.defaultAccount = issuer
    txn_hash = bond_token.transact().redeem()
    chain.wait.for_receipt(txn_hash)

    is_redeemed = bond_token.call().isRedeemed()
    assert is_redeemed is True


# エラー系1: issuer以外のアドレスから償還を実施した場合
def test_redeem_error_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    other = users['admin']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils.issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Owner以外のアドレスから償還を実施 -> Failure
    web3.eth.defaultAccount = other
    txn_hash = bond_token.transact().redeem()
    chain.wait.for_receipt(txn_hash)

    is_redeemed = bond_token.call().isRedeemed()
    assert is_redeemed is False


'''
TEST9_商品画像の設定（setImageURL, getImageURL）
'''


# 正常系1: 発行（デプロイ） -> 商品画像の設定
def test_setImageURL_normal_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    image_url = 'https://some_image_url.com/image.png'

    # 商品画像の設定 -> Success
    web3.eth.defaultAccount = issuer
    txn_hash = bond_token.transact().setImageURL(0, image_url)
    chain.wait.for_receipt(txn_hash)

    image_url_0 = bond_token.call().getImageURL(0)
    assert image_url_0 == image_url


# 正常系2: 発行（デプロイ） -> 商品画像の設定（複数設定）
def test_setImageURL_normal_2(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    image_url = 'https://some_image_url.com/image.png'

    # 商品画像の設定（1つ目） -> Success
    web3.eth.defaultAccount = issuer
    txn_hash_1 = bond_token.transact().setImageURL(0, image_url)
    chain.wait.for_receipt(txn_hash_1)

    # 商品画像の設定（2つ目） -> Success
    web3.eth.defaultAccount = issuer
    txn_hash_2 = bond_token.transact().setImageURL(1, image_url)
    chain.wait.for_receipt(txn_hash_2)

    image_url_0 = bond_token.call().getImageURL(0)
    image_url_1 = bond_token.call().getImageURL(1)
    assert image_url_0 == image_url
    assert image_url_1 == image_url


# 正常系3: 発行（デプロイ） -> 商品画像の設定（上書き登録）
def test_setImageURL_normal_3(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    image_url = 'https://some_image_url.com/image.png'
    image_url_after = 'https://some_image_url.com/image_after.png'

    # 商品画像の設定（1回目） -> Success
    web3.eth.defaultAccount = issuer
    txn_hash_1 = bond_token.transact().setImageURL(0, image_url)
    chain.wait.for_receipt(txn_hash_1)

    # 商品画像の設定（2回目：上書き） -> Success
    web3.eth.defaultAccount = issuer
    txn_hash_2 = bond_token.transact().setImageURL(0, image_url_after)
    chain.wait.for_receipt(txn_hash_2)

    image_url_0 = bond_token.call().getImageURL(0)
    assert image_url_0 == image_url_after


# エラー系1: 入力値の型誤り（Class）
def test_setImageURL_error_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    image_url = 'https://some_image_url.com/image.png'

    web3.eth.defaultAccount = issuer

    with pytest.raises(TypeError):
        bond_token.transact().setImageURL(-1, image_url)

    with pytest.raises(TypeError):
        bond_token.transact().setImageURL(256, image_url)

    with pytest.raises(TypeError):
        bond_token.transact().setImageURL('0', image_url)


# エラー系2: 入力値の型誤り（ImageURL）
def test_setImageURL_error_2(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    image_url = 1234

    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        bond_token.transact().setImageURL(0, image_url)


# エラー系3: Issuer以外のアドレスから画像設定を実施した場合
def test_setImageURL_error_3(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    other = users['admin']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    image_url = 'https://some_image_url.com/image.png'

    # Owner以外のアドレスから画像設定を実施 -> Failure
    web3.eth.defaultAccount = other
    txn_hash = bond_token.transact().setImageURL(0, image_url)
    chain.wait.for_receipt(txn_hash)

    image_url_0 = bond_token.call().getImageURL(0)
    assert image_url_0 == ''


'''
TEST10_メモの更新（updateMemo）
'''


# 正常系1: 発行（デプロイ） -> メモ欄の修正
def test_updateMemo_normal_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # メモ欄の修正 -> Success
    web3.eth.defaultAccount = issuer
    txn_hash = bond_token.transact().updateMemo('updated memo')
    chain.wait.for_receipt(txn_hash)

    memo = bond_token.call().memo()
    assert memo == 'updated memo'


# エラー系1: 入力値の型誤り
def test_updateMemo_error_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        bond_token.transact().updateMemo(1234)


# エラー系2: Owner以外のアドレスからメモ欄の修正を実施した場合
def test_updateMemo_error_2(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    other = users['admin']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Owner以外のアドレスからメモ欄の修正を実施 -> Failure
    web3.eth.defaultAccount = other
    bond_token.transact().updateMemo('updated memo')

    memo = bond_token.call().memo()
    assert memo == 'some_memo'


'''
TEST11_トークンの移転（transferFrom）
'''


# 正常系1: アカウントアドレスへの移転
def test_transferFrom_normal_1(web3, chain, users, bond_exchange, personal_info):
    _issuer = users['issuer']
    _from = users['admin']
    _to = users['trader']
    _value = 100

    # 債券トークン新規発行
    web3.eth.defaultAccount = _issuer
    bond_contract, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 振替先の個人情報登録（_from）
    web3.eth.defaultAccount = _from
    utils.register_personal_info(chain, personal_info, _issuer)

    # 譲渡（issuer -> _from）
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_contract.transact().transfer(_from, _value)
    chain.wait.for_receipt(txn_hash)

    # 移転（_from -> _to）
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_contract.transact().transferFrom(_from, _to, _value)
    chain.wait.for_receipt(txn_hash)

    issuer_balance = bond_contract.call().balanceOf(_issuer)
    from_balance = bond_contract.call().balanceOf(_from)
    to_balance = bond_contract.call().balanceOf(_to)

    assert issuer_balance == deploy_args[2] - _value
    assert from_balance == 0
    assert to_balance == _value


# エラー系1: 入力値の型誤り（From）
def test_transferFrom_error_1(web3, chain, users, bond_exchange, personal_info):
    _issuer = users['issuer']
    _to = users['trader']
    _value = 100

    # 債券トークン新規発行
    web3.eth.defaultAccount = _issuer
    bond_contract, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 移転（_from -> _to）
    web3.eth.defaultAccount = _issuer

    with pytest.raises(TypeError):
        bond_contract.transact().transferFrom('1234', _to, _value)

    with pytest.raises(TypeError):
        bond_contract.transact().transferFrom(1234, _to, _value)


# エラー系2: 入力値の型誤り（To）
def test_transferFrom_error_2(web3, chain, users, bond_exchange, personal_info):
    _issuer = users['issuer']
    _from = users['admin']
    _value = 100

    # 債券トークン新規発行
    web3.eth.defaultAccount = _issuer
    bond_contract, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 移転（_from -> _to）
    web3.eth.defaultAccount = _issuer

    with pytest.raises(TypeError):
        bond_contract.transact().transferFrom(_from, '1234', _value)

    with pytest.raises(TypeError):
        bond_contract.transact().transferFrom(_from, 1234, _value)


# エラー系3: 入力値の型誤り（Value）
def test_transferFrom_error_3(web3, chain, users, bond_exchange, personal_info):
    _issuer = users['issuer']
    _from = users['admin']
    _to = users['trader']

    # 債券トークン新規発行
    web3.eth.defaultAccount = _issuer
    bond_contract, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 移転（_from -> _to）
    web3.eth.defaultAccount = _issuer

    with pytest.raises(TypeError):
        bond_contract.transact().transferFrom(_from, _to, -1)

    with pytest.raises(TypeError):
        bond_contract.transact().transferFrom(_from, _to, 2 ** 256)

    with pytest.raises(TypeError):
        bond_contract.transact().transferFrom(_from, _to, '0')

    with pytest.raises(TypeError):
        bond_contract.transact().transferFrom(_from, _to, 0.1)


# エラー系4: 残高不足
def test_transferFrom_error_4(web3, chain, users, bond_exchange, personal_info):
    _issuer = users['issuer']
    _from = users['admin']
    _to = users['trader']
    _value = 100

    # 債券トークン新規発行
    web3.eth.defaultAccount = _issuer
    bond_contract, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 振替先の個人情報登録（_from）
    web3.eth.defaultAccount = _from
    utils.register_personal_info(chain, personal_info, _issuer)

    # 譲渡（issuer -> _from）
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_contract.transact().transfer(_from, _value)
    chain.wait.for_receipt(txn_hash)

    # 移転（_from -> _to）
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_contract.transact().transferFrom(_from, _to, 101)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    issuer_balance = bond_contract.call().balanceOf(_issuer)
    from_balance = bond_contract.call().balanceOf(_from)
    to_balance = bond_contract.call().balanceOf(_to)

    assert issuer_balance == deploy_args[2] - _value
    assert from_balance == _value
    assert to_balance == 0


# エラー系5: 権限エラー
def test_transferFrom_error_5(web3, chain, users, bond_exchange, personal_info):
    _issuer = users['issuer']
    _from = users['admin']
    _to = users['trader']
    _value = 100

    # 債券トークン新規発行
    web3.eth.defaultAccount = _issuer
    bond_contract, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 振替先の個人情報登録（_from）
    web3.eth.defaultAccount = _from
    utils.register_personal_info(chain, personal_info, _issuer)

    # 譲渡（issuer -> _from）
    web3.eth.defaultAccount = _issuer
    txn_hash = bond_contract.transact().transfer(_from, _value)
    chain.wait.for_receipt(txn_hash)

    # 移転（_from -> _to）
    web3.eth.defaultAccount = _from
    txn_hash = bond_contract.transact().transferFrom(_from, _to, _value)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    issuer_balance = bond_contract.call().balanceOf(_issuer)
    from_balance = bond_contract.call().balanceOf(_from)
    to_balance = bond_contract.call().balanceOf(_to)

    assert issuer_balance == deploy_args[2] - _value
    assert from_balance == _value
    assert to_balance == 0


'''
TEST12_取引可能Exchangeの更新（setTradableExchange）
'''


# 正常系1: 発行 -> Exchangeの更新
def test_setTradableExchange_normal_1(web3, chain, users, bond_exchange, personal_info,
                                      coupon_exchange_storage, payment_gateway):
    issuer = users['issuer']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # その他Exchange
    web3.eth.defaultAccount = users['admin']
    other_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetCouponExchange',  # IbetStraightBondExchange以外を読み込む必要がある
        deploy_args=[
            payment_gateway.address,
            coupon_exchange_storage.address
        ]
    )

    # Exchangeの更新
    web3.eth.defaultAccount = issuer
    txn_hash = bond_token.transact().setTradableExchange(other_exchange.address)
    chain.wait.for_receipt(txn_hash)

    assert bond_token.call().tradableExchange() == to_checksum_address(other_exchange.address)


# エラー系1: 発行 -> Exchangeの更新（入力値の型誤り）
def test_setTradableExchange_error_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Exchangeの更新
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        bond_token.transact().setTradableExchange('0xaaaa')


# エラー系2: 発行 -> Exchangeの更新（権限エラー）
def test_setTradableExchange_error_2(web3, chain, users, bond_exchange, personal_info,
                                     coupon_exchange_storage, payment_gateway):
    issuer = users['issuer']
    trader = users['trader']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # その他Exchange
    web3.eth.defaultAccount = users['admin']
    other_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetCouponExchange',  # IbetStraightBondExchange以外を読み込む必要がある
        deploy_args=[
            payment_gateway.address,
            coupon_exchange_storage.address
        ]
    )

    # Exchangeの更新
    web3.eth.defaultAccount = trader
    txn_hash = bond_token.transact(). \
        setTradableExchange(other_exchange.address)  # エラーになる
    chain.wait.for_receipt(txn_hash)

    assert bond_token.call().tradableExchange() == to_checksum_address(bond_exchange.address)


'''
TEST13_問い合わせ先情報の更新（setContactInformation）
'''


# 正常系1: 発行（デプロイ） -> 修正
def test_setContactInformation_normal_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 修正 -> Success
    web3.eth.defaultAccount = issuer
    txn_hash = bond_token.transact().setContactInformation('updated contact information')
    chain.wait.for_receipt(txn_hash)

    contact_information = bond_token.call().contactInformation()
    assert contact_information == 'updated contact information'


# エラー系1: 入力値の型誤り
def test_setContactInformation_error_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        bond_token.transact().setContactInformation(1234)


# エラー系2: 権限エラー
def test_setContactInformation_error_2(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    other = users['admin']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Owner以外のアドレスから更新 -> Failure
    web3.eth.defaultAccount = other
    bond_token.transact().setContactInformation('updated contact information')

    contact_information = bond_token.call().contactInformation()
    assert contact_information == 'some_contact_information'


'''
TEST14_プライバシーポリシーの更新（setPrivacyPolicy）
'''


# 正常系1: 発行（デプロイ） -> 修正
def test_setPrivacyPolicy_normal_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 修正 -> Success
    web3.eth.defaultAccount = issuer
    txn_hash = bond_token.transact().setPrivacyPolicy('updated privacy policy')
    chain.wait.for_receipt(txn_hash)

    privacy_policy = bond_token.call().privacyPolicy()
    assert privacy_policy == 'updated privacy policy'


# エラー系1: 入力値の型誤り
def test_setPrivacyPolicy_error_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        bond_token.transact().setPrivacyPolicy(1234)


# エラー系2: 権限エラー
def test_setPrivacyPolicy_error_2(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    other = users['admin']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # Owner以外のアドレスから更新 -> Failure
    web3.eth.defaultAccount = other
    bond_token.transact().setPrivacyPolicy('updated privacy policy')

    privacy_policy = bond_token.call().privacyPolicy()
    assert privacy_policy == 'some_privacy_policy'


'''
TEST15_個人情報記帳コントラクトの更新（setPersonalInfoAddress）
'''


# 正常系1: トークン発行 -> 更新
def test_setPersonalInfoAddress_normal_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 更新
    web3.eth.defaultAccount = issuer
    txn_hash = bond_token.transact().setPersonalInfoAddress('0x0000000000000000000000000000000000000000')
    chain.wait.for_receipt(txn_hash)

    assert bond_token.call().personalInfoAddress() == '0x0000000000000000000000000000000000000000'


# エラー系1: トークン発行 -> 更新（入力値の型誤り）
def test_setPersonalInfoAddress_error_1(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 更新
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        bond_token.transact().setPersonalInfoAddress('0xaaaa')


# エラー系2: トークン発行 -> 更新（権限エラー）
def test_setPersonalInfoAddress_error_2(web3, chain, users, bond_exchange, personal_info):
    issuer = users['issuer']
    attacker = users['trader']

    # 債券トークン新規発行
    web3.eth.defaultAccount = issuer
    bond_token, deploy_args = utils. \
        issue_bond_token(web3, chain, users, bond_exchange.address, personal_info.address)

    # 更新
    web3.eth.defaultAccount = attacker
    txn_hash = bond_token.transact().setPersonalInfoAddress('0x0000000000000000000000000000000000000000')
    chain.wait.for_receipt(txn_hash)

    assert bond_token.call().personalInfoAddress() == to_checksum_address(personal_info.address)
