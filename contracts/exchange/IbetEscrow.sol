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

import "OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/utils/math/SafeMath.sol";
import "./EscrowStorage.sol";
import "../access/Ownable.sol";
import "../utils/Errors.sol";
import "../../interfaces/IbetExchangeInterface.sol";
import "../../interfaces/IbetStandardTokenInterface.sol";


/// @title ibet Escrow
contract IbetEscrow is Ownable, IbetExchangeInterface {
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
        address agent
    );

    // ---------------------------------------------------------------
    // Constructor
    // ---------------------------------------------------------------
    address public storageAddress;

    // [CONSTRUCTOR]
    /// @param _storageAddress EscrowStorageコントラクトアドレス
    constructor(address _storageAddress)
    {
        storageAddress = _storageAddress;
    }

    // ---------------------------------------------------------------
    // Function: Storage
    // ---------------------------------------------------------------

    struct Escrow {
        address token;  // トークンアドレス
        address sender;  // 送信者
        address recipient;  // 受信者
        uint256 amount;  // 数量
        address agent;  // エスクローエージェント
        bool valid;  // 有効状態
    }

    /// @notice 直近エスクローID取得
    /// @return 直近エスクローID
    function latestEscrowId()
        public
        view
        returns (uint256)
    {
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
    function getEscrow(uint256 _escrowId)
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

    /// @notice 残高数量の参照
    /// @param _account アカウントアドレス
    /// @param _token トークンアドレス
    /// @return 残高数量
    function balanceOf(address _account, address _token)
        public
        view
        override
        returns (uint256)
    {
        return EscrowStorage(storageAddress).getBalance(
            _account,
            _token
        );
    }

    /// @notice エスクロー中数量の参照
    /// @param _account アカウントアドレス
    /// @param _token トークンアドレス
    /// @return 残高数量
    function commitmentOf(address _account, address _token)
        public
        view
        override
        returns (uint256)
    {
        return EscrowStorage(storageAddress).getCommitment(
            _account,
            _token
        );
    }

    // ---------------------------------------------------------------
    // Function: Logic
    // ---------------------------------------------------------------

    /// @notice エスクロー新規作成
    /// @param _token トークンアドレス
    /// @param _recipient トークン受領者
    /// @param _amount 数量
    /// @param _agent エスクローエージェント
    /// @param _data イベント出力用の任意のデータ
    function createEscrow(
        address _token,
        address _recipient,
        uint256 _amount,
        address _agent,
        string memory _data
    )
        public
        returns (bool)
    {
        // チェック：数量がゼロより大きいこと
        require(
            _amount > 0,
            ErrorCode.ERR_IbetEscrow_createEscrow_2301
        );

        // チェック：数量が残高以下であること
        require(
            balanceOf(msg.sender, _token) >= _amount,
            ErrorCode.ERR_IbetEscrow_createEscrow_2302
        );

        // チェック：トークンのステータスが有効であること
        require(
            IbetStandardTokenInterface(_token).status() == true,
            ErrorCode.ERR_IbetEscrow_createEscrow_2303
        );

        // 更新：エスクローIDをカウントアップ
        uint256 _escrowId = EscrowStorage(storageAddress).getLatestEscrowId() + 1;
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
    function cancelEscrow(uint256 _escrowId)
        public
        returns (bool)
    {
        // チェック：エスクローIDが直近ID以下であること
        require(
            _escrowId <= EscrowStorage(storageAddress).getLatestEscrowId(),
            ErrorCode.ERR_IbetEscrow_cancelEscrow_2311
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
            ErrorCode.ERR_IbetEscrow_cancelEscrow_2312
        );

        // チェック：msg.senderがエスクローのsender、またはagentであること
        require(
            msg.sender == escrow.sender || msg.sender == escrow.agent,
            ErrorCode.ERR_IbetEscrow_cancelEscrow_2313
        );

        // チェック：トークンのステータスが有効であること
        require(
            IbetStandardTokenInterface(escrow.token).status() == true,
            ErrorCode.ERR_IbetEscrow_cancelEscrow_2314
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

    /// @notice エスクロー完了
    /// @param _escrowId エスクローID
    function finishEscrow(uint256 _escrowId)
        public
        returns (bool)
    {
        // チェック：エスクローIDが直近ID以下であること
        require(
            _escrowId <= EscrowStorage(storageAddress).getLatestEscrowId(),
            ErrorCode.ERR_IbetEscrow_finishEscrow_2321
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
            ErrorCode.ERR_IbetEscrow_finishEscrow_2322
        );

        // チェック：msg.senderがエスクローのagentであること
        require(
            escrow.agent == msg.sender,
            ErrorCode.ERR_IbetEscrow_finishEscrow_2323
        );

        // チェック：トークンのステータスが有効であること
        require(
            IbetStandardTokenInterface(escrow.token).status() == true,
            ErrorCode.ERR_IbetEscrow_finishEscrow_2324
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
            escrow.agent
        );
        emit HolderChanged(
            escrow.token,
            escrow.sender,
            escrow.recipient,
            escrow.amount
        );

        return true;
    }

    /// @notice 全ての残高を引き出しする
    /// @dev エスクローで拘束されているものは引き出しされない
    /// @param _token トークンアドレス
    /// @return 処理結果
    function withdraw(address _token)
        public
        override
        returns (bool)
    {
        uint256 balance = balanceOf(msg.sender, _token);

        require(
            balance > 0,
            ErrorCode.ERR_IbetEscrow_withdraw_2331
        );

        // 更新処理：トークン引き出し（送信）
        IbetStandardTokenInterface(_token).transfer(msg.sender, balance);
        EscrowStorage(storageAddress).setBalance(msg.sender, _token, 0);

        // イベント登録
        emit Withdrawn(_token, msg.sender);

        return true;
    }

    /// @notice Deposit Handler：デポジット処理
    /// @param _from アカウントアドレス：残高を保有するアドレス
    /// @param _value デポジット数量
    function tokenFallback(address _from, uint _value, bytes memory /*_data*/)
        public
        override
    {
        EscrowStorage(storageAddress).setBalance(
            _from,
            msg.sender,
            balanceOf(_from, msg.sender).add(_value)
        );

        // イベント登録
        emit Deposited(msg.sender, _from);
    }

}
