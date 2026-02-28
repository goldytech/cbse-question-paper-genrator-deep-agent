---
name: question-assembler
description: Assembles CBSE-compliant questions from retrieved textbook chunks and LLM-generated content. Supports both single question assembly and section compilation with CBSE format.
metadata:
  version: "2.0"
  author: CBSE Question Paper Generator
---

# Question Assembler Skill

## Overview

This skill assembles CBSE-compliant questions from retrieved textbook chunks and LLM-generated content. It supports both:
1. **Single Question Assembly**: Individual question creation with diagram detection
2. **Section Compilation**: Organizing multiple questions into CBSE-formatted sections

**Version 2.0 Changes:**
- ✅ Streamlined schema (removed hints, prerequisites, common_mistakes, quality_score)
- ✅ Options format conversion (array → dict)
- ✅ Sequential numbering across sections
- ✅ CBSE internal choice rules
- ✅ Section compilation mode

## When to Use

**ALWAYS use this skill after cbse-question-retriever generates questions.**

This skill:
- Formats questions into CBSE-compliant structure
- Detects and generates diagrams when needed
- Converts options to proper format
- Applies CBSE internal choice rules
- Compiles sections with proper metadata

## Input Format

You will receive:
- `retrieval_result`: Result from chunk retrieval (chapter, topic, format, marks, etc.)
- `llm_result`: Generated question content from LLM
- `question_number`: Sequential number (1, 2, 3...)
- `section_config`: (Optional) For section compilation mode

## Output Format

### Single Question Mode (Streamlined Schema):
```json
{
  "question_id": "MATH-10-POL-MCQ-001",
  "question_text": "Find the zero of p(x) = x - 3",
  "section_id": "A",
  "question_number": 1,
  "chapter": "Polynomials",
  "topic": "Zeros of a Polynomial",
  "question_format": "MCQ",
  "marks": 1,
  "options": {
    "A": "3",
    "B": "-3", 
    "C": "0",
    "D": "1"
  },
  "correct_answer": "A",
  "difficulty": "easy",
  "bloom_level": "remember",
  "nature": "numerical",
  "has_diagram": false,
  "diagram_needed": false,
  "diagram_description": null,
  "diagram_type": null,
  "diagram_svg_base64": null,
  "diagram_elements": null,
  "explanation": "To find the zero, set p(x) = 0...",
  "internal_choice": false,
  "choice_text": null,
  "has_sub_questions": false,
  "sub_questions": [],
  "generation_metadata": {...},
  "status": "success",
  "error": null,
  "error_phase": null
}
```

### Section Compilation Mode:
```json
{
  "section_id": "B",
  "title": "Short Answer Questions",
  "question_format": "SHORT",
  "marks_per_question": 2,
  "questions_provided": 5,
  "questions_attempt": 5,
  "section_total_marks": 10,
  "questions": [...],
  "internal_choice_available": true,
  "cbse_format": true
}
```

## Key Features

### 1. Options Format Conversion
**Input**: Can be either:
- Array format: `["A) option1", "B) option2", "C) option3", "D) option4"]`
- Dict format: `{"A": "option1", "B": "option2", ...}`

**Output**: Always dict format for CBSE compliance and docx-generator compatibility

### 2. Streamlined Schema (v2.0)

**Removed Fields** (no longer in output):
- ❌ `hints`
- ❌ `prerequisites`
- ❌ `common_mistakes`
- ❌ `quality_score`

**Kept Fields**:
- ✅ `question_text`
- ✅ `options` (dict format)
- ✅ `correct_answer`
- ✅ `explanation`
- ✅ `diagram_needed`
- ✅ `diagram_description`
- ✅ `has_diagram`
- ✅ `diagram_svg_base64`

**New Fields**:
- ✅ `internal_choice`: Boolean flag
- ✅ `choice_text`: "OR" or description
- ✅ `has_sub_questions`: For case studies
- ✅ `sub_questions`: Array of sub-parts

### 3. Diagram Detection & Generation
Automatically detects if question needs diagram based on:
- Geometric keywords (triangle, circle, angle, etc.)
- Coordinate geometry terms (graph, plot, axis, etc.)
- Chart terms (histogram, bar chart, pie chart, etc.)

Generates SVG diagrams and converts to base64 for embedding.

### 4. CBSE Internal Choice Rules
Applied automatically during section compilation:

| Section | Internal Choice |
|---------|----------------|
| A | None (all compulsory) |
| B | Last 2 questions (OR) |
| C | Last 2 questions (OR) |
| D | Last 2 questions (OR) |
| E | All questions (Case Study with sub-parts) |

### 5. Sequential Numbering
Questions are numbered Q1, Q2, Q3... across all sections automatically.

## Tools

### assemble_question_tool
Assembles individual questions with streamlined schema.

