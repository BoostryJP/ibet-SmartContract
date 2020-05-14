import pytest


@pytest.fixture()
def users(accounts):
    admin = accounts[0]
    trader = accounts[1]
    issuer = accounts[2]
    agent = accounts[3]
    users = {
        'admin': admin,
        'trader': trader,
        'issuer': issuer,
        'agent': agent
    }
    return users


@pytest.fixture()
def personal_info(PersonalInfo, users):
    personal_info = users['admin'].deploy(PersonalInfo)
    return personal_info


# TODO: アンコメントしてbrownie移行
"""
@pytest.yield_fixture()
def payment_gateway(web3, chain, users):
    web3.eth.defaultAccount = users['admin']
    payment_gateway, _ = chain.provider.get_or_deploy_contract('PaymentGateway')
    payment_gateway.transact().addAgent(users['agent'])
    return payment_gateway


@pytest.yield_fixture()
def exchange_regulator_service(web3, chain, users):
    web3.eth.defaultAccount = users['admin']
    exchange_regulator_service, _ = chain.provider.get_or_deploy_contract('ExchangeRegulatorService')
    exchange_regulator_service.transact().register(users['issuer'], False)
    exchange_regulator_service.transact().register(users['trader'], False)
    exchange_regulator_service.transact().register(users['admin'], False)
    return exchange_regulator_service


@pytest.yield_fixture()
def bond_exchange_storage(web3, chain, users):
    web3.eth.defaultAccount = users['admin']
    bond_exchange_storage, _ = chain.provider.get_or_deploy_contract('ExchangeStorage')
    return bond_exchange_storage


@pytest.yield_fixture()
def bond_exchange(web3, chain, users,
                  personal_info, payment_gateway, bond_exchange_storage, exchange_regulator_service):
    web3.eth.defaultAccount = users['admin']
    deploy_args = [
        payment_gateway.address,
        personal_info.address,
        bond_exchange_storage.address,
        exchange_regulator_service.address
    ]
    bond_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBondExchange',
        deploy_args=deploy_args
    )
    bond_exchange_storage.transact().upgradeVersion(bond_exchange.address)
    return bond_exchange


@pytest.yield_fixture()
def membership_exchange_storage(web3, chain, users):
    web3.eth.defaultAccount = users['admin']
    membership_exchange_storage, _ = chain.provider.get_or_deploy_contract('ExchangeStorage')
    return membership_exchange_storage


@pytest.yield_fixture()
def membership_exchange(web3, chain, users, payment_gateway, membership_exchange_storage):
    web3.eth.defaultAccount = users['admin']
    deploy_args = [payment_gateway.address, membership_exchange_storage.address]
    membership_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetMembershipExchange',
        deploy_args=deploy_args
    )
    membership_exchange_storage.transact().upgradeVersion(membership_exchange.address)
    return membership_exchange


@pytest.yield_fixture()
def coupon_exchange_storage(web3, chain, users):
    web3.eth.defaultAccount = users['admin']
    coupon_exchange_storage, _ = chain.provider.get_or_deploy_contract('ExchangeStorage')
    return coupon_exchange_storage


@pytest.yield_fixture()
def coupon_exchange(web3, chain, users, payment_gateway, coupon_exchange_storage):
    web3.eth.defaultAccount = users['admin']
    deploy_args = [payment_gateway.address, coupon_exchange_storage.address]
    coupon_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetCouponExchange',
        deploy_args=deploy_args
    )
    coupon_exchange_storage.transact().upgradeVersion(coupon_exchange.address)
    return coupon_exchange


@pytest.yield_fixture()
def share_exchange_storage(web3, chain, users):
    web3.eth.defaultAccount = users['admin']
    share_exchange_storage, _ = chain.provider.get_or_deploy_contract('OTCExchangeStorage')
    return share_exchange_storage


@pytest.yield_fixture()
def share_exchange(web3, chain, users,
                  personal_info, payment_gateway, share_exchange_storage, exchange_regulator_service):
    web3.eth.defaultAccount = users['admin']
    deploy_args = [
        payment_gateway.address,
        personal_info.address,
        share_exchange_storage.address,
        exchange_regulator_service.address
    ]
    share_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetOTCExchange',
        deploy_args=deploy_args
    )
    share_exchange_storage.transact().upgradeVersion(share_exchange.address)
    return share_exchange

@pytest.yield_fixture()
def otc_exchange_storage(web3, chain, users):
    web3.eth.defaultAccount = users['admin']
    otc_exchange_storage, _ = chain.provider.get_or_deploy_contract('OTCExchangeStorage')
    return otc_exchange_storage


@pytest.yield_fixture()
def otc_exchange(web3, chain, users,
                  personal_info, payment_gateway, otc_exchange_storage, exchange_regulator_service):
    web3.eth.defaultAccount = users['admin']
    deploy_args = [
        payment_gateway.address,
        personal_info.address,
        otc_exchange_storage.address,
        exchange_regulator_service.address
    ]
    otc_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetOTCExchange',
        deploy_args=deploy_args
    )
    otc_exchange_storage.transact().upgradeVersion(otc_exchange.address)
    return otc_exchange
"""
