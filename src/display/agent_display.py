"""Live display system for CBSE Question Paper Generator with enhanced subagent tracking."""

from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text
from rich.table import Table
from rich.layout import Layout


def convert_json_to_text(json_content: str) -> str:
    """Convert question paper JSON to human-readable format for teacher preview."""
    import json

    try:
        data = json.loads(json_content) if isinstance(json_content, str) else json_content
    except json.JSONDecodeError:
        return "Error: Invalid JSON content"

    output = []

    # Header
    metadata = data.get("exam_metadata", {})
    output.append("=" * 70)
    output.append(
        f"CBSE CLASS {metadata.get('class', '10')} {metadata.get('subject', 'MATHEMATICS').upper()}"
    )
    output.append(f"{metadata.get('exam_type', 'EXAMINATION').upper()}")
    output.append("=" * 70)
    output.append(
        f"Total Marks: {metadata.get('total_marks', 0)} | Duration: {metadata.get('duration_minutes', 120)} minutes"
    )
    output.append(f"Academic Year: {metadata.get('academic_year', '2025-26')}")
    output.append("")

    # Sections
    for section in data.get("sections", []):
        section_id = section.get("section_id", "")
        title = section.get("title", "")
        format_type = section.get("question_format", "")
        marks_per_q = section.get("marks_per_question", 0)

        output.append("-" * 70)
        output.append(f"SECTION {section_id}: {title.upper()}")
        output.append(f"Question Format: {format_type} | Marks per Question: {marks_per_q}")
        output.append("-" * 70)
        output.append("")

        # Questions
        for i, q in enumerate(section.get("questions", []), 1):
            q_id = q.get("question_id", f"Q{i}")
            text = q.get("question_text", "")
            marks = q.get("marks", 0)
            difficulty = q.get("difficulty", "medium")
            chapter = q.get("chapter", "")
            topic = q.get("topic", "")

            output.append(f"{i}. {text} ({marks} mark{'s' if marks > 1 else ''})")
            output.append(
                f"   [Difficulty: {difficulty}] | [Chapter: {chapter}] | [Topic: {topic}]"
            )

            # MCQ options
            if format_type == "MCQ" and q.get("options"):
                for opt in q.get("options", []):
                    output.append(f"   {opt}")
                output.append(f"   [Correct Answer: {q.get('correct_answer', 'N/A')}]")

            # Show correct answer for non-MCQ if available
            elif q.get("correct_answer"):
                output.append(f"   [Answer: {q.get('correct_answer')}]")

            # NEW: Diagram preview in terminal
            if q.get("has_diagram"):
                desc = q.get("diagram_description", "[Diagram description missing]")
                elements = q.get("diagram_elements", {})
                diag_type = q.get("diagram_type", "geometric")

                output.append("")
                output.append(f"   [bold]📊 DIAGRAM PREVIEW:[/]")
                output.append(f"   [dim]Type:[/] {diag_type}")
                output.append(f"   [dim]Description:[/] {desc}")

                # Show structured elements
                if isinstance(elements, dict):
                    if "points" in elements:
                        output.append(
                            f"   [dim]Points:[/] {', '.join(str(p) for p in elements['points'])}"
                        )
                    if "sides" in elements:
                        output.append(f"   [dim]Sides:[/] {', '.join(elements['sides'])}")
                    if "angles" in elements:
                        output.append(f"   [dim]Angles:[/] {', '.join(elements['angles'])}")
                    if "coordinates" in elements:
                        coords_str = ", ".join(
                            [f"{k}={v}" for k, v in elements["coordinates"].items()]
                        )
                        output.append(f"   [dim]Coordinates:[/] {coords_str}")
                    if "axes" in elements:
                        output.append(f"   [dim]Axes:[/] {elements['axes']}")

                output.append("")
                output.append(f"   [dim]⊙ Full-quality SVG will be embedded in DOCX export[/]")
                output.append("")

    # Footer
    total_questions = sum(len(s.get("questions", [])) for s in data.get("sections", []))
    output.append("=" * 70)
    output.append(f"END OF QUESTION PAPER - Total Questions: {total_questions}")
    output.append("=" * 70)

    return "\n".join(output)


