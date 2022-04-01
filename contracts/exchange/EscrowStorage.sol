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

    /// 最新バージョンのEscrowコントラクトアドレス
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

    /// 残高情報
    /// account => token => amount
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
    // 拘束数量：Commitment
    // -------------------------------------------------------------------

    /// 拘束数量
    /// account => token => amount
    mapping(address => mapping(address => uint256)) public commitments;

    /// @notice 拘束数量の更新
    /// @dev 最新バージョンのEscrowコントラクトのみ実行が可能
    /// @param _account アドレス
    /// @param _token トークンアドレス
    /// @param _value 更新後の数量
    /// @return 処理結果
    function setCommitment(address _account, address _token, uint256 _value)
        public
        onlyLatestVersion()
        returns (bool)
    {
        commitments[_account][_token] = _value;
        return true;
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
    // エスクロー情報：Escrow
    // -------------------------------------------------------------------

    struct Escrow {
        address token;  // トークンアドレス
        address sender;  // 送信者
        address recipient;  // 受信者
        uint256 amount;  // 数量
        address agent;  // エスクローエージェント
        bool valid;  // 有効状態
    }

    /// エスクロー情報
    /// escrowId => Escrow
    mapping(uint256 => Escrow) private escrow;

    /// 直近エスクローID
    uint256 private latestEscrowId = 0;

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

    /// @notice エスクロー情報の更新
    /// @param _escrowId エスクローID
    /// @param _token トークンアドレス
    /// @param _sender 送信者
    /// @param _recipient 受信者
    /// @param _amount 数量
    /// @param _agent エスクローエージェント
    /// @param _valid 有効状態
    function setEscrow(
        uint256 _escrowId,
        address _token,
        address _sender,
        address _recipient,
        uint256 _amount,
        address _agent,
        bool _valid
    )
        public
        onlyLatestVersion()
    {
        escrow[_escrowId].token = _token;
        escrow[_escrowId].sender = _sender;
        escrow[_escrowId].recipient = _recipient;
        escrow[_escrowId].amount = _amount;
        escrow[_escrowId].agent = _agent;
        escrow[_escrowId].valid = _valid;
    }

    /// @notice エスクロー情報の取得
    /// @param _escrowId エスクローID
    /// @return token トークンアドレス
    /// @return sender 送信者
    /// @return recipient 受信者
    /// @return amount 数量
    /// @return agent エスクローエージェント
    /// @return valid 有効状態
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
            bool valid
        )
    {
        return (
            escrow[_escrowId].token,
            escrow[_escrowId].sender,
            escrow[_escrowId].recipient,
            escrow[_escrowId].amount,
            escrow[_escrowId].agent,
            escrow[_escrowId].valid
        );
    }

    // -------------------------------------------------------------------
    // 移転承諾関連機能
    // -------------------------------------------------------------------

    /// 移転申請
    struct ApplicationForTransfer {
        address token; // トークンアドレス
        string applicationData; // 移転申請データ
        string approvalData; // 移転承認データ
        bool valid; // 申請有効状態
        bool escrowFinished; // エスクロー完了状態
        bool approved; // 移転承認状態
    }
    mapping(uint256 => ApplicationForTransfer) private applicationsForTransfer;

    /// @notice 移転申請情報更新
    /// @param _escrowId エスクローID
    /// @param _token トークンアドレス
    /// @param _applicationData 移転申請データ
    /// @param _approvalData 移転承認データ
    /// @param _valid 申請有効状態
    /// @param _escrowFinished エスクロー完了状態
    /// @param _approved 移転承認状態
    function setApplicationForTransfer(
        uint256 _escrowId,
        address _token,
        string memory _applicationData,
        string memory _approvalData,
        bool _valid,
        bool _escrowFinished,
        bool _approved
    )
        public
        onlyLatestVersion()
    {
        applicationsForTransfer[_escrowId].token = _token;
        applicationsForTransfer[_escrowId].applicationData = _applicationData;
        applicationsForTransfer[_escrowId].approvalData = _approvalData;
        applicationsForTransfer[_escrowId].valid = _valid;
        applicationsForTransfer[_escrowId].escrowFinished = _escrowFinished;
        applicationsForTransfer[_escrowId].approved = _approved;
    }

    /// @notice 移転申請情報参照
    /// @param _escrowId エスクローID
    /// @return token トークンアドレス
    /// @return applicationData 移転申請データ
    /// @return approvalData 移転承認データ
    /// @return valid 申請有効状態
    /// @return escrowFinished エスクロー完了状態
    /// @return approved 移転承認状態
    function getApplicationForTransfer(
        uint256 _escrowId
    )
        public
        view
        returns(
            address token,
            string memory applicationData,
            string memory approvalData,
            bool valid,
            bool escrowFinished,
            bool approved
        )
    {
        return (
            applicationsForTransfer[_escrowId].token,
            applicationsForTransfer[_escrowId].applicationData,
            applicationsForTransfer[_escrowId].approvalData,
            applicationsForTransfer[_escrowId].valid,
            applicationsForTransfer[_escrowId].escrowFinished,
            applicationsForTransfer[_escrowId].approved
        );
    }

}
