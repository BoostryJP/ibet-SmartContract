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

import "./IbetStandardTokenInterface.sol";

/// @title ibet Security Token Interface
abstract contract IbetSecurityTokenInterface is IbetStandardTokenInterface {
    // -------------------------------------------------------------------
    // 投資家名簿関連機能
    // -------------------------------------------------------------------

    /// 個人情報コントラクト
    address public personalInfoAddress;

    /// @notice 個人情報コントラクトの更新
    /// @param _address 個人情報記帳コントラクトアドレス
    function setPersonalInfoAddress(address _address) public virtual;

    /// 移転時個人情報登録要否
    bool public requirePersonalInfoRegistered;

    /// @notice 移転時個人情報登録要否の更新
    /// @param _requireRegistered 移転時個人情報登録要否（true:必要）
    function setRequirePersonalInfoRegistered(
        bool _requireRegistered
    ) public virtual;

    // -------------------------------------------------------------------
    // 譲渡制限関連機能
    // -------------------------------------------------------------------

    /// 譲渡可否
    bool public transferable;

    /// @notice 譲渡可否を更新
    /// @param _transferable 譲渡可否
    function setTransferable(bool _transferable) public virtual;

    // -------------------------------------------------------------------
    // 募集関連機能
    // -------------------------------------------------------------------

    /// 募集ステータス
    bool public isOffering;

    /// 募集申込
    struct ApplicationForOffering {
        uint256 applicationAmount; // 申込数量
        uint256 allotmentAmount; // 割当数量
        string data; // 申込付与情報
    }
    mapping(address => ApplicationForOffering) public applicationsForOffering;

    /// @notice 募集ステータス更新
    /// @param _isOffering 募集状態
    function changeOfferingStatus(bool _isOffering) public virtual;

    /// @notice 募集申込
    /// @param _amount 申込数量
    /// @param _data 申込付与情報
    function applyForOffering(
        uint256 _amount,
        string memory _data
    ) public virtual;

    /// @notice 募集割当
    /// @param _accountAddress 割当先アカウント
    /// @param _amount 割当数量
    function allot(address _accountAddress, uint256 _amount) public virtual;

    /// Event: 募集ステータス変更
    event ChangeOfferingStatus(bool indexed status);

    /// Event: 募集申込
    event ApplyForOffering(address accountAddress, uint256 amount, string data);

    /// Event: 募集割当
    event Allot(address accountAddress, uint256 amount);

    // -------------------------------------------------------------------
    // 移転承諾関連機能
    // -------------------------------------------------------------------

    /// 移転承諾要否フラグ
    bool public transferApprovalRequired;

    /// @notice 移転承諾要否フラグの更新
    /// @param _required 移転承諾要否
    function setTransferApprovalRequired(bool _required) public virtual;

    /// 移転申請
    struct ApplicationForTransfer {
        address from; // 移転元アドレス
        address to; // 移転先アドレス
        uint256 amount; // 移転数量
        bool valid; // 申請有効状態
    }
    ApplicationForTransfer[] public applicationsForTransfer;

    // 移転待ち数量
    // address => amount
    mapping(address => uint256) public pendingTransfer;

    /// @notice 移転申請
    /// @param _to 移転先アドレス
    /// @param _value 移転数量
    /// @param _data イベント出力用の任意のデータ
    function applyForTransfer(
        address _to,
        uint256 _value,
        string memory _data
    ) public virtual;

    /// @notice 移転申請取消
    /// @param _index 取消対象のインデックス
    /// @param _data イベント出力用の任意のデータ
    function cancelTransfer(uint256 _index, string memory _data) public virtual;

    /// @notice 移転承認
    /// @param _index 承認対象のインデックス
    /// @param _data イベント出力用の任意のデータ
    function approveTransfer(
        uint256 _index,
        string memory _data
    ) public virtual;

    /// Event: 移転承諾要否フラグ変更
    event ChangeTransferApprovalRequired(bool required);

    /// Event: 移転申請
    event ApplyForTransfer(
        uint256 indexed index,
        address from,
        address to,
        uint256 value,
        string data
    );

    /// Event: 移転申請取消
    event CancelTransfer(
        uint256 indexed index,
        address from,
        address to,
        string data
    );

    /// Event: 移転承認
    event ApproveTransfer(
        uint256 indexed index,
        address from,
        address to,
        string data
    );

    // -------------------------------------------------------------------
    // 資産ロック関連機能
    // -------------------------------------------------------------------

    /// ロック中数量
    /// lockAddress => accountAddress => balance
    mapping(address => mapping(address => uint256)) public locked;

    /// @notice 資産をロックする
    /// @param _lockAddress 資産ロック先アドレス
    /// @param _value ロックする数量
    /// @param _data イベント出力用の任意のデータ
    function lock(
        address _lockAddress,
        uint256 _value,
        string memory _data
    ) public virtual;

    /// @notice 資産をアンロックする
    /// @param _accountAddress アンロック対象のアドレス
    /// @param _recipientAddress 受取アドレス
    /// @param _data イベント出力用の任意のデータ
    function unlock(
        address _accountAddress,
        address _recipientAddress,
        uint256 _value,
        string memory _data
    ) public virtual;

    /// @notice 資産を強制アンロックする
    /// @param _lockAddress 資産ロック先アドレス
    /// @param _accountAddress アンロック対象のアドレス
    /// @param _recipientAddress 受取アドレス
    /// @param _data イベント出力用の任意のデータ
    function forceUnlock(
        address _lockAddress,
        address _accountAddress,
        address _recipientAddress,
        uint256 _value,
        string memory _data
    ) public virtual;

    /// @notice ロック中資産の参照
    /// @param _lockAddress ロック先アドレス
    /// @param _accountAddress ロック対象アカウント
    /// @return ロック中の数量
    function lockedOf(
        address _lockAddress,
        address _accountAddress
    ) public view virtual returns (uint256);

    /// Event: 資産ロック
    event Lock(
        address indexed accountAddress,
        address indexed lockAddress,
        uint256 value,
        string data
    );

    /// Event: 資産アンロック
    event Unlock(
        address indexed accountAddress,
        address indexed lockAddress,
        address recipientAddress,
        uint256 value,
        string data
    );

    // -------------------------------------------------------------------
    // 追加発行・償却
    // -------------------------------------------------------------------

    /// @notice 追加発行
    /// @param _targetAddress 追加発行対象の残高を保有するアドレス
    /// @param _lockAddress 資産ロック先アドレス
    /// @param _amount 追加発行数量
    function issueFrom(
        address _targetAddress,
        address _lockAddress,
        uint256 _amount
    ) public virtual;

    /// @notice 追加発行（一括）
    /// @param _targetAddressList 追加発行対象の残高を保有するアドレスのリスト
    /// @param _lockAddressList 資産ロック先アドレスのリスト
    /// @param _amounts 追加発行数量のリスト
    function bulkIssueFrom(
        address[] calldata _targetAddressList,
        address[] calldata _lockAddressList,
        uint256[] calldata _amounts
    ) public virtual;

    /// @notice 償却/消却
    /// @param _targetAddress 償却対象の残高を保有するアドレス
    /// @param _lockAddress 資産ロック先アドレス
    /// @param _amount 償却数量
    function redeemFrom(
        address _targetAddress,
        address _lockAddress,
        uint256 _amount
    ) public virtual;

    /// @notice 償却/消却（一括）
    /// @param _targetAddressList 償却対象の残高を保有するアドレスのリスト
    /// @param _lockAddressList 資産ロック先アドレスのリスト
    /// @param _amounts 償却数量のリスト
    function bulkRedeemFrom(
        address[] calldata _targetAddressList,
        address[] calldata _lockAddressList,
        uint256[] calldata _amounts
    ) public virtual;

    /// Event: 追加発行
    event Issue(
        address indexed from,
        address indexed targetAddress,
        address indexed lockAddress,
        uint256 amount
    );

    /// Event: 償却/消却
    event Redeem(
        address indexed from,
        address indexed targetAddress,
        address indexed lockAddress,
        uint256 amount
    );
}
