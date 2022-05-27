/**
* Copyright BOOSTRY Co., Ltd.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
*
* You may obtain a copy of the License at
* http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing,
* software distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*
* See the License for the specific language governing permissions and
* limitations under the License.
*
* SPDX-License-Identifier: Apache-2.0
*/

pragma solidity ^0.8.0;

library ErrorCode {


    // 10XX
    // TokenList_register
    string constant ERR_TokenList_register_1001 = "1001";
    string constant ERR_TokenList_register_1002 = "1002";
    // TokenList_changeOwner
    string constant ERR_TokenList_changeOwner_1011 = "1011";
    string constant ERR_TokenList_changeOwner_1012 = "1012";


    // 11XX / 12XX
    // IbetShare_lock
    string constant ERR_IbetShare_lock_1101 = "1101";
    string constant ERR_IbetShare_lock_1102 = "1102";
    // IbetShare_unlock
    string constant ERR_IbetShare_unlock_1111 = "1111";
    string constant ERR_IbetShare_unlock_1112 = "1112";
    // IbetShare_transferToAddress
    string constant ERR_IbetShare_transferToAddress_1121 = "1121";
    string constant ERR_IbetShare_transferToAddress_1122 = "1122";
    // IbetShare_transferToContract
    string constant ERR_IbetShare_transferToContract_1131 = "1131";
    // IbetShare_transfer
    string constant ERR_IbetShare_transfer_1141 = "1141";
    string constant ERR_IbetShare_transfer_1142 = "1142";
    // IbetShare_bulkTransfer
    string constant ERR_IbetShare_bulkTransfer_1151 = "1151";
    string constant ERR_IbetShare_bulkTransfer_1152 = "1152";
    string constant ERR_IbetShare_bulkTransfer_1153 = "1153";
    string constant ERR_IbetShare_bulkTransfer_1154 = "1154";
    // IbetShare_transferFrom
    string constant ERR_IbetShare_transferFrom_1161 = "1161";
    // IbetShare_applyForTransfer
    string constant ERR_IbetShare_applyForTransfer_1171 = "1171";
    string constant ERR_IbetShare_applyForTransfer_1172 = "1172";
    // IbetShare_cancelTransfer
    string constant ERR_IbetShare_cancelTransfer_1181 = "1181";
    string constant ERR_IbetShare_cancelTransfer_1182 = "1182";
    // IbetShare_approveTransfer
    string constant ERR_IbetShare_approveTransfer_1191 = "1191";
    string constant ERR_IbetShare_approveTransfer_1192 = "1192";
    // IbetShare_applyForOffering
    string constant ERR_IbetShare_applyForOffering_1201 = "1201";
    string constant ERR_IbetShare_applyForOffering_1202 = "1202";
    // IbetShare_redeemFrom
    string constant ERR_IbetShare_redeemFrom_1211 = "1211";
    string constant ERR_IbetShare_redeemFrom_1212 = "1212";


    // 13XX/14XX
    // IbetStraightBond_lock
    string constant ERR_IbetStraightBond_lock_1301 = "1301";
    string constant ERR_IbetStraightBond_lock_1302 = "1302";
    // IbetStraightBond_unlock
    string constant ERR_IbetStraightBond_unlock_1311 = "1311";
    string constant ERR_IbetStraightBond_unlock_1312 = "1312";
    // IbetStraightBond_transferToAddress
    string constant ERR_IbetStraightBond_transferToAddress_1321 = "1321";
    string constant ERR_IbetStraightBond_transferToAddress_1322 = "1322";
    // IbetStraightBond_transferToContract
    string constant ERR_IbetStraightBond_transferToContract_1331 = "1331";
    // IbetStraightBond_transfer
    string constant ERR_IbetStraightBond_transfer_1341 = "1341";
    string constant ERR_IbetStraightBond_transfer_1342 = "1342";
    // IbetStraightBond_bulkTransfer
    string constant ERR_IbetStraightBond_bulkTransfer_1351 = "1351";
    string constant ERR_IbetStraightBond_bulkTransfer_1352 = "1352";
    string constant ERR_IbetStraightBond_bulkTransfer_1353 = "1353";
    // IbetStraightBond_transferFrom
    string constant ERR_IbetStraightBond_transferFrom_1361 = "1361";
    // IbetStraightBond_applyForTransfer
    string constant ERR_IbetStraightBond_applyForTransfer_1371 = "1371";
    string constant ERR_IbetStraightBond_applyForTransfer_1372 = "1372";
    // IbetStraightBond_cancelTransfer
    string constant ERR_IbetStraightBond_cancelTransfer_1381 = "1381";
    string constant ERR_IbetStraightBond_cancelTransfer_1382 = "1382";
    // IbetStraightBond_approveTransfer
    string constant ERR_IbetStraightBond_approveTransfer_1391 = "1391";
    string constant ERR_IbetStraightBond_approveTransfer_1392 = "1392";
    // IbetStraightBond_applyForOffering
    string constant ERR_IbetStraightBond_applyForOffering_1401 = "1401";
    string constant ERR_IbetStraightBond_applyForOffering_1402 = "1402";
    // IbetStraightBond_redeemFrom
    string constant ERR_IbetStraightBond_redeemFrom_1411 = "1411";
    string constant ERR_IbetStraightBond_redeemFrom_1412 = "1412";


    // 15XX
    // IbetCoupon_transferToContract
    string constant ERR_IbetCoupon_transferToContract_1501 = "1501";
    // IbetCoupon_transfer
    string constant ERR_IbetCoupon_transfer_1511 = "1511";
    string constant ERR_IbetCoupon_transfer_1512 = "1512";
    // IbetCoupon_bulkTransfer
    string constant ERR_IbetCoupon_bulkTransfer_1521 = "1521";
    string constant ERR_IbetCoupon_bulkTransfer_1522 = "1522";
    string constant ERR_IbetCoupon_bulkTransfer_1523 = "1523";
    // IbetCoupon_transferFrom
    string constant ERR_IbetCoupon_transferFrom_1531 = "1531";
    // IbetCoupon_consume
    string constant ERR_IbetCoupon_consume_1541 = "1541";
    // IbetCoupon_applyForOffering
    string constant ERR_IbetCoupon_applyForOffering_1551 = "1551";


    // 16XX
    // IbetMembership_transferToContract
    string constant ERR_IbetMembership_transferToContract_1601 = "1601";
    // IbetMembership_transfer
    string constant ERR_IbetMembership_transfer_1611 = "1611";
    string constant ERR_IbetMembership_transfer_1612 = "1612";
    // IbetMembership_bulkTransfer
    string constant ERR_IbetMembership_bulkTransfer_1621 = "1621";
    string constant ERR_IbetMembership_bulkTransfer_1622 = "1622";
    string constant ERR_IbetMembership_bulkTransfer_1623 = "1623";
    // IbetMembership_transferFrom
    string constant ERR_IbetMembership_transferFrom_1631 = "1631";
    // IbetMembership_applyForOffering
    string constant ERR_IbetMembership_applyForOffering_1641 = "1641";


    // 17XX
    // IbetStandardToken_transferToContract
    string constant ERR_IbetStandardToken_transferToContract_1701 = "1701";
    // IbetStandardToken_transfer
    string constant ERR_IbetStandardToken_transfer_1711 = "1711";
    // IbetStandardToken_bulkTransfer
    string constant ERR_IbetStandardToken_bulkTransfer_1721 = "1721";
    string constant ERR_IbetStandardToken_bulkTransfer_1722 = "1722";
    // IbetStandardToken_transferFrom
    string constant ERR_IbetStandardToken_transferFrom_1731 = "1731";


    // 20XX
    // ExchangeStorage_onlyLatestVersion
    string constant ERR_ExchangeStorage_onlyLatestVersion_2001 = "2001";


    // 21XX
    // IbetExchange_createOrder
    string constant ERR_IbetExchange_createOrder_2101 = "2101";
    // IbetExchange_cancelOrder
    string constant ERR_IbetExchange_cancelOrder_2111 = "2111";
    string constant ERR_IbetExchange_cancelOrder_2112 = "2112";
    string constant ERR_IbetExchange_cancelOrder_2113 = "2113";
    string constant ERR_IbetExchange_cancelOrder_2114 = "2114";
    // IbetExchange_forceCancelOrder
    string constant ERR_IbetExchange_forceCancelOrder_2121 = "2121";
    string constant ERR_IbetExchange_forceCancelOrder_2122 = "2122";
    string constant ERR_IbetExchange_forceCancelOrder_2123 = "2123";
    string constant ERR_IbetExchange_forceCancelOrder_2124 = "2124";
    // IbetExchange_executeOrder
    string constant ERR_IbetExchange_executeOrder_2131 = "2131";
    string constant ERR_IbetExchange_executeOrder_2132 = "2132";
    // IbetExchange_confirmAgreement
    string constant ERR_IbetExchange_confirmAgreement_2141 = "2141";
    string constant ERR_IbetExchange_confirmAgreement_2142 = "2142";
    string constant ERR_IbetExchange_confirmAgreement_2143 = "2143";
    // IbetExchange_cancelAgreement
    string constant ERR_IbetExchange_cancelAgreement_2151 = "2151";
    string constant ERR_IbetExchange_cancelAgreement_2152 = "2152";
    string constant ERR_IbetExchange_cancelAgreement_2153 = "2153";
    string constant ERR_IbetExchange_cancelAgreement_2154 = "2154";
    // IbetExchange_withdraw
    string constant ERR_IbetExchange_withdraw_2161 = "2161";


    // 22XX
    // EscrowStorage_onlyLatestVersion
    string constant ERR_EscrowStorage_onlyLatestVersion_2201 = "2201";


    // 23XX
    // IbetEscrow_createEscrow
    string constant ERR_IbetEscrow_createEscrow_2301 = "2301";
    string constant ERR_IbetEscrow_createEscrow_2302 = "2302";
    string constant ERR_IbetEscrow_createEscrow_2303 = "2303";
    // IbetEscrow_cancelEscrow
    string constant ERR_IbetEscrow_cancelEscrow_2311 = "2311";
    string constant ERR_IbetEscrow_cancelEscrow_2312 = "2312";
    string constant ERR_IbetEscrow_cancelEscrow_2313 = "2313";
    string constant ERR_IbetEscrow_cancelEscrow_2314 = "2314";
    // IbetEscrow_finishEscrow
    string constant ERR_IbetEscrow_finishEscrow_2321 = "2321";
    string constant ERR_IbetEscrow_finishEscrow_2322 = "2322";
    string constant ERR_IbetEscrow_finishEscrow_2323 = "2323";
    string constant ERR_IbetEscrow_finishEscrow_2324 = "2324";
    // IbetEscrow_withdraw
    string constant ERR_IbetEscrow_withdraw_2331 = "2331";



    // 24XX
    // IbetSecurityTokenEscrow_createEscrow
    string constant ERR_IbetSecurityTokenEscrow_createEscrow_2401 = "2401";
    string constant ERR_IbetSecurityTokenEscrow_createEscrow_2402 = "2402";
    string constant ERR_IbetSecurityTokenEscrow_createEscrow_2403 = "2403";
    // IbetSecurityTokenEscrow_cancelEscrow
    string constant ERR_IbetSecurityTokenEscrow_cancelEscrow_2411 = "2411";
    string constant ERR_IbetSecurityTokenEscrow_cancelEscrow_2412 = "2412";
    string constant ERR_IbetSecurityTokenEscrow_cancelEscrow_2413 = "2413";
    string constant ERR_IbetSecurityTokenEscrow_cancelEscrow_2414 = "2414";
    // IbetSecurityTokenEscrow_approveTransfer
    string constant ERR_IbetSecurityTokenEscrow_approveTransfer_2421 = "2421";
    string constant ERR_IbetSecurityTokenEscrow_approveTransfer_2422 = "2422";
    string constant ERR_IbetSecurityTokenEscrow_approveTransfer_2423 = "2423";
    string constant ERR_IbetSecurityTokenEscrow_approveTransfer_2424 = "2424";
    string constant ERR_IbetSecurityTokenEscrow_approveTransfer_2425 = "2425";
    // IbetSecurityTokenEscrow_finishEscrow
    string constant ERR_IbetSecurityTokenEscrow_finishEscrow_2431 = "2431";
    string constant ERR_IbetSecurityTokenEscrow_finishEscrow_2432 = "2432";
    string constant ERR_IbetSecurityTokenEscrow_finishEscrow_2433 = "2433";
    string constant ERR_IbetSecurityTokenEscrow_finishEscrow_2434 = "2434";
    // IbetSecurityTokenEscrow_withdraw
    string constant ERR_IbetSecurityTokenEscrow_withdraw_2441 = "2441";


    // 30XX
    // PaymentGateway_register
    string constant ERR_PaymentGateway_register_3001 = "3001";
    // PaymentGateway_approve
    string constant ERR_PaymentGateway_approve_3011 = "3011";
    // PaymentGateway_warn
    string constant ERR_PaymentGateway_warn_3021 = "3021";
    // PaymentGateway_disapprove
    string constant ERR_PaymentGateway_disapprove_3031 = "3031";
    // PaymentGateway_ban
    string constant ERR_PaymentGateway_ban_3041 = "3041";
    // PaymentGateway_modify
    string constant ERR_PaymentGateway_modify_3051 = "3051";


    // 40XX
    // PersonalInfo_modify
    string constant ERR_PersonalInfo_modify_4001 = "4001";
    string constant ERR_PersonalInfo_modify_4002 = "4002";


    // 50XX
    // Ownable_onlyOwner
    string constant ERR_Ownable_onlyOwner_5001 = "5001";
    // Ownable_transferOwnership
    string constant ERR_Ownable_transferOwnership_5011 = "5011";


    // 60XX
    // ContractRegistry_register
    string constant ERR_ContractRegistry_register_6001 = "6001";
    string constant ERR_ContractRegistry_register_6002 = "6002";


    // 61XX
    // E2EMessaging_getLastMessage
    string constant ERR_E2EMessaging_getLastMessage_6101 = "6101";
    // E2EMessaging_clearMessage
    string constant ERR_E2EMessaging_clearMessage_6111 = "6111";


    // 62XX
    // FreezeLog_updateLog
    string constant ERR_FreezeLog_updateLog_6201 = "6201";
}
