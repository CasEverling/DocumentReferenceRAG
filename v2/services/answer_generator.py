"""
Answer Generator - Static Class
Generates natural language responses from structured actions

Location: microservices/answer_generator.py
Usage:
    from answer_generator import AnswerGenerator
    
    answer = AnswerGenerator.generate(
        actions=[...],
        context={...},
        last_messages=[...]
    )
"""

from typing import Dict, Any, List, Optional
from llm_client import LLMClient
import logging

logger = logging.getLogger(__name__)


class AnswerGenerator:
    """
    Static class for generating natural language answers
    All methods are class methods - no instantiation needed
    """
    
    # Class-level LLM client (initialized once)
    _llm_client: Optional[LLMClient] = None
    
    @classmethod
    def _get_llm_client(cls) -> LLMClient:
        """Get or create LLM client"""
        if cls._llm_client is None:
            cls._llm_client = LLMClient(default_model="gpt-4o")
        return cls._llm_client
    
    @classmethod
    def generate(
        cls,
        actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
        last_messages: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate natural language answer from structured actions
        
        Args:
            actions: List of diagnostic/repair actions
                [
                    {
                        "step_number": 1,
                        "action": "Check connections...",
                        "tools_required": [...],
                        "specification": "...",
                        "safety_warning": "...",
                        "source_sections": [...]
                    }
                ]
            context: Conversation context (optional)
                {
                    "vehicle": {...},
                    "reported_issues": [...],
                    "attempted_solutions": [...]
                }
            last_messages: Previous conversation (optional)
                [
                    {"role": "user", "content": "..."},
                    {"role": "assistant", "content": "..."}
                ]
        
        Returns:
            {
                "answer": "Since you've already replaced...",
                "tone": "conversational",
                "word_count": 247
            }
        """
        llm = cls._get_llm_client()
        
        # If no actions, return helpful message
        if not actions:
            return {
                "answer": "I couldn't find specific diagnostic steps for this issue in the manual. Could you provide more details about the problem?",
                "tone": "helpful",
                "word_count": 0
            }
        
        # Build conversation history
        conversation = ""
        if last_messages:
            conversation = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in last_messages[-5:]
            ])
        
        # Build system prompt
        system_prompt = """You are an experienced fleet mechanic helping another mechanic diagnose and repair a vehicle.

Write in a natural, conversational tone - mechanic to mechanic. This is a colleague, not a customer.

Key guidelines:
- Reference the vehicle's history in context (e.g., "Since you already replaced the spark plugs...")
- Explain WHY each action matters, not just WHAT to do
- Emphasize safety warnings prominently with ⚠️ 
- Be specific with torque specs and measurements
- Use clear, actionable language
- Keep it concise but informative
- Show empathy - acknowledge the work already done
- Use casual mechanic language when appropriate

Structure:
1. Acknowledge what they've already tried (from context)
2. Walk through the diagnostic steps
3. Explain what each step tests for and why
4. Mention any safety warnings prominently
5. End with encouragement or next steps

Do NOT:
- Use overly formal language
- Repeat the entire conversation
- Just list steps without explanation
- Ignore what they've already done"""

        # Format actions for the prompt
        actions_text = ""
        for action in actions:
            actions_text += f"\nStep {action['step_number']}: {action['action']}\n"
            if action.get('tools_required'):
                actions_text += f"  Tools: {', '.join(action['tools_required'])}\n"
            if action.get('specification'):
                actions_text += f"  Spec: {action['specification']}\n"
            if action.get('safety_warning'):
                actions_text += f"  ⚠️ SAFETY: {action['safety_warning']}\n"
            if action.get('expected_result'):
                actions_text += f"  Expected: {action['expected_result']}\n"
        
        # Build context string
        context_str = ""
        if context:
            vehicle = context.get('vehicle', {})
            context_str = f"""Vehicle: {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')}
Reported issues: {context.get('reported_issues', [])}
Already tried: {context.get('attempted_solutions', [])}
Measurements: {context.get('measurements', [])}"""
        
        user_prompt = f"""{context_str}

Recent conversation:
{conversation}

Recommended diagnostic steps from manual:
{actions_text}

Generate a helpful, conversational response that walks through these diagnostic steps."""

        # Call LLM
        logger.info(f"Generating answer for {len(actions)} actions...")
        
        try:
            answer = llm.generate(
                system_prompt=system_prompt,
                prompt=user_prompt,
                temperature=0.7,  # Higher temperature for natural conversation
                max_tokens=2000
            )
            
            word_count = len(answer.split())
            logger.info(f"Generated answer: {word_count} words")
            
            return {
                "answer": answer,
                "tone": "conversational",
                "word_count": word_count
            }
        
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "answer": "I encountered an error generating a response. Please try again.",
                "tone": "error",
                "word_count": 0
            }
    
    @classmethod
    def generate_simple(
        cls,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a simple conversational response without structured actions
        Useful for general queries or small talk
        
        Args:
            message: User's message
            context: Optional context
        
        Returns:
            Conversational response string
        """
        llm = cls._get_llm_client()
        
        system_prompt = """You are a helpful fleet mechanic assistant.
Respond conversationally and naturally. Be friendly but professional."""

        context_str = ""
        if context:
            vehicle = context.get('vehicle', {})
            if vehicle:
                context_str = f"\nVehicle: {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')}"
        
        prompt = f"""{context_str}

User message: {message}

Respond helpfully."""

        try:
            return llm.generate(
                system_prompt=system_prompt,
                prompt=prompt,
                temperature=0.7,
                max_tokens=500
            )
        except Exception as e:
            logger.error(f"Error in simple generation: {e}")
            return "I'm here to help! Could you tell me more about what you need?"
    
    @classmethod
    def format_actions_as_text(cls, actions: List[Dict[str, Any]]) -> str:
        """
        Helper method to format actions as plain text
        
        Args:
            actions: List of action dicts
        
        Returns:
            Formatted text string
        """
        if not actions:
            return "No actions available"
        
        text = ""
        for action in actions:
            text += f"\nStep {action['step_number']}: {action['action']}\n"
            
            if action.get('tools_required'):
                text += f"Tools needed: {', '.join(action['tools_required'])}\n"
            
            if action.get('specification'):
                text += f"Specification: {action['specification']}\n"
            
            if action.get('safety_warning'):
                text += f"⚠️ Safety Warning: {action['safety_warning']}\n"
            
            if action.get('expected_result'):
                text += f"Expected result: {action['expected_result']}\n"
        
        return text


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == '__main__':
    # Example 1: Generate from actions
    print("=" * 80)
    print("Example 1: Generate Answer from Actions")
    print("=" * 80)
    
    actions = [
        {
            "step_number": 1,
            "action": "Check for loose or corroded connections at ignition coil",
            "tools_required": ["visual inspection"],
            "specification": None,
            "safety_warning": None,
            "expected_result": "Connections should be tight and free of corrosion"
        },
        {
            "step_number": 2,
            "action": "Test ignition coil primary resistance",
            "tools_required": ["multimeter"],
            "specification": "0.4-0.9 ohms at 20°C",
            "safety_warning": "Disconnect battery negative terminal before testing",
            "expected_result": "Reading should be within specification range"
        }
    ]
    
    result = AnswerGenerator.generate(
        actions=actions,
        context={
            "vehicle": {
                "brand": "Toyota",
                "model": "Camry",
                "year": 2018
            },
            "reported_issues": ["P0301 - Cylinder 1 misfire"],
            "attempted_solutions": ["replaced spark plugs"]
        },
        last_messages=[
            {"role": "user", "content": "I already replaced the spark plugs"},
            {"role": "assistant", "content": "Let's diagnose further..."}
        ]
    )
    
    print(f"Tone: {result['tone']}")
    print(f"Word count: {result['word_count']}")
    print(f"\nAnswer:\n{'-' * 80}")
    print(result['answer'][:500] + "..." if len(result['answer']) > 500 else result['answer'])
    print('-' * 80)
    
    # Example 2: Simple generation
    print("\n" + "=" * 80)
    print("Example 2: Simple Response")
    print("=" * 80)
    
    simple_answer = AnswerGenerator.generate_simple(
        message="Thanks for the help!",
        context={"vehicle": {"brand": "Toyota", "model": "Camry", "year": 2018}}
    )
    
    print(f"Response: {simple_answer}")
    
    # Example 3: Format actions as text
    print("\n" + "=" * 80)
    print("Example 3: Format Actions as Text")
    print("=" * 80)
    
    formatted = AnswerGenerator.format_actions_as_text(actions)
    print(formatted)