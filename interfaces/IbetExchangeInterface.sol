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

import "./ContractReceiver.sol";

/// @title ibet Exchange Interface
abstract contract IbetExchangeInterface is ContractReceiver {
    // Event: 入庫
    event Deposited(address indexed token, address indexed account);

    // Event: 出庫
    event Withdrawn(address indexed token, address indexed account);

    // Event: 保有者変更
    event HolderChanged(
        address indexed token,
        address indexed from,
        address indexed to,
        uint256 value
    );

    /// @notice 残高数量の参照
    /// @param _account アカウントアドレス
    /// @param _token トークンアドレス
    /// @return 残高数量
    function balanceOf(
        address _account,
        address _token
    ) public view virtual returns (uint256);

    /// @notice 拘束数量の参照
    /// @param _account アカウントアドレス
    /// @param _token トークンアドレス
    /// @return 拘束数量
    function commitmentOf(
        address _account,
        address _token
    ) public view virtual returns (uint256);

    /// @notice 出庫
    /// @dev エスクローで拘束されているものは引き出しされない
    /// @param _token トークンアドレス
    /// @return 処理結果
    function withdraw(address _token) public virtual returns (bool);

    /// @notice 入庫
    /// @param _from アカウントアドレス：残高を保有するアドレス
    /// @param _value デポジット数量
    /// @param _data 任意のデータ
    function tokenFallback(
        address _from,
        uint _value,
        bytes memory _data
    ) public virtual override;
}
