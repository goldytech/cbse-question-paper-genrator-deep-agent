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


@pytest.fixture
def sample_tavily_results():
    """Return sample Tavily search results."""
    return [
        {
            "title": f"CBSE Question {i}",
            "content": f"Sample question content about polynomials {i}. Find the zeros of x² - 5x + 6.",
            "url": f"https://example.com/question-{i}",
        }
        for i in range(15)
    ]


@pytest.fixture
def mock_tavily_client():
    """Mock Tavily client for testing."""
    with patch("question_generation.orchestrator._get_tavily_client") as mock:
        client = Mock()
        client.search.return_value = {
            "results": [
                {
                    "title": f"Result {i}",
                    "content": f"Content {i}",
                    "url": f"http://test{i}.com",
                }
                for i in range(15)
            ]
        }
        mock.return_value = client
        yield client


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
