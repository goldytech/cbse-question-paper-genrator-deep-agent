---
name: docx-generator
description: Converts CBSE question papers from JSON format to DOCX documents with CBSE-compliant formatting, internal choice questions, case study sub-parts, and embedded diagrams. Use this skill AFTER the question paper is approved and ready for document generation.
metadata:
  version: "2.0"
  author: CBSE Question Paper Generator
---

# DOCX Generator Skill

## Overview

This skill converts CBSE question papers from JSON format to Microsoft Word (DOCX) documents with proper CBSE formatting, embedded diagrams, and professional layout. It handles CBSE-compliant headers, internal choice questions (OR format), case study sub-parts, sequential numbering, and diagram embedding.

## When to Use

**Use this skill ONLY AFTER** the teacher has approved the JSON question paper with "yes". This is the final step in the workflow that creates the printable examination document.

## Input Format

### Input Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `json_paper_path` | str | Yes | Path to the approved JSON question paper file | `"output/mathematics_class10_first_term_20260115_143052_a7f3d.json"` |
| `output_docx_path` | str | Optional | Custom output path for DOCX file. Auto-generated if not provided | `"output/docx/my_paper.docx"` |

### Input JSON Structure

```json
{
  "exam_metadata": {
    "subject": "Mathematics",
    "class": 10,
    "exam_type": "First Term Examination",
    "total_marks": 80,
    "duration_minutes": 180
  },
  "sections": [
    {
      "section_id": "A",
      "title": "Multiple Choice Questions",
      "marks_per_question": 1,
      "questions": [
        {
          "question_id": "MATH-10-REA-MCQ-001",
          "question_text": "Find the LCM of 12 and 18",
          "question_format": "MCQ",
          "marks": 1,
          "options": {
            "A": "36",
            "B": "72",
            "C": "6",
            "D": "24"
          },
          "internal_choice": false,
          "has_diagram": false
        }
      ]
    }
  ],
  "total_marks": 80
}
```

## Tools

### Tool 1: generate_docx_tool

**Purpose**: Convert JSON question paper to DOCX format with CBSE-compliant formatting and embedded diagrams.

**Input Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `json_paper_path` | str | Yes | Path to the JSON question paper file |
| `output_docx_path` | Optional[str] | No | Custom output path (auto-generated if omitted) |

**Return Format**:

```json
{
  "success": true,
  "docx_path": "output/docx/mathematics_class10_first_term_20260206_150301_a7f3d.docx",
  "questions_count": 23,
  "diagrams_embedded": 5,
  "generation_time": "2026-02-06T15:03:01",
  "error": null
}
```

**Return Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether DOCX generation succeeded |
| `docx_path` | str | Absolute path to generated DOCX file |
| `questions_count` | int | Total questions in the paper |
| `diagrams_embedded` | int | Number of diagrams successfully embedded |
| `generation_time` | str | ISO timestamp of generation |
| `error` | str/null | Error message if generation failed |

**Error Response**:

```json
{
  "success": false,
  "docx_path": null,
  "questions_count": 0,
  "diagrams_embedded": 0,
  "generation_time": "2026-02-06T15:03:01",
  "error": "JSON file not found: output/paper.json"
}
```

## CBSE Format Features

### Header Format
Creates CBSE-compliant header with:
- CENTRAL BOARD OF SECONDARY EDUCATION
- Subject (Class) - e.g., "MATHEMATICS (Class 10)"
- Exam Type - e.g., "FIRST TERM EXAMINATION"
- Time and Max Marks - e.g., "TIME: 3 HOURS    MAX. MARKS: 80"

### General Instructions
Standard CBSE instructions including:
- Section counts and question types
- Marks per section
- Internal choice information
- Calculator and figure guidelines

### Section Headers
Format: **SECTION X** (centered, bold)
Subtitle: Section title (italic)
Marks: (count × marks = total marks)

### Question Formatting

**Sequential Numbering**: Questions numbered Q1, Q2, Q3... across all sections continuously

**MCQ Format**:
```
1. Question text (1 mark)
   A) option text
   B) option text
   C) option text
   D) option text
```

**Internal Choice (OR Format)**: For Sections B, C, D (last 2 questions)
```
21. Question text (2 marks)
    OR
    Alternative question text (2 marks)
```

**Case Study (Section E)**: With sub-parts (i), (ii), (iii)
```
36. Case study passage text...
    (i) (1 mark)
    (ii) (1 mark)
    (iii) (2 marks)
```

### CBSE Section Configuration

| Section | Title | Marks/Question |
|---------|-------|----------------|
| A | Multiple Choice Questions | 1 |
| B | Very Short Answer Questions | 2 |
| C | Short Answer Questions | 3 |
| D | Long Answer Questions | 5 |
| E | Case Study Based Questions | 4 |

## Helper Functions

