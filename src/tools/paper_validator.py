"""Paper validation tool for generated question papers."""

import json
from typing import Dict, List, Optional
from langchain_core.tools import tool


@tool
def validate_paper_tool(paper_path: str, blueprint_path: str) -> Dict:
    """
    Validates generated question paper matches blueprint constraints.

    Args:
        paper_path: Path to generated paper JSON
        blueprint_path: Path to original blueprint JSON

    Returns:
        {
          valid: bool,
          issues: list[str],
          warnings: list[str]
        }
    """
    issues = []
    warnings = []

    try:
        # Load both files
        with open(paper_path, "r") as f:
            paper = json.load(f)

        with open(blueprint_path, "r") as f:
            blueprint = json.load(f)

        # Check 1: Total marks match
        expected_marks = blueprint.get("exam_metadata", {}).get("total_marks", 0)
        actual_marks = paper.get("total_marks", 0)

        if expected_marks != actual_marks:
            issues.append(f"Total marks mismatch: expected {expected_marks}, actual {actual_marks}")

        # Check 2: Question count per section
        blueprint_sections = {s.get("section_id"): s for s in blueprint.get("sections", [])}

        for section in paper.get("sections", []):
            section_id = section.get("section_id")

            if section_id not in blueprint_sections:
                issues.append(f"Section {section_id}: not in blueprint")
                continue

            # Handle nested questions structure
            questions_key = section.get("questions", [])
            questions_count = len(questions_key) if isinstance(questions_key, list) else 0

            blueprint_section = blueprint_sections.get(section_id, {})
            expected = blueprint_section.get(
                "questions PROVIDED", blueprint_section.get("questions", {}).get("provided", 0)
            )

            # Also check for flat key
            if blueprint_section.get("questions_provided"):
                expected = blueprint_section["questions_provided"]
            elif blueprint_section.get("questions", {}).get("provided"):
                expected = blueprint_section["questions"]["provided"]

            if expected != questions_count:
                issues.append(
                    f"Section {section_id}: expected {expected} questions, got {questions_count}"
                )

        # Check 3: Chapter/topic coverage
        blueprint_chapters = blueprint.get("syllabus_scope", {}).get("chapters_included", [])
        blueprint_topics = blueprint.get("syllabus_scope", {}).get("topics", {})
        valid_chapters = set([c.lower() for c in blueprint_chapters])

        for section in paper.get("sections", []):
            questions = section.get("questions", [])
            if not isinstance(questions, list):
                questions = section.get("questions", [])

            for question in questions:
                if not isinstance(question, dict):
                    continue

                chapter = question.get("chapter", "").lower()

                if chapter and chapter not in valid_chapters:
                    issues.append(
                        f"Question {question.get('question_id', 'unknown')}: "
                        f"chapter '{question.get('chapter')}' not in blueprint"
                    )

        # Check 4: Internal choice alignment
        for section in paper.get("sections", []):
            section_id = section.get("section_id")
            blueprint_section = blueprint_sections.get(section_id, {})

            # Get internal choice config
            ic_config = blueprint_section.get("internal_choice", {})
            ic_type = ic_config.get("type") if isinstance(ic_config, dict) else None

            if ic_type == "any_n_out_of_m":
                provided = ic_config.get("provided", 0)
                actual_count = len(section.get("questions", []))

                if provided != actual_count:
                    issues.append(
                        f"Section {section_id}: expected {provided} questions "
                        f"for any_n_out_of_m, got {actual_count}"
                    )

        # Warning: Check for potential duplicate questions
        question_texts = []
        for section in paper.get("sections", []):
            questions = section.get("questions", [])
            if isinstance(questions, list):
                for q in questions:
                    question_texts.append(q.get("question_text", ""))

        if len(question_texts) != len(set(question_texts)):
            warnings.append("Potential duplicate questions detected")

        # Check 5: All required fields in questions
        required_question_fields = [
            "question_id",
            "question_text",
            "chapter",
            "topic",
            "question_format",
            "marks",
            "difficulty",
        ]

        for section in paper.get("sections", []):
            questions = section.get("questions", [])
            if isinstance(questions, list):
                for q in questions:
                    if isinstance(q, dict):
                        for field in required_question_fields:
                            if field not in q:
                                warnings.append(
                                    f"Question {q.get('question_id', 'unknown')}: "
                                    f"missing field '{field}'"
                                )
                                break

    except FileNotFoundError as e:
        issues.append(f"File not found: {str(e)}")
    except json.JSONDecodeError as e:
        issues.append(f"Invalid JSON: {str(e)}")
    except Exception as e:
        issues.append(f"Validation error: {str(e)}")

    return {"valid": len(issues) == 0, "issues": issues, "warnings": warnings}
