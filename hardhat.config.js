/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  networks: {
    hardhat: {
      gasPrice: 0,
      blockGasLimit: 800000000,
      hardfork: "berlin"
    },
  },
  solidity: "0.8.23",
};
