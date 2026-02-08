"""Subagent configurations for question generation.

These configurations define the specialized subagents used in the question
paper generation pipeline. Each subagent uses its own skill and model.
"""

from typing import Dict, Any, List

# Query Optimizer Subagent Configuration
# Uses GPT-4o-mini for cost-effective query generation
QUERY_OPTIMIZER_SUBAGENT: Dict[str, Any] = {
    "name": "query-optimizer",
    "description": "Generates optimized Tavily search queries for CBSE question retrieval",
    "model": "openai:gpt-4o-mini",
    "tools": [],  # No tools needed - just query generation
    "skills": ["src/question_generation/skills/query-optimization/"],
    # Note: No system_prompt - all instructions in SKILL.md
}

# Question Assembler Subagent Configuration
# Uses GPT-4o for high-quality question generation
QUESTION_ASSEMBLER_SUBAGENT: Dict[str, Any] = {
    "name": "question-assembler",
    "description": "Assembles CBSE-compliant questions from search results",
    "model": "openai:gpt-4o",
    "tools": ["generate_diagram_tool"],  # Can generate diagrams
    "skills": ["src/question_generation/skills/question-assembly/"],
    # Note: No system_prompt - all instructions in SKILL.md
}

# List of all subagents for registration
SUBAGENTS: List[Dict[str, Any]] = [
    QUERY_OPTIMIZER_SUBAGENT,
    QUESTION_ASSEMBLER_SUBAGENT,
]
