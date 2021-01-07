"""
Copyright BOOSTRY Co., Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
"""

from brownie import IbetShare, IbetStraightBond, IbetMembership, IbetCoupon

import brownie_utils


# 普通社債新規発行
def issue_bond_token(users, exchange_address, personal_info_address):
    name = 'test_bond'
    symbol = 'BND'
    total_supply = 10000
    face_value = 10000
    redemption_date = '20191231'
    redemption_value = 100
    return_date = '20191231'
    return_amount = 'some_return'
    purpose = 'some_purpose'

    deploy_args = [
        name, symbol, total_supply, face_value,
        redemption_date, redemption_value,
        return_date, return_amount,
        purpose
    ]

    # デプロイ
    bond_token = brownie_utils.force_deploy(users['issuer'], IbetStraightBond, *deploy_args)

    # 取引可能DEXの更新
    bond_token.setTradableExchange.transact(exchange_address, {'from': users["issuer"]})

    # 個人情報コントラクトの更新
    bond_token.setPersonalInfoAddress.transact(personal_info_address, {'from': users["issuer"]})

    return bond_token, deploy_args


# 株式新規発行
def issue_share_token(users, exchange_address, personal_info_address):
    name = 'test_share'
    symbol = 'IBS'
    issue_price = 10000
    total_supply = 10000
    dividends = 1000
    devidend_record_date = '20200830'
    devidend_payment_date = '20200831'
    cansellation_date = '20211231'
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'
    memo = 'some_memo'
    transferable = True

    deploy_args = [
        name, symbol, issue_price, total_supply,
        dividends, devidend_record_date, devidend_payment_date, cansellation_date
    ]

    issuer = users['issuer']

    # デプロイ
    share_token = issuer.deploy(IbetShare, *deploy_args)

    # 各種情報の更新
    share_token.setTradableExchange.transact(exchange_address, {'from': issuer})
    share_token.setPersonalInfoAddress.transact(personal_info_address, {'from': issuer})
    share_token.setContactInformation.transact(contact_information, {'from': issuer})
    share_token.setPrivacyPolicy.transact(privacy_policy, {'from': issuer})
    share_token.setMemo.transact(memo, {'from': issuer})
    share_token.setTransferable.transact(transferable, {'from': issuer})
    return share_token, deploy_args


# 会員権（譲渡可能）新規発行
def issue_transferable_membership(issuer, exchange_address):
    name = 'test_membership'
    symbol = 'MEM'
    initial_supply = 10000
    tradableExchange = exchange_address
    details = 'some_details'
    return_details = 'some_return'
    expiration_date = '20191231'
    memo = 'some_memo'
    transferable = True
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'

    deploy_args = [
        name, symbol, initial_supply, tradableExchange,
        details, return_details,
        expiration_date, memo, transferable,
        contact_information, privacy_policy
    ]

    membership = issuer.deploy(IbetMembership, *deploy_args)
    return membership, deploy_args


# 会員権（譲渡不可）新規発行
def issue_non_transferable_membership(issuer, exchange_address):
    name = 'test_membership'
    symbol = 'MEM'
    initial_supply = 10000
    tradableExchange = exchange_address
    details = 'some_details'
    return_details = 'some_return'
    expiration_date = '20191231'
    memo = 'some_memo'
    transferable = False
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'

    deploy_args = [
        name, symbol, initial_supply, tradableExchange,
        details, return_details,
        expiration_date, memo, transferable,
        contact_information, privacy_policy
    ]

    membership = issuer.deploy(IbetMembership, *deploy_args)
    return membership, deploy_args


# クーポン（譲渡可能）新規発行
def issue_transferable_coupon(issuer, exchange_address):
    name = 'test_coupon'
    symbol = 'CPN'
    total_supply = 1000000
    tradableExchange = exchange_address
    details = 'some_details'
    return_details = 'some_return'
    memo = 'some_memo'
    expirationDate = '20201231'
    transferable = True
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'

    deploy_args = [
        name, symbol, total_supply, tradableExchange,
        details, return_details,
        memo, expirationDate, transferable,
        contact_information, privacy_policy
    ]

    coupon = issuer.deploy(IbetCoupon, *deploy_args)
    return coupon, deploy_args


# クーポン（譲渡不可）新規発行
def issue_non_transferable_coupon(issuer, exchange_address):
    name = 'test_coupon'
    symbol = 'CPN'
    total_supply = 1000000
    tradableExchange = exchange_address
    details = 'some_details'
    return_details = 'some_return'
    memo = 'some_memo'
    expirationDate = '20201231'
    transferable = False
    contact_information = 'some_contact_information'
    privacy_policy = 'some_privacy_policy'

    deploy_args = [
        name, symbol, total_supply, tradableExchange,
        details, return_details,
        memo, expirationDate, transferable,
        contact_information, privacy_policy
    ]

    coupon = issuer.deploy(IbetCoupon, *deploy_args)
    return coupon, deploy_args


# 個人情報登録
def register_personal_info(from_account, personal_info, link_address):
    personal_info.register.transact(link_address, "encrypted_message", {'from': from_account})
