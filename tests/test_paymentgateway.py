import pytest

encrypted_message = 'encrypted_message'
encrypted_message_after = 'encrypted_message_after'
terms_text = 'terms_sample\nend'
terms_text_after = 'terms_sample\nafter\nend'

'''
TEST_デプロイ
'''


# 正常系1: デプロイ
def test_deploy_normal_1(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    payment_account = pg_contract.call().payment_accounts(trader, agent)
    account_approved = pg_contract.call().accountApproved(trader, agent)

    # デフォルトの登録情報の内容が正しいことを確認
    assert payment_account[0] == '0x0000000000000000000000000000000000000000'
    assert payment_account[1] == '0x0000000000000000000000000000000000000000'
    assert payment_account[2] == ''
    assert payment_account[3] == 0

    # 認可状態が未認可の状態であることを確認
    assert account_approved is False


'''
TEST_支払情報を登録（register）
'''


# 正常系1: 新規登録
def test_register_normal_1(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # PaymentGateway登録
    web3.eth.defaultAccount = trader
    txn_hash = pg_contract.transact().register(agent, encrypted_message)
    chain.wait.for_receipt(txn_hash)

    payment_account = pg_contract.call().payment_accounts(trader, agent)
    account_approved = pg_contract.call().accountApproved(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert account_approved is False


# 正常系2: 新規登録 -> 更新
def test_register_normal_2(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 登録 -> Success
    web3.eth.defaultAccount = trader
    txn_hash_1 = pg_contract.transact().register(agent, encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # 登録（２回目） -> Success
    web3.eth.defaultAccount = trader
    txn_hash_2 = pg_contract.transact().register(agent, encrypted_message_after)
    chain.wait.for_receipt(txn_hash_2)

    payment_account = pg_contract.call().payment_accounts(trader, agent)
    account_approved = pg_contract.call().accountApproved(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message_after
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert account_approved is False


# エラー系1:入力値の型誤り（agent address）
def test_register_error_1(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = 1234

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # PaymentGateway登録 -> Failure
    web3.eth.defaultAccount = trader
    with pytest.raises(TypeError):
        pg_contract.transact().register(agent, encrypted_message)


# エラー系2:入力値の型誤り（encrypted_info）
def test_register_error_2(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # PaymentGateway登録 -> Failure
    web3.eth.defaultAccount = trader
    with pytest.raises(TypeError):
        pg_contract.transact().register(agent, 1234)


# エラー系3: 登録 -> BAN -> 登録（２回目）
def test_register_error_3(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 新規登録 -> Success
    web3.eth.defaultAccount = trader
    txn_hash_1 = pg_contract.transact().register(agent, encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # BAN -> Success
    web3.eth.defaultAccount = agent
    txn_hash_2 = pg_contract.transact().ban(trader)
    chain.wait.for_receipt(txn_hash_2)

    # 登録（２回目） -> Failure
    web3.eth.defaultAccount = trader
    txn_hash_3 = pg_contract.transact().register(agent, encrypted_message_after)
    chain.wait.for_receipt(txn_hash_3)

    payment_account = pg_contract.call().payment_accounts(trader, agent)
    account_approved = pg_contract.call().accountApproved(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 4

    # 認可状態が未認可の状態であることを確認
    assert account_approved is False


'''
TEST_支払情報を承認する(approve)
'''


# 正常系1: 新規登録 -> 承認
def test_approve_normal_1(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 新規登録 -> Success
    web3.eth.defaultAccount = trader
    txn_hash_1 = pg_contract.transact().register(agent, encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # 承認 -> Success
    web3.eth.defaultAccount = agent
    txn_hash_2 = pg_contract.transact().approve(trader)
    chain.wait.for_receipt(txn_hash_2)

    payment_account = pg_contract.call().payment_accounts(trader, agent)
    account_approved = pg_contract.call().accountApproved(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 2

    # 認可状態が認可の状態であることを確認
    assert account_approved is True


# エラー系1: 入力値の型誤り
def test_approve_error_1(web3, chain, users):
    admin = users['admin']
    trader = 1234
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 承認 -> Failure
    web3.eth.defaultAccount = agent
    with pytest.raises(TypeError):
        pg_contract.transact().approve(trader)


# エラー系2: 登録なし -> 承認
def test_approve_error_2(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 承認 -> Failure
    web3.eth.defaultAccount = agent
    pg_contract.transact().approve(trader)

    payment_account = pg_contract.call().payment_accounts(trader, agent)

    assert payment_account[0] == '0x0000000000000000000000000000000000000000'


'''
TEST_支払情報を警告状態にする(warn)
'''


# 正常系1: 新規登録 -> 警告
def test_warn_normal_1(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 新規登録 -> Success
    web3.eth.defaultAccount = trader
    txn_hash_1 = pg_contract.transact().register(agent, encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # 警告 -> Success
    web3.eth.defaultAccount = agent
    txn_hash_2 = pg_contract.transact().warn(trader)
    chain.wait.for_receipt(txn_hash_2)

    payment_account = pg_contract.call().payment_accounts(trader, agent)
    account_approved = pg_contract.call().accountApproved(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 3

    # 認可状態が未認可の状態であることを確認
    assert account_approved is False


# エラー系1: 入力値の型誤り
def test_warn_error_1(web3, chain, users):
    admin = users['admin']
    trader = 1234
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 承認 -> Failure
    web3.eth.defaultAccount = agent
    with pytest.raises(TypeError):
        pg_contract.transact().warn(trader)


# エラー系2: 登録なし -> 警告
def test_warn_error_2(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 警告 -> Failure
    web3.eth.defaultAccount = agent
    pg_contract.transact().warn(trader)

    payment_account = pg_contract.call().payment_accounts(trader, agent)

    assert payment_account[0] == '0x0000000000000000000000000000000000000000'


'''
TEST_支払情報を非承認にする(unapprove)
'''


# 正常系1: 新規登録 -> 非承認
def test_unapprove_normal_1(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 新規登録 -> Success
    web3.eth.defaultAccount = trader
    txn_hash_1 = pg_contract.transact().register(agent, encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # 非承認 -> Success
    web3.eth.defaultAccount = agent
    txn_hash_2 = pg_contract.transact().unapprove(trader)
    chain.wait.for_receipt(txn_hash_2)

    payment_account = pg_contract.call().payment_accounts(trader, agent)
    account_approved = pg_contract.call().accountApproved(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert account_approved is False


# 正常系2: 新規登録 -> 承認 -> 非承認
# 認可状態が未認可の状態に戻る
def test_unapprove_normal_2(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 新規登録 -> Success
    web3.eth.defaultAccount = trader
    txn_hash_1 = pg_contract.transact().register(agent, encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # 承認 -> Success、　認可状態
    web3.eth.defaultAccount = agent
    txn_hash_2 = pg_contract.transact().approve(trader)
    chain.wait.for_receipt(txn_hash_2)

    # 非承認 -> Success。　未認可状態
    web3.eth.defaultAccount = agent
    txn_hash_3 = pg_contract.transact().unapprove(trader)
    chain.wait.for_receipt(txn_hash_3)

    payment_account = pg_contract.call().payment_accounts(trader, agent)
    account_approved = pg_contract.call().accountApproved(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert account_approved is False


# エラー系1: 入力値の型誤り
def test_unapprove_error_1(web3, chain, users):
    admin = users['admin']
    trader = 1234
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 非承認 -> Failure
    web3.eth.defaultAccount = agent
    with pytest.raises(TypeError):
        pg_contract.transact().unapprove(trader)


# エラー系2: 登録なし -> 非承認
def test_unapprove_error_2(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 非承認 -> Failure
    web3.eth.defaultAccount = agent
    pg_contract.transact().unapprove(trader)

    payment_account = pg_contract.call().payment_accounts(trader, agent)

    assert payment_account[0] == '0x0000000000000000000000000000000000000000'


'''
TEST_支払情報をBAN状態にする(ban)
'''


# 正常系1: 新規登録 -> BAN
def test_ban_normal_1(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 新規登録 -> Success
    web3.eth.defaultAccount = trader
    txn_hash_1 = pg_contract.transact().register(agent, encrypted_message)
    chain.wait.for_receipt(txn_hash_1)

    # BAN -> Success
    web3.eth.defaultAccount = agent
    txn_hash_2 = pg_contract.transact().ban(trader)
    chain.wait.for_receipt(txn_hash_2)

    payment_account = pg_contract.call().payment_accounts(trader, agent)
    account_approved = pg_contract.call().accountApproved(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 4

    # 認可状態が未認可の状態であることを確認
    assert account_approved is False


# エラー系1: 入力値の型誤り
def test_ban_error_1(web3, chain, users):
    admin = users['admin']
    trader = 1234
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 承認 -> Failure
    web3.eth.defaultAccount = agent
    with pytest.raises(TypeError):
        pg_contract.transact().ban(trader)


# エラー系2: 登録なし -> BAN
def test_ban_error_2(web3, chain, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # BAN -> Failure
    web3.eth.defaultAccount = agent
    pg_contract.transact().ban(trader)

    payment_account = pg_contract.call().payment_accounts(trader, agent)

    assert payment_account[0] == '0x0000000000000000000000000000000000000000'


'''
TEST_収納代行業者（Agent）の追加（addAgent）
'''


# 正常系1: 新規登録
def test_addAgent_normal_1(web3, chain, users):
    admin = users['admin']
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 収納代行業者（Agent）の追加
    web3.eth.defaultAccount = admin
    txn_hash = pg_contract.transact().addAgent(0, agent)
    chain.wait.for_receipt(txn_hash)

    agents = pg_contract.call().getAgents()
    assert agents[0] == agent
    assert len(agents) == 30


# 正常系2: 登録２回
def test_addAgent_normal_2(web3, chain, users):
    admin = users['admin']
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 収納代行業者（Agent）の追加
    web3.eth.defaultAccount = admin
    txn_hash = pg_contract.transact().addAgent(0, agent)
    chain.wait.for_receipt(txn_hash)

    # 収納代行業者（Agent）の追加（2回目）
    web3.eth.defaultAccount = admin
    txn_hash = pg_contract.transact().addAgent(0, agent)
    chain.wait.for_receipt(txn_hash)

    agents = pg_contract.call().getAgents()
    assert agents[0] == agent
    assert len(agents) == 30


# エラー系1: 入力値の型誤り（agent_id）
def test_addAgent_error_1(web3, chain, users):
    admin = users['admin']
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 収納代行業者（Agent）の追加
    web3.eth.defaultAccount = admin
    with pytest.raises(TypeError):
        pg_contract.transact().addAgent('0', agent)


# エラー系2: 入力値の型誤り（agent_address）
def test_addAgent_error_2(web3, chain, users):
    admin = users['admin']
    agent = '1234'

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 収納代行業者（Agent）の追加
    web3.eth.defaultAccount = admin
    with pytest.raises(TypeError):
        pg_contract.transact().addAgent(0, agent)


# エラー系3: リスト上限超
def test_addAgent_error_3(web3, chain, users):
    admin = users['admin']
    agent = users['agent']

    # PaymentGatewayデプロイ
    web3.eth.defaultAccount = admin
    pg_contract, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # 収納代行業者（Agent）の追加
    web3.eth.defaultAccount = admin
    txn_hash = pg_contract.transact().addAgent(30, agent)
    chain.wait.for_receipt(txn_hash)

    agents = pg_contract.call().getAgents()
    for agent_address in agents:
        assert agent_address == '0x0000000000000000000000000000000000000000'
    assert len(agents) == 30
