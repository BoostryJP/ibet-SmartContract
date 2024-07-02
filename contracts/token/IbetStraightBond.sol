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

import "OpenZeppelin/openzeppelin-contracts@4.9.3/contracts/utils/math/SafeMath.sol";
import "../access/Ownable.sol";
import "../ledger/PersonalInfo.sol";
import "../utils/Errors.sol";
import "../../interfaces/ContractReceiver.sol";
import "../../interfaces/IbetSecurityTokenInterface.sol";

/// @title ibet Straight Bond Token
contract IbetStraightBond is Ownable, IbetSecurityTokenInterface {
    using SafeMath for uint256;

    uint256 public faceValue; // 額面金額
    uint256 public interestRate; // 年利
    string public interestPaymentDate; // 利払日（JSON）
    string public redemptionDate; // 償還日
    uint256 public redemptionValue; // 償還金額
    string public returnDate; // 特典付与日
    string public returnAmount; // 特典内容
    string public purpose; // 発行目的
    string public memo; // 補足情報
    bool public isRedeemed; // 償還状況
    string public faceValueCurrency; // 額面金額通貨
    string public interestPaymentCurrency; // 利払金額通貨
    string public redemptionValueCurrency; // 償還金額通貨
    string public baseFXRate; // 基準為替レート

    /// Event: 額面金額変更
    event ChangeFaceValue(uint256 faceValue);

    /// Event: 償還金額変更
    event ChangeRedemptionValue(uint256 redemptionValue);

    /// Event: 償還状態に変更
    event ChangeToRedeemed();

    // [CONSTRUCTOR]
    /// @param _name 名称
    /// @param _symbol 略称
    /// @param _totalSupply 総発行数量
    /// @param _faceValue 額面金額
    /// @param _faceValueCurrency 額面金額通貨
    /// @param _redemptionDate 償還日
    /// @param _redemptionValue 償還金額
    /// @param _redemptionValueCurrency 償還金額通貨
    /// @param _returnDate 特典付与日
    /// @param _returnAmount 特典内容
    /// @param _purpose 発行目的
    constructor(
        string memory _name,
        string memory _symbol,
        uint256 _totalSupply,
        uint256 _faceValue,
        string memory _faceValueCurrency,
        string memory _redemptionDate,
        uint256 _redemptionValue,
        string memory _redemptionValueCurrency,
        string memory _returnDate,
        string memory _returnAmount,
        string memory _purpose
    ) {
        owner = msg.sender;
        name = _name;
        symbol = _symbol;
        totalSupply = _totalSupply;
        faceValue = _faceValue;
        faceValueCurrency = _faceValueCurrency;
        redemptionDate = _redemptionDate;
        redemptionValue = _redemptionValue;
        redemptionValueCurrency = _redemptionValueCurrency;
        returnDate = _returnDate;
        returnAmount = _returnAmount;
        purpose = _purpose;
        balances[owner] = totalSupply;
        isRedeemed = false;
        status = true;
        requirePersonalInfoRegistered = true;
    }

    /// @notice アドレスがコントラクトアドレスであるかを判定
    /// @param _addr アドレス
    /// @return is_contract 判定結果
    function isContract(address _addr) private view returns (bool is_contract) {
        uint length;
        assembly {
            length := extcodesize(_addr)
        }
        return (length > 0);
    }

    /// @notice EOAへの移転
    /// @param _to 宛先アドレス
    /// @param _value 移転数量
    /// @return success 処理結果
    function transferToAddress(
        address _to,
        uint _value,
        bytes memory /*_data*/
    ) private returns (bool success) {
        if (
            msg.sender != tradableExchange && transferApprovalRequired == true
        ) {
            revert(ErrorCode.ERR_IbetStraightBond_transferToAddress_120201);
        }

        // <CHK>
        // 個人情報登録済みチェック
        // 以下の場合はチェックを行わない
        // - 発行体への移転の場合
        // - 移転時個人情報登録が不要の場合
        if (_to != owner && requirePersonalInfoRegistered == true) {
            require(
                PersonalInfo(personalInfoAddress).isRegistered(_to, owner) ==
                    true,
                ErrorCode.ERR_IbetStraightBond_transferToAddress_120202
            );
        }

        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        balances[_to] = balanceOf(_to).add(_value);

        // イベント登録
        emit Transfer(msg.sender, _to, _value);

        return true;
    }

    /// @notice コントラクトアドレスへの移転
    /// @param _to 宛先アドレス
    /// @param _value 移転数量
    /// @param _data 任意のデータ
    /// @return success 処理結果
    function transferToContract(
        address _to,
        uint _value,
        bytes memory _data
    ) private returns (bool success) {
        // 宛先はtradableExchangeのみ可能
        require(
            _to == tradableExchange,
            ErrorCode.ERR_IbetStraightBond_transferToContract_120301
        );

        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        balances[_to] = balanceOf(_to).add(_value);

        ContractReceiver receiver = ContractReceiver(_to);
        receiver.tokenFallback(msg.sender, _value, _data);

        // イベント登録
        emit Transfer(msg.sender, _to, _value);

        return true;
    }

    /// @notice 移転
    /// @param _to 宛先アドレス
    /// @param _value 移転数量
    /// @return success 処理結果
    function transfer(
        address _to,
        uint _value
    ) public override returns (bool success) {
        require(
            balanceOf(msg.sender) >= _value,
            ErrorCode.ERR_IbetStraightBond_transfer_120401
        );

        require(
            transferable == true,
            ErrorCode.ERR_IbetStraightBond_transfer_120402
        );

        bytes memory empty;
        if (isContract(_to)) {
            return transferToContract(_to, _value, empty);
        } else {
            return transferToAddress(_to, _value, empty);
        }
    }

    /// @notice 移転（一括）
    /// @param _toList 宛先アドレスのリスト
    /// @param _valueList 移転数量のリスト
    /// @return success 処理結果
    function bulkTransfer(
        address[] calldata _toList,
        uint[] calldata _valueList
    ) public override returns (bool success) {
        // <CHK>
        // リスト長が等しくない場合、エラーを返す
        if (_toList.length != _valueList.length)
            revert(ErrorCode.ERR_IbetStraightBond_bulkTransfer_120501);

        // <CHK>
        // 数量が残高を超えている場合、エラーを返す
        uint totalValue;
        for (uint i = 0; i < _toList.length; i++) {
            totalValue += _valueList[i];
        }
        if (balanceOf(msg.sender) < totalValue)
            revert(ErrorCode.ERR_IbetStraightBond_bulkTransfer_120502);

        // <CHK>
        // 譲渡可能ではない場合、エラーを返す
        if (msg.sender != tradableExchange) {
            require(
                transferable == true,
                ErrorCode.ERR_IbetStraightBond_bulkTransfer_120503
            );
        }

        bytes memory empty;
        bool result;
        success = true;
        for (uint i = 0; i < _toList.length; i++) {
            if (isContract(_toList[i])) {
                result = transferToContract(_toList[i], _valueList[i], empty);
            } else {
                result = transferToAddress(_toList[i], _valueList[i], empty);
            }
            if (result == false) {
                success = false;
            }
        }
        return success;
    }

    /// @notice 強制移転
    /// @dev オーナーのみ実行可能
    /// @param _from 移転元アドレス
    /// @param _to 移転先アドレス
    /// @param _value 移転数量
    /// @return success 処理結果
    function transferFrom(
        address _from,
        address _to,
        uint _value
    ) public override onlyOwner returns (bool success) {
        // <CHK>
        //  数量が送信元アドレス（from）の残高を超えている場合、エラーを返す
        if (balanceOf(_from) < _value)
            revert(ErrorCode.ERR_IbetStraightBond_transferFrom_120601);

        bytes memory empty;

        if (isContract(_to)) {
            // 送信先アドレスがコントラクトアドレスの場合
            balances[_from] = balanceOf(_from).sub(_value);
            balances[_to] = balanceOf(_to).add(_value);
            ContractReceiver receiver = ContractReceiver(_to);
            receiver.tokenFallback(msg.sender, _value, empty);
        } else {
            // 送信先アドレスがアカウントアドレスの場合
            balances[_from] = balanceOf(_from).sub(_value);
            balances[_to] = balanceOf(_to).add(_value);
        }

        // イベント登録
        emit Transfer(_from, _to, _value);

        return true;
    }

    /// @notice 強制移転（一括）
    /// @dev オーナーのみ実行可能
    /// @param _fromList 移転元アドレスのリスト
    /// @param _toList 移転先アドレスのリスト
    /// @param _valueList 移転数量のリスト
    /// @return success 処理結果
    function bulkTransferFrom(
        address[] calldata _fromList,
        address[] calldata _toList,
        uint[] calldata _valueList
    ) public override onlyOwner returns (bool success) {
        // <CHK>
        // 全てのリスト長が等しくない場合、エラーを返す
        if (
            _fromList.length != _toList.length ||
            _fromList.length != _valueList.length
        ) revert(ErrorCode.ERR_IbetStraightBond_bulkTransferFrom_121501);
        // 強制移転（一括）
        for (uint256 i = 0; i < _fromList.length; i++) {
            transferFrom(_fromList[i], _toList[i], _valueList[i]);
        }
        return true;
    }

    /// @notice 残高の参照
    /// @param _owner 保有者のアドレス
    /// @return 残高数量
    function balanceOf(address _owner) public view override returns (uint256) {
        return balances[_owner];
    }

    /// @notice 取引コントラクトの更新
    /// @dev オーナーのみ実行可能
    /// @param _exchange 更新後取引コントラクト
    function setTradableExchange(address _exchange) public override onlyOwner {
        tradableExchange = _exchange;
    }

    /// @notice 個人情報記帳コントラクトの更新
    /// @dev オーナーのみ実行可能
    /// @param _address 個人情報記帳コントラクトのアドレス
    function setPersonalInfoAddress(
        address _address
    ) public override onlyOwner {
        personalInfoAddress = _address;
    }

    /// @notice 移転時個人情報登録要否の更新
    /// @dev オーナーのみ実行可能
    /// @param _requireRegistered 移転時個人情報登録要否（true:必要）
    function setRequirePersonalInfoRegistered(
        bool _requireRegistered
    ) public override onlyOwner {
        requirePersonalInfoRegistered = _requireRegistered;
    }

    /// @notice 問い合わせ先情報の更新
    /// @dev オーナーのみ実行可能
    /// @param _contactInformation 問い合わせ先情報
    function setContactInformation(
        string memory _contactInformation
    ) public override onlyOwner {
        contactInformation = _contactInformation;
    }

    /// @notice プライバシーポリシーの更新
    /// @dev オーナーのみ実行可能
    /// @param _privacyPolicy プライバシーポリシー
    function setPrivacyPolicy(
        string memory _privacyPolicy
    ) public override onlyOwner {
        privacyPolicy = _privacyPolicy;
    }

    /// @notice 補足情報の更新
    /// @dev オーナーのみ実行可能
    /// @param _memo 補足情報
    function setMemo(string memory _memo) public onlyOwner {
        memo = _memo;
    }

    /// @notice 年利情報の更新
    /// @dev オーナーのみ実行可能
    /// @param _interestRate 年利
    function setInterestRate(uint _interestRate) public onlyOwner {
        interestRate = _interestRate;
    }

    /// @notice 利払日情報の更新
    /// @dev オーナーのみ実行可能
    /// @param _interestPaymentDate 利払日（JSON）
    function setInterestPaymentDate(
        string memory _interestPaymentDate
    ) public onlyOwner {
        interestPaymentDate = _interestPaymentDate;
    }

    /// @notice 譲渡可否の更新
    /// @dev オーナーのみ実行可能
    /// @param _transferable 譲渡可否
    function setTransferable(bool _transferable) public override onlyOwner {
        transferable = _transferable;
    }

    /// @notice 取扱ステータスの更新
    /// @dev オーナーのみ実行可能
    /// @param _status 更新後の取扱ステータス
    function setStatus(bool _status) public override onlyOwner {
        status = _status;

        // イベント登録
        emit ChangeStatus(status);
    }

    /// @notice 額面金額の更新
    /// @dev オーナーのみ実行可能
    /// @param _faceValue 更新後の額面金額
    function setFaceValue(uint256 _faceValue) public onlyOwner {
        faceValue = _faceValue;

        // イベント登録
        emit ChangeFaceValue(_faceValue);
    }

    /// @notice 償還金額の更新
    /// @dev オーナーのみ実行可能
    /// @param _redemptionValue 更新後の償還金額
    function setRedemptionValue(uint256 _redemptionValue) public onlyOwner {
        redemptionValue = _redemptionValue;

        // イベント登録
        emit ChangeRedemptionValue(_redemptionValue);
    }

    /// @notice 移転承諾要否フラグの更新
    /// @dev 発行体のみ実行可能
    /// @param _required 移転承諾要否
    function setTransferApprovalRequired(
        bool _required
    ) public override onlyOwner {
        transferApprovalRequired = _required;

        // イベント登録
        emit ChangeTransferApprovalRequired(_required);
    }

    /// @notice 額面金額通貨の更新
    /// @dev オーナーのみ実行可能
    /// @param _faceValueCurrency 更新後の額面金額通貨
    function setFaceValueCurrency(
        string memory _faceValueCurrency
    ) public onlyOwner {
        faceValueCurrency = _faceValueCurrency;
    }

    /// @notice 利払金額通貨の更新
    /// @dev オーナーのみ実行可能
    /// @param _interestPaymentCurrency 更新後の利払金額通貨
    function setInterestPaymentCurrency(
        string memory _interestPaymentCurrency
    ) public onlyOwner {
        interestPaymentCurrency = _interestPaymentCurrency;
    }

    /// @notice 償還金額通貨の更新
    /// @dev オーナーのみ実行可能
    /// @param _redemptionValueCurrency 更新後の償還金額通貨
    function setRedemptionValueCurrency(
        string memory _redemptionValueCurrency
    ) public onlyOwner {
        redemptionValueCurrency = _redemptionValueCurrency;
    }

    /// @notice 基準為替レートの更新
    /// @dev オーナーのみ実行可能
    /// @param _baseFXRate 更新後の基準為替レート
    function setBaseFXRate(string memory _baseFXRate) public onlyOwner {
        baseFXRate = _baseFXRate;
    }

    /// @notice 新規募集ステータスの更新
    /// @dev オーナーのみ実行可能
    /// @param _isOffering 募集状態
    function changeOfferingStatus(bool _isOffering) public override onlyOwner {
        isOffering = _isOffering;

        // イベント登録
        emit ChangeOfferingStatus(_isOffering);
    }

    /// @notice 募集申込
    /// @param _amount 申込数量
    /// @param _data 申込付与情報
    function applyForOffering(
        uint256 _amount,
        string memory _data
    ) public override {
        // 申込ステータスが停止中の場合、エラーを返す
        require(
            isOffering == true,
            ErrorCode.ERR_IbetStraightBond_applyForOffering_121001
        );

        if (requirePersonalInfoRegistered == true) {
            // 個人情報未登録の場合、エラーを返す
            require(
                PersonalInfo(personalInfoAddress).isRegistered(
                    msg.sender,
                    owner
                ) == true,
                ErrorCode.ERR_IbetStraightBond_applyForOffering_121002
            );
        }

        applicationsForOffering[msg.sender].applicationAmount = _amount;
        applicationsForOffering[msg.sender].data = _data;

        // イベント登録
        emit ApplyForOffering(msg.sender, _amount, _data);
    }

    /// @notice 募集割当
    /// @dev オーナーのみ実行可能
    /// @param _accountAddress 割当先アカウント
    /// @param _amount 割当数量
    function allot(
        address _accountAddress,
        uint256 _amount
    ) public override onlyOwner {
        applicationsForOffering[_accountAddress].allotmentAmount = _amount;

        // イベント登録
        emit Allot(_accountAddress, _amount);
    }

    /// @notice ロック中資産の参照
    /// @param _lockAddress ロック先アドレス
    /// @param _accountAddress ロック対象アカウント
    /// @return ロック中の数量
    function lockedOf(
        address _lockAddress,
        address _accountAddress
    ) public view override returns (uint256) {
        return locked[_lockAddress][_accountAddress];
    }

    /// @notice 資産をロックする
    /// @param _lockAddress 資産ロック先アドレス
    /// @param _value ロックする数量
    /// @param _data イベント出力用の任意のデータ
    function lock(
        address _lockAddress,
        uint256 _value,
        string memory _data
    ) public override {
        // ロック数量が保有数量を上回っている場合、エラーを返す
        if (balanceOf(msg.sender) < _value)
            revert(ErrorCode.ERR_IbetStraightBond_lock_120002);

        // データ更新
        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        locked[_lockAddress][msg.sender] = lockedOf(_lockAddress, msg.sender)
            .add(_value);

        // イベント登録
        emit Lock(msg.sender, _lockAddress, _value, _data);
    }

    /// @notice 資産をアンロックする
    /// @param _accountAddress アンロック対象のアドレス
    /// @param _recipientAddress 受取アドレス
    /// @param _data イベント出力用の任意のデータ
    function unlock(
        address _accountAddress,
        address _recipientAddress,
        uint256 _value,
        string memory _data
    ) public override {
        // アンロック数量がロック数量を上回ってる場合、エラーを返す
        if (lockedOf(msg.sender, _accountAddress) < _value)
            revert(ErrorCode.ERR_IbetStraightBond_unlock_120102);

        // データ更新
        locked[msg.sender][_accountAddress] = lockedOf(
            msg.sender,
            _accountAddress
        ).sub(_value);
        balances[_recipientAddress] = balanceOf(_recipientAddress).add(_value);

        // イベント登録
        emit Unlock(
            _accountAddress,
            msg.sender,
            _recipientAddress,
            _value,
            _data
        );
    }

    /// @notice 資産を強制アンロックする
    /// @dev 発行体のみ実行可能
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
    ) public override onlyOwner {
        // アンロック数量がロック数量を上回ってる場合、エラーを返す
        if (lockedOf(_lockAddress, _accountAddress) < _value)
            revert(ErrorCode.ERR_IbetStraightBond_forceUnlock_121201);

        // データ更新
        locked[_lockAddress][_accountAddress] = lockedOf(
            _lockAddress,
            _accountAddress
        ).sub(_value);
        balances[_recipientAddress] = balanceOf(_recipientAddress).add(_value);

        // イベント登録
        emit Unlock(
            _accountAddress,
            _lockAddress,
            _recipientAddress,
            _value,
            _data
        );
    }

    /// @notice 移転申請
    /// @param _to 移転先アドレス
    /// @param _value 移転数量
    /// @param _data イベント出力用の任意のデータ
    function applyForTransfer(
        address _to,
        uint256 _value,
        string memory _data
    ) public override {
        // <CHK>
        //  1) 移転時の発行体承諾が不要な場合
        //  2) 移転不可の場合
        //  3) 数量が残高を超えている場合
        //  -> REVERT
        if (
            transferApprovalRequired == false ||
            transferable == false ||
            balanceOf(msg.sender) < _value
        ) {
            revert(ErrorCode.ERR_IbetStraightBond_applyForTransfer_120701);
        }

        // <CHK>
        // 個人情報登録済みチェック
        // 以下の場合はチェックを行わない
        // - 発行体への移転の場合
        // - 移転時個人情報登録が不要の場合
        if (_to != owner && requirePersonalInfoRegistered == true) {
            require(
                PersonalInfo(personalInfoAddress).isRegistered(_to, owner) ==
                    true,
                ErrorCode.ERR_IbetStraightBond_applyForTransfer_120702
            );
        }

        balances[msg.sender] -= _value;
        pendingTransfer[msg.sender] += _value;

        uint256 index = applicationsForTransfer.length;
        applicationsForTransfer.push(
            ApplicationForTransfer({
                from: msg.sender,
                to: _to,
                amount: _value,
                valid: true
            })
        );

        // イベント登録
        emit ApplyForTransfer(index, msg.sender, _to, _value, _data);
    }

    /// @notice 移転申請取消
    /// @dev 発行体または申請者のみが実行可能
    /// @param _index 取消対象のインデックス
    /// @param _data イベント出力用の任意のデータ
    function cancelTransfer(
        uint256 _index,
        string memory _data
    ) public override {
        // <CHK>
        // 実行者自身の移転申請ではない場合 かつ
        // 実行者が発行体ではない場合
        // -> REVERT
        if (
            applicationsForTransfer[_index].from != msg.sender &&
            msg.sender != owner
        ) {
            revert(ErrorCode.ERR_IbetStraightBond_cancelTransfer_120801);
        }

        // <CHK>
        // すでに無効な申請に対する取消の場合
        // -> REVERT
        if (applicationsForTransfer[_index].valid == false)
            revert(ErrorCode.ERR_IbetStraightBond_cancelTransfer_120802);

        balances[
            applicationsForTransfer[_index].from
        ] += applicationsForTransfer[_index].amount;
        pendingTransfer[
            applicationsForTransfer[_index].from
        ] -= applicationsForTransfer[_index].amount;

        applicationsForTransfer[_index].valid = false;

        // イベント登録
        emit CancelTransfer(
            _index,
            applicationsForTransfer[_index].from,
            applicationsForTransfer[_index].to,
            _data
        );
    }

    /// @notice 移転承認
    /// @dev 発行体のみが実行可能
    /// @param _index 承認対象のインデックス
    /// @param _data イベント出力用の任意のデータ
    function approveTransfer(
        uint256 _index,
        string memory _data
    ) public override onlyOwner {
        // <CHK>
        // 移転不可の場合
        // -> REVERT
        if (transferable == false)
            revert(ErrorCode.ERR_IbetStraightBond_approveTransfer_120901);

        // <CHK>
        // すでに無効な申請に対する取消の場合
        // -> REVERT
        if (applicationsForTransfer[_index].valid == false)
            revert(ErrorCode.ERR_IbetStraightBond_approveTransfer_120902);

        balances[applicationsForTransfer[_index].to] += applicationsForTransfer[
            _index
        ].amount;
        pendingTransfer[
            applicationsForTransfer[_index].from
        ] -= applicationsForTransfer[_index].amount;

        applicationsForTransfer[_index].valid = false;

        // イベント登録
        emit ApproveTransfer(
            _index,
            applicationsForTransfer[_index].from,
            applicationsForTransfer[_index].to,
            _data
        );
        emit Transfer(
            applicationsForTransfer[_index].from,
            applicationsForTransfer[_index].to,
            applicationsForTransfer[_index].amount
        );
    }

    /// @notice 追加発行
    /// @dev オーナーのみ実行可能
    /// @param _targetAddress 追加発行対象の残高を保有するアドレス
    /// @param _lockAddress 資産ロック先アドレス: ロック残高に追加する場合に指定。ゼロアドレスの場合はEOA残高に追加。
    /// @param _amount 追加発行数量
    function issueFrom(
        address _targetAddress,
        address _lockAddress,
        uint256 _amount
    ) public override onlyOwner {
        // locked_addressを指定した場合：ロック資産に対して追加発行を行う
        // locked_addressを指定しない場合：アカウントアドレスの残高に対して追加発行を行う
        if (_lockAddress != address(0)) {
            // ロック資産の更新
            locked[_lockAddress][_targetAddress] = lockedOf(
                _lockAddress,
                _targetAddress
            ).add(_amount);
            // 総発行数量の更新
            totalSupply = totalSupply.add(_amount);
        } else {
            // アカウント残高の更新
            balances[_targetAddress] = balanceOf(_targetAddress).add(_amount);
            // 総発行数量の更新
            totalSupply = totalSupply.add(_amount);
        }

        // イベント登録
        emit Issue(msg.sender, _targetAddress, _lockAddress, _amount);
    }

    /// @notice 追加発行（一括）
    /// @dev 指定したアドレスの残高に対して、追加発行を行う
    /// @dev 発行体のみ実行可能
    /// @param _targetAddressList 追加発行対象の残高を保有するアドレスのリスト
    /// @param _lockAddressList 資産ロック先アドレスのリスト: ロック残高に追加する場合に指定。ゼロアドレスの場合はEOA残高に追加。
    /// @param _amounts 追加発行数量のリスト
    function bulkIssueFrom(
        address[] calldata _targetAddressList,
        address[] calldata _lockAddressList,
        uint256[] calldata _amounts
    ) public override onlyOwner {
        // <CHK>
        // 全てのリスト長が等しくない場合、エラーを返す
        if (
            _targetAddressList.length != _lockAddressList.length ||
            _targetAddressList.length != _amounts.length
        ) revert(ErrorCode.ERR_IbetStraightBond_bulkIssueFrom_121301);

        // 追加発行（一括）
        for (uint256 i = 0; i < _targetAddressList.length; i++) {
            issueFrom(_targetAddressList[i], _lockAddressList[i], _amounts[i]);
        }
    }

    /// @notice 償却
    /// @dev 特定のアドレスの残高に対して、発行数量の削減を行う
    /// @dev 発行体のみ実行可能
    /// @param _targetAddress 償却対象の残高を保有するアドレス
    /// @param _lockAddress 資産ロック先アドレス: ロック残高から償却する場合に指定。ゼロアドレスの場合はEOA残高より償却。
    /// @param _amount 償却数量
    function redeemFrom(
        address _targetAddress,
        address _lockAddress,
        uint256 _amount
    ) public override onlyOwner {
        // locked_addressを指定した場合：ロック資産から減資を行う
        // locked_addressを指定しない場合：アカウントアドレスの残高から減資を行う
        if (_lockAddress != address(0)) {
            // 減資数量が対象アドレスのロック数量を上回っている場合はエラー
            if (lockedOf(_lockAddress, _targetAddress) < _amount)
                revert(ErrorCode.ERR_IbetStraightBond_redeemFrom_121101);
            // ロック資産の更新
            locked[_lockAddress][_targetAddress] = lockedOf(
                _lockAddress,
                _targetAddress
            ).sub(_amount);
            // 総発行数量の更新
            totalSupply = totalSupply.sub(_amount);
        } else {
            // 減資数量が対象アドレスの残高数量を上回っている場合はエラーを返す
            if (balances[_targetAddress] < _amount)
                revert(ErrorCode.ERR_IbetStraightBond_redeemFrom_121102);
            // アカウント残高の更新
            balances[_targetAddress] = balanceOf(_targetAddress).sub(_amount);
            // 総発行数量の更新
            totalSupply = totalSupply.sub(_amount);
        }

        // イベント登録
        emit Redeem(msg.sender, _targetAddress, _lockAddress, _amount);
    }

    /// @notice 償却（一括）
    /// @dev 指定したアドレスの残高に対して、数量の削減を行う
    /// @dev 発行体のみ実行可能
    /// @param _targetAddressList 償却対象の残高を保有するアドレスのリスト
    /// @param _lockAddressList 資産ロック先アドレスのリスト: ロック残高から償却する場合に指定。ゼロアドレスの場合はEOA残高より償却。
    /// @param _amounts 償却数量のリスト
    function bulkRedeemFrom(
        address[] calldata _targetAddressList,
        address[] calldata _lockAddressList,
        uint256[] calldata _amounts
    ) public override onlyOwner {
        // <CHK>
        // 全てのリスト長が等しくない場合、エラーを返す
        if (
            _targetAddressList.length != _lockAddressList.length ||
            _targetAddressList.length != _amounts.length
        ) revert(ErrorCode.ERR_IbetStraightBond_bulkRedeemFrom_121401);

        // 償却（一括）
        for (uint256 i = 0; i < _targetAddressList.length; i++) {
            redeemFrom(_targetAddressList[i], _lockAddressList[i], _amounts[i]);
        }
    }

    /// @notice 償還状態に変更
    /// @dev オーナーのみ実行可能
    function changeToRedeemed() public onlyOwner {
        isRedeemed = true;

        // イベント登録
        emit ChangeToRedeemed();
    }
}
