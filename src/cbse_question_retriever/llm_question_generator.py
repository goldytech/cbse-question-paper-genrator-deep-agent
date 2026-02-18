"""LLM Question Generator Tool.

Generates CBSE-compliant questions using gpt-5-mini based on retrieved chunks.
"""

import logging
from typing import Any, Dict, List

from langchain_core.tools import tool

from .diagram_detector import diagram_detector
from .llm_client import llm_client
from .prompt_templates import build_generation_prompt

from .settings import settings

logger = logging.getLogger(__name__)


@tool
def generate_llm_question_tool(
    chunks: List[Dict[str, Any]],
    blueprint_context: Dict[str, Any],
    question_id: str,
) -> Dict[str, Any]:
    """Generates a CBSE-compliant question using gpt-5-mini based on retrieved textbook chunks.

    This tool takes retrieved chunks from Qdrant and generates a complete, high-quality
    CBSE examination question using gpt-5-mini with detailed prompting including
    few-shot examples, format specifications, and pedagogical guidelines.

    Args:
        chunks: List of retrieved textbook chunks from Qdrant. Each chunk should contain:
            - text: The chunk content
            - chunk_type: THEORY/WORKED_EXAMPLE/EXERCISE_PATTERN
            - chapter: Chapter name
            - topic: Topic name

        blueprint_context: Complete blueprint specifications including:
            - class_level: CBSE class (1-12)
            - subject: Subject name
            - chapter: Chapter name
            - topic: Topic name
            - question_format: MCQ/VERY_SHORT/SHORT/LONG/CASE_STUDY
            - marks: Marks allocated
            - difficulty: easy/medium/hard
            - bloom_level: REMEMBER/UNDERSTAND/APPLY/ANALYSE/EVALUATE
            - nature: NUMERICAL/CONCEPTUAL/REASONING/WORD_PROBLEM/DERIVATION
            - section_title: Section name from blueprint

        question_id: Pre-generated question ID (e.g., "MATH-10-POL-MCQ-001")

    Returns:
        Complete question dictionary with:
        - question_id: The question ID
        - question_text: Generated question text
        - options: List of 4 options for MCQ, null for others
        - correct_answer: "A"/"B"/"C"/"D" for MCQ, null for others
        - explanation: Step-by-step solution for teacher verification
        - diagram_needed: Boolean indicating diagram requirement
        - diagram_description: Detailed description if diagram needed
        - generation_metadata: Technical details
        - error: Error message if generation failed, else None

    Example:
        >>> chunks = [
        ...     {"text": "Zeros of polynomial...", "chunk_type": "THEORY"},
        ...     {"text": "Example: Find zero...", "chunk_type": "WORKED_EXAMPLE"}
        ... ]
        >>> blueprint = {
        ...     "class_level": 10,
        ...     "subject": "Mathematics",
        ...     "chapter": "Polynomials",
        ...     "topic": "Zeros of a Polynomial",
        ...     "question_format": "MCQ",
        ...     "marks": 1,
        ...     "difficulty": "easy",
        ...     "bloom_level": "REMEMBER",
        ...     "nature": "NUMERICAL",
        ...     "section_title": "Multiple Choice Questions"
        ... }
        >>> result = generate_llm_question_tool(
        ...     chunks=chunks,
        ...     blueprint_context=blueprint,
        ...     question_id="MATH-10-POL-MCQ-001"
        ... )
        >>> print(result["question_text"])
        "What is the zero of the polynomial p(x) = x - 3?"

    Configuration:
        Settings controlled via environment variables:
        - OPENAI__MODEL: LLM model (default: gpt-5-mini)
        - OPENAI__TEMPERATURE: Temperature (default: 0.3)
        - OPENAI__MAX_TOKENS: Max tokens (default: 1000)
        - OPENAI__QUALITY_CHECK_ENABLED: Enable quality score (default: true)
        - OPENAI__FEW_SHOT_EXAMPLES_ENABLED: Include examples (default: true)
    """
    try:
        logger.info(
            f"Generating question with LLM for {question_id}: "
            f"{blueprint_context.get('topic')} ({blueprint_context.get('question_format')})"
        )

        # Check if retrieval had errors (passed via blueprint_context)
        retrieval_error = blueprint_context.get("retrieval_error")
        if retrieval_error:
            logger.warning(
                f"Skipping LLM generation for {question_id} due to retrieval error: {retrieval_error}"
            )
            return create_error_response(
                question_id,
                blueprint_context,
                f"Retrieval failed: {retrieval_error}",
                error_phase="retrieval",
            )

        # Check if we have valid chunks to work with
        if not chunks:
            logger.error("No chunks provided for question generation")
            return create_error_response(
                question_id,
                blueprint_context,
                "No textbook chunks provided for question generation",
                error_phase="retrieval",
            )

        # Step 1: Build generation prompt
        include_examples = settings.llm.few_shot_examples_enabled

        prompt = build_generation_prompt(
            chunks=chunks,
            blueprint_context=blueprint_context,
            include_examples=include_examples,
        )

        logger.debug(f"Generation prompt built (examples={include_examples})")

        # Step 2: Generate question using LLM with structured output
        try:
            question_data = llm_client.generate_question(prompt)
            logger.info("LLM question generation completed successfully with structured output")
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return create_error_response(
                question_id,
                blueprint_context,
                f"LLM generation error: {str(e)}",
                error_phase="llm",
            )

        # Step 3: Validate quality
        is_valid = validate_question_quality(question_data)
        if not is_valid:
            logger.warning("Question quality validation failed, but continuing with best-effort")

        # Step 5: Detect diagram need using LLM
        diagram_info = diagram_detector.detect_diagram_need(
            question_text=question_data.get("question_text", ""),
            topic=blueprint_context.get("topic", ""),
            chapter=blueprint_context.get("chapter", ""),
            question_format=blueprint_context.get("question_format", "MCQ"),
        )

        # Update question data with diagram info
        question_data["diagram_needed"] = diagram_info["diagram_needed"]
        question_data["diagram_description"] = diagram_info["diagram_description"]

        logger.info(
            f"Diagram detection: needed={diagram_info['diagram_needed']}, "
            f"type={diagram_info['diagram_type']}"
        )

        # Step 6: Add metadata
        question_data["question_id"] = question_id
        question_data["generation_metadata"] = {
            "model": settings.llm.model,
            "temperature": settings.llm.temperature,
            "max_tokens": settings.llm.max_tokens,
            "chunks_used": len(chunks),
            "few_shot_enabled": include_examples,
            "validation_passed": is_valid,
        }
        question_data["error"] = None

        logger.info(f"Question generation completed successfully for {question_id}")

        return question_data

    except Exception as e:
        logger.exception(f"Unexpected error in question generation: {e}")
        return create_error_response(
            question_id,
            blueprint_context,
            f"Unexpected error: {str(e)}",
            error_phase="llm",
        )


