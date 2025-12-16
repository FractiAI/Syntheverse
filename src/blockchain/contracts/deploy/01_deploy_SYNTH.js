import { ethers } from "hardhat";

export default async ({ getNamedAccounts, deployments, network }) => {
  const { deploy } = deployments;
  const { deployer } = await getNamedAccounts();

  console.log(`\n📦 Deploying SYNTH Token on ${network.name}`);
  console.log(`Deployer: ${deployer}`);

  // Get constructor parameters
  const pocEvaluator = process.env.POC_EVALUATOR || deployer;
  const treasury = process.env.TREASURY || deployer;

  console.log(`PoC Evaluator: ${pocEvaluator}`);
  console.log(`Treasury: ${treasury}`);

  // Deploy SYNTH token
  const synth = await deploy("SYNTH", {
    from: deployer,
    args: [pocEvaluator, treasury],
    log: true,
    waitConfirmations: network.name === "hardhat" ? 1 : 2,
  });

  console.log(`✅ SYNTH deployed at: ${synth.address}`);

  // Verify contract if not on local network
  if (network.name !== "hardhat" && network.name !== "localhost" && network.name !== "anvil") {
    console.log("⏳ Verifying contract on Etherscan...");
    try {
      await run("verify:verify", {
        address: synth.address,
        constructorArguments: [pocEvaluator, treasury],
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
    synth: synth.address,
    pocEvaluator,
    treasury,
    deployer,
    timestamp: new Date().toISOString(),
  };

  console.log("\n📋 Deployment Summary:");
  console.log(JSON.stringify(deploymentInfo, null, 2));

  return deploymentInfo;
};

export const tags = ["SYNTH", "all"];
