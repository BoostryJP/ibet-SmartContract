import pytest
import utils

'''
TEST1_デプロイ
'''
def init_args():
    name = 'test_coupon'
    symbol = 'CPN'
    total_supply = 1000000
    details = 'some_details'
    memo = 'some_memo'
    expirationDate = '20201231'
    transferable = False

    deploy_args = [
        name, symbol, total_supply, details,
        memo, expirationDate, transferable
    ]
    return deploy_args

# 正常系1: deploy
def test_deploy_normal_1(web3, chain, users):
    issuer = users['issuer']

    web3.eth.defaultAccount = issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    owner_address = coupon.call().owner()
    name = coupon.call().name()
    symbol = coupon.call().symbol()
    total_supply = coupon.call().totalSupply()
    details = coupon.call().details()
    memo = coupon.call().memo()
    expirationDate = coupon.call().expirationDate()
    is_valid = coupon.call().isValid()
    transferable = coupon.call().transferable()

    assert owner_address == issuer
    assert name == deploy_args[0]
    assert symbol == deploy_args[1]
    assert total_supply == deploy_args[2]
    assert details == deploy_args[3]
    assert memo == deploy_args[4]
    assert expirationDate == deploy_args[5]
    assert is_valid == True
    assert transferable == deploy_args[6]

# エラー系1: 入力値の型誤り（name）
def test_deploy_error_1(chain):
    deploy_args = init_args()
    deploy_args[0] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetCoupon', deploy_args = deploy_args)

# エラー系2: 入力値の型誤り（symbol）
def test_deploy_error_2(chain):
    deploy_args = init_args()
    deploy_args[1] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetCoupon', deploy_args = deploy_args)

# エラー系3: 入力値の型誤り（totalSupply）
def test_deploy_error_3(chain):
    deploy_args = init_args()
    deploy_args[2] = "10000"

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetCoupon', deploy_args = deploy_args)

# エラー系4: 入力値の型誤り（details）
def test_deploy_error_4(chain):
    deploy_args = init_args()
    deploy_args[3] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetCoupon', deploy_args = deploy_args)

# エラー系5: 入力値の型誤り（memo）
def test_deploy_error_5(chain):
    deploy_args = init_args()
    deploy_args[4] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetCoupon', deploy_args = deploy_args)

# エラー系6: 入力値の型誤り（expirationDate）
def test_deploy_error_6(chain):
    deploy_args = init_args()
    deploy_args[5] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetCoupon', deploy_args = deploy_args)

# エラー系7: 入力値の型誤り（transferable）
def test_deploy_error_7(chain):
    deploy_args = init_args()
    deploy_args[6] = 'True'

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetCoupon', deploy_args = deploy_args)


'''
TEST2_クーポンの割当（allocate）
'''
# 正常系1: アカウントアドレスへの割当
def test_allocate_normal_1(web3, chain, users):
    _from = users['issuer']
    _to = users['trader']
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _from
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 割当
    txn_hash = coupon.transact().allocate(_to, _value)
    chain.wait.for_receipt(txn_hash)

    from_balance = coupon.call().balanceOf(_from)
    to_balance = coupon.call().balanceOf(_to)

    assert from_balance == deploy_args[2] - _value
    assert to_balance == _value

# エラー系1: 入力値の型誤り（To）
def test_allocate_error_1(web3, chain, users):
    _from = users['issuer']
    _to = 1234
    _value = 100

    web3.eth.defaultAccount = _from
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    web3.eth.defaultAccount = _from
    with pytest.raises(TypeError):
        coupon.transact().transfer(_to, _value)

# エラー系2: 入力値の型誤り（Value）
def test_allocate_error_2(web3, chain, users):
    _from = users['issuer']
    _to = users['trader']

    # 新規発行
    web3.eth.defaultAccount = _from
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    web3.eth.defaultAccount = _from
    with pytest.raises(TypeError):
        coupon.transact().transfer(_to, '0')

    with pytest.raises(TypeError):
        coupon.transact().transfer(_to, 2**256)

    with pytest.raises(TypeError):
        coupon.transact().transfer(_to, -1)

    with pytest.raises(TypeError):
        coupon.transact().transfer(_to, 0.1)

