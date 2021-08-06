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

import "./SafeMath.sol";
import "./Ownable.sol";
import "./PersonalInfo.sol";
import "../interfaces/ContractReceiver.sol";
import "../interfaces/IbetStandardTokenInterface.sol";


/// @title ibet Straight Bond Token
contract IbetStraightBond is Ownable, IbetStandardTokenInterface {
    using SafeMath for uint256;

    // 募集申込情報
    struct Application {
        uint256 requestedAmount; // 申込数量
        uint256 allottedAmount; // 割当数量
        string data; // その他データ
    }

    // 属性情報
    uint256 public faceValue; // 額面金額
    uint256 public interestRate; // 年利
    string public interestPaymentDate; // 利払日（JSON）
    string public redemptionDate; // 償還日
    uint256 public redemptionValue; // 償還金額
    string public returnDate; // 特典付与日
    string public returnAmount; // 特典内容
    string public purpose; // 発行目的
    string public memo; // 補足情報
    bool public initialOfferingStatus; // 新規募集ステータス（True：募集中、False：停止中）
    bool public isRedeemed; // 償還状況
    bool public transferable; // 譲渡可否
    address public personalInfoAddress; // 個人情報記帳コントラクト

    // 第三者認定情報
    // signer_address => status
    mapping(address => uint8) public signatures;

    // 商品画像
    // image class => url
    mapping(uint8 => string) public image_urls;

    // 募集申込
    // account_address => data
    mapping(address => Application) public applications;

    // 資産ロック認可済アドレス
    mapping(address => bool) public authorizedAddress;

    // ロックされた数量
    // locked_address => account_address => balance
    mapping(address => mapping(address => uint256)) public locked;

    // イベント：認定
    event Sign(address indexed signer);

    // イベント：認定取消
    event Unsign(address indexed signer);

    // イベント：償還
    event Redeem();

    // イベント：募集ステータス変更
    event ChangeInitialOfferingStatus(bool indexed status);

    // イベント：募集申込
    event ApplyFor(address indexed accountAddress, uint256 amount);

    // イベント：割当
    event Allot(address indexed accountAddress, uint256 amount);

    // イベント：認可
    event Authorize(address indexed to, bool auth);

    // イベント：資産ロック
    event Lock(address indexed from, address indexed target_address, uint256 value);

    // イベント：資産アンロック
    event Unlock(address indexed from, address indexed to, uint256 value);

    // イベント：追加発行
    event Issue(address indexed from, address indexed target_address, address indexed locked_address, uint256 amount);

    // イベント：額面金額変更
    event ChangeFaceValue(uint256 faceValue);

    // イベント：償還金額変更
    event ChangeRedemptionValue(uint256 redemptionValue);

    // [CONSTRUCTOR]
    /// @param _name 名称
    /// @param _symbol 略称
    /// @param _totalSupply 総発行数量
    /// @param _faceValue 額面金額
    /// @param _redemptionDate 償還日
    /// @param _redemptionValue 償還金額
    /// @param _returnDate 特典付与日
    /// @param _returnAmount 特典内容
    /// @param _purpose 発行目的
    constructor(
        string memory _name,
        string memory _symbol,
        uint256 _totalSupply,
        uint256 _faceValue,
        string memory _redemptionDate,
        uint256 _redemptionValue,
        string memory _returnDate,
        string memory _returnAmount,
        string memory _purpose
    )
    {
        owner = msg.sender;
        name = _name;
        symbol = _symbol;
        totalSupply = _totalSupply;
        faceValue = _faceValue;
        redemptionDate = _redemptionDate;
        redemptionValue = _redemptionValue;
        returnDate = _returnDate;
        returnAmount = _returnAmount;
        purpose = _purpose;
        transferable = true;
        balances[owner] = totalSupply;
        isRedeemed = false;
        status = true;
    }

    /// @notice アドレスがコントラクトアドレスであるかを判定
    /// @param _addr アドレス
    /// @return is_contract 判定結果
    function isContract(address _addr)
        private
        view
        returns (bool is_contract)
    {
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
    function transferToAddress(address _to, uint _value, bytes memory /*_data*/)
        private
        returns (bool success)
    {
        if (msg.sender != tradableExchange) {
            require(PersonalInfo(personalInfoAddress).isRegistered(_to, owner) == true);
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
    function transferToContract(address _to, uint _value, bytes memory _data)
        private
        returns (bool success)
    {
        require(_to == tradableExchange);
        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        balances[_to] = balanceOf(_to).add(_value);

        ContractReceiver receiver = ContractReceiver(_to);
        receiver.tokenFallback(msg.sender, _value, _data);

        // イベント登録
        emit Transfer(msg.sender, _to, _value);

        return true;
    }

    /// @notice トークンの移転
    /// @param _to 宛先アドレス
    /// @param _value 移転数量
    /// @return success 処理結果
    function transfer(address _to, uint _value)
        public
        override
        returns (bool success)
    {
        // <CHK>
        //  数量が残高を超えている場合、エラーを返す
        if (balanceOf(msg.sender) < _value) revert();
        if (msg.sender != tradableExchange) {
            // 譲渡可能ではない場合、エラーを返す
            require(transferable == true);
        }

        bytes memory empty;
        if (isContract(_to)) {
            return transferToContract(_to, _value, empty);
        } else {
            return transferToAddress(_to, _value, empty);
        }
    }

    /// @notice トークンの一括移転
    /// @param _toList 宛先アドレスのリスト
    /// @param _valueList 移転数量のリスト
    /// @return success 処理結果
    function bulkTransfer(address[] memory _toList, uint[] memory _valueList)
        public
        override
        returns (bool success)
    {
        // <CHK>
        // リスト長が等しくない場合、エラーを返す
        if (_toList.length != _valueList.length) revert();

        // <CHK>
        // 数量が残高を超えている場合、エラーを返す
        uint totalValue;
        for(uint i = 0; i < _toList.length; i++) {
             totalValue += _valueList[i];
        }
        if (balanceOf(msg.sender) < totalValue) revert();

        // <CHK>
        // 譲渡可能ではない場合、エラーを返す
        if (msg.sender != tradableExchange) {
            require(transferable == true);
        }

        bytes memory empty;
        bool result = false;
        for(uint i = 0; i < _toList.length; i++) {
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
    function transferFrom(address _from, address _to, uint _value)
        public
        onlyOwner()
        returns (bool success)
    {
        // <CHK>
        //  数量が送信元アドレス（from）の残高を超えている場合、エラーを返す
        if (balanceOf(_from) < _value) revert();

        bytes memory empty;

        if (isContract(_to)) {// 送信先アドレスがコントラクトアドレスの場合
            balances[_from] = balanceOf(_from).sub(_value);
            balances[_to] = balanceOf(_to).add(_value);
            ContractReceiver receiver = ContractReceiver(_to);
            receiver.tokenFallback(msg.sender, _value, empty);
        } else {// 送信先アドレスがアカウントアドレスの場合
            balances[_from] = balanceOf(_from).sub(_value);
            balances[_to] = balanceOf(_to).add(_value);
        }

        // イベント登録
        emit Transfer(_from, _to, _value);

        return true;
    }

    /// @notice 残高の参照
    /// @param _owner 保有者のアドレス
    /// @return 残高数量
    function balanceOf(address _owner)
        public
        view
        override
        returns (uint256)
    {
        return balances[_owner];
    }

    /// @notice 取引コントラクトの更新
    /// @dev オーナーのみ実行可能
    /// @param _exchange 更新後取引コントラクト
    function setTradableExchange(address _exchange)
        public
        onlyOwner()
        override
    {
        tradableExchange = _exchange;
    }

    /// @notice 個人情報記帳コントラクトの更新
    /// @dev オーナーのみ実行可能
    /// @param _address 個人情報記帳コントラクトのアドレス
    function setPersonalInfoAddress(address _address)
        public
        onlyOwner()
    {
        personalInfoAddress = _address;
    }

    /// @notice 問い合わせ先情報の更新
    /// @dev オーナーのみ実行可能
    /// @param _contactInformation 問い合わせ先情報
    function setContactInformation(string memory _contactInformation)
        public
        onlyOwner()
        override
    {
        contactInformation = _contactInformation;
    }

    /// @notice プライバシーポリシーの更新
    /// @dev オーナーのみ実行可能
    /// @param _privacyPolicy プライバシーポリシー
    function setPrivacyPolicy(string memory _privacyPolicy)
        public
        onlyOwner()
        override
    {
        privacyPolicy = _privacyPolicy;
    }

    /// @notice 商品画像の更新
    /// @dev オーナーのみ実行可能
    /// @param _class 画像番号
    /// @param _image_url 画像URL
    function setImageURL(uint8 _class, string memory _image_url)
        public
        onlyOwner()
    {
        image_urls[_class] = _image_url;
    }

    /// @notice 商品画像の参照
    /// @param _class 画像番号
    /// @return 画像URL
    function getImageURL(uint8 _class)
        public
        view
        returns (string memory)
    {
        return image_urls[_class];
    }

    /// @notice 補足情報の更新
    /// @dev オーナーのみ実行可能
    /// @param _memo 補足情報
    function setMemo(string memory _memo)
        public
        onlyOwner()
    {
        memo = _memo;
    }

    /// @notice 年利情報の更新
    /// @dev オーナーのみ実行可能
    /// @param _interestRate 年利
    function setInterestRate(uint _interestRate)
        public
        onlyOwner()
    {
        interestRate = _interestRate;
    }

    /// @notice 利払日情報の更新
    /// @dev オーナーのみ実行可能
    /// @param _interestPaymentDate 利払日（JSON）
    function setInterestPaymentDate(string memory _interestPaymentDate)
        public
        onlyOwner()
    {
        interestPaymentDate = _interestPaymentDate;
    }

    /// @notice 譲渡可否の更新
    /// @dev オーナーのみ実行可能
    /// @param _transferable 譲渡可否
    function setTransferable(bool _transferable)
        public
        onlyOwner()
    {
        transferable = _transferable;
    }

    /// @notice 取扱ステータスの更新
    /// @dev オーナーのみ実行可能
    /// @param _status 更新後の取扱ステータス
    function setStatus(bool _status)
        public
        onlyOwner()
        override
    {
        status = _status;
        emit ChangeStatus(status);
    }

    /// @notice 商品の認定をリクエストする
    /// @param _signer 認定者
    /// @return 処理結果
    function requestSignature(address _signer)
        public
        returns (bool)
    {
        signatures[_signer] = 1;
        return true;
    }

    /// @notice 商品を認定する
    /// @return 処理結果
    function sign()
        public
        returns (bool)
    {
        require(signatures[msg.sender] == 1);
        signatures[msg.sender] = 2;
        emit Sign(msg.sender);
        return true;
    }

    /// @notice 商品の認定を取り消す
    /// @return 処理結果
    function unsign()
        public
        returns (bool)
    {
        require(signatures[msg.sender] == 2);
        signatures[msg.sender] = 0;
        emit Unsign(msg.sender);
        return true;
    }

    /// @notice 新規募集ステータスの更新
    /// @dev オーナーのみ実行可能
    /// @param _status 募集ステータス
    function setInitialOfferingStatus(bool _status)
        public
        onlyOwner()
    {
        initialOfferingStatus = _status;
        emit ChangeInitialOfferingStatus(_status);
    }

    /// @notice 募集申込
    /// @param _data 申込付与情報
    function applyForOffering(uint256 _amount, string memory _data)
        public
    {
        // 申込ステータスが停止中の場合、エラーを返す
        require(initialOfferingStatus == true);

        // 個人情報未登録の場合、エラーを返す
        require(PersonalInfo(personalInfoAddress).isRegistered(msg.sender, owner) == true);

        applications[msg.sender].requestedAmount = _amount;
        applications[msg.sender].data = _data;
        emit ApplyFor(msg.sender, _amount);
    }

    /// @notice 募集割当
    /// @dev オーナーのみ実行可能
    /// @param _address 割当先アドレス
    /// @param _amount 割当数量
    function allot(address _address, uint256 _amount)
        public
        onlyOwner()
    {
        applications[_address].allottedAmount = _amount;
        emit Allot(_address, _amount);
    }

    /// @notice 償還する
    /// @dev オーナーのみ実行可能
    function redeem()
        public
        onlyOwner()
    {
        isRedeemed = true;
        emit Redeem();
    }

    /// @notice 資産ロック先アドレスの認可
    /// @dev オーナーのみ実行可能
    /// @param _address 認可対象のアドレス
    /// @param _auth 認可状態（true:認可、false:未認可）
    function authorize(address _address, bool _auth)
        public
        onlyOwner()
    {
        authorizedAddress[_address] = _auth;
        emit Authorize(_address, _auth);
    }

    /// @notice ロック済み資産の参照
    /// @param _authorized_address 資産ロック先アドレス（認可済）
    /// @param _account_address 資産ロック対象アカウント
    /// @return ロック済み数量
    function lockedOf(address _authorized_address, address _account_address)
        public
        view
        returns (uint256)
    {
        return locked[_authorized_address][_account_address];
    }

    /// @notice 資産をロックする
    /// @param _target_address 資産をロックする先のアドレス
    /// @param _value ロックする数量
    function lock(address _target_address, uint256 _value)
        public
    {
        // ロック対象が認可済みアドレス、まはは発行者アドレスであることをチェック
        require(
            authorizedAddress[_target_address] == true ||
            _target_address == owner
        );

        // ロック数量が保有数量を上回っている場合、エラーを返す
        if (balanceOf(msg.sender) < _value) revert();

        // データ更新
        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        locked[_target_address][msg.sender] = lockedOf(_target_address, msg.sender).add(_value);

        emit Lock(msg.sender, _target_address, _value);
    }

    /// @notice 資産をアンロックする
    /// @dev 認可済みアドレスあるいは発行体のみ実行可能
    /// @param _account_address アンロック対象のアドレス
    /// @param _receive_address 受取アドレス
    function unlock(address _account_address, address _receive_address, uint256 _value)
        public
    {
        // msg.senderが認可済みアドレス、または発行者アドレスであることをチェック
        require(
            authorizedAddress[msg.sender] == true ||
            msg.sender == owner
        );

        // アンロック数量がロック数量を上回ってる場合、エラーを返す
        if (lockedOf(msg.sender, _account_address) < _value) revert();

        // データ更新
        locked[msg.sender][_account_address] = lockedOf(msg.sender, _account_address).sub(_value);
        balances[_receive_address] = balanceOf(_receive_address).add(_value);
        emit Unlock(_account_address, _receive_address, _value);
    }

    /// @notice 追加発行
    /// @dev 特定のアドレスの残高に対して、追加発行を行う
    /// @dev オーナーのみ実行可能
    /// @param _target_address 追加発行対象の残高を保有するアドレス
    /// @param _locked_address （任意）資産ロックアドレス
    /// @param _amount 追加発行数量
    function issueFrom(address _target_address, address _locked_address, uint256 _amount)
        public
        onlyOwner()
    {
        // locked_addressを指定した場合：ロック資産に対して追加発行を行う
        // locked_addressを指定しない場合：アカウントアドレスの残高に対して追加発行を行う
        if (_locked_address != address(0)) {
            // ロック資産の更新
            locked[_locked_address][_target_address] = lockedOf(_locked_address, _target_address).add(_amount);
            // 総発行数量の更新
            totalSupply = totalSupply.add(_amount);
        } else {
            // アカウント残高の更新
            balances[_target_address] = balanceOf(_target_address).add(_amount);
            // 総発行数量の更新
            totalSupply = totalSupply.add(_amount);
        }
        emit Issue(msg.sender, _target_address, _locked_address, _amount);
    }

    /// @notice 額面金額の更新
    /// @dev オーナーのみ実行可能
    /// @param _faceValue 更新後の額面金額
    function setFaceValue(uint256 _faceValue)
        public
        onlyOwner()
    {
        faceValue = _faceValue;
        emit ChangeFaceValue(_faceValue);
    }

    /// @notice 償還金額の更新
    /// @dev オーナーのみ実行可能
    /// @param _redemptionValue 更新後の償還金額
    function setRedemptionValue(uint256 _redemptionValue)
        public
        onlyOwner()
    {
        redemptionValue = _redemptionValue;
        emit ChangeRedemptionValue(_redemptionValue);
    }

}
