---
name: query-optimization
description: Generates optimized search queries for CBSE educational content retrieval. Use when creating search queries to find CBSE question examples from educational websites.
metadata:
  version: "1.0"
  author: CBSE Question Paper Generator
---

# Query Optimization Skill

## Overview
This skill specializes in creating effective search queries for finding CBSE question examples from educational websites.

> **NOTE:** This skill was previously designed for Tavily web search. It will be updated for Qdrant vector database queries in the next phase.

## When to Use
Use this skill when you need to:
- Generate search queries for CBSE question retrieval
- Find practice questions for specific chapters and topics
- Search for solved examples and previous year questions
- Query educational content matching specific difficulty levels and formats

## Input Format
You will receive a JSON object with these fields:

```json
{
  "class": 10,
  "subject": "Mathematics",
  "chapter": "Polynomials",
  "topic": "Zeros of a Polynomial",
  "format": "MCQ",
  "marks": 1,
  "difficulty": "easy",
  "nature": "NUMERICAL",
  "cognitive_level": "REMEMBER"
}
```

**Field Definitions:**
- `class`: Class level (1-12)
- `subject`: Subject name (e.g., Mathematics, Science, English)
- `chapter`: Chapter name from CBSE syllabus
- `topic`: Specific topic within the chapter
- `format`: Question format - MCQ, VERY_SHORT, SHORT, LONG, CASE_STUDY
- `marks`: Marks per question (1, 2, 3, 4, 5)
- `difficulty`: Difficulty level - easy, medium, hard
- `nature`: Question nature - NUMERICAL, PROOF, WORD_PROBLEM, REASONING, DERIVATION, DATA_INTERPRETATION
- `cognitive_level`: Bloom's taxonomy level - REMEMBER, UNDERSTAND, APPLY, ANALYSE, EVALUATE, CREATE

## Output Format
Return a JSON object with the optimized query:

```json
{
  "optimized_query": "CBSE Class 10 Mathematics Polynomials Zeros practice questions easy MCQ"
}
```

## Query Construction Rules

### 1. Character Limit
- Maximum: 400 characters
- Optimal: 200-300 characters for best results
- Always stay under the limit

### 2. Required Keywords (ALWAYS Include)
These keywords must be present in every query:
- "CBSE" - Board identifier
- "Class {X}" - Class level (e.g., Class 10)
- "{Subject}" - Subject name
- "{Chapter}" - Chapter name
- "{Topic}" - Specific topic

### 3. Optional Modifiers (Include Based on Context)

**Format-specific terms:**
- MCQ: "multiple choice", "objective type", "MCQ"
- VERY_SHORT: "very short answer", "1 mark", "2 marks"
- SHORT: "short answer", "3 marks"
- LONG: "long answer", "5 marks", "detailed solution"
- CASE_STUDY: "case based", "passage based"

**Difficulty modifiers:**
- Easy: "basic", "simple", "introduction", "fundamental"
- Medium: "exercise", "problems", "application"
- Hard: "challenging", "difficult", "advanced", "complex"

**Nature-specific terms:**
- NUMERICAL: "numerical", "calculation", "solve"
- PROOF: "prove", "derivation", "theorem"
- WORD_PROBLEM: "word problem", "application", "real life"
- REASONING: "reasoning", "logical", "analytical"
- DATA_INTERPRETATION: "data", "interpretation", "graph"

**Content type terms:**
- "practice questions"
- "solved examples"
- "important questions"
- "NCERT solutions"
- "previous year questions"

### 4. Domain Filtering
The search will automatically target these educational domains:
- cbseacademic.nic.in
- byjus.com
- vedantu.com
- learn.careers360.com

### 5. Query Structure Template
```
CBSE Class {class} {subject} {chapter} {topic} {difficulty} {format} {content_type}
```

## Examples

### Example 1: MCQ Question
**Input:**
```json
{
  "class": 10,
  "subject": "Mathematics",
  "chapter": "Polynomials",
  "topic": "Zeros of a Polynomial",
  "format": "MCQ",
  "marks": 1,
  "difficulty": "easy",
  "nature": "NUMERICAL",
  "cognitive_level": "REMEMBER"
}
```

**Output:**
```json
{
  "optimized_query": "CBSE Class 10 Mathematics Polynomials Zeros of Polynomial easy MCQ multiple choice practice questions"
}
```

### Example 2: Long Answer Proof
**Input:**
```json
{
  "class": 10,
  "subject": "Mathematics",
  "chapter": "Triangles",
  "topic": "Pythagoras Theorem",
  "format": "LONG",
  "marks": 5,
  "difficulty": "medium",
  "nature": "PROOF",
  "cognitive_level": "UNDERSTAND"
}
```

**Output:**
```json
{
  "optimized_query": "CBSE Class 10 Mathematics Triangles Pythagoras Theorem proof derivation 5 marks long answer solved examples"
}
```

### Example 3: Short Answer Word Problem
**Input:**
```json
{
  "class": 10,
  "subject": "Mathematics",
  "chapter": "Pair of Linear Equations",
  "topic": "Graphical Method",
  "format": "SHORT",
  "marks": 3,
  "difficulty": "medium",
  "nature": "WORD_PROBLEM",
  "cognitive_level": "APPLY"
}
```

**Output:**
```json
{
  "optimized_query": "CBSE Class 10 Mathematics Pair of Linear Equations Graphical Method word problem application 3 marks short answer"
}
```

## Process

Follow these steps to construct the query:

1. **Extract Required Fields**
   - Identify class, subject, chapter, topic from input
   - Note format, difficulty, nature, cognitive level

2. **Build Core Query**
   - Start with "CBSE Class {class} {subject}"
   - Add "{chapter} {topic}"

3. **Add Context Modifiers**
   - Append difficulty modifier (easy, medium, hard)
   - Add format-specific term (MCQ, short answer, etc.)

4. **Include Content Type**
   - Add "practice questions" or "solved examples"
   - Include "important questions" if high marks (4-5)

5. **Verify Length**
   - Count characters
   - Trim if over 400 characters
   - Ensure all required keywords present

6. **Return JSON**
   - Format as {"optimized_query": "..."}
   - Ensure valid JSON syntax

## Best Practices

- Prioritize clarity over completeness
- Use standard CBSE terminology
- Include "NCERT" for textbook-style questions
- Add "previous year" for exam-focused content
- Keep queries focused and specific
- Avoid generic terms like "questions" alone
