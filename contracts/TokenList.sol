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


/// @title Token Registry
contract TokenList is Ownable {

    // トークン情報
    struct Token {
        address token_address; // トークンアドレス
        string token_template; // トークン仕様
        address owner_address; // トークンのオーナー
    }

    // トークン情報
    // token address => Token
    mapping(address => Token) tokens;

    // トークンリスト
    Token[] token_list;

    // イベント：登録
    event Register(
        address indexed token_address,
        string token_template,
        address owner_address
    );

    /// @notice トークン登録
    /// @param _token_address トークンアドレス
    /// @param _token_template トークン仕様
    function register(address _token_address, string memory _token_template)
        public
    {
        require(tokens[_token_address].token_address == 0x0000000000000000000000000000000000000000);
        require(Ownable(_token_address).owner() == msg.sender);
        tokens[_token_address].token_address = _token_address;
        tokens[_token_address].token_template = _token_template;
        tokens[_token_address].owner_address = msg.sender;
        token_list.push(Token({
            token_address: _token_address,
            token_template: _token_template,
            owner_address: msg.sender
        }));
        emit Register(_token_address, _token_template, msg.sender);
    }

    /// @notice オーナー変更登録
    /// @param _token_address トークンアドレス
    /// @param _new_owner_address 新しいオーナーアドレス
    function changeOwner(address _token_address, address _new_owner_address)
        public
    {
        require(tokens[_token_address].token_address != 0x0000000000000000000000000000000000000000);
        require(tokens[_token_address].owner_address == msg.sender);
        tokens[_token_address].owner_address = _new_owner_address;
        for (uint i = 0; i < token_list.length; i++) {
            if (token_list[i].token_address == _token_address) {
                token_list[i].owner_address = _new_owner_address;
            }
        }
    }

    /// @notice オーナーアドレスの参照
    /// @param _token_address トークンアドレス
    /// @return issuer_address オーナーアドレス
    function getOwnerAddress(address _token_address)
        public
        view
        returns (address issuer_address)
    {
        issuer_address = tokens[_token_address].owner_address;
    }

    /// @notice トークンリストのリスト長取得
    /// @return length リスト長
    function getListLength()
        public
        view
        returns (uint length)
    {
        length = token_list.length;
    }

    /// @notice リスト番号を指定してトークン情報を取得
    /// @return token_address トークンアドレス
    /// @return token_template トークン仕様
    /// @return owner_address オーナーアドレス
    function getTokenByNum(uint _num)
        public
        view
        returns (
            address token_address,
            string memory token_template,
            address owner_address
        )
    {
        token_address = token_list[_num].token_address;
        token_template = token_list[_num].token_template;
        owner_address = token_list[_num].owner_address;
    }

    /// @notice トークンアドレスを指定してトークン情報を取得
    /// @return token_address トークンアドレス
    /// @return token_template トークン仕様
    /// @return owner_address オーナーアドレス
    function getTokenByAddress(address _token_address)
        public
        view
        returns (
            address token_address,
            string memory token_template,
            address owner_address
        )
    {
        token_address = tokens[_token_address].token_address;
        token_template = tokens[_token_address].token_template;
        owner_address = tokens[_token_address].owner_address;
    }

}
