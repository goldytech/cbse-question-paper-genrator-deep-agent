---
name: paper-validator
description: Validates generated question papers against original blueprints to ensure all requirements are met. Use this skill AFTER all questions are generated.
metadata:
  version: "1.0"
  author: CBSE Question Paper Generator
---

# Paper Validation Skill

## Overview

This skill validates generated question papers against the original exam blueprints to ensure all requirements are met before presenting to the teacher.

## When to Use

**Use this skill AFTER** all questions are generated and compiled into the paper. This is the final validation step before human review.

## Input Format

You will receive:
- `paper_path`: Path to the generated question paper JSON
- `blueprint_path`: Path to the original exam blueprint JSON

## Validation Checks

### 1. Total Marks Verification
- Verify paper total marks equals blueprint total marks
- Check: `paper.total_marks == blueprint.exam_metadata.total_marks`
- Error if mismatch

### 2. Section Question Counts
- For each section in paper, verify question count matches blueprint
- Check: `len(section.questions) == blueprint_section.questions_provided`
- Error if any section has wrong count

### 3. Chapter Coverage
- Verify all questions are from blueprint-specified chapters
- Check each question's chapter is in `blueprint.syllabus_scope.chapters`
- Error if question references chapter not in blueprint

### 4. Internal Choice Compliance
- For sections with internal_choice type "any_n_out_of_m"
- Verify provided question count matches blueprint
- Check: `len(questions) == blueprint.internal_choice.provided`
- Error if mismatch

### 5. Required Fields Check
Ensure all questions have required fields:
- question_id
- question_text
- chapter
- topic
- question_format
- marks
- difficulty

Warning if any field is missing.

### 6. Duplicate Detection
- Check for duplicate question texts
- Warning if potential duplicates found

## Output Format

Return JSON:
```json
{
  "valid": true|false,
  "issues": ["Issue 1", "Issue 2"],
  "warnings": ["Warning 1"]
}
```

## Process

1. **Load Files**
   - Read generated paper JSON
   - Read original blueprint JSON

2. **Check Total Marks**
   - Compare paper total with blueprint total
   - Add error if mismatch

3. **Validate Sections**
   - Create mapping of blueprint sections by ID
   - For each paper section:
     - Find matching blueprint section
     - Compare question counts
     - Check internal choice rules
     - Validate all questions have required fields

4. **Check Chapter Coverage**
   - Extract valid chapters from blueprint
   - For each question in paper:
     - Verify chapter is in valid list
     - Add error if invalid chapter found

5. **Detect Duplicates**
   - Collect all question texts
   - Check for duplicates
   - Add warning if found

6. **Determine Validity**
   - If any errors in issues → valid: false
   - If no errors → valid: true
   - Include all warnings

## Examples

### Valid Paper
```json
{
  "valid": true,
  "issues": [],
  "warnings": []
}
```

### Invalid Paper
```json
{
  "valid": false,
  "issues": [
    "Total marks mismatch: expected 50, actual 45",
    "Section A: expected 10 questions, got 9",
    "Question MATH-10-REA-MCQ-011: chapter 'Algebra' not in blueprint"
  ],
  "warnings": [
    "Question MATH-10-REA-MCQ-003: missing bloom_level field"
  ]
}
```

## Error Handling

- **File not found**: Return error indicating which file is missing
- **Invalid JSON**: Return error with parsing details
- **Missing sections**: Error if paper section not in blueprint
- **Empty paper**: Error if paper has no questions

## Best Practices

- Always validate before presenting to teacher
- Fix all errors before considering paper complete
- Review warnings - some may need attention
- If invalid, identify which questions need regeneration
- Re-validate after making fixes
- Log validation results for tracking

## Integration with Workflow

This validation is the **final gate** before human review:

1. Generate all questions → Compile paper
2. **Run paper-validator** ← This skill
3. If valid → Save to output/ and present to teacher
4. If invalid → Fix issues, regenerate questions, re-validate

## Common Issues and Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Total marks mismatch | Missing questions or wrong marks | Add questions or adjust marks |
| Section count wrong | Wrong number of questions generated | Regenerate section with correct count |
| Invalid chapter | Question from non-blueprint chapter | Replace with question from valid chapter |
| Missing fields | Incomplete question generation | Regenerate question with all fields |
| Duplicates | Same question generated twice | Regenerate one of the duplicates |