# エラー系3: 残高不足
def test_allocate_error_3(web3, chain, users):
    _from = users['issuer']
    _to = users['trader']

    # クーポン新規発行
    web3.eth.defaultAccount = _from
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 割当（残高超）
    web3.eth.defaultAccount = _from
    _value = deploy_args[2] + 1
    txn_hash = coupon.transact().transfer(_to, _value) #エラーになる
    chain.wait.for_receipt(txn_hash)

    assert coupon.call().balanceOf(_from) == deploy_args[2]
    assert coupon.call().balanceOf(_to) == 0

# エラー系4: 権限なし
def test_allocate_error_4(web3, chain, users):
    _issuer = users['issuer']
    _other = users['trader']

    # クーポン新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 割当（権限なし）
    web3.eth.defaultAccount = _other
    _value = deploy_args[2]
    txn_hash = coupon.transact().transfer(_other, _value) #エラーになる
    chain.wait.for_receipt(txn_hash)

    assert coupon.call().balanceOf(_issuer) == deploy_args[2]
    assert coupon.call().balanceOf(_other) == 0

# エラー系5: 無効化されたクーポンの割当
def test_allocate_error_5(web3, chain, users):
    _issuer = users['issuer']
    _trader = users['trader']

    # クーポン新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # クーポンの無効化
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().updateStatus(False)
    chain.wait.for_receipt(txn_hash)

    # 割当
    web3.eth.defaultAccount = _issuer
    _value = deploy_args[2]
    txn_hash = coupon.transact().allocate(_trader, _value) #エラーになる
    chain.wait.for_receipt(txn_hash)

    assert coupon.call().balanceOf(_issuer) == deploy_args[2]
    assert coupon.call().balanceOf(_trader) == 0


'''
TEST3_クーポンの譲渡（transfer）
'''
# 正常系1: アカウントアドレスへの譲渡
def test_transfer_normal_1(web3, chain, users):
    _from = users['issuer']
    _to = users['trader']
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _from
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 譲渡
    web3.eth.defaultAccount = _from
    txn_hash = coupon.transact().transfer(_to, _value)
    chain.wait.for_receipt(txn_hash)

    from_balance = coupon.call().balanceOf(_from)
    to_balance = coupon.call().balanceOf(_to)

    assert from_balance == deploy_args[2] - _value
    assert to_balance == _value

# エラー系1: 入力値の型誤り（To）
def test_transfer_error_1(web3, chain, users):
    _from = users['issuer']
    _to = 1234
    _value = 100

    # 新規発行
    web3.eth.defaultAccount = _from
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 譲渡
    web3.eth.defaultAccount = _from
    with pytest.raises(TypeError):
        coupon.transact().transfer(_to, _value)

# エラー系2: 入力値の型誤り（Value）
def test_transfer_error_2(web3, chain, users):
    _from = users['issuer']
    _to = users['trader']

    # 新規発行
    web3.eth.defaultAccount = _from
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 譲渡
    web3.eth.defaultAccount = _from
    with pytest.raises(TypeError):
        coupon.transact().transfer(_to, '0')

    with pytest.raises(TypeError):
        coupon.transact().transfer(_to, 2**256)

    with pytest.raises(TypeError):
        coupon.transact().transfer(_to, -1)

    with pytest.raises(TypeError):
        coupon.transact().transfer(_to, 0.1)

# エラー系3: 残高不足
def test_transfer_error_3(web3, chain, users):
    _from = users['issuer']
    _to = users['trader']

    # 新規発行
    web3.eth.defaultAccount = _from
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 譲渡（残高超）
    web3.eth.defaultAccount = _from
    _value = deploy_args[2] + 1
    txn_hash = coupon.transact().transfer(_to, _value) # エラーになる
    chain.wait.for_receipt(txn_hash)

    assert coupon.call().balanceOf(_from) == deploy_args[2]
    assert coupon.call().balanceOf(_to) == 0

