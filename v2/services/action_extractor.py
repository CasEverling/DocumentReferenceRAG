"""
Action Extractor - Static Class
Extracts diagnostic/repair steps from manual sections

Location: microservices/action_extractor.py
Usage:
    from action_extractor import ActionExtractor
    
    actions = ActionExtractor.extract(
        section_references=[{"section_id": "RAG_1_45"}],
        query="What should I check?",
        context={...}
    )
"""

from typing import Dict, Any, List, Optional
from llm_client import LLMClient
from document_loader import DocumentLoader
import logging

logger = logging.getLogger(__name__)


class ActionExtractor:
    """
    Static class for extracting actions from manual sections
    All methods are class methods - no instantiation needed
    """
    
    # Class-level clients (initialized once)
    _llm_client: Optional[LLMClient] = None
    _doc_loader: Optional[DocumentLoader] = None
    
    @classmethod
    def _get_llm_client(cls) -> LLMClient:
        """Get or create LLM client"""
        if cls._llm_client is None:
            cls._llm_client = LLMClient(default_model="gpt-4o")
        return cls._llm_client
    
    @classmethod
    def _get_doc_loader(cls) -> DocumentLoader:
        """Get or create document loader"""
        if cls._doc_loader is None:
            cls._doc_loader = DocumentLoader()
        return cls._doc_loader
    
    @classmethod
    def extract(
        cls,
        section_references: List[Dict[str, Any]],
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract diagnostic/repair actions from manual sections
        
        Args:
            section_references: List of section refs
                [
                    {"section_id": "RAG_1_45"},
                    {"section_id": "RAG_1_50"}
                ]
            query: User's query
            context: Conversation context (optional)
                {
                    "vehicle": {...},
                    "reported_issues": [...],
                    "attempted_solutions": [...]
                }
        
        Returns:
            {
                "actions": [
                    {
                        "step_number": 1,
                        "action": "Check for loose connections...",
                        "tools_required": ["visual inspection"],
                        "specification": null,
                        "safety_warning": null,
                        "expected_result": "...",
                        "source_sections": [
                            {
                                "section_id": "RAG_1_45",
                                "section_name": "...",
                                "page_numbers": [45, 46]
                            }
                        ]
                    }
                ],
                "summary": "Found 3 steps from 2 sections"
            }
        """
        llm = cls._get_llm_client()
        doc_loader = cls._get_doc_loader()
        
        if not section_references:
            return {
                "actions": [],
                "summary": "No section references provided"
            }
        
        # Load full text from document sections
        logger.info(f"Loading content for {len(section_references)} sections...")
        sections = doc_loader.get_sections_content(section_references)
        
        if not sections:
            return {
                "actions": [],
                "summary": "No sections found"
            }
        
        logger.info(f"Loaded {len(sections)} sections")
        
        # Build system prompt
        system_prompt = """You are a master mechanic extracting diagnostic procedures from service manual sections.

Extract step-by-step procedures from the manual text. For EACH step:
1. Write a clear, actionable description
2. List required tools
3. Include specifications (torque, resistance, clearances) EXACTLY as written in manual
4. Note safety warnings
5. Cite which section(s) this step comes from

CRITICAL RULES:
- ONLY include steps explicitly mentioned in the manual text
- Preserve exact specifications from manual (don't approximate)
- Order steps logically (diagnose before repair)
- Flag safety warnings prominently
- Every action MUST cite its source section

Return JSON array:
[
  {
    "step_number": 1,
    "action": "Detailed description of what to do",
    "tools_required": ["tool1", "tool2"] or [],
    "specification": "Exact spec from manual (e.g., '18-22 ft-lbs')" or null,
    "safety_warning": "Warning text from manual" or null,
    "expected_result": "What should happen" or null,
    "source_sections": [
      {
        "section_id": "RAG_X_Y",
        "section_name": "Section name",
        "page_numbers": [X, Y]
      }
    ]
  }
]

If manual says "dealer only" or "special tools required", note it in the action."""

        # Build section texts with metadata for citation
        sections_text = ""
        for i, section in enumerate(sections, 1):
            sections_text += f"\n\n{'='*80}\n"
            sections_text += f"SECTION {i}: {section['section_name']}\n"
            sections_text += f"Section ID: {section['section_id']}\n"
            sections_text += f"Pages: {section['page_numbers']}\n"
            sections_text += f"{'='*80}\n\n"
            sections_text += section['full_text']
        
        user_prompt = f"""Vehicle context:
{context or {}}

User query:
{query}

Manual sections:
{sections_text}

Extract diagnostic/repair steps from these manual sections."""

        # Call LLM
        logger.info(f"Extracting actions for query: {query[:100]}...")
        
        try:
            result = llm.generate_json(
                system_prompt=system_prompt,
                prompt=user_prompt,
                temperature=0.2,  # Very low temperature for accurate extraction
                max_tokens=3000
            )
            
            # Handle different response formats
            if isinstance(result, dict) and 'actions' in result:
                actions = result['actions']
            elif isinstance(result, list):
                actions = result
            else:
                actions = []
            
            logger.info(f"Extracted {len(actions)} actions")
            
            return {
                "actions": actions,
                "summary": f"Found {len(actions)} diagnostic steps from {len(sections)} manual sections"
            }
        
        except Exception as e:
            logger.error(f"Error extracting actions: {e}")
            return {
                "actions": [],
                "summary": f"Error occurred: {str(e)}"
            }
    
    @classmethod
    def extract_from_text(
        cls,
        manual_text: str,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract actions directly from manual text (without loading from DB)
        Useful if text is already loaded
        
        Args:
            manual_text: Raw manual text
            query: User's query
            context: Conversation context (optional)
        
        Returns:
            List of actions
        """
        llm = cls._get_llm_client()
        
        system_prompt = """Extract step-by-step diagnostic procedures from this manual text.

Return JSON array of actions with: step_number, action, tools_required, specification, safety_warning.
Only include steps explicitly in the manual."""

        user_prompt = f"""Context: {context or {}}
Query: {query}

Manual text:
{manual_text}

Extract diagnostic steps."""

        try:
            result = llm.generate_json(
                system_prompt=system_prompt,
                prompt=user_prompt,
                temperature=0.2,
                max_tokens=3000
            )
            
            if isinstance(result, dict) and 'actions' in result:
                return result['actions']
            elif isinstance(result, list):
                return result
            else:
                return []
        
        except Exception as e:
            logger.error(f"Error extracting from text: {e}")
            return []


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == '__main__':
    # Example 1: Extract from section references
    print("=" * 80)
    print("Example 1: Extract Actions from References")
    print("=" * 80)
    
    result = ActionExtractor.extract(
        section_references=[
            {"section_id": "RAG_1_45"}
        ],
        query="What should I check for a cylinder misfire?",
        context={
            "vehicle": {
                "brand": "Toyota",
                "model": "Camry",
                "year": 2018
            },
            "reported_issues": ["P0301 - Cylinder 1 misfire"],
            "attempted_solutions": ["replaced spark plugs"]
        }
    )
    
    print(f"Summary: {result['summary']}")
    print(f"\nActions:")
    for action in result['actions'][:3]:  # Show first 3
        print(f"\nStep {action['step_number']}: {action['action']}")
        if action.get('tools_required'):
            print(f"  Tools: {', '.join(action['tools_required'])}")
        if action.get('specification'):
            print(f"  Spec: {action['specification']}")
    
    # Example 2: Extract from raw text
    print("\n" + "=" * 80)
    print("Example 2: Extract from Raw Text")
    print("=" * 80)
    
    manual_text = """
    DIAGNOSTIC PROCEDURE:
    1. Check ignition coil connections
    2. Test coil resistance (0.4-0.9 ohms)
    3. WARNING: Disconnect battery before testing
    """
    
    actions = ActionExtractor.extract_from_text(
        manual_text=manual_text,
        query="How to test ignition coil?",
        context={"vehicle": {"brand": "Toyota"}}
    )
    
    print(f"Extracted {len(actions)} actions from raw text")
    for action in actions:
        print(f"  - {action['action']}")