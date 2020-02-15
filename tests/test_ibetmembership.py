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


def deploy(chain, deploy_args):
    membership_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetMembership',
        deploy_args=deploy_args
    )
    return membership_contract


'''
TEST_デプロイ
'''


# 正常系1: deploy
def test_deploy_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    owner_address = membership_contract.call().owner()
    name = membership_contract.call().name()
    symbol = membership_contract.call().symbol()
    total_supply = membership_contract.call().totalSupply()
    tradable_exchange = membership_contract.call().tradableExchange()
    details = membership_contract.call().details()
    return_details = membership_contract.call().returnDetails()
    expiration_date = membership_contract.call().expirationDate()
    memo = membership_contract.call().memo()
    transferable = membership_contract.call().transferable()
    status = membership_contract.call().status()
    balance = membership_contract.call().balanceOf(issuer)
    contact_information = membership_contract.call().contactInformation()
    privacy_policy = membership_contract.call().privacyPolicy()

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
def test_deploy_error_1(chain, membership_exchange):
    deploy_args = init_args(membership_exchange.address)
    deploy_args[0] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetMembership',
            deploy_args=deploy_args
        )


# エラー系2: 入力値の型誤り（symbol）
def test_deploy_error_2(chain, membership_exchange):
    deploy_args = init_args(membership_exchange.address)
    deploy_args[1] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetMembership',
            deploy_args=deploy_args
        )


# エラー系3: 入力値の型誤り（initialSupply）
def test_deploy_error_3(chain, membership_exchange):
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = "10000"

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetMembership',
            deploy_args=deploy_args
        )


# エラー系4: 入力値の型誤り（details）
def test_deploy_error_4(chain, membership_exchange):
    deploy_args = init_args(membership_exchange.address)
    deploy_args[4] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetMembership',
            deploy_args=deploy_args
        )


# エラー系5: 入力値の型誤り（returnDetails）
def test_deploy_error_5(chain, membership_exchange):
    deploy_args = init_args(membership_exchange.address)
    deploy_args[5] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetMembership',
            deploy_args=deploy_args
        )


# エラー系6: 入力値の型誤り（expirationDate）
def test_deploy_error_6(chain, membership_exchange):
    deploy_args = init_args(membership_exchange.address)
    deploy_args[6] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetMembership',
            deploy_args=deploy_args
        )


# エラー系7: 入力値の型誤り（memo）
def test_deploy_error_7(chain, membership_exchange):
    deploy_args = init_args(membership_exchange.address)
    deploy_args[7] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetMembership',
            deploy_args=deploy_args
        )


# エラー系8: 入力値の型誤り（transferable）
def test_deploy_error_8(chain, membership_exchange):
    deploy_args = init_args(membership_exchange.address)
    deploy_args[8] = 'True'

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetMembership',
            deploy_args=deploy_args
        )


# エラー系9: 入力値の型誤り（tradableExchange）
def test_deploy_error_9(chain, membership_exchange):
    deploy_args = init_args(membership_exchange.address)
    deploy_args[3] = '0xaaaa'

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetMembership',
            deploy_args=deploy_args
        )


# エラー系10: 入力値の型誤り（contactInformation）
def test_deploy_error_10(chain, membership_exchange):
    deploy_args = init_args(membership_exchange.address)
    deploy_args[9] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetMembership', deploy_args=deploy_args)


# エラー系10: 入力値の型誤り（privacyPolicy）
def test_deploy_error_11(chain, membership_exchange):
    deploy_args = init_args(membership_exchange.address)
    deploy_args[10] = 1234

    with pytest.raises(TypeError):
        chain.provider.get_or_deploy_contract(
            'IbetMembership', deploy_args=deploy_args)


'''
TEST_トークンの振替（transfer）
'''


# 正常系1: アカウントアドレスへの振替
def test_transfer_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']
    transfer_amount = 100

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 振替
    txn_hash = membership_contract.transact().transfer(trader, transfer_amount)
    chain.wait.for_receipt(txn_hash)

    # 振替後の残高取得
    issuer_balance = membership_contract.call().balanceOf(issuer)
    trader_balance = membership_contract.call().balanceOf(trader)

    assert issuer_balance == deploy_args[2] - transfer_amount
    assert trader_balance == transfer_amount


