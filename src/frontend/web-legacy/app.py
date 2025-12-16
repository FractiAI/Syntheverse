"""
Syntheverse PoC Registration Web UI
Browser-based interface for registering PoC certificates on the blockchain.
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import json
from datetime import datetime
from typing import Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import web3 for blockchain interaction
try:
    from web3 import Web3
    import json
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    print("⚠️  web3 not available - registration will use simulation mode")

# Import API client for communication with PoC API (fallback)
import requests

# PDF generator is optional - only used if needed
try:
    from pdf_generator import PODPDFGenerator
except ImportError:
    PODPDFGenerator = None

# API endpoints
POC_API_URL = os.getenv('POC_API_URL', 'http://localhost:5001')

# Web3 and contract setup for Hardhat integration
w3 = None
poc_registry_contract = None
synth_token_contract = None
blockchain_enabled = False

if WEB3_AVAILABLE:
    try:
        # Connect to local Hardhat network
        w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
        if w3.is_connected():
            print("✅ Connected to Hardhat network (http://127.0.0.1:8545)")

            # Load contract ABIs and addresses
            contracts_dir = Path(__file__).parent.parent.parent / "contracts"
            poc_registry_abi_file = contracts_dir / "artifacts" / "src" / "POCRegistry.sol" / "POCRegistry.json"
            synth_abi_file = contracts_dir / "artifacts" / "src" / "SYNTH.sol" / "SYNTH.json"

            if poc_registry_abi_file.exists() and synth_abi_file.exists():
                with open(poc_registry_abi_file) as f:
                    poc_registry_data = json.load(f)
                with open(synth_abi_file) as f:
                    synth_data = json.load(f)

                # Use deployed contract addresses from Foundry deployment
                poc_registry_address = '0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9'  # POCRegistry deployed address
                synth_address = '0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0'  # SYNTH deployed address

                poc_registry_contract = w3.eth.contract(address=poc_registry_address, abi=poc_registry_data['abi'])
                synth_token_contract = w3.eth.contract(address=synth_address, abi=synth_data['abi'])

                # Get deployer account (first Hardhat account)
                deployer_account = w3.eth.accounts[0]
                print(f"✅ Using deployer account: {deployer_account}")
                print(f"📋 POCRegistry contract: {poc_registry_address}")
                print(f"💰 SYNTH token contract: {synth_address}")
                blockchain_enabled = True
            else:
                print("⚠️  Contract artifacts not found - using simulation mode")
        else:
            print("⚠️  Cannot connect to Hardhat network - using simulation mode")
    except Exception as e:
        print(f"⚠️  Blockchain setup failed: {e} - using simulation mode")
else:
    print("⚠️  Web3 not available - using simulation mode")

# Mock UI module for backward compatibility
class MockUI:
    def __init__(self):
        self.submissions = []
        self.node = MockNode()
        self.pod_server = MockPodServer()

    def submit_pdf(self, filepath, contributor, category):
        """Mock submission - in real implementation this would call the PoC API"""
        print(f"Mock submission: {filepath} by {contributor} in category {category}")
        # In a real implementation, this would call the PoC API
        return {"success": True, "message": "Mock submission completed"}

class MockNode:
    def get_blockchain_info(self):
        return {
            "block_height": 12345,
            "total_transactions": 678,
            "active_nodes": 3,
            "network_status": "healthy"
        }

class MockPodServer:
    def get_epoch_info(self):
        return {
            "current_epoch": "Pioneer",
            "epoch_progress": 65,
            "total_supply": 90000000000000,
            "circulating_supply": 1500000000000
        }

    def get_tokenomics_statistics(self):
        return {
            "total_allocated": 1500000000000,
            "gold_tier_count": 12,
            "silver_tier_count": 45,
            "copper_tier_count": 123,
            "average_reward": 12500000000
        }

ui = MockUI()

# Get the absolute path to the templates directory
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')

app = Flask(__name__,
            template_folder=template_dir,
            static_folder=os.path.join(current_dir, 'static') if os.path.exists(os.path.join(current_dir, 'static')) else None)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'syntheverse-pod-secret-key'

# Disable dotenv loading to avoid permission issues
app.config['FLASK_SKIP_DOTENV'] = True

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('test_outputs', exist_ok=True)

# Initialize blockchain components (disabled - now using API)
# node = SyntheverseNode("registration-node", data_dir="test_outputs/blockchain")
# poc_contract = POCContract()
node = None
poc_contract = None

# Progress tracking for submissions
submission_progress = {}  # submission_hash -> progress dict


@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')


@app.route('/register')
def register_certificate():
    """Certificate registration page."""
    return render_template('register_certificate.html')




@app.route('/api/status', methods=['GET'])
def get_status():
    """Get epoch status and tokenomics."""
    try:
        epoch_info = ui.pod_server.get_epoch_info()
        token_stats = ui.pod_server.get_tokenomics_statistics()
        blockchain_info = ui.node.get_blockchain_info()
        
        return jsonify({
            "success": True,
            "epoch_info": epoch_info,
            "token_stats": token_stats,
            "blockchain": {
                "chain_length": blockchain_info["chain_length"],
                "pending_transactions": blockchain_info["pending_transactions"],
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    """Get all PoD submissions."""
    try:
        submissions = ui.submissions
        return jsonify({
            "success": True,
            "submissions": submissions,
            "count": len(submissions)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/submit', methods=['POST'])
def submit_document():
    """Submit document(s) for PoD evaluation. Supports multiple files."""
    try:
        # Check if files are present
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400
        
        # Get single file
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400
        
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        # Get form data
        contributor = request.form.get('contributor', 'anonymous')
        category = request.form.get('category', 'scientific')
        
        # Validate category
        if category not in ['scientific', 'tech', 'alignment']:
            category = 'scientific'
        
        try:
            # Save uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Submit for evaluation (this will create submission_hash)
            # We need to get the hash BEFORE submitting, so we can track progress
            submission_hash_preview = None
            
            try:
                # Generate a hash for the submission (simplified approach)
                import hashlib
                with open(filepath, 'rb') as f:
                    file_content = f.read()
                submission_hash_preview = hashlib.sha256(file_content).hexdigest()

                # Store submission info for tracking
                submission_progress[submission_hash_preview] = {
                    "status": "uploaded",
                    "filename": filename,
                    "contributor": contributor,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Start progress tracking BEFORE submitting
                if submission_hash_preview:
                    submission_progress[submission_hash_preview] = {
                        "status": "processing",
                        "message": "Submission created, starting evaluation...",
                        "stage": "submitted",
                        "timestamp": datetime.now().isoformat()
                    }
                    print(f"Started progress tracking for submission: {submission_hash_preview[:16]}...")
                
                # Now submit for full evaluation (progress tracking is handled in ui_pod_submission)
                ui.submit_pdf(filepath, contributor, category)
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Submission failed: {str(e)}",
                    "error_type": "submission_error"
                }), 500
            
            # Get the submission from history
            if ui.submissions:
                latest_submission = ui.submissions[-1]
                submission_hash = latest_submission.get('submission_hash') or submission_hash_preview
                
                # Update progress if we have it
                if submission_hash and submission_hash in submission_progress:
                    submission_progress[submission_hash]["status"] = "completed"
                    submission_progress[submission_hash]["stage"] = "complete"
                    submission_progress[submission_hash]["message"] = "Evaluation completed successfully"
                
                # Check if evaluation failed
                if latest_submission.get('status') == 'evaluation_failed':
                    # Evaluation failed - return error
                    error_msg = latest_submission.get('error', 'Evaluation failed')
                    error_type = latest_submission.get('error_type', 'evaluation_error')
                    
                    result = {
                        "filename": filename,
                        "submission": latest_submission,
                        "submission_hash": submission_hash,
                        "report_data": None,
                        "success": False,
                        "error": error_msg,
                        "error_type": error_type
                    }
                    
                    return jsonify({
                        "success": False,
                        "result": result,
                        "message": f"Submission created but evaluation failed: {error_msg}"
                    }), 500
                
                # Get full report data for display
                # Wait a moment for report to be written, then try to load it
                import time
                report_data = None
                report_dir = Path('test_outputs/pod_reports')
                if submission_hash:
                    # Try multiple times with small delays (reduced wait time)
                    for attempt in range(10):  # More attempts but shorter waits
                        time.sleep(0.2)  # Reduced from 0.5 to 0.2 seconds
                        report_files = list(report_dir.glob(f"{submission_hash}_*.json"))
                        if report_files:
                            latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
                            try:
                                with open(latest_report, 'r') as f:
                                    report_data = json.load(f)
                                break  # Successfully loaded
                            except (json.JSONDecodeError, IOError):
                                continue  # File might still be writing, try again
                        
                        # Don't wait too long - if we've tried a few times, return what we have
                        if attempt >= 4:  # After 1 second total, don't wait longer
                            break
                
                result = {
                    "filename": filename,
                    "submission": latest_submission,
                    "submission_hash": submission_hash,
                    "report_data": report_data,
                    "success": True
                }
                
                return jsonify({
                    "success": True,
                    "result": result,
                    "message": "Document submitted successfully!"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Submission failed - no submission created",
                    "error_type": "submission_error"
                }), 500
                
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/submission/<submission_hash>', methods=['GET'])
def get_submission(submission_hash):
    """Get details of a specific submission."""
    try:
        for submission in ui.submissions:
            if submission.get('submission_hash') == submission_hash:
                return jsonify({
                    "success": True,
                    "submission": submission
                })
        
        return jsonify({"success": False, "error": "Submission not found"}), 404
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/submission/<submission_hash>/progress', methods=['GET'])
def get_submission_progress(submission_hash):
    """Get progress status for a submission."""
    # Debug: log all available submission hashes
    if submission_hash not in submission_progress:
        print(f"Progress not found for hash: {submission_hash[:16]}...")
        print(f"Available hashes: {[h[:16] + '...' for h in submission_progress.keys()]}")
    
    progress = submission_progress.get(submission_hash, {
        "status": "unknown",
        "message": "No progress information available. Submission may not have started yet.",
        "stage": "unknown",
        "timestamp": datetime.now().isoformat()
    })
    return jsonify({
        "success": True,
        "progress": progress
    })


@app.route('/api/reports/<submission_hash>', methods=['GET'])
def get_report(submission_hash):
    """Get PoD report for a submission."""
    try:
        report_dir = Path('test_outputs/pod_reports')
        report_files = list(report_dir.glob(f"{submission_hash}_*.json"))
        
        if not report_files:
            return jsonify({"success": False, "error": "Report not found"}), 404
        
        # Get most recent report
        latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
        
        with open(latest_report, 'r') as f:
            report = json.load(f)
        
        return jsonify({
            "success": True,
            "report": report
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/register-poc', methods=['POST'])
def register_poc_certificate():
    """Register a PoC certificate on the blockchain using Hardhat contracts."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        submission_hash = data.get('submission_hash')
        contributor = data.get('contributor')
        contributor_address = data.get('contributor_address', deployer_account)  # Use provided address or default
        registration_fee = data.get('registration_fee', 50.00)

        if not submission_hash or not contributor:
            return jsonify({"success": False, "error": "Missing submission_hash or contributor"}), 400

        # Get contribution data from PoC API first
        try:
            response = requests.get(f"{POC_API_URL}/api/archive/contributions/{submission_hash}", timeout=10)
            if response.status_code != 200:
                return jsonify({"success": False, "error": "Could not retrieve contribution data"}), 400

            contribution_data = response.json()
        except requests.RequestException:
            return jsonify({"success": False, "error": "Could not connect to PoC API"}), 500

        # Check if contribution is qualified
        if contribution_data.get('status') != 'qualified':
            return jsonify({"success": False, "error": "Contribution is not qualified for registration"}), 400

        # Extract evaluation data
        metals = contribution_data.get('metals', [])
        coherence = contribution_data.get('metadata', {}).get('coherence', 0)
        density = contribution_data.get('metadata', {}).get('density', 0)
        poc_score = contribution_data.get('metadata', {}).get('pod_score', 0)

        if not metals:
            return jsonify({"success": False, "error": "No metals assigned to contribution"}), 400

        # Use blockchain registration if available
        if blockchain_enabled and poc_registry_contract and synth_token_contract:
            try:
                print(f"🔗 Registering PoC certificate on blockchain for {submission_hash}")

                # Convert contributor to address (use provided address or hash-based address)
                if not contributor_address or contributor_address == deployer_account:
                    # Create a deterministic address from contributor string
                    import hashlib
                    contributor_hash = hashlib.sha256(contributor.encode()).hexdigest()[:40]
                    contributor_address = w3.to_checksum_address('0x' + contributor_hash)

                # Convert data for blockchain
                submission_hash_bytes = w3.to_bytes(hexstr=submission_hash)
                metals_strings = [str(m) for m in metals]

                # Check submission count for fee calculation
                submission_count = poc_registry_contract.functions.contributorSubmissionCount(contributor_address).call()
                fee_required = submission_count >= poc_registry_contract.functions.FREE_SUBMISSIONS().call()

                if fee_required:
                    fee_amount = poc_registry_contract.functions.REGISTRATION_FEE().call()
                    print(f"💰 Registration fee required: {w3.from_wei(fee_amount, 'ether')} ETH")
                else:
                    fee_amount = 0
                    print("🆓 Free registration (first 3 submissions)")

                # Register the certificate on blockchain
                tx_hash = poc_registry_contract.functions.registerCertificate(
                    submission_hash_bytes,
                    contributor_address,
                    contribution_data.get('title', ''),
                    contribution_data.get('category', 'scientific'),
                    metals_strings,
                    coherence,
                    density,
                    poc_score
                ).transact({
                    'from': deployer_account,
                    'value': fee_amount,
                    'gas': 500000
                })

                # Wait for transaction confirmation
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                print(f"✅ PoC certificate registered on blockchain! TX: {tx_hash.hex()}")

                return jsonify({
                    "success": True,
                    "transaction_hash": tx_hash.hex(),
                    "block_number": receipt.blockNumber,
                    "gas_used": receipt.gasUsed,
                    "fee_paid": float(w3.from_wei(fee_amount, 'ether')),
                    "contributor_address": contributor_address,
                    "metals_registered": metals,
                    "message": f"PoC certificate registered on Syntheverse Blockmine!"
                })

            except Exception as e:
                print(f"❌ Blockchain registration failed: {e}")
                return jsonify({"success": False, "error": f"Blockchain registration failed: {str(e)}"}), 500

        else:
            # Fallback: Use API registration when blockchain is not available
            print("⚠️  Blockchain not available, using API fallback")
            api_payload = {
                "submission_hash": submission_hash,
                "contributor": contributor,
                "registration_fee": registration_fee
            }

            try:
                response = requests.post(f"{POC_API_URL}/api/register-poc", json=api_payload, timeout=30)
                response_data = response.json()

                if response.status_code == 200 and response_data.get("success"):
                    return jsonify(response_data)
                else:
                    return jsonify({
                        "success": False,
                        "error": response_data.get("error", "API registration failed")
                    }), response.status_code

            except requests.RequestException as e:
                # Final fallback: Simulate registration
                return _simulate_registration(submission_hash, contributor, registration_fee)

    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


