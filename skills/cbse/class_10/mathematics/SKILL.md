---
name: class-10-mathematics
description: Domain knowledge reference for CBSE Class 10 Mathematics question generation. Provides links to external reference files for chapters, topics, formulas, and question patterns.
skill_type: domain_knowledge
version: 1.0.0
author: CBSE Question Paper Generator
dependencies:
  - ../common/QUESTION_FORMATS.json
  - ../common/QUESTION_PAPER_FORMAT.json
  - ../common/DIFFICULTY_DISTRIBUTION.md
  - ../common/QUALITY_GUIDELINES.md
---

# CBSE Class 10 Mathematics Domain Knowledge

## Overview
This skill provides access to Class 10 Mathematics question generation resources. For detailed chapter topics, formulas, and question patterns, see the external reference files listed below.

## Quick Reference Paths

**For Format Specifications:**
- `../common/QUESTION_FORMATS.json` - Question object structure
- `../common/QUESTION_PAPER_FORMAT.json` - Output paper format

**For Quality Standards:**
- `../common/DIFFICULTY_DISTRIBUTION.md` - 40/40/20 distribution guidelines
- `../common/QUALITY_GUIDELINES.md` - Quality checklist and standards

**For Class-Specific Procedures:**
- `references/BLUEPRINT_REFERENCE.md` - Blueprint interpretation
- `references/GENERATION_WORKFLOW.md` - Format-specific algorithms

**For Helper Scripts:**
- `scripts/difficulty_calculator.py` - Distribution calculator
- `scripts/validators.py` - Validation helpers

## Question Generation Support

When generating questions for Class 10 Mathematics, use the **question-researcher** subagent to get high-quality question templates.

### How to Use question-researcher Subagent

**Purpose**: Searches internet for CBSE question examples and returns a rephrased template

**When to use**: For EACH question you need to generate

**Invocation**:
```
task(name="question-researcher", 
     task="Format=MCQ, Chapter=Real Numbers, Topic=LCM HCF, Difficulty=easy")
```

**What it returns**:
```json
{
  "rephrased_question": "Calculate the least common multiple of 15 and 20",
  "original_concept": "LCM calculation",
  "difficulty": "easy",
  "question_type": "MCQ",
  "suggested_answer": "60",
  "sources_consulted": ["https://..."]
}
```

**How to use the result**:
1. Take the `rephrased_question` as your template
2. Adapt it to match exact blueprint requirements
3. Add proper question_id, options (for MCQ), and other metadata
4. Ensure it follows the question ID format: `MATH-10-[CHAP]-[FORMAT]-[NUM]`

**Example workflow**:
1. Determine you need an MCQ for Real Numbers chapter, LCM topic, easy difficulty
2. Call question-researcher subagent with those parameters
3. Receive rephrased template: "Calculate the least common multiple of 15 and 20"
4. Create final question:
   - Assign ID: MATH-10-REA-MCQ-001
   - Add options: ["A) 40", "B) 60", "C) 80", "D) 100"]
   - Set correct_answer: "B"
   - Add metadata (chapter, topic, marks, difficulty, bloom_level)

⚠️ **Note**: For blueprint validation and final paper validation, use the appropriate subagents as described in AGENTS.md.

## Chapter Abbreviations for Question IDs

- REA: Real Numbers
- POL: Polynomials
- LIN: Linear Equations
- QUAD: Quadratic Equations
- AP: Arithmetic Progressions
- COG: Coordinate Geometry
- TRI: Triangles
- CIR: Circles
- MEN: Mensuration
- STA: Statistics
- PRO: Probability

Question ID Format: `MATH-10-[CHAP]-[FORMAT]-[NUM]`
Example: `MATH-10-REA-MCQ-001`, `MATH-10-TRI-LA-002`

## Mathematics Diagram Patterns (Class 10)

This section provides pattern definitions for generating diagrams for Class 10 Mathematics questions using geometrySVG.

### Diagram Types by Chapter

**Triangles (TRI)**
- Pythagoras theorem problems
- Similarity and congruence
- Angle properties
- Construction problems
- Required elements: vertices (A, B, C), side labels, angle measures

**Coordinate Geometry (COG)**
- Distance formula
- Section formula
- Graph plotting
- Linear equations
- Required elements: axes, coordinates of points, plot labels

