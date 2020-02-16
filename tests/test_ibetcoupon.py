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


def deploy(chain, deploy_args):
    coupon_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetCoupon',
        deploy_args=deploy_args
    )
    return coupon_contract


'''
TEST_デプロイ
'''


# 正常系1: deploy
def test_deploy_normal_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    owner_address = coupon.call().owner()
    name = coupon.call().name()
    symbol = coupon.call().symbol()
    total_supply = coupon.call().totalSupply()
    tradable_exchange = coupon.call().tradableExchange()
    details = coupon.call().details()
    return_details = coupon.call().returnDetails()
    memo = coupon.call().memo()
    expiration_date = coupon.call().expirationDate()
    is_valid = coupon.call().status()
    transferable = coupon.call().transferable()
    contact_information = coupon.call().contactInformation()
    privacy_policy = coupon.call().privacyPolicy()

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
def test_deploy_error_1(chain, coupon_exchange):
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[0] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetCoupon', deploy_args=deploy_args)


# エラー系2: 入力値の型誤り（symbol）
def test_deploy_error_2(chain, coupon_exchange):
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[1] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetCoupon', deploy_args=deploy_args)


# エラー系3: 入力値の型誤り（totalSupply）
def test_deploy_error_3(chain, coupon_exchange):
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[2] = "10000"

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetCoupon', deploy_args=deploy_args)


# エラー系4: 入力値の型誤り（tradableExchange）
def test_deploy_error_4(chain, coupon_exchange):
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[3] = '0xaaa'

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetCoupon', deploy_args=deploy_args)


# エラー系5: 入力値の型誤り（details）
def test_deploy_error_5(chain, coupon_exchange):
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[4] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetCoupon', deploy_args=deploy_args)


# エラー系6: 入力値の型誤り（returnDetails）
def test_deploy_error_6(chain, coupon_exchange):
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[5] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetCoupon', deploy_args=deploy_args)


# エラー系7: 入力値の型誤り（memo）
def test_deploy_error_7(chain, coupon_exchange):
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[6] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetCoupon', deploy_args=deploy_args)


# エラー系8: 入力値の型誤り（expirationDate）
def test_deploy_error_8(chain, coupon_exchange):
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[7] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetCoupon', deploy_args=deploy_args)


# エラー系9: 入力値の型誤り（transferable）
def test_deploy_error_9(chain, coupon_exchange):
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[8] = 'True'

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetCoupon', deploy_args=deploy_args)


# エラー系10: 入力値の型誤り（contactInformation）
def test_deploy_error_10(chain, coupon_exchange):
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[9] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetCoupon', deploy_args=deploy_args)


# エラー系11: 入力値の型誤り（privacyPolicy）
def test_deploy_error_11(chain, coupon_exchange):
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[10] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetCoupon', deploy_args=deploy_args)


'''
TEST_クーポンの譲渡（transfer）
'''


# 正常系1: アカウントアドレスへの譲渡
def test_transfer_normal_1(web3, chain, users, coupon_exchange):
    _from = users['issuer']
    _to = users['trader']
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _from
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 譲渡
    web3.eth.defaultAccount = _from
    txn_hash = coupon.transact().transfer(_to, _value)
    chain.wait.for_receipt(txn_hash)

    from_balance = coupon.call().balanceOf(_from)
    to_balance = coupon.call().balanceOf(_to)

    assert from_balance == deploy_args[2] - _value
    assert to_balance == _value


# エラー系1: 入力値の型誤り（To）
def test_transfer_error_1(web3, chain, users, coupon_exchange):
    _from = users['issuer']
    _to = 1234
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _from
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 譲渡
    web3.eth.defaultAccount = _from
    with pytest.raises(TypeError):
        coupon.transact().transfer(_to, _value)


# エラー系2: 入力値の型誤り（Value）
def test_transfer_error_2(web3, chain, users, coupon_exchange):
    _from = users['issuer']
    _to = users['trader']

    # 新規発行
    web3.eth.defaultAccount = _from
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 譲渡
    web3.eth.defaultAccount = _from
    with pytest.raises(TypeError):
        coupon.transact().transfer(_to, '0')

    with pytest.raises(TypeError):
        coupon.transact().transfer(_to, 2 ** 256)

    with pytest.raises(TypeError):
        coupon.transact().transfer(_to, -1)

    with pytest.raises(TypeError):
        coupon.transact().transfer(_to, 0.1)


