from brownie import IbetShare, IbetStraightBond, IbetMembership, IbetCoupon


# 普通社債新規発行
def issue_bond_token(issuer, exchange_address, personal_info_address):
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

    bond_token = issuer.deploy(IbetStraightBond, *deploy_args)
    return bond_token, deploy_args


# 株式新規発行
def issue_share_token(issuer, exchange_address, personal_info_address):
    name = 'test_share'
    symbol = 'IBS'
    issue_price = 10000
    total_supply = 10000
    dividends = 1000
    devidend_record_date = '20200830'
    devidend_payment_date = '20200831'
    cansellation_date = '20211231'
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'
    memo = 'some_memo'
    transferable = True

    deploy_args = [
        name, symbol, exchange_address, personal_info_address, issue_price, total_supply,
        dividends, devidend_record_date, devidend_payment_date, cansellation_date,
        contact_information, privacy_policy, memo, transferable
    ]

    share_token, _ = issuer.deploy(IbetShare, *deploy_args)
    return share_token, deploy_args


# 会員権（譲渡可能）新規発行
def issue_transferable_membership(issuer, exchange_address):
    name = 'test_membership'
    symbol = 'MEM'
    initial_supply = 10000
    tradableExchange = exchange_address
    details = 'some_details'
    return_details = 'some_return'
    expiration_date = '20191231'
    memo = 'some_memo'
    transferable = True
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'

    deploy_args = [
        name, symbol, initial_supply, tradableExchange,
        details, return_details,
        expiration_date, memo, transferable,
        contact_information, privacy_policy
    ]

    membership = issuer.deploy(IbetMembership, *deploy_args)
    return membership, deploy_args


# 会員権（譲渡不可）新規発行
def issue_non_transferable_membership(issuer, exchange_address):
    name = 'test_membership'
    symbol = 'MEM'
    initial_supply = 10000
    tradableExchange = exchange_address
    details = 'some_details'
    return_details = 'some_return'
    expiration_date = '20191231'
    memo = 'some_memo'
    transferable = False
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'

    deploy_args = [
        name, symbol, initial_supply, tradableExchange,
        details, return_details,
        expiration_date, memo, transferable,
        contact_information, privacy_policy
    ]

    membership = issuer.deploy(IbetMembership, *deploy_args)
    return membership, deploy_args


# クーポン（譲渡可能）新規発行
def issue_transferable_coupon(issuer, exchange_address):
    name = 'test_coupon'
    symbol = 'CPN'
    total_supply = 1000000
    tradableExchange = exchange_address
    details = 'some_details'
    return_details = 'some_return'
    memo = 'some_memo'
    expirationDate = '20201231'
    transferable = True
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'

    deploy_args = [
        name, symbol, total_supply, tradableExchange,
        details, return_details,
        memo, expirationDate, transferable,
        contact_information, privacy_policy
    ]

    coupon = issuer.deploy(IbetCoupon, *deploy_args)
    return coupon, deploy_args


# クーポン（譲渡不可）新規発行
def issue_non_transferable_coupon(issuer, exchange_address):
    name = 'test_coupon'
    symbol = 'CPN'
    total_supply = 1000000
    tradableExchange = exchange_address
    details = 'some_details'
    return_details = 'some_return'
    memo = 'some_memo'
    expirationDate = '20201231'
    transferable = False
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'

    deploy_args = [
        name, symbol, total_supply, tradableExchange,
        details, return_details,
        memo, expirationDate, transferable,
        contact_information, privacy_policy
    ]

    coupon = issuer.deploy(IbetCoupon, *deploy_args)
    return coupon, deploy_args


# 個人情報登録
def register_personal_info(from_account, personal_info, link_address):
    personal_info.register.transact(link_address, "encrypted_message", {'from': from_account})
