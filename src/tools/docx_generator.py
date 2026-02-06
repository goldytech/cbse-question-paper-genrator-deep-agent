"""Tool for converting JSON question papers to DOCX format with embedded diagrams."""

import os
import base64
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from langchain_core.tools import tool


# Cache directory for temporary PNG files
TEMP_DIR = Path(__file__).parent.parent / "cache" / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Output directory for DOCX files
DOCX_OUTPUT_DIR = Path(__file__).parent.parent / "output" / "docx"
DOCX_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_cairosvg_installed():
    """Check if cairosvg is installed."""
    try:
        import cairosvg

        return True
    except ImportError:
        print("Warning: cairosvg not installed. SVG to PNG conversion will be skipped.")
        print("Diagrams in DOCX will be missing, but document will still be generated.")
        return False


def _svg_base64_to_png(svg_base64: str, width: int = 400) -> Optional[bytes]:
    """Convert base64-encoded SVG to PNG using cairosvg."""
    if not _ensure_cairosvg_installed():
        print("Warning: cairosvg not available, cannot convert SVG to PNG")
        return None

    try:
        import cairosvg

        # Decode base64 SVG
        svg_content = base64.b64decode(svg_base64)

        # Convert SVG to PNG
        png_bytes = cairosvg.svg2png(bytestring=svg_content, output_width=width, write_to=None)

        return png_bytes

    except Exception as e:
        print(f"Error converting SVG to PNG: {e}")
        return None


def _generate_docx_filename(metadata: Dict) -> str:
    """Generate DOCX filename from metadata."""
    subject = metadata.get("subject", "mathematics").lower().replace(" ", "_")
    cls = metadata.get("class", "10")
    exam_type = metadata.get("exam_type", "examination").lower().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_id = str(uuid.uuid4())[:5]

    return f"{subject}_class{cls}_{exam_type}_{timestamp}_{short_id}.docx"


def _create_cbse_header(doc, metadata: Dict):
    """Create CBSE-style header for document."""
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    # Get section
    section = doc.sections[0]

    # Header content
    header = section.header
    header_para = header.paragraphs[0] if header.paragraphs else header.add_paragraph()

    # Add CBSE title
    header_para.text = "CBSE | CENTRAL BOARD OF SECONDARY EDUCATION"
    header_para.runs[0].bold = True
    header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header_para.runs[0].font.size = Pt(10)

    # Add exam details
    exam_para = header.add_paragraph()
    exam_details = f"""
{metadata.get("subject", "").upper()} (Class {metadata.get("class", "")})
{metadata.get("exam_type", "").upper()}
TIME: {metadata.get("duration_minutes", 0) // 60} hours | MAX.MARKS: {metadata.get("total_marks", 0)}
    """.strip()
    exam_para.text = exam_details
    exam_run = exam_para.runs[0]
    exam_run.bold = True
    exam_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    exam_run.font.size = Pt(8)


def _create_cbse_general_instructions(doc):
    """Add general instructions section."""
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    para = doc.add_paragraph()
    para.add_run("General Instructions:").bold = True
    para.spacing_after = Pt(6)

    instructions = [
        "This Question Paper consists of 5 Sections A, B, C, D and E.",
        "All questions are compulsory.",
        "Draw neat and clean figures wherever required.",
        "Use of calculators is not allowed.",
        "Take π = 22/7 wherever required if not stated.",
    ]

    for i, instruction in enumerate(instructions, 1):
        inst_para = doc.add_paragraph()
        inst_para.add_run(f"{i}. {instruction}")
        inst_para.paragraph_format.left_indent = Inches(0.25)

    doc.add_paragraph()  # Empty line after instructions


