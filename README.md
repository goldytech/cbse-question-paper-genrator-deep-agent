# CBSE Question Paper Generator

An intelligent agent system for generating CBSE (Central Board of Secondary Education) question papers from JSON blueprints using Deep Agents framework with subagent delegation, live streaming, and human-in-the-loop approval. Includes **automatic diagram generation** and **DOCX export** capabilities.

## Overview

This system generates high-quality, CBSE-compliant question papers through an intelligent workflow that combines AI generation with teacher oversight. It uses a multi-agent architecture where specialized subagents handle validation, research, verification, diagram generation, and DOCX export while the main agent coordinates the process.

## Key Features

### 🤖 Multi-Agent Architecture
- **Main Agent**: Orchestrates the workflow, coordinates subagents
- **input-file-locator**: Locates and validates teacher's input blueprint JSON
- **blueprint-validator**: Validates blueprint against master policy blueprints (two-blueprint validation)
- **cbse-question-retriever**: **NEW** - Two-tier system: retrieves chunks from Qdrant vector DB, then generates questions using gpt-5-mini
- **question-assembler**: Assembles and formats final questions
- **paper-validator**: Validates final paper against blueprint
- **docx-generator**: Generates professional DOCX documents with embedded images

### 🎯 Intelligent Question Generation
- **Retrieves content from Qdrant vector database**: Stores CBSE textbook chunks with embeddings (text-embedding-3-large)
- **Generates questions using gpt-5-mini**: Detailed prompting with few-shot examples, Bloom's taxonomy, and CBSE standards
- **Hybrid search**: Combines vector similarity with metadata filters (chapter, topic)
- **Fuzzy topic matching**: Handles variations in topic names using rapidfuzz
- Maintains CBSE difficulty distribution (40% easy, 40% medium, 20% hard)
- Follows official CBSE question formats and standards
- **🎨 Auto-generates diagrams** for geometry, coordinate geometry, trigonometry, and statistics questions

### 📄 Automatic DOCX Export
- **Instant DOCX generation** after teacher approval
- **CBSE-standard formatting** with headers, sections, footers
- **Embedded PNG images** from generated SVG diagrams
- Professional document output ready for printing

### 👨‍🏫 Teacher Approval Workflow (HITL)
- **Human-in-the-Loop**: Teachers review formatted question paper before saving
- **Visual Preview**: Shows clean text format (not raw JSON)
- **Diagram Preview**: Shows structured diagram descriptions for terminal review
- **Feedback Loop**: If rejected, captures specific feedback and reworks accordingly
- **Multiple Attempts**: Up to 5 rework iterations with teacher guidance
- **DOCX Export**: Automatic after approval with embedded diagrams

### 📝 Smart Filename Management
- Unique filenames prevent overwrites: `mathematics_class10_first_term_20260201_143052_a7f3d.json`
- Extracts exam type from blueprint filename automatically
- Supports multiple teachers/users simultaneously
- Human-readable format with timestamp and subject info

### 📚 Progressive Disclosure Skills
- Dynamically loads domain knowledge based on class/subject
- Skills for CBSE Class 10 Mathematics (chapters, topics, patterns, diagram generation)
- Common quality standards and question formats
- Extensible for other classes and subjects

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Agent (Orchestrator)                │
│  • Coordinates workflow                                     │
│  • Delegates to subagents                                   │
│  • Manages HITL approval                                    │
│  • Compiles final paper                                     │
└──────────────────────┬──────────────────────────────────────┘
                        │
    ┌───────────────────┼───────────────────┐
    │                   │                   │
┌───▼────┐ ┌───────────▼────────┐ ┌───────▼───────┐ ┌────▼──────┐
│ Input  │ │  Blueprint         │ │    Paper      │ │   DOCX    │
│ File   │ │  Validator         │ │   Validator   │ │ Generator │
│Locator │ │  Subagent          │ │   Subagent    │ │ Subagent  │
└────────┘ └────────────────────┘ └───────────────┘ └───────────┘
                        │
            ┌───────────▼───────────┐
            │  CBSE Question        │
            │  Retriever Subagent   │
            │  (Two-Tier System)    │
            └───────────┬───────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────┐          ┌──────────▼──────────┐
│  Retrieval     │          │   Generation        │
│  (Qdrant DB)   │          │   (gpt-5-mini)      │
│                │          │                     │
│ • Vector Search│          │ • Few-shot Prompts  │
│ • Hybrid Query │          │ • Diagram Detection │
│ • Chunk Mixing │          │ • Quality Check     │
└────────────────┘          └─────────────────────┘
```

## Workflow

### Complete Generation Flow

```
1. Teacher Input
   ↓
