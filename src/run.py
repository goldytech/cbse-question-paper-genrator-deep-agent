"""
Main run function for CBSE Question Paper Generator with Live Display.
"""

import asyncio
import json
import re
import uuid
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langgraph.types import Command

load_dotenv()

from src.display.agent_display import QuestionPaperAgentDisplay, convert_json_to_text
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def should_trigger_hitl(file_path: str) -> bool:
    """
    Determine if Human-in-the-Loop should be triggered for this file write.

    HITL is triggered ONLY for final question papers in the output/ folder.
    Auto-approve all other file operations.

    Args:
        file_path: Path to the file being written

    Returns:
        True if HITL should be triggered, False for auto-approval
    """
    # Must be in the output directory
    if "output/" not in file_path and not file_path.startswith("output"):
        return False

    filename = Path(file_path).name.lower()

    # Don't interrupt for master/user files (blueprint, config, etc.)
    master_patterns = ["blueprint", "config", "template", "settings"]
    if any(pattern in filename for pattern in master_patterns):
        return False

    # Must be a question paper file
    # Pattern: {subject}_{class}_{exam}_YYYYMMDD_HHMMSS_xxxx.json
    if re.match(r"^[a-z]+_class\d+_[a-z_]+_\d{8}_\d{6}_[a-z0-9]+\.json$", filename):
        return True

    # Also check if filename contains question paper indicators
    if any(indicator in filename for indicator in ["question", "paper", "exam"]):
        return True

    return False


def extract_exam_type_from_blueprint_path(blueprint_path: str) -> str:
    """
    Extract exam type from blueprint filename.

    Example:
        Input: "input/blueprint_first_term_50.json"
        Output: "first_term"

    Args:
        blueprint_path: Path to the blueprint file

    Returns:
        Exam type string (e.g., "first_term", "second_term", "final")
    """
    filename = Path(blueprint_path).stem  # Get filename without extension

    # Pattern: blueprint_{exam_type}_{marks}.json
    match = re.match(r"blueprint_([a-z_]+)_\d+", filename)
    if match:
        return match.group(1)

    # Fallback: return generic name
    return "exam"


def cleanup_old_preview_files(output_dir: str = "output", keep_count: int = 3):
    """
    Clean up old preview files, keeping only the most recent ones.

    Args:
        output_dir: Directory containing preview files
        keep_count: Number of most recent preview files to keep
    """
    try:
        output_path = Path(output_dir)
        if not output_path.exists():
            return

        # Find all preview files
        preview_files = list(output_path.glob("preview_*.json"))
        if len(preview_files) <= keep_count:
            return

        # Sort by modification time (newest first)
        preview_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        # Delete older files
        for old_file in preview_files[keep_count:]:
            try:
                old_file.unlink()
            except:
                pass  # Ignore deletion errors
    except Exception:
        pass  # Silently ignore cleanup errors


def generate_output_filename(blueprint_path: str, blueprint_data: dict) -> str:
    """
    Generate unique filename for question paper based on blueprint metadata.

    Format: {subject}_{class}_{exam}_YYYYMMDD_HHMMSS_{short_id}.json

    Args:
        blueprint_path: Path to blueprint file (to extract exam type)
        blueprint_data: Parsed blueprint JSON data

    Returns:
        Full filename for the output question paper
    """
    # Extract metadata from blueprint
    metadata = blueprint_data.get("exam_metadata", {})
    subject = metadata.get("subject", "unknown").lower().replace(" ", "_")
    class_num = metadata.get("class", "10")

    # Extract exam type from blueprint filename
    exam_type = extract_exam_type_from_blueprint_path(blueprint_path)

    # Generate timestamp: YYYYMMDD_HHMMSS
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Generate short unique ID (first 5 chars of UUID)
    short_id = str(uuid.uuid4())[:5]

    # Build filename
    filename = f"{subject}_class{class_num}_{exam_type}_{timestamp}_{short_id}.json"

    return f"output/{filename}"


def find_blueprint_path(task):
    """Extract blueprint path from task or discover in input folder.

    Returns a relative path (e.g., 'input/blueprint.json') for FilesystemBackend compatibility.
    """
    input_dir = Path("input")

    words = task.split()
    for word in words:
        if word.startswith("input/") and word.endswith(".json"):
            return word
        if word.startswith("output/") and word.endswith(".json"):
            return word

    if input_dir.exists():
        json_files = list(input_dir.glob("*.json"))
        if json_files:
            # Return a relative path with forward slashes for FilesystemBackend
            latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
            return str(latest_file).replace("\\", "/")

    raise FileNotFoundError(
        "No blueprint file found. Please provide a blueprint path in your task "
        "or place a blueprint JSON file in the input/ folder."
    )


