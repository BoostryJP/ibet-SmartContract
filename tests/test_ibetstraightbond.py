import pytest
from ethereum.tester import TransactionFailed

def init_args():
    name = 'test_bond'
    symbol = 'BND'
    total_supply = 10000
    face_value = 10000
    interest_rate = 1000
    interest_payment_date = '{"interestPaymentDate1":"0331","interestPaymentDate2":"0930"}'
    redemption_date = '20191231'
    redemption_amount = 100
    return_date = '20191231'
    return_amount = 'some_return'
    purpose = 'some_purpose'
    memo = 'some_memo'

    deploy_args = [
        name, symbol, total_supply, face_value,
        interest_rate, interest_payment_date, redemption_date,
        redemption_amount, return_date, return_amount,
        purpose, memo
    ]
    return deploy_args

'''
TEST1_デプロイ
'''

# 正常系1: deploy
def test_deploy_normal_1(web3,chain):
    account_address = web3.eth.accounts[0]

    deploy_args = init_args()

    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    owner_address = bond_contract.call().owner()
    name = bond_contract.call().name()
    symbol = bond_contract.call().symbol()
    total_supply = bond_contract.call().totalSupply()
    face_value = bond_contract.call().faceValue()
    interest_rate = bond_contract.call().interestRate()
    interest_payment_date = bond_contract.call().interestPaymentDate()
    redemption_date = bond_contract.call().redemptionDate()
    redemption_amount = bond_contract.call().redemptionAmount()
    return_date = bond_contract.call().returnDate()
    return_amount = bond_contract.call().returnAmount()
    purpose = bond_contract.call().purpose()
    memo = bond_contract.call().memo()

    assert owner_address == account_address
    assert name == deploy_args[0]
    assert symbol == deploy_args[1]
    assert total_supply == deploy_args[2]
    assert face_value == deploy_args[3]
    assert interest_rate == deploy_args[4]
    assert interest_payment_date == deploy_args[5]
    assert redemption_date == deploy_args[6]
    assert redemption_amount == deploy_args[7]
    assert return_date == deploy_args[8]
    assert return_amount == deploy_args[9]
    assert purpose == deploy_args[10]
    assert memo == deploy_args[11]


# エラー系1: 入力値の型誤り（name）
def test_deploy_error_1(chain):
    deploy_args = init_args()
    deploy_args[0] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args = deploy_args)


# エラー系2: 入力値の型誤り（symbol）
def test_deploy_error_2(chain):
    deploy_args = init_args()
    deploy_args[1] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args = deploy_args)


# エラー系3: 入力値の型誤り（totalSupply）
def test_deploy_error_3(chain):
    deploy_args = init_args()
    deploy_args[2] = "10000"

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args = deploy_args)


# エラー系4: 入力値の型誤り（faceValue）
def test_deploy_error_4(chain):
    deploy_args = init_args()
    deploy_args[3] = "10000"

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args = deploy_args)


# エラー系5: 入力値の型誤り（interestRate）
def test_deploy_error_5(chain):
    deploy_args = init_args()
    deploy_args[4] = "1000"

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args = deploy_args)


# エラー系6: 入力値の型誤り（interestPaymentDate）
def test_deploy_error_6(chain):
    deploy_args = init_args()
    deploy_args[5] = 1231

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args = deploy_args)


# エラー系7: 入力値の型誤り（redemptionDate）
def test_deploy_error_7(chain):
    deploy_args = init_args()
    deploy_args[6] = 20191231

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args = deploy_args)


# エラー系8: 入力値の型誤り（redemptionAmount）
def test_deploy_error_8(chain):
    deploy_args = init_args()
    deploy_args[7] = "100"

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args = deploy_args)


# エラー系9: 入力値の型誤り（returnDate）
def test_deploy_error_9(chain):
    deploy_args = init_args()
    deploy_args[8] = 20191231

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args = deploy_args)


# エラー系10: 入力値の型誤り（returnAmount）
def test_deploy_error_10(chain):
    deploy_args = init_args()
    deploy_args[9] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args = deploy_args)


# エラー系11: 入力値の型誤り（purpose）
def test_deploy_error_11(chain):
    deploy_args = init_args()
    deploy_args[10] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args = deploy_args)


# エラー系12: 入力値の型誤り（memo）
def test_deploy_error_12(chain):
    deploy_args = init_args()
    deploy_args[11] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract('IbetStraightBond', deploy_args = deploy_args)


'''
TEST2_トークンの振替（transfer）
'''

# 正常系1: アカウントアドレスへの振替
def test_transfer_normal_1(web3,chain):
    from_address = web3.eth.accounts[0]
    to_address = web3.eth.accounts[1]
    transfer_amount = 100

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    txn_hash = bond_contract.transact().transfer(to_address, transfer_amount)
    chain.wait.for_receipt(txn_hash)

    from_balance = bond_contract.call().balanceOf(from_address)
    to_balance = bond_contract.call().balanceOf(to_address)

    assert from_balance == deploy_args[2] - transfer_amount
    assert to_balance == transfer_amount