2. Locate Blueprint (input-file-locator subagent)
   └─ Auto-discovers from input/classes/{class}/{subject}/
   └─ Returns: file_path, class, subject
   ↓
3. Validate Blueprint (blueprint-validator subagent)
   └─ Two-blueprint validation: exam + master policy
   └─ Checks: schema, formats, internal choice, syllabus scope
   ↓
4. For Each Question Needed:
    
    TIER 1 - RETRIEVE CHUNKS (generate_question_tool):
    a. Query Qdrant vector database
       └─ Collection: {subject}_{class} (e.g., "mathematics_10")
       └─ Hybrid search: vector similarity + metadata filters
       └─ Fuzzy topic matching with rapidfuzz
       └─ Returns: 10 chunks (THEORY/WORKED_EXAMPLE/EXERCISE)
    
    TIER 2 - GENERATE QUESTION (generate_llm_question_tool):
    b. Build detailed prompt with:
       └─ Few-shot examples (MCQ, SHORT, LONG formats)
       └─ Bloom's taxonomy cognitive level instructions
       └─ CBSE quality standards and pedagogical guidelines
    c. Call gpt-5-mini (temperature=0.3) via LangChain
    d. Parse JSON response with validation
    e. Detect diagram need using LLM
    f. If needed: Generate diagram using generate_diagram_tool
       └─ Creates SVG with drawsvg
       └─ Stores base64 for JSON portability
       └─ Adds structured diagram description
    g. Return complete question with:
       └─ Options, correct_answer, explanation, hints
       └─ Prerequisites, common_mistakes, quality_score
    ↓
5. Compile Paper
   ↓
6. Validate Paper (paper-validator subagent)
   ↓
7. HITL: Show Formatted Preview to Teacher (with diagram descriptions)
   ↓
8. Teacher Decision:
    ├─ YES → Generate DOCX (docx-generator subagent)
    │    ├─ Convert SVG → PNG (cairosvg)
    │    ├─ Embed images in DOCX (python-docx)
    │    └─ Save to output/docx/
    └─ NO  → Capture feedback → Go to step 4 (rework)
    ↓
9. Complete
```

### Human-in-the-Loop (HITL) Details

When the question paper is ready:

1. **Formatted Preview**: Shows clean text format (not JSON)
   ```
   CBSE CLASS 10 MATHEMATICS
   FIRST TERM EXAMINATION
   Total Marks: 50 | Duration: 120 minutes
   
   SECTION A: MULTIPLE CHOICE QUESTIONS
   1. Calculate the LCM of 15 and 20. (1 mark)
       [Difficulty: easy] | [Chapter: Real Numbers]
       A) 40    B) 60    C) 80    D) 100
       [Correct: B]
   ...
   ```

2. **Diagram Preview**: Shows structured diagram descriptions (text format, not images)

   ```
   Question 1: In right-angled triangle ABC, AB = 5 cm, BC = 12 cm, and ∠B = 90°. Find AC. (5 marks)
   
   📊 DIAGRAM PREVIEW:
   Type: geometric
   Description: Right-angled triangle ABC with right angle at vertex B. Side AB extends vertically (5 cm), side BC extends horizontally (12 cm). Hypotenuse AC connects A to C diagonally.
   Points: A, B, C
   Sides: AB = 5 cm, BC = 12 cm, AC = ?
   Angles: ∠B = 90°
   ⊙ Full-quality SVG will be embedded in DOCX export
   ```

3. **Teacher Approval**: Prompt asks "Approve this question paper? (yes/no)"

4. **DOCX Generation** (if approved):
   ```
   ▶ Subagent: docx-generator
     Task: Generate DOCX from: output/paper.json
     ✓ docx-generator complete
   
   ▶ Writing: mathematics_class10_first_term_YYYYMMDD_HHMMSS_id.docx
   ✓ DOCX generated: output/docx/mathematics_class10_first_term_YYYYMMDD_HHMMSS_id.docx
   
   Generated: 20 questions total
   Diagrams embedded: 8
   ```

5. **If Rejected**:
    - Teacher provides specific feedback (e.g., "Change MCQ 3 to Polynomials", "Fix triangle diagram for LA question 2")
    - Agent identifies only the affected questions/diagrams
    - Uses question-researcher to get new templates/diagrams
    - Regenerates ONLY the requested changes
    - Presents updated paper for re-approval
    - Up to 5 attempts, then asks "Force save or cancel?"

## Installation & Setup

### Prerequisites
- Python 3.11 or later
- uv package manager (recommended)
- OpenAI API key
- Qdrant vector database (running locally or accessible endpoint)
- **All Python package dependencies are pre-installed** (no subprocess installation needed)
  - `qdrant-client>=1.12.0` - For vector database operations
  - `rapidfuzz>=3.0.0` - For fuzzy topic matching
  - `pydantic-settings>=2.0.0` - For configuration management
  - `drawsvg>=2.4.1` - For diagram generation
  - `cairosvg>=2.7.0` - For SVG to PNG conversion
  - `python-docx>=1.2.0` - For DOCX export
  - `langchain-openai>=0.3.0` - For gpt-5-mini integration

### Step 1: Clone Repository
```bash
git clone https://github.com/goldytech/cbse-question-paper-genrator-deep-agent.git
cd cbse-question-paper-genrator-deep-agent
```

### Step 2: Install Dependencies
```bash
# Using uv (recommended)
uv sync

