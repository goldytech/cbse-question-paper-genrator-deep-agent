"""Few-shot examples for CBSE Class 10 Mathematics.

These examples demonstrate high-quality question generation for board exam preparation.
Optimized for CBSE exam paper generation - streamlined schema for teacher review.
"""

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
  "explanation": "To find the zero of a polynomial, set p(x) = 0. Therefore: x - 3 = 0 → x = 3. The zero is 3. This helps teachers verify that B is the correct answer without manual calculation.",
  "diagram_needed": false,
  "diagram_description": null
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
  "explanation": "Euclid's division lemma states that for any two positive integers a and b, there exist unique integers q and r such that a = bq + r, where 0 ≤ r < b. Here, a is the dividend, b is the divisor, q is the quotient, and r is the remainder. Teachers can verify the student's answer against this explanation during review.",
  "diagram_needed": false,
  "diagram_description": null
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
  "diagram_description": null
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
  "diagram_description": "Two parallel lines on coordinate axes with positive slopes, labeled L1 and L2, showing they never intersect"
}
"""


def get_class_10_examples() -> dict:
    """Return Class 10 Mathematics few-shot examples.

    Returns:
        Dictionary with examples by format.
    """
    return {
        "MCQ": MCQ_EXAMPLE,
        "VERY_SHORT": VERY_SHORT_EXAMPLE,
        "VSA": VERY_SHORT_EXAMPLE,
        "SHORT": SHORT_EXAMPLE,
        "SA": SHORT_EXAMPLE,
        "LONG": LONG_EXAMPLE,
        "LA": LONG_EXAMPLE,
        "CASE_STUDY": LONG_EXAMPLE,
    }
