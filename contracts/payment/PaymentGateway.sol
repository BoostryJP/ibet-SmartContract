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


/// @title DvP Agent Contract
contract PaymentGateway is Ownable {

    // 支払用口座情報
    struct PaymentAccount {
        address account_address; // アカウントアドレス
        address agent_address; // 収納代行業者（Agent）のアドレス
        string encrypted_info; // 銀行口座情報（暗号化済）
        uint8 approval_status; // 認可状況（NONE(0)/NG(1)/OK(2)/WARN(3)/BAN(4)）
    }

    // 収納代行業者（Agent）
    // agent_address => 登録状況
    mapping(address => bool) public agents;

    // 支払用口座情報
    // account_address => agent_address => PaymentAccount
    mapping(address => mapping(address => PaymentAccount)) public payment_accounts;

    // イベント：収納代行業者追加
    event AddAgent(address indexed agent_address);

    // イベント：収納代行業者削除
    event RemoveAgent(address indexed agent_address);

    // イベント：登録
    event Register(address indexed account_address, address indexed agent_address);

    // イベント：承認
    event Approve(address indexed account_address, address indexed agent_address);

    // イベント：警告
    event Warn(address indexed account_address, address indexed agent_address);

    // イベント：非承認
    event Disapprove(address indexed account_address, address indexed agent_address);

    // イベント：アカウント停止（BAN）
    event Ban(address indexed account_address, address indexed agent_address);

    // イベント：修正
    event Modify(address indexed account_address, address indexed agent_address);

    // [CONSTRUCTOR]
    constructor() {}

    /// @notice 収納代行業者の追加
    /// @dev オーナーのみ実行可能
    /// @param _agent_address 収納代行業者のアドレス
    function addAgent(address _agent_address)
        public
        onlyOwner()
    {
        agents[_agent_address] = true;
        emit AddAgent(_agent_address);
    }

    /// @notice 収納代行業者の削除
    /// @dev オーナーのみ実行可能
    /// @param _agent_address 収納代行業者のアドレス
    function removeAgent(address _agent_address)
        public
        onlyOwner()
    {
        agents[_agent_address] = false;
        emit RemoveAgent(_agent_address);
    }

    /// @notice 収納代行業者の登録状態
    /// @param _agent_address 収納代行業者のアドレス
    /// @return 登録状態
    function getAgent(address _agent_address)
        public
        view
        returns (bool)
    {
        return agents[_agent_address];
    }

    /// @notice 支払用口座情報の登録
    /// @dev ２回目以降は上書き登録を行う
    /// @param _agent_address 収納代行業者のアドレス
    /// @param _encrypted_info 銀行口座情報（暗号化済）
    /// @return 処理結果
    function register(address _agent_address, string memory _encrypted_info)
        public
        returns (bool)
    {
        PaymentAccount storage payment_account = payment_accounts[msg.sender][_agent_address];
        require(payment_account.approval_status != 4, ErrorCode.ERR_PaymentGateway_register_3001);

        // 口座情報の登録
        payment_account.account_address = msg.sender;
        payment_account.agent_address = _agent_address;
        payment_account.encrypted_info = _encrypted_info;
        payment_account.approval_status = 1;

        emit Register(msg.sender, _agent_address);
        return true;
    }

    /// @notice 支払用口座情報の承認
    /// @param _account_address アカウントアドレス
    /// @return 処理結果
    function approve(address _account_address)
        public
        returns (bool)
    {
        PaymentAccount storage payment_account = payment_accounts[_account_address][msg.sender];
        require(payment_account.account_address != address(0), ErrorCode.ERR_PaymentGateway_approve_3011);

        payment_account.approval_status = 2;

        emit Approve(_account_address, msg.sender);
        return true;
    }

    /// @notice 支払用口座情報を警告状態にする
    /// @param _account_address アカウントアドレス
    /// @return 処理結果
    function warn(address _account_address)
        public
        returns (bool)
    {
        PaymentAccount storage payment_account = payment_accounts[_account_address][msg.sender];
        require(payment_account.account_address != address(0), ErrorCode.ERR_PaymentGateway_warn_3021);

        payment_account.approval_status = 3;

        emit Warn(_account_address, msg.sender);
        return true;
    }

    /// @notice 支払用口座情報を非承認状態にする
    /// @param _account_address アカウントアドレス
    /// @return 処理結果
    function disapprove(address _account_address)
        public
        returns (bool)
    {
        PaymentAccount storage payment_account = payment_accounts[_account_address][msg.sender];
        require(payment_account.account_address != address(0), ErrorCode.ERR_PaymentGateway_disapprove_3031);

        payment_account.approval_status = 1;

        emit Disapprove(_account_address, msg.sender);
        return true;
    }

    /// @notice 支払用口座情報を停止状態にする
    /// @param _account_address アカウントアドレス
    /// @return 処理結果
    function ban(address _account_address)
        public
        returns (bool)
    {
        PaymentAccount storage payment_account = payment_accounts[_account_address][msg.sender];
        require(payment_account.account_address != address(0), ErrorCode.ERR_PaymentGateway_ban_3041);

        payment_account.approval_status = 4;

        emit Ban(_account_address, msg.sender);
        return true;
    }

    /// @notice アカウントの承認状態を返却する
    /// @param _account_address アカウントアドレス
    /// @param _agent_address 収納代行業者のアドレス
    /// @return 承認状態
    function accountApproved(address _account_address, address _agent_address)
        public
        view
        returns (bool)
    {
        PaymentAccount storage payment_account = payment_accounts[_account_address][_agent_address];
        // アカウントが登録済み、かつ承認済みである場合、trueを返す
        if (payment_account.account_address != address(0) &&
        payment_account.approval_status == 2)
        {
            return true;
        } else {
            return false;
        }
    }

    /// @notice 支払用口座情報の修正
    /// @dev 収納代行業者による修正。口座登録アカウントによる修正はregister()を使う。この関数では認可状況の更新は行わない。
    /// @param _account_address 銀行口座情報登録アカウントアドレス
    /// @param _encrypted_info 銀行口座情報（暗号化済）
    /// @return 処理結果
    function modify(address _account_address, string memory _encrypted_info)
        public
        returns (bool)
    {
        PaymentAccount storage payment_account = payment_accounts[_account_address][msg.sender];

        // 登録済みか確認
        require(payment_account.account_address != address(0),ErrorCode.ERR_PaymentGateway_modify_3051);

        payment_account.encrypted_info = _encrypted_info;

        emit Modify(_account_address, msg.sender);
        return true;
    }
}
