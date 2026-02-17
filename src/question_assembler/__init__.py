"""Question Assembler package.

This package assembles CBSE-compliant questions from retrieved chunks and LLM-generated content.
"""

from question_assembler.tool import assemble_question_tool
from question_assembler.data_types import AssembledQuestion

__all__ = [
    "assemble_question_tool",
    "AssembledQuestion",
]
