// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Script.sol";
import "../src/SYNTH.sol";
import "../src/POCRegistry.sol";

contract Deploy is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");

        vm.startBroadcast(deployerPrivateKey);

        // Deploy SYNTH token
        // Note: In production, these would be controlled by the Syntheverse system
        address pocEvaluator = vm.envOr("POC_EVALUATOR", address(0x1234567890123456789012345678901234567890));
        address treasury = vm.envOr("TREASURY", address(0x0987654321098765432109876543210987654321));

        SYNTH synth = new SYNTH(pocEvaluator, treasury);
        console.log("SYNTH deployed at:", address(synth));

        // Deploy POC Registry
        POCRegistry registry = new POCRegistry(address(synth), pocEvaluator);
        console.log("POCRegistry deployed at:", address(registry));

        // Transfer ownership to multisig or governance (in production)
        // synth.transferOwnership(governanceAddress);
        // registry.transferOwnership(governanceAddress);

        vm.stopBroadcast();

        // Log deployment information
        console.log("=== Deployment Summary ===");
        console.log("Network:", block.chainid);
        console.log("SYNTH Token:", address(synth));
        console.log("POC Registry:", address(registry));
        console.log("PoC Evaluator:", pocEvaluator);
        console.log("Treasury:", treasury);
        console.log("Deployer:", vm.addr(deployerPrivateKey));
    }
}
