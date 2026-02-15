"""Chunk mixing strategy for different question formats."""

import logging
from typing import Dict, List

from cbse_question_retriever.data_types import Chunk, ChunkMixConfig, ChunkType, CHUNK_MIX_CONFIGS

logger = logging.getLogger(__name__)


class ChunkMixer:
    """Mixes and ranks chunks based on question format."""

    def mix_chunks(
        self,
        chunks: List[Chunk],
        question_format: str,
    ) -> List[Chunk]:
        """Mix chunks according to question format strategy.

        Args:
            chunks: List of retrieved chunks
            question_format: Question format (MCQ, VERY_SHORT, SHORT, LONG, CASE_STUDY)

        Returns:
            Mixed and ranked list of chunks
        """
        # Get mixing configuration for this format
        from cbse_question_retriever.data_types import QuestionFormat

        format_enum = QuestionFormat(question_format.upper())
        config = CHUNK_MIX_CONFIGS.get(
            format_enum,
            CHUNK_MIX_CONFIGS[QuestionFormat.MCQ],  # Default to MCQ config
        )

        # Group chunks by type
        theory_chunks = [c for c in chunks if c.chunk_type == ChunkType.THEORY]
        worked_chunks = [c for c in chunks if c.chunk_type == ChunkType.WORKED_EXAMPLE]
        exercise_chunks = [c for c in chunks if c.chunk_type == ChunkType.EXERCISE_PATTERN]

        # Sort each group by similarity score (descending)
        theory_chunks = self._sort_by_score(theory_chunks)
        worked_chunks = self._sort_by_score(worked_chunks)
        exercise_chunks = self._sort_by_score(exercise_chunks)

        # Calculate how many of each type to include
        total = config.total_chunks
        theory_count = int(total * config.theory_ratio)
        worked_count = int(total * config.worked_example_ratio)
        exercise_count = total - theory_count - worked_count  # Remainder

        # Select top chunks from each category
        selected_theory = theory_chunks[:theory_count]
        selected_worked = worked_chunks[:worked_count]
        selected_exercise = exercise_chunks[:exercise_count]

        # Interleave chunks for variety: Theory -> Worked -> Exercise -> Theory -> ...
        mixed = []
        max_len = max(len(selected_theory), len(selected_worked), len(selected_exercise))

        for i in range(max_len):
            if i < len(selected_theory):
                mixed.append(selected_theory[i])
            if i < len(selected_worked):
                mixed.append(selected_worked[i])
            if i < len(selected_exercise):
                mixed.append(selected_exercise[i])

        # Trim to exact count
        mixed = mixed[: config.total_chunks]

        logger.info(
            f"Mixed chunks for {question_format}: "
            f"{len(selected_theory)} theory, "
            f"{len(selected_worked)} worked examples, "
            f"{len(selected_exercise)} exercises"
        )

        return mixed

    def _sort_by_score(self, chunks: List[Chunk]) -> List[Chunk]:
        """Sort chunks by similarity score (highest first).

        Args:
            chunks: List of chunks

        Returns:
            Sorted list
        """
        return sorted(chunks, key=lambda c: c.score or 0.0, reverse=True)


# Global chunk mixer instance
chunk_mixer = ChunkMixer()
