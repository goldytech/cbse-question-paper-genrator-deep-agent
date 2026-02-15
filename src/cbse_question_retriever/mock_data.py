"""Mock data generator for CBSE Question Retriever testing.

Creates realistic mock Qdrant data for Class 10 Mathematics.
"""

import json
import random
from typing import List, Dict, Any

# Sample content for each topic (simplified NCERT content)
TOPIC_CONTENT = {
    "Euclid's Division Algorithm": [
        (
            "THEORY",
            "Euclid's division algorithm is a technique to compute the Highest Common Factor (HCF) of two positive integers. It states that any positive integer 'a' can be divided by another positive integer 'b' in such a way that it leaves a remainder 'r' that is smaller than 'b'.",
        ),
        (
            "THEORY",
            "The algorithm is based on Euclid's division lemma which states that for any two positive integers a and b, there exist unique integers q and r such that a = bq + r, where 0 ≤ r < b.",
        ),
        (
            "WORKED_EXAMPLE",
            "Example 1: Find the HCF of 135 and 225 using Euclid's algorithm. Solution: 225 = 135 × 1 + 90, 135 = 90 × 1 + 45, 90 = 45 × 2 + 0. Therefore, HCF is 45.",
        ),
        (
            "WORKED_EXAMPLE",
            "Example 2: Show that any positive odd integer is of the form 6q + 1, or 6q + 3, or 6q + 5, where q is some integer. Solution: By Euclid's algorithm, a = 6q + r where r can be 0, 1, 2, 3, 4, or 5.",
        ),
        (
            "EXERCISE_PATTERN",
            "Exercise 1.1 - Question 1: Use Euclid's division algorithm to find the HCF of: (i) 135 and 225 (ii) 196 and 38220 (iii) 867 and 255",
        ),
    ],
    "Fundamental Theorem of Arithmetic": [
        (
            "THEORY",
            "The Fundamental Theorem of Arithmetic states that every composite number can be expressed (factorised) as a product of primes, and this factorisation is unique, apart from the order in which the prime factors occur.",
        ),
        (
            "THEORY",
            "A composite number is a positive integer which has at least one divisor other than 1 and itself. Every composite number can be written as the product of powers of primes.",
        ),
        (
            "WORKED_EXAMPLE",
            "Example: Find the LCM and HCF of 6 and 20 by prime factorization. Solution: 6 = 2¹ × 3¹, 20 = 2² × 5¹. HCF = 2¹ = 2, LCM = 2² × 3¹ × 5¹ = 60.",
        ),
        (
            "WORKED_EXAMPLE",
            "Example: Find the LCM of 96 and 404 by prime factorization. Solution: 96 = 2⁵ × 3, 404 = 2² × 101. LCM = 2⁵ × 3 × 101 = 9696.",
        ),
        (
            "EXERCISE_PATTERN",
            "Exercise 1.2 - Question 3: Find the LCM and HCF of the following pairs of integers and verify that LCM × HCF = product of the two numbers: (i) 26 and 91 (ii) 510 and 92",
        ),
    ],
    "HCF and LCM using Prime Factorisation": [
        (
            "THEORY",
            "The HCF of two numbers is the product of the smallest power of each common prime factor in the numbers. The LCM is the product of the greatest power of each prime factor involved in the numbers.",
        ),
        (
            "THEORY",
            "For any two positive integers a and b: HCF(a,b) × LCM(a,b) = a × b. This relationship is useful for finding one when the other is known.",
        ),
        (
            "WORKED_EXAMPLE",
            "Example: Given that HCF(306, 657) = 9, find LCM(306, 657). Solution: Using HCF × LCM = Product, we get LCM = (306 × 657) / 9 = 22338.",
        ),
        (
            "EXERCISE_PATTERN",
            "Exercise 1.2 - Question 4: Given that HCF(306, 657) = 9, find LCM(306, 657).",
        ),
    ],
    "Zeros of a Polynomial": [
        (
            "THEORY",
            "A zero of a polynomial p(x) is a number c such that p(c) = 0. Geometrically, zeros of a polynomial are the x-coordinates of the points where the graph of y = p(x) intersects the x-axis.",
        ),
        (
            "THEORY",
            "A polynomial of degree n has at most n zeros. For example, a linear polynomial has at most one zero, a quadratic polynomial has at most two zeros.",
        ),
        (
            "WORKED_EXAMPLE",
            "Example 1: Find the zero of the linear polynomial p(x) = 2x + 3. Solution: Set p(x) = 0, so 2x + 3 = 0, which gives x = -3/2.",
        ),
        (
            "WORKED_EXAMPLE",
            "Example 2: Verify whether 2 and 0 are zeroes of the polynomial x² - 2x. Solution: p(2) = 4 - 4 = 0 ✓, p(0) = 0 - 0 = 0 ✓. Both are zeroes.",
        ),
        (
            "EXERCISE_PATTERN",
            "Exercise 2.1 - Question 1: Find the number of zeroes of p(x) in each case: (i) Graph intersects x-axis at 3 points (ii) Graph touches x-axis at 1 point.",
        ),
    ],
    "Geometrical Meaning of Zeroes": [
        (
            "THEORY",
            "The geometrical meaning of the zeroes of a polynomial is the x-coordinates of the points where the graph of the polynomial intersects the x-axis. If the graph does not intersect the x-axis, the polynomial has no real zeroes.",
        ),
        (
            "WORKED_EXAMPLE",
            "Example: For the quadratic polynomial x² - 3x - 4, find the zeroes and verify geometrically. Solution: x² - 3x - 4 = 0 gives (x-4)(x+1) = 0, so x = 4 or x = -1.",
        ),
        (
            "EXERCISE_PATTERN",
            "Exercise 2.1 - Question 3: Find the zeroes of the following quadratic polynomials and verify the relationship between the zeroes and the coefficients: (i) x² - 2x - 8 (ii) 4s² - 4s + 1",
        ),
    ],
    "Relationship between Zeroes and Coefficients": [
        (
            "THEORY",
            "For a quadratic polynomial ax² + bx + c = 0 with zeroes α and β: Sum of zeroes α + β = -b/a, Product of zeroes α × β = c/a.",
        ),
        (
            "THEORY",
            "For a cubic polynomial ax³ + bx² + cx + d = 0 with zeroes α, β, γ: α + β + γ = -b/a, αβ + βγ + γα = c/a, αβγ = -d/a.",
        ),
        (
            "WORKED_EXAMPLE",
            "Example: Find a quadratic polynomial whose sum and product of zeroes are -3 and 2 respectively. Solution: x² - (sum)x + (product) = x² + 3x + 2.",
        ),
        (
            "WORKED_EXAMPLE",
            "Example: If α and β are zeroes of 2x² - 5x + 2, find α² + β². Solution: α + β = 5/2, αβ = 1, so α² + β² = (α+β)² - 2αβ = 25/4 - 2 = 17/4.",
        ),
        (
            "EXERCISE_PATTERN",
            "Exercise 2.2 - Question 2: Find a quadratic polynomial each with the given numbers as the sum and product of its zeroes respectively: (i) 1/4, -1 (ii) √2, 1/3",
        ),
    ],
    "Graphical Method": [
        (
            "THEORY",
            "Graphical method involves drawing the lines represented by the two equations on the same coordinate plane. The point of intersection gives the solution.",
        ),
        (
            "THEORY",
            "A pair of linear equations in two variables can be represented as: a₁x + b₁y + c₁ = 0 and a₂x + b₂y + c₂ = 0. The lines may intersect, be parallel, or coincide.",
        ),
        (
            "WORKED_EXAMPLE",
            "Example: Solve graphically: x + y = 5 and 2x - y = 4. Solution: Plot both lines. They intersect at (3, 2), which is the solution.",
        ),
        (
            "EXERCISE_PATTERN",
            "Exercise 3.1 - Question 2: On comparing the ratios a₁/a₂, b₁/b₂ and c₁/c₂, find out whether the lines representing the following pairs of linear equations intersect at a point, are parallel or coincident.",
        ),
    ],
    "Consistency of Linear Equations": [
        (
            "THEORY",
            "A system of linear equations is consistent if it has at least one solution. It is inconsistent if there is no solution (parallel lines).",
        ),
        (
            "THEORY",
            "For equations a₁x + b₁y + c₁ = 0 and a₂x + b₂y + c₂ = 0: (i) If a₁/a₂ ≠ b₁/b₂ → consistent with unique solution (ii) If a₁/a₂ = b₁/b₂ ≠ c₁/c₂ → inconsistent (iii) If a₁/a₂ = b₁/b₂ = c₁/c₂ → consistent with infinite solutions.",
        ),
        (
            "WORKED_EXAMPLE",
            "Example: Check consistency: 5x - 2y = 3 and 10x - 4y = 6. Solution: 5/10 = -2/-4 = 3/6 = 1/2. All ratios equal, so consistent with infinite solutions.",
        ),
        (
            "EXERCISE_PATTERN",
            "Exercise 3.2 - Question 3: On comparing the ratios a₁/a₂, b₁/b₂ and c₁/c₂ find out whether the following pair of linear equations are consistent, or inconsistent.",
        ),
    ],
    "Substitution Method": [
        (
            "THEORY",
            "Substitution method involves solving one equation for one variable and substituting this expression into the other equation. This reduces the system to a single equation in one variable.",
        ),
        (
            "WORKED_EXAMPLE",
            "Example: Solve by substitution: x + y = 14 and x - y = 4. Solution: From first equation, y = 14 - x. Substitute in second: x - (14-x) = 4 → 2x = 18 → x = 9. Then y = 5.",
        ),
        (
            "WORKED_EXAMPLE",
            "Example: Solve by substitution: s - t = 3 and s/3 + t/2 = 6. Solution: s = t + 3. Substitute: (t+3)/3 + t/2 = 6 → (2t+6+3t)/6 = 6 → 5t+6 = 36 → t = 6, s = 9.",
        ),
        (
            "EXERCISE_PATTERN",
            "Exercise 3.3 - Question 1: Solve the following pair of linear equations by the substitution method: (i) x + y = 14, x - y = 4 (ii) s - t = 3, s/3 + t/2 = 6.",
        ),
    ],
    "Elimination Method": [
        (
            "THEORY",
            "Elimination method involves multiplying equations by suitable numbers so that coefficients of one variable become equal (or negatives), then adding or subtracting to eliminate that variable.",
        ),
        (
            "WORKED_EXAMPLE",
            "Example: Solve by elimination: x + y = 5 and 2x - 3y = 4. Solution: Multiply first by 3: 3x + 3y = 15. Add to second: 5x = 19 → x = 19/5. Then y = 6/5.",
        ),
        (
            "WORKED_EXAMPLE",
            "Example: Solve: 3x + 4y = 17 and 6x + 8y = 34. Solution: Multiply first by 2: 6x + 8y = 34, which equals second equation. Infinitely many solutions.",
        ),
        (
            "EXERCISE_PATTERN",
            "Exercise 3.4 - Question 1: Solve the following pair of linear equations by the elimination method: (i) x + y = 5 and 2x - 3y = 4 (ii) 3x + 4y = 17 and 6x - 8y = 34.",
        ),
    ],
}


