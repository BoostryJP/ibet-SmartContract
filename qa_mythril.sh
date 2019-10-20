#!/bin/bash
source ~/.bash_profile

cd /app/ibet-SmartContract

# 脆弱性チェック実施
myth -x IbetCoupon.sol SafeMath.sol Ownable.sol ContractReceiver.sol
myth -x IbetCouponExchange.sol SafeMath.sol Ownable.sol IbetCoupon.sol
myth -x IbetStraightBond.sol SafeMath.sol Ownable.sol ContractReceiver.sol
myth -x IbetStraightBondExchange.sol SafeMath.sol Ownable.sol IbetStraightBond.sol WhiteList.sol PersonalInfo.sol
myth -x TokenList.sol
myth -x PersonalInfo.sol
myth -x WhiteList.sol
