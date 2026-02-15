"""Prompt templates for LLM question generation.

Contains detailed prompts with few-shot examples for different question formats.
"""

# Few-shot examples by question format
MCQ_EXAMPLE = """
EXAMPLE 1 - MCQ (Multiple Choice Question):
Topic: Zeros of a Polynomial
Cognitive Level: REMEMBER
Difficulty: Easy
Marks: 1

Textbook Context:
A polynomial p(x) has zeros where p(x) = 0. For linear polynomial ax + b, zero is -b/a.

Generated Question:
{
  "question_text": "What is the zero of the polynomial p(x) = x - 3?",
  "options": ["A) 0", "B) 3", "C) -3", "D) 1"],
  "correct_answer": "B",
  "explanation": "To find the zero of a polynomial, set p(x) = 0. Therefore: x - 3 = 0 → x = 3. The zero is 3.",
  "diagram_needed": false,
  "diagram_description": null,
  "hints": ["Set the polynomial equal to zero", "Solve for x"],
  "prerequisites": ["Understanding polynomial zeros", "Basic equation solving"],
  "common_mistakes": ["Confusing zero with coefficient", "Sign errors"],
  "quality_score": 0.95
}
"""

VERY_SHORT_EXAMPLE = """
EXAMPLE 2 - VERY SHORT ANSWER:
Topic: Euclid's Division Algorithm
Cognitive Level: UNDERSTAND
Difficulty: Easy
Marks: 2

Textbook Context:
Euclid's division lemma states that for positive integers a and b, there exist unique integers q and r such that a = bq + r, where 0 ≤ r < b.

Generated Question:
{
  "question_text": "State Euclid's division lemma for positive integers.",
  "options": null,
  "correct_answer": null,
  "explanation": "Euclid's division lemma states that for any two positive integers a and b, there exist unique integers q and r such that a = bq + r, where 0 ≤ r < b. Here, a is the dividend, b is the divisor, q is the quotient, and r is the remainder.",
  "diagram_needed": false,
  "diagram_description": null,
  "hints": ["Recall the relationship between dividend, divisor, quotient, and remainder"],
  "prerequisites": ["Division concept", "Understanding of dividend and divisor"],
  "common_mistakes": ["Forgetting the condition 0 ≤ r < b", "Confusing quotient and remainder"],
  "quality_score": 0.92
}
"""

SHORT_EXAMPLE = """
EXAMPLE 3 - SHORT ANSWER:
Topic: Relationship between Zeroes and Coefficients
Cognitive Level: APPLY
Difficulty: Medium
Marks: 3

Textbook Context:
For quadratic polynomial ax² + bx + c with zeroes α and β:
Sum of zeroes: α + β = -b/a
Product of zeroes: αβ = c/a

Generated Question:
{
  "question_text": "If α and β are the zeroes of the polynomial x² - 5x + 6, find the value of α² + β² without finding the actual zeroes.",
  "options": null,
  "correct_answer": null,
  "explanation": "Given: x² - 5x + 6, comparing with ax² + bx + c, we get a=1, b=-5, c=6.\\nSum of zeroes: α + β = -b/a = -(-5)/1 = 5\\nProduct of zeroes: αβ = c/a = 6/1 = 6\\nUsing identity: α² + β² = (α + β)² - 2αβ\\n= (5)² - 2(6)\\n= 25 - 12\\n= 13",
  "diagram_needed": false,
  "diagram_description": null,
  "hints": ["Use the identity: α² + β² = (α+β)² - 2αβ", "First find sum and product of zeroes"],
  "prerequisites": ["Quadratic polynomial zeroes", "Algebraic identities"],
  "common_mistakes": ["Sign errors in the formula", "Calculating (α+β)² incorrectly", "Finding actual zeroes first (time consuming)"],
  "quality_score": 0.94
}
"""

