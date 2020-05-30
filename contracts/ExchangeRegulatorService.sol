pragma solidity ^0.4.24;

import "./Ownable.sol";
import "./RegulatorService.sol";

/// @title Exchangeの取引参加者制限サービス
/// @dev Exchangeの取引参加者制限
contract ExchangeRegulatorService is RegulatorService, Ownable {

    /// 取引参加者の登録情報
    struct Participant {
        address participant; // 取引参加者EOAアドレス
        bool locked; // ロック状態
    }

    /// Check success code
    uint8 constant private CHECK_SUCCESS = 0;

    /// Check error reason : アカウントロック
    uint8 constant private CHECK_LOCKED = 1;

    /// Check error reason : アカウント未登録
    uint8 constant private CHECK_NOT_REGISTERD = 2;

    /// 購入可能者情報
    /// whitelist[participantAddress]
    mapping(address => Participant) whitelist;

    /// 参加者登録時イベント
    event Register(address indexed participant, bool locked);

    /// @dev コントラクトアドレス判定
    /// @param _address アドレス
    /// @return 判定結果
    function isContract(address _address)
        private
        view
        returns (bool)
    {
        uint length;
        assembly {
            length := extcodesize(_address)
        }
        return (length>0);
    }

    /// @dev EOAアドレスチェック
    /// @param _address チェック対象のアドレス
    modifier onlyEOA(address _address) {
        if (isContract(_address)) revert();
        _;
    }

    /// @notice 取引参加者登録
    /// @dev コントラクトオーナーのみ実行可能
    /// @param _participant 取引参加者のEOAアドレス
    /// @param _locked ロック状態
    function register(address _participant, bool _locked)
        public
        onlyOwner()
        onlyEOA(_participant)
    {
        whitelist[_participant].participant = _participant;
        whitelist[_participant].locked = _locked;
        emit Register(_participant, _locked);
    }

    /// @notice 取引参加者参照
    /// @param _participant 取引参加者のEOAアドレス
    /// @return participant 取引参加者のEOAアドレス
    /// @return ロック状態
    function getWhitelist(address _participant)
        public
        view
        returns (address participant, bool locked)
    {
        participant = whitelist[_participant].participant;
        locked = whitelist[_participant].locked;
    }

    /// @notice 取引可否チェック
    /// @param _participant 取引参加者のアドレス（EOA）
    /// @return チェック結果
    function check(address _participant)
        public
        view
        returns (uint8)
    {
        if (whitelist[_participant].locked) {
            return CHECK_LOCKED;
        }

        if (whitelist[_participant].participant == address(0)) {
            return CHECK_NOT_REGISTERD;
        }

        return CHECK_SUCCESS;
    }

}