# 正常系2: 債券取引コントラクトへの振替
def test_transfer_normal_2(web3,chain):
    from_address = web3.eth.accounts[0]
    transfer_amount = 100

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    personalinfo_contract, _ = chain.provider.get_or_deploy_contract('PersonalInfo')
    whitelist_contract, _ = chain.provider.get_or_deploy_contract('WhiteList')

    exchange_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBondExchange',
        deploy_transaction = {'gas':5500000},
        deploy_args = [
            whitelist_contract.address,
            personalinfo_contract.address,
        ]
    )

    to_address = exchange_contract.address
    txn_hash = bond_contract.transact().transfer(to_address, transfer_amount)
    chain.wait.for_receipt(txn_hash)

    from_balance = bond_contract.call().balanceOf(from_address)
    to_balance = bond_contract.call().balanceOf(to_address)

    assert from_balance == deploy_args[2] - transfer_amount
    assert to_balance == transfer_amount


# エラー系1: 入力値の型誤り（To）
def test_transfer_error_1(chain):
    to_address = 1234
    transfer_amount = 100

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    with pytest.raises(TypeError):
        bond_contract.transact().transfer(to_address, transfer_amount)


# エラー系2: 入力値の型誤り（Value）
def test_transfer_error_2(web3,chain):
    to_address = web3.eth.accounts[1]
    transfer_amount = '100'

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    with pytest.raises(TypeError):
        bond_contract.transact().transfer(to_address, transfer_amount)


# エラー系3: 残高不足
def test_transfer_error_3(web3,chain):
    from_address = web3.eth.accounts[0]
    to_address = web3.eth.accounts[1]
    transfer_amount = 10000000000

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    with pytest.raises(TransactionFailed):
        bond_contract.transact().transfer(to_address, transfer_amount)


# エラー系4: private functionにアクセスできない
def test_transfer_error_4(web3,chain):
    from_address = web3.eth.accounts[0]
    to_address = web3.eth.accounts[1]
    transfer_amount = 100
    data = 0

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    with pytest.raises(ValueError):
        bond_contract.call().isContract(to_address)

    with pytest.raises(ValueError):
        bond_contract.transact().transferToAddress(to_address, transfer_amount, data)

    with pytest.raises(ValueError):
        bond_contract.transact().transferToContract(to_address, transfer_amount, data)


'''
TEST3_残高確認（balanceOf）
'''

# 正常系1: 商品コントラクト作成 -> 残高確認
def test_balanceOf_normal_1(web3,chain):
    account_address = web3.eth.accounts[0]

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    balance = bond_contract.call().balanceOf(account_address)
    assert balance == deploy_args[2]


# エラー系1: 入力値の型誤り（Owner）
def test_balanceOf_error_1(chain):
    account_address = 1234

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    with pytest.raises(TypeError):
        bond_contract.call().balanceOf(account_address)


'''
TEST4_認定リクエスト（requestSignature）
'''

# 正常系1: 初期値が0
def test_requestSignature_normal_1(web3,chain):
    signer_address = web3.eth.accounts[1]

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    signature = bond_contract.call().signatures(signer_address)
    assert signature == 0


# 正常系2: 認定リクエスト
def test_requestSignature_normal_2(web3,chain):
    signer_address = web3.eth.accounts[1]

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    txn_hash = bond_contract.transact().requestSignature(signer_address)
    chain.wait.for_receipt(txn_hash)

    signature = bond_contract.call().signatures(signer_address)
    assert signature == 1


# エラー系1: 入力値の型誤り（Signer）
def test_requestSignature_error_1(chain):
    signer_address = 1234

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    with pytest.raises(TypeError):
        bond_contract.transact().requestSignature(signer_address)


'''
TEST5_認定（sign）
'''

# 正常系1: 認定リクエスト -> 認定
def test_sign_normal_1(web3,chain):
    account_address = web3.eth.accounts[0]
    signer_address = web3.eth.accounts[1]

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    # 認定リクエスト -> Success
    web3.eth.defaultAccount = account_address
    txn_hash_1 = bond_contract.transact().requestSignature(signer_address)
    chain.wait.for_receipt(txn_hash_1)

    # 認定 -> Success
    web3.eth.defaultAccount = signer_address
    txn_hash_2 = bond_contract.transact().sign()
    chain.wait.for_receipt(txn_hash_2)

    signature = bond_contract.call().signatures(signer_address)
    assert signature == 2


