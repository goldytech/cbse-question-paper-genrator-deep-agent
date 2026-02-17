"""Question Assembler Tool.

This tool assembles CBSE-compliant questions from retrieved chunks and LLM-generated content.
"""

import logging
from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

from cbse_question_retriever.data_types import (
    CHAPTER_ABBREVIATIONS,
    FORMAT_ABBREVIATIONS,
    SUBJECT_ABBREVIATIONS,
)
from diagram_generation.tool import generate_diagram_tool

logger = logging.getLogger(__name__)

# Keywords for diagram detection
DIAGRAM_KEYWORDS = {
    "geometric": [
        "triangle",
        "circle",
        "quadrilateral",
        "polygon",
        "angle",
        "∠",
        "vertex",
        "vertices",
        "side",
        "radius",
        "diameter",
        "chord",
        "tangent",
        "congruence",
        "similarity",
        "pythagoras",
        "perpendicular",
        "parallel",
        "intersecting",
        "sin",
        "cos",
        "tan",
        "cot",
        "sec",
        "cosec",
        "elevation",
        "depression",
        "height",
        "tower",
        "shadow",
        "ladder",
        "pole",
    ],
    "coordinate": [
        "graph",
        "plot",
        "coordinate",
        "axis",
        "point",
        "line",
        "slope",
        "intercept",
        "distance",
        "midpoint",
        "quadrant",
        "x-coordinate",
        "y-coordinate",
    ],
    "chart": [
        "histogram",
        "bar chart",
        "pie chart",
        "frequency",
        "class interval",
        "ogive",
        "data interpretation",
        "graph",
        "distribution",
    ],
}


def detect_diagram_need(
    question_text: str,
    topic: str,
    chapter: str,
    question_format: str,
) -> Dict[str, Any]:
    """Detect if a question needs a diagram based on content analysis.

    Args:
        question_text: The generated question text
        topic: Topic name
        chapter: Chapter name
        question_format: Question format (MCQ, SHORT, LONG, etc.)

    Returns:
        Dictionary with diagram detection results
    """
    text_lower = (question_text + " " + topic + " " + chapter).lower()

    # Check for geometric keywords
    for keyword in DIAGRAM_KEYWORDS["geometric"]:
        if keyword.lower() in text_lower:
            return {
                "diagram_needed": True,
                "diagram_type": "geometric",
                "reason": f"Detected keyword: {keyword}",
            }

    # Check for coordinate keywords
    for keyword in DIAGRAM_KEYWORDS["coordinate"]:
        if keyword.lower() in text_lower:
            return {
                "diagram_needed": True,
                "diagram_type": "coordinate",
                "reason": f"Detected keyword: {keyword}",
            }

    # Check for chart keywords
    for keyword in DIAGRAM_KEYWORDS["chart"]:
        if keyword.lower() in text_lower:
            return {
                "diagram_needed": True,
                "diagram_type": "chart",
                "reason": f"Detected keyword: {keyword}",
            }

    return {
        "diagram_needed": False,
        "diagram_type": None,
        "reason": "No diagram keywords detected",
    }


def generate_question_id(
    subject: str,
    class_level: int,
    chapter: str,
    question_format: str,
    question_number: int,
) -> str:
    """Generate question ID in format: SUBJECT-CLASS-CHAPTER-FORMAT-NUMBER.

    Args:
        subject: Subject name
        class_level: Class number (1-12)
        chapter: Chapter name
        question_format: Question format
        question_number: Question number (1-based)

    Returns:
        Formatted question ID
    """
    # Get abbreviations
    subject_abbr = SUBJECT_ABBREVIATIONS.get(subject.lower(), "UNK")
    chapter_lower = chapter.lower()
    chapter_abbr = None

    # Find chapter abbreviation (handle partial matches)
    for ch_name, ch_abbr in CHAPTER_ABBREVIATIONS.items():
        if ch_name in chapter_lower or chapter_lower in ch_name:
            chapter_abbr = ch_abbr
            break

    if not chapter_abbr:
        # Create abbreviation from first 3 letters of each word
        words = chapter.split()
        chapter_abbr = "".join([w[:3].upper() for w in words[:3]])

    format_abbr = FORMAT_ABBREVIATIONS.get(question_format, "UNK")

    # Format: MATH-10-POL-MCQ-001
    return f"{subject_abbr}-{class_level}-{chapter_abbr}-{format_abbr}-{question_number:03d}"


