"""Prompt templates for LLM question generation.

Contains detailed prompts with few-shot examples for different question formats.
Few-shot examples are loaded dynamically based on subject and class level.
"""

from .few_shot_examples import get_examples_for_subject

# Format-specific instructions
FORMAT_INSTRUCTIONS = {
    "MCQ": """MCQ-SPECIFIC REQUIREMENTS (1 mark):
- Generate exactly 4 options labeled A, B, C, D
- One option must be clearly correct
- Other 3 options must be plausible distractors based on common misconceptions
- Distractors should be of similar length and complexity to the correct answer
- Options should test different aspects of understanding
- Include brief explanation of why correct answer is right and why distractors are wrong""",
    "VERY_SHORT": """VERY SHORT ANSWER REQUIREMENTS (2 marks):
- Question should require 1-2 step solution or direct recall
- Can be: definition, formula, simple calculation, or concept identification
- Answer should be specific and brief (1-2 sentences)
- Clear expected answer format
- Explanation should elaborate the concept briefly""",
    "SHORT": """SHORT ANSWER REQUIREMENTS (3 marks):
- Question should require 3-5 step solution
- Show complete working steps in explanation
- Can ask for: derivation, proof, application, or multi-step problem
- Answer should be comprehensive but concise
- Include all mathematical steps clearly""",
    "LONG": """LONG ANSWER REQUIREMENTS (5 marks):
- Multi-step problem requiring comprehensive solution (5+ steps)
- May combine multiple concepts from the chapter
- Real-world application or complex analysis preferred
- Step-by-step working is essential
- Include interpretation/conclusion where applicable
- May require diagram support""",
    "CASE_STUDY": """CASE STUDY REQUIREMENTS (4 marks):
- Provide a real-world scenario or context first
- Then ask 2-3 related analytical questions
- Questions should have mark distribution (e.g., 1+1+2 or 2+2)
- Application of multiple concepts to solve practical problem
- Context should be relatable to students' life""",
}

# Main generation prompt template
CBSE_QUESTION_GENERATION_PROMPT = """You are an expert CBSE (Central Board of Secondary Education) question paper setter with 20 years of experience creating high-quality examination questions for Indian secondary school students.

=== STUDENT AND CURRICULUM CONTEXT ===
Target Class: {class_level}
Subject: {subject}
Chapter: {chapter}
Specific Topic: {topic}
Section in Paper: {section_title}

=== QUESTION SPECIFICATIONS ===
Question Format: {question_format}
Marks Allocated: {marks}
Difficulty Level: {difficulty}
  - Easy (40%): Direct formula/concept application
  - Medium (40%): Multi-concept integration, problem-solving
  - Hard (20%): Complex analysis, multi-step reasoning

Cognitive Level (Bloom's Taxonomy): {bloom_level}
  - REMEMBER: Recall facts, terms, basic concepts
  - UNDERSTAND: Explain ideas, concepts, interpret information
  - APPLY: Use information in new situations, solve problems
  - ANALYSE: Draw connections, differentiate, examine structure
  - EVALUATE: Justify decisions, critique, assess
  - CREATE: Produce new work, design, construct

Question Nature: {nature}
  - NUMERICAL: Requires calculation/computation
  - CONCEPTUAL: Tests understanding of concepts
  - REASONING: Logical thinking, proofs, deductions
  - WORD_PROBLEM: Real-world application scenarios
  - DERIVATION: Step-by-step derivation or proof

=== REFERENCE TEXTBOOK CONTENT (NCERT) ===
Use the following content as your primary source for generating the question:

{chunks_formatted}

{few_shot_section}

=== FORMAT-SPECIFIC INSTRUCTIONS ===
{format_instructions}

=== QUALITY AND PEDAGOGICAL STANDARDS ===
MUST FOLLOW:
1. CBSE Language: Use standard terminology and phrasing as per NCERT
2. Clarity: Question must be unambiguous with single correct interpretation
3. Solvability: Can be solved without calculator (unless specified)
4. Age-Appropriate: Matches Class {class_level} cognitive development level
5. Accuracy: Mathematically and scientifically correct
6. Originality: Inspired by textbook but not copied verbatim
7. Pedagogy: Effectively tests the specified cognitive level

STRICTLY AVOID:
- Ambiguous or unclear wording
- Multiple correct answers (unless specified in format)
- Overly complex language or unnecessary jargon
- Values requiring calculator for computation
- Out-of-syllabus content or advanced concepts
- Biased or culturally insensitive content

=== DIAGRAM REQUIREMENT ===
After generating the question, determine if a diagram is needed based on:
1. Geometric shapes or constructions mentioned?
2. Coordinate geometry or graphing involved?
3. Visual representation would aid understanding?
4. Statistical data visualization required?

If YES, provide detailed description of what should be drawn.

=== OUTPUT FORMAT (STRICT JSON) ===
Return ONLY a valid JSON object with exactly this structure:

{{
  "question_text": "The actual question text - clear and precise",
  "options": [{options_field}],
  "correct_answer": {correct_answer_field},
  "explanation": "Step-by-step solution or detailed reasoning with all working shown. This helps teachers verify answer correctness during review.",
  "diagram_needed": true or false,
  "diagram_description": "Detailed description if diagram needed, else null"
}}

Field Requirements:
- "question_text": String, the complete question
- "options": Array of 4 strings for MCQ (format: "A) text", "B) text", etc.), or null for other formats
- "correct_answer": String ("A", "B", "C", or "D") for MCQ, or null for other formats
- "explanation": String, detailed solution with all steps - essential for teacher verification during Human-in-Loop review
- "diagram_needed": Boolean, true if diagram required
- "diagram_description": String (detailed) or null

Generate a question that effectively assesses {bloom_level} level understanding of {topic} while maintaining CBSE standards and pedagogical quality.
"""


