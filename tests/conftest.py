"""Pytest configuration and fixtures for blueprint validation tests."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir():
    """Return the path to the fixtures' directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def exam_blueprints_dir(fixtures_dir):
    """Return the path to the exam blueprints fixtures directory."""
    return fixtures_dir / "exam_blueprints"


@pytest.fixture
def master_blueprints_dir(fixtures_dir):
    """Return the path to the master blueprints fixtures directory."""
    return fixtures_dir / "master_blueprints"


@pytest.fixture
def master_blueprint_path(master_blueprints_dir):
    """Return the path to the mathematics class 10 master blueprint."""
    return str(master_blueprints_dir / "mathematics_class10.json")


@pytest.fixture
def master_blueprint_data(master_blueprint_path):
    """Load and return the master blueprint data."""
    with open(master_blueprint_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def valid_exam_blueprint_path(exam_blueprints_dir):
    """Return the path to a valid schema 1.1 exam blueprint."""
    return str(exam_blueprints_dir / "valid_schema_11.json")


@pytest.fixture
def valid_exam_blueprint_data(valid_exam_blueprint_path):
    """Load and return a valid exam blueprint data."""
    with open(valid_exam_blueprint_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def invalid_schema_10_path(exam_blueprints_dir):
    """Return the path to an invalid schema 1.0 exam blueprint."""
    return str(exam_blueprints_dir / "invalid_schema_10.json")


@pytest.fixture
def missing_topics_path(exam_blueprints_dir):
    """Return the path to a blueprint missing topics."""
    return str(exam_blueprints_dir / "missing_topics.json")


@pytest.fixture
def invalid_topic_focus_path(exam_blueprints_dir):
    """Return the path to a blueprint with invalid topic_focus."""
    return str(exam_blueprints_dir / "invalid_topic_focus.json")


@pytest.fixture
def invalid_format_path(exam_blueprints_dir):
    """Return the path to a blueprint with an invalid question format."""
    return str(exam_blueprints_dir / "invalid_format.json")


@pytest.fixture
def invalid_internal_choice_path(exam_blueprints_dir):
    """Return the path to a blueprint with an invalid internal choice."""
    return str(exam_blueprints_dir / "invalid_internal_choice.json")


@pytest.fixture
def all_topics_keyword_path(exam_blueprints_dir):
    """Return the path to a blueprint using the ALL_TOPICS keyword."""
    return str(exam_blueprints_dir / "all_topics_keyword.json")


@pytest.fixture
def missing_topic_focus_path(exam_blueprints_dir):
    """Return the path to a blueprint missing topic_focus (should be valid)."""
    return str(exam_blueprints_dir / "missing_topic_focus.json")


@pytest.fixture
def comprehensive_violations_path(exam_blueprints_dir):
    """Return the path to a blueprint with multiple violations."""
    return str(exam_blueprints_dir / "comprehensive_violations.json")


@pytest.fixture
def advanced_formats_path(exam_blueprints_dir):
    """Return the path to a blueprint with advanced formats."""
    return str(exam_blueprints_dir / "advanced_formats.json")


@pytest.fixture
def invalid_topic_focus_type_path(exam_blueprints_dir):
    """Return the path to a blueprint with non-array topic_focus."""
    return str(exam_blueprints_dir / "invalid_topic_focus_type.json")


@pytest.fixture
def nonexistent_master_blueprint_path():
    """Return a path to a non-existent master blueprint."""
    return "tests/fixtures/master_blueprints/nonexistent.json"


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def skills_dir(project_root):
    """Return the skills directory."""
    return project_root / "src" / "skills"


@pytest.fixture(autouse=True)
def add_src_to_path(project_root):
    """Add the src directory to sys.path for imports."""
    import sys

    src_path = str(project_root / "src")
    sys.path.insert(0, src_path)
    yield
    sys.path.remove(src_path)
