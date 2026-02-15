"""Question Generator Tool for CBSE Question Paper Generation.

This tool orchestrates the question paper generation process using subagents:
- cbse-question-retriever: Retrieves CBSE content and generates questions
- question-assembler: Assembles questions into final format

NOTE: This tool is now a wrapper that delegates to the cbse-question-retriever subagent.
Direct question generation logic will be moved to the subagent.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from langchain_core.tools import tool

# =============================================================================
# TAVILY SEARCH INTEGRATION - DISABLED
# =============================================================================
# The following code is commented out as Tavily is being replaced with Qdrant
# vector database for CBSE question retrieval.
#
# To re-enable Tavily:
# 1. Uncomment the import below
# 2. Uncomment the TAVILY_CONFIG dictionary
# 3. Uncomment the _get_tavily_client() function
# 4. Uncomment the _search_tavily() function
# 5. Re-enable search calls in _generate_single_question()
#
# from tavily import TavilyClient
#
# # Configuration
# TAVILY_CONFIG = {
#     "max_results": 15,
#     "search_depth": "advanced",
#     "include_raw_content": True,
#     "include_domains": [
#         "cbseacademic.nic.in",
#         "byjus.com",
#         "vedantu.com",
#         "learn.careers360.com",
#     ],
# }
# =============================================================================

RATE_LIMIT_PER_MINUTE = 100
MAX_CONCURRENT = 15


@dataclass
class QuestionRequirements:
    """Requirements for a single question."""

    class_level: int
    subject: str
    chapter: str
    topic: str
    question_format: str
    marks: int
    difficulty: str
    nature: str
    cognitive_level: str


# =============================================================================
# TAVILY CLIENT FUNCTION - DISABLED
# =============================================================================
# This function was used to create Tavily client instances for search operations.
# Currently disabled pending Qdrant vector database integration.
#
# def _get_tavily_client() -> TavilyClient:
#     """Get or create Tavily client."""
#     api_key = os.environ.get("TAVILY_API_KEY")
#     if not api_key:
#         raise ValueError("TAVILY_API_KEY not set in environment")
#     return TavilyClient(api_key=api_key)
# =============================================================================


# Semaphore for rate limiting
request_semaphore = asyncio.Semaphore(MAX_CONCURRENT)


async def _optimize_query(requirements: QuestionRequirements) -> str:
    """Use query-optimizer subagent to generate search query."""
    # This would be called via the task() tool in practice
    # For now, construct a basic query
    query_parts = [
        "CBSE",
        f"Class {requirements.class_level}",
        requirements.subject,
        requirements.chapter,
        requirements.topic,
        requirements.difficulty,
        requirements.question_format,
        "practice questions",
    ]
    return " ".join(query_parts)


# =============================================================================
# TAVILY SEARCH FUNCTION - DISABLED
# =============================================================================
# This function performed web searches using Tavily to find CBSE question examples.
# Currently disabled pending Qdrant vector database integration.
#
# async def _search_tavily(query: str) -> List[Dict]:
#     """Search Tavily for question examples."""
#     async with request_semaphore:
#         try:
#             client = _get_tavily_client()
#             results = client.search(
#                 query=query,
#                 max_results=TAVILY_CONFIG["max_results"],
#                 search_depth=TAVILY_CONFIG["search_depth"],
#                 include_raw_content=TAVILY_CONFIG["include_raw_content"],
#                 include_domains=TAVILY_CONFIG["include_domains"],
#             )
#             return results.get("results", [])
#         except Exception as e:
#             print(f"Tavily search error: {e}")
#             return []
# =============================================================================


async def _assemble_question(
    search_results: List[Dict],
    requirements: QuestionRequirements,
    question_number: int,
) -> Dict:
    """Use question-assembler subagent to create question."""
    # Generate question ID
    chapter_abbr = _get_chapter_abbreviation(requirements.chapter)
    format_abbr = _get_format_abbreviation(requirements.question_format)
    question_id = (
        f"MATH-{requirements.class_level}-{chapter_abbr}-{format_abbr}-{question_number:03d}"
    )

    # This would use the subagent in practice
    # For now, create a basic structure
    question = {
        "question_id": question_id,
        "question_text": f"Sample question for {requirements.topic}",
        "chapter": requirements.chapter,
        "topic": requirements.topic,
        "question_format": requirements.question_format,
        "marks": requirements.marks,
        "options": None,
        "correct_answer": None,
        "difficulty": requirements.difficulty,
        "bloom_level": requirements.cognitive_level.lower(),
        "nature": requirements.nature,
        "has_diagram": False,
        "diagram_type": None,
        "diagram_svg_base64": None,
        "diagram_description": None,
        "diagram_elements": None,
        "tags": [
            requirements.chapter.lower().replace(" ", "-"),
            requirements.topic.lower().replace(" ", "-"),
            requirements.nature.lower(),
        ],
    }

    # Add MCQ options if applicable
    if requirements.question_format == "MCQ":
        question["options"] = ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"]
        question["correct_answer"] = "A"

    return question


def _get_chapter_abbreviation(chapter: str) -> str:
    """Get chapter abbreviation for question ID."""
    mapping = {
        "real numbers": "REA",
        "polynomials": "POL",
        "linear equations": "LIN",
        "quadratic equations": "QUAD",
        "arithmetic progressions": "AP",
        "coordinate geometry": "COG",
        "triangles": "TRI",
        "circles": "CIR",
        "mensuration": "MEN",
        "statistics": "STA",
        "probability": "PRO",
    }
    return mapping.get(chapter.lower(), "GEN")


def _get_format_abbreviation(format_str: str) -> str:
    """Get format abbreviation for question ID."""
    mapping = {
        "mcq": "MCQ",
        "very_short": "VSQ",
        "short": "SA",
        "long": "LA",
        "case_study": "CS",
    }
    return mapping.get(format_str.lower(), "UNK")


async def _generate_single_question(
    requirements: QuestionRequirements,
    question_number: int,
) -> Dict:
    """Generate a single question."""
    # TEMPORARY: This function should delegate to cbse-question-retriever subagent
    # For now, generate a placeholder question
    question = await _assemble_question([], requirements, question_number)
    return question


@tool
def generate_question_paper_tool(
    blueprint_path: str,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generates complete CBSE question paper from blueprint.

    Args:
        blueprint_path: Path to exam blueprint JSON file
        output_path: Where to save generated paper (auto-generated if None)

    Returns:
        {
            "success": bool,
            "paper_path": str,
            "total_questions": int,
            "total_marks": int,
            "sections_generated": List[str],
            "difficulty_distribution": Dict[str, int],
            "error": Optional[str]
        }
    """
    try:
        # Load blueprint
        with open(blueprint_path, "r", encoding="utf-8") as f:
            blueprint = json.load(f)

        # Extract metadata
        metadata = blueprint.get("metadata", {})
        class_level = metadata.get("class", 10)
        subject = metadata.get("subject", "Mathematics")
        total_marks = metadata.get("total_marks", 0)

        # Get syllabus scope
        syllabus_scope = blueprint.get("syllabus_scope", {})
        chapters_data = syllabus_scope.get("chapters", [])

        # Build chapters/topics mapping
        chapters_topics = {}
        for chapter_data in chapters_data:
            chapter_name = chapter_data.get("chapter_name", "")
            topics = chapter_data.get("topics", [])
            chapters_topics[chapter_name] = topics

        # Process sections
        sections = []
        all_questions = []
        question_counter = 1
        difficulty_distribution = {"easy": 0, "medium": 0, "hard": 0}

        for section in blueprint.get("sections", []):
            section_id = section.get("section_id", "")
            questions_provided = section.get("questions_provided", 0)
            marks_per_question = section.get("marks_per_question", 0)
            question_format = section.get("question_format", "MCQ")
            topic_focus = section.get("topic_focus", [])
            allowed_natures = section.get("allowed_question_natures", ["NUMERICAL"])
            cognitive_hints = section.get("cognitive_level_hint", [])

            # Calculate difficulty distribution (40/40/20)
            easy_count = int(questions_provided * 0.4)
            medium_count = int(questions_provided * 0.4)
            hard_count = questions_provided - easy_count - medium_count

            section_questions = []

            for i in range(questions_provided):
                # Determine difficulty
                if i < easy_count:
                    difficulty = "easy"
                elif i < easy_count + medium_count:
                    difficulty = "medium"
                else:
                    difficulty = "hard"

                # Select topic
                topic = topic_focus[i % len(topic_focus)] if topic_focus else "General"

                # Find chapter for topic
                chapter = "General"
                for ch_name, topics in chapters_topics.items():
                    if topic in topics or topics == ["ALL_TOPICS"]:
                        chapter = ch_name
                        break

                # Select nature and cognitive level
                nature = (
                    allowed_natures[i % len(allowed_natures)] if allowed_natures else "NUMERICAL"
                )
                cognitive = (
                    cognitive_hints[i % len(cognitive_hints)] if cognitive_hints else "REMEMBER"
                )

                # Create requirements
                requirements = QuestionRequirements(
                    class_level=class_level,
                    subject=subject,
                    chapter=chapter,
                    topic=topic,
                    question_format=question_format,
                    marks=marks_per_question,
                    difficulty=difficulty,
                    nature=nature,
                    cognitive_level=cognitive,
                )

                # Generate question
                question = asyncio.run(_generate_single_question(requirements, question_counter))

                section_questions.append(question)
                all_questions.append(question)
                difficulty_distribution[difficulty] += 1
                question_counter += 1

            sections.append(
                {
                    "section_id": section_id,
                    "title": section.get("section_title", ""),
                    "questions": section_questions,
                    "section_total": questions_provided * marks_per_question,
                }
            )

        # Create paper structure
        paper = {
            "paper_id": f"{subject.upper()}-{class_level}-{datetime.now().strftime('%Y%m%d')}",
            "exam_metadata": {
                "class": class_level,
                "subject": subject,
                "exam_type": metadata.get("assessment_type", "Exam"),
                "total_marks": total_marks,
                "duration_minutes": blueprint.get("duration_minutes", 120),
            },
            "sections": sections,
            "total_marks": sum(q["marks"] for q in all_questions),
            "generated_at": datetime.now().isoformat(),
        }

        # Save paper
        if not output_path:
            output_path = f"output/{subject.lower()}_class{class_level}_paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(paper, f, indent=2)

        return {
            "success": True,
            "paper_path": output_path,
            "total_questions": len(all_questions),
            "total_marks": paper["total_marks"],
            "sections_generated": [s["section_id"] for s in sections],
            "difficulty_distribution": difficulty_distribution,
            "error": None,
        }

    except FileNotFoundError as e:
        return {"success": False, "error": f"Blueprint file not found: {str(e)}"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Invalid JSON in blueprint: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Generation error: {str(e)}"}


def _distribute_difficulties(total_questions: int) -> Dict[str, int]:
    """
    Distribute questions according to 40/40/20 rule.

    Args:
        total_questions: Total number of questions to distribute

    Returns:
        Dict with counts for easy, medium, hard
    """
    if total_questions == 0:
        return {"easy": 0, "medium": 0, "hard": 0}

    easy_count = int(total_questions * 0.4)
    medium_count = int(total_questions * 0.4)
    hard_count = total_questions - easy_count - medium_count

    return {
        "easy": easy_count,
        "medium": medium_count,
        "hard": hard_count,
    }
