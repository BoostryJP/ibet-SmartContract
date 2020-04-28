pragma solidity ^0.4.24;

import "./Ownable.sol";

// =========================================================================
// ExchangeStorage
//   Exchange コントラクトの取引情報を管理するための Eternal Storage
// =========================================================================
contract ExchangeStorage is Ownable {

    constructor() public {}

    // -------------------------------------------------------------------
    // 最新バージョンのExchangeコントラクトアドレス
    // -------------------------------------------------------------------
    address public latestVersion;

    function upgradeVersion(address _newVersion)
        public
        onlyOwner()
    {
        latestVersion = _newVersion;
    }

    modifier onlyLatestVersion() {
       require(msg.sender == latestVersion);
        _;
    }

    // -------------------------------------------------------------------
    // 残高数量
    // -------------------------------------------------------------------

    // +++++++++++++++++++
    // 残高情報
    // account => token => balance
    // +++++++++++++++++++
    mapping(address => mapping(address => uint256)) public balances;

    function setBalance(address _account, address _token, uint256 _value)
        public
        returns (bool)
    {
        balances[_account][_token] = _value;
        return true;
    }

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

    // +++++++++++++++++++
    // 拘束数量
    // account => token => order commitment
    // +++++++++++++++++++
    mapping(address => mapping(address => uint256)) public commitments;

    function setCommitment(address _account, address _token, uint256 _value)
        public
        onlyLatestVersion()
    {
        commitments[_account][_token] = _value;
    }

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
        address owner;
        address token;
        uint256 amount; // 数量
        uint256 price; // 価格
        bool isBuy; // 売買区分（買い：True）
        address agent; // 決済業者のアドレス
        bool canceled; // キャンセル済みフラグ
    }

    // +++++++++++++++++++
    // 注文情報
    // orderId => order
    // +++++++++++++++++++
    mapping(uint256 => Order) public orderBook;

    function setOrder(
        uint256 _orderId, address _owner, address _token,
        uint256 _amount, uint256 _price, bool _isBuy,
        address _agent, bool _canceled)
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

    function setOrderOwner(uint256 _orderId, address _owner)
        public
        onlyLatestVersion()
    {
        orderBook[_orderId].owner = _owner;
    }

    function setOrderToken(uint256 _orderId, address _token)
        public
        onlyLatestVersion()
    {
        orderBook[_orderId].token = _token;
    }

    function setOrderAmount(uint256 _orderId, uint256 _amount)
        public
        onlyLatestVersion()
    {
        orderBook[_orderId].amount = _amount;
    }

    function setOrderPrice(uint256 _orderId, uint256 _price)
        public
        onlyLatestVersion()
    {
        orderBook[_orderId].price = _price;
    }

    function setOrderIsBuy(uint256 _orderId, bool _isBuy)
        public
        onlyLatestVersion()
    {
        orderBook[_orderId].isBuy = _isBuy;
    }

    function setOrderAgent(uint256 _orderId, address _agent)
        public
        onlyLatestVersion()
    {
        orderBook[_orderId].agent = _agent;
    }

    function setOrderCanceled(uint256 _orderId, bool _canceled)
        public
        onlyLatestVersion()
    {
        orderBook[_orderId].canceled = _canceled;
    }

    function getOrder(uint256 _orderId)
        public
        view
        returns(address owner, address token, uint256 amount, uint256 price,
        bool isBuy, address agent, bool canceled)
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


    function getOrderOwner(uint256 _orderId)
        public
        view
        returns(address)
    {
        return orderBook[_orderId].owner;
    }

    function getOrderToken(uint256 _orderId)
        public
        view
        returns(address)
    {
        return orderBook[_orderId].token;
    }

    function getOrderAmount(uint256 _orderId)
        public
        view
        returns(uint256)
    {
        return orderBook[_orderId].amount;
    }

    function getOrderPrice(uint256 _orderId)
        public
        view
        returns(uint256)
    {
        return orderBook[_orderId].price;
    }

    function getOrderIsBuy(uint256 _orderId)
        public
        view
        returns(bool)
    {
        return orderBook[_orderId].isBuy;
    }

    function getOrderAgent(uint256 _orderId)
        public
        view
        returns(address)
    {
        return orderBook[_orderId].agent;
    }

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
    uint256 public latestOrderId = 0;

    function setLatestOrderId(uint256 _latestOrderId)
        public
        onlyLatestVersion()
    {
        latestOrderId = _latestOrderId;
    }

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
        uint256 price; // 約定価格
        bool canceled; // キャンセル済みフラグ
        bool paid; // 支払い済みフラグ
        uint256 expiry; // 有効期限（約定から１４日）
    }

    // +++++++++++++++++++
    // 約定情報
    // orderId => agreementId => Agreement
    // +++++++++++++++++++
    mapping(uint256 => mapping(uint256 => Agreement)) public agreements;

    function setAgreement(uint256 _orderId, uint256 _agreementId,
        address _counterpart, uint256 _amount, uint256 _price,
        bool _canceled, bool _paid, uint256 _expiry)
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

    function setAgreementCounterpart(uint256 _orderId, uint256 _agreementId, address _counterpart)
        public
        onlyLatestVersion()
    {
        agreements[_orderId][_agreementId].counterpart = _counterpart;
    }

    function setAgreementAmount(uint256 _orderId, uint256 _agreementId, uint256 _amount)
        public
        onlyLatestVersion()
    {
        agreements[_orderId][_agreementId].amount = _amount;
    }

    function setAgreementPrice(uint256 _orderId, uint256 _agreementId, uint256 _price)
        public
        onlyLatestVersion()
    {
        agreements[_orderId][_agreementId].price = _price;
    }

    function setAgreementCanceled(uint256 _orderId, uint256 _agreementId, bool _canceled)
        public
        onlyLatestVersion()
    {
        agreements[_orderId][_agreementId].canceled = _canceled;
    }

    function setAgreementPaid(uint256 _orderId, uint256 _agreementId, bool _paid)
        public
        onlyLatestVersion()
    {
        agreements[_orderId][_agreementId].paid = _paid;
    }

    function setAgreementExpiry(uint256 _orderId, uint256 _agreementId, uint256 _expiry)
        public
        onlyLatestVersion()
    {
        agreements[_orderId][_agreementId].expiry = _expiry;
    }

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

    function getAgreementCounterpart(uint256 _orderId, uint256 _agreementId)
        public
        view
        returns(address)
    {
        return agreements[_orderId][_agreementId].counterpart;
    }

    function getAgreementAmount(uint256 _orderId, uint256 _agreementId)
        public
        view
        returns(uint256)
    {
        return agreements[_orderId][_agreementId].amount;
    }

    function getAgreementPrice(uint256 _orderId, uint256 _agreementId)
        public
        view
        returns(uint256)
    {
        return agreements[_orderId][_agreementId].price;
    }

    function getAgreementCanceled(uint256 _orderId, uint256 _agreementId)
        public
        view
        returns(bool)
    {
        return agreements[_orderId][_agreementId].canceled;
    }

    function getAgreementPaid(uint256 _orderId, uint256 _agreementId)
        public
        view
        returns(bool)
    {
        return agreements[_orderId][_agreementId].paid;
    }

    function getAgreementExpiry(uint256 _orderId, uint256 _agreementId)
        public
        view
        returns(uint256)
    {
        return agreements[_orderId][_agreementId].expiry;
    }

    // -------------------------------------------------------------------
    // 直近約定ID
    // orderId => latestAgreementId
    // -------------------------------------------------------------------
    mapping(uint256 => uint256) public latestAgreementIds;

    function setLatestAgreementId(uint256 _orderId, uint256 _latestAgreementId)
        public
        onlyLatestVersion()
    {
        latestAgreementIds[_orderId] = _latestAgreementId;
    }

    function getLatestAgreementId(uint256 _orderId)
        public
        view
        returns(uint256)
    {
        return latestAgreementIds[_orderId];
    }

    // -------------------------------------------------------------------
    // 現在値
    // token => latest_price
    // -------------------------------------------------------------------
    mapping(address => uint256) public lastPrice;

    function setLastPrice(address _token, uint256 _value)
        public
        onlyLatestVersion()
    {
        lastPrice[_token] = _value;
    }

    function getLastPrice(address _token)
        public
        view
        returns(uint256)
    {
        return lastPrice[_token];
    }

}