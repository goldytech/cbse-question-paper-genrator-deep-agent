"""Blueprint validation tool for CBSE question papers.

Validates exam blueprints against master policy blueprints using two-blueprint validation.
"""

import json
import os
from typing import Dict, List, Optional, Any
from langchain_core.tools import tool


@tool
def validate_blueprint_tool(
    exam_blueprint_path: str,
    master_blueprint_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Validates exam blueprint against the master policy blueprint.

    Args:
        exam_blueprint_path: Path to exam blueprint (teacher-provided)
        master_blueprint_path: Path to master policy blueprint (optional, auto-discovers
                              from exam blueprint class/subject if not provided)

    Returns:
        {
            "valid": bool,
            "errors": list[str],
            "warnings": list[str],
            "validation_details": {
                "schema_version": str,
                "enforcement_mode": str,
                "strict_checks_passed": list[str],
                "strict_checks_failed": list[str],
                "advisory_checks_warnings": list[str]
            }
        }
    """
    errors = []
    warnings = []
    validation_details = {}

    try:
        # 1. Load exam blueprint
        with open(exam_blueprint_path, "r", encoding="utf-8") as f:
            exam_blueprint = json.load(f)

        # 2. Discover a master blueprint path if not provided
        if not master_blueprint_path:
            master_blueprint_path = _discover_master_blueprint_path(exam_blueprint)

        # 3. Load master blueprint
        if not os.path.exists(master_blueprint_path):
            errors.append(f"Master blueprint file not found: {master_blueprint_path}")
            return _create_result(False, errors, warnings, validation_details)

        with open(master_blueprint_path, "r", encoding="utf-8") as f:
            master_blueprint = json.load(f)

        # 4. Schema version check - compare exam with master blueprint
        exam_schema_version = exam_blueprint.get("schema_version")
        master_schema_version = master_blueprint.get("schema_version")

        if not exam_schema_version:
            errors.append("Missing schema_version in exam blueprint.")
            return _create_result(False, errors, warnings, validation_details)

        if not master_schema_version:
            errors.append("Missing schema_version in master blueprint.")
            return _create_result(False, errors, warnings, validation_details)

        if exam_schema_version != master_schema_version:
            errors.append(
                f"Schema version mismatch: exam blueprint has '{exam_schema_version}', "
                f"but master blueprint requires '{master_schema_version}'."
            )
            validation_details["schema_version"] = exam_schema_version
            return _create_result(False, errors, warnings, validation_details)

        validation_details["schema_version"] = exam_schema_version

        # 5. Get validation policies from the master blueprint
        validation_policies = master_blueprint.get("validation_policies", {})
        strict_checks = validation_policies.get("strict_checks", [])
        advisory_checks = validation_policies.get("advisory_checks", [])

        # 6. Get enforcement mode (global setting for ALL checks)
        cognitive_levels = master_blueprint.get("cognitive_levels", {})
        enforcement_mode = cognitive_levels.get("enforcement_mode", "STRICT")
        validation_details["enforcement_mode"] = enforcement_mode

        # 7. Get whitelists from the master blueprint
        allowed_question_formats = master_blueprint.get("allowed_question_formats", [])
        allowed_question_natures = master_blueprint.get("allowed_question_natures", [])
        internal_choice_supported_types = master_blueprint.get("internal_choice_rules", {}).get(
            "supported_types", []
        )

        # 8. Get syllabus granularity policy
        syllabus_granularity = master_blueprint.get("syllabus_granularity_policy", {})
        topic_selection_required = syllabus_granularity.get("topic_selection_required", False)
        all_topics_keyword = syllabus_granularity.get("all_topics_keyword", "ALL_TOPICS")
        topic_level_is_primary_constraint = syllabus_granularity.get(
            "topic_level_is_primary_constraint", False
        )

        # Initialize check results
        strict_checks_passed = []
        strict_checks_failed = []
        advisory_checks_warnings = []

        # 9. Apply strict checks using match-case
        for check in strict_checks:
            match check:
                case "QUESTION_FORMAT_WHITELIST":
                    result = _validate_question_format_whitelist(
                        exam_blueprint, allowed_question_formats
                    )
                    if result["valid"]:
                        strict_checks_passed.append(check)
                    else:
                        if enforcement_mode in ["STRICT", "ADVISORY"]:
                            _handle_validation_result(
                                result, errors, warnings, strict_checks_failed, enforcement_mode
                            )

                case "INTERNAL_CHOICE_ARITHMETIC":
                    result = _validate_internal_choice_arithmetic(
                        exam_blueprint, internal_choice_supported_types
                    )
                    if result["valid"]:
                        strict_checks_passed.append(check)
                    else:
                        if enforcement_mode in ["STRICT", "ADVISORY"]:
                            _handle_validation_result(
                                result, errors, warnings, strict_checks_failed, enforcement_mode
                            )

                case "SYLLABUS_SCOPE_ENFORCEMENT":
                    result = _validate_syllabus_scope_enforcement(
                        exam_blueprint, topic_selection_required, all_topics_keyword
                    )
                    if result["valid"]:
                        strict_checks_passed.append(check)
                    else:
                        if enforcement_mode in ["STRICT", "ADVISORY"]:
                            _handle_validation_result(
                                result, errors, warnings, strict_checks_failed, enforcement_mode
                            )

                case "TOPIC_SCOPE_ENFORCEMENT":
                    result = _validate_topic_scope_enforcement(
                        exam_blueprint, all_topics_keyword, topic_level_is_primary_constraint
                    )
                    if result["valid"]:
                        strict_checks_passed.append(check)
                    else:
                        if enforcement_mode in ["STRICT", "ADVISORY"]:
                            _handle_validation_result(
                                result, errors, warnings, strict_checks_failed, enforcement_mode
                            )

                case _:
                    # Unknown strict check - skip or log warning
                    warnings.append(f"Unknown strict check: {check}")

        # 10. Apply advisory checks (only warnings) using match-case
        for check in advisory_checks:
            if enforcement_mode == "DISABLED":
                continue

            match check:
                case "COGNITIVE_DISTRIBUTION":
                    result = _validate_cognitive_distribution(exam_blueprint, master_blueprint)
                    if not result["valid"]:
                        advisory_checks_warnings.extend(result["errors"])

                case "QUESTION_NATURE_BALANCE":
                    result = _validate_question_nature_balance(
                        exam_blueprint, allowed_question_natures
                    )
                    if not result["valid"]:
                        advisory_checks_warnings.extend(result["errors"])

                case "INTERNAL_CHOICE_PRESENCE":
                    result = _validate_internal_choice_presence(exam_blueprint)
                    if not result["valid"]:
                        advisory_checks_warnings.extend(result["errors"])

                case "DIAGRAM_VI_COVERAGE":
                    result = _validate_diagram_vi_coverage(exam_blueprint, master_blueprint)
                    if not result["valid"]:
                        advisory_checks_warnings.extend(result["errors"])

                case _:
                    # Unknown advisory check - skip
                    pass

        validation_details.update(
            {
                "strict_checks_passed": strict_checks_passed,
                "strict_checks_failed": strict_checks_failed,
                "advisory_checks_warnings": advisory_checks_warnings,
            }
        )

    except FileNotFoundError as e:
        errors.append(f"Blueprint file not found: {str(e)}")
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in blueprint: {str(e)}")
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")

    return _create_result(len(errors) == 0, errors, warnings, validation_details)


def _discover_master_blueprint_path(exam_blueprint: Dict[str, Any]) -> str:
    """Discover master blueprint path from exam blueprint metadata."""
    metadata = exam_blueprint.get("metadata", {})
    subject = metadata.get("subject", "Mathematics")
    class_num = metadata.get("class", 10)

    # Normalize subject name for path
    subject_normalized = subject.lower().replace(" ", "_")

    # Construct path: skills/cbse/class_{class}/{subject}/references/blueprint.json
    master_blueprint_path = (
        f"skills/cbse/class_{class_num}/{subject_normalized}/references/blueprint.json"
    )

    return master_blueprint_path


def _handle_validation_result(
    result: Dict[str, Any],
    errors: List[str],
    warnings: List[str],
    failed_checks: List[str],
    enforcement_mode: str,
):
    """Handle validation result based on enforcement mode."""
    match enforcement_mode:
        case "STRICT":
            errors.extend(result["errors"])
            failed_checks.append(result.get("check_name", "Unknown"))
        case "ADVISORY":
            # In advisory mode, strict checks become warnings
            warnings.extend(result["errors"])


def _validate_question_format_whitelist(
    exam_blueprint: Dict[str, Any], allowed_formats: List[str]
) -> Dict[str, Any]:
    """Check all question_formats are in master's whitelist."""
    errors = []

    for section in exam_blueprint.get("sections", []):
        q_format = section.get("question_format")
        if q_format and q_format not in allowed_formats:
            errors.append(
                f"Section {section.get('section_id', 'Unknown')}: "
                f"Invalid format '{q_format}'. Allowed formats: {allowed_formats}"
            )

    return {"valid": len(errors) == 0, "errors": errors, "check_name": "QUESTION_FORMAT_WHITELIST"}


def _validate_internal_choice_arithmetic(
    exam_blueprint: Dict[str, Any], supported_types: List[str]
) -> Dict[str, Any]:
    """Check attempt <= provided for internal_choice."""
    errors = []

    # Normalize supported types to lowercase for case-insensitive comparison
    normalized_supported_types = [t.lower() for t in supported_types]

    for section in exam_blueprint.get("sections", []):
        ic = section.get("internal_choice")
        if ic:
            ic_type = ic.get("type", "")
            if ic_type:
                if ic_type.lower() not in normalized_supported_types:
                    errors.append(
                        f"Section {section.get('section_id', 'Unknown')}: "
                        f"Unsupported internal_choice type '{ic_type}'. "
                        f"Supported: {supported_types}"
                    )

            provided = ic.get("provided")
            actual_attempt = section.get("questions_attempt") or ic.get("attempt") or 0

            if provided and actual_attempt and actual_attempt > provided:
                errors.append(
                    f"Section {section.get('section_id', 'Unknown')}: "
                    f"attempt ({actual_attempt}) > provided ({provided})"
                )

    return {"valid": len(errors) == 0, "errors": errors, "check_name": "INTERNAL_CHOICE_ARITHMETIC"}


def _validate_syllabus_scope_enforcement(
    exam_blueprint: Dict[str, Any], topic_selection_required: bool, all_topics_keyword: str
) -> Dict[str, Any]:
    """Check chapters have topics per syllabus_granularity_policy."""
    errors = []

    syllabus_scope = exam_blueprint.get("syllabus_scope", {})
    chapters = syllabus_scope.get("chapters", [])

    if not chapters:
        errors.append("syllabus_scope.chapters is required but not found.")
        return {"valid": False, "errors": errors, "check_name": "SYLLABUS_SCOPE_ENFORCEMENT"}

    for chapter_data in chapters:
        chapter_name = chapter_data.get("chapter_name", "")
        topics = chapter_data.get("topics", [])

        if topic_selection_required:
            if not topics:
                errors.append(
                    f"Chapter '{chapter_name}': topics required but not found. "
                    f"Set topic_selection_required: false in master blueprint to make topics optional."
                )
            elif topics == [all_topics_keyword]:
                pass  # ALL_TOPICS is explicitly allowed
            elif len(topics) == 0:
                errors.append(f"Chapter '{chapter_name}': Empty topics array.")

    return {"valid": len(errors) == 0, "errors": errors, "check_name": "SYLLABUS_SCOPE_ENFORCEMENT"}


def _validate_topic_scope_enforcement(
    exam_blueprint: Dict[str, Any], all_topics_keyword: str, topic_level_is_primary_constraint: bool
) -> Dict[str, Any]:
    """Check section topic_focus arrays are subsets of syllabus topics."""
    errors = []

    syllabus_scope = exam_blueprint.get("syllabus_scope", {})
    chapters = syllabus_scope.get("chapters", [])

    # Build topic map: topic -> chapter_name
    topic_map = {}
    chapters_with_all_topics = []

    for chapter in chapters:
        chapter_name = chapter.get("chapter_name", "")
        topics = chapter.get("topics", [])

        if topics == [all_topics_keyword]:
            chapters_with_all_topics.append(chapter_name)
        else:
            for topic in topics:
                topic_map[topic] = chapter_name

    # Validate each section's topic_focus
    for section in exam_blueprint.get("sections", []):
        topic_focus = section.get("topic_focus")
        section_id = section.get("section_id", "Unknown")

        # Only validate if topic_focus is present
        if topic_focus is not None:
            if not isinstance(topic_focus, list):
                errors.append(f"Section {section_id}: topic_focus must be an array.")
            else:
                for topic in topic_focus:
                    # Check if topic exists in syllabus
                    if topic not in topic_map:
                        # If no chapter has ALL_TOPICS, it's an error
                        if not chapters_with_all_topics:
                            errors.append(
                                f"Section {section_id}: Invalid topic '{topic}' not in syllabus scope."
                            )

    return {"valid": len(errors) == 0, "errors": errors, "check_name": "TOPIC_SCOPE_ENFORCEMENT"}


def _validate_cognitive_distribution(
    exam_blueprint: Dict[str, Any], master_blueprint: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate cognitive level distribution matches CBSE recommendations (advisory)."""
    errors = []

    # Check if exam blueprint has cognitive level hints
    has_cognitive_hints = any(
        section.get("cognitive_level_hint") for section in exam_blueprint.get("sections", [])
    )

    if not has_cognitive_hints:
        errors.append(
            "No cognitive_level_hint defined in sections. Consider adding cognitive level guidance."
        )

    return {"valid": len(errors) == 0, "errors": errors}


def _validate_question_nature_balance(
    exam_blueprint: Dict[str, Any], allowed_natures: List[str]
) -> Dict[str, Any]:
    """Validate question natures are balanced (advisory)."""
    errors = []

    for section in exam_blueprint.get("sections", []):
        section_id = section.get("section_id", "Unknown")
        section_natures = section.get("allowed_question_natures", [])

        if not section_natures:
            errors.append(
                f"Section {section_id}: No allowed_question_natures defined. "
                f"Consider specifying natures for better question variety."
            )
        else:
            for nature in section_natures:
                if nature not in allowed_natures:
                    errors.append(
                        f"Section {section_id}: Unknown question nature '{nature}'. "
                        f"Known natures: {allowed_natures}"
                    )

    return {"valid": len(errors) == 0, "errors": errors}


def _validate_internal_choice_presence(exam_blueprint: Dict[str, Any]) -> Dict[str, Any]:
    """Check if internal choice is appropriately used (advisory)."""
    errors = []

    for section in exam_blueprint.get("sections", []):
        section_id = section.get("section_id", "Unknown")
        provided = section.get("questions_provided", 0)
        attempt = section.get("questions_attempt", 0)
        ic = section.get("internal_choice")

        if provided > 0 and attempt < provided and not ic:
            errors.append(
                f"Section {section_id}: provided ({provided}) > attempt ({attempt}) but no internal_choice defined. "
                f"Consider adding internal choice for questions."
            )

    return {"valid": len(errors) == 0, "errors": errors}


def _validate_diagram_vi_coverage(
    exam_blueprint: Dict[str, Any], master_blueprint: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate diagrams have VI alternatives (advisory)."""
    errors = []

    # Check if diagram alternative required for VI
    diagram_requirements = master_blueprint.get("diagram_and_data_requirements", {})
    vi_required = diagram_requirements.get("diagram_alternative_required_for_vi", False)

    if vi_required:
        # Check if exam blueprint has any mention of VI alternatives
        has_vi_alternative = False

        # Check if accessibility is mentioned anywhere
        for section in exam_blueprint.get("sections", []):
            if "vi_alternative" in section or "accessibility" in section:
                has_vi_alternative = True
                break

        if not has_vi_alternative:
            errors.append(
                "VI diagram alternatives required by master blueprint but not specified. "
                "Ensure all diagram-based questions have non-diagrammatic alternatives."
            )

    return {"valid": len(errors) == 0, "errors": errors}


def _create_result(
    valid: bool, errors: List[str], warnings: List[str], validation_details: Dict[str, Any]
) -> Dict[str, Any]:
    """Create standardized validation result."""
    return {
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
        "validation_details": validation_details,
    }
