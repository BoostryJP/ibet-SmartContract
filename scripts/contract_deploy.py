# -*- coding:utf-8 -*-
import os

from brownie import accounts, project, network

p = project.load('.', name="ibet_smart_contract")
p.load_config()
from brownie.project.ibet_smart_contract import TokenList, PersonalInfo, PaymentGateway, OTCExchangeStorage, \
    IbetOTCExchange, ExchangeRegulatorService, ExchangeStorage, IbetMembershipExchange, IbetCouponExchange, \
    IbetStraightBondExchange

APP_ENV = os.environ.get('APP_ENV') or 'local'
if APP_ENV == 'local':
    network_id = 'development'
else:
    network_id = 'ganache'
network.connect(network_id)


def main():
    deployer = accounts[0]

    # TokenList
    token_list = deployer.deploy(TokenList)

    # PersonalInfo
    personal_info = deployer.deploy(PersonalInfo)

    # PaymentGateway
    payment_gateway = deployer.deploy(PaymentGateway)

    # ------------------------------------
    # IbetOTC
    # ------------------------------------
    # Storage
    otc_exchange_storage = deployer.deploy(OTCExchangeStorage)

    # IbetOTCExchange
    deploy_args = [
        payment_gateway.address,
        personal_info.address,
        otc_exchange_storage.address,
        "0x0000000000000000000000000000000000000000"
    ]
    otc_exchange = deployer.deploy(IbetOTCExchange, *deploy_args)

    # Upgrade Version
    otc_exchange_storage.upgradeVersion.transact(otc_exchange.address, {'from': deployer})

    # ------------------------------------
    # IbetStraightBond
    # ------------------------------------
    # ExchangeRegulatorService
    exchange_regulator_service = deployer.deploy(ExchangeRegulatorService)

    # Storage
    bond_exchange_storage = deployer.deploy(ExchangeStorage)

    # IbetStraightBondExchange
    deploy_args = [
        payment_gateway.address,
        personal_info.address,
        bond_exchange_storage.address,
        exchange_regulator_service.address
    ]
    bond_exchange = deployer.deploy(IbetStraightBondExchange, *deploy_args)

    # Upgrade Version
    bond_exchange_storage.upgradeVersion.transact(bond_exchange.address, {'from': deployer})

    # ------------------------------------
    # IbetCoupon
    # ------------------------------------
    # Storage
    coupon_exchange_storage = deployer.deploy(ExchangeStorage)

    # IbetCouponExchange
    deploy_args = [
        payment_gateway.address,
        coupon_exchange_storage.address
    ]
    coupon_exchange = deployer.deploy(IbetCouponExchange, *deploy_args)

    # Upgrade Version
    coupon_exchange_storage.upgradeVersion.transact(coupon_exchange.address, {'from': deployer})

    # ------------------------------------
    # IbetMembership
    # ------------------------------------
    # Storage
    membership_exchange_storage = deployer.deploy(ExchangeStorage)

    # IbetMembershipExchange
    deploy_args = [
        payment_gateway.address,
        membership_exchange_storage.address
    ]
    membership_exchange = deployer.deploy(IbetMembershipExchange, *deploy_args)

    # Upgrade Version
    membership_exchange_storage.upgradeVersion(membership_exchange.address, {'from': deployer})

    print('TokenList : ' + token_list.address)
    print('PersonalInfo : ' + personal_info.address)
    print('PaymentGateway : ' + payment_gateway.address)
    print('OTCExchangeStorage: ' + otc_exchange_storage.address)
    print('IbetOTCExchange : ' + otc_exchange.address)
    print('ExchangeStorage - Bond : ' + bond_exchange_storage.address)
    print('ExchangeRegulatorService - Bond : ' + exchange_regulator_service.address)
    print('IbetStraightBondExchange : ' + bond_exchange.address)
    print('ExchangeStorage - Coupon : ' + coupon_exchange_storage.address)
    print('IbetCouponExchange : ' + coupon_exchange.address)
    print('ExchangeStorage - Membership : ' + membership_exchange_storage.address)
    print('IbetMembershipExchange : ' + membership_exchange.address)


if __name__ == '__main__':
    main()