**Parameters**:
- `retrieval_result`: Chunk retrieval result
- `llm_result`: LLM generation result
- `question_number`: Sequential number
- `section_config`: (Optional) Section compilation config

**Returns**: Assembled question object

### compile_section_tool
Compiles multiple questions into CBSE section format.

**Parameters**:
- `questions`: List of assembled questions
- `section_id`: "A", "B", "C", "D", or "E"
- `section_title`: Section title
- `marks_per_question`: Marks per question
- `question_format`: Question format type

**Returns**: CBSE-formatted section object

### Helper Functions

**reset_question_counter()**: Reset counter before new paper generation

**get_next_question_number()**: Get next sequential question number

## Process

### For Single Question:
1. **Validate Inputs**: Check retrieval and LLM results
2. **Generate ID**: Format `SUBJECT-CLASS-CHAPTER-FORMAT-NUM`
3. **Convert Options**: Array → Dict format
4. **Detect Diagram**: Rule-based + LLM input
5. **Generate Diagram**: If needed, create SVG
6. **Build Question**: Assemble streamlined schema fields
7. **Return**: Complete question object

### For Section Compilation:
1. **Assemble All Questions**: Call for each question in section
2. **Collect Questions**: Build list of assembled questions
3. **Apply CBSE Rules**: Add internal_choice flags per section rules
4. **Calculate Marks**: section_total_marks = count × marks_per_question
5. **Return**: Section object with metadata

## CBSE Format Compliance

### Section Structure:
- **Section A**: MCQs + Assertion Reason (1 mark each)
- **Section B**: Very Short Answer (2 marks each)
- **Section C**: Short Answer (3 marks each)
- **Section D**: Long Answer (5 marks each)
- **Section E**: Case Study-Based (4 marks with sub-parts)

### Question ID Format:
Pattern: `{SUBJECT}-{CLASS}-{CHAPTER}-{FORMAT}-{NUMBER}`

Examples:
- `MATH-10-POL-MCQ-001`: Math Class 10, Polynomials, MCQ
- `MATH-10-TRI-LA-005`: Math Class 10, Triangles, Long Answer

### Internal Choice Format:
```json
{
  "internal_choice": true,
  "choice_text": "OR",
  "choice_type": "alternative_question"
}
```

### Case Study Format (Section E):
```json
{
  "has_sub_questions": true,
  "sub_questions": [
    {"part": "(i)", "marks": 1},
    {"part": "(ii)", "marks": 1},
    {"part": "(iii)", "marks": 2}
  ],
  "internal_choice": true,
  "choice_text": "Case Study based question"
}
```

## Example Workflows

### Workflow 1: Single Question Assembly
```python
result = assemble_question_tool(
    retrieval_result={
        "chapter": "Polynomials",
        "topic": "Zeros",
        "question_format": "MCQ",
        "marks": 1,
        "difficulty": "easy"
    },
    llm_result={
        "question_text": "Find the zero of p(x) = x - 3",
        "options": ["A) 3", "B) -3", "C) 0", "D) 1"],  # Array input OK
        "correct_answer": "A",
        "explanation": "Set p(x) = 0...",
        "diagram_needed": false
    },
    question_number=1
)
# Returns: Question with options in dict format {"A": "3", "B": "-3", ...}
```

### Workflow 2: Section Compilation
```python
# First: Reset counter for new paper
reset_question_counter()

# Collect questions for Section B
questions = []
for i in range(5):
    q = assemble_question_tool(retrieval, llm_result, get_next_question_number())
    questions.append(q)

# Compile into section
section_b = compile_section_tool(
    questions=questions,
    section_id="B",
    section_title="Short Answer Questions",
    marks_per_question=2,
    question_format="SHORT"
)
# Returns: Section with questions[3] and [4] having internal_choice=true
```

## Error Handling

Returns error object with:
- `status`: "failed"
- `error`: Error message
- `error_phase`: "retrieval" | "llm" | "diagram" | "assembly"
- `generation_metadata.error`: true

Error response uses streamlined schema with empty/default values.

## Best Practices

1. **Always reset counter** before new paper: `reset_question_counter()`
2. **Use dict options format** for consistency
3. **Check diagram detection** results in metadata
4. **Verify internal_choice** flags in sections B, C, D, E
5. **Validate section totals** match blueprint marks
6. **Use sequential numbering** across all sections

## Quality Checklist

Before returning:
- [ ] Options converted to dict format
- [ ] Question number is sequential (Q1, Q2, Q3...)
- [ ] ID format is correct
- [ ] Diagram generated (if needed)
- [ ] Explanation provided
- [ ] CBSE internal choice rules applied (for sections)
- [ ] Section totals calculated correctly
- [ ] Streamlined schema (no hints/prerequisites/common_mistakes/quality_score)
