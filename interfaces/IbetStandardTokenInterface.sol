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

/// @title ibet Standard Token Interface
abstract contract IbetStandardTokenInterface {
    string public name; // 名称
    string public symbol; //略称
    uint256 public totalSupply; // 総発行量
    address public tradableExchange; // 取引可能Exchangeアドレス
    string public contactInformation; // 発行体の問い合わせ先情報
    string public privacyPolicy; // 発行体のプライバシーポリシー

    /// トークンの状態
    /// tradableExchangeとして指定したコントラクトにて、トークンの利用可否を制御する際に利用する
    /// True：有効、False：無効
    bool public status;

    /// @notice 取引コントラクトの更新
    /// @param _exchange 更新後の取引コントラクト
    function setTradableExchange(address _exchange) public virtual;

    /// @notice 問い合わせ先情報の更新
    /// @param _contactInformation 更新後の問い合わせ先情報
    function setContactInformation(
        string memory _contactInformation
    ) public virtual;

    /// @notice プライバシーポリシーの更新
    /// @param _privacyPolicy 更新後のプライバシーポリシー
    function setPrivacyPolicy(string memory _privacyPolicy) public virtual;

    /// @notice 取扱ステータスの更新
    /// @param _status 更新後の取扱ステータス
    function setStatus(bool _status) public virtual;

    /// Event: 取扱ステータス変更
    event ChangeStatus(bool indexed status);

    /**
     * 残高関連機能
     */

    /// 残高数量
    /// account_address => balance
    mapping(address => uint256) public balances;

    /// @notice 残高の参照
    /// @param _owner 保有者のアドレス
    /// @return 残高数量
    function balanceOf(address _owner) public view virtual returns (uint256);

    /**
     * 移転関連機能
     */

    /// @notice 移転
    /// @dev 発行体のみ実行可能
    /// @param _to 宛先アドレス
    /// @param _value 移転数量
    /// @return success 処理結果
    function transfer(
        address _to,
        uint _value
    ) public virtual returns (bool success);

    /// @notice 強制移転
    /// @param _from 移転元アドレス
    /// @param _to 移転先アドレス
    /// @param _value 移転数量
    /// @return success 処理結果
    function transferFrom(
        address _from,
        address _to,
        uint256 _value
    ) public virtual returns (bool success);

    /// @notice 移転（一括）
    /// @param _toList 宛先アドレスのリスト
    /// @param _valueList 移転数量のリスト
    /// @return success 処理結果
    function bulkTransfer(
        address[] calldata _toList,
        uint[] calldata _valueList
    ) public virtual returns (bool success);

    /// @notice 強制移転（一括）
    /// @param _fromList 移転元アドレスのリスト
    /// @param _toList 移転先アドレスのリスト
    /// @param _valueList 移転数量のリスト
    /// @return success 処理結果
    function bulkTransferFrom(
        address[] calldata _fromList,
        address[] calldata _toList,
        uint256[] calldata _valueList
    ) public virtual returns (bool success);

    /// Event: 移転
    event Transfer(address indexed from, address indexed to, uint256 value);
}