# Note: All dependencies are pre-installed, no subprocess installation needed
```

### Step 3: Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
OPENAI_API_KEY=sk-your-key-here
TAVILY_API_KEY=tvly-your-key-here  # Optional but recommended
```

### Step 4: Prepare Input Folder
```bash
# Create input directory structure
mkdir -p input/classes/10/mathematics

# Add your blueprint JSON file(s)
# Example: input/classes/10/mathematics/blueprint.json
# Teacher files: input/classes/10/mathematics/input_first_term_50.json
```

## Getting Started

### Quick Start - Auto Discovery

If you have one blueprint file in `input/classes/` folder structure:

```bash
python run.py "Generate Class 10 Mathematics question paper"
```

The agent will:
1. Auto-discover the most recent `.json` file in `input/classes/*/*/`
2. Prioritizes teacher files (`input_*.json`) over master blueprints (`blueprint.json`)
3. Load and validate the blueprint
3. Generate questions using subagents
4. **Auto-detect and generate diagrams** for geometry/coordinate questions
5. Show formatted preview (text + diagram descriptions) for approval
6. Teacher approves → **Generate DOCX automatically with embedded images**

### Specify Blueprint Explicitly

```bash
python run.py "Generate paper using input/classes/10/mathematics/blueprint.json"
```

### Example Session

```bash
$ python run.py "Generate Class 10 Mathematics first term paper"

              Blueprint Configuration
┌──────────┬─────────────────────────────────────────────────┐
│ File     │ input/classes/10/mathematics/blueprint.json     │
│ Location │ input/classes/10/mathematics/ (auto-discovered) │
└──────────┴─────────────────────────────────────────────────┘

Creating CBSE Question Paper Generator agent...
Agent created successfully!

CBSE Question Paper Generator
Task: Generate a CBSE question paper using blueprint input/classes/10/mathematics/blueprint.json...
Using Live Streaming with Human-in-the-Loop...

✓ Loaded blueprint: input/classes/10/mathematics/blueprint.json
Will save to: output/mathematics_class10_first_term_20260201_143052_a7f3d.json

  ▶ Subagent: blueprint-validator
    Task: Validate blueprint...
    ✓ blueprint-validator complete

  ▶ Subagent: question-researcher
    Task: Format=MCQ, Chapter=Real Numbers, Topic=LCM HCF, Difficulty=easy
    ✓ question-researcher complete
    [Generated diagram triangle geometry]

  ... (more subagent calls with diagram generation) ...

  ▶ Writing: mathematics_class10_first_term_20260201_143052_a7f3d.json

📄 Question Paper Ready for Review
┌─────────────────────────────────────────────────────────────┐
│ CBSE CLASS 10 MATHEMATICS                                   │
│ FIRST TERM EXAMINATION                                      │
│ Total Marks: 50 | Duration: 120 minutes                     │
│                                                             │
│ SECTION A: MULTIPLE CHOICE QUESTIONS                        │
│ 1. Calculate the LCM of 15 and 20. (1 mark)                │
│    [Difficulty: easy] | [Chapter: Real Numbers]             │
│    A) 40    B) 60    C) 80    D) 100                       │
│    [Correct Answer: B]                                      │
│ ...                                                        │
│                                                             │
│ SECTION B: SHORT ANSWER QUESTIONS (5 × 3 = 15 marks)           │
│                                                             │
│ 1. In a right-angled triangle ABC, AB = 5 cm, BC = 12 cm, and ∠B = 90°. Find AC. (3 marks)
│    [Difficulty: medium] | [Chapter: Triangles] | [Topic: Pythagoras]   │
│                                                             │
│    📊 DIAGRAM PREVIEW:                                      │
│    Type: geometric                                              │
│    Description: Right-angled triangle ABC...                  │
│    Points: A (top), B (right angle), C (bottom)                  │
│    Sides: AB = 5 cm, BC = 12 cm                         │
│    Angles: ∠B = 90°                                              │
│    ⊙ Full-quality SVG will be embedded in DOCX export         │
│ ...                                                        │
└─────────────────────────────────────────────────────────────┘

✋ Approve this question paper? (yes/no): yes

  ▶ Subagent: docx-generator
    Task: Generate DOCX from: output/mathematics_class10_first_term_20260201_143052_a7f3d.json
    ✓ docx-generator complete

  ▶ Writing: mathematics_class10_first_term_20260201_143052_a7f3d.docx
  ✓ DOCX generated: output/docx/mathematics_class10_first_term_20260201_143052_a7f3d.docx

✓ Generation Complete!
Generated: 20 questions total
Diagrams embedded: 8
```

