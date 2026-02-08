"""Question generation domain."""

from .orchestrator import generate_question_paper_tool
from .config import QUERY_OPTIMIZER_SUBAGENT, QUESTION_ASSEMBLER_SUBAGENT, SUBAGENTS

__all__ = [
    "generate_question_paper_tool",
    "QUERY_OPTIMIZER_SUBAGENT",
    "QUESTION_ASSEMBLER_SUBAGENT",
    "SUBAGENTS",
]