# エラー系3: 残高不足
def test_transfer_error_3(web3, chain, users, coupon_exchange):
    _from = users['issuer']
    _to = users['trader']

    # 新規発行
    web3.eth.defaultAccount = _from
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 譲渡（残高超）
    web3.eth.defaultAccount = _from
    _value = deploy_args[2] + 1
    try:
        txn_hash = coupon.transact().transfer(_to, _value)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    assert coupon.call().balanceOf(_from) == deploy_args[2]
    assert coupon.call().balanceOf(_to) == 0


# エラー系4: 譲渡不可クーポンの譲渡
def test_transfer_error_4(web3, chain, users, coupon_exchange):
    _from = users['issuer']
    _to = users['trader']

    # 新規発行（譲渡不可クーポン）
    web3.eth.defaultAccount = _from
    deploy_args = init_args(coupon_exchange.address)
    deploy_args[8] = False
    coupon = deploy(chain, deploy_args)

    # 譲渡（譲渡不可）
    web3.eth.defaultAccount = _from
    _value = 1
    try:
        txn_hash = coupon.transact().transfer(_to, _value)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    assert coupon.call().balanceOf(_from) == deploy_args[2]
    assert coupon.call().balanceOf(_to) == 0


# エラー系5: 取引不可Exchangeへの振替
def test_transfer_error_5(web3, chain, users, coupon_exchange, coupon_exchange_storage,
                          payment_gateway):
    _issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 取引不可Exchange
    web3.eth.defaultAccount = users['admin']
    dummy_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetMembershipExchange',  # IbetCouponExchange以外を読み込む必要がある
        deploy_args=[payment_gateway.address, coupon_exchange_storage.address]
    )

    # 譲渡
    web3.eth.defaultAccount = _issuer
    _value = deploy_args[2]
    try:
        txn_hash = coupon.transact().transfer(dummy_exchange.address, _value)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    assert coupon.call().balanceOf(_issuer) == deploy_args[2]
    assert coupon.call().balanceOf(dummy_exchange.address) == 0


'''
TEST_クーポンの消費（consume）
'''


# 正常系1
# ＜発行者＞発行　->　＜発行者＞消費
def test_consume_normal_1(web3, chain, users, coupon_exchange):
    _user = users['issuer']
    _value = 1

    # 新規発行
    web3.eth.defaultAccount = _user
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 消費
    web3.eth.defaultAccount = _user
    txn_hash = coupon.transact().consume(_value)
    chain.wait.for_receipt(txn_hash)

    balance = coupon.call().balanceOf(_user)
    used = coupon.call().usedOf(_user)

    assert balance == deploy_args[2] - _value
    assert used == _value


