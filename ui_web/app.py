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

from layer1.node import SyntheverseNode
from layer1.contracts.poc_contract import POCContract
# PDF generator is optional - only used if needed
try:
    from pdf_generator import PODPDFGenerator
except ImportError:
    PODPDFGenerator = None

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'syntheverse-pod-secret-key'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('test_outputs', exist_ok=True)

# Initialize blockchain components
node = SyntheverseNode("registration-node", data_dir="test_outputs/blockchain")
poc_contract = POCContract()

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
                # Create a temporary submission to get the hash first
                from layer1.node import SyntheverseNode
                temp_node = SyntheverseNode("temp", data_dir="test_outputs/blockchain")
                temp_submission = {
                    "title": Path(filepath).stem.replace("_", " ").title(),
                    "description": f"PDF submission: {Path(filepath).name}",
                    "category": category or "scientific",
                    "contributor": contributor,
                    "evidence": filepath,
                }
                temp_result = temp_node.submit_pod(temp_submission)
                submission_hash_preview = temp_result.get("submission_hash")
                
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
    """Register a PoC certificate on the blockchain."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        submission_hash = data.get('submission_hash')
        contributor = data.get('contributor')
        registration_fee = data.get('registration_fee', 200.00)

        if not submission_hash or not contributor:
            return jsonify({"success": False, "error": "Missing submission_hash or contributor"}), 400

        # Load contribution data from test outputs (simulating PoC server)
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

        # Submit to blockchain
        poc_submission = {
            "title": contribution.get('title', 'Unknown'),
            "description": contribution.get('text_content', '')[:500],  # Truncate for blockchain
            "category": contribution.get('category', 'scientific'),
            "contributor": contributor,
            "evidence": f"PoC Archive Hash: {submission_hash}",
            "metals": contribution.get('metals', []),
            "poc_score": contribution.get('metadata', {}).get('pod_score', 0),  # Note: still uses pod_score in metadata
        }

        # Submit to PoC contract
        blockchain_hash = poc_contract.submit_poc(poc_submission)

        # Record evaluation from existing data
        evaluation = {
            "coherence": contribution.get('metadata', {}).get('coherence', 0),
            "density": contribution.get('metadata', {}).get('density', 0),
            "novelty": contribution.get('metadata', {}).get('redundancy', 0),
            "status": "approved"
        }

        poc_contract.record_evaluation(blockchain_hash, evaluation)

        # Allocate tokens
        allocation_result = poc_contract.allocate_tokens(blockchain_hash)

        # Create blockchain transaction
        transaction_data = {
            "type": "poc_registration",
            "submission_hash": blockchain_hash,
            "contributor": contributor,
            "registration_fee": registration_fee,
            "timestamp": datetime.now().isoformat(),
            "poc_data": poc_submission
        }

        # Submit transaction to blockchain
        tx_result = node.submit_transaction(transaction_data)

        if tx_result.get("success"):
            return jsonify({
                "success": True,
                "transaction_hash": tx_result.get("transaction_hash", blockchain_hash),
                "blockchain_hash": blockchain_hash,
                "allocated_tokens": allocation_result.get("allocation", {}).get("reward", 0) if allocation_result.get("success") else 0,
                "message": "PoC certificate registered successfully on the blockchain"
            })
        else:
            return jsonify({"success": False, "error": "Blockchain transaction failed"}), 500

    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


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
    print("   Handles $200 registration fee and token allocation")

    print("\nPress Ctrl+C to stop the server")
    print("="*70)

    app.run(debug=True, host='0.0.0.0', port=5000)