**Circles (CIR)**
- Tangent-chord theorem
- Angle in a segment
- Chord properties
- Required elements: center (O), radius, chords, tangents

**Statistics (STA)**
- Histograms for grouped data
- Bar charts for categorical data
- Pie charts for percentage distribution
- Required elements: axes, labels, data values

### geometrySVG Pattern Examples

**Right-Angled Triangle Pattern**:
```python
from geometrySVG import SVGCanvas

canvas = SVGCanvas(300, 300, cart_coords=True)
canvas.add_point(50, 80, "A")   # Top vertex
canvas.add_point(50, 0, "B")    # Bottom-left (right angle)
canvas.add_point(120, 0, "C")   # Bottom-right
canvas.add_polygon("ABC", name="triangle", fill="none", stroke="black")
canvas.add_angles(text=["90°", "a", "b"], fill="blue")
canvas.to_svg("output.svg")
```

**Coordinate System Pattern**:
```python
canvas = SVGCanvas(400, 300, cart_coords=True)
canvas.add_axes(length=(350, 250))  # X and Y axes
canvas.add_point(100, 80, "A")     # Plot point A
canvas.add_point(200, 160, "B")    # Plot point B
canvas.add_line("AB")              # Connect A and B
canvas.to_svg("output.svg")
```

**Circle with Tangent Pattern**:
```python
canvas = SVGCanvas(300, 300, cart_coords=True)
canvas.add_point(150, 150, "O")    # Center
canvas.add_circle("O", 60, name="circle", fill="none", stroke="black")
canvas.add_point(210, 150, "P")   # Point of tangency
canvas.add_tangent("P")            # Tangent at P
canvas.to_svg("output.svg")
```

**Histogram Pattern**:
```python
canvas = SVGCanvas(400, 300, cart_coords=True)
canvas.add_axes(length=(350, 250))
canvas.add_bar_chart([
    ("0-10", 5),
    ("10-20", 12),
    ("20-30", 8)
], bar_width=30)
canvas.to_svg("output.svg")
```

### Diagram-Specific Question Examples

**Example 1: Triangle with Pythagoras**
```
Question: "In a right-angled triangle ABC, AB = 5 cm, BC = 12 cm, and ∠B = 90°. Find AC."
Diagram Type: geometric
Elements:
  - Points: A(50, 80), B(50, 0), C(120, 0)
  - Right angle at B
  - Labels: AB=5, BC=12, AC=?
Description: "Right-angled triangle ABC with vertices A(top), B(bottom-left), C(bottom-right). AB vertical (5 cm), BC horizontal (12 cm). AC hypotenuse. Right angle symbol at B."
```

**Example 2: Distance Between Points**
```
Question: "Find the distance between points A(2, 3) and B(5, 7)."
Diagram Type: coordinate
Elements:
  - Coordinate system (0-6 on both axes)
  - Points: A(2, 3), B(5, 7)
  - Line segment AB
Description: "Cartesian coordinate system with origin (0,0). Point A at (2, 3), point B at (5, 7). Line segment connecting A and B."
```

**Example 3: Circle Theorem**
```
Question: "Prove that the angle in a semicircle is a right angle."
Diagram Type: geometric
Elements:
  - Circle with center O, radius r
  - Points A, B, C on circumference (C is top)
  - AB is diameter
Description: "Circle with center O and points A, B, C on circumference. AB is diameter. C at top of circle. Angle ACB marked as right angle."
```

### Quality Checkpoints

For each generated diagram, verify:
- ✅ All points labeled (A, B, C...)
- ✅ All measurements shown where given
- ✅ Angles marked with arc symbol where needed
- ✅ Right angle symbol (□) for 90°
- ✅ Consistent font size for labels
- ✅ Clear contrast (black strokes on white background)
- ✅ Adequate spacing (no overlap)

---

## Math Notation

Fractions: numerator/denominator or \frac{numerator}{denominator}
Powers: x^2 or Unicode x²
Roots: \sqrt{x} or Unicode √x
Greek letters: π, θ, Δ, Σ (Unicode preferred)
Sets: { } notation
Angles: ° symbol
Degree to radian conversions (π rad = 180°)

For complete quality standards and difficulty distribution, see `../common/QUALITY_GUIDELINES.md` and `../common/DIFFICULTY_DISTRIBUTION.md`.