# エラー系1: 認定リクエスト未実施 -> 認定
def test_sign_error_1(web3,chain):
    signer_address = web3.eth.accounts[0]

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    # 認定 -> Failure
    web3.eth.defaultAccount = signer_address
    with pytest.raises(TransactionFailed):
        bond_contract.transact().sign()


# エラー系2: 認定リクエスト-> 異なるSinerから認定をした場合
def test_sign_error_2(web3,chain):
    account_address = web3.eth.accounts[0]
    signer_address = web3.eth.accounts[1]
    signer_address_other = web3.eth.accounts[2]

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    # 認定リクエスト -> Success
    web3.eth.defaultAccount = account_address
    txn_hash_1 = bond_contract.transact().requestSignature(signer_address)
    chain.wait.for_receipt(txn_hash_1)

    # 異なるSignerが認定 -> Failure
    web3.eth.defaultAccount = signer_address_other
    with pytest.raises(TransactionFailed):
        bond_contract.transact().sign()


'''
TEST6_認定取消（unsign）
'''

# 正常系1: 認定リクエスト -> 認定 -> 認定取消
def test_unsign_normal_1(web3,chain):
    account_address = web3.eth.accounts[0]
    signer_address = web3.eth.accounts[1]

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    # 認定リクエスト -> Success
    web3.eth.defaultAccount = account_address
    txn_hash_1 = bond_contract.transact().requestSignature(signer_address)
    chain.wait.for_receipt(txn_hash_1)

    # 認定 -> Success
    web3.eth.defaultAccount = signer_address
    txn_hash_2 = bond_contract.transact().sign()
    chain.wait.for_receipt(txn_hash_2)

    # 認定取消 -> Success
    web3.eth.defaultAccount = signer_address
    txn_hash_3 = bond_contract.transact().unsign()
    chain.wait.for_receipt(txn_hash_3)

    signature = bond_contract.call().signatures(signer_address)
    assert signature == 0


# エラー系1: 認定リクエスト未実施 -> 認定取消
def test_unsign_error_1(web3,chain):
    signer_address = web3.eth.accounts[0]

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    # 認定取消 -> Failure
    web3.eth.defaultAccount = signer_address
    with pytest.raises(TransactionFailed):
        bond_contract.transact().unsign()


# エラー系2: 認定リクエスト -> （認定未実施） -> 認定取消
def test_unsign_error_2(web3,chain):
    account_address = web3.eth.accounts[0]
    signer_address = web3.eth.accounts[1]

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    # 認定リクエスト -> Success
    web3.eth.defaultAccount = account_address
    txn_hash_1 = bond_contract.transact().requestSignature(signer_address)
    chain.wait.for_receipt(txn_hash_1)

    # 認定取消 -> Failure
    web3.eth.defaultAccount = signer_address
    with pytest.raises(TransactionFailed):
        bond_contract.transact().unsign()


# エラー系3: 認定リクエスト-> 認定 -> 異なるSinerから認定取消を実施した場合
def test_sign_error_3(web3,chain):
    account_address = web3.eth.accounts[0]
    signer_address = web3.eth.accounts[1]
    signer_address_other = web3.eth.accounts[2]

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    # 認定リクエスト -> Success
    web3.eth.defaultAccount = account_address
    txn_hash_1 = bond_contract.transact().requestSignature(signer_address)
    chain.wait.for_receipt(txn_hash_1)

    # 認定 -> Success
    web3.eth.defaultAccount = signer_address
    txn_hash_2 = bond_contract.transact().sign()
    chain.wait.for_receipt(txn_hash_2)

    # 異なるSignerが認定取消を実施 -> Failure
    web3.eth.defaultAccount = signer_address_other
    with pytest.raises(TransactionFailed):
        bond_contract.transact().unsign()


'''
TEST7_償還（redeem）
'''

# 正常系1: 発行（デプロイ） -> 償還
def test_redeem_normal_1(web3,chain):
    owner_address = web3.eth.accounts[0]

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    # 償還 -> Success
    web3.eth.defaultAccount = owner_address
    txn_hash = bond_contract.transact().redeem()
    chain.wait.for_receipt(txn_hash)

    is_redeemed = bond_contract.call().isRedeemed()
    assert is_redeemed == True


# エラー系1: Owner以外のアドレスから償還を実施した場合
def test_redeem_error_1(web3,chain):
    owner_address = web3.eth.accounts[0]
    other_address = web3.eth.accounts[1]

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    # Owner以外のアドレスから償還を実施 -> Failure
    web3.eth.defaultAccount = other_address
    with pytest.raises(TransactionFailed):
        bond_contract.transact().redeem()


'''
TEST8_商品画像の設定（setImageURL, getImageURL）
'''

