import pytest

encrypted_message = 'encrypted_message'
encrypted_message_after = 'encrypted_message_after'
terms_text = 'terms_sample\nend'
terms_text_after = 'terms_sample\nafter\nend'

'''
TEST_デプロイ
'''


# 正常系1: デプロイ
def test_deploy_normal_1(PaymentGateway, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    payment_account = pg_contract.payment_accounts(trader, agent)
    account_approved = pg_contract.accountApproved(trader, agent)

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
def test_register_normal_1(PaymentGateway, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # PaymentGateway登録
    pg_contract.register.transact(agent, encrypted_message, {'from': trader})

    payment_account = pg_contract.payment_accounts(trader, agent)
    account_approved = pg_contract.accountApproved(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert account_approved is False


# 正常系2: 新規登録 -> 更新
def test_register_normal_2(PaymentGateway, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 登録 -> Success
    pg_contract.register.transact(agent, encrypted_message, {'from': trader})

    # 登録（２回目） -> Success
    pg_contract.register.transact(agent, encrypted_message_after, {'from': trader})

    payment_account = pg_contract.payment_accounts(trader, agent)
    account_approved = pg_contract.accountApproved(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message_after
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert account_approved is False


# エラー系1:入力値の型誤り（agent address）
def test_register_error_1(PaymentGateway, users):
    admin = users['admin']
    trader = users['trader']
    agent = 1234

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # PaymentGateway登録 -> Failure
    with pytest.raises(ValueError):
        pg_contract.register.transact(agent, encrypted_message, {'from': trader})


# エラー系2:入力値の型誤り（encrypted_info）
def test_register_error_2(PaymentGateway, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # PaymentGateway登録 -> Failure
    with pytest.raises(ValueError):
        pg_contract.register.transact(agent, '0x66aB6D9362d4F35596279692F0251Db635165871', {'from': trader})


# エラー系3: 登録 -> BAN -> 登録（２回目）
def test_register_error_3(PaymentGateway, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 新規登録 -> Success
    pg_contract.register.transact(agent, encrypted_message, {'from': trader})

    # BAN -> Success
    pg_contract.ban.transact(trader, {'from': agent})

    # 登録（２回目） -> Failure
    pg_contract.register.transact(agent, encrypted_message_after, {'from': trader})

    payment_account = pg_contract.payment_accounts(trader, agent)
    account_approved = pg_contract.accountApproved(trader, agent)

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
def test_approve_normal_1(PaymentGateway, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 新規登録 -> Success
    pg_contract.register.transact(agent, encrypted_message, {'from': trader})

    # 承認 -> Success
    pg_contract.approve.transact(trader, {'from': agent})

    payment_account = pg_contract.payment_accounts(trader, agent)
    account_approved = pg_contract.accountApproved(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 2

    # 認可状態が認可の状態であることを確認
    assert account_approved is True


# エラー系1: 入力値の型誤り
def test_approve_error_1(PaymentGateway, users):
    admin = users['admin']
    trader = 1234
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 承認 -> Failure
    with pytest.raises(ValueError):
        pg_contract.approve.transact(trader, {'from': agent})


# エラー系2: 登録なし -> 承認
def test_approve_error_2(PaymentGateway, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 承認 -> Failure
    pg_contract.approve.transact(trader, {'from': agent})

    payment_account = pg_contract.payment_accounts(trader, agent)
    assert payment_account[0] == '0x0000000000000000000000000000000000000000'


'''
TEST_支払情報を警告状態にする(warn)
'''


# 正常系1: 新規登録 -> 警告
def test_warn_normal_1(PaymentGateway, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 新規登録 -> Success
    pg_contract.register.transact(agent, encrypted_message, {'from': trader})

    # 警告 -> Success
    pg_contract.warn.transact(trader, {'from': agent})

    payment_account = pg_contract.payment_accounts(trader, agent)
    account_approved = pg_contract.accountApproved(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 3

    # 認可状態が未認可の状態であることを確認
    assert account_approved is False


# エラー系1: 入力値の型誤り
def test_warn_error_1(PaymentGateway, users):
    admin = users['admin']
    trader = 1234
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 承認 -> Failure
    with pytest.raises(ValueError):
        pg_contract.warn.transact(trader, {'from': agent})


# エラー系2: 登録なし -> 警告
def test_warn_error_2(PaymentGateway, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 警告 -> Failure
    pg_contract.warn.transact(trader, {'from': agent})

    payment_account = pg_contract.payment_accounts(trader, agent)
    assert payment_account[0] == '0x0000000000000000000000000000000000000000'


'''
TEST_支払情報を非承認にする(unapprove)
'''


# 正常系1: 新規登録 -> 非承認
def test_unapprove_normal_1(PaymentGateway, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 新規登録 -> Success
    pg_contract.register.transact(agent, encrypted_message, {'from': trader})

    # 非承認 -> Success
    pg_contract.unapprove.transact(trader, {'from': agent})

    payment_account = pg_contract.payment_accounts(trader, agent)
    account_approved = pg_contract.accountApproved(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert account_approved is False


# 正常系2: 新規登録 -> 承認 -> 非承認
# 認可状態が未認可の状態に戻る
def test_unapprove_normal_2(PaymentGateway, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 新規登録 -> Success
    pg_contract.register.transact(agent, encrypted_message, {'from': trader})

    # 承認 -> Success、　認可状態
    pg_contract.approve.transact(trader, {'from': agent})

    # 非承認 -> Success。　未認可状態
    pg_contract.unapprove.transact(trader, {'from': agent})

    payment_account = pg_contract.payment_accounts(trader, agent)
    account_approved = pg_contract.accountApproved(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 1

    # 認可状態が未認可の状態であることを確認
    assert account_approved is False


# エラー系1: 入力値の型誤り
def test_unapprove_error_1(PaymentGateway, users):
    admin = users['admin']
    trader = 1234
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 非承認 -> Failure
    with pytest.raises(ValueError):
        pg_contract.unapprove.transact(trader, {'from': agent})


# エラー系2: 登録なし -> 非承認
def test_unapprove_error_2(PaymentGateway, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 非承認 -> Failure
    pg_contract.unapprove.transact(trader, {'from': agent})

    payment_account = pg_contract.payment_accounts(trader, agent)

    assert payment_account[0] == '0x0000000000000000000000000000000000000000'


'''
TEST_支払情報をBAN状態にする(ban)
'''


# 正常系1: 新規登録 -> BAN
def test_ban_normal_1(PaymentGateway, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 新規登録 -> Success
    pg_contract.register.transact(agent, encrypted_message, {'from': trader})

    # BAN -> Success
    pg_contract.ban.transact(trader, {'from': agent})

    payment_account = pg_contract.payment_accounts(trader, agent)
    account_approved = pg_contract.accountApproved(trader, agent)

    # 登録情報の内容が正しいことを確認
    assert payment_account[0] == trader
    assert payment_account[1] == agent
    assert payment_account[2] == encrypted_message
    assert payment_account[3] == 4

    # 認可状態が未認可の状態であることを確認
    assert account_approved is False


# エラー系1: 入力値の型誤り
def test_ban_error_1(PaymentGateway, users):
    admin = users['admin']
    trader = 1234
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 承認 -> Failure
    with pytest.raises(ValueError):
        pg_contract.ban.transact(trader, {'from': agent})


# エラー系2: 登録なし -> BAN
def test_ban_error_2(PaymentGateway, users):
    admin = users['admin']
    trader = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # BAN -> Failure
    pg_contract.ban.transact(trader, {'from': agent})

    payment_account = pg_contract.payment_accounts(trader, agent)

    assert payment_account[0] == '0x0000000000000000000000000000000000000000'


'''
TEST_収納代行業者の追加（addAgent）
'''


# 正常系1: 新規登録
def test_addAgent_normal_1(PaymentGateway, users):
    admin = users['admin']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 収納代行業者（Agent）の追加
    pg_contract.addAgent.transact(agent, {'from': admin})

    agent_available = pg_contract.getAgent(agent)
    assert agent_available == True


# 正常系2: 登録２回（同一アドレス）
def test_addAgent_normal_2(PaymentGateway, users):
    admin = users['admin']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 収納代行業者（Agent）の追加
    pg_contract.addAgent.transact(agent, {'from': admin})

    # 収納代行業者（Agent）の追加（2回目）
    pg_contract.addAgent.transact(agent, {'from': admin})

    agent_available = pg_contract.getAgent(agent)
    assert agent_available == True


# 正常系3: 登録２回（異なるアドレス）
def test_addAgent_normal_3(PaymentGateway, users):
    admin = users['admin']
    agent_1 = users['agent']
    agent_2 = users['trader']  # NOTE:traderのアドレスで代用

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 収納代行業者（Agent）の追加
    pg_contract.addAgent.transact(agent_1, {'from': admin})

    # 収納代行業者（Agent）の追加（2回目）
    pg_contract.addAgent.transact(agent_2, {'from': admin})

    agent_1_available = pg_contract.getAgent(agent_1)
    assert agent_1_available == True

    agent_2_available = pg_contract.getAgent(agent_2)
    assert agent_2_available == True


# 正常系4: 登録なしアドレスの参照
def test_addAgent_normal_4(PaymentGateway, users):
    admin = users['admin']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    agent_available = pg_contract.getAgent("0xCfC4BEa6d2f573EB7E804E7a01ba1f4D1b208939")  # NOTE:任意のEOA
    assert agent_available == False


# エラー系1: 入力値の型誤り（agent_address）
def test_addAgent_error_1(PaymentGateway, users):
    admin = users['admin']
    agent = '1234'

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 収納代行業者（Agent）の追加
    with pytest.raises(ValueError):
        pg_contract.addAgent.transact(agent, {'from': admin})


# エラー系2: 権限不足
def test_addAgent_error_2(PaymentGateway, users):
    admin = users['admin']
    attacker = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 権限不足で更新できない
    pg_contract.addAgent.transact(agent, {'from': attacker})

    agent_available = pg_contract.getAgent(agent)
    assert agent_available == False


'''
TEST_収納代行業者の削除（removeAgent）
'''


# 正常系1: データなし
def test_removeAgent_normal_1(PaymentGateway, users):
    admin = users['admin']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 収納代行業者（Agent）の削除
    pg_contract.removeAgent.transact(agent, {'from': admin})

    agent_available = pg_contract.getAgent(agent)
    assert agent_available == False


# 正常系2: データあり
def test_removeAgent_normal_2(PaymentGateway, users):
    admin = users['admin']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 収納代行業者（Agent）の追加
    pg_contract.addAgent.transact(agent, {'from': admin})

    # 収納代行業者（Agent）の削除
    pg_contract.removeAgent.transact(agent, {'from': admin})

    agent_available = pg_contract.getAgent(agent)
    assert agent_available == False


# エラー系1: 入力値の型誤り（agent_address）
def test_removeAgent_error_1(PaymentGateway, users):
    admin = users['admin']
    agent = '1234'

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 収納代行業者（Agent）の追加
    with pytest.raises(ValueError):
        pg_contract.removeAgent.transact(agent, {'from': admin})


# エラー系2: 権限不足
def test_removeAgent_error_2(PaymentGateway, users):
    admin = users['admin']
    attacker = users['trader']
    agent = users['agent']

    # PaymentGatewayデプロイ
    pg_contract = admin.deploy(PaymentGateway)

    # 収納代行業者追加：正常
    pg_contract.addAgent.transact(agent, {'from': admin})

    # 収納代行業者削除：権限不足
    pg_contract.removeAgent.transact(agent, {'from': attacker})

    agent_available = pg_contract.getAgent(agent)
    assert agent_available == True

