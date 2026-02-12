"""Pytest configuration and shared fixtures for question generation tests."""

import json
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

# Add src to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from question_generation.orchestrator import (
    QuestionRequirements,
    QuestionCache,
    DiagramStorage,
)


@pytest.fixture
def sample_blueprint():
    """Return a sample exam blueprint."""
    return {
        "metadata": {
            "class": 10,
            "subject": "Mathematics",
            "assessment_type": "First Term",
            "total_marks": 50,
        },
        "duration_minutes": 120,
        "syllabus_scope": {
            "chapters": [
                {
                    "chapter_name": "Polynomials",
                    "topics": ["Zeros of a Polynomial", "Relationship between Zeros"],
                },
                {
                    "chapter_name": "Real Numbers",
                    "topics": ["Euclid's Division Lemma", "Fundamental Theorem"],
                },
            ]
        },
        "sections": [
            {
                "section_id": "A",
                "section_title": "Multiple Choice Questions",
                "question_format": "MCQ",
                "marks_per_question": 1,
                "questions_provided": 10,
                "questions_attempt": 10,
                "topic_focus": ["Zeros of a Polynomial", "Euclid's Division Lemma"],
                "allowed_question_natures": ["NUMERICAL", "REASONING"],
                "cognitive_level_hint": ["REMEMBER", "UNDERSTAND"],
            }
        ],
    }


@pytest.fixture
def sample_requirements_easy():
    """Return sample question requirements - easy difficulty."""
    return QuestionRequirements(
        class_level=10,
        subject="Mathematics",
        chapter="Polynomials",
        topic="Zeros of a Polynomial",
        question_format="MCQ",
        marks=1,
        difficulty="easy",
        nature="NUMERICAL",
        cognitive_level="REMEMBER",
    )


@pytest.fixture
def sample_requirements_medium():
    """Return sample question requirements - medium difficulty."""
    return QuestionRequirements(
        class_level=10,
        subject="Mathematics",
        chapter="Triangles",
        topic="Pythagoras Theorem",
        question_format="SHORT",
        marks=3,
        difficulty="medium",
        nature="PROOF",
        cognitive_level="UNDERSTAND",
    )


@pytest.fixture
def sample_requirements_hard():
    """Return sample question requirements - hard difficulty."""
    return QuestionRequirements(
        class_level=10,
        subject="Mathematics",
        chapter="Coordinate Geometry",
        topic="Distance Formula",
        question_format="LONG",
        marks=5,
        difficulty="hard",
        nature="WORD_PROBLEM",
        cognitive_level="APPLY",
    )


