"""
POD (Proof-of-Discovery) Evaluator
Evaluates submissions against Syntheverse criteria and generates evaluation reports.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import logging
import re

logger = logging.getLogger(__name__)


class PODEvaluator:
    """
    Evaluates Proof-of-Discovery submissions.
    Integrates with RAG API for knowledge verification.
    """

    def __init__(self, rag_api_url: str = "http://localhost:8000"):
        """
        Initialize POD evaluator.

        Args:
            rag_api_url: URL of the RAG API service

        Raises:
            ValueError: If rag_api_url is invalid
        """
        if not rag_api_url or not isinstance(rag_api_url, str):
            raise ValueError("RAG API URL must be a non-empty string")

        self.rag_api_url = rag_api_url
        self.evaluation_criteria = {
            "novelty": 0.3,  # Weight for novelty of discovery
            "significance": 0.3,  # Weight for scientific/technical significance
            "verification": 0.2,  # Weight for verifiability
            "documentation": 0.2,  # Weight for quality of documentation
        }

        # Initialize logger
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def evaluate_submission(self, submission: Dict) -> Dict:
        """
        Evaluate a POD submission.

        Args:
            submission: Submission data including:
                - title: Title of the discovery
                - description: Description of the discovery
                - evidence: Evidence/documentation
                - category: Category of discovery
                - contributor: Contributor information

        Returns:
            Evaluation report with scores and recommendations

        Raises:
            ValueError: If submission data is invalid
            RuntimeError: If evaluation fails
        """
        try:
            # Validate input
            validation_result = self._validate_submission(submission)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid submission: {validation_result['errors']}")

            self.logger.info(f"Evaluating submission: {submission.get('id', 'unknown')}")

            # Extract submission components
            title = submission.get("title", "").strip()
            description = submission.get("description", "").strip()
            evidence = submission.get("evidence", "").strip()
            category = submission.get("category", "").strip()

            # Evaluate individual criteria
            novelty_score = self._evaluate_novelty(title, description, evidence)
            significance_score = self._evaluate_significance(title, description, category)
            verification_score = self._evaluate_verification(evidence)
            documentation_score = self._evaluate_documentation(title, description, evidence)

            # Calculate overall score
            overall_score = (
                novelty_score * self.evaluation_criteria["novelty"] +
                significance_score * self.evaluation_criteria["significance"] +
                verification_score * self.evaluation_criteria["verification"] +
                documentation_score * self.evaluation_criteria["documentation"]
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                novelty_score, significance_score, verification_score, documentation_score
            )

            # Determine status
            status = self._determine_status(overall_score)

            evaluation = {
                "submission_id": submission.get("id"),
                "timestamp": datetime.now().isoformat(),
                "scores": {
                    "novelty": round(novelty_score, 2),
                    "significance": round(significance_score, 2),
                    "verification": round(verification_score, 2),
                    "documentation": round(documentation_score, 2),
                },
                "overall_score": round(overall_score, 2),
                "status": status,
                "recommendations": recommendations,
                "evaluation_version": "1.0"
            }

            self.logger.info(f"Evaluation completed for {submission.get('id', 'unknown')}: score {overall_score:.2f}, status {status}")

            return evaluation

        except Exception as e:
            self.logger.error(f"Evaluation failed for submission {submission.get('id', 'unknown')}: {e}")
            raise RuntimeError(f"Evaluation failed: {e}") from e

    def _validate_submission(self, submission: Dict) -> Dict:
        """
        Validate submission data.

        Args:
            submission: Submission data to validate

        Returns:
            Dict with 'valid' boolean and 'errors' list
        """
        errors = []

        if not isinstance(submission, dict):
            errors.append("Submission must be a dictionary")
            return {"valid": False, "errors": errors}

        # Required fields
        required_fields = ["title", "description", "category"]
        for field in required_fields:
            if field not in submission:
                errors.append(f"Missing required field: {field}")
            elif not submission[field] or not isinstance(submission[field], str):
                errors.append(f"Field {field} must be a non-empty string")

        # Optional but recommended fields
        if "evidence" in submission and submission["evidence"]:
            if not isinstance(submission["evidence"], str):
                errors.append("Evidence must be a string")

        # Validate field lengths
        if "title" in submission and len(submission["title"].strip()) > 200:
            errors.append("Title too long (max 200 characters)")
        if "description" in submission and len(submission["description"].strip()) > 2000:
            errors.append("Description too long (max 2000 characters)")

        return {"valid": len(errors) == 0, "errors": errors}

    def _evaluate_novelty(self, title: str, description: str, evidence: str) -> float:
        """Evaluate novelty based on content uniqueness."""
        # Simple heuristic: longer, more specific content tends to be more novel
        content = f"{title} {description} {evidence}".lower()

        # Check for scientific/technical keywords
        scientific_keywords = ["research", "discovery", "novel", "new", "fractal", "hydrogen", "holography", "quantum"]
        keyword_score = sum(1 for keyword in scientific_keywords if keyword in content) / len(scientific_keywords)

        # Length and complexity score
        length_score = min(len(content) / 1000, 1.0)  # Normalize to 0-1

        # Uniqueness score (avoid generic terms)
        generic_terms = ["study", "analysis", "paper", "report"]
        uniqueness_penalty = sum(1 for term in generic_terms if term in content) * 0.1

        novelty_score = (keyword_score * 0.6 + length_score * 0.4) - uniqueness_penalty
        return max(0.0, min(1.0, novelty_score))

    def _evaluate_significance(self, title: str, description: str, category: str) -> float:
        """Evaluate scientific/technical significance."""
        content = f"{title} {description} {category}".lower()

        # Category-based significance
        category_multipliers = {
            "scientific": 1.0,
            "technological": 0.9,
            "research": 0.8,
            "discovery": 0.9,
            "innovation": 0.8
        }

        category_score = category_multipliers.get(category.lower(), 0.5)

        # Impact keywords
        impact_keywords = ["breakthrough", "revolutionary", "transformative", "significant", "major", "important"]
        impact_score = sum(1 for keyword in impact_keywords if keyword in content) / len(impact_keywords)

        significance_score = (category_score * 0.7 + impact_score * 0.3)
        return max(0.0, min(1.0, significance_score))

    def _evaluate_verification(self, evidence: str) -> float:
        """Evaluate verifiability based on evidence quality."""
        if not evidence or not evidence.strip():
            return 0.1  # Minimal score for no evidence

        evidence = evidence.lower()

        # Evidence quality indicators
        quality_indicators = [
            "experimental", "data", "results", "methodology", "validation",
            "measurement", "observation", "analysis", "proof", "evidence"
        ]

        quality_score = sum(1 for indicator in quality_indicators if indicator in evidence) / len(quality_indicators)

        # Length indicates thoroughness
        length_score = min(len(evidence) / 500, 1.0)

        verification_score = (quality_score * 0.7 + length_score * 0.3)
        return max(0.0, min(1.0, verification_score))

    def _evaluate_documentation(self, title: str, description: str, evidence: str) -> float:
        """Evaluate documentation quality."""
        content = f"{title} {description} {evidence}"

        # Check for completeness
        has_title = bool(title.strip())
        has_description = bool(description.strip())
        has_evidence = bool(evidence.strip())

        completeness_score = (has_title + has_description + has_evidence) / 3.0

        # Check for clarity (sentence structure, punctuation)
        sentences = re.split(r'[.!?]+', content)
        avg_sentence_length = sum(len(s.strip()) for s in sentences) / len(sentences) if sentences else 0

        # Ideal sentence length is 15-25 words
        clarity_score = 1.0 - min(abs(avg_sentence_length - 20) / 20, 1.0)

        documentation_score = (completeness_score * 0.6 + clarity_score * 0.4)
        return max(0.0, min(1.0, documentation_score))

    def _generate_recommendations(self, novelty: float, significance: float, verification: float, documentation: float) -> List[str]:
        """Generate improvement recommendations based on scores."""
        recommendations = []

        if novelty < 0.5:
            recommendations.append("Consider emphasizing what makes this discovery novel or unique")
        if significance < 0.5:
            recommendations.append("Provide more context on the scientific or technical significance")
        if verification < 0.5:
            recommendations.append("Include more detailed evidence, experimental data, or validation methods")
        if documentation < 0.5:
            recommendations.append("Improve clarity and completeness of the description and documentation")

        # General recommendations
        if len(recommendations) == 0:
            recommendations.append("Consider providing additional context or related work")

        return recommendations

    def _determine_status(self, overall_score: float) -> str:
        """Determine evaluation status based on overall score."""
        if overall_score >= 0.8:
            return "excellent"
        elif overall_score >= 0.6:
            return "good"
        elif overall_score >= 0.4:
            return "acceptable"
        else:
            return "needs_improvement"
    
    def verify_against_knowledge_base(self, submission: Dict) -> Dict:
        """
        Verify submission against RAG knowledge base.

        Args:
            submission: Submission data

        Returns:
            Verification results with similarity analysis

        Raises:
            RuntimeError: If verification fails
        """
        try:
            title = submission.get("title", "").strip()
            description = submission.get("description", "").strip()

            if not title:
                raise ValueError("Submission must have a title for verification")

            self.logger.info(f"Verifying submission '{title}' against knowledge base")

            # In a real implementation, this would query the RAG API
            # For now, simulate verification with heuristic analysis

            # Combine title and description for analysis
            content = f"{title} {description}".lower()

            # Simulate similarity checking (in real implementation, this would use embeddings)
            similarity_score = self._calculate_similarity_score(content)

            # Determine novelty threshold
            novelty_threshold = 0.7  # Configurable threshold
            is_novel = similarity_score < novelty_threshold

            # Generate mock related documents (in real implementation, these would come from RAG)
            related_documents = []
            if similarity_score > 0.3:
                related_documents = self._generate_related_documents(content, similarity_score)

            result = {
                "similarity_score": round(similarity_score, 3),
                "related_documents": related_documents,
                "is_novel": is_novel,
                "novelty_threshold": novelty_threshold,
                "verification_timestamp": datetime.now().isoformat(),
                "method": "heuristic_analysis"  # Would be "rag_api" in production
            }

            self.logger.info(f"Verification completed: similarity {similarity_score:.3f}, novel: {is_novel}")

            return result

        except Exception as e:
            self.logger.error(f"Knowledge base verification failed: {e}")
            raise RuntimeError(f"Verification failed: {e}") from e

    def _calculate_similarity_score(self, content: str) -> float:
        """Calculate similarity score using heuristic analysis."""
        # This is a placeholder - real implementation would use embeddings and RAG

        # Simple heuristic: check for common phrases that might indicate existing work
        common_phrases = [
            "research on", "study of", "analysis of", "investigation into",
            "exploration of", "examination of", "review of"
        ]

        phrase_matches = sum(1 for phrase in common_phrases if phrase in content)
        phrase_score = min(phrase_matches / 3, 1.0)  # Normalize

        # Length-based similarity (shorter content might be more unique)
        length_penalty = max(0, (len(content) - 100) / 500)  # Penalize very long content

        similarity_score = (phrase_score * 0.6 + length_penalty * 0.4)

        return min(similarity_score, 1.0)

    def _generate_related_documents(self, content: str, similarity_score: float) -> List[Dict]:
        """Generate mock related documents for testing."""
        # This would normally come from RAG API results
        mock_documents = [
            {
                "title": "Fractal Intelligence Research",
                "similarity": round(similarity_score * 0.9, 3),
                "source": "knowledge_base",
                "relevance": "high" if similarity_score > 0.7 else "medium"
            },
            {
                "title": "Hydrogen Holography Studies",
                "similarity": round(similarity_score * 0.8, 3),
                "source": "research_papers",
                "relevance": "medium"
            }
        ]

        # Only return documents above similarity threshold
        return [doc for doc in mock_documents if doc["similarity"] > 0.2]


if __name__ == "__main__":
    # Example usage
    evaluator = PODEvaluator()
    
    sample_submission = {
        "id": "pod-001",
        "title": "Sample Discovery",
        "description": "A novel finding in hydrogen holography",
        "evidence": "Research paper and experimental data",
        "category": "research",
        "contributor": "researcher-001",
    }
    
    evaluation = evaluator.evaluate_submission(sample_submission)
    print(json.dumps(evaluation, indent=2))


