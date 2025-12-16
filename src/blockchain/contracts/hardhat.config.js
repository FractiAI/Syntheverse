import "@nomicfoundation/hardhat-ethers";
import "@nomicfoundation/hardhat-chai-matchers";

/**
 * @type import('hardhat/config').HardhatUserConfig
 */
const config = {
  solidity: "0.8.19",
  paths: {
    sources: "./src",
    tests: "./test/hardhat",
  },
};

export default config;
