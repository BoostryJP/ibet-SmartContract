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
    return bond_token
