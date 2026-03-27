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
pragma solidity ^0.8.23;

import "./Errors.sol";

/// @title P256 Wallet (EIP-7951 precompile based)
/// @notice A minimal contract wallet that verifies secp256r1(P-256) signatures
///         through the EIP-7951-compatible precompile and executes transactions.
contract P256Wallet {
    // NOTE:
    // The precompile address follows the expected EIP-7951 deployment on ibet quorum.
    // If the chain uses a different address, this constant can be adjusted.
    address internal constant P256_VERIFY_PRECOMPILE =
        0x0000000000000000000000000000000000000100;

    uint256 public immutable pubKeyX;
    uint256 public immutable pubKeyY;

    uint256 public nonce;

    event Executed(
        address indexed target,
        uint256 value,
        bytes data,
        bytes returnData,
        uint256 nonce
    );

    constructor(uint256 _pubKeyX, uint256 _pubKeyY) {
        if (_pubKeyX == 0 || _pubKeyY == 0) {
            revert(ErrorCode.ERR_P256Wallet_constructor_630001);
        }
        pubKeyX = _pubKeyX;
        pubKeyY = _pubKeyY;
    }

    receive() external payable {}

    /// @notice Execute a transaction authorized by a P-256 signature.
    /// @param target Destination contract/account.
    /// @param value Native token amount to transfer.
    /// @param data Calldata for the call.
    /// @param sigR ECDSA signature r.
    /// @param sigS ECDSA signature s.
    /// @return returnData Raw return data from target call.
    function execute(
        address target,
        uint256 value,
        bytes calldata data,
        uint256 sigR,
        uint256 sigS
    ) external payable returns (bytes memory returnData) {
        bytes32 txHash = getTransactionHash(target, value, data, nonce);

        if (!_verify(txHash, sigR, sigS)) {
            revert(ErrorCode.ERR_P256Wallet_execute_630101);
        }

        uint256 currentNonce = nonce;
        nonce = currentNonce + 1;

        (bool success, bytes memory result) = target.call{value: value}(data);
        if (!success) {
            revert(ErrorCode.ERR_P256Wallet_execute_630102);
        }

        emit Executed(target, value, data, result, currentNonce);
        return result;
    }

    /// @notice Build the signed hash for execution authorization.
    function getTransactionHash(
        address target,
        uint256 value,
        bytes calldata data,
        uint256 _nonce
    ) public view returns (bytes32) {
        return
            keccak256(
                abi.encodePacked(
                    bytes1(0x19),
                    bytes1(0x01),
                    block.chainid,
                    address(this),
                    target,
                    value,
                    keccak256(data),
                    _nonce
                )
            );
    }

    /// @dev Calls EIP-7951-compatible precompile with input (hash, r, s, x, y).
    ///      The precompile is expected to return 32-byte boolean-style value.
    function _verify(
        bytes32 hash,
        uint256 sigR,
        uint256 sigS
    ) internal view returns (bool) {
        bytes memory input = abi.encode(hash, sigR, sigS, pubKeyX, pubKeyY);
        (bool success, bytes memory output) = P256_VERIFY_PRECOMPILE.staticcall(
            input
        );

        if (!success || output.length < 32) {
            return false;
        }

        return abi.decode(output, (uint256)) == 1;
    }
}
