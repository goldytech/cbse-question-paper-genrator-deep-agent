---
name: mathematics
description: Domain knowledge reference for CBSE Class 10 standard Mathematics question generation.
metadata:
  version: "1.1.0"
  author: CBSE Question Paper Generator
---

# CBSE Class 10 Mathematics Domain Knowledge

## Overview
This skill provides comprehensive guidance for generating CBSE-compliant Class 10 Mathematics question papers from blueprints.

## Question Paper Generation Workflow

### Step 1: Discover Exam Blueprint

The exam blueprint can be:
- **Auto-discovered**: From `input/` folder (most recent JSON file)
- **Teacher-provided**: Explicit path provided (e.g., `input/blueprint_first_term_50.json`)

**Master Policy Blueprint**: Auto-discovered at `skills/cbse/class_10/mathematics/references/blueprint.json`

### Step 2: Validate Blueprint (CRITICAL)

**ALWAYS validate first** using blueprint-validator subagent:
```
task(name="blueprint-validator", 
     task="Validate exam blueprint at path: input/blueprint_first_term_50.json")
```

**Validation checks**:
- Schema version matches master policy blueprint
- Topics present under each chapter
- Question formats in whitelist
- Internal choice arithmetic (attempt ≤ provided)
- Section topic_focus in syllabus scope

**DO NOT PROCEED** if validation fails.

### Step 3: Generate Questions Using question-researcher

**For EACH question, invoke question-researcher with ALL applicable rules:**

```
task(name="question-researcher", 
     task="Format=MCQ, Chapter=Polynomials, Topic=Zeros of a Polynomial, Difficulty=easy, Nature=NUMERICAL, CognitiveLevel=REMEMBER")
```

**Required Parameters** (extract from blueprint):
- `Format`: From section `question_format` (MCQ, VERY_SHORT, SHORT, LONG, CASE_STUDY)
- `Chapter`: From `syllabus_scope.chapters[].chapter_name`
- `Topic`: From section `topic_focus[]` or chapter `topics[]`
- `Difficulty`: Based on difficulty distribution (easy/medium/hard)
- `Nature`: From section `allowed_question_natures[]` (NUMERICAL, PROOF, WORD_PROBLEM, REASONING, DERIVATION, DATA_INTERPRETATION)
- `CognitiveLevel`: From section `cognitive_level_hint[]` (REMEMBER, UNDERSTAND, APPLY, ANALYSE, EVALUATE, CREATE)

**Optional** (auto-detect if not specified):
- `has_diagram`: Set to `true` if question involves geometry, coordinate geometry, trigonometry, or statistics visualization

**Rules to Consider When Invoking**:
1. **Difficulty Distribution**: Follow 40/40/20 (easy/medium/hard) per section
2. **Question Nature**: Use only allowed natures from section's `allowed_question_natures`
3. **Cognitive Levels**: Target section's `cognitive_level_hint` distribution
4. **Diagram Generation**: Auto-detect based on question content (see Diagram Patterns section)

**What it returns**:
```json
{
  "rephrased_question": "Calculate the least common multiple of 15 and 20",
  "original_concept": "LCM calculation",
  "difficulty": "easy",
  "question_type": "MCQ",
  "suggested_answer": "60",
  "has_diagram": false,
  "sources_consulted": ["https://..."]
}
```

**If diagram is generated**:
```json
{
  "rephrased_question": "In triangle ABC with AB=5cm, BC=12cm, angle B=90°...",
  "original_concept": "Pythagoras theorem application",
  "difficulty": "medium",
  "question_type": "SHORT",
  "suggested_answer": "13 cm",
  "has_diagram": true,
  "diagram_type": "geometric",
  "diagram_svg_base64": "...",
  "diagram_description": "Right-angled triangle ABC...",
  "diagram_elements": {"shape": "right_triangle", "points": ["A", "B", "C"], ...},
  "sources_consulted": ["https://..."]
}
```

### Step 4: Create Final Question Object

From the rephrased template, create final question:

```json
{
  "question_id": "MATH-10-POL-MCQ-001",
  "question_text": "Calculate the least common multiple of 15 and 20",
  "chapter": "Polynomials",
  "topic": "Zeros of a Polynomial",
  "question_format": "MCQ",
  "marks": 1,
  "options": ["A) 40", "B) 60", "C) 80", "D) 100"],
  "correct_answer": "B",
  "difficulty": "easy",
  "bloom_level": "REMEMBER",
  "nature": "NUMERICAL",
  "has_diagram": false,
  "tags": ["polynomials", "zeros", "lcm"]
}
```

