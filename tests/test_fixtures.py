#!/usr/bin/env python3
"""
Test Fixtures and Utilities
Common setup/teardown utilities, test data generators, and service mocks for Syntheverse tests
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, MagicMock, patch

# Add test framework to path
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir))

from test_framework import test_config, TestFixtures as BaseTestFixtures

class TestDataGenerators:
    """Generate test data for various test scenarios"""

    @staticmethod
    def generate_sample_contributions(count: int = 5) -> List[Dict[str, Any]]:
        """Generate sample contributions for testing"""
        contributions = []

        base_contributions = [
            {
                "title": "Fractal Intelligence in Neural Networks",
                "content": "This paper explores how fractal patterns enhance neural network performance through recursive coherence and phase alignment.",
                "category": "scientific",
                "contributor": "researcher-001@example.com"
            },
            {
                "title": "Hydrogen Holographic Data Structures",
                "content": "Novel approach to data organization using hydrogen geometric principles and holographic storage paradigms.",
                "category": "technological",
                "contributor": "researcher-002@example.com"
            },
            {
                "title": "Blockchain Consensus via Fractal Resonance",
                "content": "Implementing consensus mechanisms using fractal resonance patterns for enhanced security and efficiency.",
                "category": "scientific",
                "contributor": "researcher-003@example.com"
            },
            {
                "title": "AI Safety through Recursive Self-Reflection",
                "content": "Developing AI safety mechanisms using recursive self-reflection and fractal awareness patterns.",
                "category": "alignment",
                "contributor": "researcher-004@example.com"
            },
            {
                "title": "Decentralized Knowledge Networks",
                "content": "Building decentralized knowledge networks using fractal topology and hydrogen holographic principles.",
                "category": "technological",
                "contributor": "researcher-005@example.com"
            }
        ]

        for i in range(min(count, len(base_contributions))):
            contrib = base_contributions[i].copy()
            contrib["id"] = f"test-contrib-{i+1:03d}"
            contrib["timestamp"] = f"2024-01-{i+1:02d}T10:00:00Z"
            contributions.append(contrib)

        return contributions

    @staticmethod
    def generate_evaluation_results(contributions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate evaluation results for contributions"""
        results = []

        tier_patterns = {
            0: {"tier": "gold", "coherence": 92, "density": 88, "novelty": 85},
            1: {"tier": "silver", "coherence": 78, "density": 75, "novelty": 72},
            2: {"tier": "gold", "coherence": 95, "density": 91, "novelty": 88},
            3: {"tier": "copper", "coherence": 68, "density": 65, "novelty": 62},
            4: {"tier": "silver", "coherence": 82, "density": 79, "novelty": 76}
        }

        for i, contrib in enumerate(contributions):
            pattern = tier_patterns.get(i % len(tier_patterns), tier_patterns[0])

            evaluation = {
                "submission_hash": f"hash_{i+1:03d}",
                "title": contrib["title"],
                "contributor": contrib["contributor"],
                "coherence": pattern["coherence"],
                "density": pattern["density"],
                "novelty": pattern["novelty"],
                "tier": pattern["tier"],
                "status": "approved",
                "evaluation_timestamp": f"2024-01-{i+2:02d}T11:00:00Z"
            }

            results.append(evaluation)

        return results

    @staticmethod
    def generate_tokenomics_data() -> Dict[str, Any]:
        """Generate sample tokenomics data"""
        return {
            "current_epoch": "pioneer",
            "epoch_number": 2,
            "total_supply": 90000000000000,  # 90T SYNTH
            "total_allocated": 4500000000000,  # 4.5T allocated
            "total_rewards": 3800000000000,   # 3.8T in rewards
            "epoch_allocations": {
                "founder": 1000000000000,     # 1T
                "pioneer": 2800000000000,     # 2.8T
                "community": 0,
                "ecosystem": 0
            },
            "tier_distributions": {
                "gold": 1800000000000,        # 1.8T
                "silver": 1200000000000,      # 1.2T
                "copper": 800000000000        # 0.8T
            }
        }

    @staticmethod
    def generate_sandbox_map_data() -> Dict[str, Any]:
        """Generate sample sandbox map data"""
        return {
            "dimensions": [
                {"id": "coherence", "name": "Coherence", "description": "Structural coherence metric"},
                {"id": "density", "name": "Density", "description": "Information density metric"},
                {"id": "novelty", "name": "Novelty", "description": "Novel contribution metric"},
                {"id": "impact", "name": "Impact", "description": "Potential impact metric"}
            ],
            "nodes": [
                {"id": "node_1", "label": "Fractal Intelligence", "x": 100, "y": 100, "size": 20, "color": "#FFD700"},
                {"id": "node_2", "label": "Hydrogen Holography", "x": 200, "y": 150, "size": 18, "color": "#C0C0C0"},
                {"id": "node_3", "label": "Neural Networks", "x": 150, "y": 200, "size": 16, "color": "#CD7F32"},
                {"id": "node_4", "label": "Blockchain Consensus", "x": 250, "y": 100, "size": 15, "color": "#FFD700"},
                {"id": "node_5", "label": "AI Safety", "x": 300, "y": 180, "size": 14, "color": "#CD7F32"}
            ],
            "edges": [
                {"source": "node_1", "target": "node_2", "strength": 0.8},
                {"source": "node_1", "target": "node_3", "strength": 0.9},
                {"source": "node_2", "target": "node_4", "strength": 0.7},
                {"source": "node_3", "target": "node_5", "strength": 0.6},
                {"source": "node_4", "target": "node_5", "strength": 0.8}
            ]
        }