# 正常系2: 会員権取引コントラクトへの振替
def test_transfer_normal_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    transfer_amount = 100

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    exchange_address = membership_exchange.address
    txn_hash = membership_contract.transact().transfer(exchange_address, transfer_amount)
    chain.wait.for_receipt(txn_hash)

    issuer_balance = membership_contract.call().balanceOf(issuer)
    exchange_balance = membership_contract.call().balanceOf(exchange_address)

    assert issuer_balance == deploy_args[2] - transfer_amount
    assert exchange_balance == transfer_amount


# 正常系3-1: 限界値：上限値
# アカウントアドレスへの振替
def test_transfer_normal_3_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2 ** 256 - 1  # 上限まで発行する
    membership_contract = deploy(chain, deploy_args)

    # 振替
    web3.eth.defaultAccount = issuer
    transfer_amount = 2 ** 256 - 1
    txn_hash = membership_contract.transact().transfer(trader, transfer_amount)
    chain.wait.for_receipt(txn_hash)

    assert membership_contract.call().balanceOf(issuer) == 0
    assert membership_contract.call().balanceOf(trader) == 2 ** 256 - 1


# 正常系3-2: 限界値：下限値
# アカウントアドレスへの振替
def test_transfer_normal_3_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 0
    membership_contract = deploy(chain, deploy_args)

    # 振替
    web3.eth.defaultAccount = issuer
    transfer_amount = 0
    txn_hash = membership_contract.transact().transfer(trader, transfer_amount)
    chain.wait.for_receipt(txn_hash)

    assert membership_contract.call().balanceOf(issuer) == 0
    assert membership_contract.call().balanceOf(trader) == 0


