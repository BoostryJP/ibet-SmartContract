import pytest
import os


@pytest.yield_fixture()
def chain(project):
    app_env = os.environ.get('APP_ENV') or 'local'
    if app_env == 'local':
        with project.get_chain('local_chain') as chain:
            yield chain
    else:
        with project.get_chain('dev_chain') as chain:
            yield chain


@pytest.yield_fixture()
def users(web3, accounts):
    admin = accounts[0]
    trader = accounts[1]
    issuer = accounts[2]
    agent = accounts[3]
    web3.personal.unlockAccount(accounts[0], "password", 0)
    web3.personal.unlockAccount(accounts[1], "password", 0)
    web3.personal.unlockAccount(accounts[2], "password", 0)
    web3.personal.unlockAccount(accounts[3], "password", 0)
    users = {
        'admin': admin,
        'trader': trader,
        'issuer': issuer,
        'agent': agent
    }
    return users


@pytest.yield_fixture()
def personal_info(web3, chain, users):
    web3.eth.defaultAccount = users['admin']
    personal_info, _ = chain.provider.get_or_deploy_contract('PersonalInfo')
    return personal_info


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
                  personal_info, payment_gateway, otc_exchange_storage):
    web3.eth.defaultAccount = users['admin']
    deploy_args = [
        payment_gateway.address,
        personal_info.address,
        otc_exchange_storage.address,
    ]
    otc_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetOTCExchange',
        deploy_args=deploy_args
    )
    otc_exchange_storage.transact().upgradeVersion(otc_exchange.address)
    # storage参照可能コントラクトの設定
    otc_exchange_storage.transact().register(otc_exchange.address, True)
    return otc_exchange