def create_error_response(
    question_id: str,
    blueprint_context: Dict[str, Any],
    error_message: str,
    error_phase: str = "llm",
) -> Dict[str, Any]:
    """Create an error response with minimal valid structure.

    Args:
        question_id: The question ID
        blueprint_context: Blueprint context
        error_message: Error description
        error_phase: Phase where error occurred ("retrieval" or "llm")

    Returns:
        Error response dictionary
    """
    logger.error(f"Question generation error for {question_id}: {error_message}")

    return {
        "question_id": question_id,
        "question_text": f"[Error: Could not generate question - {error_message}]",
        "options": None,
        "correct_answer": None,
        "explanation": f"Error during generation: {error_message}",
        "diagram_needed": False,
        "diagram_description": None,
        "generation_metadata": {
            "model": settings.llm.model,
            "temperature": settings.llm.temperature,
            "error": True,
            "error_message": error_message,
            "error_phase": error_phase,
        },
        "error": error_message,
        "error_phase": error_phase,
    }


def validate_question_quality(question_data: Dict[str, Any]) -> bool:
    """Validate that generated question meets minimum quality standards.

    Args:
        question_data: Parsed question dictionary from structured output

    Returns:
        True if question meets quality standards
    """
    # Check minimum requirements
    if not question_data.get("question_text"):
        logger.warning("Question failed validation: missing question_text")
        return False

    if len(question_data["question_text"]) < 10:
        logger.warning("Question failed validation: question_text too short")
        return False

    # For MCQ, check options and answer
    if question_data.get("options") is not None:
        if not question_data.get("correct_answer"):
            logger.warning("MCQ failed validation: missing correct_answer")
            return False

    # Check explanation
    if not question_data.get("explanation"):
        logger.warning("Question failed validation: missing explanation")
        return False

    return True