# エラー系4: 譲渡不可クーポンの譲渡
def test_transfer_error_4(web3, chain, users):
    _from = users['issuer']
    _to = users['trader']

    # 新規発行
    web3.eth.defaultAccount = _from
    coupon, deploy_args = utils.issue_non_transferable_coupon(web3, chain)

    # 譲渡（譲渡不可）
    web3.eth.defaultAccount = _from
    _value = 1
    txn_hash = coupon.transact().transfer(_to, _value) # エラーになる
    chain.wait.for_receipt(txn_hash)

    assert coupon.call().balanceOf(_from) == deploy_args[2]
    assert coupon.call().balanceOf(_to) == 0

# エラー系5: 無効化されたクーポンの譲渡
def test_transfer_error_5(web3, chain, users):
    _issuer = users['issuer']
    _to = users['trader']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # クーポンの無効化
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().updateStatus(False)
    chain.wait.for_receipt(txn_hash)

    # 譲渡
    web3.eth.defaultAccount = _issuer
    _value = deploy_args[2]
    txn_hash = coupon.transact().transfer(_to, _value) #エラーになる
    chain.wait.for_receipt(txn_hash)

    assert coupon.call().balanceOf(_issuer) == deploy_args[2]
    assert coupon.call().balanceOf(_to) == 0


'''
TEST4_クーポンの消費（consume）
'''
# 正常系1
# ＜発行者＞発行　->　＜発行者＞消費
def test_consume_normal_1(web3, chain, users):
    _user = users['issuer']
    _value = 1

    # 新規発行
    web3.eth.defaultAccount = _user
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

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
def test_consume_normal_2(web3, chain, users):
    _issuer = users['issuer']
    _consumer = users['trader']
    _value = 1

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 割当
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().allocate(_consumer, _value)
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
def test_consume_error_1(web3, chain, users):
    _issuer = users['issuer']
    _consumer = users['trader']
    _value = '1'

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 消費
    web3.eth.defaultAccount = _issuer
    with pytest.raises(TypeError):
        coupon.transact().consume('0')

    with pytest.raises(TypeError):
        coupon.transact().consume(2**256)

    with pytest.raises(TypeError):
        coupon.transact().consume(-1)

    with pytest.raises(TypeError):
        coupon.transact().consume(0.1)

# エラー系2: 残高不足
def test_consume_error_2(web3, chain, users):
    _issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 消費
    web3.eth.defaultAccount = _issuer
    _value = deploy_args[2] + 1
    txn_hash = coupon.transact().consume(_value) # エラーになる
    chain.wait.for_receipt(txn_hash)

    assert coupon.call().balanceOf(_issuer) == deploy_args[2]
    assert coupon.call().usedOf(_issuer) == 0

# エラー系3: 無効化されたクーポンの消費
def test_consume_error_3(web3, chain, users):
    _issuer = users['issuer']
    _value = 1

    # クーポン新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # クーポンの無効化
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().updateStatus(False)
    chain.wait.for_receipt(txn_hash)

    # 消費
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().consume(_value) #エラーになる
    chain.wait.for_receipt(txn_hash)

    assert coupon.call().balanceOf(_issuer) == deploy_args[2]
    assert coupon.call().usedOf(_issuer) == 0


'''
TEST5_追加発行（issue）
'''
# 正常系1
# ＜発行者＞発行　->　＜発行者＞追加発行
def test_issue_normal_1(web3, chain, users):
    _issuer = users['issuer']
    _value = 1

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 追加発行
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().issue(_value)
    chain.wait.for_receipt(txn_hash)

    balance = coupon.call().balanceOf(_issuer)
    totalSupply = coupon.call().totalSupply()

    assert balance == deploy_args[2] + _value
    assert totalSupply == deploy_args[2] + _value

# 正常系2
# ＜発行者＞発行　->　＜発行者＞割当 -> ＜発行者＞追加発行
def test_issue_normal_2(web3, chain, users):
    _issuer = users['issuer']
    _consumer = users['trader']
    _allocated = 1
    _value = 10

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 割当
    txn_hash = coupon.transact().allocate(_consumer, _allocated)
    chain.wait.for_receipt(txn_hash)

    # 追加発行
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().issue(_value)
    chain.wait.for_receipt(txn_hash)

    balance = coupon.call().balanceOf(_issuer)
    totalSupply = coupon.call().totalSupply()

    assert balance == deploy_args[2] + _value - _allocated
    assert totalSupply == deploy_args[2] + _value

