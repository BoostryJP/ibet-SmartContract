pragma solidity ^0.4.24;
pragma experimental ABIEncoderV2;

import "./Ownable.sol";
import "./ExchangeStorageModel.sol";


// =========================================================================
// OTCExchangeStorage
//   Exchange コントラクトの取引情報を管理するための Eternal Storage
//   Storageのアクセスは認可したExchangeコントラクト限定
// =========================================================================
contract OTCExchangeStorage is Ownable, ExchangeStorageModel {
    constructor() public {}

    // -------------------------------------------------------------------
    // 認可済みコントラクトアドレス
    // -------------------------------------------------------------------
    mapping(address => bool) public registeredAddress;

    // -------------------------------------------------------------------
    // 最新バージョンのExchangeコントラクトアドレス
    // -------------------------------------------------------------------
    address public latestVersion;

    function upgradeVersion(address _newVersion) public onlyOwner() {
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
    mapping(address => mapping(address => uint256)) private balances;

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
    // 拘束数量（約定済みの数量）
    // -------------------------------------------------------------------

    // +++++++++++++++++++
    // 拘束数量
    // account => token => order commitment
    // +++++++++++++++++++
    mapping(address => mapping(address => uint256)) private commitments;

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


    // +++++++++++++++++++
    // 注文情報
    // orderId => order
    // +++++++++++++++++++
    mapping(uint256 => ExchangeStorageModel.OTCOrder) private orderBook;

    function setOrder(
        uint256 _orderId,
        ExchangeStorageModel.OTCOrder _order
    ) public onlyLatestVersion() {
        orderBook[_orderId] = _order;
    }
    
    function setOrderAmount(uint256 _orderId, uint256 _amount)
        public
        onlyLatestVersion()
    {
        orderBook[_orderId].amount = _amount;
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
        returns (ExchangeStorageModel.OTCOrder)
    {
        return orderBook[_orderId];
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

    function getLatestOrderId() public view returns (uint256) {
        return latestOrderId;
    }

    // -------------------------------------------------------------------
    // 約定情報
    // -------------------------------------------------------------------

    // +++++++++++++++++++
    // 約定情報
    // orderId => agreementId => Agreement
    // +++++++++++++++++++
    mapping(uint256 => mapping(uint256 => ExchangeStorageModel.OTCAgreement)) public agreements;

    function setAgreement(
        uint256 _orderId,
        uint256 _agreementId,
        ExchangeStorageModel.OTCAgreement _agreement
    ) public onlyLatestVersion() {
        agreements[_orderId][_agreementId] = _agreement;
    }

    function setAgreementCanceled(
        uint256 _orderId,
        uint256 _agreementId,
        bool _canceled
    ) public onlyLatestVersion() {
        agreements[_orderId][_agreementId].canceled = _canceled;
    }

    function setAgreementPaid(
        uint256 _orderId,
        uint256 _agreementId,
        bool _paid
    ) public onlyLatestVersion() {
        agreements[_orderId][_agreementId].paid = _paid;
    }

    function getAgreement(uint256 _orderId, uint256 _agreementId)
        public
        view
        returns (ExchangeStorageModel.OTCAgreement)
    {
        return agreements[_orderId][_agreementId];
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
        returns (uint256)
    {
        return latestAgreementIds[_orderId];
    }
}
