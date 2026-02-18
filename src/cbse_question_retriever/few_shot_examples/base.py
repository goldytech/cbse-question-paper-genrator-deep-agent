"""Generic few-shot examples (fallback for unimplemented subjects).

These examples show the JSON structure without subject-specific content.
Used when a subject or class doesn't have specific examples implemented.
"""

GENERIC_MCQ_EXAMPLE = """
EXAMPLE - MCQ (Multiple Choice Question):
Topic: [Topic Name]
Cognitive Level: REMEMBER
Difficulty: Easy
Marks: 1

Textbook Context:
[Relevant textbook content about the topic]

Generated Question:
{
  "question_text": "The question text goes here - clear and precise",
  "options": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
  "correct_answer": "A",
  "explanation": "Step-by-step explanation of why A is correct and why other options are wrong. This helps teachers verify the answer during review.",
  "diagram_needed": false,
  "diagram_description": null
}
"""

GENERIC_SHORT_EXAMPLE = """
EXAMPLE - SHORT ANSWER:
Topic: [Topic Name]
Cognitive Level: APPLY
Difficulty: Medium
Marks: 3

Textbook Context:
[Relevant textbook content about the topic]

Generated Question:
{
  "question_text": "The question text requiring 3-5 step solution",
  "options": null,
  "correct_answer": null,
  "explanation": "Step 1: ...\\nStep 2: ...\\nStep 3: ...\\nFinal answer: ...",
  "diagram_needed": false,
  "diagram_description": null
}
"""

GENERIC_LONG_EXAMPLE = """
EXAMPLE - LONG ANSWER:
Topic: [Topic Name]
Cognitive Level: ANALYSE
Difficulty: Hard
Marks: 5

Textbook Context:
[Relevant textbook content about the topic]

Generated Question:
{
  "question_text": "Comprehensive question requiring detailed multi-step solution",
  "options": null,
  "correct_answer": null,
  "explanation": "Step 1: ...\\nStep 2: ...\\nStep 3: ...\\nStep 4: ...\\nStep 5: ...\\nConclusion: ...",
  "diagram_needed": true,
  "diagram_description": "Detailed description of the diagram needed"
}
"""


def get_generic_examples() -> dict:
    """Return generic examples for fallback.

    Returns:
        Dictionary with examples by format.
    """
    return {
        "MCQ": GENERIC_MCQ_EXAMPLE,
        "VERY_SHORT": GENERIC_SHORT_EXAMPLE,
        "VSA": GENERIC_SHORT_EXAMPLE,
        "SHORT": GENERIC_SHORT_EXAMPLE,
        "SA": GENERIC_SHORT_EXAMPLE,
        "LONG": GENERIC_LONG_EXAMPLE,
        "LA": GENERIC_LONG_EXAMPLE,
        "CASE_STUDY": GENERIC_LONG_EXAMPLE,
    }