# エラー系1: 入力値の型誤り（Value）
def test_issue_error_1(web3, chain, users):
    _issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 追加発行
    web3.eth.defaultAccount = _issuer
    with pytest.raises(TypeError):
        coupon.transact().issue('0')

    with pytest.raises(TypeError):
        coupon.transact().issue(2**256)

    with pytest.raises(TypeError):
        coupon.transact().issue(-1)

    with pytest.raises(TypeError):
        coupon.transact().issue(0.1)

# エラー系2
# ＜発行者＞発行　->　＜発行者＞追加発行（uint最大値超）
def test_issue_error_2(web3, chain, users):
    _issuer = users['issuer']
    _consumer = users['trader']
    _allocated = 999999
    _value = 2**256 - 1

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 割当
    txn_hash = coupon.transact().allocate(_consumer, _allocated)
    chain.wait.for_receipt(txn_hash)

    # 追加発行（uint最大値超）
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().issue(_value) # エラーになる（2**256 -1 +1）
    chain.wait.for_receipt(txn_hash)

    balance = coupon.call().balanceOf(_issuer)
    totalSupply = coupon.call().totalSupply()

    assert balance == deploy_args[2] - _allocated
    assert totalSupply == deploy_args[2]

# エラー系3
# ＜発行者＞発行　->　＜発行者以外＞追加発行
def test_issue_error_3(web3, chain, users):
    _issuer = users['issuer']
    _other = users['trader']
    _value = 1000

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 追加発行（uint最大値超）
    web3.eth.defaultAccount = _other
    txn_hash = coupon.transact().issue(_value) # エラーになる
    chain.wait.for_receipt(txn_hash)

    balance = coupon.call().balanceOf(_issuer)
    totalSupply = coupon.call().totalSupply()

    assert balance == deploy_args[2]
    assert totalSupply == deploy_args[2]


'''
TEST6_クーポン詳細欄の更新（updateDetails）
'''
# 正常系1
# ＜発行者＞発行 -> ＜発行者＞詳細欄の修正
def test_updateDetails_normal_1(web3, chain, users):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 詳細欄の修正
    web3.eth.defaultAccount = issuer
    txn_hash = coupon.transact().updateDetails('updated details')
    chain.wait.for_receipt(txn_hash)

    details = coupon.call().details()
    assert details == 'updated details'

# エラー系1: 入力値の型誤り
def test_updateDetails_error_1(web3, chain, users):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 詳細欄の修正
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        coupon.transact().updateDetails(1234)

# エラー系2: 権限エラー
def test_updateDetails_error_2(web3, chain, users):
    issuer = users['issuer']
    other = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 詳細欄の修正
    web3.eth.defaultAccount = other
    txn_hash = coupon.transact().updateDetails('updated details')
    chain.wait.for_receipt(txn_hash)

    details = coupon.call().details()
    assert details == 'some_details'


'''
TEST7_メモ欄の更新（updateMemo）
'''
# 正常系1
# ＜発行者＞発行 -> ＜発行者＞メモ欄の修正
def test_updateMemo_normal_1(web3, chain, users):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # メモ欄の修正
    web3.eth.defaultAccount = issuer
    txn_hash = coupon.transact().updateMemo('updated memo')
    chain.wait.for_receipt(txn_hash)

    details = coupon.call().memo()
    assert details == 'updated memo'

# エラー系1: 入力値の型誤り
def test_updateMemo_error_1(web3, chain, users):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # メモ欄の修正
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        coupon.transact().updateMemo(1234)

# エラー系2: 権限エラー
def test_updateMemo_error_2(web3, chain, users):
    issuer = users['issuer']
    other = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # メモ欄の修正
    web3.eth.defaultAccount = other
    txn_hash = coupon.transact().updateMemo('updated memo')
    chain.wait.for_receipt(txn_hash)

    details = coupon.call().memo()
    assert details == 'some_memo'


