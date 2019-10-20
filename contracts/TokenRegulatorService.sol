pragma solidity ^0.4.24;

import "./Ownable.sol";
import "./RegulatorService.sol";
import "./IbetStandardTokenInterface.sol";

contract TokenRegulatorService is RegulatorService, Ownable {

    // @dev 取引参加者の登録情報
    struct Participant {
        address token;
        address participant;
        bool locked;
    }

    // @dev Check success code
    uint8 constant private CHECK_SUCCESS = 0;

    // @dev Check error reason : アカウントロック
    uint8 constant private CHECK_LOCKED = 1;

    // @dev Check error reason : アカウント未登録
    uint8 constant private CHECK_NOT_REGISTERD = 2;

    // @dev 購入可能者情報
    //      whitelist[tokenAddress][participantAddress]
    mapping(address => mapping(address => Participant)) whitelist;

    event Register(address indexed token, address indexed participant, bool locked);

    /**
     * @notice トークンオーナー権限チェック
     *         トークンオーナーの権限を有していることをチェック
     * @param _token トークンのアドレス
     */
    modifier onlyTokenOwner(address _token) {
        require(msg.sender == IbetStandardTokenInterface(_token).owner());
        _;
    }

    /**
     * @notice コントラクトアドレス判定
     */
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

    /**
     * @notice EOAアドレスチェック
     * @param _address チェック対象のアドレス
     */
    modifier onlyEOA(address _address) {
        if (isContract(_address)) revert();
        _;
    }

    /**
     * @notice 取引参加者登録
     * @param _token トークンのアドレス
     * @param _participant 取引参加者のアドレス（EOA）
     * @param _locked ロック状態
     */
    function register(address _token, address _participant, bool _locked)
        public
        onlyTokenOwner(_token)
        onlyEOA(_participant)
    {
        whitelist[_token][_participant].token = _token;
        whitelist[_token][_participant].participant = _participant;
        whitelist[_token][_participant].locked = _locked;
        emit Register(_token, _participant, _locked);
    }

    /**
     * @notice 取引参加者参照
     * @param _token トークンのアドレス
     * @param _participant 取引参加者のアドレス（EOA）
     */
    function getWhitelist(address _token, address _participant)
        public
        view
        returns (address token, address participant, bool locked)
    {
        token = whitelist[_token][_participant].token;
        participant = whitelist[_token][_participant].participant;
        locked = whitelist[_token][_participant].locked;
    }

    /**
     * @notice 取引可否チェック
     * @param _token トークンのアドレス
     * @param _participant 取引参加者のアドレス（EOA）
     */
    function check(address _token, address _participant)
        public
        view
        returns (uint8)
    {
        if (whitelist[_token][_participant].locked) {
            return CHECK_LOCKED;
        }

        if (whitelist[_token][_participant].participant == address(0)) {
            return CHECK_NOT_REGISTERD;
        }

        return CHECK_SUCCESS;
    }

}