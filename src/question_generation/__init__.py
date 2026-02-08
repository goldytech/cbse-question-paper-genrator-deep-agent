"""Question generation domain."""

from .orchestrator import generate_question_paper_tool
from .config import (
    BLUEPRINT_VALIDATOR_SUBAGENT,
    QUERY_OPTIMIZER_SUBAGENT,
    QUESTION_ASSEMBLER_SUBAGENT,
    PAPER_VALIDATOR_SUBAGENT,
    DOCX_GENERATOR_SUBAGENT,
    ALL_SUBAGENTS,
)

__all__ = [
    "generate_question_paper_tool",
    "BLUEPRINT_VALIDATOR_SUBAGENT",
    "QUERY_OPTIMIZER_SUBAGENT",
    "QUESTION_ASSEMBLER_SUBAGENT",
    "PAPER_VALIDATOR_SUBAGENT",
    "DOCX_GENERATOR_SUBAGENT",
    "ALL_SUBAGENTS",
]
