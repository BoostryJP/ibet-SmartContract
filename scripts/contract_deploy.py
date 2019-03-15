# -*- coding:utf-8 -*-
import os
from populus import Project

APP_ENV = os.environ.get('APP_ENV') or 'local'
if APP_ENV == 'local':
    chain_env = 'local_chain'
else:
    chain_env = 'dev_chain'

project = Project()
with project.get_chain(chain_env) as chain:
    web3 = chain.web3
    web3.eth.defaultAccount = web3.eth.accounts[0]
    web3.personal.unlockAccount(web3.eth.defaultAccount, os.environ.get('ETH_ACCOUNT_PASSWORD'), 1000)

    # TokenList
    token_list, _ = chain.provider.get_or_deploy_contract('TokenList')

    # PersonalInfo
    personal_info, _ = chain.provider.get_or_deploy_contract('PersonalInfo')

    # PaymentGateway
    payment_gateway, _ = chain.provider.get_or_deploy_contract('PaymentGateway')

    # IbetStraightBondExchange
    deploy_args = [payment_gateway.address, personal_info.address]
    bond_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBondExchange',
        deploy_args = deploy_args
    )

    # IbetCouponExchange
    deploy_args = [payment_gateway.address]
    coupon_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetCouponExchange',
        deploy_args = deploy_args
    )

    # IbetMembershipExchange
    deploy_args = [payment_gateway.address]
    membership_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetMembershipExchange',
        deploy_args = deploy_args
    )

    print('TokenList : ' + token_list.address)
    print('PersonalInfo : ' + personal_info.address)
    print('PaymentGateway : ' + payment_gateway.address)
    print('IbetStraightBondExchange : ' + bond_exchange.address)
    print('IbetCouponExchange : ' + coupon_exchange.address)
    print('IbetMembershipExchange : ' + membership_exchange.address)