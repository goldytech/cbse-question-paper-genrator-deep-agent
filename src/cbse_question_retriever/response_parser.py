"""Response parser for LLM question generation.

Parses and validates LLM responses, handling various formats and errors.
"""

import json
import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def extract_json_from_text(text: str) -> str:
    """Extract JSON from text that may contain markdown or other content.

    Args:
        text: Raw LLM response text

    Returns:
        Extracted JSON string
    """
    # Try to find JSON in code blocks
    patterns = [
        r"```json\s*(.*?)\s*```",  # Markdown JSON block
        r"```\s*(.*?)\s*```",  # Generic code block
        r"(\{.*\})",  # Raw JSON object (greedy match)
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

    # If no patterns match, return the text as-is
    return text.strip()


def attempt_json_repair(json_text: str) -> Dict[str, Any]:
    """Attempt to repair malformed JSON.

    Args:
        json_text: Potentially malformed JSON string

    Returns:
        Parsed dictionary or minimal valid structure
    """
    # Common fixes
    repaired = json_text

    # Remove trailing commas
    repaired = re.sub(r",(\s*[}\]])", r"\1", repaired)

    # Fix single quotes to double quotes
    repaired = repaired.replace("'", '"')

    # Try to find the main JSON object
    try:
        # Find content between first { and last }
        start = repaired.find("{")
        end = repaired.rfind("}")
        if start != -1 and end != -1 and end > start:
            repaired = repaired[start : end + 1]
            return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    # If all repairs fail, return minimal structure
    logger.warning("Could not repair JSON, returning minimal structure")
    return {
        "question_text": "",
        "options": None,
        "correct_answer": None,
        "explanation": "",
        "diagram_needed": False,
        "diagram_description": None,
        "hints": [],
        "prerequisites": [],
        "common_mistakes": [],
        "quality_score": None,
    }


def parse_llm_response(response_text: str, include_quality_score: bool = True) -> Dict[str, Any]:
    """Parse LLM response into structured question data.

    Args:
        response_text: Raw LLM response
        include_quality_score: Whether quality score is expected

    Returns:
        Parsed and validated question dictionary
    """
    try:
        # Extract JSON
        json_text = extract_json_from_text(response_text)

        # Parse JSON
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError:
            logger.warning("JSON decode error, attempting repair")
            data = attempt_json_repair(json_text)

        # Validate and set defaults for required fields
        validated = {
            "question_text": data.get("question_text", "").strip(),
            "options": data.get("options") if data.get("options") else None,
            "correct_answer": data.get("correct_answer"),
            "explanation": data.get("explanation", "").strip(),
            "diagram_needed": data.get("diagram_needed", False),
            "diagram_description": data.get("diagram_description"),
            "hints": data.get("hints", []) if isinstance(data.get("hints"), list) else [],
            "prerequisites": data.get("prerequisites", [])
            if isinstance(data.get("prerequisites"), list)
            else [],
            "common_mistakes": data.get("common_mistakes", [])
            if isinstance(data.get("common_mistakes"), list)
            else [],
        }

        # Add quality score if enabled
        if include_quality_score:
            quality_score = data.get("quality_score")
            if isinstance(quality_score, (int, float)):
                validated["quality_score"] = float(quality_score)
            else:
                validated["quality_score"] = None

        # Validate options for MCQ
        if validated["options"] is not None:
            if not isinstance(validated["options"], list) or len(validated["options"]) != 4:
                logger.warning(f"Invalid options format: {validated['options']}")
                validated["options"] = None
                validated["correct_answer"] = None

        # Validate correct_answer
        if validated["correct_answer"] is not None:
            if validated["correct_answer"] not in ["A", "B", "C", "D"]:
                logger.warning(f"Invalid correct_answer: {validated['correct_answer']}")
                validated["correct_answer"] = None

        return validated

    except Exception as e:
        logger.error(f"Error parsing LLM response: {e}")
        # Return minimal valid structure on error
        result = {
            "question_text": "",
            "options": None,
            "correct_answer": None,
            "explanation": f"Error parsing response: {str(e)}",
            "diagram_needed": False,
            "diagram_description": None,
            "hints": [],
            "prerequisites": [],
            "common_mistakes": [],
        }
        if include_quality_score:
            result["quality_score"] = None
        return result


def validate_question_quality(question_data: Dict[str, Any]) -> bool:
    """Validate that generated question meets minimum quality standards.

    Args:
        question_data: Parsed question dictionary

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
