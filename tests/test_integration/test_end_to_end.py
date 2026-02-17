"""End-to-end integration test for CBSE Question Paper Generator.

This test performs a complete integration test in 3 phases:
1. Phase 1: Read and parse the input blueprint
2. Phase 2: Connect to Qdrant and retrieve chunks for all questions
3. Phase 3: Generate questions using LLM (real or mock based on config)

Outputs:
- output/test_retrieved_chunks.json: All retrieved chunks from Qdrant
- output/test_generated_questions.json: Complete assembled question paper
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cbse_question_retriever.settings import settings
from cbse_question_retriever.tool import generate_question_tool
from cbse_question_retriever.llm_question_generator import generate_llm_question_tool
from question_assembler.tool import assemble_question_tool
from tests.test_integration.mock_llm_loader import get_mock_loader

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
BLUEPRINT_PATH = "input/classes/10/mathematics/input_first_term.json"
OUTPUT_DIR = "output"
CHUNKS_OUTPUT_FILE = f"{OUTPUT_DIR}/test_retrieved_chunks.json"
QUESTIONS_OUTPUT_FILE = f"{OUTPUT_DIR}/test_generated_questions.json"


class QuestionPaperIntegrationTest:
    """End-to-end integration test for question paper generation."""

    def __init__(self):
        """Initialize the test."""
        self.blueprint: Dict[str, Any] = {}
        self.retrieved_chunks: List[Dict[str, Any]] = []
        self.generated_questions: List[Dict[str, Any]] = []
        self.mock_loader = get_mock_loader(settings.mock_llm_responses_path)
        self.use_real_openai = settings.use_real_openai

        logger.info(f"Integration test initialized")
        logger.info(f"USE_REAL_OPENAI: {self.use_real_openai}")
        logger.info(f"Qdrant host: {settings.qdrant.host}:{settings.qdrant.http_port}")

    # =========================================================================
    # PHASE 1: Read Blueprint
    # =========================================================================
    def phase_1_read_blueprint(self) -> bool:
        """Phase 1: Read and parse the input blueprint.

        Returns:
            True if blueprint loaded successfully
        """
        logger.info("=" * 70)
        logger.info("PHASE 1: Reading Blueprint")
        logger.info("=" * 70)

        try:
            blueprint_path = Path(BLUEPRINT_PATH)

            if not blueprint_path.exists():
                logger.error(f"Blueprint file not found: {BLUEPRINT_PATH}")
                return False

            with open(blueprint_path, "r", encoding="utf-8") as f:
                self.blueprint = json.load(f)

            # Log blueprint summary
            metadata = self.blueprint.get("metadata", {})
            sections = self.blueprint.get("sections", [])

            logger.info(f"Blueprint loaded successfully")
            logger.info(f"  Class: {metadata.get('class')}")
            logger.info(f"  Subject: {metadata.get('subject')}")
            logger.info(f"  Total Marks: {metadata.get('total_marks')}")
            logger.info(f"  Sections: {len(sections)}")

            # Count total questions
            total_questions = sum(s.get("questions_provided", 0) for s in sections)
            logger.info(f"  Total Questions to Generate: {total_questions}")

            return True

        except Exception as e:
            logger.error(f"Error reading blueprint: {e}")
            return False

    # =========================================================================
    # PHASE 2: Connect to Qdrant and Retrieve Chunks
    # =========================================================================
    def phase_2_retrieve_chunks(self) -> bool:
        """Phase 2: Connect to Qdrant and retrieve chunks for all questions.

        Returns:
            True if all chunks retrieved successfully
        """
        logger.info("=" * 70)
        logger.info("PHASE 2: Retrieving Chunks from Qdrant")
        logger.info("=" * 70)

        if not self.blueprint:
            logger.error("No blueprint loaded. Run phase 1 first.")
            return False

        sections = self.blueprint.get("sections", [])

        for section in sections:
            section_id = section.get("section_id")
            questions_count = section.get("questions_provided", 0)

            logger.info(f"\nProcessing Section {section_id}: {questions_count} questions")

            for q_num in range(1, questions_count + 1):
                try:
                    logger.info(
                        f"  Retrieving question {q_num}/{questions_count} from section {section_id}..."
                    )

                    # Call the retrieval tool
                    result = generate_question_tool.func(
                        blueprint_path=BLUEPRINT_PATH,
                        section_id=section_id,
                        question_number=q_num,
                    )

                    # Store retrieval result (both success and failure)
                    retrieval_data = {
                        "question_id": result.get("question_id")
                        if not result.get("error")
                        else f"{section_id}-{q_num:03d}",
                        "section_id": section_id,
                        "question_number": q_num,
                        "chapter": result.get("chapter", ""),
                        "topic": result.get("topic", ""),
                        "question_format": result.get(
                            "question_format", section.get("question_format", "MCQ")
                        ),
                        "marks": result.get("marks", section.get("marks_per_question", 1)),
                        "difficulty": result.get("difficulty", "medium"),
                        "bloom_level": result.get("bloom_level", "understand"),
                        "nature": result.get("nature", "NUMERICAL"),
                        "chunks_used": result.get("chunks_used", 0),
                        "chunks": result.get("chunks", []),
                        "blueprint_reference": result.get(
                            "blueprint_reference",
                            {
                                "section_id": section_id,
                                "class": self.blueprint.get("metadata", {}).get("class", 10),
                                "subject": self.blueprint.get("metadata", {}).get(
                                    "subject", "Mathematics"
                                ),
                            },
                        ),
                        "retrieval_metadata": result.get("retrieval_metadata", {}),
                        "error": result.get("error"),
                    }

                    self.retrieved_chunks.append(retrieval_data)

                    if result.get("error"):
                        logger.error(f"    ERROR: {result['error']} (stored for error reporting)")
                    else:
                        logger.info(f"    SUCCESS: Retrieved {result.get('chunks_used', 0)} chunks")

                except Exception as e:
                    logger.error(f"    ERROR retrieving question {q_num}: {e}")

        logger.info(
            f"\nPhase 2 Complete: Retrieved chunks for {len(self.retrieved_chunks)} questions"
        )
        return len(self.retrieved_chunks) > 0

    # =========================================================================
    # PHASE 3: Generate Questions using LLM
    # =========================================================================
    def phase_3_generate_questions(self) -> bool:
        """Phase 3: Generate questions using LLM (real or mock).

        Returns:
            True if all questions generated successfully
        """
        logger.info("=" * 70)
        logger.info("PHASE 3: Generating Questions")
        logger.info("=" * 70)
        logger.info(f"Mode: {'REAL OpenAI API' if self.use_real_openai else 'MOCK Responses'}")

        if not self.retrieved_chunks:
            logger.error("No chunks retrieved. Run phase 2 first.")
            return False

        generated_count = 0
        mock_responses_to_save: Dict[str, Any] = {}

        for retrieval_data in self.retrieved_chunks:
            question_id = retrieval_data.get("question_id")
            section_id = retrieval_data.get("section_id")
            q_num = retrieval_data.get("question_number")

            try:
                logger.info(
                    f"\n  Generating question {question_id} (Section {section_id}, Q{q_num})..."
                )

                # Build blueprint context for LLM
                retrieval_error = retrieval_data.get("error")
                blueprint_context = {
                    "class_level": retrieval_data.get("blueprint_reference", {}).get("class", 10),
                    "subject": retrieval_data.get("blueprint_reference", {}).get(
                        "subject", "Mathematics"
                    ),
                    "chapter": retrieval_data.get("chapter"),
                    "topic": retrieval_data.get("topic"),
                    "question_format": retrieval_data.get("question_format"),
                    "marks": retrieval_data.get("marks"),
                    "difficulty": retrieval_data.get("difficulty"),
                    "bloom_level": retrieval_data.get("bloom_level"),
                    "nature": retrieval_data.get("nature"),
                    "section_title": section_id,
                    "retrieval_error": retrieval_error,  # Pass retrieval error to LLM
                }

                # Get chunks for LLM
                chunks = retrieval_data.get("chunks", [])

                # Generate question using LLM or mock
                if retrieval_error:
                    # Skip LLM generation if retrieval failed
                    logger.info(f"    Skipping LLM generation due to retrieval error")
                    llm_result = {
                        "question_id": question_id,
                        "question_text": f"[RETRIEVAL ERROR: {retrieval_error}]",
                        "options": None,
                        "correct_answer": None,
                        "explanation": None,
                        "diagram_needed": False,
                        "diagram_description": None,
                        "hints": [],
                        "prerequisites": [],
                        "common_mistakes": [],
                        "quality_score": None,
                        "generation_metadata": {
                            "error": True,
                            "error_phase": "retrieval",
                            "error_message": retrieval_error,
                        },
                        "error": retrieval_error,
                        "error_phase": "retrieval",
                    }
                elif self.use_real_openai:
                    # Real LLM call
                    logger.info(f"    Calling OpenAI API...")
                    llm_result = generate_llm_question_tool.func(
                        chunks=chunks,
                        blueprint_context=blueprint_context,
                        question_id=question_id,
                    )

                    # Save for later mock generation
                    mock_responses_to_save[question_id] = llm_result

                else:
                    # Use mock response
                    logger.info(f"    Using mock response...")
                    llm_result = self.mock_loader.get_mock_response(
                        question_id=question_id,
                        question_format=blueprint_context["question_format"],
                        topic=blueprint_context["topic"],
                        chapter=blueprint_context["chapter"],
                    )

                if llm_result.get("error") and not retrieval_error:
                    logger.error(f"    LLM ERROR: {llm_result['error']}")

                # Assemble the final question (handles both success and error cases)
                logger.info(f"    Assembling question...")
                assembled = assemble_question_tool.func(
                    retrieval_result=retrieval_data,
                    llm_result=llm_result,
                    question_number=q_num,
                )

                if assembled.get("error"):
                    logger.error(f"    ASSEMBLY ERROR: {assembled['error']}")

                self.generated_questions.append(assembled)

                if assembled.get("status") == "success":
                    generated_count += 1
                    has_diagram = assembled.get("has_diagram", False)
                    diagram_status = "(with diagram)" if has_diagram else "(no diagram)"
                    logger.info(f"    SUCCESS: Generated question {diagram_status}")
                else:
                    logger.info(f"    FAILED: {assembled.get('error_phase', 'unknown')} error")

                # Log success details
                has_diagram = assembled.get("has_diagram", False)
                diagram_status = "(with diagram)" if has_diagram else "(no diagram)"
                logger.info(f"    SUCCESS: Generated question {diagram_status}")

            except Exception as e:
                logger.error(f"    ERROR generating question {question_id}: {e}")
                import traceback

                logger.error(traceback.format_exc())

        # Save mock responses if we used real API (for future use)
        if self.use_real_openai and mock_responses_to_save:
            mock_output_path = settings.mock_llm_responses_path
            logger.info(
                f"\n  Saving {len(mock_responses_to_save)} real responses to {mock_output_path}"
            )
            self.mock_loader.save_mock_responses(mock_responses_to_save, mock_output_path)

        logger.info(
            f"\nPhase 3 Complete: Generated {generated_count}/{len(self.retrieved_chunks)} questions"
        )
        return generated_count > 0

    # =========================================================================
    # Save Results
    # =========================================================================
    def save_results(self) -> bool:
        """Save the test results to output files.

        Returns:
            True if files saved successfully
        """
        logger.info("=" * 70)
        logger.info("SAVING RESULTS")
        logger.info("=" * 70)

        try:
            # Create output directory
            Path(OUTPUT_DIR).mkdir(exist_ok=True)

            # Save retrieved chunks
            chunks_output = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "blueprint_path": BLUEPRINT_PATH,
                    "total_questions": len(self.retrieved_chunks),
                    "use_real_openai": self.use_real_openai,
                },
                "questions": self.retrieved_chunks,
            }

            with open(CHUNKS_OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(chunks_output, f, indent=2, ensure_ascii=False)

            logger.info(f"  Saved retrieved chunks to: {CHUNKS_OUTPUT_FILE}")

            # Save generated questions (organized by section)
            sections_map: Dict[str, List[Dict]] = {}
            for q in self.generated_questions:
                section_id = (
                    q.get("question_id", "").split("-")[-2] if q.get("question_id") else "UNKNOWN"
                )
                # Extract section from question_id (format: MATH-10-XXX-FMT-NNN)
                # Actually we need to get it from the retrieval data
                # Let's find the matching retrieval data
                q_id = q.get("question_id")
                for retrieval in self.retrieved_chunks:
                    if retrieval.get("question_id") == q_id:
                        section_id = retrieval.get("section_id", "UNKNOWN")
                        break

                if section_id not in sections_map:
                    sections_map[section_id] = []
                sections_map[section_id].append(q)

            # Build sections list
            sections_output = []
            for section in self.blueprint.get("sections", []):
                section_id = section.get("section_id")
                questions = sections_map.get(section_id, [])

                section_output = {
                    "section_id": section_id,
                    "title": section.get("title"),
                    "question_format": section.get("question_format"),
                    "marks_per_question": section.get("marks_per_question"),
                    "questions_provided": section.get("questions_provided"),
                    "questions_attempt": section.get("questions_attempt"),
                    "questions": questions,
                }
                sections_output.append(section_output)

            questions_output = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "blueprint_path": BLUEPRINT_PATH,
                    "class": self.blueprint.get("metadata", {}).get("class"),
                    "subject": self.blueprint.get("metadata", {}).get("subject"),
                    "total_marks": self.blueprint.get("metadata", {}).get("total_marks"),
                    "total_questions_generated": len(self.generated_questions),
                    "use_real_openai": self.use_real_openai,
                },
                "sections": sections_output,
            }

            with open(QUESTIONS_OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(questions_output, f, indent=2, ensure_ascii=False)

            logger.info(f"  Saved generated questions to: {QUESTIONS_OUTPUT_FILE}")

            return True

        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return False

    # =========================================================================
    # Run Complete Test
    # =========================================================================
    def run(self) -> bool:
        """Run the complete integration test.

        Returns:
            True if all phases completed successfully
        """
        logger.info("\n" + "=" * 70)
        logger.info("CBSE QUESTION PAPER GENERATOR - INTEGRATION TEST")
        logger.info("=" * 70)

        # Phase 1: Read blueprint
        if not self.phase_1_read_blueprint():
            logger.error("Phase 1 FAILED")
            return False

        # Phase 2: Retrieve chunks
        if not self.phase_2_retrieve_chunks():
            logger.error("Phase 2 FAILED")
            return False

        # Phase 3: Generate questions
        if not self.phase_3_generate_questions():
            logger.error("Phase 3 FAILED")
            return False

        # Save results
        if not self.save_results():
            logger.error("Save results FAILED")
            return False

        logger.info("\n" + "=" * 70)
        logger.info("INTEGRATION TEST COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)
        logger.info(f"Total questions generated: {len(self.generated_questions)}")
        logger.info(f"Output files:")
        logger.info(f"  - {CHUNKS_OUTPUT_FILE}")
        logger.info(f"  - {QUESTIONS_OUTPUT_FILE}")

        return True


def main():
    """Main entry point for the integration test."""
    test = QuestionPaperIntegrationTest()
    success = test.run()

    if success:
        logger.info("\nTest PASSED")
        sys.exit(0)
    else:
        logger.error("\nTest FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
