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


// @title E2E Messaging
contract E2EMessaging {

    event Message(address indexed sender, address indexed receiver, uint256 time, string text);
    event PublicKeyUpdated(address indexed who, string key, string key_type);

    struct message {
        address from;  // Message sender
        string  text;  // Message text
        uint256 time;  // Timestamp of the message in UNIX seconds
    }

    struct public_key_struct {
        string key;  // Public key
        string key_type;  // Key type
    }

    mapping (address => uint256) public last_msg_index;
    mapping (address => mapping (uint256 => message)) public messages;
    mapping (address => public_key_struct) public keys;

    // [CONSTRUCTOR]
    constructor () {}

    /// @notice Send message
    /// @param _to Message receiver address
    /// @param _text Message text
    function sendMessage(address _to, string memory _text)
        public
    {
        messages[_to][last_msg_index[_to]].from = msg.sender;
        messages[_to][last_msg_index[_to]].text = _text;
        messages[_to][last_msg_index[_to]].time = block.timestamp;
        last_msg_index[_to]++;
        emit Message(msg.sender, _to, block.timestamp, _text);
    }

    /// @notice Get last index
    /// @param _owner Message sender address
    /// @return _index Last index
    function lastIndex(address _owner)
        public
        view
        returns (uint256 _index)
    {
        return last_msg_index[_owner];
    }

    /// @notice Get last message
    /// @param _who Message receiver address
    /// @return _from Message sender address
    /// @return _text Message text
    /// @return _time Message block timestamp
    function getLastMessage(address _who)
        public
        view
        returns (
            address _from,
            string memory _text,
            uint256 _time
        )
    {
        require(last_msg_index[_who] > 0);
        return (
            messages[_who][last_msg_index[_who] - 1].from,
            messages[_who][last_msg_index[_who] - 1].text,
            messages[_who][last_msg_index[_who] - 1].time
        );
    }

    /// @notice Get message by index
    /// @param _who Message receiver address
    /// @param _index Message index
    /// @return _from Message sender address
    /// @return _text Message text
    /// @return _time Message block timestamp
    function getMessageByIndex(address _who, uint256 _index)
        public
        view
        returns (
            address _from,
            string memory _text,
            uint256 _time
        )
    {
        return (
            messages[_who][_index].from,
            messages[_who][_index].text,
            messages[_who][_index].time
        );
    }

    /// @notice Get public key
    /// @param _who Message receiver address
    /// @return _key Public key
    /// @return _type Key type
    function getPublicKey(address _who)
        public
        view
        returns (
            string memory _key,
            string memory _type
        )
    {
        return (
            keys[_who].key,
            keys[_who].key_type
        );
    }

    /// @notice Set public key
    /// @param _key Public key
    /// @param _type Key type
    function setPublicKey(string memory _key, string memory _type)
        public
    {
        keys[msg.sender].key = _key;
        keys[msg.sender].key_type = _type;
        emit PublicKeyUpdated(msg.sender, _key, _type);
    }
}