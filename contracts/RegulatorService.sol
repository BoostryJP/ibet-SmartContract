pragma solidity ^0.4.24;

import "../interfaces/Ownable.sol";

/// @notice RegulatorServiceの標準インターフェース
contract RegulatorService {

    /*
    * @notice 取引可否チェック
    * @param _participant 取引参加者のアドレス（EOA）
    * @return uint8 リターンコード：成功（0）
    */
    function check(address _participant)
        public
        view
        returns (uint8);

}
