"""
PoC API Server
Flask API server that connects the Next.js frontend to the PoC backend.
"""

import os
import sys
import logging
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import hashlib
from datetime import datetime

# Add parent directory to path (go up to project root)
# app.py is at src/api/poc-api/app.py, so parents are:
#   0=poc-api, 1=api, 2=src, 3=project root
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root / "src" / "core"))
sys.path.insert(0, str(project_root / "src"))

# Define base directory (project root)
base_dir = project_root

from core.layer2.poc_server import PoCServer
from core.layer2.poc_archive import ContributionStatus, MetalType
from core.layer2.tokenomics_state import Epoch

# Load GROQ_API_KEY using centralized utility
from core.utils import load_groq_api_key

# Set up logger
logger = logging.getLogger(__name__)

# Blockchain Integration Setup
try:
    from web3 import Web3
    import json

    # Try to connect to Anvil (local Foundry node)
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

    # Load contract ABIs and addresses
    contracts_dir = base_dir / "src" / "blockchain" / "contracts"
    synth_artifact_path = contracts_dir / "artifacts" / "src" / "SYNTH.sol" / "SYNTH.json"
    poc_registry_artifact_path = contracts_dir / "artifacts" / "src" / "POCRegistry.sol" / "POCRegistry.json"

    if synth_artifact_path.exists() and poc_registry_artifact_path.exists():
        # Load SYNTH contract
        with open(synth_artifact_path) as f:
            synth_artifact = json.load(f)
        synth_address = synth_artifact.get('address', '0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
        synth_contract = w3.eth.contract(
            address=synth_address,
            abi=synth_artifact['abi']
        )

        # Load POCRegistry contract
        with open(poc_registry_artifact_path) as f:
            poc_registry_artifact = json.load(f)
        poc_registry_address = poc_registry_artifact.get('address', '0x742d35Cc6634C0532925a3b844Bc454e4438f44f')
        poc_registry_contract = w3.eth.contract(
            address=poc_registry_address,
            abi=poc_registry_artifact['abi']
        )

        # Test connection to blockchain
        if w3.is_connected():
            blockchain_enabled = True
            logger.info("Blockchain integration enabled - Connected to Anvil")
            logger.info(f"SYNTH Contract: {synth_address}")
            logger.info(f"POCRegistry Contract: {poc_registry_address}")
        else:
            blockchain_enabled = False
            logger.warning("Blockchain not connected - using simulation mode")
            logger.info("Start Anvil: cd contracts && anvil")
            logger.info("Deploy contracts: python3 deploy_contracts.py")
    else:
        logger.warning("Blockchain contracts not found - using simulation mode")
        blockchain_enabled = False
        synth_contract = None
        poc_registry_contract = None

except ImportError:
    logger.warning("web3 not installed - blockchain features disabled")
    w3 = None
    blockchain_enabled = False
    synth_contract = None
    poc_registry_contract = None

def simulate_blockchain_registration(submission_hash, contributor):
    """Simulate blockchain registration to demonstrate Foundry/Hardhat integration."""
    try:
        # Get contribution from PoC server
        if not poc_server:
            return jsonify({"success": False, "error": "PoC Server not available"}), 503

        contribution = poc_server.archive.get_contribution(submission_hash)
        if not contribution:
            return jsonify({"success": False, "error": f"Contribution not found: {submission_hash}"}), 404

        # Check if contribution is qualified
        current_status = contribution.get('status')

        if current_status != 'qualified':
            return jsonify({"success": False, "error": f"Contribution status is '{current_status}', not qualified for registration"}), 400

        # Get evaluation data
        metadata = contribution.get('metadata', {})
        metals = contribution.get('metals', [])
        coherence = metadata.get('coherence', 0)
        density = metadata.get('density', 0)
        novelty = metadata.get('novelty', 0)
        poc_score = metadata.get('pod_score', 0)

        print(f"🔗 SIMULATING BLOCKCHAIN REGISTRATION (Foundry/Hardhat Style)")
        print(f"   Contract: POCRegistry at 0x742d35Cc6634C0532925a3b844Bc454e4438f44f")
        print(f"   Token: SYNTH at 0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
        print(f"   Submission: {submission_hash}")
        print(f"   Metals: {metals}")
        print(f"   Score: {poc_score}")

        # Simulate blockchain transaction
        import time
        import hashlib

        # Generate mock transaction hash
        tx_data = f"{submission_hash}:{contributor}:{time.time()}"
        mock_tx_hash = "0x" + hashlib.sha256(tx_data.encode()).hexdigest()[:64]

        print("📝 Simulating POCRegistry.recordEvaluation() call...")
        print(f"   Function: recordEvaluation(bytes32, string[], uint256, uint256, uint256, uint256)")
        print(f"   Params: {submission_hash}, {metals}, {coherence}, {density}, {novelty}, {poc_score}")

        # Simulate token allocation
        allocations = metadata.get('allocations', [])
        total_allocation = 0

        print("💰 Simulating SYNTH token allocations...")
        for alloc in allocations:
            metal = alloc.get('metal', '').lower()
            reward = alloc.get('allocation', {}).get('reward', 0)
            epoch = alloc.get('epoch', 'founder')
            tier = alloc.get('tier', 'standard')

            if reward > 0:
                total_allocation += reward
                print(f"   ✅ Allocated {reward} SYNTH tokens for {metal} ({epoch} epoch)")
                print("   Function: SYNTH.mint(address, uint256)")
                # Simulate contract call
                time.sleep(0.1)  # Simulate blockchain delay

        # Update contribution status in archive
        poc_server.archive.update_contribution(
            submission_hash,
            status=ContributionStatus.REGISTERED
        )

        result = {
            "success": True,
            "submission_hash": submission_hash,
            "blockchain_tx": mock_tx_hash,
            "simulation_mode": True,
            "total_tokens_allocated": total_allocation,
            "metals_registered": metals,
            "poc_score": poc_score,
            "contracts_used": {
                "POCRegistry": "0x742d35Cc6634C0532925a3b844Bc454e4438f44f",
                "SYNTH": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
            },
            "message": f"Successfully registered PoC on Syntheverse Blockmine blockchain (SIMULATION)!",
            "note": "This demonstrates Foundry/Hardhat contract integration. Start Anvil and deploy contracts for real blockchain interaction."
        }

        print(f"🎉 SIMULATION COMPLETE: {submission_hash}")
        print(f"   Mock TX: {mock_tx_hash}")
        return jsonify(result)

    except Exception as e:
        print(f"❌ Simulation error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# Try to import PDF generator (optional)
try:
    sys.path.insert(0, str(base_dir / "ui_web"))
    from pdf_generator import PODPDFGenerator
    pdf_generator_available = True
except ImportError:
    logger.warning("PDF generator not available (reportlab not installed)")
    PODPDFGenerator = None
    pdf_generator_available = False

app = Flask(__name__)
CORS(app)  # Enable CORS for Next.js frontend

# Disable dotenv loading to avoid permission issues
app.config['FLASK_SKIP_DOTENV'] = True

# Initialize PoC Server
logger.info("Starting PoC API server initialization...")
try:
    # Use absolute paths for consistent file locations
    base_dir = Path(__file__).parent.parent.parent  # Project root
    groq_key = load_groq_api_key()

    logger.info(f"Environment check - GROQ_API_KEY: {'set' if groq_key else 'NOT SET'}")
    if groq_key:
        logger.debug(f"GROQ key starts with: {groq_key[:15]}...")
    else:
        logger.warning("No GROQ_API_KEY found in environment")

    logger.info("Initializing PoC Server...")
    poc_server = PoCServer(
        groq_api_key=groq_key,
        output_dir=str(base_dir / "test_outputs" / "poc_reports"),
        tokenomics_state_file=str(base_dir / "test_outputs" / "l2_tokenomics_state.json"),
        archive_file=str(base_dir / "test_outputs" / "poc_archive.json")
    )
    logger.info(f"Archive file path: {base_dir / 'test_outputs' / 'poc_archive.json'}")
    logger.info(f"Archive file exists: {(base_dir / 'test_outputs' / 'poc_archive.json').exists()}")
    logger.info("PoC Server initialized successfully")
except Exception as e:
    logger.warning(f"Failed to initialize PoC Server: {e}")
    logger.warning("Some endpoints may not work until GROQ_API_KEY is set")
    poc_server = None

# Initialize PDF Generator
if pdf_generator_available:
    try:
        pdf_generator = PODPDFGenerator(output_dir=str(base_dir / "ui_web" / "test_outputs" / "pdf_reports"))
        logger.info("PDF Generator initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize PDF Generator: {e}")
        pdf_generator = None
        pdf_generator_available = False
else:
    pdf_generator = None

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/api/archive/statistics', methods=['GET'])
def get_archive_statistics():
    """Get archive statistics."""
    try:
        if not poc_server:
            # Return mock data when PoC server isn't available
            stats = {
                "total_contributions": 0,
                "status_counts": {"draft": 0, "submitted": 0, "evaluating": 0, "qualified": 0, "unqualified": 0},
                "metal_counts": {"gold": 0, "silver": 0, "copper": 0},
                "unique_contributors": 0,
                "unique_content_hashes": 0,
                "last_updated": "2025-01-01T00:00:00Z"
            }
        else:
            stats = poc_server.get_archive_statistics()

        # Backwards-compatible aliases expected by tests/clients
        stats.setdefault("contributions_by_status", stats.get("status_counts", {}))
        stats.setdefault("contributions_by_metal", stats.get("metal_counts", {}))
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/archive/contributions', methods=['GET'])
def get_contributions():
    """Get contributions with optional filters."""
    try:
        if not poc_server:
            # Return empty response in the standard API shape
            return jsonify({"contributions": [], "count": 0})

        status = request.args.get('status')
        contributor = request.args.get('contributor')
        metal = request.args.get('metal')

        # Convert string filters to enums if needed
        status_enum = None
        if status:
            try:
                status_enum = ContributionStatus(status)
            except ValueError:
                pass

        metal_enum = None
        if metal:
            try:
                metal_enum = MetalType(metal)
            except ValueError:
                pass

        contributions = poc_server.archive.get_all_contributions(
            status=status_enum,
            contributor=contributor,
            metal=metal_enum
        )

        # Convert MetalType enums to strings for JSON serialization
        def convert_metals(obj):
            if isinstance(obj, dict):
                return {k: convert_metals(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_metals(item) for item in obj]
            elif hasattr(obj, 'value'):  # MetalType enum
                return obj.value
            else:
                return obj

        # Convert to API format
        contributions_out = []
        for contrib in contributions:
            contributions_out.append(convert_metals({
                "submission_hash": contrib["submission_hash"],
                "title": contrib["title"],
                "contributor": contrib["contributor"],
                "content_hash": contrib["content_hash"],
                "text_content": contrib.get("text_content", ""),
                "status": contrib["status"],
                "category": contrib.get("category"),
                "metals": contrib.get("metals", []),
                "metadata": contrib.get("metadata", {}),
                "created_at": contrib.get("created_at"),
                "updated_at": contrib.get("updated_at"),
            }))

        return jsonify({"contributions": contributions_out, "count": len(contributions_out)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/archive/contributions/<submission_hash>', methods=['GET'])
def get_contribution(submission_hash):
    """Get a specific contribution."""
    try:
        if not poc_server:
            return jsonify({"error": "PoC Server not initialized"}), 503
        contrib = poc_server.archive.get_contribution(submission_hash)
        if not contrib:
            return jsonify({"error": "Contribution not found"}), 404

        # Convert MetalType enums to strings for JSON serialization
        def convert_metals(obj):
            if isinstance(obj, dict):
                return {k: convert_metals(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_metals(item) for item in obj]
            elif hasattr(obj, 'value'):  # MetalType enum
                return obj.value
            else:
                return obj

        # Get contributor submission count for fee calculation
        contributor = contrib["contributor"]
        submission_count = poc_server.get_contributor_submission_count(contributor)

        response_data = {
            "submission_hash": contrib["submission_hash"],
            "title": contrib["title"],
            "contributor": contrib["contributor"],
            "content_hash": contrib["content_hash"],
            "text_content": contrib.get("text_content", ""),
            "status": contrib["status"],
            "category": contrib.get("category"),
            "metals": contrib.get("metals", []),
            "metadata": contrib.get("metadata", {}),
            "created_at": contrib.get("created_at"),
            "updated_at": contrib.get("updated_at"),
            "contributor_stats": {
                "submission_count": submission_count,
                "free_submissions_remaining": max(0, 3 - submission_count),
                "fee_required": submission_count >= 3
            }
        }

        return jsonify(convert_metals(response_data))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/submit', methods=['POST'])
def submit_contribution():
    """Submit a new contribution."""
    try:
        if not poc_server:
            return jsonify({"error": "PoC Server not initialized"}), 503

        # Handle both JSON and form-data requests
        if request.content_type and 'application/json' in request.content_type:
            # JSON request
            data = request.json
            submission_hash = data.get('submission_hash')
            title = data.get('title')
            contributor = data.get('contributor')
            text_content = data.get('text_content', '')
            pdf_path = data.get('pdf_path')
            category = data.get('category', 'scientific')
        else:
            # Form-data request (for file uploads)
            submission_hash = request.form.get('submission_hash')
            title = request.form.get('title')
            contributor = request.form.get('contributor')
            text_content = request.form.get('text_content', '')
            category = request.form.get('category', 'scientific')

            # Handle file upload
            pdf_path = None
            # Accept both `pdf` (tests) and `file` (legacy)
            upload = request.files.get('pdf') or request.files.get('file')
            if upload and upload.filename and upload.filename.lower().endswith('.pdf'):
                # If submission_hash isn't provided, generate one deterministically enough for tracing.
                # Prefer a stable hash of (title, contributor, file bytes) when possible.
                if not submission_hash:
                    file_bytes = upload.read()
                    upload.stream.seek(0)
                    submission_hash = hashlib.sha256(
                        (title or "").encode("utf-8") + b"\n" +
                        (contributor or "").encode("utf-8") + b"\n" +
                        file_bytes
                    ).hexdigest()

                filename = secure_filename(f"{submission_hash}_{upload.filename}")
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                upload.save(filepath)
                pdf_path = filepath

        # Require core fields; submission_hash is optional (can be generated from PDF)
        if not title or not contributor:
            return jsonify({"error": "Missing required fields"}), 400

        # If submission_hash is still missing (no PDF provided), generate one from content + current time
        if not submission_hash:
            submission_hash = hashlib.sha256(
                f"{title}|{contributor}|{datetime.utcnow().isoformat()}".encode("utf-8")
            ).hexdigest()

        # If we have a PDF but no text content, extract text from PDF
        if pdf_path and not text_content.strip():
            extracted_text = poc_server._extract_text_from_pdf(pdf_path)
            if extracted_text:
                text_content = extracted_text
            else:
                # PDF extraction failed - use a placeholder and mark for manual review
                text_content = f"[PDF Upload: {os.path.basename(pdf_path)} - Text extraction failed. Please provide text content or contact administrators for manual processing.]"

        # If we have both PDF text and additional text, combine them
        if pdf_path and text_content.strip():
            additional_text = request.form.get('text_content', '') if request.form else data.get('text_content', '')
            if additional_text.strip():
                text_content += f"\n\n--- Additional Notes ---\n{additional_text.strip()}"

        # Submit to PoC server
        # Check if this is a test submission
        is_test_submission = (
            'test' in title.lower() or
            'test' in contributor.lower() or
            'demo' in title.lower() or
            'demo' in contributor.lower() or
            submission_hash.endswith('-test-123') or
            submission_hash.endswith('-123')
        )

        result = poc_server.submit_contribution(
            submission_hash=submission_hash,
            title=title,
            contributor=contributor,
            text_content=text_content,
            pdf_path=pdf_path,
            category=category,
            is_test=is_test_submission
        )

        # Automatically evaluate the contribution
        try:
            eval_result = poc_server.evaluate_contribution(
                submission_hash=submission_hash,
                progress_callback=None
            )
            final_status = eval_result.get("status", result["status"])
        except Exception as eval_error:
            print(f"Auto-evaluation failed for {submission_hash}: {eval_error}")
            final_status = result["status"]

        return jsonify({
            "success": True,
            "submission_hash": result["submission_hash"],
            "status": final_status
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/evaluate/<submission_hash>', methods=['POST'])
def evaluate_contribution(submission_hash):
    """Evaluate a contribution."""
    try:
        if not poc_server:
            return jsonify({"error": "PoC Server not initialized"}), 503
        result = poc_server.evaluate_contribution(
            submission_hash=submission_hash,
            progress_callback=None
        )

        # Convert MetalType enums to strings for JSON serialization
        def convert_metals(obj):
            if isinstance(obj, dict):
                return {k: convert_metals(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_metals(item) for item in obj]
            elif hasattr(obj, 'value'):  # MetalType enum
                return obj.value
            else:
                return obj

        result = convert_metals(result)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/api/certificate/<submission_hash>', methods=['POST'])
def generate_certificate(submission_hash):
    """Generate PoC certificate PDF for a qualified contribution."""
    try:
        if not poc_server:
            return jsonify({"error": "PoC Server not initialized"}), 503
        if not pdf_generator_available or not pdf_generator:
            return jsonify({"error": "Certificate generation not available (PDF generator not installed)"}), 503

        # Get contribution details
        contribution = poc_server.archive.get_contribution(submission_hash)
        if not contribution:
            return jsonify({"error": "Contribution not found"}), 404

        # Check if contribution is qualified
        if contribution.get('status') != 'qualified':
            return jsonify({"error": "Contribution is not qualified for certification"}), 400

        # Get evaluation and allocation data
        evaluation_data = contribution.get('metadata', {})
        allocations = evaluation_data.get('allocations', [])

        if not allocations:
            return jsonify({"error": "No allocations found for this contribution"}), 400

        # Use the first allocation (primary metal)
        allocation = allocations[0]['allocation']

        # Prepare submission data for PDF generation
        submission_data = {
            'submission_hash': submission_hash,
            'title': contribution.get('title', 'Unknown'),
            'contributor': contribution.get('contributor', 'Unknown'),
            'category': contribution.get('category', 'general'),
            'status': contribution.get('status', 'unknown'),
            'timestamp': contribution.get('created_at', 'Unknown')
        }

        # Prepare allocation data for PDF generation
        allocation_data = {
            'epoch': allocation.get('epoch', 'unknown'),
            'tier': allocation.get('tier', 'unknown'),
            'pod_score': evaluation_data.get('pod_score', 0),
            'reward': allocation.get('reward', 0)
        }

        # Generate certificate PDF
        pdf_path = pdf_generator.generate_certificate_pdf(submission_data, allocation_data)

        # Return the PDF file
        return send_from_directory(
            str(Path(pdf_path).parent),
            Path(pdf_path).name,
            as_attachment=True,
            download_name=f"poc_certificate_{submission_hash[:8]}.pdf"
        )

    except Exception as e:
        print(f"Error generating certificate for {submission_hash}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/sandbox-map', methods=['GET'])
def get_sandbox_map():
    """Get sandbox map data."""
    try:
        if not poc_server:
            return jsonify({"error": "PoC Server not initialized"}), 503
        map_data = poc_server.get_sandbox_map()
        # Ensure a stable top-level shape for clients/tests
        if isinstance(map_data, dict):
            map_data.setdefault("dimensions", ["contributor", "submission_hash", "status", "metals", "epoch"])
        return jsonify(map_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/tokenomics/epoch-info', methods=['GET'])
def get_epoch_info():
    """Get epoch information."""
    try:
        if not poc_server:
            # Return mock data when PoC server isn't available
            return jsonify({
                "current_epoch": "founder",
                "epochs": {
                    "founder": {
                        "balance": 45000000000000,
                        "threshold": 10000,
                        "distribution_amount": 45000000000000,
                        "distribution_percent": 50.0,
                        "available_tiers": ["gold", "silver", "copper"]
                    },
                    "pioneer": {
                        "balance": 22500000000000,
                        "threshold": 5000,
                        "distribution_amount": 22500000000000,
                        "distribution_percent": 25.0,
                        "available_tiers": ["silver", "copper"]
                    },
                    "community": {
                        "balance": 11250000000000,
                        "threshold": 2500,
                        "distribution_amount": 11250000000000,
                        "distribution_percent": 12.5,
                        "available_tiers": ["copper"]
                    },
                    "ecosystem": {
                        "balance": 11250000000000,
                        "threshold": 1250,
                        "distribution_amount": 11250000000000,
                        "distribution_percent": 12.5,
                        "available_tiers": ["copper"]
                    }
                }
            })
        epoch_info = poc_server.get_epoch_info()
        # Backwards-compatible fields expected by tests/clients
        current_epoch = epoch_info.get("current_epoch")
        if current_epoch:
            epoch_info.setdefault("epoch_name", current_epoch.title())
            epoch_info.setdefault("epoch_description", f"Token distribution epoch: {current_epoch}")
        return jsonify(epoch_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/tokenomics/statistics', methods=['GET'])
def get_tokenomics_statistics():
    """Get tokenomics statistics."""
    try:
        if not poc_server:
            # Return mock data when PoC server isn't available
            return jsonify({
                "total_supply": 90000000000000,  # 90T
                "total_distributed": 0,
                "total_remaining": 90000000000000,
                "epoch_balances": {
                    "founder": 45000000000000,
                    "pioneer": 22500000000000,
                    "community": 11250000000000,
                    "ecosystem": 11250000000000
                },
                "current_epoch": "founder",
                "founder_halving_count": 0,
                "total_coherence_density": 0,
                "total_holders": 0,
                "total_allocations": 0
            })
        stats = poc_server.get_tokenomics_statistics()
        # Backwards-compatible aliases expected by tests/clients
        if isinstance(stats, dict):
            # Many callers use "allocated" / "rewards" terminology.
            stats.setdefault("total_allocated", stats.get("total_distributed", stats.get("total_allocations", 0)))
            stats.setdefault("total_rewards", stats.get("total_distributed", 0))
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/contributor/<contributor>/submission-count', methods=['GET'])
def get_contributor_submission_count(contributor):
    """Get the number of submissions by a contributor."""
    try:
        if not poc_server:
            return jsonify({"error": "PoC Server not initialized"}), 503

        count = poc_server.get_contributor_submission_count(contributor)
        return jsonify({
            "contributor": contributor,
            "submission_count": count,
            "free_submissions_remaining": max(0, 3 - count),
            "fee_required": count >= 3
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/admin/cleanup-test-submissions', methods=['POST'])
def cleanup_test_submissions():
    """Clean up all test submissions from the archive."""
    try:
        if not poc_server:
            return jsonify({"error": "PoC Server not initialized"}), 503

        result = poc_server.cleanup_test_submissions()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/admin/clear-memory', methods=['POST'])
def clear_memory():
    """Completely clear all contributions from memory and archive."""
    try:
        if not poc_server:
            return jsonify({"error": "PoC Server not initialized"}), 503

        # Clear all contributions from archive
        poc_server.archive.archive["contributions"] = {}
        poc_server.archive.archive["content_hashes"] = {}
        poc_server.archive.archive["by_status"] = {
            status.value: [] for status in ContributionStatus
        }
        poc_server.archive.archive["by_contributor"] = {}
        poc_server.archive.archive["by_metal"] = {
            metal.value: [] for metal in MetalType
        }
        poc_server.archive.archive["metadata"]["total_contributions"] = 0

        # Save the cleared archive
        poc_server.archive.save_archive()

        # Clear tokenomics allocations and reset epoch balances
        poc_server.tokenomics.state["allocation_history"] = []
        poc_server.tokenomics.state["contributor_balances"] = {}
        # Reset epoch balances to initial distribution
        for epoch in Epoch:
            poc_server.tokenomics.state["epoch_balances"][epoch.value] = (
                poc_server.tokenomics.TOTAL_SUPPLY * poc_server.tokenomics.EPOCH_DISTRIBUTION[epoch]
            )
        poc_server.tokenomics.state["total_coherence_density"] = 0.0
        poc_server.tokenomics.state["founder_halving_count"] = 0
        poc_server.tokenomics.save_state()

        # Also reset the persistent state file to ensure clean initial values
        import json
        clean_state = {
            "epoch_balances": {
                "founder": 45000000000000.0,
                "pioneer": 22500000000000.0,
                "community": 11250000000000.0,
                "ecosystem": 11250000000000.0
            },
            "total_coherence_density": 0.0,
            "founder_halving_count": 0,
            "current_epoch": "founder",
            "epoch_progression": {
                "founder": False,
                "pioneer": False,
                "community": False,
                "ecosystem": False
            },
            "allocation_history": [],
            "contributor_balances": {},
            "last_updated": "2025-12-16T14:13:00.000000"
        }

        with open(poc_server.tokenomics.state_file, 'w') as f:
            json.dump(clean_state, f, indent=2)

        return jsonify({
            "success": True,
            "message": "Memory completely cleared - all contributions and allocations removed"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/debug/tokenomics-state', methods=['GET'])
def debug_tokenomics_state():
    """Debug endpoint to check tokenomics state in memory."""
    try:
        if not poc_server:
            return jsonify({"error": "PoC Server not initialized"}), 503

        state = poc_server.tokenomics.state
        return jsonify({
            "tokenomics_state": state,
            # Convenience top-level summary fields
            "epoch_balances": state.get("epoch_balances", {}),
            "total_coherence_density": state.get("total_coherence_density", 0.0),
            "allocation_history_count": len(state.get("allocation_history", [])),
            "state_file_path": str(poc_server.tokenomics.state_file),
            "state_file_exists": poc_server.tokenomics.state_file.exists()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/register', methods=['GET'])
def register_poc():
    """Serve Syntheverse Blockmine registration page for PoC."""
    try:
        submission_hash = request.args.get('hash')
        contributor = request.args.get('contributor')

        if not submission_hash or not contributor:
            return """
            <html>
            <head><title>Syntheverse Blockmine PoC Registration</title></head>
            <body>
                <h1>Invalid Registration Request</h1>
                <p>Missing required parameters: hash and contributor</p>
                <p><a href="javascript:window.close()">Close Window</a></p>
            </body>
            </html>
            """, 400

        if not poc_server:
            return """
            <html>
            <head><title>Syntheverse Blockmine PoC Registration</title></head>
            <body>
                <h1>Service Unavailable</h1>
                <p>PoC Server not initialized. Please try again later.</p>
                <p><a href="javascript:window.close()">Close Window</a></p>
            </body>
            </html>
            """, 503

        # Get contribution details
        contribution = poc_server.archive.get_contribution(submission_hash)
        if not contribution:
            return f"""
            <html>
            <head><title>Syntheverse Blockmine PoC Registration</title></head>
            <body>
                <h1>Contribution Not Found</h1>
                <p>Could not find contribution with hash: {submission_hash}</p>
                <p><a href="javascript:window.close()">Close Window</a></p>
            </body>
            </html>
            """, 404

        # Check if contribution is qualified
        if contribution.get('status') != 'qualified':
            return f"""
            <html>
            <head><title>Syntheverse Blockmine PoC Registration</title></head>
            <body>
                <h1>Contribution Not Qualified</h1>
                <p>This contribution is not qualified for registration on Syntheverse Blockmine.</p>
                <p>Status: {contribution.get('status', 'unknown')}</p>
                <p><a href="javascript:window.close()">Close Window</a></p>
            </body>
            </html>
            """, 400

        # Get evaluation and allocation data
        metadata = contribution.get('metadata', {})
        allocations = metadata.get('allocations', [])

        if not allocations:
            return """
            <html>
            <head><title>Syntheverse Blockmine PoC Registration</title></head>
            <body>
                <h1>No Allocations Found</h1>
                <p>This contribution has no token allocations to register.</p>
                <p><a href="javascript:window.close()">Close Window</a></p>
            </body>
            </html>
            """, 400

        # Convert MetalType enums to strings for display
        def convert_metals(obj):
            if isinstance(obj, dict):
                return {k: convert_metals(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_metals(item) for item in obj]
            elif hasattr(obj, 'value'):  # MetalType enum
                return obj.value
            else:
                return obj

        contribution = convert_metals(contribution)
        allocations = convert_metals(allocations)

        # Calculate total tokens
        total_tokens = sum(alloc['allocation']['reward'] for alloc in allocations) / 1e12  # Convert to trillions

        # Generate registration form HTML
        metals_list = ', '.join([alloc['metal'] for alloc in allocations])
        allocation_details = '\n'.join([
            f"• {alloc['metal'].title()}: {alloc['allocation']['reward'] / 1e12:.2f}T SYNTH ({alloc['tier']} tier)"
            for alloc in allocations
        ])

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Syntheverse Blockmine PoC Registration</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    border-radius: 12px;
                    padding: 30px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #2563eb;
                    margin-bottom: 10px;
                }}
                .subtitle {{
                    color: #6b7280;
                    font-size: 1.1em;
                }}
                .poc-details {{
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .allocation-summary {{
                    background: #ecfdf5;
                    border: 1px solid #d1fae5;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .fee-notice {{
                    background: #fef3c7;
                    border: 1px solid #fde68a;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .fee-amount {{
                    font-size: 1.5em;
                    font-weight: bold;
                    color: #d97706;
                }}
                .register-btn {{
                    background: #2563eb;
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-size: 1.1em;
                    font-weight: 600;
                    cursor: pointer;
                    display: block;
                    width: 100%;
                    margin: 20px 0;
                    transition: background-color 0.2s;
                }}
                .register-btn:hover {{
                    background: #1d4ed8;
                }}
                .register-btn:disabled {{
                    background: #9ca3af;
                    cursor: not-allowed;
                }}
                .cancel-btn {{
                    background: #6b7280;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    cursor: pointer;
                    margin-top: 10px;
                }}
                .cancel-btn:hover {{
                    background: #4b5563;
                }}
                .warning {{
                    background: #fee2e2;
                    border: 1px solid #fecaca;
                    color: #dc2626;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🔗 Syntheverse Blockmine</div>
                    <h1>PoC Registration</h1>
                    <div class="subtitle">Register your Proof of Concept on the blockchain</div>
                </div>

                <div class="poc-details">
                    <h3>📄 PoC Details</h3>
                    <p><strong>Title:</strong> {contribution.get('title', 'Unknown')}</p>
                    <p><strong>Hash:</strong> <code>{submission_hash}</code></p>
                    <p><strong>Contributor:</strong> <code>{contributor}</code></p>
                    <p><strong>Category:</strong> {contribution.get('category', 'Unknown').title()}</p>
                    <p><strong>Metals:</strong> {metals_list}</p>
                    <p><strong>PoC Score:</strong> {metadata.get('pod_score', 0):.0f}</p>
                </div>

                <div class="allocation-summary">
                    <h3>💰 Token Allocation</h3>
                    <p><strong>Total SYNTH Tokens:</strong> {total_tokens:.2f}T</p>
                    <h4>Allocation Breakdown:</h4>
                    <pre>{allocation_details}</pre>
                </div>

                <div class="fee-notice">
                    <h3>💳 Registration Fee</h3>
                    <p>The registration fee for entering this PoC certificate and token allocations into the Syntheverse Blockmine blockchain is:</p>
                    <div class="fee-amount">$200 USD</div>
                    <p><small>This fee covers blockchain transaction costs and certificate minting.</small></p>
                </div>

                <div class="warning">
                    <h4>⚠️ Important Notice</h4>
                    <p>This action will permanently register your PoC on the Syntheverse Blockmine blockchain. Please verify all details above are correct before proceeding.</p>
                    <p>The registration process is irreversible and the fee is non-refundable.</p>
                </div>

                <button class="register-btn" onclick="proceedToRegistration()">
                    Proceed to Payment & Registration
                </button>

                <button class="cancel-btn" onclick="window.close()">
                    Cancel & Close
                </button>
            </div>

            <script>
                async function proceedToRegistration() {{
                    // Disable button to prevent double-clicks
                    const button = document.querySelector('.register-btn');
                    const originalText = button.textContent;
                    button.disabled = true;
                    button.textContent = 'Registering...';

                    try {{
                        // Call the blockchain registration API
                        const response = await fetch('/api/register-poc', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify({{
                                submission_hash: '{submission_hash}',
                                contributor: '{contributor}'
                            }})
                        }});

                        const result = await response.json();

                        if (result.success) {{
                            alert('🎉 SUCCESS!\\n\\nYour PoC has been registered on the Syntheverse Blockmine blockchain!\\n\\n' +
                                  'Transaction Hash: ' + (result.blockchain_tx || 'N/A') + '\\n' +
                                  'Tokens Allocated: ' + (result.total_tokens_allocated || 0) + ' SYNTH\\n' +
                                  'Metals: ' + (result.metals_registered || []).join(', ') + '\\n\\n' +
                                  'Your contribution is now permanently recorded on the blockchain.');
                            window.close();
                        }} else {{
                            alert('❌ Registration Failed\\n\\n' + result.error);
                            button.disabled = false;
                            button.textContent = originalText;
                        }}
                    }} catch (error) {{
                        alert('❌ Network Error\\n\\nFailed to connect to registration service. Please try again.');
                        button.disabled = false;
                        button.textContent = originalText;
                        console.error('Registration error:', error);
                    }}
                }}
            </script>
        </body>
        </html>
        """

        return html_content

    except Exception as e:
        print(f"Error in register_poc: {e}")
        return f"""
        <html>
        <head><title>Syntheverse Blockmine PoC Registration</title></head>
        <body>
            <h1>Registration Error</h1>
            <p>An error occurred while processing your registration request.</p>
            <p>Error: {str(e)}</p>
            <p><a href="javascript:window.close()">Close Window</a></p>
        </body>
        </html>
        """, 500


@app.route('/api/register-poc', methods=['POST'])
def register_poc_blockchain():
    """Register PoC contribution on the blockchain using Foundry/Hardhat contracts."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        submission_hash = data.get('submission_hash')
        contributor = data.get('contributor')

        if not submission_hash or not contributor:
            return jsonify({"success": False, "error": "Missing submission_hash or contributor"}), 400

        # Check if blockchain is enabled - if not, simulate the calls
        if not blockchain_enabled:
            print("🔄 SIMULATING BLOCKCHAIN REGISTRATION (Foundry/Hardhat contracts not connected)")
            return simulate_blockchain_registration(submission_hash, contributor)

        # Verify connection to Anvil
        if not w3.is_connected():
            print("🔄 SIMULATING BLOCKCHAIN REGISTRATION (Anvil not connected)")
            return simulate_blockchain_registration(submission_hash, contributor)

        # Get contribution from PoC server
        if not poc_server:
            return jsonify({"success": False, "error": "PoC Server not available"}), 503

        contribution = poc_server.archive.get_contribution(submission_hash)
        if not contribution:
            return jsonify({"success": False, "error": f"Contribution not found: {submission_hash}"}), 404

        # Check if contribution is qualified
        if contribution.get('status') != 'qualified':
            return jsonify({"success": False, "error": "Contribution is not qualified for registration"}), 400

        # Get evaluation data
        metadata = contribution.get('metadata', {})
        metals = contribution.get('metals', [])
        coherence = metadata.get('coherence', 0)
        density = metadata.get('density', 0)
        novelty = metadata.get('novelty', 0)
        poc_score = metadata.get('pod_score', 0)

        # Convert metals to strings if they're enums
        if metals and hasattr(metals[0], 'value'):
            metals = [metal.value for metal in metals]

        # Get the first account from Anvil (default unlocked account)
        accounts = w3.eth.accounts
        if not accounts:
            return jsonify({"success": False, "error": "No accounts available in Anvil"}), 500

        deployer_account = accounts[0]

        print(f"🔗 Registering PoC on blockchain...")
        print(f"   Account: {deployer_account}")
        print(f"   Submission: {submission_hash}")
        print(f"   Metals: {metals}")
        print(f"   Score: {poc_score}")

        # Convert submission_hash to bytes32
        submission_hash_bytes32 = Web3.keccak(text=submission_hash)

        # Record evaluation on POCRegistry contract
        try:
            tx = poc_registry_contract.functions.recordEvaluation(
                submission_hash_bytes32,
                metals,
                int(coherence * 100),  # Scale to avoid decimals
                int(density * 100),
                int(novelty * 100),
                int(poc_score * 100)
            ).transact({'from': deployer_account})

            # Wait for transaction
            receipt = w3.eth.wait_for_transaction_receipt(tx)
            print(f"✅ Evaluation recorded: {receipt.transactionHash.hex()}")

        except Exception as e:
            print(f"❌ Failed to record evaluation: {e}")
            return jsonify({"success": False, "error": f"Blockchain evaluation failed: {str(e)}"}), 500

        # Allocate SYNTH tokens
        allocations = metadata.get('allocations', [])
        total_allocation = 0

        for alloc in allocations:
            try:
                metal = alloc.get('metal', '').lower()
                reward = alloc.get('allocation', {}).get('reward', 0)
                epoch = alloc.get('epoch', 'founder')
                tier = alloc.get('tier', 'standard')

                # Mint SYNTH tokens to contributor (simplified - in reality would use contributor address)
                if reward > 0:
                    mint_tx = synth_contract.functions.mint(
                        deployer_account,  # For demo - would be contributor address
                        int(reward)
                    ).transact({'from': deployer_account})

                    mint_receipt = w3.eth.wait_for_transaction_receipt(mint_tx)
                    total_allocation += reward
                    print(f"✅ Allocated {reward} SYNTH tokens for {metal} ({epoch} epoch)")

            except Exception as e:
                print(f"❌ Failed to allocate {metal} tokens: {e}")
                continue

        # Update contribution status in archive
        poc_server.archive.update_contribution(
            submission_hash,
            status=ContributionStatus.REGISTERED
        )

        result = {
            "success": True,
            "submission_hash": submission_hash,
            "blockchain_tx": receipt.transactionHash.hex() if 'receipt' in locals() else None,
            "total_tokens_allocated": total_allocation,
            "metals_registered": metals,
            "poc_score": poc_score,
            "message": f"Successfully registered PoC on Syntheverse Blockmine blockchain!"
        }

        print(f"🎉 PoC Registration Complete: {submission_hash}")
        return jsonify(result)

    except Exception as e:
        print(f"❌ Registration error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "poc-api",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })


if __name__ == '__main__':
    logger.info("Starting PoC API Server...")
    logger.info("API will be available at: http://localhost:5001")
    logger.info("Make sure GROQ_API_KEY is set in environment")
    # Debug/reloader should be off by default (test runners spawn processes and expect stable PIDs).
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host='0.0.0.0', port=5001, debug=debug)
