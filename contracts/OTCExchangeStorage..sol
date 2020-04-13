pragma solidity ^0.4.24;

import "./Ownable.sol";


// =========================================================================
// OTCExchangeStorage
//   Exchange コントラクトの取引情報を管理するための Eternal Storage
//   Storageのアクセスは認可したExchangeコントラクト限定
// =========================================================================
contract OTCExchangeStorage is Ownable {

    constructor() public {}

    // -------------------------------------------------------------------
    // 認可済みコントラクトアドレス
    // -------------------------------------------------------------------
    mapping(address => bool) public authorizedAddress;

    // ファンクション：アドレス認可
    // オーナーのみ実行可能
    function authorize(address _address, bool _auth) public onlyOwner() {
        authorizedAddress[_address] = _auth;
    }

    modifier onlyAuthorized() {
        require(authorizedAddress[msg.sender]);
        _;
    }

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
        onlyAuthorized()
        returns (bool)
    {
        balances[_account][_token] = _value;
    }

    function getBalance(address _account, address _token)
        public
        view
        onlyAuthorized()
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
        onlyAuthorized()
        returns (uint256)
    {
        return commitments[_account][_token];
    }

    // -------------------------------------------------------------------
    // 注文情報
    // -------------------------------------------------------------------
    struct Order {
        address owner;
        address counterpart;
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
    mapping(uint256 => Order) private orderBook;

    function setOrder(
        uint256 _orderId,
        address _owner,
        address _counterpart;
        address _token,
        uint256 _amount,
        uint256 _price,
        bool _isBuy,
        address _agent,
        bool _canceled
    ) public onlyLatestVersion() {
        orderBook[_orderId].owner = _owner;
        orderBook[_orderId].counterpart = _counterpart;
        orderBook[_orderId].token = _token;
        orderBook[_orderId].amount = _amount;
        orderBook[_orderId].price = _price;
        orderBook[_orderId].isBuy = _isBuy;
        orderBook[_orderId].agent = _agent;
        orderBook[_orderId].canceled = _canceled;
    }

    function setOrderCanceled(uint256 _orderId, bool _canceled)
        public
        onlyLatestVersion()
    {
        orderBook[_orderId].canceled = _canceled;
    }

    function getOrder(uint256 _orderId)
        public
        onlyAuthorized()
        view
        returns (
            address owner,
            address counterpart,
            address token,
            uint256 amount,
            uint256 price,
            bool isBuy,
            address agent,
            bool canceled
        )
    {
        return (
            orderBook[_orderId].owner,
            orderBook[_orderId].counterpart,
            orderBook[_orderId].token,
            orderBook[_orderId].amount,
            orderBook[_orderId].price,
            orderBook[_orderId].isBuy,
            orderBook[_orderId].agent,
            orderBook[_orderId].canceled
        );
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

    function getLatestOrderId() public onlyAuthorized() view returns (uint256) {
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

    function setAgreement(
        uint256 _orderId,
        uint256 _agreementId,
        address _counterpart,
        uint256 _amount,
        uint256 _price,
        bool _canceled,
        bool _paid,
        uint256 _expiry
    ) public onlyLatestVersion() {
        agreements[_orderId][_agreementId].counterpart = _counterpart;
        agreements[_orderId][_agreementId].amount = _amount;
        agreements[_orderId][_agreementId].price = _price;
        agreements[_orderId][_agreementId].canceled = _canceled;
        agreements[_orderId][_agreementId].paid = _paid;
        agreements[_orderId][_agreementId].expiry = _expiry;
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

    function setAgreementExpiry(
        uint256 _orderId,
        uint256 _agreementId,
        uint256 _expiry
    ) public onlyLatestVersion() {
        agreements[_orderId][_agreementId].expiry = _expiry;
    }

    function getAgreement(uint256 _orderId, uint256 _agreementId)
        public
        view
        onlyAuthorized()
        returns (
            address _counterpart,
            uint256 _amount,
            uint256 _price,
            bool _canceled,
            bool _paid,
            uint256 _expiry
        )
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
        onlyAuthorized()
        returns (uint256)
    {
        return latestAgreementIds[_orderId];
    }
}