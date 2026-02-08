"""Subagent configurations for question paper generation.

These configurations define the specialized subagents used in the question
paper generation pipeline. Each subagent uses its own skill and model.
Tools are explicitly imported from their respective domain modules.
"""

from typing import Dict, Any, List
from blueprint_validation.tool import validate_blueprint_tool
from paper_validation.tool import validate_paper_tool
from diagram_generation.tool import generate_diagram_tool
from docx_generation.tool import generate_docx_tool

# Skill root path
SKILL_ROOT = "src/skills"

# Blueprint Validator Subagent Configuration
BLUEPRINT_VALIDATOR_SUBAGENT: Dict[str, Any] = {
    "name": "blueprint-validator",
    "description": "Validates exam blueprints against master policy blueprints to ensure compliance with CBSE standards",
    "model": "openai:gpt-4o",
    "tools": [validate_blueprint_tool],
    "skills": [f"{SKILL_ROOT}/blueprint-validator/"],
}

# Query Optimizer Subagent Configuration
# Uses GPT-4o-mini for cost-effective query generation
QUERY_OPTIMIZER_SUBAGENT: Dict[str, Any] = {
    "name": "query-optimizer",
    "description": "Generates optimized Tavily search queries for CBSE question retrieval",
    "model": "openai:gpt-4o-mini",
    "tools": [],  # No tools needed - just query generation
    "skills": [f"{SKILL_ROOT}/query-optimizer/"],
}

# Question Assembler Subagent Configuration
# Uses GPT-4o for high-quality question generation
QUESTION_ASSEMBLER_SUBAGENT: Dict[str, Any] = {
    "name": "question-assembler",
    "description": "Assembles CBSE-compliant questions from search results",
    "model": "openai:gpt-4o",
    "tools": [generate_diagram_tool],  # Can generate diagrams
    "skills": [f"{SKILL_ROOT}/question-assembler/"],
}

# Paper Validator Subagent Configuration
PAPER_VALIDATOR_SUBAGENT: Dict[str, Any] = {
    "name": "paper-validator",
    "description": "Validates generated papers against original blueprints",
    "model": "openai:gpt-4o",
    "tools": [validate_paper_tool],
    "skills": [f"{SKILL_ROOT}/paper-validator/"],
}

# DOCX Generator Subagent Configuration
DOCX_GENERATOR_SUBAGENT: Dict[str, Any] = {
    "name": "docx-generator",
    "description": "Converts approved JSON question papers to DOCX format with embedded diagrams. Use ONLY AFTER teacher approves the JSON question paper.",
    "model": "openai:gpt-4o",
    "tools": [generate_docx_tool],
    "skills": [f"{SKILL_ROOT}/docx-generator/"],
}

# List of all subagents for registration
ALL_SUBAGENTS: List[Dict[str, Any]] = [
    BLUEPRINT_VALIDATOR_SUBAGENT,
    QUERY_OPTIMIZER_SUBAGENT,
    QUESTION_ASSEMBLER_SUBAGENT,
    PAPER_VALIDATOR_SUBAGENT,
    DOCX_GENERATOR_SUBAGENT,
]
