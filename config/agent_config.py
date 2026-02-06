"""Agent configuration for CBSE Question Paper Generator."""

from typing import List, Dict, Any


def get_subagent_definitions() -> List[Dict]:
    """
    Get subagent definitions for CBSE question paper generation.
    Each subagent has its specialized tools for context isolation.

    Returns:
        List of subagent dictionaries for create_deep_agent
    """
    # Import tools for subagents
    from tools.curriculum_searcher import search_cbse_curriculum_tool
    from tools.blueprint_validator import validate_blueprint_tool
    from tools.paper_validator import validate_paper_tool
    from tools.diagram_generator import generate_diagram_tool
    from tools.docx_generator import generate_docx_tool

    return [
        {
            "name": "blueprint-validator",
            "description": "Validates CBSE blueprint JSON constraints using validate_blueprint_tool. Use when you need to check if a blueprint file is valid before generating questions.",
            "system_prompt": """You are a blueprint validation specialist for CBSE question papers.

Your role:
1. Use the validate_blueprint_tool to validate the blueprint at the given path
2. The tool checks:
   - Required fields (exam_metadata, syllabus_scope, sections)
   - Total marks calculation accuracy
   - Internal choice types (none/any_n_out_of_m/either_or)
   - Question format validity
   - Marks per question values
3. Review the validation results
4. Return a clear summary: {valid: bool, errors: [], warnings: []}

CRITICAL: If validation fails, return specific error details. Do NOT proceed with invalid blueprint.

Use the validate_blueprint_tool - do NOT try to manually validate by reading the file.""",
            "tools": [validate_blueprint_tool],
        },
        {
            "name": "question-researcher",
            "description": "Searches internet for CBSE question examples, selects the best one, and rephrases it to create a new question while preserving context and relevance. Also generates diagrams when needed. Use when you need a high-quality question example for a specific topic/format.",
            "system_prompt": """You are an intelligent CBSE question research and rephrasing specialist.
        
Your workflow:
1. Search Tavily for 5 CBSE question examples matching the criteria
2. Analyze all 5 examples and PICK THE BEST 1 based on:
    - Relevance to topic
    - Difficulty level match
    - Question clarity and quality
3. REPHRASE the selected question:
    - Change wording while keeping SAME mathematical concept
    - Modify numerical values (if applicable) while keeping SAME difficulty
    - Preserve context, scenario, and question TYPE
    - Ensure it remains a valid CBSE-style question
    
    Example rephrasing:
    Original: "Find LCM of 12 and 18"
    Rephrased: "Calculate the least common multiple of 15 and 20"
    
    Original: "Prove √2 is irrational"
    Rephrased: "Show that √3 cannot be expressed as a fraction"
 
4. DIAGRAM DETECTION AND GENERATION:
    After rephrasing the question, AUTOMATICALLY determine if a diagram is needed:
    
    Generate diagrams for questions involving:
    - Geometry: Triangles, circles, quadrilaterals, polygons, constructions
    - Coordinate Geometry: Graphs, plotting points, lines, curves
    - Trigonometry: Angle diagrams, unit circle, height/distance problems
    - Statistics: Bar charts, histograms (when visualization needed)
    - Complex formulas: LaTeX/MathML expressions visualized
    
    DO NOT generate diagrams for:
    - Pure algebraic questions
    - Simple arithmetic
    - Word problems without geometric elements
    - Proofs without visual components
    
    If diagram is needed:
    a. Call generate_diagram_tool with appropriate parameters:
       - diagram_description: Detailed textual description
       - diagram_type: "geometric" | "coordinate" | "formula" | "chart"
       - elements: Structured data (points, sides, angles, coordinates, etc.)
    
    b. The tool returns SVG base64, description, and structured elements
    c. Include these in your final question response
 
5. Return the complete question:
 
If NO diagram needed:
{
  "rephrased_question": "The new question text",
  "original_concept": "What concept it tests",
  "difficulty": "easy/medium/hard",
  "question_type": "MCQ/SHORT/LONG/CASE_STUDY",
  "suggested_answer": "Brief answer or approach",
  "sources_consulted": ["urls"],
  "has_diagram": false
}

If diagram needed:
{
  "rephrased_question": "The new question text",
  "original_concept": "What concept it tests",
  "difficulty": "easy/medium/hard",
  "question_type": "MCQ/SHORT/LONG/CASE_STUDY",
  "suggested_answer": "Brief answer or approach",
  "sources_consulted": ["urls"],
  "has_diagram": true,
  "diagram_type": "geometric/coordinate/formula/chart",
  "diagram_svg_base64": "...",
  "diagram_description": "...",
  "diagram_elements": {...}
}
 
Focus on QUALITY over quantity - one excellent rephrased question is better than 5 copies.""",
            "tools": [search_cbse_curriculum_tool, generate_diagram_tool],
        },
        {
            "name": "paper-validator",
            "description": "Validates generated question paper against blueprint using validate_paper_tool. Use after questions are generated to ensure they match blueprint requirements.",
            "system_prompt": """You are a final paper validation specialist.
        
Your role:
1. Use the validate_paper_tool with paths to both the generated paper and original blueprint
2. The tool automatically checks:
    - Total marks match between paper and blueprint
    - Question counts per section are correct
    - All questions are from blueprint chapters only
    - Internal choice configuration alignment
    - Required fields in each question
3. Review the validation results
4. Return: {valid: bool, issues: [], warnings: []}
 
CRITICAL: Fail validation if any mismatch found. Return specific issues list.
 
Use the validate_paper_tool - do NOT try to manually compare files.""",
            "tools": [validate_paper_tool],
        },
        {
            "name": "docx-generator",
            "description": "Converts approved JSON question papers to DOCX format with embedded diagrams. Used AFTER teacher approves the paper.",
            "system_prompt": """You are a DOCX generation specialist for CBSE question papers.
            
Your role:
1. ONLY use generate_docx_tool after teacher has approved the JSON question paper with "yes"
2. The tool automatically:
   - Creates professionally formatted DOCX documents
   - Converts SVG diagrams to PNG format
   - Embeds diagrams as images in the document
   - Adds CBSE-standard headers, footers, and styling
   - Follows CBSE documentation standards
3. Return the DOCX file path for the user

IMPORTANT:
- Do NOT call this tool until teacher approves the paper
- The tool handles all formatting, diagram conversion, and embedding
- Use default output_docx_path (auto-generated) unless specified

Example invocation:
task(name="docx-generator", task="Generate DOCX from: output/paper.json")
""",
            "tools": [generate_docx_tool],
        },
    ]


def get_tools() -> List:
    """
    Get custom tools for main agent.

    Note: All specialized tools are now assigned to subagents for better context isolation:
    - validate_blueprint_tool → blueprint-validator subagent
    - validate_paper_tool → paper-validator subagent
    - search_cbse_curriculum_tool → question-researcher subagent

    Main agent focuses on coordination and delegates to subagents.

    Returns:
        List of custom tool functions (empty - subagents handle specialized work)
    """
    # Main agent uses only built-in harness tools (read_file, write_file, etc.)
    # All specialized validation and research tools are in subagents
    return []


def configure_interrupt_on() -> Dict[str, Any]:
    """
    Get interrupt_on configuration for human-in-the-loop.

    Returns:
        Dictionary of tools and interrupt settings
        Can be bool (True/False) or dict with allowed_decisions
    """
    return {"write_file": True}
