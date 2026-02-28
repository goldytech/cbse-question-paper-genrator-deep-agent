"""Question Assembler Tool.

This tool assembles CBSE-compliant questions from retrieved chunks and LLM-generated content.
Supports both single question assembly and section compilation with CBSE format.
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

# Global counter for sequential question numbering across sections
_question_counter = 0

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


def reset_question_counter():
    """Reset counter for new paper generation."""
    global _question_counter
    _question_counter = 0


def get_next_question_number() -> int:
    """Get next sequential question number (Q1, Q2, Q3...)."""
    global _question_counter
    _question_counter += 1
    return _question_counter


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


def convert_options_to_dict(options_raw) -> Dict[str, str]:
    """Convert options from array format to dict format.

    Converts ["A) text", "B) text", ...] to {"A": "text", "B": "text", ...}

    Args:
        options_raw: Raw options (list or dict)

    Returns:
        Dictionary format options
    """
    options = {}

    if isinstance(options_raw, list):
        for opt in options_raw:
            if opt and len(opt) > 2 and opt[0] in "ABCD" and opt[1] == ")":
                key = opt[0]  # "A", "B", "C", or "D"
                value = opt[2:].strip()  # Remove "X) " prefix
                options[key] = value
    elif isinstance(options_raw, dict):
        options = options_raw  # Already in correct format

    return options


def apply_cbse_internal_choice(questions: List[Dict], section_id: str) -> List[Dict]:
    """Apply CBSE internal choice rules to questions.

    CBSE Format:
    - Sections B, C, D: Internal choice in last 2 questions
    - Section E: Internal choice in ALL questions (case study)

    Args:
        questions: List of question dictionaries
        section_id: Section identifier (A, B, C, D, E)

    Returns:
        Updated questions with internal_choice flags
    """
    total_questions = len(questions)

    # Sections B, C, D: Choice in last 2 questions
    if section_id in ["B", "C", "D"] and total_questions >= 2:
        for i in range(total_questions - 2, total_questions):
            questions[i]["internal_choice"] = True
            questions[i]["choice_text"] = "OR"
            questions[i]["choice_type"] = "alternative_question"

    # Section E: Case Study - All questions have sub-parts
    elif section_id == "E":
        for q in questions:
            q["has_sub_questions"] = True
            q["sub_questions"] = [
                {"part": "(i)", "marks": 1},
                {"part": "(ii)", "marks": 1},
                {"part": "(iii)", "marks": 2},
            ]
            q["internal_choice"] = True
            q["choice_text"] = "Case Study based question"

    return questions


def compile_section(
    questions: List[Dict],
    section_id: str,
    section_title: str,
    marks_per_question: int,
    question_format: str,
) -> Dict[str, Any]:
    """Compile questions into CBSE section format.

    Organizes questions into a CBSE-compliant section with:
    - Sequential numbering (Q1, Q2, Q3...)
    - Section marks calculation
    - Internal choice flags per CBSE rules
    - Section metadata

    Args:
        questions: List of assembled questions
        section_id: Section identifier (A, B, C, D, E)
        section_title: Section title (e.g., "MCQs", "Short Answer")
        marks_per_question: Marks for each question in section
        question_format: Format of questions (MCQ, SHORT, LONG, CASE_STUDY)

    Returns:
        CBSE-formatted section dictionary
    """
    total_questions = len(questions)
    section_total_marks = total_questions * marks_per_question

    # Apply CBSE internal choice rules
    questions = apply_cbse_internal_choice(questions, section_id)

    return {
        "section_id": section_id,
        "title": section_title,
        "question_format": question_format,
        "marks_per_question": marks_per_question,
        "questions_provided": total_questions,
        "questions_attempt": total_questions,  # CBSE: all compulsory
        "section_total_marks": section_total_marks,
        "questions": questions,
        "internal_choice_available": section_id in ["B", "C", "D", "E"],
        "cbse_format": True,
    }


@tool
def assemble_question_tool(
    retrieval_result: Dict[str, Any],
    llm_result: Dict[str, Any],
    question_number: int,
    section_config: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Assembles a CBSE-compliant question from retrieved chunks and LLM-generated content.

    This tool takes the results from chunk retrieval and LLM question generation,
    combines them into a complete CBSE question object, detects diagram needs,
    generates diagrams when required, and optionally compiles entire sections.

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
            - options: MCQ options (list ["A) text", ...] or dict {"A": "text", ...})
            - correct_answer: Correct answer
            - explanation: Solution explanation
            - diagram_needed: Boolean from LLM
            - diagram_description: Diagram description from LLM

        question_number: Question number within section (1-based)

        section_config: Optional section compilation config:
            - section_id: "A", "B", "C", "D", "E"
            - title: Section title
            - marks_per_question: Marks per question
            - compile_section: bool - if True, return section format

    Returns:
        Complete assembled question or compiled section with:
        - question_id: Formatted ID
        - question_text: Final question text
        - chapter, topic, format, marks, difficulty, etc.
        - options: Dict format {"A": "text", "B": "text", ...}
        - correct_answer (for MCQ)
        - has_diagram, diagram_type, diagram_svg_base64 (if diagram generated)
        - explanation
        - internal_choice, has_sub_questions (CBSE format)
        - generation_metadata

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
        ...     "options": ["A) 3", "B) -3", "C) 0", "D) 1"],  # Or dict format
        ...     "correct_answer": "A",
        ...     "diagram_needed": False
        ... }
        >>> result = assemble_question_tool(retrieval, llm_output, 1)
        >>> print(result["question_id"])
        "MATH-10-POL-MCQ-001"
        >>> print(result["options"])
        {"A": "3", "B": "-3", "C": "0", "D": "1"}
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
                "options": {},
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
                "internal_choice": False,
                "choice_text": None,
                "has_sub_questions": False,
                "sub_questions": [],
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
                "options": {},
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
                "internal_choice": False,
                "choice_text": None,
                "has_sub_questions": False,
                "sub_questions": [],
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

        # Convert options to dict format (handles both array and dict input)
        options_raw = llm_result.get("options")
        options = convert_options_to_dict(options_raw)

        correct_answer = llm_result.get("correct_answer")
        explanation = llm_result.get("explanation")

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
                diagram_result = generate_diagram_tool.invoke(
                    {
                        "diagram_description": diagram_description,
                        "diagram_type": diagram_type,
                        "elements": diagram_elements,
                    }
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

        # Combine generation metadata
        generation_metadata = {
            **llm_result.get("generation_metadata", {}),
            "retrieval_metadata": retrieval_result.get("retrieval_metadata", {}),
            "diagram_detection": detection_result,
            "diagram_generated": has_diagram and diagram_svg_base64 is not None,
        }

        # Build final assembled question (STREAMLINED SCHEMA)
        assembled_question = {
            "question_id": question_id,
            "question_text": question_text,
            "section_id": blueprint_ref.get("section_id", ""),
            "question_number": question_number,
            "chapter": chapter,
            "topic": topic,
            "question_format": question_format,
            "marks": marks,
            "options": options,  # Dict format: {"A": "text", "B": "text", ...}
            "correct_answer": correct_answer,
            "difficulty": difficulty,
            "bloom_level": bloom_level.lower() if isinstance(bloom_level, str) else bloom_level,
            "nature": nature,
            "has_diagram": has_diagram,
            "diagram_needed": has_diagram,  # Duplicate for compatibility
            "diagram_type": diagram_type if has_diagram else None,
            "diagram_svg_base64": diagram_svg_base64,
            "diagram_description": diagram_description if has_diagram else None,
            "diagram_elements": diagram_elements if has_diagram else None,
            "explanation": explanation,
            "internal_choice": False,  # Will be set by compile_section()
            "choice_text": None,
            "has_sub_questions": False,
            "sub_questions": [],
            "generation_metadata": generation_metadata,
            "status": "success",
            "error": None,
            "error_phase": None,
        }

        # If section compilation requested, compile the section
        if section_config and section_config.get("compile_section", False):
            section = compile_section(
                questions=[assembled_question],  # Single question in section for now
                section_id=section_config.get("section_id", "A"),
                section_title=section_config.get("title", "Section A"),
                marks_per_question=marks,
                question_format=question_format,
            )
            logger.info(f"Successfully compiled section {section['section_id']}")
            return section

        logger.info(f"Successfully assembled question {question_id}")
        return assembled_question

    except Exception as e:
        logger.exception(f"Error assembling question: {e}")
        return {
            "question_id": retrieval_result.get("question_id", f"ERR-{question_number}"),
            "question_text": f"[Error: Could not assemble question - {str(e)}]",
            "section_id": retrieval_result.get("blueprint_reference", {}).get("section_id", ""),
            "question_number": question_number,
            "chapter": retrieval_result.get("chapter", ""),
            "topic": retrieval_result.get("topic", ""),
            "question_format": retrieval_result.get("question_format", "MCQ"),
            "marks": retrieval_result.get("marks", 1),
            "options": {},
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
            "internal_choice": False,
            "choice_text": None,
            "has_sub_questions": False,
            "sub_questions": [],
            "generation_metadata": {"error": True, "error_message": str(e)},
            "status": "failed",
            "error": str(e),
            "error_phase": "assembly",
        }


@tool
def compile_section_tool(
    questions: List[Dict[str, Any]],
    section_id: str,
    section_title: str,
    marks_per_question: int,
    question_format: str,
) -> Dict[str, Any]:
    """Compile multiple questions into a CBSE section format.

    This tool organizes assembled questions into a CBSE-compliant section
    with proper internal choice rules, sequential numbering, and section metadata.

    Args:
        questions: List of assembled question dictionaries
        section_id: Section identifier (A, B, C, D, E)
        section_title: Section title (e.g., "MCQs", "Short Answer Questions")
        marks_per_question: Marks allocated to each question
        question_format: Question format type (MCQ, SHORT, LONG, CASE_STUDY)

    Returns:
        CBSE-formatted section dictionary with:
        - section_id, title, format, marks info
        - questions: List with internal_choice flags applied
        - section_total_marks: Calculated total
        - internal_choice_available: Boolean

    Example:
        >>> questions = [assembled_q1, assembled_q2, ...]
        >>> section = compile_section_tool(
        ...     questions=questions,
        ...     section_id="B",
        ...     section_title="Short Answer Questions",
        ...     marks_per_question=2,
        ...     question_format="SHORT"
        ... )
        >>> print(section["section_total_marks"])
        10
        >>> print(section["questions"][-1]["internal_choice"])
        True  # Last question has choice
    """
    return compile_section(
        questions=questions,
        section_id=section_id,
        section_title=section_title,
        marks_per_question=marks_per_question,
        question_format=question_format,
    )
