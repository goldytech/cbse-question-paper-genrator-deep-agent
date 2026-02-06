# Blueprint Structure Reference

## Overview
This document defines the structure of `output/blueprint.json` and how to interpret it during question paper generation.

## Blueprint Structure

### Top-Level Elements

```json
{
  "schema_version": "1.0",
  "exam_metadata": {
    "board": "CBSE",
    "class": 10,
    "subject": "Mathematics",
    "exam_type": "First Term",
    "total_marks": 80,
    "duration_minutes": 180,
    "academic_year": "2025-26"
  },
  "syllabus_scope": {
    "chapters_included": [...],
    "topics": {
      "Chapter Name": ["Topic 1", "Topic 2", ...]
    }
  },
  "sections": [...]
}
```

### Exam Metadata
- **board**: Education board (e.g., "CBSE", "ICSE")
- **class**: Class level (1-12)
- **subject**: Subject name (e.g., "Mathematics", "Science")
- **exam_type**: Exam type (e.g., "First Term", "Final", "Pre-Board")
- **total_marks**: Total marks for paper (e.g., 80, 100)
- **duration_minutes**: Exam duration (e.g., 180)
- **academic_year**: Academic year (e.g., "2025-26")

### Syllabus Scope
- **chapters_included**: List of chapters to include
- **topics**: Chapter to topics mapping (optional, for topic-specific questions). If topics not specified, skill should use all topics from the chapter.

### Sections Array

Each section defines:
- **section_id**: Section identifier (A, B, C, D, E)
- **title**: Section title (e.g., "Multiple Choice Questions")

**Section Configuration:**

```json
{
  "section_id": "A",
  "title": "Multiple Choice Questions",
  "question_format": "MCQ",
  "marks_per_question": 1,
  "internal_choice": {
    "type": "none" | "any_n_out_of_m" | "either_or",
    "provided": 7,    // for any_n_out_of_m
    "attempt": 5      // for any_n_out_of_m
  },
  "questions_provided": 20,
  "questions_attempt": 20
}
```

**question_format** Values:**
- `MCQ`: Multiple Choice Questions
- `VERY_SHORT`: Very Short Answer (2 marks)
- `SHORT`: Short Answer (3 marks)
- `LONG`: Long Answer (5 marks)
- `CASE_STUDY`: Case Study Based Questions (4 marks)
- `ASSERTION_REASON`: Assertion-Reason (1 mark)

**internal_choice Types:**
- `none`: No internal choice (answer all)
- `any_n_out_of_m`: Provided N questions, attempt M where N > M
- `either_or`: Two alternatives (planned, not in MVP)

**questions_provided vs. questions_attempt:**
- `questions_provided`: Total questions in section
- `questions_attempt`: How many students must attempt (attempt ≤ provided)

---

## Reading the Blueprint

### Step 1: Load Blueprint
```markdown
Use the read_file tool to load the blueprint from `output/blueprint.json`.

Read the blueprint and extract the section configurations.
```

### Step 2: Extract Information

For each section, extract:
- section_id, title
- question_format
- marks_per_question
- internal_choice configuration
- questions_provided count to generate

### Step 3: Extract Topic Scope

From `syllabus_scope`:
- Get `chapters_included` list
- For each chapter, check if `topics` map exists
- If topics not provided, skill should assume all chapter topics are in scope

---

## Section Processing

**For generating Section A (MCQ - 20×1 mark):**
1. Format: MCQ questions require 4 options (A, B, C, D)
2. Must be unambiguous with single correct answer
3. Time: 1-2 minutes per question
4. Difficulty: Mix of easy (40%), medium (40%), hard (20%)
5. Must follow MCQ formatting in `QUESTION_FORMATS.json`

**For generating Section B (VSA - 5×2 marks):**
1. Format: Very Short Answer questions, 2-3 step calculations
2. Numeric or single-line acceptable
3. Working shown but brief
4. Time: 2-3 minutes per question
5. Complexity: Easy to Medium

**For generating Section C (SA - 6×3 marks):**
1. Format: Short Answer questions, 3-5 step solutions
2. Working shown clearly with intermediate steps
3. Formula-based questions
4. Time: 5-7 minutes per question
5. Complexity: Easy to Medium

**For generating Section D (LA - 4×5 marks):**
1. Format: Long Answer questions, 5+ step problems
2. Detailed working mandatory
3. Application-based problems with real-world scenarios
4. Time: 10-12 minutes per question
5. Complexity: Medium to Hard