# 正常系2
# ＜発行者＞発行　->　＜発行者＞割当　-> ＜消費者＞消費
def test_consume_normal_2(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _consumer = users['trader']
    _value = 1

    # 新規発行
    web3.eth.defaultAccount = _issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 割当
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().transferFrom(_issuer, _consumer, _value)
    chain.wait.for_receipt(txn_hash)

    # 消費
    web3.eth.defaultAccount = _consumer
    txn_hash = coupon.transact().consume(_value)
    chain.wait.for_receipt(txn_hash)

    balance_issuer = coupon.call().balanceOf(_issuer)
    balance_consumer = coupon.call().balanceOf(_consumer)
    used_consumer = coupon.call().usedOf(_consumer)

    assert balance_issuer == deploy_args[2] - _value
    assert balance_consumer == 0
    assert used_consumer == _value


# エラー系1: 入力値の型誤り（Value）
def test_consume_error_1(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _consumer = users['trader']
    _value = '1'

    # 新規発行
    web3.eth.defaultAccount = _issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 消費
    web3.eth.defaultAccount = _issuer
    with pytest.raises(TypeError):
        coupon.transact().consume('0')

    with pytest.raises(TypeError):
        coupon.transact().consume(2 ** 256)

    with pytest.raises(TypeError):
        coupon.transact().consume(-1)

    with pytest.raises(TypeError):
        coupon.transact().consume(0.1)


# エラー系2: 残高不足
def test_consume_error_2(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 消費
    web3.eth.defaultAccount = _issuer
    _value = deploy_args[2] + 1
    try:
        txn_hash = coupon.transact().consume(_value)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    assert coupon.call().balanceOf(_issuer) == deploy_args[2]
    assert coupon.call().usedOf(_issuer) == 0


# エラー系3: 無効化されたクーポンの消費
def test_consume_error_3(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _value = 1

    # 新規発行
    web3.eth.defaultAccount = _issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # クーポンの無効化
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().setStatus(False)
    chain.wait.for_receipt(txn_hash)

    # 消費
    web3.eth.defaultAccount = _issuer
    try:
        txn_hash = coupon.transact().consume(_value)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    assert coupon.call().balanceOf(_issuer) == deploy_args[2]
    assert coupon.call().usedOf(_issuer) == 0


'''
TEST_追加発行（issue）
'''


# 正常系1
# ＜発行者＞発行　->　＜発行者＞追加発行
def test_issue_normal_1(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _value = 1

    # 新規発行
    web3.eth.defaultAccount = _issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 追加発行
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().issue(_value)
    chain.wait.for_receipt(txn_hash)

    balance = coupon.call().balanceOf(_issuer)
    total_supply = coupon.call().totalSupply()

    assert balance == deploy_args[2] + _value
    assert total_supply == deploy_args[2] + _value


# 正常系2
# ＜発行者＞発行　->　＜発行者＞割当 -> ＜発行者＞追加発行
def test_issue_normal_2(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _consumer = users['trader']
    _allocated = 1
    _value = 10

    # 新規発行
    web3.eth.defaultAccount = _issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 割当
    txn_hash = coupon.transact().transferFrom(_issuer, _consumer, _allocated)
    chain.wait.for_receipt(txn_hash)

    # 追加発行
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().issue(_value)
    chain.wait.for_receipt(txn_hash)

    balance = coupon.call().balanceOf(_issuer)
    total_supply = coupon.call().totalSupply()

    assert balance == deploy_args[2] + _value - _allocated
    assert total_supply == deploy_args[2] + _value


# エラー系1: 入力値の型誤り（Value）
def test_issue_error_1(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 追加発行
    web3.eth.defaultAccount = _issuer
    with pytest.raises(TypeError):
        coupon.transact().issue('0')

    with pytest.raises(TypeError):
        coupon.transact().issue(2 ** 256)

    with pytest.raises(TypeError):
        coupon.transact().issue(-1)

    with pytest.raises(TypeError):
        coupon.transact().issue(0.1)


# エラー系2
# ＜発行者＞発行　->　＜発行者＞追加発行（uint最大値超）
def test_issue_error_2(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _consumer = users['trader']
    _allocated = 999999
    _value = 2 ** 256 - 1

    # 新規発行
    web3.eth.defaultAccount = _issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 割当
    txn_hash = coupon.transact().transferFrom(_issuer, _consumer, _allocated)
    chain.wait.for_receipt(txn_hash)

    # 追加発行（uint最大値超）
    web3.eth.defaultAccount = _issuer
    try:
        txn_hash = coupon.transact().issue(_value)  # エラーになる（2**256 -1 +1）
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    balance = coupon.call().balanceOf(_issuer)
    total_supply = coupon.call().totalSupply()

    assert balance == deploy_args[2] - _allocated
    assert total_supply == deploy_args[2]


# エラー系3
# ＜発行者＞発行　->　＜発行者以外＞追加発行
def test_issue_error_3(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _other = users['trader']
    _value = 1000

    # 新規発行
    web3.eth.defaultAccount = _issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 追加発行（uint最大値超）
    web3.eth.defaultAccount = _other
    try:
        txn_hash = coupon.transact().issue(_value)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    balance = coupon.call().balanceOf(_issuer)
    total_supply = coupon.call().totalSupply()

    assert balance == deploy_args[2]
    assert total_supply == deploy_args[2]


'''
TEST_クーポン詳細欄の更新（setDetails）
'''


# 正常系1
# ＜発行者＞発行 -> ＜発行者＞詳細欄の修正
def test_setDetails_normal_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 詳細欄の修正
    web3.eth.defaultAccount = issuer
    txn_hash = coupon.transact().setDetails('updated details')
    chain.wait.for_receipt(txn_hash)

    details = coupon.call().details()
    assert details == 'updated details'


# エラー系1: 入力値の型誤り
def test_setDetails_error_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 詳細欄の修正
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        coupon.transact().setDetails(1234)


# エラー系2: 権限エラー
def test_setDetails_error_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    other = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 詳細欄の修正
    web3.eth.defaultAccount = other
    try:
        txn_hash = coupon.transact().setDetails('updated details')
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    details = coupon.call().details()
    assert details == 'some_details'


'''
TEST_メモ欄の更新（setMemo）
'''


# 正常系1
# ＜発行者＞発行 -> ＜発行者＞メモ欄の修正
def test_setMemo_normal_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # メモ欄の修正
    web3.eth.defaultAccount = issuer
    txn_hash = coupon.transact().setMemo('updated memo')
    chain.wait.for_receipt(txn_hash)

    details = coupon.call().memo()
    assert details == 'updated memo'


# エラー系1: 入力値の型誤り
def test_setMemo_error_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # メモ欄の修正
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        coupon.transact().setMemo(1234)


# エラー系2: 権限エラー
def test_setMemo_error_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    other = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # メモ欄の修正
    web3.eth.defaultAccount = other
    try:
        txn_hash = coupon.transact().setMemo('updated memo')
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    details = coupon.call().memo()
    assert details == 'some_memo'


'''
TEST_残高確認（balanceOf）
'''


# 正常系1: クーポン新規作成 -> 残高確認
def test_balanceOf_normal_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    balance = coupon.call().balanceOf(issuer)
    assert balance == deploy_args[2]


# エラー系1: 入力値の型誤り（Owner）
def test_balanceOf_error_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    account_address = 1234

    with pytest.raises(TypeError):
        coupon.call().balanceOf(account_address)


'''
TEST_使用済数量確認（usedOf）
'''


# 正常系1: クーポン作成 -> 消費 -> 使用済数量確認
def test_usedOf_normal_1(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']
    _value = 1

    # 新規発行
    web3.eth.defaultAccount = _issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 消費
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().consume(_value)
    chain.wait.for_receipt(txn_hash)

    # 使用済み数量確認
    used = coupon.call().usedOf(_issuer)

    assert used == _value


# エラー系1: 入力値の型誤り（Owner）
def test_usedOf_error_1(web3, chain, users, coupon_exchange):
    _issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    account_address = 1234

    with pytest.raises(TypeError):
        coupon.call().usedOf(account_address)


'''
TEST_商品画像の設定（setImageURL, getImageURL）
'''


# 正常系1: 発行 -> 商品画像の設定
def test_setImageURL_normal_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 商品画像の設定
    web3.eth.defaultAccount = issuer
    image_url = 'https://some_image_url.com/image.png'
    txn_hash = coupon.transact().setImageURL(0, image_url)
    chain.wait.for_receipt(txn_hash)

    image_url_0 = coupon.call().getImageURL(0)
    assert image_url_0 == image_url


# 正常系2: 発行 -> 商品画像の設定（複数設定）
def test_setImageURL_normal_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    image_url = 'https://some_image_url.com/image1.png'

    # 商品画像の設定（1つ目）
    web3.eth.defaultAccount = issuer
    txn_hash_1 = coupon.transact().setImageURL(0, image_url)
    chain.wait.for_receipt(txn_hash_1)

    # 商品画像の設定（2つ目）
    web3.eth.defaultAccount = issuer
    txn_hash_2 = coupon.transact().setImageURL(1, image_url)
    chain.wait.for_receipt(txn_hash_2)

    image_url_0 = coupon.call().getImageURL(0)
    image_url_1 = coupon.call().getImageURL(1)
    assert image_url_0 == image_url
    assert image_url_1 == image_url


# 正常系3: 発行（デプロイ） -> 商品画像の設定（上書き登録）
def test_setImageURL_normal_3(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    image_url = 'https://some_image_url.com/image.png'
    image_url_after = 'https://some_image_url.com/image_after.png'

    # 商品画像の設定（1回目）
    web3.eth.defaultAccount = issuer
    txn_hash_1 = coupon.transact().setImageURL(0, image_url)
    chain.wait.for_receipt(txn_hash_1)

    # 商品画像の設定（2回目：上書き）
    web3.eth.defaultAccount = issuer
    txn_hash_2 = coupon.transact().setImageURL(0, image_url_after)
    chain.wait.for_receipt(txn_hash_2)

    image_url_0 = coupon.call().getImageURL(0)
    assert image_url_0 == image_url_after


# エラー系1: 入力値の型誤り（Class）
def test_setImageURL_error_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    image_url = 'https://some_image_url.com/image.png'

    web3.eth.defaultAccount = issuer

    with pytest.raises(TypeError):
        coupon.transact().setImageURL(-1, image_url)

    with pytest.raises(TypeError):
        coupon.transact().setImageURL(256, image_url)

    with pytest.raises(TypeError):
        coupon.transact().setImageURL('0', image_url)

    with pytest.raises(TypeError):
        coupon.transact().getImageURL(-1)

    with pytest.raises(TypeError):
        coupon.transact().getImageURL(256)

    with pytest.raises(TypeError):
        coupon.transact().getImageURL('0')


# エラー系2: 入力値の型誤り（ImageURL）
def test_setImageURL_error_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    image_url = 1234

    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        coupon.transact().setImageURL(0, image_url)


# エラー系3: 権限エラー
def test_setImageURL_error_3(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    other = users['admin']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    image_url = 'https://some_image_url.com/image.png'

    # 画像設定
    web3.eth.defaultAccount = other
    try:
        txn_hash = coupon.transact().setImageURL(0, image_url)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    image_url_0 = coupon.call().getImageURL(0)
    assert image_url_0 == ''


'''
TEST_ステータス（有効・無効）の更新（setStatus）
'''


# 正常系1
# ＜発行者＞発行 -> ＜発行者＞ステータスの修正
def test_setStatus_normal_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # ステータスの修正
    web3.eth.defaultAccount = issuer
    txn_hash = coupon.transact().setStatus(False)
    chain.wait.for_receipt(txn_hash)

    assert coupon.call().status() is False


# エラー系1: 入力値の型誤り
def test_setStatus_error_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # ステータスの修正
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        coupon.transact().setStatus('False')


# エラー系2: 権限エラー
def test_setStatus_error_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    other = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # メモ欄の修正
    web3.eth.defaultAccount = other
    try:
        txn_hash = coupon.transact().setStatus(False)
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    assert coupon.call().status() is True


'''
TEST_取引可能Exchangeの更新（setTradableExchange）
'''


# 正常系1: 発行 -> Exchangeの更新
def test_setTradableExchange_normal_1(web3, chain, users, coupon_exchange,
                                      coupon_exchange_storage, payment_gateway):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # Exchange（新）
    web3.eth.defaultAccount = users['admin']
    other_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetMembershipExchange',  # IbetCouponExchange以外を読み込む必要がある
        deploy_args=[payment_gateway.address, coupon_exchange_storage.address]
    )

    # Exchangeの更新
    web3.eth.defaultAccount = issuer
    txn_hash = coupon.transact().setTradableExchange(other_exchange.address)
    chain.wait.for_receipt(txn_hash)

    assert coupon.call().tradableExchange() == to_checksum_address(other_exchange.address)


# エラー系1: 発行 -> Exchangeの更新（入力値の型誤り）
def test_setTradableExchange_error_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # Exchangeの更新
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        coupon.transact().setTradableExchange('0xaaaa')


# エラー系2: 発行 -> Exchangeの更新（権限エラー）
def test_setTradableExchange_error_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # その他Exchange
    web3.eth.defaultAccount = users['admin']
    other_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetCouponExchange',  # IbetCouponExchange以外を読み込む必要がある
        deploy_args=[]
    )

    # Exchangeの更新
    web3.eth.defaultAccount = trader
    try:
        txn_hash = coupon.transact().setTradableExchange(other_exchange.address)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    assert coupon.call().tradableExchange() == to_checksum_address(coupon_exchange.address)


'''
TEST_有効期限更新（setExpirationDate）
'''


# 正常系1: 発行 -> 有効期限更新
def test_setExpirationDate_normal_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    after_expiration_date = 'after_expiration_date'

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 有効期限更新
    web3.eth.defaultAccount = issuer
    txn_hash = \
        coupon.transact().setExpirationDate(after_expiration_date)
    chain.wait.for_receipt(txn_hash)

    expiration_date = coupon.call().expirationDate()
    assert after_expiration_date == expiration_date


# エラー系1: 入力値の型誤り
def test_setExpirationDate_errors_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 型誤り
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        coupon.transact().setExpirationDate(1234)


# エラー系2: 権限エラー
def test_setExpirationDate_error_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    attacker = users['trader']
    after_expiration_date = 'after_expiration_date'

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 有効期限更新：権限エラー
    web3.eth.defaultAccount = attacker
    try:
        txn_hash = coupon.transact().setExpirationDate(after_expiration_date)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    expiration_date = coupon.call().expirationDate()
    assert expiration_date == deploy_args[7]


'''
TEST_譲渡可能更新（setTransferable）
'''


# 正常系1: 発行 -> 譲渡可能更新
def test_setTransferable_normal_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    after_transferable = False

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 譲渡可能更新
    web3.eth.defaultAccount = issuer
    txn_hash = coupon.transact().setTransferable(after_transferable)
    chain.wait.for_receipt(txn_hash)

    transferable = coupon.call().transferable()
    assert after_transferable == transferable


# エラー系1: 入力値の型誤り
def test_setTransferable_error_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 型誤り
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        coupon.transact().setTransferable('True')


# エラー系2: 権限エラー
def test_setTransferable_error_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    attacker = users['trader']
    after_transferable = False

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 譲渡可能更新
    web3.eth.defaultAccount = attacker
    try:
        txn_hash = coupon.transact().setTransferable(after_transferable)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    transferable = coupon.call().transferable()
    assert transferable == deploy_args[8]


'''
TEST_新規募集ステータス更新（setInitialOfferingStatus）
'''


# 正常系1: 発行 -> 新規募集ステータス更新（False→True）
def test_setInitialOfferingStatus_normal_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 初期状態 == False
    assert coupon.call().initialOfferingStatus() is False

    # 新規募集ステータスの更新
    web3.eth.defaultAccount = issuer
    txn_hash = coupon.transact().setInitialOfferingStatus(True)
    chain.wait.for_receipt(txn_hash)

    assert coupon.call().initialOfferingStatus() is True


# 正常系2:
#   発行 -> 新規募集ステータス更新（False→True） -> 2回目更新（True→False）
def test_setInitialOfferingStatus_normal_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 新規募集ステータスの更新
    web3.eth.defaultAccount = issuer
    txn_hash = coupon.transact().setInitialOfferingStatus(True)
    chain.wait.for_receipt(txn_hash)

    # 新規募集ステータスの更新（2回目）
    web3.eth.defaultAccount = issuer
    txn_hash = coupon.transact().setInitialOfferingStatus(False)
    chain.wait.for_receipt(txn_hash)

    assert coupon.call().initialOfferingStatus() is False


# エラー系1: 発行 -> 新規募集ステータス更新（入力値の型誤り）
def test_setInitialOfferingStatus_error_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 新規募集ステータスの更新
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        coupon.transact().setInitialOfferingStatus('True')


'''
TEST_募集申込（applyForOffering）
'''


# 正常系1
#   発行：発行体 -> 投資家：募集申込
def test_applyForOffering_normal_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 新規募集ステータスの更新
    web3.eth.defaultAccount = issuer
    txn_hash = coupon.transact().setInitialOfferingStatus(True)
    chain.wait.for_receipt(txn_hash)

    # 募集申込
    web3.eth.defaultAccount = trader
    txn_hash = coupon.transact().applyForOffering('abcdefgh')
    chain.wait.for_receipt(txn_hash)

    assert coupon.call().applications(trader) == 'abcdefgh'


# 正常系2
#   発行：発行体 -> （申込なし）初期データ参照
def test_applyForOffering_normal_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 新規募集ステータスの更新
    web3.eth.defaultAccount = issuer
    txn_hash = coupon.transact().setInitialOfferingStatus(True)
    chain.wait.for_receipt(txn_hash)

    assert coupon.call().applications(trader) == ''


# エラー系1:
#   発行：発行体 -> 投資家：募集申込（入力値の型誤り）
def test_applyForOffering_error_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 新規募集ステータスの更新
    web3.eth.defaultAccount = issuer
    txn_hash = coupon.transact().setInitialOfferingStatus(True)
    chain.wait.for_receipt(txn_hash)

    # 募集申込
    web3.eth.defaultAccount = trader
    with pytest.raises(TypeError):
        coupon.transact().applyForOffering(1234)


# エラー系2:
#   発行：発行体 -> 投資家：募集申込（申込ステータスが停止中）
def test_applyForOffering_error_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 募集申込
    web3.eth.defaultAccount = trader
    try:
        txn_hash = coupon.transact().applyForOffering('abcdefgh')
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    assert coupon.call().applications(trader) == ''


'''
TEST_リターン詳細更新（setReturnDetails）
'''


# 正常系1: 発行 -> 詳細更新
def test_setReturnDetails_normal_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    after_return_details = 'after_return_details'

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # リターン詳細更新
    web3.eth.defaultAccount = issuer
    txn_hash = coupon.transact().setReturnDetails(after_return_details)
    chain.wait.for_receipt(txn_hash)

    return_details = coupon.call().returnDetails()
    assert after_return_details == return_details


# エラー系1: 入力値の型誤り
def test_setReturnDetails_error_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 型誤り
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        coupon.transact().setReturnDetails(1234)


# エラー系2: 権限エラー
def test_setReturnDetails_error_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    attacker = users['trader']
    after_return_details = 'after_return_details'

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # リターン詳細更新：権限エラー
    web3.eth.defaultAccount = attacker
    try:
        txn_hash = coupon.transact().setReturnDetails(after_return_details)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    return_details = coupon.call().returnDetails()
    assert return_details == deploy_args[5]


'''
TEST_問い合わせ先情報の更新（setContactInformation）
'''


# 正常系1
# ＜発行者＞発行 -> ＜発行者＞問い合わせ先情報の修正
def test_setContactInformation_normal_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 修正
    web3.eth.defaultAccount = issuer
    txn_hash = coupon.transact().setContactInformation('updated contact information')
    chain.wait.for_receipt(txn_hash)

    contact_information = coupon.call().contactInformation()
    assert contact_information == 'updated contact information'


# エラー系1: 入力値の型誤り
def test_setContactInformation_error_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 修正
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        coupon.transact().setContactInformation(1234)


# エラー系2: 権限エラー
def test_setContactInformation_error_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    other = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 修正
    web3.eth.defaultAccount = other
    try:
        txn_hash = coupon.transact().setContactInformation('updated contact information')
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    contact_information = coupon.call().contactInformation()
    assert contact_information == 'some_contact_information'


'''
TEST_プライバシーポリシーの更新（setPrivacyPolicy）
'''


# 正常系1
# ＜発行者＞発行 -> ＜発行者＞プライバシーポリシーの修正
def test_setPrivacyPolicy_normal_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 修正
    web3.eth.defaultAccount = issuer
    txn_hash = coupon.transact().setPrivacyPolicy('updated privacy policy')
    chain.wait.for_receipt(txn_hash)

    privacy_policy = coupon.call().privacyPolicy()
    assert privacy_policy == 'updated privacy policy'


# エラー系1: 入力値の型誤り
def test_setPrivacyPolicy_error_1(web3, chain, users, coupon_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 修正
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        coupon.transact().setPrivacyPolicy(1234)


# エラー系2: 権限エラー
def test_setPrivacyPolicy_error_2(web3, chain, users, coupon_exchange):
    issuer = users['issuer']
    other = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(coupon_exchange.address)
    coupon = deploy(chain, deploy_args)

    # 修正
    web3.eth.defaultAccount = other
    try:
        txn_hash = coupon.transact().setPrivacyPolicy('updated privacy policy')
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    privacy_policy = coupon.call().privacyPolicy()
    assert privacy_policy == 'some_privacy_policy'