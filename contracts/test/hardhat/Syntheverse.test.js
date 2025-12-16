import { expect } from "chai";
import { ethers } from "hardhat";

describe("Syntheverse PoC System", function () {
  let SYNTH, POCRegistry;
  let synth, pocRegistry;
  let owner, pocEvaluator, treasury, contributor1, contributor2;
  let submissionHash1, submissionHash2, submissionHash3, submissionHash4;

  beforeEach(async function () {
    // Get signers
    [owner, pocEvaluator, treasury, contributor1, contributor2] = await ethers.getSigners();

    // Deploy SYNTH token
    SYNTH = await ethers.getContractFactory("SYNTH");
    synth = await SYNTH.deploy(pocEvaluator.address, treasury.address);
    await synth.deployed();

    // Deploy POC Registry
    POCRegistry = await ethers.getContractFactory("POCRegistry");
    pocRegistry = await POCRegistry.deploy(synth.address, pocEvaluator.address);
    await pocRegistry.deployed();

    // Set up test data
    submissionHash1 = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("contribution-1"));
    submissionHash2 = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("contribution-2"));
    submissionHash3 = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("contribution-3"));
    submissionHash4 = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("contribution-4"));
  });

  describe("SYNTH Token", function () {
    it("Should initialize correctly", async function () {
      expect(await synth.name()).to.equal("Syntheverse SYNTH");
      expect(await synth.symbol()).to.equal("SYNTH");
      expect(await synth.pocEvaluator()).to.equal(pocEvaluator.address);
      expect(await synth.treasury()).to.equal(treasury.address);
      expect(await synth.currentEpoch()).to.equal(0); // Founder epoch
    });

    it("Should have correct total supply", async function () {
      const expectedSupply = ethers.utils.parseEther("90000000000000"); // 90 trillion
      expect(await synth.totalSupply()).to.equal(0); // No tokens minted initially
    });

    it("Should not allow direct transfers", async function () {
      await expect(
        synth.transfer(contributor1.address, 1000)
      ).to.be.revertedWith("SYNTH tokens are non-transferable - internal accounting only");
    });

    it("Should not allow approvals", async function () {
      await expect(
        synth.approve(contributor1.address, 1000)
      ).to.be.revertedWith("SYNTH tokens are non-transferable - internal accounting only");
    });

    it("Should allow owner to transition epochs", async function () {
      expect(await synth.currentEpoch()).to.equal(0);
      await synth.transitionEpoch();
      expect(await synth.currentEpoch()).to.equal(1);
    });
  });

  describe("POC Registry - Free Registrations", function () {
    beforeEach(async function () {
      // Submit first contribution
      await pocRegistry.connect(pocEvaluator).submitContribution(
        submissionHash1,
        contributor1.address,
        "First Contribution",
        "scientific"
      );

      // Record evaluation
      const metals = ["Gold"];
      await pocRegistry.connect(pocEvaluator).recordEvaluation(
        submissionHash1,
        metals,
        8500, 9000, 8000, 8500
      );
    });

    it("Should allow free registration for first submission", async function () {
      const fee = await pocRegistry.getRegistrationFee(contributor1.address);
      expect(fee).to.equal(0);

      // Register without payment
      await pocRegistry.connect(contributor1).registerCertificate(submissionHash1);

      const contribution = await pocRegistry.getContribution(submissionHash1);
      expect(contribution.registered).to.be.true;
      expect(contribution.registrationFee).to.equal(0);
    });

    it("Should allow free registration for second submission", async function () {
      // Register first
      await pocRegistry.connect(contributor1).registerCertificate(submissionHash1);

      // Submit second
      await pocRegistry.connect(pocEvaluator).submitContribution(
        submissionHash2,
        contributor1.address,
        "Second Contribution",
        "technological"
      );

      const metals = ["Silver"];
      await pocRegistry.connect(pocEvaluator).recordEvaluation(
        submissionHash2,
        metals,
        7500, 8500, 7000, 7800
      );

      const fee = await pocRegistry.getRegistrationFee(contributor1.address);
      expect(fee).to.equal(0);

      await pocRegistry.connect(contributor1).registerCertificate(submissionHash2);

      const contribution = await pocRegistry.getContribution(submissionHash2);
      expect(contribution.registered).to.be.true;
    });

    it("Should allow free registration for third submission", async function () {
      // Register first two
      await pocRegistry.connect(contributor1).registerCertificate(submissionHash1);

      await pocRegistry.connect(pocEvaluator).submitContribution(
        submissionHash2,
        contributor1.address,
        "Second Contribution",
        "technological"
      );
      await pocRegistry.connect(pocEvaluator).recordEvaluation(
        submissionHash2,
        ["Silver"],
        7500, 8500, 7000, 7800
      );
      await pocRegistry.connect(contributor1).registerCertificate(submissionHash2);

      // Submit third
      await pocRegistry.connect(pocEvaluator).submitContribution(
        submissionHash3,
        contributor1.address,
        "Third Contribution",
        "alignment"
      );

      const metals = ["Copper"];
      await pocRegistry.connect(pocEvaluator).recordEvaluation(
        submissionHash3,
        metals,
        6500, 7500, 6000, 6800
      );

      const fee = await pocRegistry.getRegistrationFee(contributor1.address);
      expect(fee).to.equal(0);

      await pocRegistry.connect(contributor1).registerCertificate(submissionHash3);

      const contribution = await pocRegistry.getContribution(submissionHash3);
      expect(contribution.registered).to.be.true;
    });
  });

  describe("POC Registry - Paid Registrations", function () {
    beforeEach(async function () {
      // Submit and register three free contributions
      for (let i = 0; i < 3; i++) {
        const hash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes(`contribution-${i}`));
        await pocRegistry.connect(pocEvaluator).submitContribution(
          hash,
          contributor1.address,
          `Contribution ${i}`,
          "scientific"
        );

        await pocRegistry.connect(pocEvaluator).recordEvaluation(
          hash,
          ["Gold"],
          8500, 9000, 8000, 8500
        );

        await pocRegistry.connect(contributor1).registerCertificate(hash);
      }
    });

    it("Should require payment for fourth submission", async function () {
      // Submit fourth contribution
      await pocRegistry.connect(pocEvaluator).submitContribution(
        submissionHash4,
        contributor1.address,
        "Fourth Contribution",
        "scientific"
      );

      await pocRegistry.connect(pocEvaluator).recordEvaluation(
        submissionHash4,
        ["Gold"],
        8500, 9000, 8000, 8500
      );

      const fee = await pocRegistry.getRegistrationFee(contributor1.address);
      expect(fee).to.equal(ethers.utils.parseEther("50")); // $50

      // Should revert without payment
      await expect(
        pocRegistry.connect(contributor1).registerCertificate(submissionHash4)
      ).to.be.revertedWith("Insufficient registration fee");

      // Should succeed with payment
      await pocRegistry.connect(contributor1).registerCertificate(submissionHash4, {
        value: ethers.utils.parseEther("50")
      });

      const contribution = await pocRegistry.getContribution(submissionHash4);
      expect(contribution.registered).to.be.true;
      expect(contribution.registrationFee).to.equal(ethers.utils.parseEther("50"));
    });

    it("Should refund excess payment", async function () {
      // Submit fourth contribution
      await pocRegistry.connect(pocEvaluator).submitContribution(
        submissionHash4,
        contributor1.address,
        "Fourth Contribution",
        "scientific"
      );

      await pocRegistry.connect(pocEvaluator).recordEvaluation(
        submissionHash4,
        ["Gold"],
        8500, 9000, 8000, 8500
      );

      const initialBalance = await contributor1.getBalance();

      // Pay more than required
      const tx = await pocRegistry.connect(contributor1).registerCertificate(submissionHash4, {
        value: ethers.utils.parseEther("75") // Pay $75, need $50
      });

      const receipt = await tx.wait();
      const gasCost = receipt.gasUsed.mul(receipt.effectiveGasPrice);
      const finalBalance = await contributor1.getBalance();

      // Should have been charged $50 + gas
      const expectedBalance = initialBalance.sub(ethers.utils.parseEther("50")).sub(gasCost);
      expect(finalBalance).to.equal(expectedBalance);
    });
  });

  describe("Token Allocation", function () {
    beforeEach(async function () {
      // Submit and register contribution
      await pocRegistry.connect(pocEvaluator).submitContribution(
        submissionHash1,
        contributor1.address,
        "Test Contribution",
        "scientific"
      );

      await pocRegistry.connect(pocEvaluator).recordEvaluation(
        submissionHash1,
        ["Gold"],
        8500, 9000, 8000, 8500
      );

      await pocRegistry.connect(contributor1).registerCertificate(submissionHash1);
    });

    it("Should allocate SYNTH tokens correctly", async function () {
      const allocationAmount = ethers.utils.parseEther("1000");

      // Allocate tokens
      await pocRegistry.connect(pocEvaluator).allocateTokens(
        submissionHash1,
        allocationAmount,
        0, // Founder epoch
        "Gold"
      );

      // Check token balance
      expect(await synth.balanceOf(contributor1.address)).to.equal(allocationAmount);

      // Check epoch balance was reduced
      const epochBalance = await synth.getEpochBalance(0);
      const expectedBalance = ethers.utils.parseEther("89999000000000"); // 90T - 1000
      expect(epochBalance).to.equal(expectedBalance);
    });

    it("Should emit correct events", async function () {
      const allocationAmount = ethers.utils.parseEther("500");

      await expect(
        pocRegistry.connect(pocEvaluator).allocateTokens(
          submissionHash1,
          allocationAmount,
          0,
          "Gold"
        )
      ).to.emit(synth, "TokensAllocated")
        .withArgs(contributor1.address, allocationAmount, 0, "Gold");

      await expect(
        pocRegistry.connect(pocEvaluator).allocateTokens(
          submissionHash1,
          allocationAmount,
          0,
          "Gold"
        )
      ).to.emit(pocRegistry, "POCContribution")
        .withArgs(contributor1.address, allocationAmount, "Gold");
    });
  });

  describe("Integration Tests", function () {
    it("Should handle complete contribution lifecycle", async function () {
      // 1. Submit contribution
      await pocRegistry.connect(pocEvaluator).submitContribution(
        submissionHash1,
        contributor1.address,
        "Complete Test Contribution",
        "scientific"
      );

      // 2. Check submission count
      expect(await pocRegistry.getTotalContributions()).to.equal(1);

      // 3. Record evaluation
      await pocRegistry.connect(pocEvaluator).recordEvaluation(
        submissionHash1,
        ["Gold", "Silver"],
        8500, 9000, 8000, 8500
      );

      // 4. Check qualification
      expect(await pocRegistry.isQualified(submissionHash1)).to.be.true;

      // 5. Register certificate
      await pocRegistry.connect(contributor1).registerCertificate(submissionHash1);

      // 6. Allocate tokens
      await pocRegistry.connect(pocEvaluator).allocateTokens(
        submissionHash1,
        ethers.utils.parseEther("2000"),
        0,
        "Gold"
      );

      // 7. Verify final state
      const contribution = await pocRegistry.getContribution(submissionHash1);
      expect(contribution.registered).to.be.true;
      expect(contribution.metals).to.deep.equal(["Gold", "Silver"]);
      expect(await synth.balanceOf(contributor1.address)).to.equal(ethers.utils.parseEther("2000"));
    });

    it("Should handle multiple contributors", async function () {
      // Contributor 1
      await pocRegistry.connect(pocEvaluator).submitContribution(
        submissionHash1,
        contributor1.address,
        "Contributor 1 Contribution",
        "scientific"
      );
      await pocRegistry.connect(pocEvaluator).recordEvaluation(
        submissionHash1,
        ["Gold"],
        8500, 9000, 8000, 8500
      );
      await pocRegistry.connect(contributor1).registerCertificate(submissionHash1);

      // Contributor 2
      await pocRegistry.connect(pocEvaluator).submitContribution(
        submissionHash2,
        contributor2.address,
        "Contributor 2 Contribution",
        "technological"
      );
      await pocRegistry.connect(pocEvaluator).recordEvaluation(
        submissionHash2,
        ["Silver"],
        7500, 8500, 7000, 7800
      );
      await pocRegistry.connect(contributor2).registerCertificate(submissionHash2);

      // Allocate different amounts
      await pocRegistry.connect(pocEvaluator).allocateTokens(
        submissionHash1,
        ethers.utils.parseEther("1500"),
        0,
        "Gold"
      );
      await pocRegistry.connect(pocEvaluator).allocateTokens(
        submissionHash2,
        ethers.utils.parseEther("800"),
        0,
        "Silver"
      );

      // Verify balances
      expect(await synth.balanceOf(contributor1.address)).to.equal(ethers.utils.parseEther("1500"));
      expect(await synth.balanceOf(contributor2.address)).to.equal(ethers.utils.parseEther("800"));
      expect(await pocRegistry.getTotalContributions()).to.equal(2);
    });
  });

  describe("Security & Access Control", function () {
    it("Should only allow PoC evaluator to submit contributions", async function () {
      await expect(
        pocRegistry.connect(contributor1).submitContribution(
          submissionHash1,
          contributor1.address,
          "Test",
          "scientific"
        )
      ).to.be.revertedWith("Only PoC evaluator can call this function");
    });

    it("Should only allow PoC evaluator to record evaluations", async function () {
      await pocRegistry.connect(pocEvaluator).submitContribution(
        submissionHash1,
        contributor1.address,
        "Test",
        "scientific"
      );

      await expect(
        pocRegistry.connect(contributor1).recordEvaluation(
          submissionHash1,
          ["Gold"],
          8500, 9000, 8000, 8500
        )
      ).to.be.revertedWith("Only PoC evaluator can call this function");
    });

    it("Should only allow PoC evaluator to allocate tokens", async function () {
      await pocRegistry.connect(pocEvaluator).submitContribution(
        submissionHash1,
        contributor1.address,
        "Test",
        "scientific"
      );
      await pocRegistry.connect(pocEvaluator).recordEvaluation(
        submissionHash1,
        ["Gold"],
        8500, 9000, 8000, 8500
      );
      await pocRegistry.connect(contributor1).registerCertificate(submissionHash1);

      await expect(
        pocRegistry.connect(contributor1).allocateTokens(
          submissionHash1,
          ethers.utils.parseEther("1000"),
          0,
          "Gold"
        )
      ).to.be.revertedWith("Only PoC evaluator can call this function");
    });

    it("Should only allow contributor to register their certificate", async function () {
      await pocRegistry.connect(pocEvaluator).submitContribution(
        submissionHash1,
        contributor1.address,
        "Test",
        "scientific"
      );
      await pocRegistry.connect(pocEvaluator).recordEvaluation(
        submissionHash1,
        ["Gold"],
        8500, 9000, 8000, 8500
      );

      await expect(
        pocRegistry.connect(contributor2).registerCertificate(submissionHash1)
      ).to.be.revertedWith("Only contributor can register certificate");
    });

    it("Should prevent double registration", async function () {
      await pocRegistry.connect(pocEvaluator).submitContribution(
        submissionHash1,
        contributor1.address,
        "Test",
        "scientific"
      );
      await pocRegistry.connect(pocEvaluator).recordEvaluation(
        submissionHash1,
        ["Gold"],
        8500, 9000, 8000, 8500
      );

      await pocRegistry.connect(contributor1).registerCertificate(submissionHash1);

      await expect(
        pocRegistry.connect(contributor1).registerCertificate(submissionHash1)
      ).to.be.revertedWith("Certificate already registered");
    });
  });
});
