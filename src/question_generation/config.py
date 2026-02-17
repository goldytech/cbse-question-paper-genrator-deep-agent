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
from input_file_locator.tool import locate_blueprint_tool
from cbse_question_retriever.tool import generate_question_tool
from cbse_question_retriever.llm_question_generator import generate_llm_question_tool
from question_assembler.tool import assemble_question_tool

# Skill root path
SKILL_ROOT = "src/skills"

# Input File Locator Subagent Configuration
# First step: Locates blueprint files from teacher input or auto-discovery
INPUT_FILE_LOCATOR_SUBAGENT: Dict[str, Any] = {
    "name": "input-file-locator",
    "description": "Locates and validates the teacher's input blueprint JSON file from explicit path or auto-discovers from input/classes/{class}/{subject}/ folder",
    "model": "openai:gpt-4o",
    "tools": [locate_blueprint_tool],
    "skills": [f"{SKILL_ROOT}/input-file-locator/"],
}

# Blueprint Validator Subagent Configuration
BLUEPRINT_VALIDATOR_SUBAGENT: Dict[str, Any] = {
    "name": "blueprint-validator",
    "description": "Validates exam blueprints against master policy blueprints to ensure compliance with CBSE standards",
    "model": "openai:gpt-4o",
    "tools": [validate_blueprint_tool],
    "skills": [f"{SKILL_ROOT}/blueprint-validator/"],
}

# CBSE Question Retriever Subagent Configuration
# Step 3: Retrieves questions from vector DB and generates with gpt-5-mini
CBSE_QUESTION_RETRIEVER_SUBAGENT: Dict[str, Any] = {
    "name": "cbse-question-retriever",
    "description": "Retrieves CBSE textbook chunks from Qdrant vector database using generate_question_tool, then generates high-quality CBSE-compliant questions using gpt-5-mini via generate_llm_question_tool. Includes detailed prompting with few-shot examples, diagram detection, and pedagogical guidelines.",
    "model": "openai:gpt-5-mini",
    "tools": [generate_question_tool, generate_llm_question_tool, generate_diagram_tool],
    "skills": [f"{SKILL_ROOT}/cbse-question-retriever/"],
}

# Question Assembler Subagent Configuration
# Uses GPT-4o for high-quality question generation
QUESTION_ASSEMBLER_SUBAGENT: Dict[str, Any] = {
    "name": "question-assembler",
    "description": "Assembles CBSE-compliant questions from search results and LLM-generated content. Takes retrieved chunks and LLM output to create complete question objects with proper IDs, diagram detection, and formatting.",
    "model": "openai:gpt-4o",
    "tools": [assemble_question_tool, generate_diagram_tool],
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
    INPUT_FILE_LOCATOR_SUBAGENT,
    BLUEPRINT_VALIDATOR_SUBAGENT,
    CBSE_QUESTION_RETRIEVER_SUBAGENT,
    QUESTION_ASSEMBLER_SUBAGENT,
    PAPER_VALIDATOR_SUBAGENT,
    DOCX_GENERATOR_SUBAGENT,
]
