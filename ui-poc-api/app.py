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

from layer2.poc_server import PoCServer
from layer2.poc_archive import ContributionStatus, MetalType

app = Flask(__name__)
CORS(app)  # Enable CORS for Next.js frontend

# Initialize PoC Server
try:
    poc_server = PoCServer(
        groq_api_key=None,  # Uses GROQ_API_KEY env var
        output_dir="test_outputs/poc_reports",
        tokenomics_state_file="test_outputs/l2_tokenomics_state.json",
        archive_file="test_outputs/poc_archive.json"
    )
    print("✓ PoC Server initialized successfully")
except Exception as e:
    print(f"⚠️  Warning: Failed to initialize PoC Server: {e}")
    print("   Some endpoints may not work until GROQ_API_KEY is set")
    poc_server = None

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/api/archive/statistics', methods=['GET'])
def get_archive_statistics():
    """Get archive statistics."""
    try:
        if not poc_server:
            return jsonify({"error": "PoC Server not initialized"}), 503
        stats = poc_server.get_archive_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/archive/contributions', methods=['GET'])
def get_contributions():
    """Get contributions with optional filters."""
    try:
        if not poc_server:
            return jsonify({"error": "PoC Server not initialized"}), 503
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

        # Convert to API format
        result = []
        for contrib in contributions:
            result.append({
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
            })

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

        return jsonify({
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
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/submit', methods=['POST'])
def submit_contribution():
    """Submit a new contribution."""
    try:
        if not poc_server:
            return jsonify({"error": "PoC Server not initialized"}), 503
        data = request.json
        submission_hash = data.get('submission_hash')
        title = data.get('title')
        contributor = data.get('contributor')
        text_content = data.get('text_content', '')
        category = data.get('category', 'scientific')

        if not submission_hash or not title or not contributor:
            return jsonify({"error": "Missing required fields"}), 400

        # Submit to PoC server
        result = poc_server.submit_contribution(
            submission_hash=submission_hash,
            title=title,
            contributor=contributor,
            text_content=text_content,
            category=category
        )

        return jsonify({
            "success": True,
            "submission_hash": result["submission_hash"],
            "status": result["status"]
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

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


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
            return jsonify({"error": "PoC Server not initialized"}), 503
        epoch_info = poc_server.get_epoch_info()
        return jsonify(epoch_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/tokenomics/statistics', methods=['GET'])
def get_tokenomics_statistics():
    """Get tokenomics statistics."""
    try:
        if not poc_server:
            return jsonify({"error": "PoC Server not initialized"}), 503
        stats = poc_server.get_tokenomics_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "poc-api"})


if __name__ == '__main__':
    print("Starting PoC API Server...")
    print("API will be available at: http://localhost:5001")
    print("Make sure GROQ_API_KEY is set in environment")
    app.run(host='0.0.0.0', port=5001, debug=True)
