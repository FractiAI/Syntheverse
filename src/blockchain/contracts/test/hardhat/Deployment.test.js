import { expect } from "chai";
import hre from "hardhat";
const { ethers } = hre;

describe("Syntheverse Deployment", function () {
  let SYNTH, POCRegistry;
  let synth, pocRegistry;
  let owner, pocEvaluator, treasury;

  before(async function () {
    [owner, pocEvaluator, treasury] = await ethers.getSigners();

    // Deploy SYNTH token
    SYNTH = await ethers.getContractFactory("SYNTH");
    synth = await SYNTH.deploy(pocEvaluator.address, treasury.address);
    await synth.deployed();

    // Deploy POC Registry
    POCRegistry = await ethers.getContractFactory("POCRegistry");
    pocRegistry = await POCRegistry.deploy(synth.address, pocEvaluator.address);
    await pocRegistry.deployed();
  });

  it("Should deploy SYNTH token correctly", async function () {
    expect(await synth.name()).to.equal("Syntheverse SYNTH");
    expect(await synth.symbol()).to.equal("SYNTH");
    expect(await synth.pocEvaluator()).to.equal(pocEvaluator.address);
    expect(await synth.treasury()).to.equal(treasury.address);
  });

  it("Should deploy POC Registry correctly", async function () {
    expect(await pocRegistry.pocEvaluator()).to.equal(pocEvaluator.address);
    // Test that contracts can interact
    const synthAddress = await pocRegistry.synthToken();
    expect(synthAddress).to.equal(synth.address);
  });

  it("Should have correct initial state", async function () {
    // SYNTH should start with Founder epoch
    expect(await synth.currentEpoch()).to.equal(0);

    // POC Registry should have no contributions initially
    expect(await pocRegistry.getTotalContributions()).to.equal(0);
  });
});
