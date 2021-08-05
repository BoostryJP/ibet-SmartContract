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

import "./Ownable.sol";
import "./ExchangeStorage.sol";
import "../interfaces/ContractReceiver.sol";


/// @title DEX for Unit Test
contract MockExchange is Ownable, ContractReceiver {

    // ---------------------------------------------------------------
    // Constructor
    // ---------------------------------------------------------------
    address public storageAddress;

    // [CONSTRUCTOR]
    /// @param _storageAddress ExchangeStorageコントラクトアドレス
    constructor(address _storageAddress)
    {
        storageAddress = _storageAddress;
    }

    /// @notice 残高参照
    /// @param _account アカウントアドレス
    /// @param _token トークンアドレス
    /// @return 残高数量
    function balanceOf(address _account, address _token)
        public
        view
        returns (uint256)
    {
        return ExchangeStorage(storageAddress).getBalance(
            _account,
            _token
        );
    }

    /// @notice 残高数量更新
    /// @param _account アカウントアドレス
    /// @param _token トークンアドレス
    /// @param _value 更新後の残高数量
    /// @return 処理結果
    function setBalance(address _account, address _token, uint256 _value)
        private
        returns (bool)
    {
        return ExchangeStorage(storageAddress).setBalance(
            _account,
            _token,
            _value
        );
    }

    /// @notice Deposit Handler：デポジット処理
    /// @param _from アカウントアドレス：残高を保有するアドレス
    /// @param _value デポジット数量
    function tokenFallback(address _from, uint _value, bytes memory /*_data*/)
        public
        override
    {
        setBalance(
            _from,
            msg.sender,
            balanceOf(_from, msg.sender) + _value
        );
    }

}