## Blueprint Format

Create a JSON blueprint in `input/` folder:

```json
{
  "schema_version": "1.0",
  "exam_metadata": {
    "board": "CBSE",
    "class": 10,
    "subject": "Mathematics",
    "exam_type": "First Term",
    "total_marks": 50,
    "duration_minutes": 120,
    "academic_year": "2025-26"
  },
  "syllabus_scope": {
    "chapters_included": [
      "Real Numbers",
      "Polynomials",
      "Pair of Linear Equations in Two Variables"
    ],
    "topics": {
      "Real Numbers": [
        "Fundamental Theorem of Arithmetic",
        "LCM HCF",
        "Irrationality Proofs"
      ],
      "Polynomials": [
        "Zeroes of Polynomial",
        "Relationship between Zeroes Coefficients"
      ]
    }
  },
  "sections": [
    {
      "section_id": "A",
      "title": "Multiple Choice Questions",
      "question_format": "MCQ",
      "marks_per_question": 1,
      "internal_choice": {"type": "none"},
      "questions_provided": 10,
      "questions_attempt": 10
    },
    {
      "section_id": "B",
      "title": "Short Answer Type",
      "question_format": "SHORT",
      "marks_per_question": 3,
      "internal_choice": {"type": "none"},
      "questions_provided": 5,
      "questions_attempt": 5
    }
  ]
}
```

## Output Format

### Filename Convention

**JSON Question Paper**:
```
{subject}_class{class}_{exam_type}_YYYYMMDD_HHMMSS_{short_id}.json
```

**DOCX Document**:
```
{subject}_class{class}_{exam_type}_YYYYMMDD_HHMMSS_{short_id}.docx
```

Example:
```
mathematics_class10_first_term_20260201_143052_a7f3d.json
mathematics_class10_first_term_20260201_143052_a7f3d.docx
```

### Question Object Structure (With Diagram Support)

```json
{
  "question_id": "MATH-10-REA-MCQ-001",
  "question_text": "Calculate the least common multiple of 15 and 20.",
  "chapter": "Real Numbers",
  "topic": "LCM HCF",
  "question_format": "MCQ",
  "marks": 1,
  "options": ["A) 40", "B) 60", "C) 80", "D) 100"],
  "correct_answer": "B",
  "difficulty": "easy",
  "bloom_level": "apply",
  "tags": ["lcm hcf", "real numbers"],
  "has_diagram": false
}
```

**Question with Diagram**:
```json
{
  "question_id": "MATH-10-TRI-LA-001",
  "question_text": "In a right-angled triangle ABC, AB = 5 cm, BC = 12 cm, and ∠B = 90°. Find AC.",
  "chapter": "Triangles",
  "topic": "Pythagoras Theorem",
  "question_format": "LONG",
  "marks": 5,
  "difficulty": "easy",
  "bloom_level": "apply",
  "has_diagram": true,
  "diagram_type": "geometric",
  "diagram_svg_base64": "PHN2Zy...",
  "diagram_description": "Right-angled triangle ABC with right angle at vertex B...",
  "diagram_elements": {
    "shape": "right_triangle",
    "points": ["A", "B", "C"],
    "sides": ["AB=5", "BC=12", "AC=?"],
    "angles": ["∠B=90°"]
  }
}
```

