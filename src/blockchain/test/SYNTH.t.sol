// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "../contracts/SYNTH.sol";

contract SYNTHTest is Test {
    SYNTH public synth;

    address public owner = address(1);
    address public contributor = address(2);
    address public contributor2 = address(3);

    function setUp() public {
        vm.prank(owner);
        synth = new SYNTH();
    }

    function testInitialSetup() public {
        assertEq(synth.name(), "Syntheverse SYNTH");
        assertEq(synth.symbol(), "SYNTH");
        assertEq(synth.owner(), owner);
    }

    function testMintContribution() public {
        vm.prank(owner);

        synth.mintContribution(
            contributor,
            SYNTH.Metal.GOLD,
            8500, // coherence
            9000, // density
            8000, // novelty
            "test-hash-1"
        );

        // Check balance
        assertEq(synth.balanceOf(contributor), 7650000000000000000000); // Calculated reward
        assertEq(synth.processedHashes("test-hash-1"), true);

        // Check contributor stats
        (uint256 balance, uint256 totalContributions) = synth.getContributorStats(contributor);
        assertEq(balance, 7650000000000000000000);
        assertEq(totalContributions, 1);
    }

    function testDuplicateSubmissionRejected() public {
        vm.startPrank(owner);

        synth.mintContribution(
            contributor,
            SYNTH.Metal.SILVER,
            7000, 7000, 7000,
            "duplicate-hash"
        );

        vm.expectRevert("Submission already processed");
        synth.mintContribution(
            contributor2,
            SYNTH.Metal.COPPER,
            6000, 6000, 6000,
            "duplicate-hash"
        );

        vm.stopPrank();
    }

    function testEpochDetermination() public {
        // High density = Founder epoch
        assertEq(uint(synth.determineEpoch(9000)), uint(SYNTH.Epoch.FOUNDER));

        // Medium density = Pioneer epoch
        assertEq(uint(synth.determineEpoch(6000)), uint(SYNTH.Epoch.PIONEER));

        // Low density = Community epoch
        assertEq(uint(synth.determineEpoch(3000)), uint(SYNTH.Epoch.COMMUNITY));

        // Very low density = Ecosystem epoch
        assertEq(uint(synth.determineEpoch(1000)), uint(SYNTH.Epoch.ECOSYSTEM));
    }

    function testRewardCalculation() public {
        // Gold metal with high scores
        uint256 goldReward = synth.calculateReward(
            SYNTH.Metal.GOLD,
            8000, 8000, 8000
        );
        assertEq(goldReward, 6400000000000000000000); // 6400 * 10^18

        // Silver metal with medium scores
        uint256 silverReward = synth.calculateReward(
            SYNTH.Metal.SILVER,
            6000, 6000, 6000
        );
        assertEq(silverReward, 1800000000000000000000); // 1800 * 10^18

        // Copper metal with low scores
        uint256 copperReward = synth.calculateReward(
            SYNTH.Metal.COPPER,
            4000, 4000, 4000
        );
        assertEq(copperReward, 600000000000000000000); // 600 * 10^18
    }

    function testTransferDisabled() public {
        vm.prank(owner);
        synth.mintContribution(
            contributor,
            SYNTH.Metal.COPPER,
            5000, 5000, 5000,
            "transfer-test-hash"
        );

        vm.expectRevert("SYNTH tokens are not transferable between users");
        vm.prank(contributor);
        synth.transfer(contributor2, 1000);
    }

    function testEpochCapEnforcement() public {
        vm.startPrank(owner);

        // Set a very low cap for testing
        synth.updateEpochCap(SYNTH.Epoch.FOUNDER, 1000 ether);

        // First contribution should work
        synth.mintContribution(
            contributor,
            SYNTH.Metal.GOLD,
            9000, 9000, 9000, // High density = Founder epoch
            "cap-test-1"
        );

        // Second contribution should fail due to cap
        vm.expectRevert("Epoch cap exceeded");
        synth.mintContribution(
            contributor2,
            SYNTH.Metal.GOLD,
            9000, 9000, 9000,
            "cap-test-2"
        );

        vm.stopPrank();
    }
}
