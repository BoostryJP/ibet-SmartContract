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
    // 10XXXX
    // TokenList_register
    string constant ERR_TokenList_register_100001 = "100001";
    string constant ERR_TokenList_register_100002 = "100002";
    // TokenList_changeOwner
    string constant ERR_TokenList_changeOwner_100101 = "100101";
    string constant ERR_TokenList_changeOwner_100102 = "100102";

    // 11XXXX
    // IbetShare_lock
    string constant ERR_IbetShare_lock_110001 = "110001";
    string constant ERR_IbetShare_lock_110002 = "110002";
    // IbetShare_unlock
    string constant ERR_IbetShare_unlock_110101 = "110101";
    string constant ERR_IbetShare_unlock_110102 = "110102";
    // IbetShare_transferToAddress
    string constant ERR_IbetShare_transferToAddress_110201 = "110201";
    string constant ERR_IbetShare_transferToAddress_110202 = "110202";
    // IbetShare_transferToContract
    string constant ERR_IbetShare_transferToContract_110301 = "110301";
    // IbetShare_transfer
    string constant ERR_IbetShare_transfer_110401 = "110401";
    string constant ERR_IbetShare_transfer_110402 = "110402";
    // IbetShare_bulkTransfer
    string constant ERR_IbetShare_bulkTransfer_110501 = "110501";
    string constant ERR_IbetShare_bulkTransfer_110502 = "110502";
    string constant ERR_IbetShare_bulkTransfer_110503 = "110503";
    string constant ERR_IbetShare_bulkTransfer_110504 = "110504";
    // IbetShare_transferFrom
    string constant ERR_IbetShare_transferFrom_110601 = "110601";
    // IbetShare_applyForTransfer
    string constant ERR_IbetShare_applyForTransfer_110701 = "110701";
    string constant ERR_IbetShare_applyForTransfer_110702 = "110702";
    // IbetShare_cancelTransfer
    string constant ERR_IbetShare_cancelTransfer_110801 = "110801";
    string constant ERR_IbetShare_cancelTransfer_110802 = "110802";
    // IbetShare_approveTransfer
    string constant ERR_IbetShare_approveTransfer_110901 = "110901";
    string constant ERR_IbetShare_approveTransfer_110902 = "110902";
    // IbetShare_applyForOffering
    string constant ERR_IbetShare_applyForOffering_111001 = "111001";
    string constant ERR_IbetShare_applyForOffering_111002 = "111002";
    // IbetShare_redeemFrom
    string constant ERR_IbetShare_redeemFrom_111101 = "111101";
    string constant ERR_IbetShare_redeemFrom_111102 = "111102";
    // IbetShare_forceUnlock
    string constant ERR_IbetShare_forceUnlock_111201 = "111201";
    // IbetShare_bulkIssueFrom
    string constant ERR_IbetShare_bulkIssueFrom_111301 = "111301";
    // IbetShare_bulkRedeemFrom
    string constant ERR_IbetShare_bulkRedeemFrom_111401 = "111401";
    // IbetShare_bulkTransferFrom
    string constant ERR_IbetShare_bulkTransferFrom_111501 = "111501";

    // 12XXXX
    // IbetStraightBond_lock
    string constant ERR_IbetStraightBond_lock_120001 = "120001";
    string constant ERR_IbetStraightBond_lock_120002 = "120002";
    // IbetStraightBond_unlock
    string constant ERR_IbetStraightBond_unlock_120101 = "120101";
    string constant ERR_IbetStraightBond_unlock_120102 = "120102";
    // IbetStraightBond_transferToAddress
    string constant ERR_IbetStraightBond_transferToAddress_120201 = "120201";
    string constant ERR_IbetStraightBond_transferToAddress_120202 = "120202";
    // IbetStraightBond_transferToContract
    string constant ERR_IbetStraightBond_transferToContract_120301 = "120301";
    // IbetStraightBond_transfer
    string constant ERR_IbetStraightBond_transfer_120401 = "120401";
    string constant ERR_IbetStraightBond_transfer_120402 = "120402";
    // IbetStraightBond_bulkTransfer
    string constant ERR_IbetStraightBond_bulkTransfer_120501 = "120501";
    string constant ERR_IbetStraightBond_bulkTransfer_120502 = "120502";
    string constant ERR_IbetStraightBond_bulkTransfer_120503 = "120503";
    // IbetStraightBond_transferFrom
    string constant ERR_IbetStraightBond_transferFrom_120601 = "120601";
    // IbetStraightBond_applyForTransfer
    string constant ERR_IbetStraightBond_applyForTransfer_120701 = "120701";
    string constant ERR_IbetStraightBond_applyForTransfer_120702 = "120702";
    // IbetStraightBond_cancelTransfer
    string constant ERR_IbetStraightBond_cancelTransfer_120801 = "120801";
    string constant ERR_IbetStraightBond_cancelTransfer_120802 = "120802";
    // IbetStraightBond_approveTransfer
    string constant ERR_IbetStraightBond_approveTransfer_120901 = "120901";
    string constant ERR_IbetStraightBond_approveTransfer_120902 = "120902";
    // IbetStraightBond_applyForOffering
    string constant ERR_IbetStraightBond_applyForOffering_121001 = "121001";
    string constant ERR_IbetStraightBond_applyForOffering_121002 = "121002";
    // IbetStraightBond_redeemFrom
    string constant ERR_IbetStraightBond_redeemFrom_121101 = "121101";
    string constant ERR_IbetStraightBond_redeemFrom_121102 = "121102";
    // IbetStraightBond_forceUnlock
    string constant ERR_IbetStraightBond_forceUnlock_121201 = "121201";
    // IbetStraightBond_bulkIssueFrom
    string constant ERR_IbetStraightBond_bulkIssueFrom_121301 = "121301";
    // IbetStraightBond_bulkRedeemFrom
    string constant ERR_IbetStraightBond_bulkRedeemFrom_121401 = "121401";
    // IbetStraightBond_bulkTransferFrom
    string constant ERR_IbetStraightBond_bulkTransferFrom_121501 = "121501";

    // 13XXXX
    // IbetCoupon_transferToContract
    string constant ERR_IbetCoupon_transferToContract_130001 = "130001";
    // IbetCoupon_transfer
    string constant ERR_IbetCoupon_transfer_130101 = "130101";
    string constant ERR_IbetCoupon_transfer_130102 = "130102";
    // IbetCoupon_bulkTransfer
    string constant ERR_IbetCoupon_bulkTransfer_130201 = "130201";
    string constant ERR_IbetCoupon_bulkTransfer_130202 = "130202";
    string constant ERR_IbetCoupon_bulkTransfer_130203 = "130203";
    // IbetCoupon_transferFrom
    string constant ERR_IbetCoupon_transferFrom_130301 = "130301";
    // IbetCoupon_consume
    string constant ERR_IbetCoupon_consume_130401 = "130401";
    // IbetCoupon_applyForOffering
    string constant ERR_IbetCoupon_applyForOffering_130501 = "130501";
    // IbetCoupon_bulkTransferFrom
    string constant ERR_IbetCoupon_bulkTransferFrom_130601 = "130601";

    // 14XXXX
    // IbetMembership_transferToContract
    string constant ERR_IbetMembership_transferToContract_140001 = "140001";
    // IbetMembership_transfer
    string constant ERR_IbetMembership_transfer_140101 = "140101";
    string constant ERR_IbetMembership_transfer_140102 = "140102";
    // IbetMembership_bulkTransfer
    string constant ERR_IbetMembership_bulkTransfer_140201 = "140201";
    string constant ERR_IbetMembership_bulkTransfer_140202 = "140202";
    string constant ERR_IbetMembership_bulkTransfer_140203 = "140203";
    // IbetMembership_transferFrom
    string constant ERR_IbetMembership_transferFrom_140301 = "140301";
    // IbetMembership_applyForOffering
    string constant ERR_IbetMembership_applyForOffering_140401 = "140401";
    // IbetMembership_bulkTransferFrom
    string constant ERR_IbetMembership_bulkTransferFrom_140501 = "140501";

    // 15XXXX
    // IbetStandardToken_transferToContract
    string constant ERR_IbetStandardToken_transferToContract_150001 = "150001";
    // IbetStandardToken_transfer
    string constant ERR_IbetStandardToken_transfer_150101 = "150101";
    // IbetStandardToken_bulkTransfer
    string constant ERR_IbetStandardToken_bulkTransfer_150201 = "150201";
    string constant ERR_IbetStandardToken_bulkTransfer_150202 = "150202";
    // IbetStandardToken_transferFrom
    string constant ERR_IbetStandardToken_transferFrom_150301 = "150301";
    // IbetStandardToken_bulkTransferFrom
    string constant ERR_IbetStandardToken_bulkTransferFrom_150401 = "150401";

    // 20XXXX
    // ExchangeStorage_onlyLatestVersion
    string constant ERR_ExchangeStorage_onlyLatestVersion_200001 = "200001";

    // 21XXXX
    // IbetExchange_createOrder
    string constant ERR_IbetExchange_createOrder_210001 = "210001";
    // IbetExchange_cancelOrder
    string constant ERR_IbetExchange_cancelOrder_210101 = "210101";
    string constant ERR_IbetExchange_cancelOrder_210102 = "210102";
    string constant ERR_IbetExchange_cancelOrder_210103 = "210103";
    string constant ERR_IbetExchange_cancelOrder_210104 = "210104";
    // IbetExchange_forceCancelOrder
    string constant ERR_IbetExchange_forceCancelOrder_210201 = "210201";
    string constant ERR_IbetExchange_forceCancelOrder_210202 = "210202";
    string constant ERR_IbetExchange_forceCancelOrder_210203 = "210203";
    string constant ERR_IbetExchange_forceCancelOrder_210204 = "210204";
    // IbetExchange_executeOrder
    string constant ERR_IbetExchange_executeOrder_210301 = "210301";
    string constant ERR_IbetExchange_executeOrder_210302 = "210302";
    // IbetExchange_confirmAgreement
    string constant ERR_IbetExchange_confirmAgreement_210401 = "210401";
    string constant ERR_IbetExchange_confirmAgreement_210402 = "210402";
    string constant ERR_IbetExchange_confirmAgreement_210403 = "210403";
    // IbetExchange_cancelAgreement
    string constant ERR_IbetExchange_cancelAgreement_210501 = "210501";
    string constant ERR_IbetExchange_cancelAgreement_210502 = "210502";
    string constant ERR_IbetExchange_cancelAgreement_210503 = "210503";
    string constant ERR_IbetExchange_cancelAgreement_210504 = "210504";
    // IbetExchange_withdraw
    string constant ERR_IbetExchange_withdraw_210601 = "210601";

    // 22XXXX
    // EscrowStorage_onlyLatestVersion
    string constant ERR_EscrowStorage_onlyLatestVersion_220001 = "220001";

    // 23XXXX
    // IbetEscrow_createEscrow
    string constant ERR_IbetEscrow_createEscrow_230001 = "230001";
    string constant ERR_IbetEscrow_createEscrow_230002 = "230002";
    string constant ERR_IbetEscrow_createEscrow_230003 = "230003";
    // IbetEscrow_cancelEscrow
    string constant ERR_IbetEscrow_cancelEscrow_230101 = "230101";
    string constant ERR_IbetEscrow_cancelEscrow_230102 = "230102";
    string constant ERR_IbetEscrow_cancelEscrow_230103 = "230103";
    string constant ERR_IbetEscrow_cancelEscrow_230104 = "230104";
    // IbetEscrow_finishEscrow
    string constant ERR_IbetEscrow_finishEscrow_230201 = "230201";
    string constant ERR_IbetEscrow_finishEscrow_230202 = "230202";
    string constant ERR_IbetEscrow_finishEscrow_230203 = "230203";
    string constant ERR_IbetEscrow_finishEscrow_230204 = "230204";
    // IbetEscrow_withdraw
    string constant ERR_IbetEscrow_withdraw_230301 = "230301";

    // 24XXXX
    // IbetSecurityTokenEscrow_createEscrow
    string constant ERR_IbetSecurityTokenEscrow_createEscrow_240001 = "240001";
    string constant ERR_IbetSecurityTokenEscrow_createEscrow_240002 = "240002";
    string constant ERR_IbetSecurityTokenEscrow_createEscrow_240003 = "240003";
    // IbetSecurityTokenEscrow_cancelEscrow
    string constant ERR_IbetSecurityTokenEscrow_cancelEscrow_240101 = "240101";
    string constant ERR_IbetSecurityTokenEscrow_cancelEscrow_240102 = "240102";
    string constant ERR_IbetSecurityTokenEscrow_cancelEscrow_240103 = "240103";
    string constant ERR_IbetSecurityTokenEscrow_cancelEscrow_240104 = "240104";
    // IbetSecurityTokenEscrow_approveTransfer
    string constant ERR_IbetSecurityTokenEscrow_approveTransfer_240201 =
        "240201";
    string constant ERR_IbetSecurityTokenEscrow_approveTransfer_240202 =
        "240202";
    string constant ERR_IbetSecurityTokenEscrow_approveTransfer_240203 =
        "240203";
    string constant ERR_IbetSecurityTokenEscrow_approveTransfer_240204 =
        "240204";
    string constant ERR_IbetSecurityTokenEscrow_approveTransfer_240205 =
        "240205";
    // IbetSecurityTokenEscrow_finishEscrow
    string constant ERR_IbetSecurityTokenEscrow_finishEscrow_240301 = "240301";
    string constant ERR_IbetSecurityTokenEscrow_finishEscrow_240302 = "240302";
    string constant ERR_IbetSecurityTokenEscrow_finishEscrow_240303 = "240303";
    string constant ERR_IbetSecurityTokenEscrow_finishEscrow_240304 = "240304";
    // IbetSecurityTokenEscrow_withdraw
    string constant ERR_IbetSecurityTokenEscrow_withdraw_240401 = "240401";

    // 25XXXX
    // DVPStorage_onlyLatestVersion
    string constant ERR_DVPStorage_onlyLatestVersion_250001 = "250001";

    // 26XXXX
    // IbetSecurityTokenDVP_createDelivery
    string constant ERR_IbetSecurityTokenDVP_createDelivery_260001 = "260001";
    string constant ERR_IbetSecurityTokenDVP_createDelivery_260002 = "260002";
    string constant ERR_IbetSecurityTokenDVP_createDelivery_260003 = "260003";
    string constant ERR_IbetSecurityTokenDVP_createDelivery_260004 = "260004";
    // IbetSecurityTokenDVP_cancelDelivery
    string constant ERR_IbetSecurityTokenDVP_cancelDelivery_260101 = "260101";
    string constant ERR_IbetSecurityTokenDVP_cancelDelivery_260102 = "260102";
    string constant ERR_IbetSecurityTokenDVP_cancelDelivery_260103 = "260103";
    string constant ERR_IbetSecurityTokenDVP_cancelDelivery_260104 = "260104";
    // IbetSecurityTokenDVP_confirmDelivery
    string constant ERR_IbetSecurityTokenDVP_confirmDelivery_260201 = "260201";
    string constant ERR_IbetSecurityTokenDVP_confirmDelivery_260202 = "260202";
    string constant ERR_IbetSecurityTokenDVP_confirmDelivery_260203 = "260203";
    string constant ERR_IbetSecurityTokenDVP_confirmDelivery_260204 = "260204";
    string constant ERR_IbetSecurityTokenDVP_confirmDelivery_260205 = "260205";
    string constant ERR_IbetSecurityTokenDVP_confirmDelivery_260206 = "260206";
    // IbetSecurityTokenDVP_finishDelivery
    string constant ERR_IbetSecurityTokenDVP_finishDelivery_260301 = "260301";
    string constant ERR_IbetSecurityTokenDVP_finishDelivery_260302 = "260302";
    string constant ERR_IbetSecurityTokenDVP_finishDelivery_260303 = "260303";
    string constant ERR_IbetSecurityTokenDVP_finishDelivery_260304 = "260304";
    string constant ERR_IbetSecurityTokenDVP_finishDelivery_260305 = "260305";
    string constant ERR_IbetSecurityTokenDVP_finishDelivery_260306 = "260306";
    // IbetSecurityTokenDVP_abortDelivery
    string constant ERR_IbetSecurityTokenDVP_abortDelivery_260401 = "260401";
    string constant ERR_IbetSecurityTokenDVP_abortDelivery_260402 = "260402";
    string constant ERR_IbetSecurityTokenDVP_abortDelivery_260403 = "260403";
    string constant ERR_IbetSecurityTokenDVP_abortDelivery_260404 = "260404";
    // IbetSecurityTokenDVP_withdraw
    string constant ERR_IbetSecurityTokenDVP_withdraw_260501 = "260501";
    // IbetSecurityTokenDVP_withdrawPartial
    string constant ERR_IbetSecurityTokenDVP_withdrawPartial_260601 = "260601";

    // 30XXXX
    // PaymentGateway_register
    string constant ERR_PaymentGateway_register_300001 = "300001";
    // PaymentGateway_approve
    string constant ERR_PaymentGateway_approve_300101 = "300101";
    // PaymentGateway_warn
    string constant ERR_PaymentGateway_warn_300201 = "300201";
    // PaymentGateway_disapprove
    string constant ERR_PaymentGateway_disapprove_300301 = "300301";
    // PaymentGateway_ban
    string constant ERR_PaymentGateway_ban_300401 = "300401";
    // PaymentGateway_modify
    string constant ERR_PaymentGateway_modify_300501 = "300501";

    // 40XXXX
    // PersonalInfo_modify
    string constant ERR_PersonalInfo_modify_400001 = "400001";
    string constant ERR_PersonalInfo_modify_400002 = "400002";

    // 50XXXX
    // Ownable_onlyOwner
    string constant ERR_Ownable_onlyOwner_500001 = "500001";
    // Ownable_transferOwnership
    string constant ERR_Ownable_transferOwnership_500101 = "500101";

    // 60XXXX
    // ContractRegistry_register
    string constant ERR_ContractRegistry_register_600001 = "600001";
    string constant ERR_ContractRegistry_register_600002 = "600002";

    // 61XXXX
    // E2EMessaging_getLastMessage
    string constant ERR_E2EMessaging_getLastMessage_610001 = "610001";
    // E2EMessaging_clearMessage
    string constant ERR_E2EMessaging_clearMessage_610101 = "610101";

    // 62XXXX
    // FreezeLog_updateLog
    string constant ERR_FreezeLog_updateLog_620001 = "620001";
}