def generate_random_vector(dimensions: int = 3072) -> List[float]:
    """Generate a random vector for mock embeddings."""
    return [random.uniform(-1, 1) for _ in range(dimensions)]


def create_mock_chunk(
    chunk_id: str,
    chapter: str,
    section: str,
    topic: str,
    chunk_type: str,
    text: str,
    page: int,
) -> Dict[str, Any]:
    """Create a single mock chunk."""
    return {
        "id": chunk_id,
        "vector": generate_random_vector(),
        "payload": {
            "text": text,
            "chapter": chapter,
            "section": section,
            "topic": topic,
            "chunk_type": chunk_type,
            "page_start": page,
            "page_end": page + 1,
        },
    }


def generate_mock_data() -> Dict[str, Any]:
    """Generate complete mock data for Class 10 Mathematics."""
    chunks = []
    chunk_counter = 1

    # Chapter mapping
    chapters = {
        "Euclid's Division Algorithm": ("Real Numbers", "1.1"),
        "Fundamental Theorem of Arithmetic": ("Real Numbers", "1.2"),
        "HCF and LCM using Prime Factorisation": ("Real Numbers", "1.2"),
        "Zeros of a Polynomial": ("Polynomials", "2.1"),
        "Geometrical Meaning of Zeroes": ("Polynomials", "2.1"),
        "Relationship between Zeroes and Coefficients": ("Polynomials", "2.2"),
        "Graphical Method": ("Pair of Linear Equations in Two Variables", "3.1"),
        "Consistency of Linear Equations": ("Pair of Linear Equations in Two Variables", "3.2"),
        "Substitution Method": ("Pair of Linear Equations in Two Variables", "3.3"),
        "Elimination Method": ("Pair of Linear Equations in Two Variables", "3.4"),
    }

    for topic, content_list in TOPIC_CONTENT.items():
        chapter, section = chapters[topic]

        for i, (chunk_type, text) in enumerate(content_list):
            chunk_id = f"chunk-{chunk_counter:04d}"
            page = 20 + chunk_counter  # Mock page numbers

            chunk = create_mock_chunk(
                chunk_id=chunk_id,
                chapter=chapter,
                section=section,
                topic=topic,
                chunk_type=chunk_type,
                text=text,
                page=page,
            )
            chunks.append(chunk)
            chunk_counter += 1

    return {
        "collection": "mathematics_10",
        "description": "Mock Qdrant data for Class 10 Mathematics",
        "total_chunks": len(chunks),
        "chapters": ["Real Numbers", "Polynomials", "Pair of Linear Equations in Two Variables"],
        "topics": list(TOPIC_CONTENT.keys()),
        "chunks": chunks,
    }


def save_mock_data(filepath: str = "tests/fixtures/mock_qdrant_data.json") -> None:
    """Generate and save mock data to file."""
    data = generate_mock_data()

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Mock data saved to {filepath}")
    print(f"Total chunks: {data['total_chunks']}")
    print(f"Chapters: {', '.join(data['chapters'])}")
    print(f"Topics: {len(data['topics'])}")


if __name__ == "__main__":
    save_mock_data()
