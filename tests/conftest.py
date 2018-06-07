import pytest

@pytest.yield_fixture()
def chain(project):
    with project.get_chain('local_chain') as chain:
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
def white_list(web3, chain, users):
    web3.eth.defaultAccount = users['admin']
    white_list, _ = chain.provider.get_or_deploy_contract('WhiteList')
    return white_list

@pytest.yield_fixture()
def bond_exchange(web3, chain, users, personal_info, white_list):
    web3.eth.defaultAccount = users['admin']
    deploy_args = [white_list.address, personal_info.address]
    bond_exchange, _ = chain.provider.get_or_deploy_contract(
        'IbetStraightBondExchange',
        deploy_args = deploy_args
    )
    return bond_exchange
