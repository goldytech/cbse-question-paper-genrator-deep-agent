"""Type definitions for CBSE Question Retriever."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class ChunkType(str, Enum):
    """Types of content chunks."""

    THEORY = "THEORY"
    WORKED_EXAMPLE = "WORKED_EXAMPLE"
    EXERCISE_PATTERN = "EXERCISE_PATTERN"


class QuestionFormat(str, Enum):
    """Question formats from blueprint."""

    MCQ = "MCQ"
    VERY_SHORT = "VERY_SHORT"
    SHORT = "SHORT"
    LONG = "LONG"
    CASE_STUDY = "CASE_STUDY"


@dataclass
class Chunk:
    """Represents a chunk of textbook content from Qdrant."""

    id: str
    text: str
    chapter: str
    section: str
    topic: str
    chunk_type: ChunkType
    page_start: int
    page_end: int
    score: Optional[float] = None  # Similarity score from vector search
    vector: Optional[List[float]] = None  # Optional: for testing


@dataclass
class RetrievedData:
    """Complete retrieval result with metadata."""

    question_id: str
    chapter: str
    topic: str
    question_format: str
    marks: int
    difficulty: str
    bloom_level: str
    nature: str
    has_diagram: bool
    chunks_used: int
    chunks: List[Chunk]
    blueprint_reference: Dict[str, Any]
    retrieval_metadata: Dict[str, Any]
    error: Optional[str] = None


@dataclass
class BlueprintSection:
    """Extracted section data from blueprint."""

    section_id: str
    title: str
    question_format: str
    marks_per_question: int
    questions_provided: int
    questions_attempt: int
    allowed_question_natures: List[str]
    cognitive_level_hint: List[str]
    topic_focus: List[str]


@dataclass
class BlueprintMetadata:
    """Metadata from blueprint."""

    class_level: int
    subject: str
    assessment_type: str
    total_marks: int
    chapters: List[Dict[str, Any]]


@dataclass
class ChunkMixConfig:
    """Configuration for mixing chunks."""

    theory_ratio: float = 0.4
    worked_example_ratio: float = 0.4
    exercise_ratio: float = 0.2
    total_chunks: int = 10


# Chunk mixing configurations by question format
CHUNK_MIX_CONFIGS = {
    QuestionFormat.MCQ: ChunkMixConfig(
        theory_ratio=0.5, worked_example_ratio=0.3, exercise_ratio=0.2, total_chunks=10
    ),
    QuestionFormat.VERY_SHORT: ChunkMixConfig(
        theory_ratio=0.4, worked_example_ratio=0.4, exercise_ratio=0.2, total_chunks=10
    ),
    QuestionFormat.SHORT: ChunkMixConfig(
        theory_ratio=0.3, worked_example_ratio=0.5, exercise_ratio=0.2, total_chunks=10
    ),
    QuestionFormat.LONG: ChunkMixConfig(
        theory_ratio=0.2, worked_example_ratio=0.6, exercise_ratio=0.2, total_chunks=10
    ),
    QuestionFormat.CASE_STUDY: ChunkMixConfig(
        theory_ratio=0.3, worked_example_ratio=0.5, exercise_ratio=0.2, total_chunks=10
    ),
}


# Chapter abbreviations for question ID generation
CHAPTER_ABBREVIATIONS = {
    "real numbers": "REA",
    "polynomials": "POL",
    "pair of linear equations in two variables": "LIN",
    "quadratic equations": "QUAD",
    "arithmetic progressions": "AP",
    "coordinate geometry": "COG",
    "triangles": "TRI",
    "circles": "CIR",
    "constructions": "CON",
    "mensuration": "MEN",
    "statistics": "STA",
    "probability": "PRO",
    "introduction to trigonometry": "TRI",
    "some applications of trigonometry": "APP",
}


# Format abbreviations for question ID generation
FORMAT_ABBREVIATIONS = {
    "MCQ": "MCQ",
    "VERY_SHORT": "VSQ",
    "SHORT": "SA",
    "LONG": "LA",
    "CASE_STUDY": "CS",
}


# Subject abbreviations for question ID generation
SUBJECT_ABBREVIATIONS = {
    "mathematics": "MATH",
    "science": "SCI",
    "english": "ENG",
    "physics": "PHY",
    "chemistry": "CHEM",
    "biology": "BIO",
    "history": "HIST",
    "geography": "GEO",
    "social science": "SST",
    "computer science": "CS",
}
