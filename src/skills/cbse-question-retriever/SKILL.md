# CBSE Question Retriever

## Overview

This subagent retrieves CBSE textbook content from Qdrant vector database and generates exam questions using gpt-5-mini with structured output. Supports all CBSE classes (1-12) and subjects with optimized token usage for efficient question generation.

## When to Use

Call this subagent for each question to be generated based on blueprint specifications. This subagent handles the complete workflow from retrieving relevant textbook content to generating CBSE-compliant questions.

## Tools

### Tool 1: generate_question_tool (Chunk Retrieval)

**Purpose**: Retrieves relevant textbook chunks from Qdrant vector database based on blueprint specifications.

**Input Parameters**:

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `blueprint_path` | str | Yes | Path to the exam blueprint JSON file | `"input/classes/10/mathematics/first.json"` |
| `section_id` | str | Yes | Section identifier from blueprint | `"A"`, `"B"`, `"C"` |
| `question_number` | int | Yes | Question number within the section | `1`, `2`, `3` |

**Return Format**:

```json
{
  "chunks": [
    {
      "text": "A polynomial p(x) has zeros where p(x) = 0. For a linear polynomial ax + b, the zero is -b/a.",
      "chunk_type": "THEORY",
      "metadata": {
        "chapter": "Polynomials",
        "topic": "Zeros",
        "page": 45
      }
    }
  ],
  "metadata": {
    "collection": "mathematics_10",
    "total_chunks": 5,
    "question_id": "MATH-10-POL-MCQ-001"
  },
  "error": null
}
```

**Error Response**:
```json
{
  "chunks": [],
  "metadata": {},
  "error": "No chunks found for specified criteria"
}
```

### Tool 2: generate_llm_question_tool (Question Generation)

**Purpose**: Generates CBSE-compliant questions using retrieved chunks and LLM with structured output.

**Input Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `chunks` | List[Dict] | Yes | Retrieved textbook chunks from Tool 1 |
| `blueprint_context` | Dict | Yes | Question specifications (see details below) |
| `question_id` | str | Yes | Unique question identifier | `"MATH-10-POL-MCQ-001"` |

**Blueprint Context Fields**:

| Field | Type | Required | Description | Allowed Values |
|-------|------|----------|-------------|----------------|
| `class_level` | int | Yes | Class number (1-12) | 1-12 |
| `subject` | str | Yes | Subject name | "mathematics", "science", etc. |
| `chapter` | str | Yes | Chapter name | e.g., "Polynomials" |
| `topic` | str | Yes | Specific topic | e.g., "Zeros" |
| `question_format` | str | Yes | Question format type | "MCQ", "VERY_SHORT", "SHORT", "LONG", "CASE_STUDY" |
| `marks` | int | Yes | Marks allocated | 1, 2, 3, 4, 5 |
| `difficulty` | str | Yes | Difficulty level | "easy", "medium", "hard" |
| `bloom_level` | str | Yes | Bloom's taxonomy level | "REMEMBER", "UNDERSTAND", "APPLY", "ANALYSE", "EVALUATE", "CREATE" |
| `nature` | str | Yes | Question nature | "NUMERICAL", "CONCEPTUAL", "REASONING", "WORD_PROBLEM", "DERIVATION" |

**Return Format - Success**:

```json
{
  "question_id": "MATH-10-POL-MCQ-001",
  "question_text": "What is the zero of the polynomial p(x) = x - 3?",
  "chapter": "Polynomials",
  "topic": "Zeros",
  "question_format": "MCQ",
  "marks": 1,
  "options": ["A) 0", "B) 3", "C) -3", "D) 1"],
  "correct_answer": "B",
  "difficulty": "easy",
  "bloom_level": "UNDERSTAND",
  "nature": "NUMERICAL",
  "explanation": "To find the zero of a polynomial, set p(x) = 0. Therefore: x - 3 = 0 → x = 3. The zero is 3.",
  "diagram_needed": false,
  "diagram_description": null,
  "generation_metadata": {
    "model": "gpt-5-mini",
    "temperature": 0.3,
    "chunks_used": 3,
    "few_shot_enabled": true,
    "validation_passed": true
  },
  "error": null,
  "error_phase": null
}
```

**Return Format - Error**:

```json
{
  "question_id": "MATH-10-POL-MCQ-001",
  "question_text": "[Error: Could not generate question - No textbook chunks found]",
  "options": null,
  "correct_answer": null,
  "explanation": "Error during generation: No textbook chunks found",
  "diagram_needed": false,
  "diagram_description": null,
  "generation_metadata": {
    "model": "gpt-5-mini",
    "temperature": 0.3,
    "error": true,
    "error_message": "No textbook chunks found",
    "error_phase": "retrieval"
  },
  "error": "No textbook chunks found",
  "error_phase": "retrieval"
}
```

**Error Phase Values**:
- `"retrieval"`: Error occurred during chunk retrieval (Tool 1)
- `"llm"`: Error occurred during question generation (Tool 2)

## Implementation Status

✅ **Fully Implemented**

- Qdrant vector database integration (port 65020)
- Hybrid search with vector similarity + metadata filtering
- LangChain structured output with gpt-5-mini
- Subject-specific few-shot examples (Mathematics Class 10 implemented)
- Automatic diagram detection and generation support
- Comprehensive error handling with detailed error responses
- Quality validation before returning questions
- Fallback to generic examples for unimplemented subjects

## Example Usage

### Complete Workflow Example

**Step 1: Retrieve textbook chunks**
```python
task(
    name="cbse-question-retriever",
    task="Retrieve chunks for: blueprint_path=input/classes/10/mathematics/first.json, section_id=A, question_number=1"
)
```

**Step 2: Generate question using retrieved chunks**
```python
blueprint_context = {
    "class_level": 10,
    "subject": "mathematics",
    "chapter": "Polynomials",
    "topic": "Zeros",
    "question_format": "MCQ",
    "marks": 1,
    "difficulty": "easy",
    "bloom_level": "UNDERSTAND",
    "nature": "NUMERICAL"
}

task(
    name="cbse-question-retriever",
    task=f"Generate question using chunks: {chunks}, blueprint_context: {blueprint_context}, question_id=MATH-10-POL-MCQ-001"
)
```

### Output Schema Notes

The streamlined output schema includes only essential fields:

**Required Fields**:
- `question_text`: The actual exam question
- `options`: Array of 4 options for MCQ, null for others
- `correct_answer`: "A"/"B"/"C"/"D" for MCQ, null for others
- `explanation`: Step-by-step solution for teacher verification
- `diagram_needed`: Boolean flag for diagram requirement
- `diagram_description`: Detailed description if diagram needed

**Metadata Fields**:
- `generation_metadata`: Technical details about generation
- `error`: Error message if generation failed
- `error_phase`: Phase where error occurred ("retrieval" or "llm")

This optimized schema reduces token usage by ~6,540 tokens per 23-question paper while maintaining all necessary information for teacher review and answer key generation.