### _create_cbse_header(doc, metadata)
Creates CBSE-style document header.

### _create_cbse_general_instructions(doc, num_sections)
Adds CBSE general instructions.

### _format_mcq_options(options, doc)
Formats MCQ options in CBSE style with indentation.

### _format_internal_choice(question, doc, q_num, q_marks)
Formats internal choice questions with "OR" separator.

### _format_case_study_question(question, doc, q_num, q_marks)
Formats case study questions with sub-parts.

### _svg_base64_to_png(svg_base64, width)
Converts base64 SVG diagrams to PNG for embedding.

## Examples

### Example 1: Basic Usage
```python
result = task(
    name="docx-generator",
    task="Generate DOCX from: output/mathematics_class10_first_term_20260206_143052_a7f3d.json"
)
```

**Response**:
```json
{
  "success": true,
  "docx_path": "output/docx/mathematics_class10_first_term_20260206_150301_a7f3d.docx",
  "questions_count": 23,
  "diagrams_embedded": 5,
  "generation_time": "2026-02-06T15:03:01"
}
```

### Example 2: With Custom Output Path
```python
result = task(
    name="docx-generator",
    task="Generate DOCX from: output/paper.json to: output/docx/my_exam.docx"
)
```

### Example 3: Error Handling
```python
result = task(
    name="docx-generator",
    task="Generate DOCX from: output/nonexistent.json"
)
```

**Response**:
```json
{
  "success": false,
  "error": "JSON file not found: output/nonexistent.json",
  "questions_count": 0,
  "diagrams_embedded": 0,
  "generation_time": "2026-02-06T15:03:01"
}
```

## Error Handling

### Missing JSON File
Returns error if input file not found:
```json
{
  "success": false,
  "error": "JSON file not found: {path}"
}
```

### Invalid JSON
Returns error with parsing details if JSON is malformed.

### Missing cairosvg
If cairosvg not installed:
- Warning printed
- DOCX still generated without diagrams
- Document remains valid and usable

### Missing Required Fields
Gracefully handles missing optional fields with defaults:
- Missing metadata → Uses empty dict defaults
- Missing marks → Uses section default
- Missing options → Skips MCQ formatting

## File Locations

### Input
```
output/
└── {subject}_class{class}_{exam_type}_YYYYMMDD_HHMMSS_{short_id}.json
```

### Output
```
src/output/docx/
└── {subject}_class{class}_{exam_type}_YYYYMMDD_HHMMSS_{short_id}.docx
```

### Cache (Temporary)
```
src/cache/temp/
└── [temporary PNG files for diagrams]
```

## Dependencies

### Required
- `python-docx`: DOCX document generation
- `langchain_core`: Tool decorators

### Optional
- `cairosvg`: SVG to PNG conversion (recommended for diagrams)

### Installation
```bash
pip install python-docx cairosvg
```

## Implementation Status

✅ **Fully Implemented**

- CBSE-compliant header with exam metadata
- General instructions section
- Sequential question numbering across all sections
- MCQ formatting with dict format options
- Internal choice questions (OR format) for Sections B, C, D
- Case study sub-parts (i), (ii), (iii) for Section E
- Diagram embedding with SVG to PNG conversion
- Automatic filename generation with timestamps
- Error handling and validation

## Best Practices

1. **Teacher Approval**: Only generate DOCX after teacher approves JSON with "yes"
2. **Verify JSON**: Ensure input JSON follows the expected schema
3. **Check Diagrams**: SVG diagrams should be valid base64-encoded
4. **Metadata Completeness**: Include all required exam metadata fields
5. **Internal Choices**: Mark questions with `internal_choice: true` for OR format
6. **Case Studies**: Use `has_sub_questions: true` and provide `sub_questions` array
7. **Question IDs**: Keep unique question IDs for tracking and debugging
8. **File Paths**: Use absolute paths for reliability

## Output Example

Generated DOCX structure:
```
CENTRAL BOARD OF SECONDARY EDUCATION
MATHEMATICS (Class 10)
FIRST TERM EXAMINATION
TIME: 3 HOURS          MAX. MARKS: 80

General Instructions:
1. This Question Paper consists of 5 Sections A, B, C, D and E.
2. Section A has 20 MCQs carrying 1 mark each.
...

SECTION A
Multiple Choice Questions
(20 × 1 = 20 marks)

1. Find the LCM of 12 and 18 (1 mark)
   A) 36
   B) 72
   C) 6
   D) 24

SECTION B
Very Short Answer Questions
(5 × 2 = 10 marks)

21. Question text here (2 marks)
    OR
    Alternative question here (2 marks)

SECTION E
Case Study Based Questions
(3 × 4 = 12 marks)

36. Case study passage text...
    (i) (1 mark)
    (ii) (1 mark)
    (iii) (2 marks)
```
