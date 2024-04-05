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

import "../utils/Errors.sol";

/// @title Ownership Management Contract
contract Ownable {
    // オーナーアドレス
    address public owner;

    // イベント：オーナー変更
    event OwnershipTransferred(
        address indexed previousOwner,
        address indexed newOwner
    );

    // [CONSTRUCTOR]
    constructor() {
        owner = msg.sender;
    }

    /// @notice オーナー権限チェック
    modifier onlyOwner() {
        require(msg.sender == owner, ErrorCode.ERR_Ownable_onlyOwner_500001);
        _;
    }

    /// @notice オーナー変更
    /// @dev オーナーのみ実行可能
    /// @param newOwner 新しいオーナー
    function transferOwnership(address newOwner) public onlyOwner {
        require(
            newOwner != address(0),
            ErrorCode.ERR_Ownable_transferOwnership_500101
        );
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }
}
