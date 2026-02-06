# Generation Workflow for CBSE Questions

## Overview
This document provides step-by-step procedures for generating CBSE Class 10 Mathematics questions using subagents for validation and research.

---

## Universal Generation Steps (All Questions)

### Step 0: Initialize Question Counter
- Start question numbering from 001 per section
- Track which section question numbers belong to

### Step 1: Read Blueprint
```
Use read_file tool to load: input/blueprint_first_term_50.json

Parse blueprint JSON to extract:
- Blueprint version
- Exam metadata (class, subject, total_marks, duration)
- Syllabus scope (chapters_included, topics)
- Section configurations
```

### Step 2: Validate Blueprint Structure Using Subagent
**Delegate validation to blueprint-validator subagent:**
```
task(name="blueprint-validator", 
     task="Validate blueprint at path: input/blueprint_first_term_50.json")
```

**Expected Response:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": ["Section B has unusual marks_per_question: 3"]
}
```

**Action:**
- If `valid: false` → Stop and report errors. Do NOT proceed.
- If `valid: true` → Continue to Step 3

**What the subagent checks:**
1. Required fields exist (exam_metadata, syllabus_scope, sections)
2. Total marks calculation is correct
3. Internal choice types are valid
4. Question formats are valid
5. Marks per question values are reasonable

---

### Step 3: Extract Section Configuration
For each section:
```
Parse to extract:
- section_id, title
- question_format (MCQ, SHORT, LONG, etc.)
- marks_per_question
- internal_choice configuration
- questions_provided (count to generate)
```

---

### Step 4: Determine Chapter and Topic Scope
```
For each section:
  1. Identify which chapters_included apply
  2. For each chapter in section:
      If blueprint.syllabus_scope.topics[chapter] exists:
          Use EXACT topics listed
      Else:
          Assume ALL chapter topics are in scope
```

---

### Step 5: Generate Questions per Section Using Subagent
For each question needed in the section:

#### 5.1 Delegate Research to question-researcher Subagent
```
task(name="question-researcher", 
     task="Format=MCQ, Chapter=Real Numbers, Topic=LCM HCF, Difficulty=easy")
```

**Parameters to provide:**
- `Format`: MCQ, SHORT, LONG, CASE_STUDY
- `Chapter`: Chapter name from blueprint
- `Topic`: Specific topic (optional but recommended)
- `Difficulty`: easy, medium, or hard

#### 5.2 Receive and Parse Subagent Response
**Expected Response Format:**
```json
{
  "rephrased_question": "Calculate the least common multiple of 15 and 20",
  "original_concept": "LCM calculation using prime factorization",
  "difficulty": "easy",
  "question_type": "MCQ",
  "suggested_answer": "60",
  "sources_consulted": [
    "https://example.com/cbse-question-1",
    "https://example.com/cbse-question-2"
  ]
}
```

#### 5.3 Create Final Question
Use the `rephrased_question` as template and add:
1. **Question ID**: Follow format `MATH-10-[CHAP]-[FORMAT]-[NUM]`
   - Example: `MATH-10-REA-MCQ-001`
2. **Question Text**: Use or adapt the rephrased question
3. **Metadata**:
   - chapter: From blueprint
   - topic: Specific topic
   - question_format: MCQ/SHORT/LONG/etc.
   - marks: From blueprint section config
   - difficulty: easy/medium/hard
   - bloom_level: remembering/understanding/applying/analyzing
   - tags: Topic keywords
4. **For MCQ only**: Add 4 options and correct_answer

**Example Final Question:**
```json
{
  "question_id": "MATH-10-REA-MCQ-001",
  "question_text": "Calculate the least common multiple of 15 and 20.",
  "chapter": "Real Numbers",
  "topic": "LCM HCF",
  "question_format": "MCQ",
  "marks": 1,
  "options": ["A) 40", "B) 60", "C) 80", "D) 100"],
  "correct_answer": "B",
  "difficulty": "easy",
  "bloom_level": "apply",
  "tags": ["lcm hcf", "real numbers"]
}
```

#### 5.4 Add to Section
Add the completed question to the current section's questions array.

**Repeat 5.1-5.4** for each question needed in the section.

---

## Format-Specific Generation Procedures

### MCQ (Multiple Choice Questions) - 1 Mark Each

**Step 1: Determine Topic Distribution**
```
Given:
- Questions needed: 20
- Chapters: Real Numbers (5), Polynomials (5), Linear Equations (5), Quadratic Equations (5)

Distribute: 5 MCQs from each chapter:
  - Easy: 2 questions per chapter (40%)
  - Medium: 2 questions per chapter (40%)
  - Hard: 1 question per chapter (20%)
```

**Step 2: Generate Each MCQ Using Subagent**
```
For each MCQ:
  1. Call question-researcher with:
     - Format: MCQ
     - Chapter: [current chapter]
     - Topic: [select from chapter topics]
     - Difficulty: [easy/medium/hard based on distribution]
  
  2. Receive rephrased question template
  
  3. Create final MCQ:
     - Use rephrased_question as base text
     - Create 4 options (A, B, C, D):
         * A: Plausible distractor
         * B: Correct answer (vary position)
         * C: Partially correct calculation
         * D: Incorrect answer
     - Define correct_answer (e.g., "B")
     - Assign bloom_level based on cognitive demand
     - Create tags with topic keywords