def _simulate_registration(submission_hash, contributor, registration_fee):
    """Simulate PoC registration when API is unavailable."""
    try:
        # Load contribution data from test outputs
        import json
        poc_archive_file = Path("test_outputs/poc_archive.json")
        contribution = None

        if poc_archive_file.exists():
            try:
                with open(poc_archive_file, 'r') as f:
                    archive_data = json.load(f)
                    # Find the contribution in the archive
                    for contrib_hash, contrib_data in archive_data.items():
                        if contrib_hash == submission_hash:
                            contribution = contrib_data
                            break
            except (json.JSONDecodeError, IOError):
                pass

        if not contribution:
            return jsonify({"success": False, "error": "PoC contribution not found"}), 404

        # Check if contribution is qualified
        if contribution.get('status') != 'qualified':
            return jsonify({"success": False, "error": "Contribution is not qualified for registration"}), 400

        # Simulate successful registration
        return jsonify({
            "success": True,
            "transaction_hash": f"sim-{submission_hash[:16]}",
            "blockchain_hash": submission_hash,
            "allocated_tokens": contribution.get('metadata', {}).get('reward', 1000),
            "message": "PoC certificate registered successfully (simulated)"
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"Simulation failed: {str(e)}"}), 500


# PDF functionality has been removed - certificates are registered on blockchain instead


if __name__ == '__main__':
    print("="*70)
    print("SYNTHVERSE PoC REGISTRATION WEB UI")
    print("="*70)
    print("\n🌐 Starting registration web server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print()

    print("🔗 Register PoC certificates on the blockchain")
    print("   Connects to L1 blockchain for permanent certificate registration")
    print("   Handles $50 registration fee and token allocation")

    print("\nPress Ctrl+C to stop the server")
    print("="*70)

    app.run(debug=True, host='0.0.0.0', port=5000)
