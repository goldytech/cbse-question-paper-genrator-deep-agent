---
name: blueprint-validator
description: Validates exam blueprints against master policy blueprints to ensure compliance with CBSE standards. Use this skill before generating any questions.
metadata:
  version: "1.0"
  author: CBSE Question Paper Generator
---

# Blueprint Validation Skill

## Overview

This skill validates teacher-provided exam blueprints against master policy blueprints to ensure they comply with CBSE standards and examination policies.

## When to Use

**ALWAYS use this skill FIRST** before generating any question paper. Validation must pass before proceeding with question generation.

## Input Format

You will receive:
- `exam_blueprint_path`: Path to the exam blueprint JSON file (teacher-provided)
- `master_blueprint_path`: (Optional) Path to master policy blueprint. If not provided, auto-discovered from exam blueprint metadata.

## Two-Blueprint Validation System

### Exam Blueprint
Contains teacher specifications:
- Metadata (class, subject, assessment type, total marks)
- Syllabus scope (chapters and topics)
- Sections (question formats, marks, counts)
- Validation policies

### Master Policy Blueprint
Contains CBSE validation rules:
- Allowed question formats
- Question natures
- Internal choice rules
- Cognitive level requirements
- Schema version

## Validation Checks

### Strict Checks (Always Enforced)
1. **Schema Version Compatibility**: Exam blueprint version must match master
2. **Question Format Whitelist**: All formats must be in allowed list
3. **Internal Choice Arithmetic**: attempt ≤ provided for all sections
4. **Syllabus Scope Enforcement**: All chapters must have topics specified
5. **Topic Scope Enforcement**: topic_focus arrays must be valid subsets

### Advisory Checks (Warnings Only)
1. **Cognitive Distribution**: Should match recommended distribution
2. **Question Nature Balance**: Variety of question natures recommended
3. **Internal Choice Presence**: Recommended when provided > attempt
4. **Diagram VI Coverage**: Visual impairment alternatives required

## Enforcement Modes

- **STRICT**: All strict checks must pass, fail on any violation
- **ADVISORY**: Strict checks generate warnings instead of errors
- **DISABLED**: Minimal validation only

## Output Format

Return JSON:
```json
{
  "valid": true|false,
  "errors": ["Error message 1", "Error message 2"],
  "warnings": ["Warning message 1"],
  "validation_details": {
    "schema_version": "detected_from_master",
    "enforcement_mode": "STRICT",
    "strict_checks_passed": ["CHECK_NAME"],
    "strict_checks_failed": [],
    "advisory_checks_warnings": []
  }
}
```

## Process

1. **Load Exam Blueprint**
   - Read JSON from provided path
   - Extract metadata (class, subject, etc.)

2. **Discover Master Blueprint** (if not provided)
   - Construct path: `skills/cbse/class_{class}/{subject}/references/blueprint.json`
   - Load master blueprint

3. **Compare Schema Versions**
   - Get version from exam blueprint
   - Get version from master blueprint
   - If mismatch → Add error

4. **Run Strict Checks**
   - QUESTION_FORMAT_WHITELIST
   - INTERNAL_CHOICE_ARITHMETIC
   - SYLLABUS_SCOPE_ENFORCEMENT
   - TOPIC_SCOPE_ENFORCEMENT

5. **Run Advisory Checks** (if enforcement_mode != DISABLED)
   - COGNITIVE_DISTRIBUTION
   - QUESTION_NATURE_BALANCE
   - INTERNAL_CHOICE_PRESENCE
   - DIAGRAM_VI_COVERAGE

6. **Determine Validity**
   - If any strict check failed → valid: false
   - If all strict checks passed → valid: true
   - Include all errors and warnings

## Examples

### Valid Blueprint
```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "validation_details": {
    "schema_version": "1.1",
    "enforcement_mode": "STRICT",
    "strict_checks_passed": [
      "QUESTION_FORMAT_WHITELIST",
      "INTERNAL_CHOICE_ARITHMETIC",
      "SYLLABUS_SCOPE_ENFORCEMENT",
      "TOPIC_SCOPE_ENFORCEMENT"
    ],
    "strict_checks_failed": [],
    "advisory_checks_warnings": []
  }
}
```

### Invalid Blueprint
```json
{
  "valid": false,
  "errors": [
    "Schema version mismatch: exam blueprint has '1.0', but master blueprint requires '1.1'",
    "Section A: Invalid format 'ESSAY'. Allowed formats: [MCQ, SHORT, LONG]"
  ],
  "warnings": [
    "No cognitive_level_hint defined in sections. Consider adding cognitive level guidance."
  ],
  "validation_details": {
    "schema_version": "1.0",
    "enforcement_mode": "STRICT",
    "strict_checks_passed": ["INTERNAL_CHOICE_ARITHMETIC"],
    "strict_checks_failed": ["QUESTION_FORMAT_WHITELIST", "SYLLABUS_SCOPE_ENFORCEMENT"],
    "advisory_checks_warnings": ["COGNITIVE_DISTRIBUTION"]
  }
}
```

## Error Handling

- **File isn’t found**: Return error with a specific path
- **Invalid JSON**: Return error with parsing details
- **Missing required fields**: List all missing fields
- **Schema mismatch**: Show expected vs actual versions

## Best Practices

- Trust the validation result - don't override strict failures
- Report all errors clearly to the teacher
- Include specific fix suggestions in error messages
- Always validate before generating questions
- Log validation results for debugging