class ServiceMocks:
    """Mock services for testing"""

    @staticmethod
    def create_mock_rag_api_response(query: str, include_sources: bool = True) -> Dict[str, Any]:
        """Create mock RAG API response"""
        response = {
            "query": query,
            "answer": f"Mock response to query: {query}. This is a comprehensive answer about Syntheverse concepts.",
            "processing_time": 0.15,
            "num_sources": 3 if include_sources else 0
        }

        if include_sources:
            response["sources"] = [
                {
                    "text": "Mock source text about fractal intelligence",
                    "score": 0.87,
                    "pdf_filename": "fractal_intelligence.pdf",
                    "chunk_index": 0,
                    "metadata": {"title": "Fractal Intelligence Paper", "page": 1}
                },
                {
                    "text": "Mock source text about hydrogen holography",
                    "score": 0.82,
                    "pdf_filename": "hydrogen_holography.pdf",
                    "chunk_index": 1,
                    "metadata": {"title": "Hydrogen Holography Study", "page": 3}
                },
                {
                    "text": "Mock source text about PoC protocol",
                    "score": 0.79,
                    "pdf_filename": "poc_protocol.pdf",
                    "chunk_index": 2,
                    "metadata": {"title": "PoC Protocol Documentation", "page": 5}
                }
            ]

        return response

    @staticmethod
    def create_mock_poc_api_response(endpoint: str) -> Dict[str, Any]:
        """Create mock PoC API response for different endpoints"""

        if endpoint == "health":
            return {"status": "healthy", "timestamp": "2024-01-01T12:00:00Z"}

        elif endpoint == "archive/statistics":
            return {
                "total_contributions": 42,
                "contributions_by_status": {"approved": 38, "pending": 4, "rejected": 0},
                "contributions_by_metal": {"gold": 12, "silver": 15, "copper": 11, "unqualified": 4}
            }

        elif endpoint == "archive/contributions":
            return {
                "contributions": TestDataGenerators.generate_sample_contributions(3)
            }

        elif endpoint == "sandbox-map":
            return TestDataGenerators.generate_sandbox_map_data()

        elif endpoint == "tokenomics/epoch-info":
            return {
                "current_epoch": "pioneer",
                "epoch_name": "Pioneer Phase",
                "epoch_description": "Early adoption and validation phase"
            }

        elif endpoint == "tokenomics/statistics":
            return TestDataGenerators.generate_tokenomics_data()

        return {"error": "Unknown endpoint"}

    @staticmethod
    def mock_requests_get(url: str, **kwargs) -> Mock:
        """Mock requests.get for API calls"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.1

        # Parse URL to determine response
        if "health" in url:
            mock_response.json.return_value = {"status": "healthy", "timestamp": "2024-01-01T12:00:00Z"}
        elif "archive/statistics" in url:
            mock_response.json.return_value = ServiceMocks.create_mock_poc_api_response("archive/statistics")
        elif "archive/contributions" in url:
            mock_response.json.return_value = ServiceMocks.create_mock_poc_api_response("archive/contributions")
        elif "sandbox-map" in url:
            mock_response.json.return_value = ServiceMocks.create_mock_poc_api_response("sandbox-map")
        elif "epoch-info" in url:
            mock_response.json.return_value = ServiceMocks.create_mock_poc_api_response("tokenomics/epoch-info")
        elif "tokenomics/statistics" in url:
            mock_response.json.return_value = ServiceMocks.create_mock_poc_api_response("tokenomics/statistics")
        else:
            mock_response.json.return_value = {"mock": "response"}

        return mock_response

    @staticmethod
    def mock_requests_post(url: str, **kwargs) -> Mock:
        """Mock requests.post for API calls"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.2

        if "query" in url:
            # RAG API query
            data = kwargs.get("json", {})
            query = data.get("query", "test query")
            mock_response.json.return_value = ServiceMocks.create_mock_rag_api_response(query)
        elif "submit" in url:
            # PoC submission
            mock_response.json.return_value = {
                "submission_hash": "mock_hash_1234567890abcdef",
                "status": "submitted",
                "message": "Submission received successfully"
            }
        elif "evaluate" in url:
            # PoC evaluation
            mock_response.json.return_value = {
                "success": True,
                "evaluation": {
                    "coherence": 85,
                    "density": 80,
                    "novelty": 75,
                    "tier": "gold",
                    "status": "approved"
                }
            }
        else:
            mock_response.json.return_value = {"mock": "post_response"}

        return mock_response


