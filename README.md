# CBSE Question Paper Generator

An intelligent agent system for generating CBSE (Central Board of Secondary Education) question papers from JSON blueprints using Deep Agents framework with subagent delegation, live streaming, and human-in-the-loop approval.

## Overview

This system generates high-quality, CBSE-compliant question papers through an intelligent workflow that combines AI generation with teacher oversight. It uses a multi-agent architecture where specialized subagents handle validation, research, and verification while the main agent coordinates the process.

## Key Features

### 🤖 Multi-Agent Architecture
- **Main Agent**: Orchestrates the workflow, coordinates subagents
- **blueprint-validator**: Validates blueprint structure and constraints
- **question-researcher**: Searches and rephrases real CBSE question examples
- **paper-validator**: Validates final paper against blueprint

### 🎯 Intelligent Question Generation
- Searches real CBSE questions online using Tavily
- Rephrases questions to create unique variants while preserving concepts
- Maintains CBSE difficulty distribution (40% easy, 40% medium, 20% hard)
- Follows official CBSE question formats and standards

### 👨‍🏫 Teacher Approval Workflow (HITL)
- **Human-in-the-Loop**: Teachers review formatted question paper before saving
- **Visual Preview**: Shows human-readable formatted paper (not raw JSON)
- **Feedback Loop**: If rejected, captures specific feedback and reworks accordingly
- **Multiple Attempts**: Up to 5 rework iterations with teacher guidance

### 📝 Smart Filename Management
- Unique filenames prevent overwrites: `mathematics_class10_first_term_20260201_143052_a7f3d.json`
- Extracts exam type from blueprint filename automatically
- Supports multiple teachers/users simultaneously
- Human-readable format with timestamp and subject info

### 📚 Progressive Disclosure Skills
- Dynamically loads domain knowledge based on class/subject
- Skills for CBSE Class 10 Mathematics (chapters, topics, patterns)
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
       ┌───────────────┼───────────────┐
       │               │               │
┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│  Blueprint  │ │   Question  │ │    Paper    │
│  Validator  │ │  Researcher │ │  Validator  │
│  Subagent   │ │  Subagent   │ │  Subagent   │
└─────────────┘ └─────────────┘ └─────────────┘
       │               │               │
       └───────────────┼───────────────┘
                       │
       ┌───────────────┴───────────────┐
       │         Skills System         │
       └───────────────┬───────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐
│   Class 10   │ │  Common  │ │  References │
│ Mathematics  │ │ Standards│ │  & Scripts  │
└──────────────┘ └──────────┘ └─────────────┘
```

## Workflow

### Complete Generation Flow

```
1. Teacher Input
   ↓
2. Load & Validate Blueprint (blueprint-validator subagent)
   ↓
3. For Each Question Needed:
   a. Delegate to question-researcher subagent
   b. Search 5 CBSE examples online
   c. Pick best 1 and rephrase
   d. Return rephrased template
   e. Generate final question
   ↓
4. Compile Paper
   ↓
5. Validate Paper (paper-validator subagent)
   ↓
6. HITL: Show Formatted Preview to Teacher
   ↓
7. Teacher Decision:
   ├─ YES → Save file
   └─ NO  → Capture feedback → Go to step 3 (rework)
   ↓
8. Complete
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
   A) 40    B) 60    C) 80    D) 100
   [Correct: B]
...
```

2. **Teacher Approval**: Prompt asks "Approve this question paper? (yes/no)"

3. **If Rejected**:
   - Teacher provides specific feedback (e.g., "Change MCQ 3 to Polynomials")
   - Agent identifies only the affected questions
   - Uses question-researcher to get new templates
   - Regenerates ONLY the requested changes
   - Presents updated paper for re-approval
   - Up to 5 attempts, then asks "Force save or cancel?"

## Installation & Setup

### Prerequisites
- Python 3.11 or later
- uv package manager (recommended)
- OpenAI API key
- Tavily API key (optional, for curriculum search)

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd question-paper-generator-agent
```

### Step 2: Install Dependencies
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
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
# Create input directory
mkdir -p input

# Add your blueprint JSON file(s)
# Example: input/blueprint_first_term_50.json
```

## Getting Started

### Quick Start - Auto Discovery

If you have one blueprint file in `input/` folder:

```bash
python run.py "Generate Class 10 Mathematics question paper"
```

The agent will:
1. Auto-discover the most recent `.json` file in `input/`
2. Load and validate the blueprint
3. Generate questions using subagents
4. Show formatted preview for approval
5. Save to `output/` with unique filename

### Specify Blueprint Explicitly

```bash
python run.py "Generate paper using input/blueprint_first_term_50.json"
```

### Example Session

```bash
$ python run.py "Generate Class 10 Mathematics first term paper"

             Blueprint Configuration             
┌──────────┬────────────────────────────────────┐
│ File     │ input/blueprint_first_term_50.json │
│ Location │ input/ folder (auto-discovered)    │
└──────────┴────────────────────────────────────┘

