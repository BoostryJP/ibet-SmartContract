/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  networks: {
    hardhat: {
      chainId: 2017,
      gasPrice: 0,
      blockGasLimit: 800000000,
      hardfork: "berlin",
      throwOnTransactionFailures: false,
      throwOnCallFailures: false
    },
  },
  solidity: "0.8.23",
};
