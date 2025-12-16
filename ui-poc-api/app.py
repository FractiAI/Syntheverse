"""
PoC API Server
Flask API server that connects the Next.js frontend to the PoC backend.
"""

import os
import sys
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import hashlib
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Define base directory
base_dir = Path(__file__).parent.parent

from layer2.poc_server import PoCServer
from layer2.poc_archive import ContributionStatus, MetalType

# Try to import PDF generator (optional)
try:
    sys.path.insert(0, str(base_dir / "ui_web"))
    from pdf_generator import PODPDFGenerator
    pdf_generator_available = True
except ImportError:
    print("⚠️  PDF generator not available (reportlab not installed)")
    PODPDFGenerator = None
    pdf_generator_available = False

app = Flask(__name__)
CORS(app)  # Enable CORS for Next.js frontend

# Initialize PoC Server
print("Starting PoC API server initialization...")
try:
    # Use absolute paths for consistent file locations
    base_dir = Path(__file__).parent.parent
    groq_key = os.getenv('GROQ_API_KEY')

    print(f"Environment check - GROQ_API_KEY: {'set' if groq_key else 'NOT SET'}")
    if groq_key:
        print(f"GROQ key starts with: {groq_key[:15]}...")
    else:
        print("No GROQ_API_KEY found in environment")

    print(f"Initializing PoC Server...")
    poc_server = PoCServer(
        groq_api_key=groq_key,
        output_dir=str(base_dir / "test_outputs" / "poc_reports"),
        tokenomics_state_file=str(base_dir / "test_outputs" / "l2_tokenomics_state.json"),
        archive_file=str(base_dir / "test_outputs" / "poc_archive.json")
    )
    print("✓ PoC Server initialized successfully")
except Exception as e:
    print(f"⚠️  Warning: Failed to initialize PoC Server: {e}")
    print("   Some endpoints may not work until GROQ_API_KEY is set")
    poc_server = None

# Initialize PDF Generator
if pdf_generator_available:
    try:
        pdf_generator = PODPDFGenerator(output_dir=str(base_dir / "ui_web" / "test_outputs" / "pdf_reports"))
        print("✓ PDF Generator initialized successfully")
    except Exception as e:
        print(f"⚠️  Warning: Failed to initialize PDF Generator: {e}")
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
            return jsonify({
                "total_contributions": 0,
                "status_counts": {"draft": 0, "submitted": 0, "evaluating": 0, "qualified": 0, "unqualified": 0},
                "metal_counts": {"gold": 0, "silver": 0, "copper": 0},
                "unique_contributors": 0,
                "unique_content_hashes": 0,
                "last_updated": "2025-01-01T00:00:00Z"
            })
        stats = poc_server.get_archive_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/archive/contributions', methods=['GET'])
def get_contributions():
    """Get contributions with optional filters."""
    try:
        if not poc_server:
            # Return empty list when PoC server isn't available
            return jsonify([])

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
        result = []
        for contrib in contributions:
            result.append(convert_metals({
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

        return jsonify(result)
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
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename and file.filename.lower().endswith('.pdf'):
                    # Save the uploaded file
                    filename = secure_filename(f"{submission_hash}_{file.filename}")
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    pdf_path = filepath

        if not submission_hash or not title or not contributor:
            return jsonify({"error": "Missing required fields"}), 400

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
        result = poc_server.submit_contribution(
            submission_hash=submission_hash,
            title=title,
            contributor=contributor,
            text_content=text_content,
            pdf_path=pdf_path,
            category=category
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
        if contribution.get('status') != ContributionStatus.QUALIFIED:
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
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/register', methods=['GET'])
def register_poc():
    """Serve Synthechain registration page for PoC."""
    try:
        submission_hash = request.args.get('hash')
        contributor = request.args.get('contributor')

        if not submission_hash or not contributor:
            return """
            <html>
            <head><title>Synthechain PoC Registration</title></head>
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
            <head><title>Synthechain PoC Registration</title></head>
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
            <head><title>Synthechain PoC Registration</title></head>
            <body>
                <h1>Contribution Not Found</h1>
                <p>Could not find contribution with hash: {submission_hash}</p>
                <p><a href="javascript:window.close()">Close Window</a></p>
            </body>
            </html>
            """, 404

        # Check if contribution is qualified
        if contribution.get('status') != ContributionStatus.QUALIFIED:
            return f"""
            <html>
            <head><title>Synthechain PoC Registration</title></head>
            <body>
                <h1>Contribution Not Qualified</h1>
                <p>This contribution is not qualified for registration on Synthechain.</p>
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
            <head><title>Synthechain PoC Registration</title></head>
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
            <title>Synthechain PoC Registration</title>
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
                    <div class="logo">🔗 Synthechain</div>
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
                    <p>The registration fee for entering this PoC certificate and token allocations into the Synthechain blockchain is:</p>
                    <div class="fee-amount">$200 USD</div>
                    <p><small>This fee covers blockchain transaction costs and certificate minting.</small></p>
                </div>

                <div class="warning">
                    <h4>⚠️ Important Notice</h4>
                    <p>This action will permanently register your PoC on the Synthechain blockchain. Please verify all details above are correct before proceeding.</p>
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
                function proceedToRegistration() {{
                    // In a real implementation, this would redirect to a payment processor
                    // For now, show a message that the registration would proceed
                    alert('Registration functionality would integrate with a payment processor here.\\n\\nIn production, this would:\\n1. Process $200 payment\\n2. Mint PoC certificate on blockchain\\n3. Register token allocations\\n\\nThis is a demonstration page.');

                    // For demo purposes, just close the window
                    setTimeout(() => {{
                        window.close();
                    }}, 2000);
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
        <head><title>Synthechain PoC Registration</title></head>
        <body>
            <h1>Registration Error</h1>
            <p>An error occurred while processing your registration request.</p>
            <p>Error: {str(e)}</p>
            <p><a href="javascript:window.close()">Close Window</a></p>
        </body>
        </html>
        """, 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "poc-api"})


if __name__ == '__main__':
    print("Starting PoC API Server...")
    print("API will be available at: http://localhost:5001")
    print("Make sure GROQ_API_KEY is set in environment")
    app.run(host='0.0.0.0', port=5001, debug=True)
