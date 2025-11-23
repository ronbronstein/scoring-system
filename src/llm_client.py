"""
LLM Client for Layer 2: Sequential execution of 16 specialized agents.
Handles rate limiting, retries, JSON parsing, and error recovery.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import anthropic
from dotenv import load_dotenv

from config import (
    MODEL_NAME,
    TEMPERATURE,
    MAX_TOKENS,
    MAX_RETRIES,
    RETRY_DELAY,
    DELAY_BETWEEN_AGENT_CALLS,
    RATE_LIMIT_BACKOFF,
    PROMPTS_DIR,
    get_llm_agents,
    get_agent_metadata,
)

# Load environment variables
load_dotenv()

# ============================================================================
# PROMPT LOADING
# ============================================================================


def load_prompt(agent_id: str) -> Optional[str]:
    """
    Load prompt content from the prompts directory.

    Args:
        agent_id: The agent identifier (e.g., "1A_Positive")

    Returns:
        Prompt content as string, or None if file not found
    """
    metadata = get_agent_metadata(agent_id)
    if not metadata or not metadata["prompt_file"]:
        return None

    prompt_path = PROMPTS_DIR / metadata["prompt_file"]

    if not prompt_path.exists():
        print(f"Warning: Prompt file not found: {prompt_path}")
        return None

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error loading prompt for {agent_id}: {e}")
        return None


# ============================================================================
# LLM API CLIENT
# ============================================================================


class LLMClient:
    """
    Synchronous client for Claude API with retry logic and JSON enforcement.
    """

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment variables. "
                "Please create a .env file with your API key."
            )
        self.client = anthropic.Anthropic(api_key=api_key)

    def call_agent(
        self, agent_id: str, content: str, retry_count: int = 0
    ) -> Dict:
        """
        Make a synchronous API call for a single agent with retry logic.

        Args:
            agent_id: The agent identifier
            content: The draft content to analyze
            retry_count: Current retry attempt (for exponential backoff)

        Returns:
            Dict with parsed result or error information
        """
        metadata = get_agent_metadata(agent_id)
        if not metadata:
            return {
                "agent_id": agent_id,
                "success": False,
                "error": "Agent metadata not found",
            }

        # Load prompt instructions
        prompt_instructions = load_prompt(agent_id)
        if not prompt_instructions:
            return {
                "agent_id": agent_id,
                "success": False,
                "error": f"Prompt file not found: {metadata['prompt_file']}",
            }

        # Build system prompt (specialized for this agent)
        system_prompt = self._build_system_prompt(agent_id, metadata, prompt_instructions)

        # Build user message (content to analyze)
        user_message = self._build_user_message(content, prompt_instructions)

        # Assistant prefill to enforce JSON start
        assistant_prefill = "{"

        try:
            # Add delay before API call for rate limiting (sequential execution)
            time.sleep(DELAY_BETWEEN_AGENT_CALLS)

            # Make API call (synchronous)
            response = self.client.messages.create(
                model=MODEL_NAME,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": assistant_prefill},
                ],
            )

            # Parse response
            return self._parse_response(agent_id, response, assistant_prefill)

        except anthropic.APIError as e:
            # Retry logic
            if retry_count < MAX_RETRIES:
                error_str = str(e)

                # Smart backoff: Detect rate limit errors and wait longer
                if "rate_limit" in error_str.lower():
                    wait_time = RATE_LIMIT_BACKOFF
                    print(
                        f"⚠️  Rate limit hit for {agent_id} (attempt {retry_count + 1}/{MAX_RETRIES}). "
                        f"Waiting {wait_time}s for rate limit reset..."
                    )
                else:
                    wait_time = RETRY_DELAY * (2**retry_count)  # Exponential backoff
                    print(
                        f"API error for {agent_id} (attempt {retry_count + 1}/{MAX_RETRIES}): {e}. "
                        f"Retrying in {wait_time}s..."
                    )

                time.sleep(wait_time)
                return self.call_agent(agent_id, content, retry_count + 1)
            else:
                return {
                    "agent_id": agent_id,
                    "success": False,
                    "error": f"API error after {MAX_RETRIES} retries: {str(e)}",
                }

        except Exception as e:
            return {
                "agent_id": agent_id,
                "success": False,
                "error": f"Unexpected error: {str(e)}",
            }

    def _build_system_prompt(
        self, agent_id: str, metadata: Dict, instructions: str
    ) -> str:
        """
        Build the system prompt for a specific agent.

        The prompt files in /prompts are complete and self-contained, including:
        - Role definition and mental model
        - Evaluation criteria and scoring rubric
        - Examples and output format instructions

        Args:
            agent_id: Agent identifier
            metadata: Agent metadata from config (unused but kept for compatibility)
            instructions: Complete prompt content from file

        Returns:
            System prompt string (the prompt file content as-is)
        """
        # Return the prompt file content directly without wrapping
        return instructions

    def _build_user_message(self, content: str, instructions: str) -> str:
        """
        Build the user message containing the content to analyze.

        Args:
            content: Draft content to evaluate
            instructions: Prompt instructions (unused but kept for compatibility)

        Returns:
            User message string
        """
        return f"""Evaluate and score this content piece based on the 1-4 scale:

---BEGIN CONTENT---
{content}
---END CONTENT---"""

    def _parse_response(
        self, agent_id: str, response: anthropic.types.Message, prefill: str
    ) -> Dict:
        """
        Parse the LLM response and extract the JSON object.

        Args:
            agent_id: Agent identifier
            response: API response object
            prefill: The assistant prefill used (to reconstruct full JSON)

        Returns:
            Parsed result dictionary
        """
        try:
            # Extract text from response
            if not response.content or len(response.content) == 0:
                return {
                    "agent_id": agent_id,
                    "success": False,
                    "error": "Empty response from API",
                }

            response_text = response.content[0].text

            # Reconstruct full JSON (prepend the prefill)
            full_json = prefill + response_text

            # Parse JSON
            parsed = json.loads(full_json)

            # Validate structure
            required_keys = {"score", "feedback", "flags"}
            optional_keys = {"thinking"}  # Chain-of-thought reasoning (optional)
            if not required_keys.issubset(parsed.keys()):
                missing = required_keys - set(parsed.keys())
                return {
                    "agent_id": agent_id,
                    "success": False,
                    "error": f"Missing required keys: {missing}",
                    "raw_response": full_json,
                }

            # Validate score is 1-4
            if not isinstance(parsed["score"], int) or not (1 <= parsed["score"] <= 4):
                return {
                    "agent_id": agent_id,
                    "success": False,
                    "error": f"Invalid score: {parsed.get('score')}. Must be integer 1-4.",
                    "raw_response": full_json,
                }

            # Success!
            result = {
                "agent_id": agent_id,
                "success": True,
                "score": parsed["score"],
                "feedback": parsed["feedback"],
                "flags": parsed.get("flags", []),
            }

            # Include optional thinking field if present
            if "thinking" in parsed:
                result["thinking"] = parsed["thinking"]

            return result

        except json.JSONDecodeError as e:
            return {
                "agent_id": agent_id,
                "success": False,
                "error": f"JSON parsing error: {str(e)}",
                "raw_response": prefill + response.content[0].text if response.content else "",
            }
        except Exception as e:
            return {
                "agent_id": agent_id,
                "success": False,
                "error": f"Response parsing error: {str(e)}",
            }


# ============================================================================
# SEQUENTIAL EXECUTION ORCHESTRATION
# ============================================================================


def run_all_agents_sequential(content: str) -> Dict[str, Dict]:
    """
    Execute all 16 LLM agents sequentially with smart rate limiting.

    Args:
        content: The draft content to analyze

    Returns:
        Dictionary mapping agent_id to result
    """
    client = LLMClient()
    agent_ids = get_llm_agents()

    print(f"Starting sequential execution of {len(agent_ids)} agents...")

    # Execute agents one by one
    results = []
    for i, agent_id in enumerate(agent_ids, 1):
        print(f"  [{i}/{len(agent_ids)}] Calling {agent_id}...", end=" ")
        result = client.call_agent(agent_id, content)

        if result["success"]:
            print(f"✓ Score: {result['score']}")
        else:
            print(f"✗ Error: {result.get('error', 'Unknown')[:50]}...")

        results.append(result)

    # Convert list to dictionary
    results_dict = {result["agent_id"]: result for result in results}

    # Report success/failure
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful

    print(f"\nAgent execution complete: {successful} successful, {failed} failed")

    if failed > 0:
        print("\nFailed agents:")
        for result in results:
            if not result["success"]:
                print(f"  - {result['agent_id']}: {result.get('error', 'Unknown error')}")

    return results_dict


def retry_failed_agents(content: str, previous_results: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Retry only the agents that failed in the previous run.
    This implements the "continue/resume" functionality.

    Args:
        content: The draft content to analyze
        previous_results: Results from previous execution

    Returns:
        Dictionary mapping agent_id to result (only retried agents)
    """
    client = LLMClient()

    # Identify failed agents
    failed_agents = [
        agent_id for agent_id, result in previous_results.items() if not result["success"]
    ]

    if not failed_agents:
        print("No failed agents to retry.")
        return {}

    print(f"\nRetrying {len(failed_agents)} failed agents...")

    # Execute retries sequentially
    results = []
    for agent_id in failed_agents:
        result = client.call_agent(agent_id, content)
        results.append(result)

    # Convert to dictionary
    retry_results = {result["agent_id"]: result for result in results}

    # Report results
    successful = sum(1 for r in results if r["success"])
    still_failed = len(results) - successful

    print(f"Retry complete: {successful} recovered, {still_failed} still failing")

    return retry_results


# ============================================================================
# PUBLIC API
# ============================================================================


def run_layer_2_analysis(content: str) -> Dict[str, Dict]:
    """
    Run all 16 LLM agents sequentially and return results.

    Args:
        content: Draft content to analyze

    Returns:
        Dictionary of results by agent_id
    """
    return run_all_agents_sequential(content)


def retry_failed(content: str, previous_results: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Retry only failed agents from a previous run.

    Args:
        content: Draft content to analyze
        previous_results: Previous execution results

    Returns:
        Dictionary of retry results by agent_id
    """
    return retry_failed_agents(content, previous_results)
