---
name: question-assembly
description: Assembles CBSE-compliant questions from search results. Use when creating final question objects from retrieved educational content.
metadata:
  version: "1.0"
  author: CBSE Question Paper Generator
---

# Question Assembly Skill

## Overview
This skill assembles complete CBSE question objects from search results and blueprint requirements. It handles question formatting, difficulty assessment, diagram detection, and quality validation.

> **NOTE:** This skill was previously designed to work with Tavily search results. It will be updated for Qdrant vector database results in the next phase.

## When to Use
Use this skill when you need to:
- Create final question objects from search results
- Format questions according to CBSE standards
- Generate question IDs and metadata
- Detect when diagrams are needed
- Apply difficulty and cognitive level tags

## Input Format

You will receive two inputs:

### 1. Search Results (from vector database)
```json
[
  {
    "question_text": "...",
    "metadata": {...},
    "similarity_score": 0.95
  }
]
```

> **NOTE:** Previous version used 15 items from Tavily web search. This will be replaced with Qdrant vector database results.

### 2. Blueprint Requirements
```json
{
  "class": 10,
  "subject": "Mathematics",
  "chapter": "Polynomials",
  "topic": "Zeros of a Polynomial",
  "format": "MCQ",
  "marks": 1,
  "difficulty": "easy",
  "nature": "NUMERICAL",
  "cognitive_level": "REMEMBER"
}
```

## Output Format

