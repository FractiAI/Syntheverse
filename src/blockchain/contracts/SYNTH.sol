// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title SYNTH Token
 * @dev Internal accounting token for Syntheverse PoC system
 * Non-transferable between users, only mintable by approved contracts
 */
contract SYNTH is ERC20, Ownable, ReentrancyGuard {
    // Multi-metal contribution types
    enum Metal { GOLD, SILVER, COPPER }

    // Epoch phases
    enum Epoch { FOUNDER, PIONEER, COMMUNITY, ECOSYSTEM }

    // Contribution tracking
    struct Contribution {
        address contributor;
        Metal metal;
        Epoch epoch;
        uint256 amount;
        uint256 coherence;
        uint256 density;
        uint256 novelty;
        uint256 timestamp;
        string submissionHash;
    }

    // State variables
    mapping(address => uint256) public contributorBalances;
    mapping(address => Contribution[]) public contributions;
    mapping(string => bool) public processedHashes; // Prevent duplicate processing

    // Epoch configuration
    mapping(Epoch => uint256) public epochCaps;
    mapping(Epoch => uint256) public epochDistributed;

    // Events
    event ContributionMinted(
        address indexed contributor,
        Metal metal,
        Epoch epoch,
        uint256 amount,
        string submissionHash
    );

    event EpochCapUpdated(Epoch epoch, uint256 newCap);

    constructor() ERC20("Syntheverse SYNTH", "SYNTH") {
        // Initialize epoch caps (in wei)
        epochCaps[Epoch.FOUNDER] = 45_000_000_000_000 ether;     // 45T
        epochCaps[Epoch.PIONEER] = 22_500_000_000_000 ether;     // 22.5T
        epochCaps[Epoch.COMMUNITY] = 11_250_000_000_000 ether;   // 11.25T
        epochCaps[Epoch.ECOSYSTEM] = 11_250_000_000_000 ether;   // 11.25T
    }

    /**
     * @dev Mint SYNTH tokens for a validated contribution
     * @param contributor Address receiving the tokens
     * @param metal Contribution metal type
     * @param coherence Coherence score (0-10000)
     * @param density Density score (0-10000)
     * @param novelty Novelty score (0-10000)
     * @param submissionHash Unique submission identifier
     */
    function mintContribution(
        address contributor,
        Metal metal,
        uint256 coherence,
        uint256 density,
        uint256 novelty,
        string calldata submissionHash
    ) external onlyOwner nonReentrant {
        require(contributor != address(0), "Invalid contributor address");
        require(bytes(submissionHash).length > 0, "Empty submission hash");
        require(!processedHashes[submissionHash], "Submission already processed");

        // Calculate reward amount based on multi-metal evaluation
        uint256 rewardAmount = calculateReward(metal, coherence, density, novelty);
        require(rewardAmount > 0, "Invalid reward calculation");

        // Determine epoch based on density score
        Epoch epoch = determineEpoch(density);
        require(epochDistributed[epoch] + rewardAmount <= epochCaps[epoch], "Epoch cap exceeded");

        // Mark submission as processed
        processedHashes[submissionHash] = true;

        // Update epoch distribution
        epochDistributed[epoch] += rewardAmount;

        // Update contributor balance
        contributorBalances[contributor] += rewardAmount;

        // Record contribution
        contributions[contributor].push(Contribution({
            contributor: contributor,
            metal: metal,
            epoch: epoch,
            amount: rewardAmount,
            coherence: coherence,
            density: density,
            novelty: novelty,
            timestamp: block.timestamp,
            submissionHash: submissionHash
        }));

        // Mint tokens (internal accounting only)
        _mint(contributor, rewardAmount);

        emit ContributionMinted(contributor, metal, epoch, rewardAmount, submissionHash);
    }

    /**
     * @dev Calculate reward amount based on contribution quality
     * @param metal Contribution metal type
     * @param coherence Coherence score
     * @param density Density score
     * @param novelty Novelty score
     * @return rewardAmount in wei
     */
    function calculateReward(
        Metal metal,
        uint256 coherence,
        uint256 density,
        uint256 novelty
    ) public pure returns (uint256) {
        // Base reward calculation: (coherence + density + novelty) / 300 * baseMultiplier
        uint256 baseScore = (coherence + density + novelty) / 3; // Average score
        uint256 baseMultiplier;

        // Metal-based multipliers
        if (metal == Metal.GOLD) {
            baseMultiplier = 1000; // 10x base
        } else if (metal == Metal.SILVER) {
            baseMultiplier = 500;  // 5x base
        } else {
            baseMultiplier = 250;  // 2.5x base
        }

        // Calculate final reward
        uint256 rewardAmount = (baseScore * baseMultiplier * 1 ether) / 10000;

        // Cap maximum reward per contribution
        if (rewardAmount > 1000000 ether) {
            rewardAmount = 1000000 ether; // 1M SYNTH max per contribution
        }

        return rewardAmount;
    }

    /**
     * @dev Determine epoch based on density score
     * @param density Density score (0-10000)
     * @return epoch The determined epoch
     */
    function determineEpoch(uint256 density) public pure returns (Epoch) {
        if (density >= 8000) return Epoch.FOUNDER;
        if (density >= 5000) return Epoch.PIONEER;
        if (density >= 2500) return Epoch.COMMUNITY;
        return Epoch.ECOSYSTEM;
    }

    /**
     * @dev Get contributor statistics
     * @param contributor Contributor address
     * @return balance Current SYNTH balance
     * @return totalContributions Number of contributions
     */
    function getContributorStats(address contributor)
        external
        view
        returns (uint256 balance, uint256 totalContributions)
    {
        return (contributorBalances[contributor], contributions[contributor].length);
    }

    /**
     * @dev Get epoch statistics
     * @param epoch Epoch to query
     * @return distributed Amount distributed in this epoch
     * @return remainingCap Remaining capacity in this epoch
     */
    function getEpochStats(Epoch epoch)
        external
        view
        returns (uint256 distributed, uint256 remainingCap)
    {
        uint256 cap = epochCaps[epoch];
        uint256 distributedAmount = epochDistributed[epoch];
        return (distributedAmount, cap - distributedAmount);
    }

    /**
     * @dev Update epoch cap (owner only)
     * @param epoch Epoch to update
     * @param newCap New capacity limit
     */
    function updateEpochCap(Epoch epoch, uint256 newCap) external onlyOwner {
        epochCaps[epoch] = newCap;
        emit EpochCapUpdated(epoch, newCap);
    }

    /**
     * @dev Override transfer function to prevent user-to-user transfers
     * This is an internal accounting token only
     */
    function transfer(address, uint256) public pure override returns (bool) {
        revert("SYNTH tokens are not transferable between users");
    }

    function transferFrom(address, address, uint256) public pure override returns (bool) {
        revert("SYNTH tokens are not transferable between users");
    }
}