# 正常系1: 発行（デプロイ） -> 商品画像の設定
def test_setImageURL_normal_1(web3,chain):
    owner_address = web3.eth.accounts[0]
    image_url = 'https://some_image_url.com/image.png'

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    # 商品画像の設定 -> Success
    web3.eth.defaultAccount = owner_address
    txn_hash = bond_contract.transact().setImageURL(0, image_url)
    chain.wait.for_receipt(txn_hash)

    image_url_0 = bond_contract.call().getImageURL(0)
    assert image_url_0 == image_url


# 正常系2: 発行（デプロイ） -> 商品画像の設定（複数設定）
def test_setImageURL_normal_2(web3,chain):
    owner_address = web3.eth.accounts[0]
    image_url = 'https://some_image_url.com/image.png'

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    # 商品画像の設定（1つ目） -> Success
    web3.eth.defaultAccount = owner_address
    txn_hash_1 = bond_contract.transact().setImageURL(0, image_url)
    chain.wait.for_receipt(txn_hash_1)

    # 商品画像の設定（2つ目） -> Success
    web3.eth.defaultAccount = owner_address
    txn_hash_2 = bond_contract.transact().setImageURL(1, image_url)
    chain.wait.for_receipt(txn_hash_2)

    image_url_0 = bond_contract.call().getImageURL(0)
    image_url_1 = bond_contract.call().getImageURL(1)
    assert image_url_0 == image_url
    assert image_url_1 == image_url


# 正常系3: 発行（デプロイ） -> 商品画像の設定（上書き登録）
def test_setImageURL_normal_3(web3,chain):
    owner_address = web3.eth.accounts[0]
    image_url = 'https://some_image_url.com/image.png'
    image_url_after = 'https://some_image_url.com/image_after.png'

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    # 商品画像の設定（1回目） -> Success
    web3.eth.defaultAccount = owner_address
    txn_hash_1 = bond_contract.transact().setImageURL(0, image_url)
    chain.wait.for_receipt(txn_hash_1)

    # 商品画像の設定（2回目：上書き） -> Success
    web3.eth.defaultAccount = owner_address
    txn_hash_2 = bond_contract.transact().setImageURL(0, image_url_after)
    chain.wait.for_receipt(txn_hash_2)

    image_url_0 = bond_contract.call().getImageURL(0)
    assert image_url_0 == image_url_after


# エラー系1: 入力値の型誤り（Class）
def test_setImageURL_error_1(web3,chain):
    owner_address = web3.eth.accounts[0]
    image_url = 'https://some_image_url.com/image.png'

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    web3.eth.defaultAccount = owner_address

    with pytest.raises(TypeError):
        bond_contract.transact().setImageURL(-1, image_url)

    with pytest.raises(TypeError):
        bond_contract.transact().setImageURL(256, image_url)

    with pytest.raises(TypeError):
        bond_contract.transact().setImageURL('0', image_url)


# エラー系2: 入力値の型誤り（ImageURL）
def test_setImageURL_error_2(web3,chain):
    owner_address = web3.eth.accounts[0]
    image_url = 1234

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    web3.eth.defaultAccount = owner_address
    with pytest.raises(TypeError):
        bond_contract.transact().setImageURL(0, image_url)


# エラー系3: Owner以外のアドレスから画像設定を実施した場合
def test_setImageURL_error_3(web3,chain):
    owner_address = web3.eth.accounts[0]
    other_address = web3.eth.accounts[1]
    image_url = 'https://some_image_url.com/image.png'

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    # Owner以外のアドレスから画像設定を実施 -> Failure
    web3.eth.defaultAccount = other_address
    with pytest.raises(TransactionFailed):
        bond_contract.transact().setImageURL(0, image_url)


'''
TEST9_メモの更新（updateMemo）
'''

# 正常系1: 発行（デプロイ） -> メモ欄の修正
def test_updateMemo_normal_1(web3,chain):
    owner_address = web3.eth.accounts[0]

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    # メモ欄の修正 -> Success
    web3.eth.defaultAccount = owner_address
    txn_hash = bond_contract.transact().updateMemo('updated memo')
    chain.wait.for_receipt(txn_hash)

    memo = bond_contract.call().memo()
    assert memo == 'updated memo'


# エラー系1: 入力値の型誤り
def test_updateMemo_error_1(web3,chain):
    owner_address = web3.eth.accounts[0]

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    # メモ欄の修正 -> Success
    web3.eth.defaultAccount = owner_address
    with pytest.raises(TypeError):
        bond_contract.transact().updateMemo(1234)


# エラー系2: Owner以外のアドレスからメモ欄の修正を実施した場合
def test_updateMemo_error_2(web3,chain):
    owner_address = web3.eth.accounts[0]
    other_address = web3.eth.accounts[1]

    deploy_args = init_args()
    bond_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )

    # Owner以外のアドレスからメモ欄の修正を実施 -> Failure
    web3.eth.defaultAccount = other_address
    with pytest.raises(TransactionFailed):
        bond_contract.transact().updateMemo('updated memo')