```

**Step 3: Format Question ID**
```
Format: MATH-10-[CHAPTER_ABBR]-MCQ-[NUM]
Example: MATH-10-REA-MCQ-001, MATH-10-POL-MCQ-002
```

**Step 4: Example Question Object**
```json
{
  "question_id": "MATH-10-REA-MCQ-001",
  "question_text": "Calculate the least common multiple of 15 and 20.",
  "chapter": "Real Numbers",
  "topic": "LCM HCF",
  "question_format": "MCQ",
  "marks": 1,
  "options": ["A) 40", "B) 60", "C) 80", "D) 100"],
  "correct_answer": "B",
  "difficulty": "easy",
  "bloom_level": "apply",
  "tags": ["lcm hcf", "real numbers", "mcq"]
}
```

---

### SHORT (Short Answer) - 3 Marks Each

**Step 1: Distribute Topics**
```
Mix chapter topics to ensure variety:
- 3-4 different topics per section
- Balance easy/medium difficulty
```

**Step 2: Generate Using Subagent**
```
For each SHORT question:
  1. Call question-researcher with:
     - Format: SHORT
     - Chapter: [current chapter]
     - Topic: [selected topic]
     - Difficulty: [medium recommended for 3-mark]
  
  2. Receive rephrased question requiring 3-5 steps
  
  3. Create final question:
     - Use rephrased question as base
     - Ensure it requires 3-5 step solution
     - Provide correct_answer format (numeric or short explanation)
     - Mark difficulty: medium (typical for 3-mark)
     - Format bloom_level: apply/analyze
```

**Step 3: Example**
```json
{
  "question_id": "MATH-10-REA-SHORT-001",
  "question_text": "Find HCF of 144 and 192 using Euclid's division algorithm. Show all steps.",
  "chapter": "Real Numbers",
  "topic": "Euclid Division Algorithm",
  "question_format": "SHORT",
  "marks": 3,
  "options": null,
  "correct_answer": "48 (with step-by-step working)",
  "difficulty": "medium",
  "bloom_level": "apply",
  "tags": ["euclid algorithm", "hcf", "real numbers"]
}
```

---

### LONG (Long Answer) - 5 Marks Each

**Step 1: Select Real-World Scenario**
```
Choose themes from real-life applications:
- Word problems (quadratic equations, linear equations)
- Geometry proofs (triangles, circles)
- Trigonometry applications (heights and distances)
- Surface area/volume calculations (real-world objects)
```

**Step 2: Generate Using Subagent**
```
For each LONG question:
  1. Call question-researcher with:
     - Format: LONG
     - Chapter: [current chapter]
     - Topic: [application topic]
     - Difficulty: [medium or hard]
  
  2. Receive rephrased complex problem
  
  3. Ensure question has:
     - Real-world context
     - 5+ steps to solve
     - Multiple concepts integrated
     - Detailed working required
```

**Step 3: Example**
```json
{
  "question_id": "MATH-10-QUAD-LONG-001",
  "question_text": "A train travels 360 km at uniform speed. If speed had been 6 km/h more, it would have taken 1 hour less for the same journey. Find the original speed of the train.",
  "chapter": "Quadratic Equations",
  "topic": "Word Problems - Speed/Distance",
  "question_format": "LONG",
  "marks": 5,
  "options": null,
  "correct_answer": "36 km/h (with complete solution showing quadratic equation formation and solving)",
  "difficulty": "hard",
  "bloom_level": "analyze",
  "tags": ["quadratic equations", "word problem", "speed distance"]
}
```

---

## Step 6: Compile Paper Structure
```
Structure:
{
  "schema_version": "1.0",
  "paper_id": "unique-uuid",
  "blueprint_reference": "input/blueprint_first_term_50.json",
  "exam_metadata": { ... },
  "sections": [
    {
      "section_id": "A",
      "title": "Multiple Choice Questions",
      "questions": [ ... all MCQs ... ]
    },
    {
      "section_id": "B", 
      "title": "Short Answer",
      "questions": [ ... all SHORTs ... ]
    }
    // ... more sections
  ],
  "total_marks": 50,
  "total_questions": 20,
  "generation_metadata": {
    "timestamp": "2026-01-29T18:48:26",
    "subagents_used": ["blueprint-validator", "question-researcher", "paper-validator"]
  }
}
```

---

## Step 7: Validate Final Paper Using Subagent
**Delegate validation to paper-validator subagent:**
```
task(name="paper-validator", 
     task="Validate paper at output/question_paper.json against input/blueprint_first_term_50.json")
