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

/// @title E2E Test
contract E2ETest {

    // booleans
    bool public item1_bool; // set constructor
    bool public item2_bool; // set function 'setItem2'
    bool public item3_bool; // set function 'setItem3'

    // addresses
    address public item1_address; // set constructor
    address public item2_address; // set function 'setItem2'
    address public item3_address; // set function 'setItem3'

    // strings
    string public item1_string; // set constructor
    string public item2_string; // set function 'setItem2'
    string public item3_string; // set function 'setItem3'

    // unsigned integers(max type only)
    uint256 public item1_uint; // set constructor
    uint256 public item2_uint; // set function 'setItem2'
    uint256 public item3_uint; // set function 'setItem3'

    // signed integers(max type only)
    int256 public item1_int; // set constructor
    int256 public item2_int; // set function 'setItem2'
    int256 public item3_int; // set function 'setItem3'

    // bytes(max type only)
    bytes32 public item1_bytes; // set constructor
    bytes32 public item2_bytes; // set function 'setItem2'
    bytes32 public item3_bytes; // set function 'setItem3'

    uint256 public optional_item;

    // Update Item
    event SetItem(
        bool item_bool,
        address item_address,
        string item_string,
        uint256 item_uint,
        int256 item_int,
        bytes32 item_bytes
    );

    // [CONSTRUCTOR]
    /// @param _item1_bool    item1(bool)
    /// @param _item1_address item1(address)
    /// @param _item1_string  item1(string)
    /// @param _item1_uint    item1(uint256)
    /// @param _item1_int     item1(int256)
    /// @param _item1_bytes   item1(bytes32)
    constructor(
        bool _item1_bool,
        address _item1_address,
        string memory _item1_string,
        uint256 _item1_uint,
        int256 _item1_int,
        bytes32 _item1_bytes
    )
    {
        item1_bool = _item1_bool;
        item1_address = _item1_address;
        item1_string = _item1_string;
        item1_uint = _item1_uint;
        item1_int = _item1_int;
        item1_bytes = _item1_bytes;
    }

    /// @notice Update 'item2'
    /// @dev test write/read with same test
    /// @param _item2_bool    item2(bool)
    /// @param _item2_address item2(address)
    /// @param _item2_string  item2(string)
    /// @param _item2_uint    item2(uint256)
    /// @param _item2_int     item2(int256)
    /// @param _item2_bytes   item2(bytes32)
    /// @param err_flg occur error(1:assert,2:require,3:revert)
    function setItem2(
        bool          _item2_bool,
        address       _item2_address,
        string memory _item2_string,
        uint256       _item2_uint,
        int256        _item2_int,
        bytes32       _item2_bytes,
        uint8 err_flg
    )
        public
    {
        if (err_flg == 1)  {
            assert(false);
        } else if (err_flg == 2) {
            require(false, "not-required");
        } else if (err_flg == 3) {
            revert("reverted");
        }

        item2_bool = _item2_bool;
        item2_address = _item2_address;
        item2_string = _item2_string;
        item2_uint = _item2_uint;
        item2_int = _item2_int;
        item2_bytes = _item2_bytes;

        emit SetItem(
            item2_bool,
            item2_address,
            item2_string,
            item2_uint,
            item2_int,
            item2_bytes
        );
    }

    /// @notice Update 'item3'
    /// @dev test write/read with other test
    /// @param _item3_bool    item3(bool)
    /// @param _item3_address item3(address)
    /// @param _item3_string  item3(string)
    /// @param _item3_uint    item3(uint256)
    /// @param _item3_int     item3(int256)
    /// @param _item3_bytes   item3(bytes32)
    function setItem3(
        bool          _item3_bool,
        address       _item3_address,
        string memory _item3_string,
        uint256       _item3_uint,
        int256        _item3_int,
        bytes32       _item3_bytes
    )
        public
    {
        item3_bool = _item3_bool;
        item3_address = _item3_address;
        item3_string = _item3_string;
        item3_uint = _item3_uint;
        item3_int = _item3_int;
        item3_bytes = _item3_bytes;

        emit SetItem(
            item3_bool,
            item3_address,
            item3_string,
            item3_uint,
            item3_int,
            item3_bytes
        );
    }

    /// @notice Get uint256 items value
    /// @dev test view function call
    /// @return item1,item2 add value
    function getItemsValueSame()
        public
        view
        returns (uint256)
    {
        uint256 itemsValue = item1_uint + item2_uint;
        return itemsValue;
    }

    /// @notice Get uint256 items value
    /// @dev test view function call
    /// @return item1,item3 add value
    function getItemsValueOther()
        public
        view
        returns (uint256)
    {
        uint256 itemsValue = item1_uint + item3_uint;
        return itemsValue;
    }

    /// @notice Get optional item
    /// @param _optional_item optional item
    function setOptionalItem(
        uint256 _optional_item
    )
        public
    {
        optional_item = _optional_item;
    }
}