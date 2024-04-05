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
import "../utils/Errors.sol";

/// @title DVPコントラクトのステートを永続化するためのEternalStorage
/// @dev Storageのアクセスは認可したDVPコントラクトに限定する
contract DVPStorage is Ownable {
    constructor() {}

    // -------------------------------------------------------------------
    // 最新バージョンのDVPコントラクトアドレス：LatestVersion
    // -------------------------------------------------------------------

    /// 最新バージョンのDVPコントラクトアドレス
    address public latestVersion;

    /// @notice DVPコントラクトのバージョン更新
    /// @dev コントラクトオーナーのみ実行が可能
    /// @param _newVersion 新しいDVPコントラクトのアドレス
    function upgradeVersion(address _newVersion) public onlyOwner {
        latestVersion = _newVersion;
    }

    /// @dev 実行者が最新バージョンのDVPコントラクトアドレスであることをチェック
    modifier onlyLatestVersion() {
        require(
            msg.sender == latestVersion,
            ErrorCode.ERR_DVPStorage_onlyLatestVersion_250001
        );
        _;
    }

    // -------------------------------------------------------------------
    // 残高：Balance
    // -------------------------------------------------------------------

    /// 残高情報
    /// account => token => amount
    mapping(address => mapping(address => uint256)) private balances;

    /// @notice 残高の更新
    /// @dev 最新バージョンのDVPコントラクトのみ実行が可能
    /// @param _account アドレス
    /// @param _token トークンアドレス
    /// @param _value 更新後の残高数量
    /// @return 処理結果
    function setBalance(
        address _account,
        address _token,
        uint256 _value
    ) public onlyLatestVersion returns (bool) {
        balances[_account][_token] = _value;
        return true;
    }

    /// @notice 残高数量の参照
    /// @param _account アドレス
    /// @param _token トークンアドレス
    /// @return 残高数量
    function getBalance(
        address _account,
        address _token
    ) public view returns (uint256) {
        return balances[_account][_token];
    }

    // -------------------------------------------------------------------
    // 拘束数量：Commitment
    // -------------------------------------------------------------------

    /// 拘束数量
    /// account => token => amount
    mapping(address => mapping(address => uint256)) public commitments;

    /// @notice 拘束数量の更新
    /// @dev 最新バージョンのDVPコントラクトのみ実行が可能
    /// @param _account アドレス
    /// @param _token トークンアドレス
    /// @param _value 更新後の数量
    /// @return 処理結果
    function setCommitment(
        address _account,
        address _token,
        uint256 _value
    ) public onlyLatestVersion returns (bool) {
        commitments[_account][_token] = _value;
        return true;
    }

    /// @notice 拘束数量の参照
    /// @param _account アドレス
    /// @param _token トークンアドレス
    /// @return 拘束数量
    function getCommitment(
        address _account,
        address _token
    ) public view returns (uint256) {
        return commitments[_account][_token];
    }

    // -------------------------------------------------------------------
    // DVP情報：Delivery
    // -------------------------------------------------------------------

    struct Delivery {
        address token;
        address seller;
        address buyer;
        uint256 amount;
        address agent;
        bool confirmed; // Initially false
        bool valid; // Initially true
    }

    /// DVP情報
    /// deliveryId => Delivery
    mapping(uint256 => Delivery) private delivery;

    /// 直近決済ID
    uint256 private latestDeliveryId = 0;

    /// @notice 直近決済IDの更新
    /// @dev 最新バージョンのDVPコントラクトのみ実行が可能
    /// @param _latestDeliveryId 直近決済ID
    function setLatestDeliveryId(
        uint256 _latestDeliveryId
    ) public onlyLatestVersion {
        latestDeliveryId = _latestDeliveryId;
    }

    /// @notice 直近決済IDの参照
    /// @return 直近決済ID
    function getLatestDeliveryId() public view returns (uint256) {
        return latestDeliveryId;
    }

    /// @notice DVP情報の更新
    /// @param _deliveryId 決済ID
    /// @param _token トークンアドレス
    /// @param _seller 売り手
    /// @param _buyer 買い手
    /// @param _amount 数量
    /// @param _agent 決済エージェント
    /// @param _confirmed 確認状態
    /// @param _valid 有効状態
    function setDelivery(
        uint256 _deliveryId,
        address _token,
        address _seller,
        address _buyer,
        uint256 _amount,
        address _agent,
        bool _confirmed,
        bool _valid
    ) public onlyLatestVersion {
        delivery[_deliveryId].token = _token;
        delivery[_deliveryId].seller = _seller;
        delivery[_deliveryId].buyer = _buyer;
        delivery[_deliveryId].amount = _amount;
        delivery[_deliveryId].agent = _agent;
        delivery[_deliveryId].confirmed = _confirmed;
        delivery[_deliveryId].valid = _valid;
    }

    /// @notice DVP情報の取得
    /// @param _deliveryId 決済ID
    /// @return token トークンアドレス
    /// @return seller 売り手
    /// @return buyer 買い手
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
        return (
            delivery[_deliveryId].token,
            delivery[_deliveryId].seller,
            delivery[_deliveryId].buyer,
            delivery[_deliveryId].amount,
            delivery[_deliveryId].agent,
            delivery[_deliveryId].confirmed,
            delivery[_deliveryId].valid
        );
    }
}