def display_blueprint_info(blueprint_path):
    """Display blueprint information using Rich."""
    table = Table(title="[bold blue]Blueprint Configuration[/]", show_header=False)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("File", blueprint_path)
    table.add_row("Location", "input/ folder [dim](auto-discovered)[/]")

    console.print()
    console.print(table)
    console.print()


def handle_blueprint_error(error):
    """Handle blueprint-related errors gracefully using Rich."""
    error_table = Table(title="[red]Blueprint Error[/]", show_header=False)
    error_table.add_row(str(error), style="red")

    console.print()
    console.print(
        Panel(
            error_table,
            title="[bold red]Configuration Error[/]",
            border_style="red",
            padding=(1, 2),
        )
    )
    console.print()

    console.print("[yellow]Tips:[/]")
    console.print("• Provide blueprint path in your task, e.g.,")
    console.print('  [dim]"Generate paper using input/blueprint_first_term_50.json"[/]')
    console.print("• Or place a blueprint JSON file in [bold]input/[/] folder")
    console.print("• Blueprint files must be [bold].json[/] format")


async def run_agent_with_live_display(agent, task, blueprint_path, thread_id="session-1"):
    """Run agent with real-time live display and HITL interrupt handling."""
    from rich.live import Live
    from deepagents.backends.utils import create_file_data

    console_local = Console()
    display = QuestionPaperAgentDisplay()

    # HITL tracking
    rework_count = 0
    max_rework_attempts = 5
    pending_feedback = None

    console_local.print()
    console_local.print("[bold blue]CBSE Question Paper Generator[/]")
    task_display = task[:80] + "..." if len(task) > 80 else task
    console_local.print(f"[dim]Task: {task_display}[/]")
    console_local.print()
    console_local.print("[dim]Using Live Streaming with Human-in-the-Loop...[/]")
    console_local.print()

    # Normalize path to use forward slashes for FilesystemBackend
    normalized_path = blueprint_path.replace("\\", "/")

    # Load blueprint file data - FilesystemBackend handles paths
    files = {}
    blueprint_data = None
    try:
        with open(blueprint_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Use a normalized path (forward slashes) for FilesystemBackend
            files[normalized_path] = create_file_data(content)
            # Parse blueprint for metadata
            blueprint_data = json.loads(content)
        console_local.print(f"[green]✓ Loaded blueprint: {normalized_path}[/]")
    except Exception as e:
        console_local.print(f"[red]✗ Failed to load blueprint: {e}[/]")
        raise

    # Generate a dynamic output filename based on blueprint metadata
    output_filename = generate_output_filename(blueprint_path, blueprint_data)
    console_local.print(f"[dim]Will save to: {output_filename}[/]")

    # Update task to use normalized path and include output filename
    task_with_normalized_path = task.replace(blueprint_path, normalized_path)
    task_with_normalized_path = task_with_normalized_path.replace(
        "output/question_paper.json", output_filename
    )

    live_obj = Live(display.spinner, console=console_local, refresh_per_second=10, transient=True)

    config = {"configurable": {"thread_id": thread_id}}

    with live_obj:
        while True:
            async for chunk in agent.astream(
                {"messages": [("user", task_with_normalized_path)], "files": files},
                config=config,
                stream_mode="values",
            ):
                # Handle messages
                if "messages" in chunk:
                    messages = chunk["messages"]
                    if len(messages) > display.printed_count:
                        live_obj.stop()
                        for msg in messages[display.printed_count :]:
                            display.print_message(msg)
                        display.printed_count = len(messages)
                        live_obj.start()
                        live_obj.update(display.spinner)

                # Handle HITL interrupts
                if "__interrupt__" in chunk:
                    live_obj.stop()

                    interrupts = chunk["__interrupt__"]
                    action_requests = interrupts[0].value["action_requests"]

                    decisions = []
                    hitl_triggered = False

                    for action in action_requests:
                        if action["name"] == "write_file":
                            file_path = action["args"].get("file_path", "")
                            json_content = action["args"].get("content", "")
                            filename = Path(file_path).name

                            # Check if this is a staging (preview) file
                            is_staging_file = filename.startswith("preview_")

                            # Check if this should trigger HITL
                            if not should_trigger_hitl(file_path) and not is_staging_file:
                                # Auto-approve non-question-paper files and non-staging files
                                decisions.append({"type": "approve"})
                                console_local.print(f"  [dim]✓ Auto-saved: {filename}[/]")
                                continue

                            # This is a staging file - trigger HITL for approval
                            if is_staging_file:
                                hitl_triggered = True

                                # Convert to human-readable format
                                human_readable = convert_json_to_text(json_content)

                                # Show formatted preview
                                console_local.print()
                                console_local.print(
                                    Panel(
                                        human_readable,
                                        title=f"📄 Question Paper Ready for Review (Attempt {rework_count + 1}/{max_rework_attempts})",
                                        border_style="yellow",
                                        padding=(1, 2),
                                    )
                                )

                            # Check if max attempts reached
                            if rework_count >= max_rework_attempts:
                                console_local.print(
                                    f"\n[red]⚠ Maximum rework attempts ({max_rework_attempts}) reached.[/]"
                                )

                                # Ask final time: Force save or cancel?
                                while True:
                                    final_choice = (
                                        console_local.input(
                                            "[bold yellow]Force save this version or cancel? (save/cancel): [/]"
                                        )
                                        .strip()
                                        .lower()
                                    )

                                    if final_choice in ["save", "cancel"]:
                                        break
                                    console_local.print("[red]Please enter 'save' or 'cancel'[/]")

                                if final_choice == "save":
                                    decisions.append({"type": "approve"})
                                    console_local.print("[green]✓ Force saving...[/]")
                                else:
                                    decisions.append({"type": "reject"})
                                    console_local.print("[yellow]✗ Cancelled by teacher[/]")
                                    console_local.print()
                                    console_local.print(
                                        f"[bold red]Generation stopped after {max_rework_attempts} attempts.[/]"
                                    )
                                    return
                            else:
                                # Get teacher approval
                                while True:
                                    approval = (
                                        console_local.input(
                                            "\n[bold yellow]✋ Approve this question paper? (yes/no): [/]"
                                        )
                                        .strip()
                                        .lower()
                                    )

                                    if approval in ["yes", "no"]:
                                        break
                                    console_local.print("[red]Please enter 'yes' or 'no'[/]")

                                if approval == "yes":
                                    decisions.append({"type": "approve"})

                                    # Copy staging file to final filename (Windows-safe approach)
                                    final_path = file_path.replace("preview_", "")
                                    final_filename = Path(final_path).name
                                    try:
                                        import shutil
                                        import time

                                        # Use copy + delete instead of move (avoids Windows file locking issues)
                                        shutil.copy2(file_path, final_path)
                                        time.sleep(0.1)  # Brief pause to ensure copy completes

                                        # Try to delete preview file (may fail if locked, that's OK)
                                        try:
                                            Path(file_path).unlink()
                                            console_local.print(f"[dim]Cleaned up staging file[/]")
                                        except:
                                            pass  # File may be locked, ignore

                                        console_local.print(
                                            f"[green]✓ Teacher approved! Saved to: {final_filename}[/]"
                                        )

                                        # Clean up old preview files (keep only last 3)
                                        cleanup_old_preview_files(output_dir="output")

                                    except Exception as e:
                                        console_local.print(
                                            f"[yellow]⚠ Could not finalize file: {e}[/]"
                                        )
                                        console_local.print(
                                            f"[green]✓ File available at: {filename}[/]"
                                        )

                                else:
                                    # Get specific feedback
                                    rework_count += 1
                                    console_local.print()
                                    console_local.print(
                                        "[yellow]📝 What changes do you want? Be specific:[/]"
                                    )
                                    console_local.print(
                                        "[dim]Examples: 'Change MCQ 3 to Polynomials', 'Make Section B easier', 'Add more Trigonometry'[/]"
                                    )

                                    feedback = console_local.input(
                                        "[bold]Your feedback: [/]"
                                    ).strip()

                                    if not feedback:
                                        feedback = "Improve question quality and variety"

                                    # Reject this write operation
                                    decisions.append({"type": "reject"})
                                    pending_feedback = feedback

                                    console_local.print(
                                        f"\n[yellow]✗ Rejected (attempt {rework_count}/{max_rework_attempts})[/]"
                                    )
                                    console_local.print(f"[cyan]Feedback: {feedback}[/]")
                                    console_local.print(
                                        "[cyan]Agent will rework based on your feedback...[/]"
                                    )
                                    console_local.print()

                    # If HITL was triggered, resume with decisions
                    if hitl_triggered and decisions:
                        # If rejected, add feedback to messages for agent to see
                        if pending_feedback:
                            feedback_instruction = f"""
TEACHER FEEDBACK (Rejection #{rework_count}/{max_rework_attempts}):

The question paper was rejected with the following feedback:
"{pending_feedback}"

ACTION REQUIRED:
1. Read the feedback carefully
2. Identify ONLY the specific questions or sections mentioned
3. Use question-researcher subagent to get new templates for affected questions ONLY
4. Regenerate ONLY the requested changes
5. Keep all other questions exactly as they were
6. Present updated paper for re-approval

IMPORTANT: Only change what teacher requested. Do NOT hallucinate other changes.
"""
                            # Resume with feedback in the message
                            result = await agent.ainvoke(
                                Command(
                                    resume={
                                        "decisions": decisions,
                                        "messages": [
                                            {"role": "user", "content": feedback_instruction}
                                        ],
                                    }
                                ),
                                config=config,
                            )
                            pending_feedback = None
                        else:
                            # Resume normally (approved)
                            result = await agent.ainvoke(
                                Command(resume={"decisions": decisions}), config=config
                            )

                        # Reset for next iteration
                        break
            else:
                # No interrupt, normal completion
                break

    # Count questions from the final paper JSON
    total_questions_generated = 0
    try:
        # Try to find the final output file
        output_files = list(Path("output").glob("*_class*.json"))
        if output_files:
            # Get most recent file
            latest_file = max(output_files, key=lambda f: f.stat().st_mtime)
            with open(latest_file, "r", encoding="utf-8") as f:
                paper_data = json.load(f)
                total_questions_generated = sum(
                    len(section.get("questions", [])) for section in paper_data.get("sections", [])
                )
    except:
        pass

    console_local.print()
    console_local.print(f"[bold green]✓ Generation Complete![/]")
    if total_questions_generated > 0:
        console_local.print(f"[dim]Generated: {total_questions_generated} questions total[/]")
    else:
        console_local.print(f"[dim]Generated: {display.generated_questions} questions total[/]")
    console_local.print(f"[dim]Rework iterations: {rework_count}[/]")

    if display.generated_questions != display.total_questions and display.total_questions > 0:
        console_local.print(f"[yellow]Note: Generation may not have completed fully[/]")


def create_agent():
    """Create and configure the CBSE Question Paper Generator agent."""
    from deepagents import create_deep_agent
    from deepagents.backends.filesystem import FilesystemBackend
    from langgraph.checkpoint.memory import MemorySaver
    from src.config.agent_config import get_subagent_definitions, get_tools, configure_interrupt_on

    project_root = Path(__file__).parent.parent.absolute()
    subagents = get_subagent_definitions()
    tools = get_tools()

    return create_deep_agent(
        model="openai:gpt-5-mini",
        backend=FilesystemBackend(root_dir=project_root, virtual_mode=True),
        memory=["./AGENTS.md"],
        skills=["./src/skills/"],
        subagents=subagents,
        tools=tools,
        # Enable standard HITL for write_file - custom handling in run_agent_with_live_display()
        # filters to show preview only for question papers, auto-approves other files
        interrupt_on=configure_interrupt_on(),
        checkpointer=MemorySaver(),
    )


async def main_async():
    import sys
    import os

    if len(sys.argv) > 1:
        short_task = " ".join(sys.argv[1:])
    else:
        short_task = "Generate a CBSE question paper"

    try:
        blueprint_path = find_blueprint_path(short_task)
        display_blueprint_info(blueprint_path)

        # Generate output filename for reference
        with open(blueprint_path, "r", encoding="utf-8") as f:
            blueprint_data = json.load(f)
        output_filename = generate_output_filename(blueprint_path, blueprint_data)
        preview_filename = output_filename.replace("output/", "output/preview_")

        task = f"""Generate a CBSE question paper using blueprint {blueprint_path}:
        1. Read and validate the blueprint from {blueprint_path}
        2. Generate questions for each section based on blueprint
        3. Validate the final paper matches blueprint
        4. Write the paper to: {preview_filename}
           (Use "preview_" prefix - this is a staging file for teacher approval)
        5. Wait for teacher approval. If rejected, make targeted changes and write new preview file.
        6. Once approved, the system will automatically move it to final location: {output_filename}"""

        if not os.environ.get("OPENAI_API_KEY"):
            console.print("[red]Error: OPENAI_API_KEY not set in environment[/]")
            console.print("Please set: export OPENAI_API_KEY=your-key")
            sys.exit(1)

        if not os.environ.get("TAVILY_API_KEY"):
            console.print("[yellow]Warning: TAVILY_API_KEY not set - curriculum search disabled[/]")

        print("Creating CBSE Question Paper Generator agent...")
        agent = create_agent()
        print("Agent created successfully!")
        print()

        await run_agent_with_live_display(
            agent, task, blueprint_path, thread_id="cbse-math-paper-session-001"
        )

    except FileNotFoundError as e:
        handle_blueprint_error(e)
        sys.exit(1)
    except KeyboardInterrupt:
        console.print()
        console.print("[yellow]Interrupted by user[/]")
    except Exception as e:
        console.print()
        console.print(f"[red]Unexpected Error: {e}[/]")
        import traceback

        console.print(traceback.format_exc())
        sys.exit(1)


def main():
    try:
        asyncio.run(main_async())
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