# 正常系3-3: 限界値：上限値
# コントラクトアドレスへの振替
def test_transfer_normal_3_3(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2 ** 256 - 1  # 上限まで発行する
    membership_contract = deploy(chain, deploy_args)

    # 振替
    web3.eth.defaultAccount = issuer
    exchange_address = membership_exchange.address
    transfer_amount = 2 ** 256 - 1
    txn_hash = membership_contract.transact(). \
        transfer(exchange_address, transfer_amount)
    chain.wait.for_receipt(txn_hash)

    assert membership_contract.call().balanceOf(issuer) == 0
    assert membership_contract.call().balanceOf(exchange_address) == 2 ** 256 - 1


# 正常系3-4: 限界値：下限値
# コントラクトアドレスへの振替
def test_transfer_normal_3_4(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 0
    membership_contract = deploy(chain, deploy_args)

    # 振替
    web3.eth.defaultAccount = issuer
    exchange_address = membership_exchange.address
    transfer_amount = 0
    txn_hash = membership_contract.transact(). \
        transfer(exchange_address, transfer_amount)
    chain.wait.for_receipt(txn_hash)

    assert membership_contract.call().balanceOf(issuer) == 0
    assert membership_contract.call().balanceOf(exchange_address) == 0


# エラー系1-1: 入力値の型誤り（to）
def test_transfer_error_1_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    to = 1234
    transfer_amount = 100

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 振替
    with pytest.raises(TypeError):
        membership_contract.transact().transfer(to, transfer_amount)


# エラー系1-2: 入力値の型誤り（value）
def test_transfer_error_1_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    to = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 振替（String）
    with pytest.raises(TypeError):
        membership_contract.transact().transfer(to, '100')

    # 振替（小数）
    with pytest.raises(TypeError):
        membership_contract.transact().transfer(to, 100.0)

    # 振替（負の値）
    with pytest.raises(TypeError):
        membership_contract.transact().transfer(to, -1)


# エラー系2: 限界値超
def test_transfer_error_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    to = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 振替（上限値超え）
    with pytest.raises(TypeError):
        membership_contract.transact().transfer(to, 2 ** 256)

    # 振替（下限値超え）
    with pytest.raises(TypeError):
        membership_contract.transact().transfer(to, -1)


# エラー系3: 残高不足
def test_transfer_error_3(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 振替（残高超）
    web3.eth.defaultAccount = issuer
    transfer_amount = 10000000000
    try:
        txn_hash = membership_contract.transact().transfer(trader, transfer_amount)
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    assert membership_contract.call().balanceOf(issuer) == deploy_args[2]
    assert membership_contract.call().balanceOf(trader) == 0


# エラー系4: private functionにアクセスできない
def test_transfer_error_4(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    transfer_amount = 100
    data = 0

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    with pytest.raises(ValueError):
        membership_contract.call().isContract(trader)

    with pytest.raises(ValueError):
        membership_contract.transact().transferToAddress(trader, transfer_amount, data)

    with pytest.raises(ValueError):
        membership_contract.transact().transferToContract(trader, transfer_amount, data)


# エラー系5: 譲渡不可
def test_transfer_error_5(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[8] = False
    membership_contract = deploy(chain, deploy_args)

    # 振替：譲渡不可
    web3.eth.defaultAccount = issuer
    transfer_amount = 10
    try:
        txn_hash = membership_contract.transact().transfer(trader, transfer_amount)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    assert membership_contract.call().balanceOf(issuer) == deploy_args[2]
    assert membership_contract.call().balanceOf(trader) == 0


# エラー系6: 取引不可Exchangeへの振替
def test_transfer_error_6(web3, chain, users, membership_exchange,
                          membership_exchange_storage, payment_gateway):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 取引不可Exchange
    web3.eth.defaultAccount = users['admin']
    dummy_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetCouponExchange',  # IbetMembershipExchange以外を読み込む必要がある
        deploy_args=[payment_gateway.address, membership_exchange_storage.address]
    )

    # 振替
    web3.eth.defaultAccount = issuer
    transfer_amount = 10
    try:
        txn_hash = membership_contract.transact().transfer(dummy_exchange.address, transfer_amount)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    assert membership_contract.call().balanceOf(issuer) == deploy_args[2]
    assert membership_contract.call().balanceOf(dummy_exchange.address) == 0


'''
TEST_トークンの移転（transferFrom）
'''


# 正常系1: アカウントアドレスへの移転
def test_transferFrom_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    from_address = users['admin']
    to_address = users['trader']
    value = 100

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 譲渡（issuer -> from_address）
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact(). \
        transfer(from_address, value)
    chain.wait.for_receipt(txn_hash)

    # 移転（_from -> _to）
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact(). \
        transferFrom(from_address, to_address, value)
    chain.wait.for_receipt(txn_hash)

    issuer_balance = membership_contract.call().balanceOf(issuer)
    from_balance = membership_contract.call().balanceOf(from_address)
    to_balance = membership_contract.call().balanceOf(to_address)

    assert issuer_balance == deploy_args[2] - value
    assert from_balance == 0
    assert to_balance == value


# 正常系2: コントラクトアドレスへの移転
def test_transferFrom_normal_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    from_address = users['trader']
    value = 100

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)
    to_address = membership_exchange.address

    # 譲渡（issuer -> from_address）
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact(). \
        transfer(from_address, value)
    chain.wait.for_receipt(txn_hash)

    # 移転（_from -> _to）
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact(). \
        transferFrom(from_address, to_address, value)
    chain.wait.for_receipt(txn_hash)

    issuer_balance = membership_contract.call().balanceOf(issuer)
    from_balance = membership_contract.call().balanceOf(from_address)
    to_balance = membership_contract.call().balanceOf(to_address)

    assert issuer_balance == deploy_args[2] - value
    assert from_balance == 0
    assert to_balance == value


# 正常系3-1: 限界値：上限値
#  アカウントアドレスへの移転
def test_transferFrom_normal_3_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    from_address = users['admin']
    to_address = users['trader']
    max_value = 2 ** 256 - 1

    # 発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = max_value
    membership_contract = deploy(chain, deploy_args)

    # 譲渡（issuer -> from_address）
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact(). \
        transfer(from_address, max_value)
    chain.wait.for_receipt(txn_hash)

    # 移転（from -> to）
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact(). \
        transferFrom(from_address, to_address, max_value)
    chain.wait.for_receipt(txn_hash)

    issuer_balance = membership_contract.call().balanceOf(issuer)
    from_balance = membership_contract.call().balanceOf(from_address)
    to_balance = membership_contract.call().balanceOf(to_address)

    assert issuer_balance == 0
    assert from_balance == 0
    assert to_balance == max_value


# 正常系3-2: 限界値：下限値
#  アカウントアドレスへの移転
def test_transferFrom_normal_3_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    from_address = users['admin']
    to_address = users['trader']
    min_value = 0

    # 発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = min_value
    membership_contract = deploy(chain, deploy_args)

    # 譲渡（issuer -> from_address）
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact(). \
        transfer(from_address, min_value)
    chain.wait.for_receipt(txn_hash)

    # 移転（from -> to）
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact(). \
        transferFrom(from_address, to_address, min_value)
    chain.wait.for_receipt(txn_hash)

    issuer_balance = membership_contract.call().balanceOf(issuer)
    from_balance = membership_contract.call().balanceOf(from_address)
    to_balance = membership_contract.call().balanceOf(to_address)

    assert issuer_balance == 0
    assert from_balance == 0
    assert to_balance == 0


# 正常系3-3: 限界値：上限値
#  コントラクトアドレスへの移転
def test_transferFrom_normal_3_3(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    from_address = users['admin']
    max_value = 2 ** 256 - 1

    # 発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = max_value
    membership_contract = deploy(chain, deploy_args)

    # Exchangeコントラクトのデプロイ
    exchange_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetMembershipExchange',
        deploy_transaction={'gas': 6000000},
        deploy_args=[]
    )
    to_address = exchange_contract.address

    # 譲渡（issuer -> from_address）
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact(). \
        transfer(from_address, max_value)
    chain.wait.for_receipt(txn_hash)

    # 移転（from -> to）
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact(). \
        transferFrom(from_address, to_address, max_value)
    chain.wait.for_receipt(txn_hash)

    issuer_balance = membership_contract.call().balanceOf(issuer)
    from_balance = membership_contract.call().balanceOf(from_address)
    to_balance = membership_contract.call().balanceOf(to_address)

    assert issuer_balance == 0
    assert from_balance == 0
    assert to_balance == max_value


# 正常系3-4: 限界値：下限値
#  コントラクトアドレスへの移転
def test_transferFrom_normal_3_4(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    from_address = users['admin']
    min_value = 0

    # 発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = min_value
    membership_contract = deploy(chain, deploy_args)

    # Exchangeコントラクトのデプロイ
    exchange_contract, _ = chain.provider.get_or_deploy_contract(
        'IbetMembershipExchange',
        deploy_transaction={'gas': 6000000},
        deploy_args=[]
    )
    to_address = exchange_contract.address

    # 譲渡（issuer -> from_address）
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact(). \
        transfer(from_address, min_value)
    chain.wait.for_receipt(txn_hash)

    # 移転（from -> to）
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact(). \
        transferFrom(from_address, to_address, min_value)
    chain.wait.for_receipt(txn_hash)

    issuer_balance = membership_contract.call().balanceOf(issuer)
    from_balance = membership_contract.call().balanceOf(from_address)
    to_balance = membership_contract.call().balanceOf(to_address)

    assert issuer_balance == 0
    assert from_balance == 0
    assert to_balance == 0


# エラー系1-1: 入力値の型誤り（from_address）
def test_transferFrom_error_1_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    to_address = users['trader']
    value = 100

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # String
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact(). \
            transferFrom('1234', to_address, value)

    # Int
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact(). \
            transferFrom(1234, to_address, value)


# エラー系1-2: 入力値の型誤り（to_address）
def test_transferFrom_error_1_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    value = 100

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # String
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact(). \
            transferFrom(issuer, '1234', value)

    # Int
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact(). \
            transferFrom(issuer, 1234, value)


# エラー系1-3: 入力値の型誤り（value）
def test_transferFrom_error_1_3(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    to_address = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # String
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact(). \
            transferFrom(issuer, to_address, '100')

    # 小数
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact(). \
            transferFrom(issuer, to_address, 100.0)

    # 負の値
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact(). \
            transferFrom(issuer, to_address, -1)


# エラー系2: 限界値超
def test_transferFrom_error_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    to_address = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 上限値超
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact(). \
            transferFrom(issuer, to_address, 2 ** 256)

    # 下限値超
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact(). \
            transferFrom(issuer, to_address, -1)


# エラー系3: 残高不足
def test_transferFrom_error_3(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    to_address = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 残高超
    web3.eth.defaultAccount = issuer
    transfer_amount = 10000000000
    try:
        txn_hash = membership_contract.transact().transferFrom(issuer, to_address, transfer_amount)
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    assert membership_contract.call().balanceOf(issuer) == deploy_args[2]
    assert membership_contract.call().balanceOf(to_address) == 0


# エラー系4: 権限エラー（発行者以外が実行）
def test_transferFrom_error_4(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    admin = users['admin']
    to_address = users['trader']
    transfer_amount = 100

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 残高超
    web3.eth.defaultAccount = admin
    try:
       txn_hash = membership_contract.transact().transferFrom(issuer, to_address, transfer_amount)  # エラーになる
       chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    assert membership_contract.call().balanceOf(issuer) == deploy_args[2]
    assert membership_contract.call().balanceOf(to_address) == 0


'''
TEST_残高確認（balanceOf）
'''


# 正常系1: 発行 -> 残高確認
def test_balanceOf_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    balance = membership_contract.call().balanceOf(issuer)
    assert balance == deploy_args[2]


# 正常系2: データなし -> 残高ゼロ
def test_balanceOf_normal_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    balance = membership_contract.call().balanceOf(trader)
    assert balance == 0


# エラー系1: 入力値の型誤り
def test_balanceOf_error_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 型誤り：String
    with pytest.raises(TypeError):
        membership_contract.call().balanceOf('1234')

    # 型誤り：Int
    with pytest.raises(TypeError):
        membership_contract.call().balanceOf(1234)


'''
TEST_会員権詳細更新（setDetails）
'''


# 正常系1: 発行 -> 詳細更新
def test_setDetails_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    after_details = 'after_details'

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 会員権詳細更新
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact(). \
        setDetails(after_details)
    chain.wait.for_receipt(txn_hash)

    details = membership_contract.call().details()
    assert after_details == details


# エラー系1: 入力値の型誤り
def test_setDetails_error_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 型誤り
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact().setDetails(1234)


# エラー系2: 権限エラー
def test_setDetails_error_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    attacker = users['trader']
    after_details = 'after_details'

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 会員権詳細更新
    web3.eth.defaultAccount = attacker
    try:
        txn_hash = membership_contract.transact().setDetails(after_details)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    details = membership_contract.call().details()
    assert details == deploy_args[4]


'''
TEST_リターン詳細更新（setReturnDetails）
'''


# 正常系1: 発行 -> 詳細更新
def test_setReturnDetails_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    after_return_details = 'after_return_details'

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # リターン詳細更新
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact(). \
        setReturnDetails(after_return_details)
    chain.wait.for_receipt(txn_hash)

    return_details = membership_contract.call().returnDetails()
    assert after_return_details == return_details


# エラー系1: 入力値の型誤り
def test_setReturnDetails_error_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 型誤り
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact().setReturnDetails(1234)


# エラー系2: 権限エラー
def test_setReturnDetails_error_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    attacker = users['trader']
    after_return_details = 'after_return_details'

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # リターン詳細更新：権限エラー
    web3.eth.defaultAccount = attacker
    try:
        txn_hash = membership_contract.transact().setReturnDetails(after_return_details)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    return_details = membership_contract.call().returnDetails()
    assert return_details == deploy_args[5]


'''
TEST_有効期限更新（setExpirationDate）
'''


# 正常系1: 発行 -> 有効期限更新
def test_setExpirationDate_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    after_expiration_date = 'after_expiration_date'

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 有効期限更新
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact(). \
        setExpirationDate(after_expiration_date)
    chain.wait.for_receipt(txn_hash)

    expiration_date = membership_contract.call().expirationDate()
    assert after_expiration_date == expiration_date


# エラー系1: 入力値の型誤り
def test_setExpirationDate_errors_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 型誤り
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact().setExpirationDate(1234)


# エラー系2: 権限エラー
def test_setExpirationDate_error_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    attacker = users['trader']
    after_expiration_date = 'after_expiration_date'

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 有効期限更新：権限エラー
    web3.eth.defaultAccount = attacker
    try:
        txn_hash = membership_contract.transact().setExpirationDate(after_expiration_date)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    expiration_date = membership_contract.call().expirationDate()
    assert expiration_date == deploy_args[6]


'''
TEST_メモ欄更新（setMemo）
'''


# 正常系1: 発行 -> メモ欄更新
def test_setMemo_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    after_memo = 'after_memo'

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # メモ欄更新
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact().setMemo(after_memo)
    chain.wait.for_receipt(txn_hash)

    memo = membership_contract.call().memo()
    assert after_memo == memo


# エラー系1: 入力値の型誤り
def test_setMemo_error_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 型誤り
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact().setMemo(1234)


# エラー系1: 権限エラー
def test_setMemo_error_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    attacker = users['trader']
    after_memo = 'after_memo'

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # メモ欄更新：権限エラー
    web3.eth.defaultAccount = attacker
    try:
        txn_hash = membership_contract.transact().setMemo(after_memo)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    memo = membership_contract.call().memo()
    assert memo == deploy_args[7]


'''
TEST_譲渡可能更新（setTransferable）
'''


# 正常系1: 発行 -> 譲渡可能更新
def test_setTransferable_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    after_transferable = False

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 譲渡可能更新
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact().setTransferable(after_transferable)
    chain.wait.for_receipt(txn_hash)

    transferable = membership_contract.call().transferable()
    assert after_transferable == transferable


# エラー系1: 入力値の型誤り
def test_setTransferable_error_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 型誤り
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact().setTransferable('True')


# エラー系2: 権限エラー
def test_setTransferable_error_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    attacker = users['trader']
    after_transferable = False

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 譲渡可能更新
    web3.eth.defaultAccount = attacker
    try:
        txn_hash = membership_contract.transact().setTransferable(after_transferable)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    transferable = membership_contract.call().transferable()
    assert transferable == deploy_args[8]


'''
TEST_取扱ステータス更新（setStatus）
'''


# 正常系1: 発行 -> 取扱ステータス更新
def test_setStatus_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    after_status = False

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 取扱ステータス更新
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact().setStatus(after_status)
    chain.wait.for_receipt(txn_hash)

    status = membership_contract.call().status()
    assert after_status == status


# エラー系1: 入力値の型誤り
def test_setStatus_error_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 型誤り
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact().setStatus('True')


# エラー系2: 権限エラー
def test_setStatus_error_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    attacker = users['trader']
    after_status = False

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 取扱ステータス更新
    web3.eth.defaultAccount = attacker
    try:
        txn_hash = membership_contract.transact().setStatus(after_status)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    status = membership_contract.call().status()
    assert status is True


'''
TEST_商品画像更新（setImageURL, getImageURL）
'''


# 正常系1: 発行 -> 商品画像更新
def test_setImageURL_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    after_url = 'http://hoge.com'

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 商品画像更新
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact().setImageURL(0, after_url)
    chain.wait.for_receipt(txn_hash)

    url = membership_contract.call().getImageURL(0)
    assert after_url == url


# エラー系1-1: 入力値の型誤り：Class
def test_setImageURL_error_1_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 型誤り
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact().setImageURL('0', 'after_url')


# エラー系1-2: 入力値の型誤り：ImageURL
def test_setImageURL_error_1_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 型誤り
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact().setImageURL(0, 1234)


# エラー系2: 権限エラー
def test_setImageURL_error_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    attacker = users['trader']
    after_url = 'http://hoge.com'

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 商品画像更新
    web3.eth.defaultAccount = attacker
    try:
        txn_hash = membership_contract.transact().setImageURL(0, after_url)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    url = membership_contract.call().getImageURL(0)
    assert url == ''


'''
TEST_追加発行（issue）
'''


# 正常系1: 発行 -> 追加発行
def test_issue_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    value = 10

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 追加発行
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact().issue(value)
    chain.wait.for_receipt(txn_hash)

    total_supply = membership_contract.call().totalSupply()
    balance = membership_contract.call().balanceOf(issuer)

    assert total_supply == deploy_args[2] + value
    assert balance == deploy_args[2] + value


# 正常系2: 限界値
def test_issue_normal_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2 ** 256 - 2
    membership_contract = deploy(chain, deploy_args)

    # 追加発行（限界値）
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact().issue(1)
    chain.wait.for_receipt(txn_hash)

    total_supply = membership_contract.call().totalSupply()
    balance = membership_contract.call().balanceOf(issuer)

    assert total_supply == 2 ** 256 - 1
    assert balance == 2 ** 256 - 1


# エラー系1: 入力値の型誤り
def test_issue_error_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # String
    with pytest.raises(TypeError):
        membership_contract.transact().issue("1")

    # 小数
    with pytest.raises(TypeError):
        membership_contract.transact().issue(1.0)


# エラー系2: 限界値超
def test_issue_error_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 上限値超
    with pytest.raises(TypeError):
        membership_contract.transact().issue(2 ** 256)

    # 下限値超
    with pytest.raises(TypeError):
        membership_contract.transact().issue(-1)


# エラー系3: 発行→追加発行→上限界値超
def test_issue_error_3(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    deploy_args[2] = 2 ** 256 - 1  # 限界値
    membership_contract = deploy(chain, deploy_args)

    # 追加発行（限界値超）
    web3.eth.defaultAccount = issuer
    try:
        txn_hash = membership_contract.transact().issue(1)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    total_supply = membership_contract.call().totalSupply()
    balance = membership_contract.call().balanceOf(issuer)

    assert total_supply == deploy_args[2]
    assert balance == deploy_args[2]


# エラー系4: 権限エラー
def test_issue_error_4(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    attacker = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 追加発行：権限エラー
    web3.eth.defaultAccount = attacker
    try:
        txn_hash = membership_contract.transact().issue(1)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    total_supply = membership_contract.call().totalSupply()
    balance = membership_contract.call().balanceOf(issuer)

    assert total_supply == deploy_args[2]
    assert balance == deploy_args[2]


'''
TEST_取引可能Exchangeの更新（setTradableExchange）
'''


# 正常系1: 発行 -> Exchangeの更新
def test_setTradableExchange_normal_1(web3, chain, users, membership_exchange,
                                      membership_exchange_storage, payment_gateway):
    issuer = users['issuer']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # その他Exchange
    web3.eth.defaultAccount = users['admin']
    other_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetCouponExchange',  # IbetMembershipExchange以外を読み込む必要がある
        deploy_args=[payment_gateway.address, membership_exchange_storage.address]
    )

    # Exchangeの更新
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact(). \
        setTradableExchange(other_exchange.address)
    chain.wait.for_receipt(txn_hash)

    assert membership_contract.call().tradableExchange() == to_checksum_address(other_exchange.address)


# エラー系1: 発行 -> Exchangeの更新（入力値の型誤り）
def test_setTradableExchange_error_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # Exchangeの更新
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact().setTradableExchange('0xaaaa')


# エラー系2: 発行 -> Exchangeの更新（権限エラー）
def test_setTradableExchange_error_2(web3, chain, users, membership_exchange,
                                     membership_exchange_storage, payment_gateway):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # その他Exchange
    web3.eth.defaultAccount = users['admin']
    other_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetCouponExchange',  # IbetMembershipExchange以外を読み込む必要がある
        deploy_args=[payment_gateway.address, membership_exchange_storage.address]
    )

    # Exchangeの更新
    web3.eth.defaultAccount = trader
    try:
        txn_hash = membership_contract.transact().setTradableExchange(other_exchange.address)  # エラーになる
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    assert membership_contract.call().tradableExchange() == to_checksum_address(membership_exchange.address)


'''
TEST_新規募集ステータス更新（setInitialOfferingStatus）
'''


# 正常系1: 発行 -> 新規募集ステータス更新（False→True）
def test_setInitialOfferingStatus_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 初期状態 == False
    assert membership_contract.call().initialOfferingStatus() is False

    # 新規募集ステータスの更新
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact().setInitialOfferingStatus(True)
    chain.wait.for_receipt(txn_hash)

    assert membership_contract.call().initialOfferingStatus() is True


# 正常系2:
#   発行 -> 新規募集ステータス更新（False→True） -> 2回目更新（True→False）
def test_setInitialOfferingStatus_normal_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 新規募集ステータスの更新
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact().setInitialOfferingStatus(True)
    chain.wait.for_receipt(txn_hash)

    # 新規募集ステータスの更新（2回目）
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact().setInitialOfferingStatus(False)
    chain.wait.for_receipt(txn_hash)

    assert membership_contract.call().initialOfferingStatus() is False


# エラー系1: 発行 -> 新規募集ステータス更新（入力値の型誤り）
def test_setInitialOfferingStatus_error_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 新規募集ステータスの更新
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact().setInitialOfferingStatus('True')


'''
TEST_募集申込（applyForOffering）
'''


# 正常系1
#   発行：発行体 -> 投資家：募集申込
def test_applyForOffering_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 新規募集ステータスの更新
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact().setInitialOfferingStatus(True)
    chain.wait.for_receipt(txn_hash)

    # 募集申込
    web3.eth.defaultAccount = trader
    txn_hash = membership_contract.transact().applyForOffering('abcdefgh')
    chain.wait.for_receipt(txn_hash)

    assert membership_contract.call().applications(trader) == 'abcdefgh'


# 正常系2
#   発行：発行体 -> （申込なし）初期データ参照
def test_applyForOffering_normal_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 新規募集ステータスの更新
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact().setInitialOfferingStatus(True)
    chain.wait.for_receipt(txn_hash)

    assert membership_contract.call().applications(trader) == ''


# エラー系1:
#   発行：発行体 -> 投資家：募集申込（入力値の型誤り）
def test_applyForOffering_error_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 新規募集ステータスの更新
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact().setInitialOfferingStatus(True)
    chain.wait.for_receipt(txn_hash)

    # 募集申込
    web3.eth.defaultAccount = trader
    with pytest.raises(TypeError):
        membership_contract.transact().applyForOffering(1234)


# エラー系2:
#   発行：発行体 -> 投資家：募集申込（申込ステータスが停止中）
def test_applyForOffering_error_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    trader = users['trader']

    # トークン新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 募集申込
    web3.eth.defaultAccount = trader
    try:
        txn_hash = membership_contract.transact().applyForOffering('abcdefgh')
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    assert membership_contract.call().applications(trader) == ''


'''
TEST_問い合わせ先情報の更新（setContactInformation）
'''


# 正常系1
# ＜発行者＞発行 -> ＜発行者＞問い合わせ先情報の修正
def test_setContactInformation_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 修正
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact().setContactInformation('updated contact information')
    chain.wait.for_receipt(txn_hash)

    contact_information = membership_contract.call().contactInformation()
    assert contact_information == 'updated contact information'


# エラー系1: 入力値の型誤り
def test_setContactInformation_error_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 修正
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact().setContactInformation(1234)


# エラー系2: 権限エラー
def test_setContactInformation_error_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    other = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 修正
    web3.eth.defaultAccount = other
    try:
        txn_hash = membership_contract.transact().setContactInformation('updated contact information')
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    contact_information = membership_contract.call().contactInformation()
    assert contact_information == 'some_contact_information'


'''
TEST_プライバシーポリシーの更新（setPrivacyPolicy）
'''


# 正常系1
# ＜発行者＞発行 -> ＜発行者＞プライバシーポリシーの修正
def test_setPrivacyPolicy_normal_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 修正
    web3.eth.defaultAccount = issuer
    txn_hash = membership_contract.transact().setPrivacyPolicy('updated privacy policy')
    chain.wait.for_receipt(txn_hash)

    privacy_policy = membership_contract.call().privacyPolicy()
    assert privacy_policy == 'updated privacy policy'


# エラー系1: 入力値の型誤り
def test_setPrivacyPolicy_error_1(web3, chain, users, membership_exchange):
    issuer = users['issuer']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 修正
    web3.eth.defaultAccount = issuer
    with pytest.raises(TypeError):
        membership_contract.transact().setPrivacyPolicy(1234)


# エラー系2: 権限エラー
def test_setPrivacyPolicy_error_2(web3, chain, users, membership_exchange):
    issuer = users['issuer']
    other = users['trader']

    # 新規発行
    web3.eth.defaultAccount = issuer
    deploy_args = init_args(membership_exchange.address)
    membership_contract = deploy(chain, deploy_args)

    # 修正
    web3.eth.defaultAccount = other
    try:
        txn_hash = membership_contract.transact().setPrivacyPolicy('updated privacy policy')
        chain.wait.for_receipt(txn_hash)
    except ValueError:
        pass

    privacy_policy = membership_contract.call().privacyPolicy()
    assert privacy_policy == 'some_privacy_policy'