## Directory Structure

```
question-paper-generator-agent/
├── run.py                          # Main entry point
├── AGENTS.md                       # Agent behavior & instructions
├── README.md                       # This file
├── config/
│   └── agent_config.py            # Subagent definitions
├── tools/                          # Custom tools
│   ├── blueprint_validator.py     # Blueprint validation
│   ├── curriculum_searcher.py     # Tavily search integration
│   ├── diagram_generator.py      # NEW: SVG diagram generation
│   ├── docx_generator.py         # NEW: DOCX export
│   └── paper_validator.py         # Paper validation
├── skills/                         # Domain knowledge
│   └── cbse/
│       ├── common/                # Shared standards
│       │   ├── QUESTION_FORMATS.json
│       │   ├── QUALITY_GUIDELINES.md
│       │   └── DIFFICULTY_DISTRIBUTION.md
│       └── class_10/
│           └── mathematics/
│               ├── SKILL.md            # Includes diagram patterns
│               └── references/
├── display/                        # UI components
│   └── agent_display.py           # Live display & HITL
├── input/                          # Blueprint files
│   └── classes/
│       └── 10/
│           └── mathematics/
│               ├── blueprint.json              # Master blueprint
│               └── input_first_term_50.json   # Teacher file
├── output/                         # Generated papers
│   ├── *.json                     # Question papers
│   └── docx/                      # NEW: Generated DOCX files
├── cache/                          # NEW: Cache directories
│   ├── diagrams/                  # Diagram SVG cache
│   └── temp/                       # Temp PNG for DOCX conversion
└── .env                           # API keys (not in git)
```

## Configuration

### Environment Variables

Required:
- `OPENAI_API_KEY`: OpenAI API key for GPT-4o and gpt-5-mini

Qdrant Configuration:
- `QDRANT__HOST`: Qdrant server host (default: "127.0.0.1")
- `QDRANT__HTTP_PORT`: Qdrant HTTP port (default: 6333)
- `QDRANT__API_KEY`: Qdrant API key (optional, for cloud instances)

LLM Generation Settings (optional):
- `OPENAI__MODEL`: LLM model for question generation (default: "gpt-5-mini")
- `OPENAI__TEMPERATURE`: Temperature for generation (default: 0.3)
- `OPENAI__MAX_TOKENS`: Max tokens for generation (default: 1000)
- `OPENAI__QUALITY_CHECK_ENABLED`: Enable quality self-assessment (default: true)
- `OPENAI__FEW_SHOT_EXAMPLES_ENABLED`: Include few-shot examples (default: true)

### HITL Configuration

Human-in-the-Loop is configured in `config/agent_config.py`:
- Interrupts on `write_file` tool calls
- Shows formatted preview for question papers only
- Auto-approves other file operations
- Max 5 rework iterations

### Subagent Configuration

Six subagents are configured:

1. **input-file-locator**: Locates and validates teacher's input blueprint JSON files
2. **blueprint-validator**: Validates exam blueprint against master policy blueprints (two-blueprint validation)
3. **cbse-question-retriever**: **NEW** - Two-tier system:
   - Step 1: Retrieves chunks from Qdrant vector database using hybrid search
   - Step 2: Generates questions using gpt-5-mini with few-shot examples and quality checks
4. **question-assembler**: Assembles and formats final CBSE-compliant questions
5. **paper-validator**: Validates final paper against blueprint
6. **docx-generator**: Converts JSON papers to DOCX with embedded images

## Diagram Generation Features

### Supported Diagram Types

The system automatically detects when a diagram is needed and generates it using `tools/diagram_generator.py`:

1. **geometric**: Triangles, circles, quadrilaterals, polygons, construction problems
2. **coordinate**: Graphs, coordinate planes, plotting points, distance formulas
3. **formula**: LaTeX/MathML expressions visualized
4. **chart**: Bar charts, histograms, pie charts

### Diagram Detection

The Main Agent auto-detects diagram needs using keyword and pattern matching:

- **Keywords triggering diagrams**: triangle, circle, polygon, quadrilateral, ∠, graph, plot, coordinate, tangent, etc.
- **Keywords NOT requiring diagrams**: solve for, simplify, calculate (without spatial context)

### Terminal Preview

Terminal preview shows **structured diagram descriptions** (not images):
```
📊 DIAGRAM PREVIEW:
Type: geometric
Description: Right-angled triangle ABC with vertices A(top), B(right angle), C(bottom)
Sides: AB = 5 cm, BC = 12 cm, AC = ?
Angles: ∠B = 90°
⊙ Full-quality SVG will be embedded in DOCX export
```

