import pytest
from brownie.exceptions import VirtualMachineError


@pytest.fixture(scope='session')
def accounts(accounts):
    # HACK: BrownieやGanacheが発生させるエラーを抑止する。
    for account in accounts:
        _simulate_asynchronous_tx(account)

    return accounts


def _simulate_asynchronous_tx(account_object):
    """
    トランザクションリバート時のエラーを抑止する。

    Brownieではリバート時に brownie.exceptions.VirtualMachineError を発生させる仕様となっている。
    一方、Brownieを使わずにQuorumに接続した場合など、非テスト環境ではエラーは発生しない。
    この関数を呼び出すことにより、Brownieでも非テスト環境と同様にエラーを発生させないようにする。

    :param account_object: Brownieのアカウントオブジェクト。このアカウントが送信するトランザクションはエラーを発生しなくなる。
    """
    account_object.transfer_or_raise = account_object.transfer

    def proxy(*args, **kwargs):
        try:
            return account_object.transfer_or_raise(*args, **kwargs)
        except (VirtualMachineError, ValueError, AttributeError) as e:
            # 実行環境によって挙動が異なるためエラー発生を抑止する。
            # VirtualMachineError: 通常のBrownieにおいてトランザクションリバート時に発生するエラー
            # ValueError: Live環境のGanacheでトランザクションリバート時に発生するエラー
            # AttributeError: Quorumでトランザクションリバート時に発生するエラー（おそらくBrownieのバグ）
            print(e)
            return e

    # transferメソッドを、例外を握りつぶすようにラップした関数で置き換える
    account_object.transfer = proxy


@pytest.fixture()
def users(web3, accounts):
    admin = accounts[0]
    trader = accounts[1]
    issuer = accounts[2]
    agent = accounts[3]
    web3.geth.personal.unlock_account(accounts[0].address, "password", 0)
    web3.geth.personal.unlock_account(accounts[1].address, "password", 0)
    web3.geth.personal.unlock_account(accounts[2].address, "password", 0)
    web3.geth.personal.unlock_account(accounts[3].address, "password", 0)
    users = {
        'admin': admin,
        'trader': trader,
        'issuer': issuer,
        'agent': agent
    }

    yield users


@pytest.fixture()
def personal_info(PersonalInfo, users):
    personal_info = users['admin'].deploy(PersonalInfo)
    return personal_info


@pytest.fixture()
def payment_gateway(PaymentGateway, users):
    payment_gateway = users['admin'].deploy(PaymentGateway)
    payment_gateway.addAgent.transact(users['agent'], {'from': users['admin']})
    return payment_gateway


# TODO: アンコメントしてbrownie移行
"""
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
"""


@pytest.fixture()
def membership_exchange_storage(ExchangeStorage, users):
    membership_exchange_storage = users['admin'].deploy(ExchangeStorage)
    return membership_exchange_storage


@pytest.fixture()
def membership_exchange(IbetMembershipExchange, users, payment_gateway, membership_exchange_storage):
    deploy_args = [payment_gateway.address, membership_exchange_storage.address]
    membership_exchange = users['admin'].deploy(IbetMembershipExchange, *deploy_args)
    membership_exchange_storage.upgradeVersion.transact(membership_exchange.address, {'from': users['admin']})
    return membership_exchange


"""
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
