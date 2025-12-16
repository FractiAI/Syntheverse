// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title SYNTH Token
 * @dev Internal accounting token for Syntheverse PoC system
 * @notice This token has no external monetary value and is used only for internal ecosystem accounting
 */
contract SYNTH is ERC20, Ownable, ReentrancyGuard {
    // PoC system roles
    address public pocEvaluator;
    address public treasury;

    // Epoch management
    enum Epoch { Founder, Pioneer, Community, Ecosystem }
    Epoch public currentEpoch;

    // Epoch balances (internal accounting)
    mapping(Epoch => uint256) public epochBalances;

    // Total supply: 90 trillion SYNTH
    uint256 public constant MAX_SUPPLY = 90_000_000_000_000 * 10**18;

    // Events
    event TokensAllocated(address indexed recipient, uint256 amount, Epoch epoch, string metal);
    event EpochTransition(Epoch previousEpoch, Epoch newEpoch);
    event POCContribution(address indexed contributor, uint256 amount, string metal);

    // Modifiers
    modifier onlyPOCEvaluator() {
        require(msg.sender == pocEvaluator, "Only PoC evaluator can call this function");
        _;
    }

    modifier validEpoch(Epoch _epoch) {
        require(uint8(_epoch) <= uint8(Epoch.Ecosystem), "Invalid epoch");
        _;
    }

    /**
     * @dev Constructor
     * @param _pocEvaluator Address of the PoC evaluation system
     * @param _treasury Address of the treasury for fee collection
     */
    constructor(
        address _pocEvaluator,
        address _treasury
    ) ERC20("Syntheverse SYNTH", "SYNTH") Ownable(_pocEvaluator) {
        require(_pocEvaluator != address(0), "PoC evaluator cannot be zero address");
        require(_treasury != address(0), "Treasury cannot be zero address");

        pocEvaluator = _pocEvaluator;
        treasury = _treasury;
        currentEpoch = Epoch.Founder;

        // Initialize epoch balances (Founder gets all initially)
        epochBalances[Epoch.Founder] = MAX_SUPPLY;
    }

    /**
     * @dev Allocate SYNTH tokens for PoC contributions
     * @param recipient Contributor address
     * @param amount Amount of SYNTH to allocate
     * @param epoch Target epoch for allocation
     * @param metal Metal type (Gold/Silver/Copper)
     */
    function allocatePOC(
        address recipient,
        uint256 amount,
        Epoch epoch,
        string calldata metal
    ) external onlyPOCEvaluator validEpoch(epoch) nonReentrant {
        require(recipient != address(0), "Cannot allocate to zero address");
        require(amount > 0, "Amount must be greater than zero");
        require(epochBalances[epoch] >= amount, "Insufficient epoch balance");

        // Update epoch balance
        epochBalances[epoch] -= amount;

        // Mint tokens to recipient
        _mint(recipient, amount);

        emit TokensAllocated(recipient, amount, epoch, metal);
        emit POCContribution(recipient, amount, metal);
    }

    /**
     * @dev Get current epoch balance
     * @param epoch Epoch to query
     * @return Balance of the epoch
     */
    function getEpochBalance(Epoch epoch) external view returns (uint256) {
        return epochBalances[epoch];
    }

    /**
     * @dev Transition to next epoch (only owner)
     */
    function transitionEpoch() external onlyOwner {
        require(uint8(currentEpoch) < uint8(Epoch.Ecosystem), "Already at final epoch");

        Epoch previousEpoch = currentEpoch;
        currentEpoch = Epoch(uint8(currentEpoch) + 1);

        emit EpochTransition(previousEpoch, currentEpoch);
    }

    /**
     * @dev Update PoC evaluator address (only owner)
     * @param newEvaluator New PoC evaluator address
     */
    function setPOCEvaluator(address newEvaluator) external onlyOwner {
        require(newEvaluator != address(0), "New evaluator cannot be zero address");
        pocEvaluator = newEvaluator;
    }

    /**
     * @dev Update treasury address (only owner)
     * @param newTreasury New treasury address
     */
    function setTreasury(address newTreasury) external onlyOwner {
        require(newTreasury != address(0), "New treasury cannot be zero address");
        treasury = newTreasury;
    }

    /**
     * @dev Emergency withdraw function (only owner)
     * @notice Currently disabled for security reasons
     */
    function emergencyWithdraw(address /* tokenAddress */, uint256 /* amount */) external onlyOwner {
        // Emergency withdraw functionality - currently disabled for security
        // This would be used for withdrawing accidentally sent tokens
        // Implementation depends on token interface
        revert("Emergency withdraw not implemented");
    }

    /**
     * @dev Burn tokens (for future deflationary mechanisms)
     * @param amount Amount to burn
     */
    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }

    /**
     * @dev Override ERC20 transfer to add restrictions
     * @notice SYNTH tokens are non-transferable in the current implementation
     * @dev This prevents external trading and maintains internal accounting only
     */
    function transfer(address, uint256) public pure override returns (bool) {
        revert("SYNTH tokens are non-transferable - internal accounting only");
    }

    /**
     * @dev Override ERC20 transferFrom to add restrictions
     */
    function transferFrom(address, address, uint256) public pure override returns (bool) {
        revert("SYNTH tokens are non-transferable - internal accounting only");
    }

    /**
     * @dev Override ERC20 approve to add restrictions
     */
    function approve(address, uint256) public pure override returns (bool) {
        revert("SYNTH tokens are non-transferable - internal accounting only");
    }
}
