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
pragma solidity ^0.8.23;

import "OpenZeppelin/openzeppelin-contracts@4.9.3/contracts/utils/math/SafeMath.sol";
import "./EscrowStorage.sol";
import "../access/Ownable.sol";
import "../utils/Errors.sol";
import "../../interfaces/IbetExchangeInterface.sol";
import "../../interfaces/IbetSecurityTokenInterface.sol";

/// @title ibet Security Token Escrow
contract IbetSecurityTokenEscrow is Ownable, IbetExchangeInterface {
    using SafeMath for uint256;

    // ---------------------------------------------------------------
    // Event
    // ---------------------------------------------------------------

    // Event: エスクロー新規作成
    event EscrowCreated(
        uint256 indexed escrowId,
        address indexed token,
        address sender,
        address recipient,
        uint256 amount,
        address agent,
        string data
    );

    // Event: エスクロー取消
    event EscrowCanceled(
        uint256 indexed escrowId,
        address indexed token,
        address sender,
        address recipient,
        uint256 amount,
        address agent
    );

    // Event: エスクロー完了
    event EscrowFinished(
        uint256 indexed escrowId,
        address indexed token,
        address sender,
        address recipient,
        uint256 amount,
        address agent,
        bool indexed transferApprovalRequired
    );

    /// Event: 移転申請
    event ApplyForTransfer(
        uint256 indexed escrowId,
        address indexed token,
        address from,
        address to,
        uint256 value,
        string data
    );

    /// Event: 移転申請取消
    event CancelTransfer(
        uint256 indexed escrowId,
        address indexed token,
        address from,
        address to
    );

    /// Event: 移転承認
    event ApproveTransfer(
        uint256 indexed escrowId,
        address indexed token,
        string data
    );

    // ---------------------------------------------------------------
    // Constructor
    // ---------------------------------------------------------------
    address public storageAddress;

    // [CONSTRUCTOR]
    /// @param _storageAddress EscrowStorageコントラクトアドレス
    constructor(address _storageAddress) {
        storageAddress = _storageAddress;
    }

    // ---------------------------------------------------------------
    // Function: Storage
    // ---------------------------------------------------------------

    struct Escrow {
        address token; // トークンアドレス
        address sender; // 送信者
        address recipient; // 受信者
        uint256 amount; // 数量
        address agent; // エスクローエージェント
        bool valid; // 有効状態
    }

    struct ApplicationForTransfer {
        address token; // トークンアドレス
        string applicationData; // 移転申請データ
        string approvalData; // 移転承認データ
        bool valid; // 申請有効状態
        bool escrowFinished; // エスクロー完了状態
        bool approved; // 移転承認状態
    }

    /// @notice 直近エスクローID取得
    /// @return 直近エスクローID
    function latestEscrowId() public view returns (uint256) {
        return EscrowStorage(storageAddress).getLatestEscrowId();
    }

    /// @notice エスクロー情報取得
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
        returns (
            address token,
            address sender,
            address recipient,
            uint256 amount,
            address agent,
            bool valid
        )
    {
        return EscrowStorage(storageAddress).getEscrow(_escrowId);
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
        returns (
            address token,
            string memory applicationData,
            string memory approvalData,
            bool valid,
            bool escrowFinished,
            bool approved
        )
    {
        return
            EscrowStorage(storageAddress).getApplicationForTransfer(_escrowId);
    }

    /// @notice 残高数量の参照
    /// @param _account アカウントアドレス
    /// @param _token トークンアドレス
    /// @return 残高数量
    function balanceOf(
        address _account,
        address _token
    ) public view override returns (uint256) {
        return EscrowStorage(storageAddress).getBalance(_account, _token);
    }

    /// @notice エスクロー中数量の参照
    /// @param _account アカウントアドレス
    /// @param _token トークンアドレス
    /// @return 残高数量
    function commitmentOf(
        address _account,
        address _token
    ) public view override returns (uint256) {
        return EscrowStorage(storageAddress).getCommitment(_account, _token);
    }

    // ---------------------------------------------------------------
    // Function: Logic
    // ---------------------------------------------------------------

    /// @notice エスクロー新規作成
    /// @param _token トークンアドレス
    /// @param _recipient トークン受領者
    /// @param _amount 数量
    /// @param _agent エスクローエージェント
    /// @param _transferApplicationData 移転申請データ
    /// @param _data イベント出力用の任意データ
    function createEscrow(
        address _token,
        address _recipient,
        uint256 _amount,
        address _agent,
        string memory _transferApplicationData,
        string memory _data
    ) public returns (bool) {
        // チェック：数量がゼロより大きいこと
        require(
            _amount > 0,
            ErrorCode.ERR_IbetSecurityTokenEscrow_createEscrow_240001
        );

        // チェック：数量が残高以下であること
        require(
            EscrowStorage(storageAddress).getBalance(msg.sender, _token) >=
                _amount,
            ErrorCode.ERR_IbetSecurityTokenEscrow_createEscrow_240002
        );

        // チェック：トークンのステータスが有効であること
        require(
            IbetSecurityTokenInterface(_token).status() == true,
            ErrorCode.ERR_IbetSecurityTokenEscrow_createEscrow_240003
        );

        // 更新：エスクローIDをカウントアップ
        uint256 _escrowId = EscrowStorage(storageAddress).getLatestEscrowId() +
            1;
        EscrowStorage(storageAddress).setLatestEscrowId(_escrowId);

        // 更新：エスクロー情報の挿入
        EscrowStorage(storageAddress).setEscrow(
            _escrowId,
            _token,
            msg.sender,
            _recipient,
            _amount,
            _agent,
            true
        );

        // 更新：残高
        EscrowStorage(storageAddress).setBalance(
            msg.sender,
            _token,
            balanceOf(msg.sender, _token).sub(_amount)
        );

        // 更新：エスクロー中数量
        EscrowStorage(storageAddress).setCommitment(
            msg.sender,
            _token,
            commitmentOf(msg.sender, _token).add(_amount)
        );

        // 更新：移転申請（移転承諾要トークン）
        if (
            IbetSecurityTokenInterface(_token).transferApprovalRequired() ==
            true
        ) {
            EscrowStorage(storageAddress).setApplicationForTransfer(
                _escrowId,
                _token,
                _transferApplicationData,
                "",
                true,
                false,
                false
            );
            // イベント登録
            emit ApplyForTransfer(
                _escrowId,
                _token,
                msg.sender,
                _recipient,
                _amount,
                _transferApplicationData
            );
        }

        // イベント登録
        emit EscrowCreated(
            _escrowId,
            _token,
            msg.sender,
            _recipient,
            _amount,
            _agent,
            _data
        );

        return true;
    }

    /// @notice エスクロー取消
    /// @param _escrowId エスクローID
    function cancelEscrow(uint256 _escrowId) public returns (bool) {
        // チェック：エスクローIDが直近ID以下であること
        require(
            _escrowId <= EscrowStorage(storageAddress).getLatestEscrowId(),
            ErrorCode.ERR_IbetSecurityTokenEscrow_cancelEscrow_240101
        );

        Escrow memory escrow;
        (
            escrow.token,
            escrow.sender,
            escrow.recipient,
            escrow.amount,
            escrow.agent,
            escrow.valid
        ) = EscrowStorage(storageAddress).getEscrow(_escrowId);

        // チェック：エスクローが有効であること
        require(
            escrow.valid == true,
            ErrorCode.ERR_IbetSecurityTokenEscrow_cancelEscrow_240102
        );

        // チェック：msg.senderがエスクローのsender、またはagentであること
        require(
            msg.sender == escrow.sender || msg.sender == escrow.agent,
            ErrorCode.ERR_IbetSecurityTokenEscrow_cancelEscrow_240103
        );

        // チェック：トークンのステータスが有効であること
        require(
            IbetSecurityTokenInterface(escrow.token).status() == true,
            ErrorCode.ERR_IbetSecurityTokenEscrow_cancelEscrow_240104
        );

        // 更新：残高
        EscrowStorage(storageAddress).setBalance(
            escrow.sender,
            escrow.token,
            balanceOf(escrow.sender, escrow.token).add(escrow.amount)
        );

        // 更新：エスクロー中数量
        EscrowStorage(storageAddress).setCommitment(
            escrow.sender,
            escrow.token,
            commitmentOf(escrow.sender, escrow.token).sub(escrow.amount)
        );

        // 更新：エスクロー情報
        EscrowStorage(storageAddress).setEscrow(
            _escrowId,
            escrow.token,
            escrow.sender,
            escrow.recipient,
            escrow.amount,
            escrow.agent,
            false
        );

        // 更新：移転申請（移転承諾要トークン）
        if (
            IbetSecurityTokenInterface(escrow.token)
                .transferApprovalRequired() == true
        ) {
            ApplicationForTransfer memory application;
            (
                application.token,
                application.applicationData,
                application.approvalData,
                application.valid,
                application.escrowFinished,
                application.approved
            ) = EscrowStorage(storageAddress).getApplicationForTransfer(
                _escrowId
            );

            if (application.token != address(0)) {
                EscrowStorage(storageAddress).setApplicationForTransfer(
                    _escrowId,
                    application.token,
                    application.applicationData,
                    application.approvalData,
                    false,
                    application.escrowFinished,
                    application.approved
                );
                // イベント登録
                emit CancelTransfer(
                    _escrowId,
                    escrow.token,
                    escrow.sender,
                    escrow.recipient
                );
            }
        }

        // イベント登録
        emit EscrowCanceled(
            _escrowId,
            escrow.token,
            escrow.sender,
            escrow.recipient,
            escrow.amount,
            escrow.agent
        );

        return true;
    }

    /// @notice 移転承認
    /// @dev 移転対象のトークンのオーナーのみ実行可能
    /// @param _escrowId エスクローID
    /// @param _transferApprovalData 移転承認データ
    function approveTransfer(
        uint256 _escrowId,
        string memory _transferApprovalData
    ) public returns (bool) {
        ApplicationForTransfer memory application;
        (
            application.token,
            application.applicationData,
            application.approvalData,
            application.valid,
            application.escrowFinished,
            application.approved
        ) = EscrowStorage(storageAddress).getApplicationForTransfer(_escrowId);

        Escrow memory escrow;
        (
            escrow.token,
            escrow.sender,
            escrow.recipient,
            escrow.amount,
            escrow.agent,
            escrow.valid
        ) = EscrowStorage(storageAddress).getEscrow(_escrowId);

        // チェック：移転申請が存在すること
        require(
            application.token != address(0),
            ErrorCode.ERR_IbetSecurityTokenEscrow_approveTransfer_240201
        );

        // チェック：承認者がトークンのオーナーであること
        require(
            msg.sender == Ownable(application.token).owner(),
            ErrorCode.ERR_IbetSecurityTokenEscrow_approveTransfer_240202
        );

        // チェック：移転申請が有効状態であること
        require(
            application.valid == true,
            ErrorCode.ERR_IbetSecurityTokenEscrow_approveTransfer_240203
        );

        // チェック：移転申請のエスクロー状態が完了状態であること
        require(
            application.escrowFinished == true,
            ErrorCode.ERR_IbetSecurityTokenEscrow_approveTransfer_240204
        );

        // チェック：トークンのステータスが有効であること
        require(
            IbetSecurityTokenInterface(escrow.token).status() == true,
            ErrorCode.ERR_IbetSecurityTokenEscrow_approveTransfer_240205
        );

        // 更新：移転承諾
        EscrowStorage(storageAddress).setApplicationForTransfer(
            _escrowId,
            application.token,
            application.applicationData,
            _transferApprovalData,
            application.valid,
            application.escrowFinished,
            true
        );

        // 更新：残高
        EscrowStorage(storageAddress).setBalance(
            escrow.recipient,
            escrow.token,
            balanceOf(escrow.recipient, escrow.token).add(escrow.amount)
        );

        // 更新：エスクロー中数量
        EscrowStorage(storageAddress).setCommitment(
            escrow.sender,
            escrow.token,
            commitmentOf(escrow.sender, escrow.token).sub(escrow.amount)
        );

        // イベント登録
        emit ApproveTransfer(
            _escrowId,
            application.token,
            _transferApprovalData
        );

        emit HolderChanged(
            escrow.token,
            escrow.sender,
            escrow.recipient,
            escrow.amount
        );

        return true;
    }

    /// @notice エスクロー完了
    /// @param _escrowId エスクローID
    function finishEscrow(uint256 _escrowId) public returns (bool) {
        // チェック：エスクローIDが直近ID以下であること
        require(
            _escrowId <= EscrowStorage(storageAddress).getLatestEscrowId(),
            ErrorCode.ERR_IbetSecurityTokenEscrow_finishEscrow_240301
        );

        Escrow memory escrow;
        (
            escrow.token,
            escrow.sender,
            escrow.recipient,
            escrow.amount,
            escrow.agent,
            escrow.valid
        ) = EscrowStorage(storageAddress).getEscrow(_escrowId);

        // チェック：エスクローが取消済みではないこと
        require(
            escrow.valid == true,
            ErrorCode.ERR_IbetSecurityTokenEscrow_finishEscrow_240302
        );

        // チェック：msg.senderがエスクローのagentであること
        require(
            escrow.agent == msg.sender,
            ErrorCode.ERR_IbetSecurityTokenEscrow_finishEscrow_240303
        );

        // チェック：トークンのステータスが有効であること
        require(
            IbetSecurityTokenInterface(escrow.token).status() == true,
            ErrorCode.ERR_IbetSecurityTokenEscrow_finishEscrow_240304
        );

        if (
            IbetSecurityTokenInterface(escrow.token)
                .transferApprovalRequired() == true
        ) {
            // 更新：移転承諾
            ApplicationForTransfer memory application;
            (
                application.token,
                application.applicationData,
                application.approvalData,
                application.valid,
                application.escrowFinished,
                application.approved
            ) = EscrowStorage(storageAddress).getApplicationForTransfer(
                _escrowId
            );

            EscrowStorage(storageAddress).setApplicationForTransfer(
                _escrowId,
                application.token,
                application.applicationData,
                application.approvalData,
                application.valid,
                true,
                application.approved
            );

            // 更新：エスクロー情報
            EscrowStorage(storageAddress).setEscrow(
                _escrowId,
                escrow.token,
                escrow.sender,
                escrow.recipient,
                escrow.amount,
                escrow.agent,
                false
            );

            // イベント登録
            emit EscrowFinished(
                _escrowId,
                escrow.token,
                escrow.sender,
                escrow.recipient,
                escrow.amount,
                escrow.agent,
                true
            );
        } else {
            // 更新：残高
            EscrowStorage(storageAddress).setBalance(
                escrow.recipient,
                escrow.token,
                balanceOf(escrow.recipient, escrow.token).add(escrow.amount)
            );

            // 更新：エスクロー中数量
            EscrowStorage(storageAddress).setCommitment(
                escrow.sender,
                escrow.token,
                commitmentOf(escrow.sender, escrow.token).sub(escrow.amount)
            );

            // 更新：エスクロー情報
            EscrowStorage(storageAddress).setEscrow(
                _escrowId,
                escrow.token,
                escrow.sender,
                escrow.recipient,
                escrow.amount,
                escrow.agent,
                false
            );

            // イベント登録
            emit EscrowFinished(
                _escrowId,
                escrow.token,
                escrow.sender,
                escrow.recipient,
                escrow.amount,
                escrow.agent,
                false
            );

            emit HolderChanged(
                escrow.token,
                escrow.sender,
                escrow.recipient,
                escrow.amount
            );
        }

        return true;
    }

    /// @notice エスクロー一括完了
    /// @param _escrowIdList エスクローIDのリスト
    function bulkFinishEscrow(
        uint256[] calldata _escrowIdList
    ) public returns (bool success) {
        for (uint i = 0; i < _escrowIdList.length; i++) {
            success = finishEscrow(_escrowIdList[i]);
        }
        return success;
    }

    /// @notice 全ての残高を引き出しする
    /// @dev エスクローで拘束されているものは引き出しされない
    /// @param _token トークンアドレス
    /// @return 処理結果
    function withdraw(address _token) public override returns (bool) {
        uint256 balance = balanceOf(msg.sender, _token);

        require(
            balance > 0,
            ErrorCode.ERR_IbetSecurityTokenEscrow_withdraw_240401
        );

        // 更新処理：トークン引き出し（送信）
        IbetSecurityTokenInterface(_token).transfer(msg.sender, balance);
        EscrowStorage(storageAddress).setBalance(msg.sender, _token, 0);

        // イベント登録
        emit Withdrawn(_token, msg.sender);

        return true;
    }

    /// @notice Deposit Handler：デポジット処理
    /// @param _from アカウントアドレス：残高を保有するアドレス
    /// @param _value デポジット数量
    function tokenFallback(
        address _from,
        uint _value,
        bytes memory /*_data*/
    ) public override {
        EscrowStorage(storageAddress).setBalance(
            _from,
            msg.sender,
            balanceOf(_from, msg.sender).add(_value)
        );

        // イベント登録
        emit Deposited(msg.sender, _from);
    }
}
