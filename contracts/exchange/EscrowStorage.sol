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


/// @title Escrowコントラクトのステートを永続化するためのEternalStorage
/// @dev Storageのアクセスは認可したEscrowコントラクトに限定する
contract EscrowStorage is Ownable {

    constructor() {}

    // -------------------------------------------------------------------
    // 最新バージョンのEscrowコントラクトアドレス：LatestVersion
    // -------------------------------------------------------------------

    // 最新バージョンのEscrowコントラクトアドレス
    address public latestVersion;

    /// @notice Escrowコントラクトのバージョン更新
    /// @dev コントラクトオーナーのみ実行が可能
    /// @param _newVersion 新しいEscrowコントラクトのアドレス
    function upgradeVersion(address _newVersion)
        public
        onlyOwner()
    {
        latestVersion = _newVersion;
    }

    /// @dev 実行者が最新バージョンのEscrowアドレスであることをチェック
    modifier onlyLatestVersion() {
       require(msg.sender == latestVersion);
        _;
    }

    // -------------------------------------------------------------------
    // 残高：Balance
    // -------------------------------------------------------------------

    // 残高情報
    // account => token => balance
    mapping(address => mapping(address => uint256)) private balances;

    /// @notice 残高の更新
    /// @dev 最新バージョンのEscrowコントラクトのみ実行が可能
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
    // エスクロー中数量：Deposit
    // -------------------------------------------------------------------

    // エスクロー中数量
    // account => token => deposit
    mapping(address => mapping(address => uint256)) private deposits;

    /// @notice エスクロー中数量の更新
    /// @dev 最新バージョンのEscrowコントラクトのみ実行が可能
    /// @param _account アドレス
    /// @param _token トークンアドレス
    /// @param _value 更新後の数量
    /// @return 処理結果
    function setDeposit(address _account, address _token, uint256 _value)
        public
        onlyLatestVersion()
        returns (bool)
    {
        deposits[_account][_token] = _value;
        return true;
    }

    /// @notice エスクロー中数量の参照
    /// @param _account アドレス
    /// @param _token トークンアドレス
    /// @return エスクロー中数量
    function getDeposit(address _account, address _token)
        public
        view
        returns (uint256)
    {
        return deposits[_account][_token];
    }

    // -------------------------------------------------------------------
    // エスクロー情報：Escrow
    // -------------------------------------------------------------------
    struct Escrow {
        address token;
        address sender;
        address recipient;
        uint256 amount;
        address agent;
        bool status;
    }

    // エスクロー情報
    // escrowId => Escrow
    mapping(uint256 => Escrow) private escrow;

    // 直近エスクローID
    uint256 public latestEscrowId = 0;

    /// @notice 直近エスクローIDの更新
    /// @dev 最新バージョンのExchangeコントラクトのみ実行が可能
    /// @param _latestEscrowId 直近エスクローID
    function setLatestEscrowId(uint256 _latestEscrowId)
        public
        onlyLatestVersion()
    {
        latestEscrowId = _latestEscrowId;
    }

    /// @notice 直近エスクローIDの参照
    /// @return 直近エスクローID
    function getLatestEscrowId()
        public
        view
        returns(uint256)
    {
        return latestEscrowId;
    }

    // @notice エスクロー情報の更新
    function setEscrow(
        uint256 _escrowId,
        address _token,
        address _sender,
        address _recipient,
        uint256 _amount,
        address _agent,
        bool _status
    )
        public
        onlyLatestVersion()
    {
        escrow[_escrowId].token = _token;
        escrow[_escrowId].sender = _sender;
        escrow[_escrowId].recipient = _recipient;
        escrow[_escrowId].amount = _amount;
        escrow[_escrowId].agent = _agent;
        escrow[_escrowId].status = _status;
    }

    // @notice エスクロー情報の取得
    function getEscrow(
        uint256 _escrowId
    )
        public
        view
        returns(
            address token,
            address sender,
            address recipient,
            uint256 amount,
            address agent,
            bool status
        )
    {
        return (
            escrow[_escrowId].token,
            escrow[_escrowId].sender,
            escrow[_escrowId].recipient,
            escrow[_escrowId].amount,
            escrow[_escrowId].agent,
            escrow[_escrowId].status
        );
    }

}
