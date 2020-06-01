pragma solidity ^0.4.24;
pragma experimental ABIEncoderV2;

import "./Ownable.sol";
import "./OTCExchangeStorageModel.sol";


/// @title Exchangeコントラクトの取引情報を永続化するためのEternalStorage
/// @dev Storageのアクセスは認可したExchangeコントラクト限定
contract OTCExchangeStorage is Ownable, OTCExchangeStorageModel {

    constructor() public {}

    /// -------------------------------------------------------------------
    /// 最新バージョンのExchangeコントラクトアドレス
    /// -------------------------------------------------------------------

    /// 最新バージョンのExchangeコントラクトアドレス
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
        require(msg.sender == latestVersion);
        _;
    }

    /// -------------------------------------------------------------------
    /// 残高数量
    /// -------------------------------------------------------------------

    /// 残高情報
    /// account => token => balance
    mapping(address => mapping(address => uint256)) private balances;

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

    /// -------------------------------------------------------------------
    /// 拘束数量（約定済みの数量）
    /// -------------------------------------------------------------------

    /// 拘束数量
    /// account => token => order commitment
    mapping(address => mapping(address => uint256)) private commitments;

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

    /// -------------------------------------------------------------------
    /// 注文情報
    /// -------------------------------------------------------------------

    /// 注文情報
    /// orderId => order
    mapping(uint256 => OTCExchangeStorageModel.OTCOrder) private orderBook;

    /// @notice 注文情報の更新
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _order 注文情報
    function setOrder(uint256 _orderId, OTCExchangeStorageModel.OTCOrder _order)
        public
        onlyLatestVersion()
    {
        orderBook[_orderId] = _order;
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
    /// @return 注文情報
    function getOrder(uint256 _orderId)
        public
        view
        returns (OTCExchangeStorageModel.OTCOrder)
    {
        return orderBook[_orderId];
    }

    /// -------------------------------------------------------------------
    /// 直近注文ID
    /// -------------------------------------------------------------------

    /// 直近注文ID
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
        returns (uint256)
    {
        return latestOrderId;
    }

    /// -------------------------------------------------------------------
    /// 約定情報
    /// -------------------------------------------------------------------

    /// 約定情報
    /// orderId => agreementId => Agreement
    mapping(uint256 => mapping(uint256 => OTCExchangeStorageModel.OTCAgreement)) public agreements;

    /// @notice 約定情報の更新
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @param _agreement 約定情報
    function setAgreement(
        uint256 _orderId, uint256 _agreementId,
        OTCExchangeStorageModel.OTCAgreement _agreement
    )
        public
        onlyLatestVersion()
    {
        agreements[_orderId][_agreementId] = _agreement;
    }

    /// @notice 約定情報の更新（キャンセル済み状態）
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @param _canceled キャンセル済み状態
    function setAgreementCanceled(
        uint256 _orderId,
        uint256 _agreementId,
        bool _canceled
    )
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
    function setAgreementPaid(
        uint256 _orderId,
        uint256 _agreementId,
        bool _paid
    )
        public
        onlyLatestVersion()
    {
        agreements[_orderId][_agreementId].paid = _paid;
    }

    /// @notice 約定情報の参照
    /// @param _orderId 注文ID
    /// @param _agreementId 約定ID
    /// @return 約定情報
    function getAgreement(uint256 _orderId, uint256 _agreementId)
        public
        view
        returns (OTCExchangeStorageModel.OTCAgreement)
    {
        return agreements[_orderId][_agreementId];
    }

    /// -------------------------------------------------------------------
    /// 直近約定ID
    ///-------------------------------------------------------------------

    /// 直近約定ID
    /// orderId => latestAgreementId
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
        returns (uint256)
    {
        return latestAgreementIds[_orderId];
    }

}
