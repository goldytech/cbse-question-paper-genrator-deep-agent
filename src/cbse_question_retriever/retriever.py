"""Main retrieval orchestrator for CBSE Question Retriever."""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

from .chunk_mixer import chunk_mixer
from .embedder import embedding_generator
from .fuzzy_matcher import fuzzy_matcher
from .qdrant_client import qdrant_manager
from .question_id_generator import question_id_generator
from .settings import settings
from .data_types import (
    BlueprintMetadata,
    BlueprintSection,
    Chunk,
    RetrievedData,
)

logger = logging.getLogger(__name__)


class BlueprintRetriever:
    """Retrieves textbook chunks based on blueprint specifications."""

    def retrieve(
        self,
        blueprint_path: str,
        section_id: str,
        question_number: int,
    ) -> RetrievedData:
        """Main retrieval method.

        Args:
            blueprint_path: Path to blueprint JSON file
            section_id: Section identifier ("A", "B", "C", "D")
            question_number: Question number within section (1-based)

        Returns:
            RetrievedData with chunks and metadata
        """
        try:
            # Step 1: Load and parse blueprint
            blueprint = self._load_blueprint(blueprint_path)
            metadata = self._extract_metadata(blueprint)
            section = self._get_section(blueprint, section_id)

            # Step 2: Determine collection name
            collection_name = f"{metadata.subject.lower()}_{metadata.class_level}"

            # Step 3: Check if collection exists
            if not qdrant_manager.check_collection_exists(collection_name):
                available = qdrant_manager.get_available_collections()
                return self._create_error_response(
                    section,
                    f"Collection '{collection_name}' not found. Available: {available}",
                )

            # Step 4: Determine topic for this question
            topic_index = (question_number - 1) % len(section.topic_focus)
            topic = section.topic_focus[topic_index]
            chapter = self._find_chapter_for_topic(metadata, topic)

            if not chapter:
                return self._create_error_response(
                    section,
                    f"Topic '{topic}' not found in any chapter of syllabus scope",
                )

            # Step 5: Fuzzy match topic to available topics in Qdrant
            available_topics = qdrant_manager.get_distinct_topics(collection_name, chapter)
            matched_topic, match_score, suggestions = fuzzy_matcher.find_best_match(
                topic, available_topics
            )

            if not matched_topic:
                return self._create_error_response(
                    section,
                    f"Topic '{topic}' not found. Did you mean: {', '.join(suggestions[:3])}?",
                )

            # Step 6: Generate query embedding
            cognitive_level = section.cognitive_level_hint[
                topic_index % len(section.cognitive_level_hint)
            ]
            query_text = f"{chapter} {matched_topic} {cognitive_level}"
            query_vector = embedding_generator.generate_embedding(query_text)

            # Step 7: Search Qdrant with hybrid approach
            filter_conditions = {"chapter": chapter}
            raw_chunks = qdrant_manager.search_by_vector(
                collection_name=collection_name,
                query_vector=query_vector,
                filter_conditions=filter_conditions,
                limit=settings.retrieval.max_chunks * 2,  # Get extra for mixing
            )

            if not raw_chunks:
                return self._create_error_response(
                    section,
                    f"No content found for {chapter}/{matched_topic}",
                )

            # Step 8: Mix chunks based on question format
            mixed_chunks = chunk_mixer.mix_chunks(raw_chunks, section.question_format)

            # Step 9: Generate question ID
            question_id = question_id_generator.generate_id(
                subject=metadata.subject,
                class_level=metadata.class_level,
                chapter=chapter,
                question_format=section.question_format,
                question_number=question_number,
            )

            # Step 10: Determine difficulty and nature
            difficulty = self._calculate_difficulty(section, question_number)
            nature = section.allowed_question_natures[
                topic_index % len(section.allowed_question_natures)
            ]

            # Step 11: Build response
            return RetrievedData(
                question_id=question_id,
                chapter=chapter,
                topic=matched_topic,
                question_format=section.question_format,
                marks=section.marks_per_question,
                difficulty=difficulty,
                bloom_level=cognitive_level,
                nature=nature,
                has_diagram=False,  # Will be detected by question assembler or LLM
                chunks_used=len(mixed_chunks),
                chunks=mixed_chunks,
                blueprint_reference={
                    "section_id": section.section_id,
                    "section_title": section.title,
                    "cognitive_level_hint": section.cognitive_level_hint,
                    "allowed_question_natures": section.allowed_question_natures,
                },
                retrieval_metadata={
                    "collection": collection_name,
                    "embedding_model": settings.openai.embedding_model,
                    "query_text": query_text,
                    "topic_match_score": match_score,
                    "chunks_theory": len(
                        [c for c in mixed_chunks if c.chunk_type.value == "THEORY"]
                    ),
                    "chunks_worked_example": len(
                        [c for c in mixed_chunks if c.chunk_type.value == "WORKED_EXAMPLE"]
                    ),
                    "chunks_exercise": len(
                        [c for c in mixed_chunks if c.chunk_type.value == "EXERCISE_PATTERN"]
                    ),
                },
                error=None,
            )

        except FileNotFoundError as e:
            return self._create_error_response(None, f"Blueprint file not found: {e}")
        except json.JSONDecodeError as e:
            return self._create_error_response(None, f"Invalid JSON in blueprint: {e}")
        except Exception as e:
            logger.exception("Unexpected error during retrieval")
            return self._create_error_response(None, f"Retrieval error: {e}")

    def _load_blueprint(self, blueprint_path: str) -> Dict[str, Any]:
        """Load blueprint JSON file."""
        with open(blueprint_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _extract_metadata(self, blueprint: Dict[str, Any]) -> BlueprintMetadata:
        """Extract metadata from blueprint."""
        meta = blueprint.get("metadata", {})
        return BlueprintMetadata(
            class_level=meta.get("class", 10),
            subject=meta.get("subject", ""),
            assessment_type=meta.get("assessment_type", ""),
            total_marks=meta.get("total_marks", 0),
            chapters=blueprint.get("syllabus_scope", {}).get("chapters", []),
        )

    def _get_section(self, blueprint: Dict[str, Any], section_id: str) -> BlueprintSection:
        """Get section by ID from blueprint."""
        sections = blueprint.get("sections", [])
        for section in sections:
            if section.get("section_id") == section_id:
                return BlueprintSection(
                    section_id=section_id,
                    title=section.get("title", ""),
                    question_format=section.get("question_format", "MCQ"),
                    marks_per_question=section.get("marks_per_question", 1),
                    questions_provided=section.get("questions_provided", 0),
                    questions_attempt=section.get("questions_attempt", 0),
                    allowed_question_natures=section.get("allowed_question_natures", ["NUMERICAL"]),
                    cognitive_level_hint=section.get("cognitive_level_hint", ["REMEMBER"]),
                    topic_focus=section.get("topic_focus", []),
                )
        raise ValueError(f"Section '{section_id}' not found in blueprint")

    def _find_chapter_for_topic(self, metadata: BlueprintMetadata, topic: str) -> Optional[str]:
        """Find which chapter contains a given topic."""
        for chapter_data in metadata.chapters:
            chapter_name = chapter_data.get("chapter_name", "")
            topics = chapter_data.get("topics", [])
            if topic in topics:
                return chapter_name
        return None

    def _calculate_difficulty(self, section: BlueprintSection, question_number: int) -> str:
        """Calculate difficulty based on position in section.

        Uses 40/40/20 distribution: easy/medium/hard
        """
        total = section.questions_provided
        if total == 0:
            return "medium"

        easy_count = int(total * 0.4)
        medium_count = int(total * 0.4)
        # hard gets the remainder

        if question_number <= easy_count:
            return "easy"
        elif question_number <= easy_count + medium_count:
            return "medium"
        else:
            return "hard"

    def _create_error_response(
        self,
        section: Optional[BlueprintSection],
        error_message: str,
    ) -> RetrievedData:
        """Create error response."""
        logger.error(f"Retrieval error: {error_message}")

        return RetrievedData(
            question_id="",
            chapter="",
            topic="",
            question_format=section.question_format if section else "MCQ",
            marks=section.marks_per_question if section else 0,
            difficulty="",
            bloom_level="",
            nature="",
            has_diagram=False,
            chunks_used=0,
            chunks=[],
            blueprint_reference={}
            if not section
            else {
                "section_id": section.section_id,
                "section_title": section.title,
            },
            retrieval_metadata={},
            error=error_message,
        )


# Global retriever instance
retriever = BlueprintRetriever()