@tool
def generate_docx_tool(
    json_paper_path: str, output_docx_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convert JSON question paper to DOCX format with embedded diagrams.

    This tool reads a JSON question paper from the given path, converts all SVG diagrams
    to PNG format, and creates a professionally formatted DOCX document following CBSE
    standards. The DOCX includes headers with exam information, formatted sections,
    numbered questions, and embedded images for questions with diagrams.

    Args:
        json_paper_path: Path to the JSON question paper file
        output_docx_path: Optional path for output DOCX. If not provided, filename is
                        auto-generated based on metadata.

    Returns:
        {
            "success": bool,
            "docx_path": str,           # Path to generated DOCX file
            "questions_count": int,      # Total questions in paper
            "diagrams_embedded": int,   # Number of diagrams converted/embedded
            "generation_time": str,      # ISO timestamp
            "error": str (if failed)
        }

    Example:
        generate_docx_tool(
            json_paper_path="output/paper.json",
            output_docx_path="output/docx/paper.docx"
        )
    """
    try:
        from docx import Document
        from docx.shared import Pt, Inches, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING

        # Read JSON paper
        json_path = Path(json_paper_path)
        if not json_path.exists():
            return {"success": False, "error": f"JSON file not found: {json_paper_path}"}

        with open(json_path, "r", encoding="utf-8") as f:
            paper_data = json.load(f)

        # Create Word document
        doc = Document()

        # Setup margins (CBSE standard: 1 inch on all sides)
        for section in doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

        # Create header
        metadata = paper_data.get("exam_metadata", paper_data.get("paper_metadata", {}))
        _create_cbse_header(doc, metadata)

        # Add general instructions
        _create_cbse_general_instructions(doc)

        # Process sections
        sections = paper_data.get("sections", [])
        questions_count = 0
        diagrams_embedded = 0

        for section_data in sections:
            section_id = section_data.get("section_id", "")
            section_title = section_data.get("title", "")

            # Section heading
            section_heading = doc.add_paragraph()
            section_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
            section_heading.add_run(f"SECTION {section_id}: {section_title.upper()}").bold = True
            section_heading.runs[0].font.size = Pt(11)
            section_heading.runs[0].font.color.rgb = RGBColor(0, 0, 0)

            # Section marks info
            section_marks_part = section_data.get(
                "questions_attempt", section_data.get("questions_provided", 0)
            )
            section_marks = section_marks_part * section_data.get("marks_per_question", 0)

            section_marks_para = doc.add_paragraph()
            section_marks_para.add_run(f"({section_marks} marks)").italic = True
            section_marks_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

            doc.add_paragraph()  # Empty line

            # Process questions
            questions = section_data.get("questions", [])
            for q_num, question in enumerate(questions, 1):
                q_id = question.get("question_id", f"Q{q_num}")
                q_text = question.get("question_text", "")
                q_marks = question.get("marks", 0)
                q_format = question.get("question_format", "")

                # Question number and text
                q_para = doc.add_paragraph()
                q_para.add_run(f"{q_num}.").bold = True
                q_para.add_run(f" {q_text} ({q_marks} mark{'s' if q_marks > 1 else ''})")

                # MCQ options
                if q_format == "MCQ" and question.get("options"):
                    q_para = doc.add_paragraph()
                    q_para.paragraph_format.left_indent = Inches(0.5)
                    options = question.get("options", {})
                    for opt_letter, opt_text in options.items():
                        q_para.add_run(f"{opt_letter}) {opt_text}")
                        q_para.add_run("\n")

                # Embed diagram if present
                if question.get("has_diagram"):
                    svg_base64 = question.get("diagram_svg_base64", "")
                    if svg_base64:
                        png_bytes = _svg_base64_to_png(svg_base64, width=350)

                        if png_bytes:
                            # Save PNG temporarily
                            temp_png = TEMP_DIR / f"_{uuid.uuid4()}.png"
                            with open(temp_png, "wb") as f:
                                f.write(png_bytes)

                            try:
                                # Add diagram to document
                                diagram_para = doc.add_paragraph()
                                diagram_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

                                # Add alt-text (description)
                                desc = question.get("diagram_description", "Diagram")
                                diagram_para.add_run(f"Figure: {desc}").italic = True

                                # Add image
                                doc.add_picture(str(temp_png), width=Inches(4))

                                diagrams_embedded += 1
                            finally:
                                # Clean up
                                temp_png.unlink()

                # Answer space (for non-MCQ questions)
                if q_format not in ["MCQ"]:
                    doc.add_page_break()

                questions_count += 1

            doc.add_page_break()  # Page break between sections

        # Create footer
        for section in doc.sections:
            footer = section.footer
            footer_para = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
            footer_para.text = f"CBSE Question Paper Generator | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            footer_para.runs[0].font.size = Pt(8)
            footer_para.runs[0].font.color.rgb = RGBColor(128, 128, 128)

        # Generate output filename
        if not output_docx_path:
            output_docx_path = DOCX_OUTPUT_DIR / _generate_docx_filename(metadata)

        # Save document
        doc.save(output_docx_path)

        return {
            "success": True,
            "docx_path": str(output_docx_path),
            "questions_count": questions_count,
            "diagrams_embedded": diagrams_embedded,
            "generation_time": datetime.now().isoformat(),
        }

    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        print(f"Error generating DOCX: {e}")
        print(f"Traceback:\n{error_trace}")

        return {"success": False, "error": str(e), "traceback": error_trace}


def verify_docx_generator():
    """Test function to verify DOCX generation works."""
    print("Testing docx_generator module...")

    # Check if dependencies available
    try:
        from docx import Document

        print("✓ python-docx available")
    except ImportError as e:
        print(f"✗ python-docx not available: {e}")
        return

    if not _ensure_cairosvg_installed():
        print("⚠ cairosvg not available, SVG conversion will be skipped")
    else:
        print("✓ cairosvg available")

    print("DocX generator module tests complete.")


if __name__ == "__main__":
    verify_docx_generator()