class EnvironmentHelper:
    """Test environment setup and teardown utilities"""

    def __init__(self):
        self.temp_dirs = []
        self.temp_files = []
        self.original_cwd = os.getcwd()

    def create_temp_dir(self, prefix: str = "test_") -> Path:
        """Create a temporary directory"""
        temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
        self.temp_dirs.append(temp_dir)
        return temp_dir

    def create_temp_file(self, content: str = "", suffix: str = ".txt") -> Path:
        """Create a temporary file with content"""
        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        temp_file = Path(temp_path)
        self.temp_files.append(temp_file)
        return temp_file

    def change_to_temp_dir(self):
        """Change to a temporary directory"""
        temp_dir = self.create_temp_dir()
        os.chdir(temp_dir)
        return temp_dir

    def restore_cwd(self):
        """Restore original working directory"""
        os.chdir(self.original_cwd)

    def cleanup(self):
        """Clean up all temporary resources"""
        # Clean up temp files
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except Exception:
                pass

        # Clean up temp directories
        for temp_dir in self.temp_dirs:
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
            except Exception:
                pass

        self.temp_files.clear()
        self.temp_dirs.clear()
        self.restore_cwd()


class TestContextManagers:
    """Context managers for test setup"""

    @staticmethod
    def mock_api_calls():
        """Context manager to mock all API calls"""
        import requests

        return patch.multiple(
            'requests',
            get=ServiceMocks.mock_requests_get,
            post=ServiceMocks.mock_requests_post
        )

    @staticmethod
    def temp_environment():
        """Context manager for temporary test environment"""
        env = EnvironmentHelper()
        try:
            yield env
        finally:
            env.cleanup()

    @staticmethod
    def mock_file_operations():
        """Context manager to mock file operations"""
        return patch.multiple(
            'builtins',
            open=Mock(return_value=Mock()),
            Path=Mock()
        )


# Convenience functions for common test operations
def create_test_contribution(**overrides):
    """Create a test contribution with optional overrides"""
    base = TestDataGenerators.generate_sample_contributions(1)[0]
    base.update(overrides)
    return base

def mock_successful_evaluation():
    """Create mock for successful evaluation"""
    return {
        "success": True,
        "evaluation": {
            "coherence": 87,
            "density": 83,
            "novelty": 79,
            "tier": "gold",
            "status": "approved",
            "reasoning": "Excellent coherence and novel contribution"
        }
    }

def mock_failed_evaluation():
    """Create mock for failed evaluation"""
    return {
        "success": False,
        "error": "Evaluation failed due to insufficient content",
        "evaluation": {
            "coherence": 45,
            "density": 42,
            "novelty": 38,
            "tier": "unqualified",
            "status": "rejected",
            "reasoning": "Content lacks sufficient depth and novelty"
        }
    }


# Export commonly used functions
__all__ = [
    'TestDataGenerators',
    'ServiceMocks',
    'EnvironmentHelper',
    'TestContextManagers',
    'create_test_contribution',
    'mock_successful_evaluation',
    'mock_failed_evaluation'
]


