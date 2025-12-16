// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title PoC Registry
 * @dev Manages PoC contributions, evaluations, and certificate registrations
 * @notice Handles the core PoC contribution lifecycle on-chain
 */
contract POCRegistry is Ownable, ReentrancyGuard {
    // SYNTH token contract
    ISYNTH public synthToken;

    // PoC Evaluator role
    address public pocEvaluator;

    // Fee structure
    uint256 public constant REGISTRATION_FEE = 50 ether; // $50 in wei (for gas calculations)
    uint256 public constant FREE_SUBMISSIONS = 3; // First 3 submissions are free

    // Contribution structure
    struct Contribution {
        bytes32 submissionHash;
        address contributor;
        string title;
        string category;
        string[] metals; // Gold, Silver, Copper
        uint256 coherence;
        uint256 density;
        uint256 novelty;
        uint256 pocScore;
        uint256 timestamp;
        bool registered;
        uint256 registrationFee;
    }

    // State variables
    mapping(bytes32 => Contribution) public contributions;
    mapping(address => uint256) public contributorSubmissionCount;
    mapping(address => bytes32[]) public contributorSubmissions;
    bytes32[] public allContributions;

    // Events
    event ContributionSubmitted(bytes32 indexed submissionHash, address indexed contributor, string category);
    event ContributionEvaluated(bytes32 indexed submissionHash, string[] metals, uint256 pocScore);
    event CertificateRegistered(bytes32 indexed submissionHash, address indexed contributor, uint256 fee);

    // Modifiers
    modifier onlyPOCEvaluator() {
        require(msg.sender == pocEvaluator, "Only PoC evaluator can call this function");
        _;
    }

    modifier contributionExists(bytes32 submissionHash) {
        require(contributions[submissionHash].contributor != address(0), "Contribution does not exist");
        _;
    }

    /**
     * @dev Constructor
     * @param _synthToken Address of the SYNTH token contract
     * @param _pocEvaluator Address of the PoC evaluation system
     */
    constructor(address _synthToken, address _pocEvaluator) Ownable(_pocEvaluator) {
        require(_synthToken != address(0), "SYNTH token address cannot be zero");
        require(_pocEvaluator != address(0), "PoC evaluator address cannot be zero");

        synthToken = ISYNTH(_synthToken);
        pocEvaluator = _pocEvaluator;
    }

    /**
     * @dev Submit a new PoC contribution
     * @param submissionHash Unique hash of the contribution
     * @param contributor Contributor address
     * @param title Contribution title
     * @param category Contribution category (scientific/tech/alignment)
     */
    function submitContribution(
        bytes32 submissionHash,
        address contributor,
        string calldata title,
        string calldata category
    ) external onlyPOCEvaluator {
        require(contributions[submissionHash].contributor == address(0), "Contribution already exists");
        require(contributor != address(0), "Contributor cannot be zero address");

        contributions[submissionHash] = Contribution({
            submissionHash: submissionHash,
            contributor: contributor,
            title: title,
            category: category,
            metals: new string[](0),
            coherence: 0,
            density: 0,
            novelty: 0,
            pocScore: 0,
            timestamp: block.timestamp,
            registered: false,
            registrationFee: 0
        });

        contributorSubmissionCount[contributor]++;
        contributorSubmissions[contributor].push(submissionHash);
        allContributions.push(submissionHash);

        emit ContributionSubmitted(submissionHash, contributor, category);
    }

    /**
     * @dev Record evaluation results for a contribution
     * @param submissionHash Contribution hash
     * @param metals Awarded metals (Gold/Silver/Copper)
     * @param coherence Coherence score (0-10000)
     * @param density Density score (0-10000)
     * @param novelty Novelty score (0-10000)
     * @param pocScore Overall PoC score
     */
    function recordEvaluation(
        bytes32 submissionHash,
        string[] calldata metals,
        uint256 coherence,
        uint256 density,
        uint256 novelty,
        uint256 pocScore
    ) external onlyPOCEvaluator contributionExists(submissionHash) {
        Contribution storage contribution = contributions[submissionHash];

        // Clear existing metals array
        delete contribution.metals;

        // Copy metals from calldata to storage
        for (uint256 i = 0; i < metals.length; i++) {
            contribution.metals.push(metals[i]);
        }

        contribution.coherence = coherence;
        contribution.density = density;
        contribution.novelty = novelty;
        contribution.pocScore = pocScore;

        emit ContributionEvaluated(submissionHash, metals, pocScore);
    }

    /**
     * @dev Register a certificate for a qualified contribution
     * @param submissionHash Contribution hash to register
     */
    function registerCertificate(bytes32 submissionHash) external payable nonReentrant {
        Contribution storage contribution = contributions[submissionHash];
        require(contribution.contributor != address(0), "Contribution does not exist");
        require(contribution.metals.length > 0, "Contribution not qualified for registration");
        require(!contribution.registered, "Certificate already registered");
        require(contribution.contributor == msg.sender, "Only contributor can register certificate");

        // Calculate fee based on submission count
        uint256 submissionCount = contributorSubmissionCount[msg.sender];
        uint256 requiredFee = 0;

        if (submissionCount > FREE_SUBMISSIONS) {
            requiredFee = REGISTRATION_FEE;
        }

        require(msg.value >= requiredFee, "Insufficient registration fee");

        // Mark as registered
        contribution.registered = true;
        contribution.registrationFee = requiredFee;

        // Refund excess payment
        if (msg.value > requiredFee) {
            payable(msg.sender).transfer(msg.value - requiredFee);
        }

        // Allocate SYNTH tokens based on metals
        // This would be called by the PoC evaluator system
        // For now, we emit the event for off-chain processing

        emit CertificateRegistered(submissionHash, msg.sender, requiredFee);
    }

    /**
     * @dev Allocate SYNTH tokens for a registered contribution (called by PoC evaluator)
     * @param submissionHash Contribution hash
     * @param amount Amount of SYNTH to allocate
     * @param epoch Target epoch
     * @param primaryMetal Primary metal for the allocation
     */
    function allocateTokens(
        bytes32 submissionHash,
        uint256 amount,
        uint8 epoch,
        string calldata primaryMetal
    ) external onlyPOCEvaluator contributionExists(submissionHash) {
        Contribution storage contribution = contributions[submissionHash];
        require(contribution.registered, "Contribution not registered");

        // Call SYNTH token contract to allocate
        synthToken.allocatePOC(contribution.contributor, amount, ISYNTH.Epoch(epoch), primaryMetal);
    }

    /**
     * @dev Get registration fee for a contributor
     * @param contributor Contributor address
     * @return Fee amount in wei
     */
    function getRegistrationFee(address contributor) external view returns (uint256) {
        uint256 submissionCount = contributorSubmissionCount[contributor];
        return submissionCount <= FREE_SUBMISSIONS ? 0 : REGISTRATION_FEE;
    }

    /**
     * @dev Check if a contribution is qualified for registration
     * @param submissionHash Contribution hash
     * @return True if qualified
     */
    function isQualified(bytes32 submissionHash) external view returns (bool) {
        return contributions[submissionHash].metals.length > 0;
    }

    /**
     * @dev Get contribution details
     * @param submissionHash Contribution hash
     * @return Contribution struct
     */
    function getContribution(bytes32 submissionHash) external view returns (Contribution memory) {
        return contributions[submissionHash];
    }

    /**
     * @dev Get total number of contributions
     * @return Total count
     */
    function getTotalContributions() external view returns (uint256) {
        return allContributions.length;
    }

    /**
     * @dev Get contributor's submissions
     * @param contributor Contributor address
     * @return Array of submission hashes
     */
    function getContributorSubmissions(address contributor) external view returns (bytes32[] memory) {
        return contributorSubmissions[contributor];
    }

    /**
     * @dev Withdraw collected fees to treasury
     */
    function withdrawFees() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No fees to withdraw");

        payable(owner()).transfer(balance);
    }

    /**
     * @dev Update PoC evaluator address
     * @param newEvaluator New PoC evaluator address
     */
    function setPOCEvaluator(address newEvaluator) external onlyOwner {
        require(newEvaluator != address(0), "New evaluator cannot be zero address");
        pocEvaluator = newEvaluator;
    }

    /**
     * @dev Emergency pause (for future use)
     */
    function emergencyPause() external onlyOwner {
        // Implementation for emergency pause
    }
}

// Interface for SYNTH token
interface ISYNTH {
    enum Epoch { Founder, Pioneer, Community, Ecosystem }

    function allocatePOC(
        address recipient,
        uint256 amount,
        Epoch epoch,
        string calldata metal
    ) external;
}
