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

// @title Snap Messaging
contract SnapMessaging {
    event Message(
        address indexed sender,
        address indexed receiver,
        uint256 time,
        string text
    );

    // [CONSTRUCTOR]
    constructor() {}

    /// @notice Send message
    /// @param _to Message receiver address
    /// @param _text Message text
    function sendMessage(address _to, string memory _text) public {
        emit Message(msg.sender, _to, block.timestamp, _text);
    }
}
