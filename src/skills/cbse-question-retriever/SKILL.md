# CBSE Question Retriever

## Overview

This subagent retrieves CBSE textbook content from Qdrant vector database and generates exam questions using gpt-5-mini with structured output. Supports all CBSE classes (1-12) and all subjects with optimized token usage for efficient question generation.

## Prerequisites

Before using this subagent, the blueprint file must be located using the **input_file_locator** subagent. See `src/skills/input-file-locator/SKILL.md` for details on blueprint discovery.

The input_file_locator:
- Searches `input/classes/{class}/{subject}/` folder structure
- Prioritizes teacher files (`input_*.json`) over master blueprints (`blueprint.json`)
- Returns the file path to use with this subagent

## Input Folder Structure

```
input/classes/{class}/{subject}/
├── blueprint.json          # Master blueprint (fallback)
└── input_{exam_name}.json  # Teacher input files (priority)
```

**Pattern variables**:
- `{class}`: Class number (1-12)
- `{subject}`: Subject name (e.g., "mathematics", "science", "english", "social_science", "hindi", "sanskrit")
- Teacher files (input_*.json) always override master blueprints

## Tools

### Tool 1: generate_question_tool (Chunk Retrieval)

**Purpose**: Retrieves relevant textbook chunks from Qdrant vector database based on blueprint specifications.

**Input Parameters**:

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `blueprint_path` | str | Yes | Path to the exam blueprint JSON file (from input_file_locator) | `"input/classes/{class}/{subject}/{blueprint_file}.json"` |
| `section_id` | str | Yes | Section identifier from blueprint | `"A"`, `"B"`, `"C"` |
| `question_number` | int | Yes | Question number within the section | `1`, `2`, `3` |

**Return Format**:

```json
{
  "chunks": [
    {
      "text": "[Textbook content about {topic}]",
      "chunk_type": "THEORY|WORKED_EXAMPLE|EXERCISE",
      "metadata": {
        "chapter": "{chapter}",
        "topic": "{topic}",
        "page": 45
      }
    }
  ],
  "metadata": {
    "collection": "{subject}_{class}",
    "total_chunks": 5,
    "question_id": "{SUBJECT_ABBR}-{CLASS}-{CHAPTER_ABBR}-{FORMAT_ABBR}-{NUM}"
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
| `question_id` | str | Yes | Unique question ID in format `{SUBJECT_ABBR}-{CLASS}-{CHAPTER_ABBR}-{FORMAT_ABBR}-{NUM}` |

**Blueprint Context Fields**:

| Field | Type | Required | Description | Allowed Values |
|-------|------|----------|-------------|----------------|
| `class_level` | int | Yes | Class number (1-12) | 1-12 |
| `subject` | str | Yes | Subject name | "mathematics", "science", "english", "social_science", "hindi", "sanskrit", etc. |
| `chapter` | str | Yes | Chapter name | e.g., "Polynomials", "Motion", "Literature" |
| `topic` | str | Yes | Specific topic | e.g., "Zeros", "Velocity", "Poetry" |
| `question_format` | str | Yes | Question format type | "MCQ", "VERY_SHORT", "SHORT", "LONG", "CASE_STUDY" |
| `marks` | int | Yes | Marks allocated | 1, 2, 3, 4, 5 |
| `difficulty` | str | Yes | Difficulty level | "easy", "medium", "hard" |
| `bloom_level` | str | Yes | Bloom's taxonomy level | "REMEMBER", "UNDERSTAND", "APPLY", "ANALYSE", "EVALUATE", "CREATE" |
| `nature` | str | Yes | Question nature | "NUMERICAL", "CONCEPTUAL", "REASONING", "WORD_PROBLEM", "DERIVATION" |

**Question ID Format**:

Format: `{SUBJECT_ABBR}-{CLASS}-{CHAPTER_ABBR}-{FORMAT_ABBR}-{NUM}`

Examples:
- `MATH-10-POL-MCQ-001` (Class 10 Mathematics, Polynomials chapter, MCQ format)
- `SCI-09-PHYS-SA-001` (Class 9 Science, Physics chapter, Short Answer format)
- `ENG-12-LIT-LA-001` (Class 12 English, Literature chapter, Long Answer format)

The question ID generator (`src/cbse_question_retriever/question_id_generator.py`) handles abbreviation mappings for subjects, chapters, and formats.

**Return Format - Success**:

```json
{
  "question_id": "{SUBJECT_ABBR}-{CLASS}-{CHAPTER_ABBR}-{FORMAT_ABBR}-{NUM}",
  "question_text": "[Question text for {topic} in {chapter}]",
  "chapter": "{chapter}",
  "topic": "{topic}",
  "question_format": "{format}",
  "marks": {marks},
  "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
  "correct_answer": "{A|B|C|D}",
  "difficulty": "{difficulty}",
  "bloom_level": "{bloom_level}",
  "nature": "{nature}",
  "explanation": "[Step-by-step solution for teacher verification]",
  "diagram_needed": {true|false},
  "diagram_description": "[Description if diagram needed, else null]",
  "generation_metadata": {
    "model": "gpt-5-mini",
    "temperature": 0.3,
    "chunks_used": {count},
    "few_shot_enabled": {true|false},
    "validation_passed": {true|false}
  },
  "error": null,
  "error_phase": null
}
```

**Return Format - Error**:

```json
{
  "question_id": "{SUBJECT_ABBR}-{CLASS}-{CHAPTER_ABBR}-{FORMAT_ABBR}-{NUM}",
  "question_text": "[Error: Could not generate question - {error_message}]",
  "options": null,
  "correct_answer": null,
  "explanation": "Error during generation: {error_message}",
  "diagram_needed": false,
  "diagram_description": null,
  "generation_metadata": {
    "model": "gpt-5-mini",
    "temperature": 0.3,
    "error": true,
    "error_message": "{error_message}",
    "error_phase": "{phase}"
  },
  "error": "{error_message}",
  "error_phase": "{phase}"
}
```

**Error Phase Values**:
- `"retrieval"`: Error occurred during chunk retrieval (Tool 1)
- `"llm"`: Error occurred during question generation (Tool 2)

## Collection Naming

Qdrant vector database collections follow the naming pattern: `{subject}_{class}`

Examples:
- `mathematics_10` (Class 10 Mathematics)
- `science_09` (Class 9 Science)
- `english_12` (Class 12 English)
- `social_science_08` (Class 8 Social Science)

## Implementation Status

✅ **Fully Implemented**

- Supports all CBSE classes (1-12) via `{class}` parameter
- Supports all subjects via `{subject}` parameter
- Subject-specific few-shot examples architecture (Mathematics Class 10 implemented, extensible for all subjects)
- Generic fallback examples for unimplemented subjects
- Qdrant vector database integration with `{subject}_{class}` collection naming
- Blueprint auto-discovery via input_file_locator subagent
- Hybrid search with vector similarity + metadata filtering
- LangChain structured output with gpt-5-mini
- Automatic diagram detection and generation support
- Comprehensive error handling with detailed error responses
- Quality validation before returning questions

## Example Usage

### Complete Workflow

**Step 1: Locate blueprint using input_file_locator**
```python
# This is handled by the input_file_locator subagent
blueprint_info = task(
    name="input-file-locator",
    task="Locate blueprint from: 'Generate class {class} {subject} paper'"
)
# Returns: blueprint_info["file_path"] = "input/classes/{class}/{subject}/{blueprint_file}.json"
```

**Step 2: Retrieve textbook chunks**
```python
chunks_result = task(
    name="cbse-question-retriever",
    task="Retrieve chunks for: blueprint_path=input/classes/{class}/{subject}/{blueprint_file}.json, section_id={section}, question_number={number}"
)
```

**Step 3: Generate question using retrieved chunks**
```python
blueprint_context = {
    "class_level": {class},
    "subject": "{subject}",
    "chapter": "{chapter}",
    "topic": "{topic}",
    "question_format": "{format}",
    "marks": {marks},
    "difficulty": "{difficulty}",
    "bloom_level": "{bloom_level}",
    "nature": "{nature}"
}

question_result = task(
    name="cbse-question-retriever",
    task=f"Generate question using chunks: {chunks_result}, blueprint_context: {blueprint_context}, question_id={SUBJECT_ABBR}-{CLASS}-{CHAPTER_ABBR}-{FORMAT_ABBR}-{NUM}"
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