def build_diagram_elements(
    diagram_type: str,
    question_text: str,
    topic: str,
) -> Optional[Dict[str, Any]]:
    """Build diagram elements based on diagram type and question content.

    Args:
        diagram_type: Type of diagram (geometric, coordinate, chart)
        question_text: Question text
        topic: Topic name

    Returns:
        Diagram elements dictionary or None
    """
    elements = {}

    if diagram_type == "geometric":
        # Check for triangle-related questions
        if "triangle" in question_text.lower() or "triangle" in topic.lower():
            elements = {
                "shape": "triangle",
                "points": ["A", "B", "C"],
                "sides": [],
                "angles": [],
            }
        # Check for circle-related questions
        elif "circle" in question_text.lower():
            elements = {
                "shape": "circle",
                "center": (150, 150),
                "radius": 60,
            }

    elif diagram_type == "coordinate":
        elements = {
            "coordinates": {},
            "lines": [],
        }

    elif diagram_type == "chart":
        elements = {
            "data": [],
            "chart_type": "bar",
        }

    return elements if elements else None


@tool
def assemble_question_tool(
    retrieval_result: Dict[str, Any],
    llm_result: Dict[str, Any],
    question_number: int,
) -> Dict[str, Any]:
    """Assembles a CBSE-compliant question from retrieved chunks and LLM-generated content.

    This tool takes the results from chunk retrieval and LLM question generation,
    combines them into a complete CBSE question object, detects diagram needs,
    and generates diagrams when required.

    Args:
        retrieval_result: Result from generate_question_tool containing:
            - question_id: Pre-generated ID
            - chapter: Chapter name
            - topic: Topic name
            - question_format: Format (MCQ, VERY_SHORT, SHORT, LONG, CASE_STUDY)
            - marks: Marks allocated
            - difficulty: easy/medium/hard
            - bloom_level: Cognitive level
            - nature: Question nature
            - chunks: List of retrieved chunks

        llm_result: Result from generate_llm_question_tool containing:
            - question_text: Generated question text
            - options: MCQ options (if MCQ)
            - correct_answer: Correct answer
            - explanation: Solution explanation
            - diagram_needed: Boolean from LLM
            - diagram_description: Diagram description from LLM
            - hints: Helpful hints
            - prerequisites: Required knowledge
            - common_mistakes: Typical errors
            - quality_score: Self-assessed quality

        question_number: Question number within section (1-based)

    Returns:
        Complete assembled question dictionary with:
        - question_id: Formatted ID
        - question_text: Final question text
        - chapter, topic, format, marks, difficulty, etc.
        - options, correct_answer (for MCQ)
        - has_diagram, diagram_type, diagram_svg_base64 (if diagram generated)
        - explanation, hints, prerequisites, common_mistakes
        - tags, quality_score, generation_metadata

    Example:
        >>> retrieval = {
        ...     "chapter": "Polynomials",
        ...     "topic": "Zeros of a Polynomial",
        ...     "question_format": "MCQ",
        ...     "marks": 1,
        ...     "difficulty": "easy",
        ...     "bloom_level": "REMEMBER",
        ...     "nature": "NUMERICAL",
        ...     "chunks": [...]
        ... }
        >>> llm_output = {
        ...     "question_text": "Find the zero of p(x) = x - 3",
        ...     "options": ["A) 3", "B) -3", "C) 0", "D) 1"],
        ...     "correct_answer": "A",
        ...     "diagram_needed": False
        ... }
        >>> result = assemble_question_tool(retrieval, llm_output, 1)
        >>> print(result["question_id"])
        "MATH-10-POL-MCQ-001"
    """
    try:
        logger.info(f"Assembling question {question_number}")

        # Check for retrieval errors first
        retrieval_error = retrieval_result.get("error")
        if retrieval_error:
            logger.warning(f"Creating error question due to retrieval failure: {retrieval_error}")
            question_id = retrieval_result.get("question_id", f"ERR-{question_number}")
            return {
                "question_id": question_id,
                "question_text": f"[RETRIEVAL ERROR: {retrieval_error}]",
                "section_id": retrieval_result.get("blueprint_reference", {}).get("section_id", ""),
                "question_number": question_number,
                "chapter": retrieval_result.get("chapter", ""),
                "topic": retrieval_result.get("topic", ""),
                "question_format": retrieval_result.get("question_format", "MCQ"),
                "marks": retrieval_result.get("marks", 1),
                "options": None,
                "correct_answer": None,
                "difficulty": retrieval_result.get("difficulty", ""),
                "bloom_level": retrieval_result.get("bloom_level", ""),
                "nature": retrieval_result.get("nature", ""),
                "has_diagram": False,
                "diagram_type": None,
                "diagram_svg_base64": None,
                "diagram_description": None,
                "diagram_elements": None,
                "explanation": None,
                "hints": [],
                "prerequisites": [],
                "common_mistakes": [],
                "tags": [],
                "quality_score": None,
                "generation_metadata": {
                    "error": True,
                    "error_phase": "retrieval",
                    "error_message": retrieval_error,
                    "retrieval_metadata": retrieval_result.get("retrieval_metadata", {}),
                },
                "status": "failed",
                "error": retrieval_error,
                "error_phase": "retrieval",
            }

        # Extract blueprint context from retrieval result
        chapter = retrieval_result.get("chapter", "")
        topic = retrieval_result.get("topic", "")
        question_format = retrieval_result.get("question_format", "MCQ")
        marks = retrieval_result.get("marks", 1)
        difficulty = retrieval_result.get("difficulty", "medium")
        bloom_level = retrieval_result.get("bloom_level", "understand")
        nature = retrieval_result.get("nature", "NUMERICAL")

        # Get class and subject from blueprint reference
        blueprint_ref = retrieval_result.get("blueprint_reference", {})
        class_level = blueprint_ref.get("class", 10)
        subject = blueprint_ref.get("subject", "Mathematics")

        # Generate question ID if not provided
        question_id = retrieval_result.get("question_id", "")
        if not question_id:
            question_id = generate_question_id(
                subject=subject,
                class_level=class_level,
                chapter=chapter,
                question_format=question_format,
                question_number=question_number,
            )

        # Check for LLM errors
        llm_error = llm_result.get("error")
        if llm_error:
            logger.warning(f"Creating error question due to LLM failure: {llm_error}")
            return {
                "question_id": question_id,
                "question_text": f"[LLM ERROR: {llm_error}]",
                "section_id": blueprint_ref.get("section_id", ""),
                "question_number": question_number,
                "chapter": chapter,
                "topic": topic,
                "question_format": question_format,
                "marks": marks,
                "options": None,
                "correct_answer": None,
                "difficulty": difficulty,
                "bloom_level": bloom_level,
                "nature": nature,
                "has_diagram": False,
                "diagram_type": None,
                "diagram_svg_base64": None,
                "diagram_description": None,
                "diagram_elements": None,
                "explanation": f"Error during generation: {llm_error}",
                "hints": [],
                "prerequisites": [],
                "common_mistakes": [],
                "tags": [],
                "quality_score": None,
                "generation_metadata": {
                    "error": True,
                    "error_phase": llm_result.get("error_phase", "llm"),
                    "error_message": llm_error,
                    "retrieval_metadata": retrieval_result.get("retrieval_metadata", {}),
                    "llm_metadata": llm_result.get("generation_metadata", {}),
                },
                "status": "failed",
                "error": llm_error,
                "error_phase": llm_result.get("error_phase", "llm"),
            }

        # Extract LLM-generated content
        question_text = llm_result.get("question_text", "")
        options = llm_result.get("options")
        correct_answer = llm_result.get("correct_answer")
        explanation = llm_result.get("explanation")
        hints = llm_result.get("hints", [])
        prerequisites = llm_result.get("prerequisites", [])
        common_mistakes = llm_result.get("common_mistakes", [])
        quality_score = llm_result.get("quality_score")

        # Detect diagram need (use LLM result if available, otherwise detect)
        llm_diagram_needed = llm_result.get("diagram_needed", False)
        llm_diagram_desc = llm_result.get("diagram_description")

        detection_result = detect_diagram_need(
            question_text=question_text,
            topic=topic,
            chapter=chapter,
            question_format=question_format,
        )

        # Combine LLM and rule-based detection (LLM takes precedence if True)
        has_diagram = llm_diagram_needed or detection_result["diagram_needed"]
        diagram_type = detection_result["diagram_type"]
        diagram_description = llm_diagram_desc or detection_result.get("reason", "")
        diagram_svg_base64 = None
        diagram_elements = None

        # Generate diagram if needed
        if has_diagram and diagram_type:
            logger.info(f"Generating {diagram_type} diagram for {question_id}")

            # Build diagram elements
            diagram_elements = build_diagram_elements(
                diagram_type=diagram_type,
                question_text=question_text,
                topic=topic,
            )

            # Call diagram generation tool
            try:
                diagram_result = generate_diagram_tool.func(
                    diagram_description=diagram_description,
                    diagram_type=diagram_type,
                    elements=diagram_elements,
                )

                if diagram_result.get("success"):
                    diagram_svg_base64 = diagram_result.get("diagram_svg_base64")
                    diagram_elements = diagram_result.get("diagram_elements", diagram_elements)
                    diagram_description = diagram_result.get(
                        "diagram_description", diagram_description
                    )
                    logger.info(f"Diagram generated successfully for {question_id}")
                else:
                    logger.warning(f"Diagram generation failed: {diagram_result.get('error')}")
                    has_diagram = False
            except Exception as e:
                logger.error(f"Error generating diagram: {e}")
                has_diagram = False

        # Build tags
        tags = [
            chapter.lower().replace(" ", "-"),
            topic.lower().replace(" ", "-"),
            nature.lower(),
        ]
        if has_diagram:
            tags.append(diagram_type)

        # Combine generation metadata
        generation_metadata = {
            **llm_result.get("generation_metadata", {}),
            "retrieval_metadata": retrieval_result.get("retrieval_metadata", {}),
            "diagram_detection": detection_result,
            "diagram_generated": has_diagram and diagram_svg_base64 is not None,
        }

        # Build final assembled question
        assembled_question = {
            "question_id": question_id,
            "question_text": question_text,
            "section_id": blueprint_ref.get("section_id", ""),
            "question_number": question_number,
            "chapter": chapter,
            "topic": topic,
            "question_format": question_format,
            "marks": marks,
            "options": options,
            "correct_answer": correct_answer,
            "difficulty": difficulty,
            "bloom_level": bloom_level.lower() if isinstance(bloom_level, str) else bloom_level,
            "nature": nature,
            "has_diagram": has_diagram,
            "diagram_type": diagram_type if has_diagram else None,
            "diagram_svg_base64": diagram_svg_base64,
            "diagram_description": diagram_description if has_diagram else None,
            "diagram_elements": diagram_elements if has_diagram else None,
            "explanation": explanation,
            "hints": hints,
            "prerequisites": prerequisites,
            "common_mistakes": common_mistakes,
            "tags": tags,
            "quality_score": quality_score,
            "generation_metadata": generation_metadata,
            "status": "success",
            "error": None,
            "error_phase": None,
        }

        logger.info(f"Successfully assembled question {question_id}")
        return assembled_question

    except Exception as e:
        logger.exception(f"Error assembling question: {e}")
        return {
            "question_id": retrieval_result.get("question_id", f"ERR-{question_number}"),
            "question_text": f"[Error: Could not assemble question - {str(e)}]",
            "chapter": retrieval_result.get("chapter", ""),
            "topic": retrieval_result.get("topic", ""),
            "question_format": retrieval_result.get("question_format", "MCQ"),
            "marks": retrieval_result.get("marks", 1),
            "options": None,
            "correct_answer": None,
            "difficulty": retrieval_result.get("difficulty", "medium"),
            "bloom_level": retrieval_result.get("bloom_level", "understand"),
            "nature": retrieval_result.get("nature", "NUMERICAL"),
            "has_diagram": False,
            "diagram_type": None,
            "diagram_svg_base64": None,
            "diagram_description": None,
            "diagram_elements": None,
            "explanation": f"Assembly error: {str(e)}",
            "hints": [],
            "prerequisites": [],
            "common_mistakes": [],
            "tags": [],
            "quality_score": None,
            "generation_metadata": {"error": True, "error_message": str(e)},
            "status": "failed",
            "error": str(e),
            "error_phase": "assembly",
        }
