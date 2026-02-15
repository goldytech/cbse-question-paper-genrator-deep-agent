# CBSE Question Retriever

## Overview

This subagent retrieves CBSE textbook chunks from Qdrant vector database and generates questions using GPT-4o.

## When to Use

Call this subagent for each question to be generated based on blueprint specifications.

## Tool Usage

```python
task(name="cbse-question-retriever", 
     task="Generate question for: Class=10, Subject=mathematics, Chapter=Polynomials, Topic=Zeros, Format=MCQ, Difficulty=easy, Marks=1")
```

## Workflow

1. Query Qdrant vector database using collection naming convention `{subject}_{class}`
2. Retrieve relevant textbook chunks based on chapter, topic, and requirements
3. Use GPT-4o to generate CBSE-compliant question from retrieved chunks
4. Auto-detect if diagram is needed based on question content
5. Call `generate_diagram_tool` if diagram is required
6. Return complete question with all required fields

## Return Format

```json
{
  "question_id": "MATH-10-POL-MCQ-001",
  "question_text": "Find the zeroes of the polynomial x² - 5x + 6",
  "chapter": "Polynomials",
  "topic": "Zeros",
  "question_format": "MCQ",
  "marks": 1,
  "options": ["A) 2, 3", "B) 1, 6", "C) -2, -3", "D) -1, -6"],
  "correct_answer": "A",
  "difficulty": "easy",
  "bloom_level": "understand",
  "nature": "NUMERICAL",
  "has_diagram": false,
  "chunks_used": 3
}
```

## Implementation Status

⚠️ This is a placeholder. Implementation pending.