Return a complete question JSON object:

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
  "bloom_level": "remember",
  "nature": "NUMERICAL",
  "has_diagram": false,
  "diagram_type": null,
  "diagram_svg_base64": null,
  "diagram_description": null,
  "diagram_elements": null,
  "tags": ["polynomials", "zeros", "numerical", "lcm"]
}
```

## Question ID Format

Pattern: `{SUBJECT}-{CLASS}-{CHAPTER}-{FORMAT}-{NUMBER}`

### Subject Codes
- MAT: Mathematics
- SCI: Science
- ENG: English
- SST: Social Science

### Chapter Abbreviations (Mathematics Class 10)
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

### Format Abbreviations
- MCQ: MCQ
- VSQ: VERY_SHORT
- SA: SHORT
- LA: LONG
- CS: CASE_STUDY

### Example IDs
- `MATH-10-POL-MCQ-001`: Math Class 10, Polynomials, MCQ, #1
- `MATH-10-TRI-LA-005`: Math Class 10, Triangles, Long Answer, #5

## Diagram Detection

### Auto-Detect Diagram Needs
Analyze the question content for these keywords:

**Geometry (diagram_type: "geometric"):**
- triangle, circle, quadrilateral, polygon
- angle (∠), vertex, vertices, side
- radius, diameter, chord, tangent
- congruence, similarity, Pythagoras
- perpendicular, parallel, intersecting

**Coordinate Geometry (diagram_type: "coordinate"):**
- graph, plot, coordinate, axis
- point, line, slope, intercept
- distance, midpoint, quadrant
- x-coordinate, y-coordinate

**Trigonometry (diagram_type: "geometric"):**
- sin, cos, tan, cot, sec, cosec
- elevation, depression, height
- tower, shadow, ladder, pole
- angle of elevation/depression

**Statistics (diagram_type: "chart"):**
- histogram, bar chart, pie chart
- frequency, class interval, ogive
- data interpretation, graph

**When Diagram Detected:**
1. Set `has_diagram: true`
2. Set appropriate `diagram_type`
3. Create `diagram_description` (detailed text)
4. Define `diagram_elements` (structured data)
5. Generate diagram using `generate_diagram_tool`

### Diagram Workflow

The complete diagram workflow within question assembly:

1. **Analyze Question Content**
   - Parse the generated question text
   - Scan for diagram-related keywords (listed above)
   - Determine if visualization adds value

2. **Determine Diagram Type**
   - **geometric**: For geometry, trigonometry questions
   - **coordinate**: For graphs, plots, coordinate geometry
   - **chart**: For statistics, histograms, data representation
   - **formula**: For complex mathematical expressions

3. **Create Diagram Description**
   - Write detailed textual description of the diagram
   - Include all elements, labels, and measurements
   - Make it accessible for screen readers
   - Example: "Right-angled triangle ABC with right angle at vertex C. Side AC extends vertically for 6 cm, side BC extends horizontally for 8 cm."

4. **Define Diagram Elements**
   - Structure data for diagram generation
   - Include: shape type, points, sides, angles, coordinates
   - Example:
     ```json
     {
       "shape": "right_triangle",
       "points": ["A", "B", "C"],
       "sides": ["AC=6 cm", "BC=8 cm", "AB=?"],
       "angles": ["∠C=90°"]
     }
     ```

5. **Generate Diagram**
   - Call `generate_diagram_tool` with description and elements
   - Receive SVG base64 and file path
   - Store reference in question object

### Diagram Storage

- Diagrams are stored as separate SVG files (not embedded in JSON)
- Location: `src/cache/diagrams/`
- Each diagram has a unique key based on content hash
- Questions reference diagrams by key for reuse across papers
- Diagrams can be reused if same geometry is needed again

### Diagram Quality Standards

All diagrams must meet these standards:

- **Clarity**: Elements clearly visible and properly labeled
- **Accuracy**: Measurements and positions mathematically correct
- **Consistency**: Similar diagrams use consistent styling (colors, line thickness, fonts)
- **Accessibility**: Include descriptive alt-text for screen readers
- **Professional Quality**: Suitable for CBSE exam papers
- **Proper Sizing**: Large enough to be readable when printed

## Quality Standards

All questions must meet these CBSE standards:

### ✅ Required
- **Unambiguous**: Single correct interpretation
- **Calculator-free**: Numbers workable mentally
- **CBSE notation**: Standard mathematical notation
- **Realistic values**: Reasonable numerical values
- **Time-appropriate**: Fits exam duration

### ❌ Avoid
- Ambiguous wording
- Complex calculations requiring calculators
- Non-standard notation
- Unrealistic scenarios
- Excessively long questions for marks allocated

## Cognitive Level Mapping

Map `cognitive_level` to `bloom_level`:
- REMEMBER → "remember"
- UNDERSTAND → "understand"
- APPLY → "apply"
- ANALYSE → "analyze"
- EVALUATE → "evaluate"
- CREATE → "create"

## Format-Specific Requirements

### MCQ (Multiple Choice)
- Exactly 4 options (A, B, C, D)
- Format: "A) ...", "B) ...", etc.
- One clearly correct answer
- Distractors should be plausible

### VERY_SHORT (1-2 marks)
- Direct answer expected
- 1-2 sentences maximum
- No working required

### SHORT (3 marks)
- Brief working shown
- 3-5 steps
- Clear solution path

### LONG (5 marks)
- Detailed working required
- 5+ steps
- May include proof/derivation
- Method marks consideration

### CASE_STUDY (4 marks)
- Real-world scenario
- 2-4 sub-questions
- Data/paragraph provided
- Marks distributed across parts

## Process

Follow these steps:

1. **Analyze Search Results**
   - Review all 15 Tavily results
   - Extract best question concepts
   - Note common patterns

2. **Apply Requirements**
   - Match format (MCQ, SHORT, LONG, etc.)
   - Apply difficulty level
   - Target specific marks
   - Cover required topic

3. **Create Question Text**
   - Write clear, unambiguous question
   - Use CBSE-style language
   - Include all necessary context
   - Keep within time constraints

4. **Generate Metadata**
   - Create unique question_id
   - Set chapter and topic
   - Map cognitive_level to bloom_level
   - Assign nature and difficulty

5. **Create Options/Answers**
   - For MCQ: 4 options with 1 correct
   - For others: suggested answer
   - Ensure clarity

6. **Detect Diagram Needs**
   - Scan for geometry/coordinate/trig keywords
   - Set has_diagram flag
   - Define diagram_type if needed
   - Call generate_diagram_tool if required

7. **Add Tags**
   - Include chapter name
   - Include topic name
   - Add nature tag
   - Add relevant keywords

8. **Validate Output**
   - Check all required fields present
   - Verify question_id format
   - Ensure valid JSON
   - Confirm quality standards met

## Examples

### Example 1: MCQ Question

**Input Requirements:**
```json
{
  "class": 10,
  "subject": "Mathematics",
  "chapter": "Real Numbers",
  "topic": "LCM and HCF",
  "format": "MCQ",
  "marks": 1,
  "difficulty": "easy",
  "nature": "NUMERICAL",
  "cognitive_level": "REMEMBER"
}
```

**Output:**
```json
{
  "question_id": "MATH-10-REA-MCQ-001",
  "question_text": "The LCM of two numbers is 120 and their HCF is 8. If one number is 24, find the other number.",
  "chapter": "Real Numbers",
  "topic": "LCM and HCF",
  "question_format": "MCQ",
  "marks": 1,
  "options": ["A) 30", "B) 40", "C) 50", "D) 60"],
  "correct_answer": "B",
  "difficulty": "easy",
  "bloom_level": "remember",
  "nature": "NUMERICAL",
  "has_diagram": false,
  "diagram_type": null,
  "diagram_svg_base64": null,
  "diagram_description": null,
  "diagram_elements": null,
  "tags": ["real-numbers", "lcm", "hcf", "numerical", "formula"]
}
```

### Example 2: Long Answer with Diagram

**Input Requirements:**
```json
{
  "class": 10,
  "subject": "Mathematics",
  "chapter": "Triangles",
  "topic": "Pythagoras Theorem",
  "format": "LONG",
  "marks": 5,
  "difficulty": "medium",
  "nature": "PROOF",
  "cognitive_level": "UNDERSTAND"
}
```

**Output:**
```json
{
  "question_id": "MATH-10-TRI-LA-001",
  "question_text": "In right-angled triangle ABC, right-angled at C, prove that AB² = AC² + BC². Hence, find the length of the hypotenuse if AC = 6 cm and BC = 8 cm.",
  "chapter": "Triangles",
  "topic": "Pythagoras Theorem",
  "question_format": "LONG",
  "marks": 5,
  "options": null,
  "correct_answer": "10 cm",
  "difficulty": "medium",
  "bloom_level": "understand",
  "nature": "PROOF",
  "has_diagram": true,
  "diagram_type": "geometric",
  "diagram_svg_base64": "...",
  "diagram_description": "Right-angled triangle ABC with right angle at vertex C. Side AC is vertical (6 cm), side BC is horizontal (8 cm), and AB is the hypotenuse.",
  "diagram_elements": {
    "shape": "right_triangle",
    "points": ["A", "B", "C"],
    "sides": ["AC=6 cm", "BC=8 cm", "AB=?"],
    "angles": ["∠C=90°"]
  },
  "tags": ["triangles", "pythagoras", "proof", "right-angle", "geometric"]
}
```

## Additional Resources

See references/ directory for:
- CBSE standards and guidelines
- Question format templates
- Diagram pattern reference
