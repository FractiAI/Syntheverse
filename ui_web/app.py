"""
Syntheverse PoD Submission Web UI
Browser-based interface for submitting documents for PoD scoring.
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
from layer2.pod_server import PODServer
from ui_pod_submission import PODSubmissionUI
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

# Initialize UI components
ui = PODSubmissionUI()
pdf_generator = PODPDFGenerator() if PODPDFGenerator else None

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


def send_pod_report_email(to_email: str, submission: dict, submission_hash: str):
    """
    Send PoD report email to submitter with PDF report and certificate.
    
    Args:
        to_email: Recipient email address (from user's form input)
        submission: Submission data
        submission_hash: Submission hash
    """
    # Validate email address
    if not to_email or '@' not in to_email:
        print(f"❌ Invalid email address: {to_email}")
        return False
    
    # Email functionality removed - this function is no longer used
    # All results are displayed in the UI instead
    print(f"ℹ️  Email functionality removed - results are displayed in the UI")
    return False
    
    # Get PoD report
    report_dir = Path('test_outputs/pod_reports')
    report_files = list(report_dir.glob(f"{submission_hash}_*.json"))
    
    report_data = None
    if report_files:
        latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
        with open(latest_report, 'r') as f:
            report_data = json.load(f)
    
    # Create email
    msg = MIMEMultipart()
    msg['From'] = app.config['FROM_EMAIL']
    msg['To'] = to_email
    msg['Subject'] = f"Syntheverse PoD Report - {submission.get('title', 'Your Submission')}"
    
    # Generate PDF report
    report_pdf_path = None
    certificate_pdf_path = None
    
    try:
        report_pdf_path = pdf_generator.generate_report_pdf(submission, report_data)
    except Exception as e:
        print(f"Warning: Failed to generate PDF report: {e}")
    
    # Generate certificate if tokens were allocated
    allocation = report_data.get('allocation') if report_data else None
    if allocation and allocation.get('success'):
        try:
            certificate_pdf_path = pdf_generator.generate_certificate_pdf(submission, allocation)
        except Exception as e:
            print(f"Warning: Failed to generate certificate: {e}")
    
    # Email body
    body = f"""
Hello,

Thank you for submitting your document to the Syntheverse Proof-of-Discovery protocol.

Submission Details:
- Title: {submission.get('title', 'N/A')}
- Submission Hash: {submission_hash}
- Category: {submission.get('category', 'N/A')}
- Status: {submission.get('status', 'pending')}
- Submitted: {submission.get('timestamp', 'N/A')}

"""
    
    if report_data:
        evaluation = report_data.get('evaluation', {})
        
        body += f"""
Evaluation Results:
- Coherence: {evaluation.get('coherence', 0):.0f}/10000
- Density: {evaluation.get('density', 0):.0f}/10000
- Novelty: {evaluation.get('novelty', 0):.0f}/10000
- PoD Score: {report_data.get('pod_score', 0):.2f}/10000
- Tier: {evaluation.get('tier', 'N/A')}
- Qualified Epoch: {report_data.get('qualified_epoch', 'N/A')}

"""
        
        if allocation and allocation.get('success'):
            body += f"""
🎉 CONGRATULATIONS! Your contribution has been approved and tokens have been allocated.

Token Allocation:
- Epoch: {allocation.get('epoch', 'N/A').title()}
- Tier: {allocation.get('tier', 'N/A').title()}
- SYNTH Tokens Allocated: {allocation.get('reward', 0):,.2f}
- PoD Score: {allocation.get('pod_score', 0):.2f}

📜 CERTIFICATE AWARDED:
A Proof-of-Discovery certificate has been generated and attached to this email.
This certificate serves as official recognition of your contribution to the Syntheverse knowledge base.

🔗 BLOCKCHAIN REGISTRATION:
To register your certificate on the Syntheverse blockchain:

1. Visit the Syntheverse platform: http://localhost:5000
2. Navigate to "Register Certificate" section
3. Enter your submission hash: {submission_hash}
4. Verify your contributor ID: {submission.get('contributor', 'N/A')}
5. Submit the registration transaction

Your certificate will be permanently recorded on the blockchain, providing
immutable proof of your contribution.

"""
        elif evaluation.get('status') == 'rejected':
            body += f"""
Status: REJECTED

Your submission did not meet the minimum requirements for token allocation.
Reason: {evaluation.get('reasoning', 'Density score below threshold')}

You can review the detailed report attached to this email.
"""
        else:
            body += "\nYour submission is being processed.\n"
    
    body += f"""

📄 ATTACHED DOCUMENTS:
- PoD Report (PDF): Detailed evaluation report with all scores and metrics

"""
    
    if certificate_pdf_path:
        body += "- PoD Certificate (PDF): Official certificate of discovery\n"
    
    body += f"""

For more information, visit: http://localhost:5000

Best regards,
Syntheverse PoD System
"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach PDF report
    if report_pdf_path and os.path.exists(report_pdf_path):
        with open(report_pdf_path, 'rb') as f:
            part = MIMEBase('application', 'pdf')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename=pod_report_{submission_hash}.pdf'
            )
            msg.attach(part)
    
    # Attach certificate PDF if available
    if certificate_pdf_path and os.path.exists(certificate_pdf_path):
        with open(certificate_pdf_path, 'rb') as f:
            part = MIMEBase('application', 'pdf')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename=pod_certificate_{submission_hash}.pdf'
            )
            msg.attach(part)
    
    # Send email
    try:
        print(f"📧 Sending email to {to_email}...")
        server = smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT'])
        server.starttls()
        server.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent successfully to {to_email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP authentication failed. Please check your SMTP credentials in the 'Email Config' tab: {e}"
        print(f"❌ {error_msg}")
        print(f"   Email address {to_email} is valid, but SMTP login failed")
        return False
    except smtplib.SMTPException as e:
        error_msg = f"SMTP error: {e}"
        print(f"❌ {error_msg}")
        print(f"   Could not send email to {to_email}")
        return False
    except Exception as e:
        error_msg = f"Error sending email: {e}"
        print(f"❌ {error_msg}")
        print(f"   Could not send email to {to_email}")
        return False


if __name__ == '__main__':
    print("="*70)
    print("SYNTHVERSE PoD SUBMISSION WEB UI")
    print("="*70)
    print("\n🌐 Starting web server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print()
    
    print("📄 All PoD evaluation results are displayed in the UI")
    print("   No email configuration needed - view results in the 'Results' tab")
    
    print("\nPress Ctrl+C to stop the server")
    print("="*70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
