const { ethers } = require("hardhat");

module.exports = async ({ getNamedAccounts, deployments, network, getChainId }) => {
  const { deploy } = deployments;
  const { deployer } = await getNamedAccounts();

  console.log(`\n📦 Deploying POCRegistry on ${network.name}`);
  console.log(`Deployer: ${deployer}`);

  // Get SYNTH deployment
  const synthDeployment = await deployments.get("SYNTH");
  const synthAddress = synthDeployment.address;

  // Get constructor parameters
  const pocEvaluator = process.env.POC_EVALUATOR || deployer;

  console.log(`SYNTH Token: ${synthAddress}`);
  console.log(`PoC Evaluator: ${pocEvaluator}`);

  // Deploy POC Registry
  const pocRegistry = await deploy("POCRegistry", {
    from: deployer,
    args: [synthAddress, pocEvaluator],
    log: true,
    waitConfirmations: network.name === "hardhat" ? 1 : 2,
  });

  console.log(`✅ POCRegistry deployed at: ${pocRegistry.address}`);

  // Verify contract if not on local network
  if (network.name !== "hardhat" && network.name !== "localhost" && network.name !== "anvil") {
    console.log("⏳ Verifying contract on Etherscan...");
    try {
      await run("verify:verify", {
        address: pocRegistry.address,
        constructorArguments: [synthAddress, pocEvaluator],
      });
      console.log("✅ Contract verified!");
    } catch (error) {
      console.log("❌ Verification failed:", error.message);
    }
  }

  // Save deployment info
  const deploymentInfo = {
    network: network.name,
    chainId: network.config.chainId,
    synth: synthAddress,
    pocRegistry: pocRegistry.address,
    pocEvaluator,
    deployer,
    timestamp: new Date().toISOString(),
  };

  console.log("\n📋 Deployment Summary:");
  console.log(JSON.stringify(deploymentInfo, null, 2));

  return deploymentInfo;
};

module.exports.tags = ["POCRegistry", "all"];
module.exports.dependencies = ["SYNTH"];
