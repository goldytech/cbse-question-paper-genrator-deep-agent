---
name: input-file-locator
description: Locates and validates blueprint JSON files from teacher input or auto-discovers from input/classes/{class}/{subject}/ folder structure. Handles explicit path extraction and automatic file discovery with priority-based selection.
metadata:
  version: "1.0.0"
  author: CBSE Question Paper Generator
  subagent: input-file-locator
---

# Input File Locator Skill

## Overview

This skill provides the capability to locate and validate blueprint JSON files for the CBSE question paper generation workflow. It handles two scenarios:
1. **Explicit Path**: Extracts blueprint file path directly from teacher's request
2. **Auto-Discovery**: Searches the `input/classes/` folder structure when no explicit path is provided

The subagent uses the `locate_blueprint_tool` to perform the actual file system operations.

## When to Use

**ALWAYS** as the first step in the question paper generation workflow.

Use this subagent when:
- Teacher provides an explicit blueprint file path in their request
- Teacher asks to generate a paper without specifying a blueprint file
- You need to validate the existence and accessibility of a blueprint file
- You need to determine if the file is a teacher override or master blueprint

## Input Format

You will receive a task string from the main agent (orchestrator) that contains the teacher's request. This may or may not include an explicit file path.

**Example inputs:**
```
"Generate class 10 mathematics paper from input/classes/10/mathematics/first.json"
"Generate a CBSE Class 10 Mathematics question paper for the First Term exam"
"Create question paper using input/classes/9/science/blueprint.json"
```

## Tool Usage

You must use the `locate_blueprint_tool` to locate the blueprint file.

**Tool:**
```python
locate_blueprint_tool(task: str) -> Dict[str, Any]
```

**Parameters:**
- `task` (str): The complete teacher request string

**How to invoke:**
```python
result = locate_blueprint_tool(task="Generate class 10 mathematics paper from input/classes/10/mathematics/first.json")
```

## Blueprint Discovery Algorithm

The tool performs the following steps in order:

### Step 1: Explicit Path Extraction
1. Parse the task string for any path starting with `input/` and ending with `.json`
2. If found, validate that the file exists
3. If valid, extract class and subject from the path
4. Return file information with `auto_discovered: false`

### Step 2: Auto-Discovery (if no explicit path)
1. Scan the `input/classes/` directory recursively for all `.json` files
2. **Categorize files:**
   - **Teacher files**: Names matching `input_*.json`
   - **Master blueprints**: Named exactly `blueprint.json`
3. **Apply Priority Rules:**
   - Priority 1: Teacher files (override master blueprints)
   - Priority 2: Master blueprints
   - Priority 3: Any other `.json` file (fallback)
4. **Select file**: Within each priority, select the most recent file by modification timestamp
5. Extract class and subject from the path structure
6. Return file information with `auto_discovered: true`

### Step 3: Error Handling
If no files are found after both steps, return an error with descriptive message.

## Priority Rules

The system follows these priority rules for file selection:

| File Type | Pattern | Priority | Purpose |
|-----------|---------|----------|---------|
| Teacher Input | `input_*.json` | **HIGH** | Teacher-defined exam specifications that override system defaults |
| Master Blueprint | `blueprint.json` | **LOW** | System default specifications |

**Key Points:**
- Teacher files always override master blueprints
- When multiple files of same priority exist, the most recently modified file is selected
- The `input_` prefix is reserved for teacher override files

## Path Structure

All blueprint files follow this folder structure:

```
input/classes/
├── {class}/
│   └── {subject}/
│       ├── blueprint.json              # Master blueprint
│       └── input_*.json               # Teacher override files
```

**Examples:**
- `input/classes/10/mathematics/blueprint.json`
- `input/classes/10/mathematics/input_first_term.json`
- `input/classes/9/science/blueprint.json`

## Return Format

The tool returns a JSON object with the following structure:

### Success Response
```json
{
  "file_path": "input/classes/10/mathematics/first.json",
  "found": true,
  "is_teacher_file": true,
  "auto_discovered": false,
  "class": 10,
  "subject": "mathematics",
  "error": null
}
```

### Error Response
```json
{
  "file_path": null,
  "found": false,
  "is_teacher_file": false,
  "auto_discovered": false,
  "class": null,
  "subject": null,
  "error": "No blueprint file found. Expected structure: input/classes/{class}/{subject}/blueprint.json or input/classes/{class}/{subject}/input_*.json"
}
```

