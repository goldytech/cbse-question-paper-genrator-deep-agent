---
name: docx-generator
description: Converts approved JSON question papers to DOCX format with embedded diagrams. Use ONLY AFTER teacher approves the JSON question paper with "yes".
metadata:
  version: "1.0"
  author: CBSE Question Paper Generator
---

# DOCX Generation Skill

## Overview

This skill converts approved JSON question papers into professionally formatted DOCX documents suitable for printing and distribution to students.

## When to Use

**ONLY use this skill AFTER the teacher has explicitly approved the JSON question paper with "yes".**

Do NOT generate DOCX:
- Before teacher approval
- For preview/staging files
- If the paper has validation errors

## Input Format

You will receive:
- `paper_path`: Path to the approved JSON question paper
- `output_path`: (Optional) Custom output path for DOCX file

## Output Format

Return JSON:
```json
{
  "success": true|false,
  "docx_path": "output/docx/mathematics_class10_first_term_20260206_150301_a7f3d.docx",
  "questions_count": 20,
  "diagrams_embedded": 8,
  "generation_time": "2026-02-06T15:03:01"
}
```

## Process

1. **Validate Input**
   - Check that paper_path exists and is valid JSON
   - Verify paper has been approved (look for approval indicator)

2. **Read JSON Paper**
   - Load the question paper structure
   - Extract metadata (subject, class, exam type, total marks)

3. **Create DOCX Structure**

### Header (Each Page)
```
CBSE | CENTRAL BOARD OF SECONDARY EDUCATION
MATHEMATICS (Class 10)
FIRST TERM
TIME: 2 hours MAX.MARKS: 50
```

### Body Structure

**General Instructions:**
1. This Question Paper consists of 5 Sections A, B, C, D and E.
2. All questions are compulsory.
3. Draw neat and clean figures wherever required.
4. Use of calculators is not allowed.
...

**Section A: Multiple Choice Questions (10 × 1 = 10 marks)**
1. [Question text with MCQ options]
   [Embedded diagram if applicable]

2. [Question text with MCQ options]
   [Embedded diagram if applicable]

**Section B: Short Answer Questions (5 × 3 = 15 marks)**
1. [Question text]
   [Embedded diagram if applicable]
   [Answer space provided]

### Footer (Each Page)
```
CBSE Question Paper Generator | Generated: {timestamp}
```

4. **Embed Diagrams**
   - For each question with `has_diagram: true`:
     - Locate SVG file using `diagram_key`
     - Convert SVG to PNG if needed
     - Embed in document at appropriate position
     - Ensure diagrams are clear and properly sized

5. **Format and Style**
   - Apply CBSE-standard formatting
   - Set proper margins and spacing
   - Use consistent fonts (Times New Roman or Arial)
   - Ensure proper page breaks between sections

6. **Save DOCX File**
   - Generate filename using convention (see below)
   - Save to `output/docx/` directory
   - Verify file was created successfully

## Document Structure Details

### Header Format
- Line 1: "CBSE | CENTRAL BOARD OF SECONDARY EDUCATION" (centered, bold)
- Line 2: "{SUBJECT} (Class {class})" (centered)
- Line 3: "{EXAM_TYPE}" (centered, uppercase)
- Line 4: "TIME: {duration} MAX.MARKS: {total_marks}" (centered)

### Question Formatting

**MCQ Questions:**
- Question number and text
- Options labeled A, B, C, D on separate lines
- Diagram embedded after question text (if applicable)

**Short/Long Answer:**
- Question number and text
- Diagram embedded (if applicable)
- Adequate space for student answer

### Footer Format
- "CBSE Question Paper Generator | Generated: {timestamp}" (centered, small font)
- Page numbers (optional)

## Filename Convention

```
{subject}_class{class}_{exam}_YYYYMMDD_HHMMSS_{id}.docx

Example:
mathematics_class10_first_term_20260206_150301_a7f3d.docx
```

Components:
- `subject`: Subject name from blueprint (lowercase, spaces→underscores)
- `class`: Class number from blueprint (e.g., "class10")
- `exam`: From JSON exam_type
- `YYYYMMDD_HHMMSS`: Timestamp
- `id`: First 5 chars of UUID

Storage location: `output/docx/`

## Error Handling

- **Paper not found**: Return error with file path
- **Invalid JSON**: Return error with parsing details
- **Diagram missing**: Warning, continue without diagram
- **Permission error**: Return error, suggest checking output directory permissions

## Quality Checklist

Before returning success:
- [ ] DOCX file created successfully
- [ ] File is readable (not corrupted)
- [ ] All questions included
- [ ] All diagrams embedded correctly
- [ ] Header and footer present
- [ ] Formatting consistent
- [ ] Filename follows convention

## Best Practices

- Always verify teacher approval before generating
- Use default output path unless specified
- Handle missing diagrams gracefully (continue generation)
- Ensure professional formatting suitable for exams
- Test DOCX opens correctly before marking success
