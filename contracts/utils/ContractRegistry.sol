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


/// @title Contract Registry
contract ContractRegistry is Ownable {

    // レジストリ
    struct Registry {
        string contractType;
        address contractOwner;
    }

    // contract address => Registry
    mapping(address => Registry) private registry;

    // イベント：レジストリ登録
    event Registered(
        address indexed contractAddress,
        string contractType,
        address contractOwner
    );

    /// @notice レジストリ登録
    /// @param _contractAddress コントラクトアドレス
    /// @param _contractType コントラクト型
    function register(
        address _contractAddress,
        string memory _contractType
    )
        public
        returns (bool)
    {
        // チェック：コントラクトアドレスであること
        uint extCodeLength;
        assembly {
            extCodeLength := extcodesize(_contractAddress)
        }
        require(
            extCodeLength > 0,
            ErrorCode.ERR_ContractRegistry_register_600001
        );

        // チェック：msg.senderがコントラクトのオーナーであること
        require(
            msg.sender == Ownable(_contractAddress).owner(),
            ErrorCode.ERR_ContractRegistry_register_600002
        );

        registry[_contractAddress].contractType = _contractType;
        registry[_contractAddress].contractOwner = msg.sender;

        emit Registered(
            _contractAddress,
            _contractType,
            msg.sender
        );

        return true;
    }

    /// @notice レジストリ情報を取得
    /// @param _contractAddress コントラクトアドレス
    /// @return contractType コントラクト型
    /// @return contractOwner コントラクトオーナー
    function getRegistry(address _contractAddress)
        public
        view
        returns (
            string memory contractType,
            address contractOwner
        )
    {
        contractType = registry[_contractAddress].contractType;
        contractOwner = registry[_contractAddress].contractOwner;
    }

}