**Field Descriptions:**
- `file_path`: Relative path to the blueprint file (forward slashes)
- `found`: Boolean indicating if file was successfully located
- `is_teacher_file`: True if file is a teacher override (input_*.json), False if master blueprint
- `auto_discovered`: True if found via auto-discovery, False if explicit path was provided
- `class`: Class number extracted from path (e.g., 10, 9, 12)
- `subject`: Subject name extracted from path (e.g., "mathematics", "science")
- `error`: Error message if file not found, null otherwise

## Error Handling

### When File Not Found
If no blueprint file is found:
1. Return the error response format shown above
2. Provide a descriptive error message explaining the expected folder structure
3. **Do NOT raise exceptions** - let the main agent decide how to handle the error
4. The main agent (orchestrator) will decide whether to terminate or retry

### When Explicit Path Invalid
If teacher provides an explicit path that doesn't exist:
1. Return error response with the invalid path in `file_path`
2. Error message should indicate the file was not found at the specified location
3. Main agent can report this to teacher

## Examples

### Example 1: Explicit Path Provided
**Input:**
```
"Generate class 10 mathematics paper from input/classes/10/mathematics/first.json"
```

**Action:**
```python
result = locate_blueprint_tool(task="Generate class 10 mathematics paper from input/classes/10/mathematics/first.json")
```

**Expected Output:**
```json
{
  "file_path": "input/classes/10/mathematics/first.json",
  "found": true,
  "is_teacher_file": true,
  "auto_discovered": false,
  "class": 10,
  "subject": "mathematics",
  "error": null
}
```

### Example 2: Auto-Discovery with Teacher File
**Input:**
```
"Generate a CBSE Class 10 Mathematics question paper"
```

**Action:**
```python
result = locate_blueprint_tool(task="Generate a CBSE Class 10 Mathematics question paper")
```

**Scenario:** Folder contains `input/classes/10/mathematics/input_first_term.json`

**Expected Output:**
```json
{
  "file_path": "input/classes/10/mathematics/input_first_term.json",
  "found": true,
  "is_teacher_file": true,
  "auto_discovered": true,
  "class": 10,
  "subject": "mathematics",
  "error": null
}
```

### Example 3: Auto-Discovery with Master Blueprint
**Input:**
```
"Generate a CBSE Class 9 Science question paper"
```

**Action:**
```python
result = locate_blueprint_tool(task="Generate a CBSE Class 9 Science question paper")
```

**Scenario:** Folder contains only `input/classes/9/science/blueprint.json`

**Expected Output:**
```json
{
  "file_path": "input/classes/9/science/blueprint.json",
  "found": true,
  "is_teacher_file": false,
  "auto_discovered": true,
  "class": 9,
  "subject": "science",
  "error": null
}
```

### Example 4: File Not Found
**Input:**
```
"Generate class 11 chemistry paper"
```

**Action:**
```python
result = locate_blueprint_tool(task="Generate class 11 chemistry paper")
```

**Scenario:** No files exist in `input/classes/11/chemistry/`

**Expected Output:**
```json
{
  "file_path": null,
  "found": false,
  "is_teacher_file": false,
  "auto_discovered": false,
  "class": null,
  "subject": null,
  "error": "No blueprint file found in input/classes/. Expected structure: input/classes/{class}/{subject}/blueprint.json or input/classes/{class}/{subject}/input_*.json"
}
```

**Action by Main Agent:** Report error to teacher and terminate workflow.

## Important Notes

1. **Always use the tool**: Do NOT attempt to perform file operations directly. Always delegate to `locate_blueprint_tool`.

2. **Return complete information**: Always return the full response including `class` and `subject` when found. The main agent uses this information for subsequent steps.

3. **Path format**: The `file_path` always uses forward slashes (`/`) regardless of operating system.

4. **No hardcoding**: Never hardcode class numbers or subject names. Always extract them from the actual file path.

5. **Error messages**: Provide clear, actionable error messages that explain the expected folder structure.

6. **Workflow position**: This is ALWAYS the first step. The main agent cannot proceed without a valid blueprint file.

## Integration with Workflow

After locating the blueprint file, return the result to the main agent (orchestrator). The main agent will:

1. Check `result["found"]` - if False, report error and terminate
2. Check `result["valid"]` - if True, proceed to blueprint validation step
3. Pass `result["file_path"]` to the `blueprint-validator` subagent
4. Use `result["class"]` and `result["subject"]` for subsequent operations

**Next Step in Workflow:** Delegate to `blueprint-validator` subagent with the located file path.