### DOCX Output

After teacher approval, DOCX is generated automatically with:
- CBSE-standard header (board, class, subject, exam info)
- General instructions section
- Formatted sections with numbered questions
- **Embedded PNG images** (converted from SVG using cairosvg)
- Professional styling (font size, margins, alignment)
- Footers with page numbers

**Example DOCX output filenames**:
```
mathematics_class10_first_term_20260201_143052_a7f3d.docx
```

## Troubleshooting

### "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY=sk-xxxx
# Or add to .env file
```

### "No blueprint file found"
- Ensure `.json` file exists in `input/classes/{class}/{subject}/` folder
- Or specify path explicitly: `python run.py "Generate paper from input/classes/10/mathematics/blueprint.json"`

### "Blueprint validation failed"
- Check JSON syntax
- Verify required fields: `metadata`, `syllabus_scope`, `sections`
- Ensure marks calculation is correct
- Check that all topics are present under each chapter

### "Qdrant vector DB not accessible"
- Verify Qdrant is running: `docker ps | grep qdrant`
- Check QDRANT__HOST and QDRANT__HTTP_PORT settings
- Ensure collection exists: `curl http://localhost:6333/collections`
- For Docker: Check port mapping (e.g., 62677->6333)

### "Collection 'mathematics_10' not found"
- Ensure textbook data is ingested into Qdrant
- Verify collection naming: `{subject}_{class}` (e.g., "mathematics_10")
- Check cbse-rag project for data ingestion scripts

### "No textbook content found for {chapter}/{topic}"
- Verify topic exists in Qdrant collection
- Check if topic name matches (case-sensitive in metadata)
- Try fuzzy matching with different topic phrasing
- Ensure syllabus_scope in blueprint matches Qdrant topics

### "HITL not stopping for approval"
- Check that `interrupt_on` is configured in `create_agent()`
- Verify checkpointer (MemorySaver) is enabled
- Ensure thread_id is consistent

### "Diagrams not generating"
- Check if drawsvg, cairosvg, python-docx are installed
- Verify diagram detection keywords are triggering correctly
- Check agent logs for diagram-related errors

### "DOCX generation failed"
- Verify cairosvg installation (requires external dependencies)
- Check for SVG conversion errors in logs
- Ensure JSON paper has valid structure

### "LLM question generation timeout"
- Increase OPENAI__TIMEOUT setting (default: 30 seconds)
- Reduce OPENAI__MAX_TOKENS if generation is too slow
- Check OpenAI API status and rate limits

## Development

### Code Quality
```bash
# Format code
black .

# Lint code
ruff check .

# Type check
mypy .

# Run tests
pytest
```

### Adding New Skills

To add support for a new class/subject:

1. Create folder: `skills/cbse/class_11/physics/`
2. Add `SKILL.md` with domain knowledge
3. Add references in `references/` folder
4. Update agent configuration if needed

### Customizing HITL

To modify the approval workflow:

1. Edit `display/agent_display.py` for UI changes
2. Edit `run.py` `run_agent_with_live_display()` for logic changes
3. Update `AGENTS.md` for agent behavior changes

### Customizing Diagram Generation

To modify how diagrams are generated:

1. Edit `tools/diagram_generator.py` to change pattern detection
2. Update diagram generation logic for new diagram types
3. Add new drawsvg patterns in `skills/cbse/class_10/mathematics/SKILL.md`

### Customizing DOCX Output

To modify DOCX formatting:

1. Edit `tools/docx_generator.py` for styling changes
2. Update header/footer templates
3. Modify section formatting logic
4. Add custom styling options

## License

MIT License - For educational use in CBSE settings.

## Support

For issues or questions:
- Check troubleshooting section above
- Review AGENTS.md for agent behavior details including diagram detection
- Review DIYAGRAM_IMPLEMENTATION.md for diagram generation details
- Review IMPLEMENTATION_COMPLETE.md for complete feature list
- Open an issue on GitHub

## Acknowledgments

- **Deep Agents**: Multi-agent orchestration framework
- **OpenAI GPT-4o**: Question generation and reasoning
- **Tavily**: Real-time curriculum research
- **Rich**: Terminal UI and live display
- **LangGraph**: State management and checkpointing
- **drawsvg**: Vector graphics library for diagram generation
- ** cairosvg**: SVG to PNG conversion for DOCX embedding
- **python-docx**: Professional DOCX document creation