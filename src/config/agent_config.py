"""Agent configuration for CBSE Question Paper Generator."""

from typing import List, Dict, Any


def get_subagent_definitions() -> List[Dict]:
    """
    Get subagent definitions for CBSE question paper generation.
    Uses the new skill-based configuration from question_generation.config.

    Returns:
        List of subagent dictionaries for create_deep_agent
    """
    from question_generation.config import ALL_SUBAGENTS

    return ALL_SUBAGENTS


def get_tools() -> List:
    """
    Get custom tools for main agent.

    Note: All specialized tools are now assigned to subagents for better context isolation:
    - validate_blueprint_tool → blueprint-validator subagent
    - validate_paper_tool → paper-validator subagent
    - generate_diagram_tool → question-assembler subagent

    Main agent focuses on coordination and delegates to subagents.

    Returns:
        List of custom tool functions (empty - subagents handle specialized work)
    """
    # Main agent uses only built-in harness tools (read_file, write_file, etc.)
    # All specialized validation and research tools are in subagents
    return []


def configure_interrupt_on() -> Dict[str, Any]:
    """
    Get interrupt_on configuration for human-in-the-loop.

    Returns:
        Dictionary of tools and interrupt settings
        Can be bool (True/False) or dict with allowed_decisions
    """
    return {"write_file": True}
