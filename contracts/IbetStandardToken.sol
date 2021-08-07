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

import "OpenZeppelin/openzeppelin-contracts@4.2.0/contracts/utils/math/SafeMath.sol";
import "./Ownable.sol";
import "../interfaces/ContractReceiver.sol";
import "../interfaces/IbetStandardTokenInterface.sol";


/// @title ibet Standard Token
contract IbetStandardToken is Ownable, IbetStandardTokenInterface {
    using SafeMath for uint;

    // [CONSTRUCTOR]
    /// @param _name 名称
    /// @param _symbol 略称
    /// @param _totalSupply 総発行数量
    /// @param _tradableExchange 取引コントラクト
    /// @param _contactInformation 問い合わせ先
    /// @param _privacyPolicy プライバシーポリシー
    constructor(
        string memory _name,
        string memory _symbol,
        uint256 _totalSupply,
        address _tradableExchange,
        string memory _contactInformation,
        string memory _privacyPolicy
    )
    {
        owner = msg.sender;
        name = _name;
        symbol = _symbol;
        totalSupply = _totalSupply;
        tradableExchange = _tradableExchange;
        balances[owner] = totalSupply;
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

        bytes memory empty;
        if (isContract(_to)) {
            return transferToContract(_to, _value, empty);
        }
        else {
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

}
