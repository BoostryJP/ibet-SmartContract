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

import "../access/Ownable.sol";
import "../utils/Errors.sol";


/// @title Exchangeコントラクトの取引情報を永続化するためのEternalStorage
/// @dev Storageのアクセスは認可したExchangeコントラクト限定
contract ExchangeStorage is Ownable {

    constructor() {}

    // -------------------------------------------------------------------
    // 最新バージョンのExchangeコントラクトアドレス
    // -------------------------------------------------------------------

    // 最新バージョンのExchangeコントラクトアドレス
    address public latestVersion;

    /// @notice Exchangeコントラクトのバージョン更新
    /// @dev コントラクトオーナーのみ実行が可能
    /// @param _newVersion 新しいExchangeコントラクトのアドレス
    function upgradeVersion(address _newVersion)
        public
        onlyOwner()
    {
        latestVersion = _newVersion;
    }

    /// @dev 実行者が最新バージョンのExchangeアドレスであることをチェック
    modifier onlyLatestVersion() {
       require(msg.sender == latestVersion, ErrorCode.ERR_ExchangeStorage_onlyLatestVersion_200001);
        _;
    }

    // -------------------------------------------------------------------
    // 残高数量
    // -------------------------------------------------------------------

    // 残高情報
    // account => token => balance
    mapping(address => mapping(address => uint256)) public balances;

    /// @notice 残高の更新
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _account アドレス
    /// @param _token トークンアドレス
    /// @param _value 更新後の残高数量
    /// @return 処理結果
    function setBalance(address _account, address _token, uint256 _value)
        public
        onlyLatestVersion()
        returns (bool)
    {
        balances[_account][_token] = _value;
        return true;
    }

    /// @notice 残高数量の参照
    /// @param _account アドレス
    /// @param _token トークンアドレス
    /// @return 残高数量
    function getBalance(address _account, address _token)
        public
        view
        returns (uint256)
    {
        return balances[_account][_token];
    }

    // -------------------------------------------------------------------
    // 拘束数量
    // -------------------------------------------------------------------

    // 拘束数量
    // account => token => order commitment
    mapping(address => mapping(address => uint256)) public commitments;

    /// @notice 拘束数量の更新
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _account アドレス
    /// @param _token トークンアドレス
    /// @param _value 更新後の残高数量
    function setCommitment(address _account, address _token, uint256 _value)
        public
        onlyLatestVersion()
    {
        commitments[_account][_token] = _value;
    }

    /// @notice 拘束数量の参照
    /// @param _account アドレス
    /// @param _token トークンアドレス
    /// @return 拘束数量
    function getCommitment(address _account, address _token)
        public
        view
        returns (uint256)
    {
        return commitments[_account][_token];
    }

    // -------------------------------------------------------------------
    // 注文情報
    // -------------------------------------------------------------------
    struct Order {
        address owner; // 注文実行者
        address token; // トークンアドレス
        uint256 amount; // 注文数量
        uint256 price; // 注文単価
        bool isBuy; // 売買区分（買：True）
        address agent; // 決済業者のアドレス
        bool canceled; // キャンセル済み状態
    }

    // 注文情報
    // orderId => order
    mapping(uint256 => Order) public orderBook;

    /// @notice 注文情報の更新
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _owner 注文実行者
    /// @param _token トークンアドレス
    /// @param _amount 注文数量
    /// @param _price 注文単価
    /// @param _isBuy 売買区分（買：True）
    /// @param _agent 決済業者のアドレス
    /// @param _canceled キャンセル済み状態
    function setOrder(
        uint256 _orderId, address _owner, address _token,
        uint256 _amount, uint256 _price, bool _isBuy,
        address _agent, bool _canceled
    )
        public
        onlyLatestVersion()
    {
        orderBook[_orderId].owner = _owner;
        orderBook[_orderId].token = _token;
        orderBook[_orderId].amount = _amount;
        orderBook[_orderId].price = _price;
        orderBook[_orderId].isBuy = _isBuy;
        orderBook[_orderId].agent = _agent;
        orderBook[_orderId].canceled = _canceled;
    }

    /// @notice 注文情報の更新（注文実行者）
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _owner 注文実行者
    function setOrderOwner(uint256 _orderId, address _owner)
        public
        onlyLatestVersion()
    {
        orderBook[_orderId].owner = _owner;
    }

    /// @notice 注文情報の更新（トークンアドレス）
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _token トークンアドレス
    function setOrderToken(uint256 _orderId, address _token)
        public
        onlyLatestVersion()
    {
        orderBook[_orderId].token = _token;
    }

    /// @notice 注文情報の更新（注文数量）
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _amount 注文数量
    function setOrderAmount(uint256 _orderId, uint256 _amount)
        public
        onlyLatestVersion()
    {
        orderBook[_orderId].amount = _amount;
    }

    /// @notice 注文情報の更新（注文単価）
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _price 注文単価
    function setOrderPrice(uint256 _orderId, uint256 _price)
        public
        onlyLatestVersion()
    {
        orderBook[_orderId].price = _price;
    }

    /// @notice 注文情報の更新（売買区分）
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _isBuy 売買区分（買：True）
    function setOrderIsBuy(uint256 _orderId, bool _isBuy)
        public
        onlyLatestVersion()
    {
        orderBook[_orderId].isBuy = _isBuy;
    }

    /// @notice 注文情報の更新（決済業者のアドレス）
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _agent 決済業者のアドレス
    function setOrderAgent(uint256 _orderId, address _agent)
        public
        onlyLatestVersion()
    {
        orderBook[_orderId].agent = _agent;
    }

    /// @notice 注文情報の更新（キャンセル済み状態）
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _canceled キャンセル済み状態
    function setOrderCanceled(uint256 _orderId, bool _canceled)
        public
        onlyLatestVersion()
    {
        orderBook[_orderId].canceled = _canceled;
    }

    /// @notice 注文情報の参照
    /// @param _orderId 注文ID
    /// @return owner 注文実行者
    /// @return token トークンアドレス
    /// @return amount 注文数量
    /// @return price 注文単価
    /// @return isBuy 売買区分（買：True）
    /// @return agent 決済業者のアドレス
    /// @return canceled キャンセル済み状態
    function getOrder(uint256 _orderId)
        public
        view
        returns(
            address owner, address token, uint256 amount, uint256 price,
            bool isBuy, address agent, bool canceled
        )
    {
        return (
            orderBook[_orderId].owner,
            orderBook[_orderId].token,
            orderBook[_orderId].amount,
            orderBook[_orderId].price,
            orderBook[_orderId].isBuy,
            orderBook[_orderId].agent,
            orderBook[_orderId].canceled
        );
    }

    /// @notice 注文情報の参照（注文実行者）
    /// @param _orderId 注文ID
    /// @return 注文実行者
    function getOrderOwner(uint256 _orderId)
        public
        view
        returns(address)
    {
        return orderBook[_orderId].owner;
    }

    /// @notice 注文情報の参照（トークンアドレス）
    /// @param _orderId 注文ID
    /// @return トークンアドレス
    function getOrderToken(uint256 _orderId)
        public
        view
        returns(address)
    {
        return orderBook[_orderId].token;
    }

    /// @notice 注文情報の参照（注文数量）
    /// @param _orderId 注文ID
    /// @return 注文数量
    function getOrderAmount(uint256 _orderId)
        public
        view
        returns(uint256)
    {
        return orderBook[_orderId].amount;
    }

    /// @notice 注文情報の参照（注文単価）
    /// @param _orderId 注文ID
    /// @return 注文単価
    function getOrderPrice(uint256 _orderId)
        public
        view
        returns(uint256)
    {
        return orderBook[_orderId].price;
    }

    /// @notice 注文情報の参照（売買区分）
    /// @param _orderId 注文ID
    /// @return 売買区分（買：True）
    function getOrderIsBuy(uint256 _orderId)
        public
        view
        returns(bool)
    {
        return orderBook[_orderId].isBuy;
    }

    /// @notice 注文情報の参照（決済業者のアドレス）
    /// @param _orderId 注文ID
    /// @return 決済業者のアドレス
    function getOrderAgent(uint256 _orderId)
        public
        view
        returns(address)
    {
        return orderBook[_orderId].agent;
    }

    /// @notice 注文情報の参照（キャンセル済み状態）
    /// @param _orderId 注文ID
    /// @return キャンセル済み状態
    function getOrderCanceled(uint256 _orderId)
        public
        view
        returns(bool)
    {
        return orderBook[_orderId].canceled;
    }

    // -------------------------------------------------------------------
    // 直近注文ID
    // -------------------------------------------------------------------

    // 直近注文ID
    uint256 public latestOrderId = 0;

    /// @notice 直近注文IDの更新
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _latestOrderId 直近注文ID
    function setLatestOrderId(uint256 _latestOrderId)
        public
        onlyLatestVersion()
    {
        latestOrderId = _latestOrderId;
    }

    /// @notice 直近注文IDの参照
    /// @return 直近注文ID
    function getLatestOrderId()
        public
        view
        returns(uint256)
    {
        return latestOrderId;
    }

    // -------------------------------------------------------------------
    // 約定情報
    // -------------------------------------------------------------------
    struct Agreement {
        address counterpart; // 約定相手
        uint256 amount; // 約定数量
        uint256 price; // 約定単価
        bool canceled; // キャンセル済み状態
        bool paid; // 支払い済み状態
        uint256 expiry; // 有効期限（約定から１４日）
    }

    // 約定情報
    // orderId => agreementId => Agreement
    mapping(uint256 => mapping(uint256 => Agreement)) public agreements;

    /// @notice 約定情報の更新
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @param _counterpart 約定相手
    /// @param _amount 約定数量
    /// @param _price 約定単価
    /// @param _canceled キャンセル済み状態
    /// @param _paid 支払済状態
    /// @param _expiry 有効期限
    function setAgreement(
        uint256 _orderId, uint256 _agreementId,
        address _counterpart, uint256 _amount, uint256 _price,
        bool _canceled, bool _paid, uint256 _expiry
    )
        public
        onlyLatestVersion()
    {
        agreements[_orderId][_agreementId].counterpart = _counterpart;
        agreements[_orderId][_agreementId].amount = _amount;
        agreements[_orderId][_agreementId].price = _price;
        agreements[_orderId][_agreementId].canceled = _canceled;
        agreements[_orderId][_agreementId].paid = _paid;
        agreements[_orderId][_agreementId].expiry = _expiry;
    }

    /// @notice 約定情報の更新（約定相手）
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @param _counterpart 約定相手
    function setAgreementCounterpart(uint256 _orderId, uint256 _agreementId, address _counterpart)
        public
        onlyLatestVersion()
    {
        agreements[_orderId][_agreementId].counterpart = _counterpart;
    }

    /// @notice 約定情報の更新（約定数量）
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @param _amount 約定数量
    function setAgreementAmount(uint256 _orderId, uint256 _agreementId, uint256 _amount)
        public
        onlyLatestVersion()
    {
        agreements[_orderId][_agreementId].amount = _amount;
    }

    /// @notice 約定情報の更新（約定単価）
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @param _price 約定単価
    function setAgreementPrice(uint256 _orderId, uint256 _agreementId, uint256 _price)
        public
        onlyLatestVersion()
    {
        agreements[_orderId][_agreementId].price = _price;
    }

    /// @notice 約定情報の更新（キャンセル済み状態）
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @param _canceled キャンセル済み状態
    function setAgreementCanceled(uint256 _orderId, uint256 _agreementId, bool _canceled)
        public
        onlyLatestVersion()
    {
        agreements[_orderId][_agreementId].canceled = _canceled;
    }

    /// @notice 約定情報の更新（支払済状態）
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @param _paid 支払済状態
    function setAgreementPaid(uint256 _orderId, uint256 _agreementId, bool _paid)
        public
        onlyLatestVersion()
    {
        agreements[_orderId][_agreementId].paid = _paid;
    }

    /// @notice 約定情報の更新（有効期限）
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @param _expiry 有効期限
    function setAgreementExpiry(uint256 _orderId, uint256 _agreementId, uint256 _expiry)
        public
        onlyLatestVersion()
    {
        agreements[_orderId][_agreementId].expiry = _expiry;
    }

    /// @notice 約定情報の参照
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @return _counterpart 約定相手
    /// @return _amount 約定数量
    /// @return _price 約定単価
    /// @return _canceled キャンセル済み状態
    /// @return _paid 支払済状態
    /// @return _expiry 有効期限
    function getAgreement(uint256 _orderId, uint256 _agreementId)
        public
        view
        returns (address _counterpart, uint256 _amount, uint256 _price,
        bool _canceled, bool _paid, uint256 _expiry)
    {
        return (
            agreements[_orderId][_agreementId].counterpart,
            agreements[_orderId][_agreementId].amount,
            agreements[_orderId][_agreementId].price,
            agreements[_orderId][_agreementId].canceled,
            agreements[_orderId][_agreementId].paid,
            agreements[_orderId][_agreementId].expiry
        );
    }

    /// @notice 約定情報の参照（約定相手）
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @return 約定相手
    function getAgreementCounterpart(uint256 _orderId, uint256 _agreementId)
        public
        view
        returns(address)
    {
        return agreements[_orderId][_agreementId].counterpart;
    }

    /// @notice 約定情報の参照（約定数量）
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @return 約定数量
    function getAgreementAmount(uint256 _orderId, uint256 _agreementId)
        public
        view
        returns(uint256)
    {
        return agreements[_orderId][_agreementId].amount;
    }

    /// @notice 約定情報の参照（役従尾単価）
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @return 約定単価
    function getAgreementPrice(uint256 _orderId, uint256 _agreementId)
        public
        view
        returns(uint256)
    {
        return agreements[_orderId][_agreementId].price;
    }

    /// @notice 約定情報の参照（キャンセル済み状態）
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @return キャンセル済み状態
    function getAgreementCanceled(uint256 _orderId, uint256 _agreementId)
        public
        view
        returns(bool)
    {
        return agreements[_orderId][_agreementId].canceled;
    }

    /// @notice 約定情報の参照（支払済状態）
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @return 支払済状態
    function getAgreementPaid(uint256 _orderId, uint256 _agreementId)
        public
        view
        returns(bool)
    {
        return agreements[_orderId][_agreementId].paid;
    }

    /// @notice 約定情報の参照（有効期限）
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @return expiry 有効期限
    function getAgreementExpiry(uint256 _orderId, uint256 _agreementId)
        public
        view
        returns(uint256)
    {
        return agreements[_orderId][_agreementId].expiry;
    }

    // -------------------------------------------------------------------
    // 直近約定ID
    // -------------------------------------------------------------------

    // 直近約定ID
    // orderId => latestAgreementId
    mapping(uint256 => uint256) public latestAgreementIds;

    /// @notice 直近約定IDの更新
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _latestAgreementId 直近約定ID
    function setLatestAgreementId(uint256 _orderId, uint256 _latestAgreementId)
        public
        onlyLatestVersion()
    {
        latestAgreementIds[_orderId] = _latestAgreementId;
    }

    /// @notice 直近約定IDの参照
    /// @param _orderId 注文ID
    /// @return 直近約定ID
    function getLatestAgreementId(uint256 _orderId)
        public
        view
        returns(uint256)
    {
        return latestAgreementIds[_orderId];
    }

    // -------------------------------------------------------------------
    // 現在値
    // -------------------------------------------------------------------

    // 現在値
    // token => latest_price
    mapping(address => uint256) public lastPrice;

    /// @notice 現在値の更新
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _token トークンアドレス
    /// @param _value 現在値
    function setLastPrice(address _token, uint256 _value)
        public
        onlyLatestVersion()
    {
        lastPrice[_token] = _value;
    }

    /// @notice 現在値の参照
    /// @param _token トークンアドレス
    /// @return 現在値
    function getLastPrice(address _token)
        public
        view
        returns(uint256)
    {
        return lastPrice[_token];
    }

}
