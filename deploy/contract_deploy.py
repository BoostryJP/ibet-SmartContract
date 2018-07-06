# -*- coding:utf-8 -*-
from populus import Project


project = Project()
chain = project.get_chain('dev_chain')
web3 = chain.web3
web3.eth.defaultAccount = web3.eth.accounts[0]
web3.personal.unlockAccount(web3.eth.defaultAccount, "password", 0)

token_list, _ = chain.provider.get_or_deploy_contract('TokenList')
personal_info, _ = chain.provider.get_or_deploy_contract('PersonalInfo')
white_list, _ = chain.provider.get_or_deploy_contract('WhiteList')
deploy_args = [white_list.address, personal_info.address]
bond_exchange, _ = chain.provider.get_or_deploy_contract(
    'IbetStraightBondExchange',
    deploy_args = deploy_args
)
coupon_exchange, _ = chain.provider.get_or_deploy_contract('IbetCouponExchange')

print('TokenList : ' + token_list.address)
print('PersonalInfo : ' + personal_info.address)
print('WhiteList : ' + white_list.address)
print('IbetStraightBondExchange : ' + bond_exchange.address)
print('IbetCouponExchange : ' + coupon_exchange.address)