LONG_EXAMPLE = """
EXAMPLE 4 - LONG ANSWER:
Topic: Pair of Linear Equations
Cognitive Level: ANALYSE
Difficulty: Hard
Marks: 5

Textbook Context:
A pair of linear equations in two variables can be solved using elimination method: make coefficients of one variable equal and eliminate it.

Generated Question:
{
  "question_text": "Solve the following pair of linear equations using elimination method and interpret the result: 2x + 3y = 12 and 4x + 6y = 20. What does this tell you about the lines represented by these equations?",
  "options": null,
  "correct_answer": null,
  "explanation": "Given equations:\\n2x + 3y = 12 ... (1)\\n4x + 6y = 20 ... (2)\\n\\nMultiply equation (1) by 2:\\n4x + 6y = 24 ... (3)\\n\\nSubtract equation (2) from (3):\\n(4x + 6y) - (4x + 6y) = 24 - 20\\n0 = 4\\n\\nThis is a contradiction (0 ≠ 4), which means the system has no solution.\\n\\nInterpretation: The lines represented by these equations are parallel and never intersect. This is because the ratios of coefficients are equal: a₁/a₂ = 2/4 = 1/2, b₁/b₂ = 3/6 = 1/2, but c₁/c₂ = 12/20 = 3/5. Since a₁/a₂ = b₁/b₂ ≠ c₁/c₂, the lines are parallel and inconsistent.",
  "diagram_needed": true,
  "diagram_description": "Two parallel lines on coordinate axes with positive slopes, labeled L1 and L2, showing they never intersect",
  "hints": ["Try to make coefficients equal by multiplication", "Check if you get a valid solution or contradiction", "Compare ratios a₁/a₂, b₁/b₂, and c₁/c₂"],
  "prerequisites": ["Elimination method", "Understanding of linear equations", "Ratio comparison"],
  "common_mistakes": ["Not checking the ratios after getting contradiction", "Calculation errors in multiplication", "Incorrect interpretation of no solution"],
  "quality_score": 0.96
}
"""

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
  "explanation": "Step-by-step solution or detailed reasoning",
  "diagram_needed": true or false,
  "diagram_description": "Detailed description if diagram needed, else null",
  "hints": ["Hint 1 for students", "Hint 2 for students"],
  "prerequisites": ["Knowledge point 1", "Knowledge point 2"],
  "common_mistakes": ["Common error 1", "Common error 2"],
  {quality_score_field}
}}

Field Requirements:
- "question_text": String, the complete question
- "options": Array of 4 strings for MCQ (format: "A) text", "B) text", etc.), or null for other formats
- "correct_answer": String ("A", "B", "C", or "D") for MCQ, or null for other formats
- "explanation": String, detailed solution with all steps
- "diagram_needed": Boolean, true if diagram required
- "diagram_description": String (detailed) or null
- "hints": Array of 2-3 helpful hints
- "prerequisites": Array of 2-3 required knowledge points
- "common_mistakes": Array of 2-3 typical student errors
{quality_score_field_desc}

Generate a question that effectively assesses {bloom_level} level understanding of {topic} while maintaining CBSE standards and pedagogical quality.
"""


def build_few_shot_section(question_format: str) -> str:
    """Build the few-shot examples section based on format."""
    examples = []

    # Always include the requested format example
    if question_format == "MCQ":
        examples.append(MCQ_EXAMPLE)
    elif question_format == "VERY_SHORT":
        examples.append(VERY_SHORT_EXAMPLE)
    elif question_format == "SHORT":
        examples.append(SHORT_EXAMPLE)
    elif question_format == "LONG":
        examples.append(LONG_EXAMPLE)
    else:
        # Default to MCQ if unknown
        examples.append(MCQ_EXAMPLE)

    # Add one contrasting example to show variety
    if question_format != "MCQ":
        examples.append(MCQ_EXAMPLE)
    else:
        examples.append(SHORT_EXAMPLE)

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
    include_quality_score: bool = True,
) -> str:
    """Build the complete generation prompt.

    Args:
        chunks: Retrieved textbook chunks
        blueprint_context: Blueprint specifications
        include_examples: Whether to include few-shot examples
        include_quality_score: Whether to request quality score

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
        few_shot_section = build_few_shot_section(blueprint_context.get("question_format", "MCQ"))
    else:
        few_shot_section = ""

    # Get format instructions
    format_instructions = get_format_instructions(blueprint_context.get("question_format", "MCQ"))

    # Configure quality score field
    if include_quality_score:
        quality_score_field = '"quality_score": 0.0-1.0,'
        quality_score_field_desc = (
            '- "quality_score": Number between 0.0-1.0 (self-assessment of quality)'
        )
    else:
        quality_score_field = ""
        quality_score_field_desc = ""

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
        class_level=blueprint_context.get("class_level", 10),
        subject=blueprint_context.get("subject", "Mathematics"),
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
        quality_score_field=quality_score_field,
        quality_score_field_desc=quality_score_field_desc,
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
