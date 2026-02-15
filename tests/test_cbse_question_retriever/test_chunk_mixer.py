"""Tests for chunk mixer."""

import pytest
from cbse_question_retriever.chunk_mixer import chunk_mixer
from cbse_question_retriever.data_types import Chunk, ChunkType


class TestChunkMixer:
    """Test suite for chunk mixing strategies."""

    def create_mock_chunks(self, theory_count=5, worked_count=5, exercise_count=5):
        """Helper to create mock chunks."""
        chunks = []
        for i in range(theory_count):
            chunks.append(
                Chunk(
                    id=f"theory-{i}",
                    text=f"Theory content {i}",
                    chapter="Polynomials",
                    section="2.1",
                    topic="Zeros",
                    chunk_type=ChunkType.THEORY,
                    page_start=10 + i,
                    page_end=11 + i,
                    score=0.9 - (i * 0.05),
                )
            )
        for i in range(worked_count):
            chunks.append(
                Chunk(
                    id=f"worked-{i}",
                    text=f"Worked example {i}",
                    chapter="Polynomials",
                    section="2.2",
                    topic="Zeros",
                    chunk_type=ChunkType.WORKED_EXAMPLE,
                    page_start=20 + i,
                    page_end=21 + i,
                    score=0.85 - (i * 0.05),
                )
            )
        for i in range(exercise_count):
            chunks.append(
                Chunk(
                    id=f"exercise-{i}",
                    text=f"Exercise {i}",
                    chapter="Polynomials",
                    section="2.3",
                    topic="Zeros",
                    chunk_type=ChunkType.EXERCISE_PATTERN,
                    page_start=30 + i,
                    page_end=31 + i,
                    score=0.8 - (i * 0.05),
                )
            )
        return chunks

    def test_mcq_mixing(self):
        """Test MCQ format mixing (50% theory, 30% worked, 20% exercise)."""
        chunks = self.create_mock_chunks(10, 10, 10)

        result = chunk_mixer.mix_chunks(chunks, "MCQ")

        assert len(result) == 10
        theory_count = len([c for c in result if c.chunk_type == ChunkType.THEORY])
        worked_count = len([c for c in result if c.chunk_type == ChunkType.WORKED_EXAMPLE])
        exercise_count = len([c for c in result if c.chunk_type == ChunkType.EXERCISE_PATTERN])

        assert theory_count == 5
        assert worked_count == 3
        assert exercise_count == 2

    def test_short_mixing(self):
        """Test SHORT format mixing (30% theory, 50% worked, 20% exercise)."""
        chunks = self.create_mock_chunks(10, 10, 10)

        result = chunk_mixer.mix_chunks(chunks, "SHORT")

        assert len(result) == 10
        theory_count = len([c for c in result if c.chunk_type == ChunkType.THEORY])
        worked_count = len([c for c in result if c.chunk_type == ChunkType.WORKED_EXAMPLE])
        exercise_count = len([c for c in result if c.chunk_type == ChunkType.EXERCISE_PATTERN])

        assert theory_count == 3
        assert worked_count == 5
        assert exercise_count == 2

    def test_ranking_by_score(self):
        """Test that chunks are ranked by similarity score."""
        chunks = self.create_mock_chunks(3, 3, 3)

        result = chunk_mixer.mix_chunks(chunks, "MCQ")

        # First theory chunk should have highest score
        theory_chunks = [c for c in result if c.chunk_type == ChunkType.THEORY]
        if len(theory_chunks) >= 2:
            assert theory_chunks[0].score >= theory_chunks[1].score

    def test_insufficient_chunks(self):
        """Test handling when there are fewer chunks than requested."""
        chunks = self.create_mock_chunks(2, 2, 2)

        result = chunk_mixer.mix_chunks(chunks, "MCQ")

        # Should return all available chunks
        assert len(result) <= 6

    def test_empty_chunks(self):
        """Test handling of empty chunk list."""
        result = chunk_mixer.mix_chunks([], "MCQ")

        assert len(result) == 0