Creating CBSE Question Paper Generator agent...
Agent created successfully!

CBSE Question Paper Generator
Task: Generate a CBSE question paper using blueprint input/blueprint_first_term_50.json...
Using Live Streaming with Human-in-the-Loop...

✓ Loaded blueprint: input/blueprint_first_term_50.json
Will save to: output/mathematics_class10_first_term_20260201_143052_a7f3d.json

  ▶ Subagent: blueprint-validator
    Task: Validate blueprint...
    ✓ blueprint-validator complete

  ▶ Subagent: question-researcher
    Task: Format=MCQ, Chapter=Real Numbers, Topic=LCM HCF...
    ✓ question-researcher complete

  ... (more subagent calls) ...

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
│  ...                                                        │
└─────────────────────────────────────────────────────────────┘

✋ Approve this question paper? (yes/no): yes
✓ Teacher approved! Saving file...

✓ Generation Complete!
Generated: 20 questions total
Rework iterations: 0
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
```
{subject}_class{class}_{exam_type}_YYYYMMDD_HHMMSS_{short_id}.json

Example:
mathematics_class10_first_term_20260201_143052_a7f3d.json
```

Components:
- **subject**: From blueprint (lowercase)
- **class**: From blueprint (e.g., "class10")
- **exam_type**: From blueprint filename (e.g., "first_term")
- **timestamp**: YYYYMMDD_HHMMSS (prevents overwrites)
- **short_id**: First 5 chars of UUID (ensures uniqueness)

### File Structure
```json
{
  "schema_version": "1.0",
  "paper_id": "uuid",
  "blueprint_reference": "input/blueprint_first_term_50.json",
  "exam_metadata": {...},
  "sections": [
    {
      "section_id": "A",
      "title": "Multiple Choice Questions",
      "questions": [
        {
          "question_id": "MATH-10-REA-MCQ-001",
          "question_text": "Calculate the LCM of 15 and 20.",
          "chapter": "Real Numbers",
          "topic": "LCM HCF",
          "question_format": "MCQ",
          "marks": 1,
          "options": ["A) 40", "B) 60", "C) 80", "D) 100"],
          "correct_answer": "B",
          "difficulty": "easy",
          "bloom_level": "apply",
          "tags": ["lcm hcf", "real numbers"]
        }
      ]
    }
  ],
  "total_marks": 50,
  "total_questions": 20,
  "generation_metadata": {
    "timestamp": "2026-02-01T14:30:52",
    "subagents_used": ["blueprint-validator", "question-researcher", "paper-validator"],
    "rework_iterations": 0
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
│   └── paper_validator.py         # Paper validation
├── skills/                         # Domain knowledge
│   └── cbse/
│       ├── common/                # Shared standards
│       │   ├── QUESTION_FORMATS.json
│       │   ├── QUALITY_GUIDELINES.md
│       │   └── DIFFICULTY_DISTRIBUTION.md
│       └── class_10/
│           └── mathematics/
│               ├── SKILL.md
│               └── references/
├── display/                        # UI components
│   └── agent_display.py           # Live display & HITL
├── input/                          # Blueprint files
│   └── blueprint_first_term_50.json
├── output/                         # Generated papers
│   └── mathematics_class10_first_term_20260201_143052_a7f3d.json
└── .env                           # API keys (not in git)
```

## Configuration

### Environment Variables

Required:
- `OPENAI_API_KEY`: OpenAI API key for GPT-4o

Optional:
- `TAVILY_API_KEY`: Tavily API key for curriculum search (disabled if not set)

### HITL Configuration

Human-in-the-Loop is configured in `config/agent_config.py`:
- Interrupts on `write_file` tool calls
- Shows formatted preview for question papers only
- Auto-approves other file operations
- Max 5 rework iterations

### Subagent Configuration

Three subagents are configured:

1. **blueprint-validator**: Validates blueprint JSON structure
2. **question-researcher**: Searches and rephrases CBSE questions
3. **paper-validator**: Validates final paper against blueprint

## Troubleshooting

### "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY=sk-xxxx
# Or add to .env file
```

### "No blueprint file found"
- Ensure `.json` file exists in `input/` folder
- Or specify path explicitly: `python run.py "using input/my_blueprint.json"`

### "Blueprint validation failed"
- Check JSON syntax
- Verify required fields: `exam_metadata`, `syllabus_scope`, `sections`
- Ensure marks calculation is correct

### HITL not stopping for approval
- Check that `interrupt_on` is configured in `create_agent()`
- Verify checkpointer (MemorySaver) is enabled
- Ensure thread_id is consistent

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

## License

MIT License - For educational use in CBSE settings.

## Support

For issues or questions:
- Check troubleshooting section above
- Review AGENTS.md for agent behavior details
- Open an issue on GitHub

## Acknowledgments

- **Deep Agents**: Multi-agent orchestration framework
- **OpenAI GPT-4o**: Question generation and reasoning
- **Tavily**: Real-time curriculum research
- **Rich**: Terminal UI and live display
- **LangGraph**: State management and checkpointing