# =============================================================================
# TAVILY TEST FIXTURES - DISABLED
# =============================================================================
# These fixtures were used for testing Tavily search functionality.
# They are commented out pending Qdrant vector database integration.
#
# @pytest.fixture
# def sample_tavily_results():
#     """Return sample Tavily search results."""
#     return [
#         {
#             "title": f"CBSE Question {i}",
#             "content": f"Sample question content about polynomials {i}. Find the zeros of x² - 5x + 6.",
#             "url": f"https://example.com/question-{i}",
#         }
#         for i in range(15)
#     ]
#
#
# @pytest.fixture
# def mock_tavily_client():
#     """Mock Tavily client for testing."""
#     with patch("question_generation.orchestrator._get_tavily_client") as mock:
#         client = Mock()
#         client.search.return_value = {
#             "results": [
#                 {
#                     "title": f"Result {i}",
#                     "content": f"Content {i}",
#                     "url": f"http://test{i}.com",
#                 }
#                 for i in range(15)
#             ]
#         }
#         mock.return_value = client
#         yield client
# =============================================================================


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Provide temporary cache directory."""
    return tmp_path / "cache"


@pytest.fixture
def question_cache(temp_cache_dir):
    """Provide QuestionCache instance with temp directory."""
    db_path = temp_cache_dir / "test_cache.db"
    return QuestionCache(str(db_path))


@pytest.fixture
def diagram_storage(temp_cache_dir):
    """Provide DiagramStorage instance with temp directory."""
    diagrams_dir = temp_cache_dir / "diagrams"
    return DiagramStorage(str(diagrams_dir))


@pytest.fixture
def sample_question_data():
    """Return sample question data."""
    return {
        "question_id": "MATH-10-POL-MCQ-001",
        "question_text": "Find the zeros of x² - 5x + 6",
        "chapter": "Polynomials",
        "topic": "Zeros of a Polynomial",
        "question_format": "MCQ",
        "marks": 1,
        "options": ["A) 2, 3", "B) 1, 6", "C) -2, -3", "D) -1, -6"],
        "correct_answer": "A",
        "difficulty": "easy",
        "bloom_level": "remember",
        "nature": "NUMERICAL",
        "has_diagram": False,
        "diagram_type": None,
        "diagram_svg_base64": None,
        "diagram_description": None,
        "diagram_elements": None,
        "tags": ["polynomials", "zeros", "numerical"],
    }


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# BLUEPRINT VALIDATOR TEST FIXTURES
# =============================================================================
# Fixtures for blueprint validation tests using fixture files

FIXTURES_DIR = Path(__file__).parent / "fixtures"
EXAM_BLUEPRINTS_DIR = FIXTURES_DIR / "exam_blueprints"
MASTER_BLUEPRINTS_DIR = FIXTURES_DIR / "master_blueprints"


@pytest.fixture
def valid_exam_blueprint_path():
    """Path to a valid exam blueprint for testing."""
    return str(EXAM_BLUEPRINTS_DIR / "valid_schema_11.json")


@pytest.fixture
def invalid_schema_10_path():
    """Path to an exam blueprint with invalid schema version."""
    return str(EXAM_BLUEPRINTS_DIR / "invalid_schema_10.json")


@pytest.fixture
def invalid_format_path():
    """Path to an exam blueprint with invalid question format."""
    return str(EXAM_BLUEPRINTS_DIR / "invalid_format.json")


@pytest.fixture
def invalid_internal_choice_path():
    """Path to an exam blueprint with invalid internal choice configuration."""
    return str(EXAM_BLUEPRINTS_DIR / "invalid_internal_choice.json")


@pytest.fixture
def missing_topics_path():
    """Path to an exam blueprint with missing topics in syllabus scope."""
    return str(EXAM_BLUEPRINTS_DIR / "missing_topics.json")


@pytest.fixture
def all_topics_keyword_path():
    """Path to an exam blueprint using ALL_TOPICS keyword."""
    return str(EXAM_BLUEPRINTS_DIR / "all_topics_keyword.json")


@pytest.fixture
def missing_topic_focus_path():
    """Path to an exam blueprint with missing topic_focus in sections."""
    return str(EXAM_BLUEPRINTS_DIR / "missing_topic_focus.json")


@pytest.fixture
def invalid_topic_focus_path():
    """Path to an exam blueprint with invalid topic_focus values."""
    return str(EXAM_BLUEPRINTS_DIR / "invalid_topic_focus.json")


@pytest.fixture
def invalid_topic_focus_type_path():
    """Path to an exam blueprint with invalid topic_focus type."""
    return str(EXAM_BLUEPRINTS_DIR / "invalid_topic_focus_type.json")


@pytest.fixture
def comprehensive_violations_path():
    """Path to an exam blueprint with multiple violations."""
    return str(EXAM_BLUEPRINTS_DIR / "comprehensive_violations.json")


@pytest.fixture
def advanced_formats_path():
    """Path to an exam blueprint with advanced question formats."""
    return str(EXAM_BLUEPRINTS_DIR / "advanced_formats.json")


@pytest.fixture
def master_blueprint_path():
    """Path to the master policy blueprint for validation."""
    return str(MASTER_BLUEPRINTS_DIR / "mathematics_class10.json")


@pytest.fixture
def project_root():
    """Path to the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def master_blueprint_data():
    """Load master policy blueprint data for testing."""
    with open(MASTER_BLUEPRINTS_DIR / "mathematics_class10.json", "r") as f:
        return json.load(f)


@pytest.fixture
def valid_exam_blueprint_data():
    """Load valid exam blueprint data for testing."""
    with open(EXAM_BLUEPRINTS_DIR / "valid_schema_11.json", "r") as f:
        return json.load(f)
