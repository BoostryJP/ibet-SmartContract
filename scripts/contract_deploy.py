# -*- coding:utf-8 -*-
import os
from populus import Project

APP_ENV = os.environ.get('APP_ENV') or 'local'
ETH_ACCOUNT_PASSWORD = os.environ.get('ETH_ACCOUNT_PASSWORD') or 'password'
if APP_ENV == 'local':
    chain_env = 'local_chain'
else:
    chain_env = 'dev_chain'

project = Project()
with project.get_chain(chain_env) as chain:
    web3 = chain.web3
    web3.eth.defaultAccount = web3.eth.accounts[0]
    web3.personal.unlockAccount(web3.eth.defaultAccount, ETH_ACCOUNT_PASSWORD, 1000)

    # TokenList
    token_list, _ = chain.provider.deploy_contract('TokenList')

    # PersonalInfo
    personal_info, _ = chain.provider.deploy_contract('PersonalInfo')

    # PaymentGateway
    payment_gateway, _ = chain.provider.deploy_contract('PaymentGateway')

    # ------------------------------------
    # IbetStraightBond
    # ------------------------------------
    # ExchangeRegulatorService
    exchange_regulator_service, _ = chain.provider.deploy_contract('ExchangeRegulatorService')

    # Storage
    bond_exchange_storage, _ = chain.provider.deploy_contract('ExchangeStorage')

    # IbetStraightBondExchange
    deploy_args = [
        payment_gateway.address,
        personal_info.address,
        bond_exchange_storage.address,
        exchange_regulator_service.address
    ]
    bond_exchange, _ = chain.provider.deploy_contract(
        'IbetStraightBondExchange',
        deploy_args=deploy_args
    )

    # Upgrade Version
    bond_exchange_storage.transact().upgradeVersion(bond_exchange.address)

    # ------------------------------------
    # IbetCoupon
    # ------------------------------------
    # Storage
    coupon_exchange_storage, _ = chain.provider.deploy_contract('ExchangeStorage')

    # IbetCouponExchange
    deploy_args = [
        payment_gateway.address,
        coupon_exchange_storage.address
    ]
    coupon_exchange, _ = chain.provider.deploy_contract(
        'IbetCouponExchange',
        deploy_args=deploy_args
    )

    # Upgrade Version
    coupon_exchange_storage.transact().upgradeVersion(coupon_exchange.address)

    # ------------------------------------
    # IbetMembership
    # ------------------------------------
    # Storage
    membership_exchange_storage, _ = chain.provider.deploy_contract('ExchangeStorage')

    # IbetMembershipExchange
    deploy_args = [
        payment_gateway.address,
        membership_exchange_storage.address
    ]
    membership_exchange, _ = chain.provider.deploy_contract(
        'IbetMembershipExchange',
        deploy_args=deploy_args
    )

    # Upgrade Version
    membership_exchange_storage.transact().upgradeVersion(membership_exchange.address)

    print('TokenList : ' + token_list.address)
    print('PersonalInfo : ' + personal_info.address)
    print('PaymentGateway : ' + payment_gateway.address)
    print('ExchangeStorage - Bond : ' + bond_exchange_storage.address)
    print('ExchangeRegulatorService - Bond : ' + exchange_regulator_service.address)
    print('IbetStraightBondExchange : ' + bond_exchange.address)
    print('ExchangeStorage - Coupon : ' + coupon_exchange_storage.address)
    print('IbetCouponExchange : ' + coupon_exchange.address)
    print('ExchangeStorage - Membership : ' + membership_exchange_storage.address)
    print('IbetMembershipExchange : ' + membership_exchange.address)