class QuestionPaperAgentDisplay:
    """Manages display of CBSE question paper generation progress with subagent tracking."""

    # Subagent color coding
    SUBAGENT_COLORS = {
        "blueprint-validator": "blue",
        "question-researcher": "purple",
        "paper-validator": "yellow",
        "general-purpose": "cyan",
    }

    def __init__(self):
        self.printed_count = 0
        self.current_status = ""
        self.spinner = Spinner("dots", text="Initializing...")
        self.total_questions = 0
        self.generated_questions = 0

        # Subagent tracking
        self.active_subagents: Dict[str, Dict] = {}
        self.subagent_history: List[Dict] = []
        self.current_subagent: Optional[str] = None

    def update_status(self, status: str):
        """Update the spinner status text."""
        self.current_status = status
        self.spinner = Spinner("dots", text=status)

    def get_subagent_color(self, name: str) -> str:
        """Get color for subagent type."""
        for key, color in self.SUBAGENT_COLORS.items():
            if key in name.lower():
                return color
        return "white"

    def print_message(self, msg):
        """Print messages with formatting based on type."""
        console = Console()

        if isinstance(msg, HumanMessage):
            console.print(Panel(str(msg.content), title="You", border_style="blue"))

        elif isinstance(msg, AIMessage):
            content = msg.content
            if isinstance(content, list):
                text_parts = [
                    p.get("text", "")
                    for p in content
                    if isinstance(p, dict) and p.get("type") == "text"
                ]
                content = "\n".join(text_parts)

            if content and content.strip():
                console.print(Panel(Markdown(content), title="Agent", border_style="green"))

            # Track agent tool calls for progress
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    name = tc.get("name", "unknown")
                    args = tc.get("args", {})

                    # Blueprint Validation Progress
                    if name == "validate_blueprint_tool":
                        path = args.get("blueprint_path", "")
                        console.print(f"  [bold blue]▶ Validating blueprint:[/] {Path(path).name}")
                        self.update_status(f"Validating: {Path(path).name}")

                    # Question Generation Progress
                    elif name == "generate_questions_gpt4o":
                        topic = args.get("topic", "")
                        count = args.get("count", 1)
                        self.total_questions += int(count)
                        console.print(
                            f"  [bold magenta]▶ Generating {count} questions:[/] {topic[:50]}..."
                        )
                        self.update_status(f"Generating {count} questions...")
                        self.generated_questions += int(count)
                        console.print(
                            f"    [dim]Progress: {self.generated_questions}/{self.total_questions} questions[/]"
                        )

                    # Paper Validation Progress
                    elif name == "validate_paper_tool":
                        paper_path = args.get("paper_path", "")
                        console.print(
                            f"  [bold yellow]▶ Validating paper:[/] {Path(paper_path).name}"
                        )
                        self.update_status("Validating final paper...")

                    # Subagent Delegation - Enhanced tracking
                    elif name == "task":
                        # According to deepagents documentation, task tool uses:
                        # - subagent_type: the subagent name
                        # - description: the task description
                        subagent_name = args.get("subagent_type", "unknown-subagent")
                        task_desc = args.get("description", "")

                        # Track subagent activation
                        self.current_subagent = subagent_name
                        color = self.get_subagent_color(subagent_name)

                        # Show subagent activation with icon and color
                        console.print(f"\n  [bold {color}]▶ Subagent:[/] [bold]{subagent_name}[/]")

                        # Show brief task description
                        if task_desc:
                            console.print(f"    [dim]Task:[/] {task_desc[:80]}...")

                        # Track in active subagents
                        self.active_subagents[subagent_name] = {
                            "started": datetime.now().isoformat(),
                            "status": "running",
                            "task": task_desc[:50] if task_desc else "working",
                        }

                        self.update_status(f"Running: {subagent_name}")

                    # Read/Write Operations
                    elif name == "read_file":
                        path = args.get("file_path", "")
                        console.print(f"  [dim]▶ Reading:[/] {Path(path).name}")
                        self.update_status(f"Reading: {Path(path).name}")

                    elif name == "write_file":
                        path = args.get("file_path", "")
                        console.print(f"  [bold yellow]▶ Writing:[/] {Path(path).name}")
                        self.update_status(f"Writing: {Path(path).name}")
                        console.print(f"    [yellow]⚠ HITL: Teacher approval required[/]")

        elif isinstance(msg, ToolMessage):
            name = getattr(msg, "name", "")
            content = str(msg.content) if isinstance(msg.content, str) else str(msg.content)

            # Blueprint Validation Results
            if name == "validate_blueprint_tool":
                import json

                try:
                    result = content
                    if isinstance(result, str):
                        result = json.loads(result)
                    if result.get("valid"):
                        console.print(f"    [green]✓ Blueprint valid[/]")
                        self.update_status("Blueprint valid ✓")
                    else:
                        errors = result.get("errors", [])
                        console.print(f"    [red]✗ Blueprint invalid[/]")
                        if errors:
                            console.print(f"      [red]Errors: {', '.join(errors[:2])}[/]")
                        self.update_status("Blueprint invalid ✗")
                except Exception:
                    console.print(f"    [red]✗ Validation error[/]")
                    self.update_status("Validation failed")

            # Question Generation Results
            elif name == "generate_questions_gpt4o":
                import json

                try:
                    result = content
                    if isinstance(result, str):
                        result = json.loads(result)
                    questions = result.get("questions", [])
                    if questions and len(questions) > 0:
                        console.print(f"    [green]✓ Generated {len(questions)} questions[/]")
                        self.update_status(f"Generated {len(questions)} questions ✓")
                except Exception:
                    console.print(f"    [red]✗ Generation failed[/]")
                    self.update_status("Question generation failed")

            # Paper Validation Results
            elif name == "validate_paper_tool":
                import json

                try:
                    result = content
                    if isinstance(result, str):
                        result = json.loads(result)
                    valid = result.get("valid")
                    issues = result.get("issues", [])

                    if valid:
                        console.print(f"    [green]✓ Paper validation passed[/]")
                        self.update_status("Paper valid ✓")
                    else:
                        console.print(f"    [red]✗ Paper invalid[/]")
                        if issues:
                            console.print(f"      [red]Issues: {', '.join(issues[:2])}[/]")
                        self.update_status("Paper invalid - fixing...")
                except Exception:
                    console.print(f"    [red]✗ Validation error[/]")
                    self.update_status("Validation failed")

            # Read/Write Operations Results
            elif name == "read_file":
                console.print(f"    [green]✓ File read[/]")

            elif name == "write_file":
                if "saved" in content.lower() or "complete" in content.lower():
                    console.print(f"    [green]✓ File saved[/]")
                    self.update_status("Paper saved ✓")
                else:
                    console.print(f"    [yellow]⚠ Write complete[/]")

            # Subagent Task Completion
            elif name == "task":
                # Mark subagent as completed
                if self.current_subagent:
                    color = self.get_subagent_color(self.current_subagent)
                    console.print(
                        f"    [green]✓[/] [bold {color}]{self.current_subagent}[/] complete"
                    )

                    # Move to history
                    if self.current_subagent in self.active_subagents:
                        self.subagent_history.append(
                            {
                                **self.active_subagents[self.current_subagent],
                                "name": self.current_subagent,
                                "completed": datetime.now().isoformat(),
                                "status": "completed",
                            }
                        )
                        del self.active_subagents[self.current_subagent]

                    self.current_subagent = None
                    self.update_status("Subagent complete ✓")

    def get_status_panel(self) -> Panel:
        """Generate a status panel showing current progress."""
        # Build status text
        status_lines = [
            f"[bold]Questions:[/] {self.generated_questions}/{self.total_questions} generated",
        ]

        # Add active subagents
        if self.active_subagents:
            status_lines.append(f"\n[bold]Active Subagents:[/]")
            for name, info in self.active_subagents.items():
                color = self.get_subagent_color(name)
                status_lines.append(f"  [{color}]▶ {name}[/] - {info.get('task', 'working')}")

        # Add current status
        status_lines.append(f"\n[bold]Current:[/] {self.current_status}")

        return Panel(
            "\n".join(status_lines), title="[bold blue]Generation Status[/]", border_style="blue"
        )

    def print_summary(self):
        """Print final summary of generation."""
        console = Console()

        # Create summary table
        table = Table(title="[bold green]Generation Summary[/]", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Total Questions", str(self.generated_questions))
        table.add_row("Target Questions", str(self.total_questions))
        table.add_row("Subagents Used", str(len(self.subagent_history)))

        if self.subagent_history:
            subagent_names = list(set([s["name"] for s in self.subagent_history]))
            table.add_row("Subagent Types", ", ".join(subagent_names))

        console.print()
        console.print(table)
        console.print()
