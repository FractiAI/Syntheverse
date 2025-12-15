"""
Proof of Contribution (PoC) Server
Archive-first evaluation with multi-metal support and Syntheverse Sandbox Map integration.
"""

import os
import json
from typing import Dict, Optional, List, Callable
from datetime import datetime
from pathlib import Path

# Try to load .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

from .tokenomics_state import TokenomicsState, Epoch, ContributionTier
from .poc_archive import PoCArchive, ContributionStatus, MetalType
from .sandbox_map import SandboxMap


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
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
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
            print("✓ Grok API initialized successfully")
        except Exception as e:
            raise ValueError(f"Failed to initialize Grok API client: {e}")
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.tokenomics = TokenomicsState(state_file=tokenomics_state_file)
        self.archive = PoCArchive(archive_file=archive_file)
        self.sandbox_map = SandboxMap(self.archive)
        
        print("✓ PoC Archive initialized")
        print("✓ Syntheverse Sandbox Map initialized")
    
    def submit_contribution(
        self,
        submission_hash: str,
        title: str,
        contributor: str,
        text_content: Optional[str] = None,
        pdf_path: Optional[str] = None,
        category: Optional[str] = None,
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
            category=category
        )
        
        # Update status to SUBMITTED
        self.archive.update_contribution(
            submission_hash,
            status=ContributionStatus.SUBMITTED
        )
        
        return {
            "success": True,
            "submission_hash": submission_hash,
            "status": "submitted",
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
            evaluation_result = self._call_grok_api(evaluation_query)
        except Exception as e:
            self.archive.update_contribution(
                submission_hash,
                status=ContributionStatus.UNQUALIFIED,
                metadata={"evaluation_error": str(e)}
            )
            return {
                "success": False,
                "error": f"Evaluation failed: {e}"
            }
        
        # Parse evaluation result (extract scores and metals)
        parsed_evaluation = self._parse_evaluation_result(evaluation_result, contribution)
        
        # Determine qualification status
        qualified = self._determine_qualification(parsed_evaluation)
        status = ContributionStatus.QUALIFIED if qualified else ContributionStatus.UNQUALIFIED
        
        # Update archive with evaluation results
        self.archive.update_contribution(
            submission_hash,
            status=status,
            metals=parsed_evaluation.get("metals", []),
            metadata=parsed_evaluation
        )
        
        # Calculate allocations for each metal (multi-metal support)
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
   - Density (ρ): 0-10000 (structural contribution per fractal unit)
   - Redundancy (R): 0-10000 (compare against ENTIRE archive, lower is better)

2. Determine METALS (multi-metal support - contribution can contain multiple):
   - GOLD: Discovery/Scientific contribution
   - SILVER: Technology contribution  
   - COPPER: Alignment contribution
   - A single contribution may contain Gold + Silver + Copper

3. Calculate PoC Score:
   PoC Score = (coherence/10000) × (density/10000) × ((10000 - redundancy)/10000) × 10000

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
        
        response = self.groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    def _parse_evaluation_result(self, result: str, contribution: Dict) -> Dict:
        """Parse Grok API evaluation result."""
        # Try to extract JSON from response
        import re
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
                
                return {
                    "coherence": float(eval_dict.get("coherence", 0)),
                    "density": float(eval_dict.get("density", 0)),
                    "redundancy": float(eval_dict.get("redundancy", 0)),
                    "metals": metals,
                    "pod_score": float(eval_dict.get("pod_score", 0)),
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
        """Extract text from PDF file."""
        try:
            import PyPDF2
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = "\n".join([page.extract_text() for page in reader.pages])
                return text if text.strip() else None
        except Exception:
            try:
                import pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    text = "\n".join([page.extract_text() for page in pdf.pages])
                    return text if text.strip() else None
            except Exception:
                return None
    
    def get_sandbox_map(self, **kwargs) -> Dict:
        """Get Syntheverse Sandbox Map."""
        return self.sandbox_map.export_map_for_visualization(**kwargs)
    
    def get_archive_statistics(self) -> Dict:
        """Get archive statistics."""
        return self.archive.get_statistics()
    
    def get_epoch_info(self) -> Dict:
        """Get epoch information."""
        return self.tokenomics.get_epoch_info()
    
    def get_tokenomics_statistics(self) -> Dict:
        """Get tokenomics statistics."""
        return self.tokenomics.get_statistics()
