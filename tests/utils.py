# 普通社債新規発行
def issue_bond_token(web3,chain,users,exchange_address):
    name = 'test_bond'
    symbol = 'BND'
    total_supply = 10000
    tradable_exchange = exchange_address
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
        name, symbol, total_supply, tradable_exchange, face_value,
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

# 会員権（譲渡可能）新規発行
def issue_transferable_membership(web3,chain,exchange_address):
    name = 'test_membership'
    symbol = 'MEM'
    initial_supply = 10000
    tradableExchange = exchange_address
    details = 'some_details'
    return_details = 'some_return'
    expiration_date = '20191231'
    memo = 'some_memo'
    transferable = True

    deploy_args = [
        name, symbol, initial_supply, tradableExchange,
        details, return_details,
        expiration_date, memo, transferable
    ]

    membership, _ = chain.provider.get_or_deploy_contract(
        'IbetMembership',
        deploy_args = deploy_args
    )
    return membership, deploy_args

# 会員権（譲渡不可）新規発行
def issue_non_transferable_membership(web3,chain,exchange_address):
    name = 'test_membership'
    symbol = 'MEM'
    initial_supply = 10000
    tradableExchange = exchange_address
    details = 'some_details'
    return_details = 'some_return'
    expiration_date = '20191231'
    memo = 'some_memo'
    transferable = False

    deploy_args = [
        name, symbol, initial_supply, tradableExchange,
        details, return_details,
        expiration_date, memo, transferable
    ]

    membership, _ = chain.provider.get_or_deploy_contract(
        'IbetMembership',
        deploy_args = deploy_args
    )
    return membership, deploy_args

# クーポン（譲渡可能）新規発行
def issue_transferable_coupon(web3,chain,exchange_address):
    name = 'test_coupon'
    symbol = 'CPN'
    total_supply = 1000000
    tradableExchange = exchange_address
    details = 'some_details'
    memo = 'some_memo'
    expirationDate = '20201231'
    transferable = True

    deploy_args = [
        name, symbol, total_supply, tradableExchange, details,
        memo, expirationDate, transferable
    ]

    coupon, _ = chain.provider.get_or_deploy_contract(
        'IbetCoupon',
        deploy_args = deploy_args
    )
    return coupon, deploy_args

# クーポン（譲渡不可）新規発行
def issue_non_transferable_coupon(web3,chain,exchange_address):
    name = 'test_coupon'
    symbol = 'CPN'
    total_supply = 1000000
    tradableExchange = exchange_address
    details = 'some_details'
    memo = 'some_memo'
    expirationDate = '20201231'
    transferable = False

    deploy_args = [
        name, symbol, total_supply, tradableExchange, details,
        memo, expirationDate, transferable
    ]

    coupon, _ = chain.provider.get_or_deploy_contract(
        'IbetCoupon',
        deploy_args = deploy_args
    )
    return coupon, deploy_args
