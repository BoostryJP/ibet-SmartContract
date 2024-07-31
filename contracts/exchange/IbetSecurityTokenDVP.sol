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

import "OpenZeppelin/openzeppelin-contracts@4.9.3/contracts/utils/math/SafeMath.sol";
import "./DVPStorage.sol";
import "../access/Ownable.sol";
import "../utils/Errors.sol";
import "../../interfaces/IbetExchangeInterface.sol";
import "../../interfaces/IbetSecurityTokenInterface.sol";

/// @title ibet SecurityTokenDVP
contract IbetSecurityTokenDVP is Ownable, IbetExchangeInterface {
    using SafeMath for uint256;

    // ---------------------------------------------------------------
    // Event
    // ---------------------------------------------------------------

    // Event: DVP新規作成
    event DeliveryCreated(
        uint256 indexed deliveryId,
        address indexed token,
        address seller,
        address buyer,
        uint256 amount,
        address agent,
        string data
    );

    // Event: DVP取消
    event DeliveryCanceled(
        uint256 indexed deliveryId,
        address indexed token,
        address seller,
        address buyer,
        uint256 amount,
        address agent
    );

    // Event: DVP確認
    event DeliveryConfirmed(
        uint256 indexed deliveryId,
        address indexed token,
        address seller,
        address buyer,
        uint256 amount,
        address agent
    );

    // Event: DVP完了
    event DeliveryFinished(
        uint256 indexed deliveryId,
        address indexed token,
        address seller,
        address buyer,
        uint256 amount,
        address agent
    );

    // Event: DVP中断
    event DeliveryAborted(
        uint256 indexed deliveryId,
        address indexed token,
        address seller,
        address buyer,
        uint256 amount,
        address agent
    );

    // ---------------------------------------------------------------
    // Constructor
    // ---------------------------------------------------------------
    address public storageAddress;

    // [CONSTRUCTOR]
    /// @param _storageAddress DVPStorageコントラクトアドレス
    constructor(address _storageAddress) {
        storageAddress = _storageAddress;
    }

    // ---------------------------------------------------------------
    // Function: Storage
    // ---------------------------------------------------------------

    struct Delivery {
        address token;
        address seller;
        address buyer;
        uint256 amount;
        address agent;
        bool confirmed; // Initially false
        bool valid; // Initially true
    }

    /// @notice 直近決済ID取得
    /// @return 直近決済ID
    function latestDeliveryId() public view returns (uint256) {
        return DVPStorage(storageAddress).getLatestDeliveryId();
    }

    /// @notice DVP情報取得
    /// @param _deliveryId 決済ID
    /// @return token トークンアドレス
    /// @return seller 売り方
    /// @return buyer 買い方
    /// @return amount 数量
    /// @return agent 決済エージェント
    /// @return confirmed 確認状態
    /// @return valid 有効状態
    function getDelivery(
        uint256 _deliveryId
    )
        public
        view
        returns (
            address token,
            address seller,
            address buyer,
            uint256 amount,
            address agent,
            bool confirmed,
            bool valid
        )
    {
        return DVPStorage(storageAddress).getDelivery(_deliveryId);
    }

    /// @notice 残高数量の参照
    /// @param _account アカウントアドレス
    /// @param _token トークンアドレス
    /// @return 残高数量
    function balanceOf(
        address _account,
        address _token
    ) public view override returns (uint256) {
        return DVPStorage(storageAddress).getBalance(_account, _token);
    }

    /// @notice 拘束数量の参照
    /// @param _account アカウントアドレス
    /// @param _token トークンアドレス
    /// @return 残高数量
    function commitmentOf(
        address _account,
        address _token
    ) public view override returns (uint256) {
        return DVPStorage(storageAddress).getCommitment(_account, _token);
    }

    // ---------------------------------------------------------------
    // Function: Logic
    // ---------------------------------------------------------------

    /// @notice DVP決済新規作成
    /// @param _token トークンアドレス
    /// @param _buyer トークン受領者
    /// @param _amount 数量
    /// @param _agent 決済エージェント
    /// @param _data イベント出力用の任意のデータ
    function createDelivery(
        address _token,
        address _buyer,
        uint256 _amount,
        address _agent,
        string memory _data
    ) public returns (uint256) {
        // チェック：数量がゼロより大きいこと
        require(
            _amount > 0,
            ErrorCode.ERR_IbetSecurityTokenDVP_createDelivery_260001
        );

        // チェック：数量が残高以下であること
        require(
            balanceOf(msg.sender, _token) >= _amount,
            ErrorCode.ERR_IbetSecurityTokenDVP_createDelivery_260002
        );

        // チェック：トークンのステータスが有効であること
        require(
            IbetSecurityTokenInterface(_token).status() == true,
            ErrorCode.ERR_IbetSecurityTokenDVP_createDelivery_260003
        );

        // チェック：トークンの移転承諾要否フラグが無効であること
        require(
            IbetSecurityTokenInterface(_token).transferApprovalRequired() ==
                false,
            ErrorCode.ERR_IbetSecurityTokenDVP_createDelivery_260004
        );

        // 更新：決済IDをカウントアップ
        uint256 _deliveryId = DVPStorage(storageAddress).getLatestDeliveryId() +
            1;
        DVPStorage(storageAddress).setLatestDeliveryId(_deliveryId);

        // 更新：DVP決済情報の挿入
        DVPStorage(storageAddress).setDelivery(
            _deliveryId,
            _token,
            msg.sender,
            _buyer,
            _amount,
            _agent,
            false,
            true
        );

        // 更新：残高
        DVPStorage(storageAddress).setBalance(
            msg.sender,
            _token,
            balanceOf(msg.sender, _token).sub(_amount)
        );

        // 更新：決済中数量
        DVPStorage(storageAddress).setCommitment(
            msg.sender,
            _token,
            commitmentOf(msg.sender, _token).add(_amount)
        );

        // イベント登録
        emit DeliveryCreated(
            _deliveryId,
            _token,
            msg.sender,
            _buyer,
            _amount,
            _agent,
            _data
        );

        return _deliveryId;
    }

    /// @notice DVP決済取消
    /// @param _deliveryId 決済ID
    function cancelDelivery(uint256 _deliveryId) public returns (bool) {
        // チェック：決済IDが直近ID以下であること
        require(
            _deliveryId <= DVPStorage(storageAddress).getLatestDeliveryId(),
            ErrorCode.ERR_IbetSecurityTokenDVP_cancelDelivery_260101
        );

        Delivery memory delivery;
        (
            delivery.token,
            delivery.seller,
            delivery.buyer,
            delivery.amount,
            delivery.agent,
            delivery.confirmed,
            delivery.valid
        ) = DVPStorage(storageAddress).getDelivery(_deliveryId);

        // チェック：決済が有効であること
        require(
            delivery.valid == true,
            ErrorCode.ERR_IbetSecurityTokenDVP_cancelDelivery_260102
        );

        // チェック：決済が確認済ではないこと
        require(
            delivery.confirmed == false,
            ErrorCode.ERR_IbetSecurityTokenDVP_cancelDelivery_260103
        );

        // チェック：msg.senderがDVP決済のsender、またはbuyerであること
        require(
            msg.sender == delivery.seller || msg.sender == delivery.buyer,
            ErrorCode.ERR_IbetSecurityTokenDVP_cancelDelivery_260104
        );

        // 更新：残高
        DVPStorage(storageAddress).setBalance(
            delivery.seller,
            delivery.token,
            balanceOf(delivery.seller, delivery.token).add(delivery.amount)
        );

        // 更新：拘束数量
        DVPStorage(storageAddress).setCommitment(
            delivery.seller,
            delivery.token,
            commitmentOf(delivery.seller, delivery.token).sub(delivery.amount)
        );

        // 更新：DVP決済情報
        DVPStorage(storageAddress).setDelivery(
            _deliveryId,
            delivery.token,
            delivery.seller,
            delivery.buyer,
            delivery.amount,
            delivery.agent,
            delivery.confirmed,
            false
        );

        // イベント登録
        emit DeliveryCanceled(
            _deliveryId,
            delivery.token,
            delivery.seller,
            delivery.buyer,
            delivery.amount,
            delivery.agent
        );

        return true;
    }

    /// @notice DVP決済確認
    /// @param _deliveryId 決済ID
    function confirmDelivery(uint256 _deliveryId) public returns (bool) {
        // チェック：決済IDが直近ID以下であること
        require(
            _deliveryId <= DVPStorage(storageAddress).getLatestDeliveryId(),
            ErrorCode.ERR_IbetSecurityTokenDVP_confirmDelivery_260201
        );

        Delivery memory delivery;
        (
            delivery.token,
            delivery.seller,
            delivery.buyer,
            delivery.amount,
            delivery.agent,
            delivery.confirmed,
            delivery.valid
        ) = DVPStorage(storageAddress).getDelivery(_deliveryId);

        // チェック：決済が有効であること
        require(
            delivery.valid == true,
            ErrorCode.ERR_IbetSecurityTokenDVP_confirmDelivery_260202
        );

        // チェック：決済が確認済ではないこと
        require(
            delivery.confirmed == false,
            ErrorCode.ERR_IbetSecurityTokenDVP_confirmDelivery_260203
        );

        // チェック：msg.senderがbuyerであること
        require(
            msg.sender == delivery.buyer,
            ErrorCode.ERR_IbetSecurityTokenDVP_confirmDelivery_260204
        );

        // チェック：トークンのステータスが有効であること
        require(
            IbetSecurityTokenInterface(delivery.token).status() == true,
            ErrorCode.ERR_IbetSecurityTokenDVP_confirmDelivery_260205
        );

        // チェック：トークンの移転承諾要否フラグが無効であること
        require(
            IbetSecurityTokenInterface(delivery.token)
                .transferApprovalRequired() == false,
            ErrorCode.ERR_IbetSecurityTokenDVP_confirmDelivery_260206
        );

        // 更新：DVP決済情報
        DVPStorage(storageAddress).setDelivery(
            _deliveryId,
            delivery.token,
            delivery.seller,
            delivery.buyer,
            delivery.amount,
            delivery.agent,
            true,
            delivery.valid
        );

        // イベント登録
        emit DeliveryConfirmed(
            _deliveryId,
            delivery.token,
            delivery.seller,
            delivery.buyer,
            delivery.amount,
            delivery.agent
        );

        return true;
    }

    /// @notice DVP決済完了
    /// @param _deliveryId 決済ID
    function finishDelivery(uint256 _deliveryId) public returns (bool) {
        // チェック：決済IDが直近ID以下であること
        require(
            _deliveryId <= DVPStorage(storageAddress).getLatestDeliveryId(),
            ErrorCode.ERR_IbetSecurityTokenDVP_finishDelivery_260301
        );

        Delivery memory delivery;
        (
            delivery.token,
            delivery.seller,
            delivery.buyer,
            delivery.amount,
            delivery.agent,
            delivery.confirmed,
            delivery.valid
        ) = DVPStorage(storageAddress).getDelivery(_deliveryId);

        // チェック：決済が取消済みではないこと
        require(
            delivery.valid == true,
            ErrorCode.ERR_IbetSecurityTokenDVP_finishDelivery_260302
        );

        // チェック：決済が確認済みであること
        require(
            delivery.confirmed == true,
            ErrorCode.ERR_IbetSecurityTokenDVP_finishDelivery_260303
        );

        // チェック：msg.senderがDVP決済のagentであること
        require(
            delivery.agent == msg.sender,
            ErrorCode.ERR_IbetSecurityTokenDVP_finishDelivery_260304
        );

        // チェック：トークンのステータスが有効であること
        require(
            IbetSecurityTokenInterface(delivery.token).status() == true,
            ErrorCode.ERR_IbetSecurityTokenDVP_finishDelivery_260305
        );

        // チェック：トークンの移転承諾要否フラグが無効であること
        require(
            IbetSecurityTokenInterface(delivery.token)
                .transferApprovalRequired() == false,
            ErrorCode.ERR_IbetSecurityTokenDVP_finishDelivery_260306
        );

        // 更新：残高
        DVPStorage(storageAddress).setBalance(
            delivery.buyer,
            delivery.token,
            balanceOf(delivery.buyer, delivery.token).add(delivery.amount)
        );

        // 更新：決済中数量
        DVPStorage(storageAddress).setCommitment(
            delivery.seller,
            delivery.token,
            commitmentOf(delivery.seller, delivery.token).sub(delivery.amount)
        );

        // 更新：決済情報
        DVPStorage(storageAddress).setDelivery(
            _deliveryId,
            delivery.token,
            delivery.seller,
            delivery.buyer,
            delivery.amount,
            delivery.agent,
            delivery.confirmed,
            false
        );

        // イベント登録
        emit DeliveryFinished(
            _deliveryId,
            delivery.token,
            delivery.seller,
            delivery.buyer,
            delivery.amount,
            delivery.agent
        );
        emit HolderChanged(
            delivery.token,
            delivery.seller,
            delivery.buyer,
            delivery.amount
        );

        return true;
    }

    /// @notice DVP決済中止
    /// @param _deliveryId 決済ID
    function abortDelivery(uint256 _deliveryId) public returns (bool) {
        // チェック：決済IDが直近ID以下であること
        require(
            _deliveryId <= DVPStorage(storageAddress).getLatestDeliveryId(),
            ErrorCode.ERR_IbetSecurityTokenDVP_abortDelivery_260401
        );

        Delivery memory delivery;
        (
            delivery.token,
            delivery.seller,
            delivery.buyer,
            delivery.amount,
            delivery.agent,
            delivery.confirmed,
            delivery.valid
        ) = DVPStorage(storageAddress).getDelivery(_deliveryId);

        // チェック：決済が有効であること
        require(
            delivery.valid == true,
            ErrorCode.ERR_IbetSecurityTokenDVP_abortDelivery_260402
        );

        // チェック：決済が確認済であること
        require(
            delivery.confirmed == true,
            ErrorCode.ERR_IbetSecurityTokenDVP_abortDelivery_260403
        );

        // チェック：msg.senderがDVP決済のagentであること
        require(
            msg.sender == delivery.agent,
            ErrorCode.ERR_IbetSecurityTokenDVP_abortDelivery_260404
        );

        // 更新：残高
        DVPStorage(storageAddress).setBalance(
            delivery.seller,
            delivery.token,
            balanceOf(delivery.seller, delivery.token).add(delivery.amount)
        );

        // 更新：拘束数量
        DVPStorage(storageAddress).setCommitment(
            delivery.seller,
            delivery.token,
            commitmentOf(delivery.seller, delivery.token).sub(delivery.amount)
        );

        // 更新：DVP決済情報
        DVPStorage(storageAddress).setDelivery(
            _deliveryId,
            delivery.token,
            delivery.seller,
            delivery.buyer,
            delivery.amount,
            delivery.agent,
            delivery.confirmed,
            false
        );

        // イベント登録
        emit DeliveryAborted(
            _deliveryId,
            delivery.token,
            delivery.seller,
            delivery.buyer,
            delivery.amount,
            delivery.agent
        );

        return true;
    }

    /// @notice DVP決済一括完了
    /// @param _deliveryIdList 決済IDのリスト
    function bulkFinishDelivery(
        uint256[] calldata _deliveryIdList
    ) public returns (bool success) {
        for (uint i = 0; i < _deliveryIdList.length; i++) {
            success = finishDelivery(_deliveryIdList[i]);
        }
        return success;
    }

    /// @notice 部分的に残高を引き出しする
    /// @dev 決済で拘束されているものは引き出しされない
    /// @param _token トークンアドレス
    /// @param _value 引き出し数量
    /// @return 処理結果
    function withdrawPartial(
        address _token,
        uint _value
    ) public returns (bool) {
        uint256 balance = balanceOf(msg.sender, _token);

        require(
            balance >= _value,
            ErrorCode.ERR_IbetSecurityTokenDVP_withdrawPartial_260601
        );

        // 更新処理：トークン引き出し（送信）
        IbetSecurityTokenInterface(_token).transfer(msg.sender, _value);
        DVPStorage(storageAddress).setBalance(
            msg.sender,
            _token,
            balanceOf(msg.sender, _token).sub(_value)
        );

        // イベント登録
        emit Withdrawn(_token, msg.sender);

        return true;
    }

    /// @notice 全ての残高を引き出しする
    /// @dev 決済で拘束されているものは引き出しされない
    /// @param _token トークンアドレス
    /// @return 処理結果
    function withdraw(address _token) public override returns (bool) {
        uint256 balance = balanceOf(msg.sender, _token);

        require(
            balance > 0,
            ErrorCode.ERR_IbetSecurityTokenDVP_withdraw_260501
        );

        // 更新処理：トークン引き出し（送信）
        IbetSecurityTokenInterface(_token).transfer(msg.sender, balance);
        DVPStorage(storageAddress).setBalance(msg.sender, _token, 0);

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
        DVPStorage(storageAddress).setBalance(
            _from,
            msg.sender,
            balanceOf(_from, msg.sender).add(_value)
        );

        // イベント登録
        emit Deposited(msg.sender, _from);
    }
}
