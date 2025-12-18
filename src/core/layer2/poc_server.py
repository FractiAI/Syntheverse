"""
Proof of Contribution (PoC) Server
Archive-first evaluation with multi-metal support and Syntheverse Sandbox Map integration.
"""

import os
import json
import logging
from typing import Dict, Optional, List, Callable
from datetime import datetime
from pathlib import Path

from .tokenomics_state import TokenomicsState, Epoch, ContributionTier
from .poc_archive import PoCArchive, ContributionStatus, MetalType
from .sandbox_map import SandboxMap

# Load GROQ_API_KEY using centralized utility
from core.utils import load_groq_api_key

# Set up logger
logger = logging.getLogger(__name__)


class PoCServer:
    """
    Proof of Contribution server with archive-first evaluation.
    Supports multi-metal contributions and full lifecycle tracking.
    """
    
    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        output_dir: str = "test_outputs/poc_reports",
        tokenomics_state_file: str = "test_outputs/l2_tokenomics_state.json",
        archive_file: str = "test_outputs/poc_archive.json"
    ):
        """
        Initialize PoC server.
        
        Args:
            groq_api_key: Groq API key (defaults to GROQ_API_KEY env var)
            output_dir: Directory for output reports
            tokenomics_state_file: Path to tokenomics state file
            archive_file: Path to PoC archive file
        """
        # Initialize Grok API client
        self.groq_api_key = groq_api_key or load_groq_api_key()
        if not self.groq_api_key:
            raise ValueError(
                "Groq API key not provided. Set GROQ_API_KEY environment variable or pass groq_api_key parameter."
            )
        
        try:
            from openai import OpenAI
            self.groq_client = OpenAI(
                api_key=self.groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.groq_client.models.list()
            logger.info("Grok API initialized successfully")
        except Exception as e:
            raise ValueError(f"Failed to initialize Grok API client: {e}")
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.tokenomics = TokenomicsState(state_file=tokenomics_state_file)
        self.archive = PoCArchive(archive_file=archive_file)
        self.sandbox_map = SandboxMap(self.archive)

        logger.info("PoC Archive initialized")
        logger.info("Syntheverse Sandbox Map initialized")

        # Run initial cleanup of any existing test submissions
        cleanup_result = self.cleanup_test_submissions()
        if cleanup_result.get("cleaned_count", 0) > 0:
            logger.info(f"Cleaned up {cleanup_result['cleaned_count']} existing test submissions")
    
    def submit_contribution(
        self,
        submission_hash: str,
        title: str,
        contributor: str,
        text_content: Optional[str] = None,
        pdf_path: Optional[str] = None,
        category: Optional[str] = None,
        is_test: bool = False,
        progress_callback: Optional[Callable[[str, str], None]] = None
    ) -> Dict:
        """
        Submit a contribution for evaluation.
        Archive-first: Immediately adds to archive as DRAFT.
        
        Args:
            submission_hash: Unique submission identifier
            title: Contribution title
            contributor: Contributor identifier
            text_content: Text content (if available)
            pdf_path: Path to PDF file (if available)
            category: Category (scientific/tech/alignment)
            progress_callback: Optional progress callback function
        
        Returns:
            Submission result
        """
        if progress_callback:
            progress_callback("submitting", "Submitting contribution to archive...")
        
        # Extract text from PDF if needed
        if not text_content and pdf_path:
            text_content = self._extract_text_from_pdf(pdf_path)
            if not text_content:
                return {
                    "success": False,
                    "error": "Failed to extract text from PDF"
                }
        
        if not text_content:
            return {
                "success": False,
                "error": "No text content or PDF path provided"
            }
        
        # Add to archive as DRAFT (archive-first rule)
        contribution = self.archive.add_contribution(
            submission_hash=submission_hash,
            title=title,
            contributor=contributor,
            text_content=text_content,
            status=ContributionStatus.DRAFT,
            category=category,
            is_test=is_test
        )
        
        # Update status to PENDING
        self.archive.update_contribution(
            submission_hash,
            status=ContributionStatus.PENDING
        )

        # Automatically evaluate the contribution
        if progress_callback:
            progress_callback("evaluating", "Automatically evaluating contribution...")

        try:
            evaluation_result = self.evaluate_contribution(
                submission_hash=submission_hash,
                progress_callback=progress_callback
            )

            if evaluation_result.get("success"):
                return {
                    "success": True,
                    "submission_hash": submission_hash,
                    "status": "evaluated",
                    "evaluation": evaluation_result,
                    "archive_entry": contribution
                }
            else:
                # Evaluation failed, but submission succeeded
                return {
                    "success": True,
                    "submission_hash": submission_hash,
                    "status": "submitted",
                    "evaluation_error": evaluation_result.get("error", "Evaluation failed"),
                    "archive_entry": contribution
                }
        except Exception as e:
            # Evaluation failed, but submission succeeded
            return {
                "success": True,
                "submission_hash": submission_hash,
                "status": "submitted",
                "evaluation_error": str(e),
                "archive_entry": contribution
            }
    
    def evaluate_contribution(
        self,
        submission_hash: str,
        progress_callback: Optional[Callable[[str, str], None]] = None
    ) -> Dict:
        """
        Evaluate a contribution using archive-first redundancy detection.
        
        Args:
            submission_hash: Submission identifier
            progress_callback: Optional progress callback
        
        Returns:
            Evaluation result with multi-metal support
        """
        # Get contribution from archive
        contribution = self.archive.get_contribution(submission_hash)
        if not contribution:
            return {
                "success": False,
                "error": "Contribution not found in archive"
            }
        
        # Update status to EVALUATING
        self.archive.update_contribution(
            submission_hash,
            status=ContributionStatus.EVALUATING
        )
        
        if progress_callback:
            progress_callback("evaluating", "Evaluating contribution with archive-first redundancy check...")
        
        # Archive-first redundancy check
        # Get ALL contributions from archive for redundancy comparison
        all_archive_content = self.archive.get_all_content_for_redundancy_check()

        # For first submission, set redundancy to 0
        is_first_submission = len([c for c in all_archive_content if c["submission_hash"] != submission_hash]) == 0

        # Check for exact duplicates
        content_hash = contribution["content_hash"]
        duplicate_history = self.archive.get_content_hash_history(content_hash)
        
        if len(duplicate_history) > 1:
            # Multiple contributions with same content hash
            first_contrib = duplicate_history[0]
            if first_contrib["submission_hash"] != submission_hash:
                # This is a duplicate
                self.archive.update_contribution(
                    submission_hash,
                    status=ContributionStatus.UNQUALIFIED,
                    metadata={
                        "evaluation_status": "duplicate",
                        "first_submission": first_contrib["submission_hash"],
                        "reason": "Exact duplicate of existing contribution"
                    }
                )
                return {
                    "success": False,
                    "error": f"Duplicate contribution. First submission: {first_contrib['submission_hash'][:16]}...",
                    "duplicate_info": {
                        "first_submission": first_contrib["submission_hash"],
                        "reason": "Archive-first rule: Duplicate detected against entire archive"
                    }
                }
        
        # Get redundancy report from sandbox map
        redundancy_report = self.sandbox_map.get_redundancy_report(submission_hash)
        
        # Prepare evaluation query with archive context
        evaluation_query = self._prepare_evaluation_query(
            contribution,
            all_archive_content,
            redundancy_report
        )
        
        # Call Grok API for evaluation
        if progress_callback:
            progress_callback("calling_llm", "Calling Grok API for HHFE evaluation...")
        
        try:
            logger.info(f"Starting Grok API evaluation for {submission_hash}")

            # Update status to show evaluation is in progress
            self.archive.update_contribution(
                submission_hash,
                metadata={"evaluation_status": "preparing_evaluation", "progress": "🤖 Preparing evaluation data for Grok AI..."}
            )

            # Prepare evaluation context
            self.archive.update_contribution(
                submission_hash,
                metadata={"evaluation_status": "analyzing_archive", "progress": "🔍 Analyzing archive for redundancy detection..."}
            )

            evaluation_result = self._call_grok_api(evaluation_query)
            logger.info(f"Grok API evaluation completed for {submission_hash}")

            # Store the raw Grok response for user display
            self.archive.update_contribution(
                submission_hash,
                metadata={
                    "evaluation_status": "grok_response_received",
                    "progress": "📨 Grok AI response received - processing evaluation...",
                    "grok_raw_response": evaluation_result
                }
            )

        except Exception as e:
            logger.error(f"Grok API evaluation failed for {submission_hash}: {e}")
            self.archive.update_contribution(
                submission_hash,
                status=ContributionStatus.UNQUALIFIED,
                metadata={
                    "evaluation_error": str(e),
                    "error_type": "api_failure",
                    "evaluation_status": "failed",
                    "progress": f"Evaluation failed: {str(e)[:50]}..."
                }
            )
            return {
                "success": False,
                "error": f"AI evaluation failed: {str(e)[:100]}..."
            }
        
        # Parse evaluation result (extract scores and metals)
        self.archive.update_contribution(
            submission_hash,
            metadata={"evaluation_status": "extracting_scores", "progress": "📊 Extracting coherence, density, and redundancy scores..."}
        )

        parsed_evaluation = self._parse_evaluation_result(evaluation_result, contribution)

        # Override redundancy for first submission
        if is_first_submission:
            parsed_evaluation["redundancy"] = 0.0
            parsed_evaluation["redundancy_analysis"] = "First submission in archive - zero redundancy"

        # Determine qualification status
        self.archive.update_contribution(
            submission_hash,
            metadata={"evaluation_status": "determining_qualification", "progress": "⚖️ Determining contribution qualification and metal assignment..."}
        )

        qualified = self._determine_qualification(parsed_evaluation)
        status = ContributionStatus.QUALIFIED if qualified else ContributionStatus.UNQUALIFIED
        
        # Calculate allocations for each metal (multi-metal support)
        self.archive.update_contribution(
            submission_hash,
            metadata={"evaluation_status": "calculating_rewards", "progress": "💰 Calculating SYNTH token rewards based on evaluation scores..."}
        )

        allocations = []
        if qualified and parsed_evaluation.get("metals"):
            for metal in parsed_evaluation["metals"]:
                allocation = self._calculate_allocation_for_metal(
                    submission_hash,
                    parsed_evaluation,
                    metal
                )
                if allocation:
                    allocations.append(allocation)

                    # Record the allocation in tokenomics state
                    self.tokenomics.record_allocation(
                        submission_hash=submission_hash,
                        contributor=contribution["contributor"],
                        allocation=allocation["allocation"],
                        coherence=parsed_evaluation.get("coherence", 0)
                    )

        # Store allocations in metadata for frontend access
        evaluation_with_allocations = parsed_evaluation.copy()
        evaluation_with_allocations["allocations"] = allocations

        # Update archive with evaluation results and allocations
        self.archive.update_contribution(
            submission_hash,
            status=status,
            metals=parsed_evaluation.get("metals", []),
            metadata=evaluation_with_allocations
        )

        return {
            "success": True,
            "submission_hash": submission_hash,
            "evaluation": parsed_evaluation,
            "status": status.value,
            "qualified": qualified,
            "metals": parsed_evaluation.get("metals", []),
            "allocations": allocations,
            "redundancy_report": redundancy_report
        }
    
    def _prepare_evaluation_query(
        self,
        contribution: Dict,
        archive_content: List[Dict],
        redundancy_report: Dict
    ) -> str:
        """Prepare evaluation query with archive context."""
        # Build archive history text for redundancy context
        archive_history = []
        for arch_contrib in archive_content[:50]:  # Limit to 50 for token management
            if arch_contrib["submission_hash"] != contribution["submission_hash"]:
                archive_history.append({
                    "hash": arch_contrib["submission_hash"][:16] + "...",
                    "title": arch_contrib["title"],
                    "status": arch_contrib["status"],
                    "metals": arch_contrib.get("metals", [])
                })
        
        archive_text = "\n".join([
            f"- {h['title']} ({h['hash']}) [{','.join(h['metals'])}] - {h['status']}"
            for h in archive_history
        ])
        
        return f"""
EVALUATE THIS CONTRIBUTION (Proof of Contribution):

Title: {contribution['title']}
Content: {contribution['text_content'][:8000]}...

---
ARCHIVE CONTEXT (Archive-First Redundancy Check):
Total contributions in archive: {len(archive_content)}
Recent archive entries for redundancy comparison:
{archive_text if archive_text else "No previous contributions"}

Redundancy Report:
- High redundancy: {redundancy_report.get('high_redundancy', 0)}
- Moderate overlap: {redundancy_report.get('moderate_overlap', 0)}
- Related contributions: {redundancy_report.get('related', 0)}

---
EVALUATION REQUIREMENTS:

1. Evaluate using Hydrogen-Holographic Fractal Engine (HHFE) metrics:
   - Coherence (Φ): 0-10000 (fractal grammar closure, structural consistency)
   - Density (ρ): 0-10000 (information richness, depth, and foundational significance)
     * Foundational papers defining core concepts: 9000-10000
     * Substantial research contributions: 7000-9000
     * Significant insights/applications: 5000-7000
     * Basic contributions: 2000-5000
   - Redundancy (R): 0-10000 (compare against ENTIRE archive, lower is better)

2. Determine METALS (multi-metal support - contribution can contain multiple):
   - GOLD: Discovery/Scientific contribution
   - SILVER: Technology contribution  
   - COPPER: Alignment contribution
   - A single contribution may contain Gold + Silver + Copper

3. Calculate PoC Score:
   PoC Score = ((coherence + density) / 2) × ((10000 - redundancy) / 10000)

4. Return JSON format:
{{
    "coherence": <0-10000>,
    "density": <0-10000>,
    "redundancy": <0-10000>,
    "metals": ["gold", "silver", "copper"],  // Can be multiple
    "pod_score": <calculated>,
    "tier_justification": "...",
    "redundancy_analysis": "...",
    "status": "approved" or "rejected"
}}
"""
    
    def _call_grok_api(self, query: str) -> str:
        """Call Grok API for evaluation."""
        # Use the system prompt from the original pod_server
        # For now, using a simplified version - in production, include full system prompt
        system_prompt = """You are Syntheverse PoC Reviewer evaluating contributions using the Hydrogen-Holographic Fractal Engine (HHFE)."""

        logger.debug(f"Calling Grok API with evaluation query (length: {len(query)} characters)")

        try:
            logger.debug("Sending evaluation request to Grok AI")

            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.0,  # Deterministic evaluation for consistency
                max_tokens=2000,
                timeout=300  # 5 minute timeout for complex evaluations - let Grok finish
            )

            logger.info("Grok AI evaluation completed")
            logger.debug(f"Response length: {len(response.choices[0].message.content)} characters")

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Grok API call failed: {e}")
            raise e
    
    def _parse_evaluation_result(self, result: str, contribution: Dict) -> Dict:
        """Parse Grok API evaluation result."""
        # Try to extract JSON from response - look for JSON within markdown code blocks first
        import re

        # Try to find JSON within ```json ... ``` blocks
        json_block_match = re.search(r'```json\s*\n(.*?)\n\s*```', result, re.DOTALL)
        if json_block_match:
            json_str = json_block_match.group(1).strip()
            json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
        else:
            # Fallback to finding any JSON object
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
        
        if json_match:
            try:
                eval_dict = json.loads(json_match.group(0))
                
                # Extract metals
                metals = []
                metals_raw = eval_dict.get("metals", [])
                if isinstance(metals_raw, list):
                    for m in metals_raw:
                        m_lower = m.lower()
                        if "gold" in m_lower:
                            metals.append(MetalType.GOLD)
                        if "silver" in m_lower:
                            metals.append(MetalType.SILVER)
                        if "copper" in m_lower:
                            metals.append(MetalType.COPPER)
                
                # Ensure at least one metal
                if not metals:
                    metals = [MetalType.GOLD]  # Default
                
                # Calculate correct PoC score
                coherence = float(eval_dict.get("coherence", 0))
                density = float(eval_dict.get("density", 0))
                redundancy = float(eval_dict.get("redundancy", 0))

                # PoC Score = ((coherence + density) / 2) × ((10000 - redundancy) / 10000)
                pod_score = ((coherence + density) / 2) * ((10000 - redundancy) / 10000)

                return {
                    "coherence": coherence,
                    "density": density,
                    "redundancy": redundancy,
                    "metals": metals,
                    "pod_score": pod_score,
                    "tier_justification": eval_dict.get("tier_justification", ""),
                    "redundancy_analysis": eval_dict.get("redundancy_analysis", ""),
                    "status": eval_dict.get("status", "rejected"),
                    "raw_response": result
                }
            except json.JSONDecodeError:
                pass
        
        # Fallback parsing
        return {
            "coherence": 5000.0,
            "density": 5000.0,
            "redundancy": 5000.0,
            "metals": [MetalType.GOLD],
            "pod_score": 0.0,
            "tier_justification": "Fallback evaluation",
            "redundancy_analysis": "Could not parse evaluation result",
            "status": "rejected",
            "raw_response": result
        }
    
    def _determine_qualification(self, evaluation: Dict) -> bool:
        """Determine if contribution qualifies based on scores."""
        coherence = evaluation.get("coherence", 0)
        density = evaluation.get("density", 0)
        redundancy = evaluation.get("redundancy", 10000)
        status = evaluation.get("status", "rejected")
        
        # Qualification criteria
        # Must have minimum scores and low redundancy
        if status == "rejected":
            return False
        
        if coherence < 2000 or density < 2000:
            return False
        
        if redundancy > 8000:  # Too redundant
            return False
        
        return True
    
    def _calculate_allocation_for_metal(
        self,
        submission_hash: str,
        evaluation: Dict,
        metal: MetalType
    ) -> Optional[Dict]:
        """Calculate token allocation for a specific metal."""
        pod_score = evaluation.get("pod_score", 0)
        density = evaluation.get("density", 0)
        
        # Determine epoch from density
        epoch = self.tokenomics.qualify_epoch(density)
        if not epoch:
            return None
        
        # Convert metal to tier
        tier_map = {
            MetalType.GOLD: ContributionTier.GOLD,
            MetalType.SILVER: ContributionTier.SILVER,
            MetalType.COPPER: ContributionTier.COPPER,
        }
        tier = tier_map.get(metal)
        if not tier:
            return None
        
        # Calculate allocation
        allocation = self.tokenomics.calculate_allocation(pod_score, epoch, tier)
        
        if allocation.get("success"):
            return {
                "metal": metal.value,
                "epoch": epoch.value,
                "tier": tier.value,
                "allocation": allocation
            }
        
        return None
    
    def _extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """Extract text from PDF file and clean up formatting."""
        try:
            import PyPDF2
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = "\n".join([page.extract_text() for page in reader.pages])
                if not text.strip():
                    return None
        except Exception:
            try:
                import pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    text = "\n".join([page.extract_text() for page in pdf.pages])
                    if not text.strip():
                        return None
            except Exception:
                return None

        # Clean up the extracted text formatting
        import re

        # Remove excessive whitespace and normalize line breaks
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        # Replace multiple newlines with double newlines (paragraph breaks)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        # Remove excessive whitespace at line starts/ends
        text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s+$', '', text, flags=re.MULTILINE)
        # Ensure paragraphs are properly separated
        text = re.sub(r'([.!?])\s*\n\s*([A-Z])', r'\1\n\n\2', text)

        return text.strip()
    
    def get_sandbox_map(self, **kwargs) -> Dict:
        """Get Syntheverse Sandbox Map."""
        return self.sandbox_map.export_map_for_visualization(**kwargs)
    
    def get_archive_statistics(self) -> Dict:
        """Get archive statistics."""
        return self.archive.get_statistics()

    def get_contributor_submission_count(self, contributor: str) -> int:
        """Get the number of submissions by a contributor."""
        return self.archive.get_contributor_submission_count(contributor)

    def get_epoch_info(self) -> Dict:
        """Get epoch information."""
        return self.tokenomics.get_epoch_info()
    
    def get_tokenomics_statistics(self) -> Dict:
        """Get tokenomics statistics."""
        return self.tokenomics.get_statistics()

    def cleanup_test_submissions(self) -> Dict:
        """
        Clean up test submissions from the archive.
        Removes all contributions marked as test submissions.

        Returns:
            Cleanup statistics
        """
        test_submissions = []

        # Find all test submissions (marked or detected by patterns)
        for submission_hash, contribution in self.archive.archive["contributions"].items():
            is_test = contribution.get("is_test", False)

            # Also detect by patterns (for existing submissions)
            if not is_test:
                title = contribution.get("title", "").lower()
                contributor = contribution.get("contributor", "").lower()
                is_test = (
                    'test' in title or 'test' in contributor or
                    'demo' in title or 'demo' in contributor or
                    submission_hash.endswith('-test-123') or
                    submission_hash.endswith('-123') or
                    'blockchain-test' in submission_hash
                )

            if is_test:
                test_submissions.append(submission_hash)

        cleaned_count = 0
        for submission_hash in test_submissions:
            try:
                # Remove from all indexes
                contribution = self.archive.archive["contributions"].get(submission_hash)
                if contribution:
                    content_hash = contribution.get("content_hash")
                    contributor = contribution.get("contributor")
                    metals = contribution.get("metals", [])
                    status = contribution.get("status")

                    # Remove from content hash index
                    if content_hash and content_hash in self.archive.archive["content_hashes"]:
                        if submission_hash in self.archive.archive["content_hashes"][content_hash]:
                            self.archive.archive["content_hashes"][content_hash].remove(submission_hash)
                            if not self.archive.archive["content_hashes"][content_hash]:
                                del self.archive.archive["content_hashes"][content_hash]

                    # Remove from status index
                    if status and status in self.archive.archive["by_status"]:
                        if submission_hash in self.archive.archive["by_status"][status]:
                            self.archive.archive["by_status"][status].remove(submission_hash)

                    # Remove from contributor index
                    if contributor and contributor in self.archive.archive["by_contributor"]:
                        if submission_hash in self.archive.archive["by_contributor"][contributor]:
                            self.archive.archive["by_contributor"][contributor].remove(submission_hash)
                            if not self.archive.archive["by_contributor"][contributor]:
                                del self.archive.archive["by_contributor"][contributor]

                    # Remove from metal indexes
                    for metal in metals:
                        if metal in self.archive.archive["by_metal"]:
                            if submission_hash in self.archive.archive["by_metal"][metal]:
                                self.archive.archive["by_metal"][metal].remove(submission_hash)

                    # Remove the contribution itself
                    del self.archive.archive["contributions"][submission_hash]
                    cleaned_count += 1

            except Exception as e:
                logger.warning(f"Failed to clean up test submission {submission_hash}: {e}")
                continue

        # Save the cleaned archive
        self.archive.save_archive()

        # Update metadata
        self.archive.archive["metadata"]["total_contributions"] = len(self.archive.archive["contributions"])
        self.archive.save_archive()

        return {
            "success": True,
            "cleaned_count": cleaned_count,
            "remaining_contributions": len(self.archive.archive["contributions"]),
            "message": f"Cleaned up {cleaned_count} test submissions"
        }
