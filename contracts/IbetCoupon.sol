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
import "../interfaces/ContractReceiver.sol";
import "../interfaces/IbetStandardTokenInterface.sol";


/// @title ibet Coupon Token
contract IbetCoupon is Ownable, IbetStandardTokenInterface {
    using SafeMath for uint;

    // 属性情報
    string public details; // 詳細
    string public returnDetails; // 特典詳細
    string public expirationDate; // 有効期限
    string public memo; // 補足情報
    bool public transferable; // 譲渡可否
    bool public initialOfferingStatus; // 新規募集ステータス（True：募集中、False：停止中）

    // 残高数量
    // account_address => balance
    mapping(address => uint256) public balances;

    // 使用済数量
    // account_address => used quantity
    mapping(address => uint) public useds;

    // クーポン画像
    // image class => url
    mapping(uint8 => string) public image_urls;

    // 募集申込
    // account_address => data
    mapping(address => string) public applications;

    // イベント:消費
    event Consume(address indexed consumer, uint balance, uint used, uint value);

    // イベント：募集申込
    event ApplyFor(address indexed accountAddress);

    // [CONSTRUCTOR]
    /// @param _name 名称
    /// @param _symbol 略称
    /// @param _totalSupply 総発行数量
    /// @param _tradableExchange 取引コントラクト
    /// @param _details 詳細
    /// @param _returnDetails 特典詳細
    /// @param _memo 補足情報
    /// @param _expirationDate 有効期限
    /// @param _transferable 譲渡可否
    /// @param _contactInformation 問い合わせ先
    /// @param _privacyPolicy プライバシーポリシー
    constructor(
        string memory _name,
        string memory _symbol,
        uint256 _totalSupply,
        address _tradableExchange,
        string memory _details,
        string memory _returnDetails,
        string memory _memo,
        string memory _expirationDate,
        bool _transferable,
        string memory _contactInformation,
        string memory _privacyPolicy
    )
    {
        owner = msg.sender;
        name = _name;
        symbol = _symbol;
        totalSupply = _totalSupply;
        tradableExchange = _tradableExchange;
        details = _details;
        returnDetails = _returnDetails;
        memo = _memo;
        expirationDate = _expirationDate;
        balances[owner] = totalSupply;
        transferable = _transferable;
        status = true;
        contactInformation = _contactInformation;
        privacyPolicy = _privacyPolicy;
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
        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        balances[_to] = balanceOf(_to).add(_value);
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
        // 譲渡しようとしている数量が残高を超えている場合、エラーを返す
        if (balanceOf(msg.sender) < _value) revert();
        if (msg.sender != tradableExchange) {
            // 譲渡可能なクーポンではない場合、エラーを返す
            require(transferable == true);
        }
        bytes memory empty;
        if (isContract(_to)) {
            return transferToContract(_to, _value, empty);
        }
        else {
            return transferToAddress(_to, _value, empty);
        }
    }

    /// @notice 強制移転
    /// @dev オーナーのみ実行可能
    /// @param _from 移転元アドレス
    /// @param _to 移転先アドレス
    /// @param _value 移転数量
    /// @return 処理結果
    function transferFrom(address _from, address _to, uint _value)
        public
        onlyOwner()
        returns (bool)
    {
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

    /// @notice クーポンの消費
    /// @param _value 消費数量
    function consume(uint _value)
        public
    {
        // 消費しようとしている数量が残高を超えている場合、エラーを返す
        if (balanceOf(msg.sender) < _value) revert();
        // 無効化されている場合、エラーを返す
        if (status == false) revert();

        // 残高数量を更新する
        balances[msg.sender] = balanceOf(msg.sender).sub(_value);
        // 使用済数量を更新する
        useds[msg.sender] = usedOf(msg.sender).add(_value);

        emit Consume(msg.sender, balances[msg.sender], useds[msg.sender], _value);
    }

    /// @notice 追加発行
    /// @dev オーナーのみ実行可能
    /// @param _value 追加発行数量
    function issue(uint _value)
        public
        onlyOwner()
    {
        totalSupply = totalSupply.add(_value);
        balances[owner] = balanceOf(owner).add(_value);
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

    /// @notice 消費済数量の参照
    /// @param _owner 保有者のアドレス
    /// @return 消費済数量
    function usedOf(address _owner)
        public
        view
        returns (uint)
    {
        return useds[_owner];
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

    /// @notice 詳細の更新
    /// @dev オーナーのみ実行可能
    /// @param _details クーポン詳細情報
    function setDetails(string memory _details)
        public
        onlyOwner()
    {
        details = _details;
    }

    /// @notice 特典詳細の更新
    /// @dev オーナーのみ実行可能
    /// @param _returnDetails 特典詳細
    function setReturnDetails(string memory _returnDetails)
        public
        onlyOwner()
    {
        returnDetails = _returnDetails;
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

    /// @notice 有効期限の更新
    /// @dev オーナーのみ実行可能
    /// @param _expirationDate 有効期限
    function setExpirationDate(string memory _expirationDate)
        public
        onlyOwner()
    {
        expirationDate = _expirationDate;
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

    /// @notice 譲渡可否の更新
    /// @dev オーナーのみ実行可能
    /// @param _transferable 譲渡可否
    function setTransferable(bool _transferable)
        public
        onlyOwner()
    {
        transferable = _transferable;
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

    /// @notice 新規募集ステータスの更新
    /// @dev オーナーのみ実行可能
    /// @param _status 募集ステータス
    function setInitialOfferingStatus(bool _status)
        public
        onlyOwner()
    {
        initialOfferingStatus = _status;
    }

    /// @notice 募集申込
    /// @param _data 申込付与情報
    function applyForOffering(string memory _data)
        public
    {
        // 申込ステータスが停止中の場合、エラーを返す
        require(initialOfferingStatus == true);
        applications[msg.sender] = _data;
        emit ApplyFor(msg.sender);
    }

}