**For generating Section E (Case Study - 3×4 marks):**
1. Format: Scenario description + 3-4 sub-questions (marks distributed 1+1+2 or 2+2)
2. Mix of:
   - Comprehension (paragraphs, graphs)
   - Calculation (data-based)
   - Application (apply concepts)
3. Create scenario with data/charts/tables as needed
4. Time: 10-12 minutes per case study

---

## Internal Choice Handling

### Type: none
- Generate exactly questions_provided questions
- No choice for students

### Type: any_n_out_of_m
- Generate exactly questions_provided questions in section
- Mark with internal choice indicators in paper:
  - Example: "Questions 1-7 are provided, attempt any 5"
  - Mark each question showing attempt range

### Type: either_or
- **Not implemented in MVP**
- For future: Create two alternative questions, student selects one

---

## Validation Rules

### For Generated Paper:
1. Total MUST equal blueprint.total_marks
2. Questions per section MUST equal questions_provided count
3. All questions MUST be from chapters_included
4. For any_n_out_of_m sections: attempt MUST ≤ provided

### During Generation:
1. Check questions_provided vs attempt balance
2. Difficulty distribution per section: ~40% easy, 40% medium, 20% hard
3. Ensure question IDs increment from 001 for each question type

### Generation Errors:
- If total marks mismatch: Add or remove questions to match total_marks
- If internal_choice mismatch: Log error for manual review
- Document all generation decisions in generation_metadata

---

## Example Blueprint Processing

### Given: Blueprint with 5 sections
```json
{
  "section_id": "A",
  "question_format": "MCQ",
  "marks_per_question": 1,
  "questions_provided": 20,
  "questions_attempt": 20
}
```

### Skill Instructions to Agent:
1. Generate 20 MCQ questions for Chapter: Real Numbers
2. Generate 5 VSA questions for Chapter: Polynomials
3. Continue for all sections...

### Example Processing Flow:
```
Loop through sections:
  For each section:
    Identify chapters from blueprint.syllabus_scope.chapters_included
    If blueprint.syllabus_scope.topics exists for that chapter:
        Use provided topics
    Else:
        Assume all chapter topics
    
    Generate questions following:
      - Section-specific format (MCQ/VSA/SA/LA/Case Study)
      - Difficulty distribution (40/40/20)
      - Question count from questions_provided
    
    Apply internal choice marking if needed
```

---

## Error Scenarios

### Scenario 1: Blueprint lacks topics
**Action**: When topics not specified for a chapter, assume ALL topics from that chapter are in scope.

### Scenario 2: Sections total marks don't sum to blueprint.total_marks
**Action**: Document as validation warning and continue with available sections.

### Scenario 3: Invalid internal_choice configuration (attempt > provided)
**Action**: Log error, regenerate section with correct configuration.

### Scenario 4: Blueprint chapter not in syllabus_scope.chapters_included
**Action**: Log error highlighting configuration mismatch.

---

## Agent Skills Specification Compliance

### Progressive Disclosure Strategy

1. **Always Load (~50 tokens):**
   - Name, description, references
   - Blueprint reference files path

2. **Load When Needed (~500 tokens each):**
   - Blueprint structure interpretation (load at start)
   - Generation workflow (load when generating)

3. **Load Per Format (~200 tokens each):**
   - MCQ generation reference (when generating MCQs)
   - VSA generation reference (when generating VSAs)
   - SA generation reference (when generating SAs)
   - LA generation reference (when generating LAs)
   - Case Study generation reference (when generating Case Studies)

4. **Load When Validating (~150 tokens):**
   - JSON Schema validation rules
   - Error recovery procedures
   - Quality checklists

### File References (Relative Paths)

From SKILL.md or GENERATION_WORKFLOW.md:
- `[the blueprint structure](./BLUEPRINT_REFERENCE.md)`
- `[the question formats](../common/QUESTION_FORMATS.json)`
- `[the requirements](./GENERATION_WORKFLOW.md)`

### scripts/ Directory

If Python scripts are needed:
1. Place in `scripts/` subdirectory
2. Keep scripts simple and self-contained
3. Document dependencies clearly
4. Include error handling for graceful failures

Example: Use `scripts/validators.py` for validation helpers like `calculate_difficulty_distribution()`.

---

## Summary

The blueprint.json structure provides:
1. Section configurations (format, marks, internal choice)
2. Chapter and topic scope
3. Total marks and duration
4. Exam metadata

The skill must:
1. Read and interpret this structure
2. Generate questions following section guidelines
3. Validate against constraints
4. Handle errors gracefully
5. Output QUESTION_PAPER_FORMAT.json compliant result