**Question ID Format**: `MATH-10-[CHAP]-[FORMAT]-[NUM]`
- `CHAP`: 3-letter abbreviation (REA, POL, LIN, QUAD, AP, COG, TRI, CIR, MEN, STA, PRO)
- `FORMAT`: MCQ, VSQ (Very Short), SA (Short), LA (Long), CS (Case Study)
- `NUM`: Sequential number starting from 001

### Step 5: Compile Full Paper

**Paper Structure**:
```json
{
  "paper_id": "MATH-10-FIRST-TERM-2024",
  "exam_metadata": {
    "class": 10,
    "subject": "Mathematics",
    "exam_type": "First Term",
    "total_marks": 40,
    "duration_minutes": 120
  },
  "sections": [
    {
      "section_id": "A",
      "title": "Multiple Choice Questions",
      "questions": [/* array of question objects */],
      "section_total": 10
    }
  ],
  "total_marks": 40,
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### Step 6: Validate Final Paper

**Validate generated paper** against original blueprint:
```
task(name="paper-validator", 
     task="Validate paper at output/preview_*.json against input/blueprint_first_term_50.json")
```

**Fix any validation issues** before presenting to teacher.

### Difficulty Distribution (40/40/20 Rule)

**Apply to EACH section**:
- **Easy (40%)**: Direct formula, single concept
- **Medium (40%)**: Multi-concept integration
- **Hard (20%)**: Complex analysis

**Examples**:
- 20 MCQs → 8 easy, 8 medium, 4 hard
- 10 questions → 4 easy, 4 medium, 2 hard

### Quality Standards

All questions must meet CBSE quality guidelines:
- ✅ Unambiguous wording
- ✅ Class-appropriate difficulty
- ✅ Calculator-free calculations
- ✅ Correct mathematical notation
- ✅ Realistic numerical values
- ✅ Time-appropriate (fits exam duration)

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

## Blueprint Validation Workflow

When generating papers, the blueprint_validator subagent validates exam blueprints against the master policy blueprint at `references/blueprint.json`.

### Schema Version Requirements

**Exam Blueprint Must Have:**
- `schema_version` matching the master policy blueprint version (required)
- `syllabus_scope.chapters` with `topics` arrays for each chapter
- Section definitions with `topic_focus` arrays

**Validation Checks:**

1. **Syllabus Scope Enforcement**:
   - Each chapter must have non-empty `topics` array
   - Topics must either be present explicitly OR be `["ALL_TOPICS"]`
   - If `topic_selection_required: true` in master blueprint, topics are mandatory

2. **Topic Scope Enforcement**:
   - If section has `topic_focus` array: Must be array type
   - Each topic in `topic_focus` must exist in `syllabus_scope.chapters[*].topics`
   - If chapter has `["ALL_TOPICS"]`: Any topic is accepted
   - If `topic_focus` missing or empty: No error (inherits global scope)

3. **Question Format Whitelist**:
   - All section `question_format` values must be in master's whitelist
   - Allowed formats: MCQ, MCQ_ASSERTION_REASON, VERY_SHORT, SHORT, LONG, CASE_STUDY

4. **Internal Choice Arithmetic**:
   - If `internal_choice.type` present, attempt must be ≤ provided
   - Supported types: ANY_N_OUT_OF_M, EITHER_OR

5. **Question Nature Balance**:
   - Section `allowed_question_natures` must be subset of master's whitelist
   - Allowed natures: NUMERICAL, PROOF, WORD_PROBLEM, REASONING, DERIVATION, DATA_INTERPRETATION

### Enforcement Modes

The master blueprint specifies `cognitive_levels.enforcement_mode` which controls ALL validation checks:

- **STRICT**: Fail validation if any check fails
- **ADVISORY**: Log warnings but continue (only advisory checks)
- **DISABLED**: Skip the check entirely

Example:
```json
{
  "cognitive_levels": {
    "enforcement_mode": "ADVISORY"
  }
}
```

---

## Mathematics Diagram Patterns (Class 10)

This section provides pattern definitions for generating diagrams for Class 10 Mathematics questions using drawsvg.

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

### drawsvg Pattern Examples

**Right-Angled Triangle Pattern**:
```python
import drawsvg as draw

d = draw.Drawing(300, 300, origin='center')
d.append(draw.Rectangle(-150, -150, 300, 300, fill='white'))

# Define points (adjusting for center origin)
A = (50, 80)    # Top vertex
B = (50, 0)     # Bottom-left (right angle)
C = (120, 0)    # Bottom-right

# Draw triangle sides
d.append(draw.Line(A[0], -A[1], B[0], -B[1], stroke='black', stroke_width=2))
d.append(draw.Line(B[0], -B[1], C[0], -C[1], stroke='black', stroke_width=2))
d.append(draw.Line(C[0], -C[1], A[0], -A[1], stroke='black', stroke_width=2))

