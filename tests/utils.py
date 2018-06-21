# 普通社債新規発行
def issue_bond_token(web3,chain,users):
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

    web3.eth.defaultAccount = users['issuer']
    bond_token, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBond',
        deploy_args = deploy_args
    )
    return bond_token, deploy_args

# クーポン（譲渡可能）新規発行
def issue_transferable_coupon(web3,chain):
    name = 'test_coupon'
    symbol = 'CPN'
    total_supply = 1000000
    details = 'some_details'
    memo = 'some_memo'
    expirationDate = '20201231'
    transferable = True

    deploy_args = [
        name, symbol, total_supply, details,
        memo, expirationDate, transferable
    ]

    coupon, _ = chain.provider.get_or_deploy_contract(
        'IbetCoupon',
        deploy_args = deploy_args
    )
    return coupon, deploy_args

# クーポン（譲渡不可）新規発行
def issue_non_transferable_coupon(web3,chain):
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

    coupon, _ = chain.provider.get_or_deploy_contract(
        'IbetCoupon',
        deploy_args = deploy_args
    )
    return coupon, deploy_args
