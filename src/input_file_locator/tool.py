"""Blueprint file locator tool.

This tool provides functionality to locate and validate blueprint JSON files
from teacher input or auto-discover from the input/classes/ folder structure.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Any
from langchain_core.tools import tool


@tool
def locate_blueprint_tool(task: str) -> Dict[str, Any]:
    """
    Locates and validates blueprint JSON files from teacher input or auto-discovers
    from the input/classes/{class}/{subject}/ folder structure.

    Supports two blueprint types:
    - Master blueprint: input/classes/{class}/{subject}/blueprint.json
    - Teacher input file: input/classes/{class}/{subject}/input_*.json

    Priority rules:
    1. Teacher files (input_*.json) override master blueprints
    2. Most recent file by modification timestamp is selected

    Args:
        task: Teacher's request string that may contain explicit path to blueprint file.
              Example: "Generate class 10 mathematics paper from input/classes/10/mathematics/first.json"

    Returns:
        {
            "file_path": str,           # Relative path with forward slashes (e.g., "input/classes/10/mathematics/blueprint.json")
            "found": bool,              # True if file located, False otherwise
            "is_teacher_file": bool,    # True if teacher file (input_*.json), False if master blueprint
            "auto_discovered": bool,    # True if discovered automatically, False if explicit path provided
            "class": int or None,       # Class number extracted from path
            "subject": str or None,     # Subject name extracted from path
            "error": str or None        # Error message if file not found
        }
    """
    classes_dir = Path("input/classes")

    # Step 1: Check for explicit path in task
    words = task.split()
    explicit_path = None

    for word in words:
        if word.startswith("input/") and word.endswith(".json"):
            explicit_path = word
            break
        if word.startswith("output/") and word.endswith(".json"):
            explicit_path = word
            break

    # If explicit path found, validate and return
    if explicit_path:
        file_path = Path(explicit_path)
        if file_path.exists():
            # Determine if teacher file or master blueprint
            is_teacher = file_path.name.startswith("input_")

            # Extract class and subject from path
            class_num, subject = _extract_class_subject(file_path)

            return {
                "file_path": str(file_path).replace("\\", "/"),
                "found": True,
                "is_teacher_file": is_teacher,
                "auto_discovered": False,
                "class": class_num,
                "subject": subject,
                "error": None,
            }
        else:
            return {
                "file_path": explicit_path,
                "found": False,
                "is_teacher_file": False,
                "auto_discovered": False,
                "class": None,
                "subject": None,
                "error": f"Explicit path provided but file not found: {explicit_path}",
            }

    # Step 2: Auto-discovery
    if not classes_dir.exists():
        return {
            "file_path": None,
            "found": False,
            "is_teacher_file": False,
            "auto_discovered": False,
            "class": None,
            "subject": None,
            "error": "Input classes directory not found. Expected: input/classes/",
        }

    # Search for all JSON files in the classes directory
    all_json_files = list(classes_dir.rglob("*.json"))

    if not all_json_files:
        return {
            "file_path": None,
            "found": False,
            "is_teacher_file": False,
            "auto_discovered": False,
            "class": None,
            "subject": None,
            "error": "No blueprint file found in input/classes/. Expected structure: input/classes/{class}/{subject}/blueprint.json or input/classes/{class}/{subject}/input_*.json",
        }

    # Priority 1: Look for teacher input files (input_*.json) - these override master blueprints
    teacher_files = [f for f in all_json_files if f.name.startswith("input_")]

    # Priority 2: Look for master blueprint.json files
    master_files = [f for f in all_json_files if f.name == "blueprint.json"]

    # Select the most recent file based on priority
    selected_file = None
    is_teacher = False

    if teacher_files:
        selected_file = max(teacher_files, key=lambda f: f.stat().st_mtime)
        is_teacher = True
    elif master_files:
        selected_file = max(master_files, key=lambda f: f.stat().st_mtime)
        is_teacher = False
    else:
        # Fallback: use any JSON file found
        selected_file = max(all_json_files, key=lambda f: f.stat().st_mtime)
        is_teacher = selected_file.name.startswith("input_")

    # Extract class and subject from path
    class_num, subject = _extract_class_subject(selected_file)

    return {
        "file_path": str(selected_file).replace("\\", "/"),
        "found": True,
        "is_teacher_file": is_teacher,
        "auto_discovered": True,
        "class": class_num,
        "subject": subject,
        "error": None,
    }


def _extract_class_subject(file_path: Path) -> tuple[Optional[int], Optional[str]]:
    """
    Extract class number and subject from the file path.

    Expected path format: input/classes/{class}/{subject}/{filename}.json

    Args:
        file_path: Path object to the blueprint file

    Returns:
        Tuple of (class_number, subject_name) or (None, None) if cannot parse
    """
    try:
        # Convert to relative path from project root
        parts = file_path.parts

        # Find 'classes' in path and extract next two segments
        if "classes" in parts:
            classes_idx = parts.index("classes")
            if len(parts) > classes_idx + 2:
                class_str = parts[classes_idx + 1]
                subject = parts[classes_idx + 2]

                # Try to parse class as integer
                try:
                    class_num = int(class_str)
                    return class_num, subject
                except ValueError:
                    return None, subject

        return None, None
    except Exception:
        return None, None
