/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  networks: {
    hardhat: {
      chainId: 2017,
      blockGasLimit: 16777216,
      hardfork: "osaka",
      gasPrice: 0,
      initialBaseFeePerGas: 0,
      throwOnTransactionFailures: false,
      throwOnCallFailures: false,
      allowBlocksWithSameTimestamp: true
    },
  },
  solidity: "0.8.23",
};
