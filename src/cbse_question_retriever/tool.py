"""CBSE Question Retriever tool.

This tool retrieves CBSE textbook chunks from Qdrant vector database based on blueprint specifications.
"""

import logging
from typing import Any, Dict

from langchain_core.tools import tool

from .retriever import retriever
from .data_types import RetrievedData

logger = logging.getLogger(__name__)


@tool
def generate_question_tool(
    blueprint_path: str,
    section_id: str,
    question_number: int,
) -> Dict[str, Any]:
    """Generates a CBSE-compliant question by retrieving textbook chunks from Qdrant.

    This tool reads the blueprint specification and retrieves relevant textbook content
    from the Qdrant vector database for question generation.

    Args:
        blueprint_path: Path to the exam blueprint JSON file (e.g., "input/classes/10/mathematics/input_first_term.json")
        section_id: Section identifier from blueprint (e.g., "A", "B", "C", "D")
        question_number: Question number within the section (1-based index)

    Returns:
        Dictionary containing:
        - question_id: Formatted ID (e.g., "MATH-10-POL-MCQ-001")
        - chapter: Chapter name
        - topic: Topic name (fuzzy matched)
        - question_format: Format from blueprint (MCQ, VERY_SHORT, SHORT, LONG, CASE_STUDY)
        - marks: Marks per question
        - difficulty: Calculated difficulty (easy/medium/hard based on 40/40/20 distribution)
        - bloom_level: Cognitive level (REMEMBER, UNDERSTAND, APPLY, ANALYSE, EVALUATE)
        - nature: Question nature (NUMERICAL, CONCEPTUAL, REASONING, WORD_PROBLEM, DERIVATION)
        - has_diagram: Whether question needs diagram (set to False, detected later)
        - chunks_used: Number of chunks retrieved
        - chunks: List of retrieved textbook chunks with metadata
        - blueprint_reference: Section metadata from blueprint
        - retrieval_metadata: Technical details about the retrieval process
        - error: Error message if retrieval failed, otherwise None

    Example:
        >>> result = generate_question_tool(
        ...     blueprint_path="input/classes/10/mathematics/input_first_term.json",
        ...     section_id="A",
        ...     question_number=1
        ... )
        >>> print(result["question_id"])
        "MATH-10-POL-MCQ-001"

    Error Handling:
        Returns error field with specific messages:
        - "Collection '{name}' not found"
        - "Topic '{topic}' not found"
        - "Blueprint file not found"
        - "Section '{id}' not found in blueprint"
    """
    try:
        logger.info(
            f"Retrieving question from blueprint: {blueprint_path}, "
            f"section: {section_id}, question: {question_number}"
        )

        # Call the retriever
        result: RetrievedData = retriever.retrieve(
            blueprint_path=blueprint_path,
            section_id=section_id,
            question_number=question_number,
        )

        # Convert RetrievedData to dictionary
        return {
            "question_id": result.question_id,
            "chapter": result.chapter,
            "topic": result.topic,
            "question_format": result.question_format,
            "marks": result.marks,
            "difficulty": result.difficulty,
            "bloom_level": result.bloom_level,
            "nature": result.nature,
            "has_diagram": result.has_diagram,
            "chunks_used": result.chunks_used,
            "chunks": [
                {
                    "id": chunk.id,
                    "text": chunk.text,
                    "chapter": chunk.chapter,
                    "section": chunk.section,
                    "topic": chunk.topic,
                    "chunk_type": chunk.chunk_type.value,
                    "page_start": chunk.page_start,
                    "page_end": chunk.page_end,
                    "score": chunk.score,
                }
                for chunk in result.chunks
            ],
            "blueprint_reference": result.blueprint_reference,
            "retrieval_metadata": result.retrieval_metadata,
            "error": result.error,
        }

    except Exception as e:
        logger.exception("Unexpected error in generate_question_tool")
        return {
            "question_id": "",
            "chapter": "",
            "topic": "",
            "question_format": "MCQ",
            "marks": 0,
            "difficulty": "",
            "bloom_level": "",
            "nature": "",
            "has_diagram": False,
            "chunks_used": 0,
            "chunks": [],
            "blueprint_reference": {},
            "retrieval_metadata": {},
            "error": f"Tool execution error: {str(e)}",
        }
