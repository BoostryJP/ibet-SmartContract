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

/// @title Personal Information Registry
contract PersonalInfo {
    // 個人情報
    struct Info {
        address account_address; // アカウントアドレス
        address link_address; // 情報を公開する先のアドレス
        string encrypted_info; // 暗号化済個人情報
    }

    // 個人情報
    // account_address => link_address => info
    mapping(address => mapping(address => Info)) public personal_info;

    // イベント：登録
    event Register(
        address indexed account_address,
        address indexed link_address
    );

    // イベント：修正
    event Modify(address indexed account_address, address indexed link_address);

    // [CONSTRUCTOR]
    constructor() {}

    /// @notice 個人情報登録
    /// @param _link_address 通知先アドレス
    /// @param _encrypted_info 暗号化済個人情報
    /// @return 処理結果
    function register(
        address _link_address,
        string memory _encrypted_info
    ) public returns (bool) {
        Info storage info = personal_info[msg.sender][_link_address];

        info.account_address = msg.sender;
        info.link_address = _link_address;
        info.encrypted_info = _encrypted_info;

        emit Register(msg.sender, _link_address);

        return true;
    }

    /// @notice 個人情報修正
    /// @dev 個人情報通知先アカウントによる修正。通知元アカウントによる修正はregister()を使う。
    /// @param _account_address 個人情報通知元アカウントアドレス
    /// @param _encrypted_info 暗号化済個人情報
    /// @return 処理結果
    function modify(
        address _account_address,
        string memory _encrypted_info
    ) public returns (bool) {
        Info storage info = personal_info[_account_address][msg.sender];

        // 登録済みか確認
        require(
            info.account_address == _account_address,
            ErrorCode.ERR_PersonalInfo_modify_400001
        );
        require(
            info.link_address == msg.sender,
            ErrorCode.ERR_PersonalInfo_modify_400002
        );

        info.encrypted_info = _encrypted_info;

        emit Modify(_account_address, msg.sender);
        return true;
    }

    /// @notice 個人情報登録（強制登録）
    /// @param _account_address アカウントアドレス
    /// @param _encrypted_info 暗号化済個人情報
    /// @return 処理結果
    function forceRegister(
        address _account_address,
        string memory _encrypted_info
    ) public returns (bool) {
        Info storage info = personal_info[_account_address][msg.sender];

        info.account_address = _account_address;
        info.link_address = msg.sender;
        info.encrypted_info = _encrypted_info;

        emit Register(_account_address, msg.sender);
        return true;
    }

    /// @notice 登録状況の確認
    /// @param _account_address アカウントアドレス
    /// @param _link_address 通知先アドレス
    /// @return 登録状況
    function isRegistered(
        address _account_address,
        address _link_address
    ) public view returns (bool) {
        Info storage info = personal_info[_account_address][_link_address];
        if (info.account_address == address(0)) {
            return false;
        } else {
            return true;
        }
    }
}