```

**Expected Response:**
```json
{
  "valid": true,
  "issues": [],
  "warnings": ["Question MATH-10-REA-MCQ-003: missing bloom_level field"]
}
```

**Action:**
- If `valid: false` → Review issues list, fix problems, re-validate
- If `valid: true` → Save final paper and present to teacher

**What the subagent checks:**
1. Total marks match blueprint
2. Question counts per section are correct
3. All questions from blueprint chapters only
4. Internal choice configuration alignment
5. Required fields present in questions

---

## Step 8: Save and Present
```
Save to: output/question_paper.json

Present to teacher:
"Generated 20 questions (10 MCQ + 5 SHORT + 5 LONG) for 50 marks 
covering Real Numbers, Polynomials, and Linear Equations. 
All validations passed. Ready for review."
```

---

## Example Outputs from Subagents

### Example 1: blueprint-validator Output
```json
{
  "valid": false,
  "errors": [
    "Total marks mismatch: expected 50, calculated 45",
    "Section B: invalid question format 'ESSAY'"
  ],
  "warnings": [
    "Section C: unusual marks_per_question: 4"
  ]
}
```
**Interpretation**: Fix total marks calculation and question format before proceeding.

### Example 2: question-researcher Output
```json
{
  "rephrased_question": "Find the HCF of 136 and 170 using Euclid's division algorithm",
  "original_concept": "HCF using Euclid's algorithm",
  "difficulty": "medium",
  "question_type": "SHORT",
  "suggested_answer": "34 (showing steps: 170 = 136×1 + 34, 136 = 34×4 + 0)",
  "sources_consulted": [
    "https://cbse.nic.in/sample-questions",
    "https://ncert.nic.in/class10-math"
  ]
}
```
**Interpretation**: Use this template to create a SHORT question on Euclid's algorithm.

### Example 3: paper-validator Output
```json
{
  "valid": false,
  "issues": [
    "Section A: expected 10 questions, got 8",
    "Question MATH-10-POL-MCQ-004: chapter 'Algebra' not in blueprint"
  ],
  "warnings": [
    "Potential duplicate questions detected"
  ]
}
```
**Interpretation**: Add 2 more questions to Section A, fix chapter reference, check for duplicates.

---

## Difficulty Distribution Algorithm

### Calculate Per Section
```
For each section:
  Given format and marks_per_question:
    - MCQ (1 mark): Easy questions are direct, medium multi-concept
    - SHORT (3 marks): Medium (3-5 steps), Hard (5+ steps)
    - LONG (5 marks): Medium to Hard (multi-step, complex)

For 20 MCQs:
  - Easy: 8 questions (40%)
  - Medium: 8 questions (40%)
  - Hard: 4 questions (20%)
```

### Implementation
Use hardcoded distribution in prompts to question-researcher:
```
"Generate with difficulty: easy" (for 40% of questions)
"Generate with difficulty: medium" (for 40% of questions)
"Generate with difficulty: hard" (for 20% of questions)
```

---

## Troubleshooting

### Error 1: Subagent Returns No Results
**Problem**: question-researcher returns empty or irrelevant question

**Solution**:
1. Retry with more specific topic description
2. Try broader search (remove topic, keep only chapter)
3. If still failing, generate based on SKILL.md domain knowledge
4. Log: "No online examples found, using domain knowledge for [topic]"

### Error 2: blueprint-validator Shows Marks Mismatch
**Problem**: Calculated marks don't match blueprint.total_marks

**Solution**:
1. Verify section configuration:
   ```
   section_marks = marks_per_question × questions_attempt
   ```
2. Sum all section marks
3. Adjust questions_provided or marks_per_question
4. Re-validate after fixes

### Error 3: paper-validator Finds Chapter Mismatch
**Problem**: Generated question has chapter not in blueprint

**Solution**:
1. List valid chapters from blueprint.syllabus_scope.chapters_included
2. Identify which questions have invalid chapters
3. Replace with questions from valid chapters
4. Re-validate

### Error 4: question-researcher Times Out
**Problem**: Subagent doesn't respond within reasonable time

**Solution**:
1. Wait 30 seconds, retry once
2. If still failing:
   - Use SKILL.md domain knowledge to generate question
   - Use generic CBSE pattern from memory
   - Log error for later investigation
3. Continue with best-effort generation

### Error 5: Difficulty Distribution Wrong
**Problem**: Generated paper doesn't have 40/40/20 distribution

**Solution**:
1. Count current distribution by difficulty
2. Identify which questions need adjustment
3. Re-call question-researcher with explicit difficulty requests
4. Replace questions to match distribution
5. Re-validate

---

## Summary

This workflow uses subagents for:
1. **Validation** (blueprint-validator, paper-validator) - Ensures structure correctness
2. **Research** (question-researcher) - Finds and rephrases real CBSE questions

**Key Benefits**:
- ✅ Context isolation - Research doesn't bloat main agent context
- ✅ Quality assurance - Validation checks happen automatically
- ✅ Real CBSE patterns - Questions based on actual examples
- ✅ Clean architecture - Each component has specific responsibility

**Remember**: Always delegate to subagents. Do NOT try to validate or search manually.
