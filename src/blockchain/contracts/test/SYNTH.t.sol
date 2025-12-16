// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "../src/SYNTH.sol";
import "../src/POCRegistry.sol";

contract SYNTHTest is Test {
    SYNTH public synth;
    POCRegistry public registry;

    address public owner = address(1);
    address public pocEvaluator = address(2);
    address public treasury = address(3);
    address public contributor = address(4);

    bytes32 public submissionHash = keccak256("test-submission");

    function setUp() public {
        vm.startPrank(owner);

        // Deploy SYNTH token
        synth = new SYNTH(pocEvaluator, treasury);

        // Deploy POC Registry
        registry = new POCRegistry(address(synth), pocEvaluator);

        vm.stopPrank();
    }

    function testInitialSetup() public {
        assertEq(synth.name(), "Syntheverse SYNTH");
        assertEq(synth.symbol(), "SYNTH");
        assertEq(synth.pocEvaluator(), pocEvaluator);
        assertEq(synth.treasury(), treasury);
        assertEq(uint256(synth.currentEpoch()), uint256(ISYNTH.Epoch.Founder));
    }

    function testContributionSubmission() public {
        vm.prank(pocEvaluator);

        registry.submitContribution(
            submissionHash,
            contributor,
            "Test Contribution",
            "scientific"
        );

        POCRegistry.Contribution memory contrib = registry.getContribution(submissionHash);
        assertEq(contrib.submissionHash, submissionHash);
        assertEq(contrib.contributor, contributor);
        assertEq(contrib.title, "Test Contribution");
        assertEq(contrib.category, "scientific");
    }

    function testFreeRegistration() public {
        // Submit contribution
        vm.prank(pocEvaluator);
        registry.submitContribution(
            submissionHash,
            contributor,
            "Test Contribution",
            "scientific"
        );

        // Record evaluation
        string[] memory metals = new string[](1);
        metals[0] = "Gold";

        vm.prank(pocEvaluator);
        registry.recordEvaluation(
            submissionHash,
            metals,
            8500, // coherence
            9000, // density
            8000, // novelty
            8500  // pocScore
        );

        // Check free registration
        uint256 fee = registry.getRegistrationFee(contributor);
        assertEq(fee, 0);

        // Register certificate (should be free)
        vm.prank(contributor);
        registry.registerCertificate{value: 0}(submissionHash);

        POCRegistry.Contribution memory contrib = registry.getContribution(submissionHash);
        assertTrue(contrib.registered);
        assertEq(contrib.registrationFee, 0);
    }

    function testPaidRegistration() public {
        // Submit 4 contributions to exceed free limit
        vm.startPrank(pocEvaluator);

        for (uint256 i = 0; i < 4; i++) {
            bytes32 hash = keccak256(abi.encodePacked("submission", i));
            registry.submitContribution(
                hash,
                contributor,
                string(abi.encodePacked("Contribution ", i)),
                "scientific"
            );

            // Record evaluation for qualification
            string[] memory metals = new string[](1);
            metals[0] = "Gold";

            registry.recordEvaluation(
                hash,
                metals,
                8500, 9000, 8000, 8500
            );
        }

        vm.stopPrank();

        // Check that 5th submission requires payment
        uint256 fee = registry.getRegistrationFee(contributor);
        assertEq(fee, 50 ether);

        // Register 4th certificate (should cost 50 ETH)
        bytes32 fourthHash = keccak256(abi.encodePacked("submission", uint256(3)));
        vm.prank(contributor);
        registry.registerCertificate{value: 50 ether}(fourthHash);

        POCRegistry.Contribution memory contrib = registry.getContribution(fourthHash);
        assertTrue(contrib.registered);
        assertEq(contrib.registrationFee, 50 ether);
    }

    function testTokenAllocation() public {
        // Submit and evaluate contribution
        vm.prank(pocEvaluator);
        registry.submitContribution(
            submissionHash,
            contributor,
            "Test Contribution",
            "scientific"
        );

        string[] memory metals = new string[](1);
        metals[0] = "Gold";

        vm.prank(pocEvaluator);
        registry.recordEvaluation(
            submissionHash,
            metals,
            8500, 9000, 8000, 8500
        );

        // Register certificate
        vm.prank(contributor);
        registry.registerCertificate{value: 0}(submissionHash);

        // Allocate tokens
        vm.prank(pocEvaluator);
        registry.allocateTokens(
            submissionHash,
            1000 ether, // 1000 SYNTH tokens
            0, // Founder epoch
            "Gold"
        );

        // Check token balance
        assertEq(synth.balanceOf(contributor), 1000 ether);
    }

    function testNonTransferable() public {
        // Mint some tokens
        vm.prank(pocEvaluator);
        registry.allocateTokens(
            submissionHash,
            1000 ether,
            0,
            "Gold"
        );

        // Try to transfer (should fail)
        vm.prank(contributor);
        vm.expectRevert("SYNTH tokens are non-transferable - internal accounting only");
        synth.transfer(address(5), 100 ether);
    }

    function testEmergencyFunctions() public {
        // Test owner functions
        vm.prank(owner);
        registry.setPOCEvaluator(address(5));
        assertEq(registry.pocEvaluator(), address(5));

        vm.prank(owner);
        synth.setPOCEvaluator(address(6));
        assertEq(synth.pocEvaluator(), address(6));
    }
}
