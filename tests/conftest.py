import pytest
import os

@pytest.yield_fixture()
def chain(project):
    APP_ENV = os.environ.get('APP_ENV') or 'local'
    if APP_ENV == 'local':
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
    web3.personal.unlockAccount(accounts[0],"password",0)
    web3.personal.unlockAccount(accounts[1],"password",0)
    web3.personal.unlockAccount(accounts[2],"password",0)
    web3.personal.unlockAccount(accounts[3],"password",0)
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
    txn_hash = payment_gateway.transact().addAgent(0, users['agent'])
    chain.wait.for_receipt(txn_hash)
    return payment_gateway

@pytest.yield_fixture()
def bond_exchange(web3, chain, users, personal_info, payment_gateway):
    web3.eth.defaultAccount = users['admin']
    deploy_args = [payment_gateway.address, personal_info.address]
    bond_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBondExchange',
        deploy_args = deploy_args
    )
    return bond_exchange

@pytest.yield_fixture()
def membership_exchange(web3, chain, users, payment_gateway):
    web3.eth.defaultAccount = users['admin']
    deploy_args = [payment_gateway.address]
    membership_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetMembershipExchange',
        deploy_args = deploy_args
    )
    return membership_exchange

@pytest.yield_fixture()
def coupon_exchange(web3, chain, users, payment_gateway):
    web3.eth.defaultAccount = users['admin']
    deploy_args = [payment_gateway.address]
    coupon_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetCouponExchange',
        deploy_args = deploy_args
    )
    return coupon_exchange