'''
TEST8_残高確認（balanceOf）
'''
# 正常系1: クーポン新規作成 -> 残高確認
def test_balanceOf_normal_1(web3, chain, users):
    issuer = users['issuer']

    # 債券新規発行
    web3.eth.defaultAccount = issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    balance = coupon.call().balanceOf(issuer)
    assert balance == deploy_args[2]

# エラー系1: 入力値の型誤り（Owner）
def test_balanceOf_error_1(web3, chain, users):
    issuer = users['issuer']

    # 債券新規発行
    web3.eth.defaultAccount = issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    account_address = 1234

    with pytest.raises(TypeError):
        coupon.call().balanceOf(account_address)


'''
TEST9_使用済数量確認（usedOf）
'''
# 正常系1: クーポン作成 -> 消費 -> 使用済数量確認
def test_usedOf_normal_1(web3, chain, users):
    _issuer = users['issuer']
    _value = 1

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 消費
    web3.eth.defaultAccount = _issuer
    txn_hash = coupon.transact().consume(_value)
    chain.wait.for_receipt(txn_hash)

    # 使用済み数量確認
    used = coupon.call().usedOf(_issuer)

    assert used == _value

# エラー系1: 入力値の型誤り（Owner）
def test_usedOf_error_1(web3, chain, users):
    _issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = _issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    account_address = 1234

    with pytest.raises(TypeError):
        coupon.call().usedOf(account_address)


'''
TEST10_商品画像の設定（setImageURL, getImageURL）
'''
# 正常系1: 発行 -> 商品画像の設定
def test_setImageURL_normal_1(web3, chain, users):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # 商品画像の設定
    web3.eth.defaultAccount = issuer
    image_url = 'https://some_image_url.com/image.png'
    txn_hash = coupon.transact().setImageURL(0, image_url)
    chain.wait.for_receipt(txn_hash)

    image_url_0 = coupon.call().getImageURL(0)
    assert image_url_0 == image_url

# 正常系2: 発行 -> 商品画像の設定（複数設定）
def test_setImageURL_normal_2(web3, chain, users):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

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
def test_setImageURL_normal_3(web3, chain, users):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

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
def test_setImageURL_error_1(web3, chain, users):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

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
def test_setImageURL_error_2(web3, chain, users):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    image_url = 1234

    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        coupon.transact().setImageURL(0, image_url)

# エラー系3: 権限エラー
def test_setImageURL_error_3(web3, chain, users):
    issuer = users['issuer']
    other = users['admin']

    # 新規発行
    web3.eth.defaultAccount = issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    image_url = 'https://some_image_url.com/image.png'

    # 画像設定
    web3.eth.defaultAccount = other
    txn_hash = coupon.transact().setImageURL(0, image_url) # エラーになる
    chain.wait.for_receipt(txn_hash)

    image_url_0 = coupon.call().getImageURL(0)
    assert image_url_0 == ''


'''
TEST11_ステータス（有効・無効）の更新（updateStatus）
'''
# 正常系1
# ＜発行者＞発行 -> ＜発行者＞ステータスの修正
def test_updateStatus_normal_1(web3, chain, users):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # ステータスの修正
    web3.eth.defaultAccount = issuer
    txn_hash = coupon.transact().updateStatus(False)
    chain.wait.for_receipt(txn_hash)

    assert coupon.call().isValid() == False

# エラー系1: 入力値の型誤り
def test_updateStatus_error_1(web3, chain, users):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # ステータスの修正
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        coupon.transact().updateStatus('False')

# エラー系2: 権限エラー
def test_updateStatus_error_2(web3, chain, users):
    issuer = users['issuer']
    other = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    coupon, deploy_args = utils.issue_transferable_coupon(web3, chain)

    # メモ欄の修正
    web3.eth.defaultAccount = other
    txn_hash = coupon.transact().updateStatus(False)
    chain.wait.for_receipt(txn_hash)

    assert coupon.call().isValid() == True