def build_few_shot_section(question_format: str, subject: str = "", class_level: int = 10) -> str:
    """Build the few-shot examples section based on format, subject, and class.

    Args:
        question_format: The question format (MCQ, VERY_SHORT, SHORT, LONG, etc.)
        subject: Subject name (e.g., "mathematics", "science")
        class_level: Class number (e.g., 10)

    Returns:
        Formatted few-shot examples section string
    """
    examples_by_format = get_examples_for_subject(subject, class_level)

    examples = []

    # Always include the requested format example
    primary_example = examples_by_format.get(question_format.upper())
    if primary_example:
        examples.append(primary_example)
    else:
        # Fallback to MCQ if format not found
        examples.append(examples_by_format.get("MCQ", ""))

    # Add one contrasting example to show variety
    if question_format.upper() != "MCQ":
        examples.append(examples_by_format.get("MCQ", ""))
    else:
        examples.append(examples_by_format.get("SHORT", examples_by_format.get("SA", "")))

    return "\n=== FEW-SHOT EXAMPLES ===\n" + "\n".join(examples)


def get_format_instructions(question_format: str) -> str:
    """Get format-specific instructions."""
    return FORMAT_INSTRUCTIONS.get(
        question_format.upper(),
        FORMAT_INSTRUCTIONS["MCQ"],  # Default
    )


def build_generation_prompt(
    chunks: list,
    blueprint_context: dict,
    include_examples: bool = True,
) -> str:
    """Build the complete generation prompt.

    Args:
        chunks: Retrieved textbook chunks
        blueprint_context: Blueprint specifications
        include_examples: Whether to include few-shot examples

    Returns:
        Complete prompt string
    """
    # Format chunks
    chunks_formatted = "\n\n".join(
        [
            f"CHUNK {i + 1} ({chunk.get('chunk_type', 'TEXT')}):\n{chunk.get('text', '')}"
            for i, chunk in enumerate(chunks)
        ]
    )

    # Build few-shot section
    if include_examples:
        few_shot_section = build_few_shot_section(
            question_format=blueprint_context.get("question_format", "MCQ"),
            subject=blueprint_context.get("subject", ""),
            class_level=blueprint_context.get("class_level", 10),
        )
    else:
        few_shot_section = ""

    # Get format instructions
    format_instructions = get_format_instructions(blueprint_context.get("question_format", "MCQ"))

    # Configure options/correct_answer fields based on format
    question_format = blueprint_context.get("question_format", "MCQ")
    if question_format == "MCQ":
        options_field = '"A) option1", "B) option2", "C) option3", "D) option4"'
        correct_answer_field = '"A" or "B" or "C" or "D"'
    else:
        options_field = "null"
        correct_answer_field = "null"

    # Fill in the template
    prompt = CBSE_QUESTION_GENERATION_PROMPT.format(
        class_level=blueprint_context.get("class_level", ""),
        subject=blueprint_context.get("subject", ""),
        chapter=blueprint_context.get("chapter", ""),
        topic=blueprint_context.get("topic", ""),
        section_title=blueprint_context.get("section_title", ""),
        question_format=question_format,
        marks=blueprint_context.get("marks", 1),
        difficulty=blueprint_context.get("difficulty", "medium"),
        bloom_level=blueprint_context.get("bloom_level", "UNDERSTAND"),
        nature=blueprint_context.get("nature", "NUMERICAL"),
        chunks_formatted=chunks_formatted,
        few_shot_section=few_shot_section,
        format_instructions=format_instructions,
        options_field=options_field,
        correct_answer_field=correct_answer_field,
    )

    return prompt


# Diagram detection prompt
DIAGRAM_DETECTION_PROMPT = """Analyze whether the following CBSE question requires a diagram for proper understanding and solving.

QUESTION: {question_text}

CONTEXT:
- Topic: {topic}
- Chapter: {chapter}
- Format: {format}

ANALYSIS CRITERIA:
1. Does the question mention geometric shapes (triangle, circle, quadrilateral, etc.)?
2. Is coordinate geometry or graphing involved?
3. Would a visual representation significantly aid understanding?
4. Is it a construction problem?
5. Does it involve statistical data visualization?
6. Are angles, lengths, or positions that need to be visualized?

INSTRUCTIONS:
Think step by step about whether a diagram is necessary. If yes, provide a detailed description of what should be drawn. If no, explain why not.

OUTPUT FORMAT (JSON ONLY):
{{
  "diagram_needed": true or false,
  "diagram_description": "Detailed description if true, else null",
  "diagram_type": "geometric/coordinate/construction/graphical/none",
  "reasoning": "Brief explanation of your decision"
}}

Respond with valid JSON only, no other text."""
