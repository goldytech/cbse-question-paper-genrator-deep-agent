# DOCX Generator Skill

## Overview

This skill is responsible for converting CBSE question papers from JSON format to Microsoft Word (DOCX) documents with proper CBSE formatting, embedded diagrams, and professional layout.

## Key Features

### 1. CBSE Format Compliance
- **Header**: CENTRAL BOARD OF SECONDARY EDUCATION, Subject (Class), Exam Type, Time, Max Marks
- **General Instructions**: CBSE-standard instructions for all sections
- **Section Headers**: Format "SECTION X", Title, marks calculation (count × marks = total)
- **Question Formatting**: Sequential numbering (Q1, Q2, Q3...) across all sections

### 2. Internal Choice Questions (OR Format)
- Sections B, C, D: Internal choice in last 2 questions per CBSE standard
- Format: "Q21. [question text] (marks)" followed by centered "OR" and alternative question
- Alternative questions share the same question number

### 3. Case Study Questions (Section E)
- Format: Main passage followed by sub-parts (i), (ii), (iii)
- Default marks distribution: (i) 1 mark, (ii) 1 mark, (iii) 2 marks
- Supports custom sub-questions with marks from JSON

### 4. MCQ Options (Dict Format)
- Accepts new streamlined schema: `{"A": "option text", "B": "option text"}`
- Format: Indented options with "A) text", "B) text", "C) text", "D) text"
- Supports 4 options per CBSE standard

### 5. Diagram Embedding
- Converts SVG diagrams to PNG using cairosvg
- Embeds diagrams in DOCX with figure captions
- Cleanup of temporary PNG files after generation

## File Format

### Input: JSON Question Paper
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
          "internal_choice": false
        }
      ]
    }
  ],
  "total_marks": 80
}
```

### Output: DOCX File
- CBSE-compliant header with exam information
- General instructions section
- Sequential question numbering
- Proper formatting for MCQs, internal choices, case studies
- Embedded diagrams with captions
- Footer with generation timestamp

## Tools

### generate_docx_tool
```python
generate_docx_tool(
    json_paper_path: str,           # Path to JSON question paper
    output_docx_path: Optional[str] = None  # Optional custom output path
) -> Dict[str, Any]
```

**Returns**:
- `success`: bool
- `docx_path`: Path to generated DOCX file
- `questions_count`: Total questions in paper
- `diagrams_embedded`: Number of diagrams converted
- `generation_time`: ISO timestamp
- `error`: Error message if failed

## Usage

### Basic Usage
```python
from docx_generation.tool import generate_docx_tool

result = generate_docx_tool(
    json_paper_path="output/mathematics_class10_first_term_20260115_143052_a7f3d.json"
)

if result["success"]:
    print(f"DOCX generated: {result['docx_path']}")
    print(f"Questions: {result['questions_count']}")
    print(f"Diagrams embedded: {result['diagrams_embedded']}")
```

### Custom Output Path
```python
result = generate_docx_tool(
    json_paper_path="output/paper.json",
    output_docx_path="my_exam_paper.docx"
)
```

## Helper Functions

### _create_cbse_header(doc, metadata)
Creates CBSE-style document header with:
- CBSE board name
- Subject and class
- Exam type
- Time and marks

### _create_cbse_general_instructions(doc, num_sections)
Adds CBSE general instructions with section counts.

### _format_mcq_options(options, doc)
Formats MCQ options in CBSE style with proper indentation.

### _format_internal_choice(question, doc, q_num, q_marks)
Formats internal choice questions with "OR" separator.

### _format_case_study_question(question, doc, q_num, q_marks)
Formats case study questions with sub-parts.

### _svg_base64_to_png(svg_base64, width)
Converts base64 SVG diagrams to PNG for embedding.

### _generate_docx_filename(metadata)
Generates unique DOCX filenames with timestamps.

## CBSE Section Configuration

```python
CBSE_SECTIONS = {
    "A": {"title": "Multiple Choice Questions", "marks_per_question": 1},
    "B": {"title": "Very Short Answer Questions", "marks_per_question": 2},
    "C": {"title": "Short Answer Questions", "marks_per_question": 3},
    "D": {"title": "Long Answer Questions", "marks_per_question": 5},
    "E": {"title": "Case Study Based Questions", "marks_per_question": 4},
}
```

## Dependencies

### Required
- `python-docx`: DOCX document generation
- `cairosvg`: SVG to PNG conversion (optional but recommended)
- `langchain_core`: Tool decorators

### Installation
```bash
pip install python-docx cairosvg
```

## Error Handling

### Missing SVG Support
If cairosvg is not installed:
- Warning is printed
- DOCX is still generated but without diagrams
- Document remains valid and usable

### Invalid JSON
Returns error if input file not found or invalid JSON.

### Missing Required Fields
Gracefully handles missing optional fields with defaults.

## File Locations

### Input
```
input/classes/{class}/{subject}/
├── blueprint.json
└── input_{exam_name}.json
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

## Version History

### v2.0 (Current)
- Added CBSE format compliance
- Support for internal choice questions (OR format)
- Case study sub-parts formatting
- Dict format options (streamlined schema)
- Embedded diagram support
- Sequential question numbering

### v1.0
- Basic DOCX generation
- Simple question formatting
- Array format options

## Best Practices

1. **Verify JSON Structure**: Ensure input JSON follows the expected schema
2. **Check Diagrams**: SVG diagrams should be valid base64-encoded
3. **Metadata Completeness**: Include all required exam metadata fields
4. **Internal Choices**: Mark questions with `internal_choice: true` for OR format
5. **Case Studies**: Use `has_sub_questions: true` and provide `sub_questions` array
6. **Question IDs**: Keep unique question IDs for tracking

## Example Output Structure

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

2. [Next question]...

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

## Troubleshooting

### Diagrams Not Showing
- Ensure cairosvg is installed: `pip install cairosvg`
- Check SVG is valid base64
- Verify PNG conversion works

### Formatting Issues
- Check question_format field is set correctly
- Ensure options are in dict format for MCQs
- Verify marks field is present

### File Not Found
- Verify input JSON path is correct
- Check file permissions
- Ensure parent directories exist