# Add vertex labels
d.append(draw.Text("A", 16, A[0], -A[1]-20))
d.append(draw.Text("B", 16, B[0]-15, -B[1]))
d.append(draw.Text("C", 16, C[0]+10, -C[1]))

# Add right angle symbol
d.append(draw.Rectangle(B[0]+2, -B[1]-10, 8, 8, fill='none', stroke='black'))

# Add side labels
d.append(draw.Text("5 cm", 12, (A[0]+B[0])/2-20, -(A[1]+B[1])/2))
d.append(draw.Text("12 cm", 12, (B[0]+C[0])/2, -(B[1]+C[1])/2+20))

d.save_svg("output.svg")
```

**Coordinate System Pattern**:
```python
import drawsvg as draw

d = draw.Drawing(400, 300, origin='center')
d.append(draw.Rectangle(-200, -150, 400, 300, fill='white'))

# Draw axes
d.append(draw.Line(-180, 0, 180, 0, stroke='black', stroke_width=1))  # X-axis
d.append(draw.Line(0, -130, 0, 130, stroke='black', stroke_width=1))  # Y-axis

# Add axis labels
d.append(draw.Text("X", 14, 170, 20))
d.append(draw.Text("Y", 14, 15, -120))

# Plot points (example: A at 100,80 and B at 200,160)
A = (100, 80)
B = (200, 160)
d.append(draw.Circle(A[0], -A[1], 4, fill='blue'))
d.append(draw.Circle(B[0], -B[1], 4, fill='blue'))
d.append(draw.Text("A(2,3)", 12, A[0]+10, -A[1]))
d.append(draw.Text("B(5,7)", 12, B[0]+10, -B[1]))

# Connect points
d.append(draw.Line(A[0], -A[1], B[0], -B[1], stroke='red', stroke_width=1, stroke_dasharray='4,4'))

d.save_svg("output.svg")
```

**Circle with Tangent Pattern**:
```python
import drawsvg as draw

d = draw.Drawing(300, 300, origin='center')
d.append(draw.Rectangle(-150, -150, 300, 300, fill='white'))

# Circle center and radius
O = (0, 0)
r = 60

# Draw circle
d.append(draw.Circle(O[0], O[1], r, fill='none', stroke='black', stroke_width=2))
d.append(draw.Text("O", 16, O[0]-5, O[1]-r-10))

# Point of tangency (right side)
P = (r, 0)
d.append(draw.Circle(P[0], P[1], 4, fill='red'))
d.append(draw.Text("P", 16, P[0]+10, P[1]))

# Draw tangent line at P (vertical)
d.append(draw.Line(P[0], -100, P[0], 100, stroke='blue', stroke_width=1))
d.append(draw.Text("Tangent", 12, P[0]+10, -80, fill='blue'))

# Add radius OP
d.append(draw.Line(O[0], O[1], P[0], P[1], stroke='black', stroke_width=1, stroke_dasharray='4,4'))
d.append(draw.Text("r", 12, O[0]+r/2, O[1]+15))

d.save_svg("output.svg")
```

**Histogram Pattern**:
```python
import drawsvg as draw

d = draw.Drawing(400, 300, origin='center')
d.append(draw.Rectangle(-200, -150, 400, 300, fill='white'))

# Data: [(interval, frequency), ...]
data = [("0-10", 5), ("10-20", 12), ("20-30", 8)]
bar_width = 30
gap = 10
start_x = -150

# Find max frequency for scaling
max_freq = max(freq for _, freq in data)
scale = 200 / max_freq  # Scale to fit in height

# Draw axes
d.append(draw.Line(-180, 130, 180, 130, stroke='black', stroke_width=1))  # X-axis
d.append(draw.Line(-180, -130, -180, 130, stroke='black', stroke_width=1))  # Y-axis

# Draw bars
for i, (interval, freq) in enumerate(data):
    x = start_x + i * (bar_width + gap)
    height = freq * scale
    d.append(draw.Rectangle(x, 130-height, bar_width, height, fill='skyblue', stroke='black', stroke_width=1))
    d.append(draw.Text(interval, 10, x+bar_width/2, 145, text_anchor='middle'))
    d.append(draw.Text(str(freq), 10, x+bar_width/2, 130-height-5, text_anchor='middle'))

# Add labels
d.append(draw.Text("Class Interval", 12, 0, 160, text_anchor='middle'))
d.append(draw.Text("Frequency", 12, -195, 0, text_anchor='middle', transform='rotate(-90,-195,0)'))

d.save_svg("output.svg")
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

For complete quality standards, see `../common/QUALITY_GUIDELINES.md`.
