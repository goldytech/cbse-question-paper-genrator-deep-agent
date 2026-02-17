"""Data types for Question Assembler."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AssembledQuestion:
    """Represents a fully assembled CBSE question."""

    question_id: str
    question_text: str
    chapter: str
    topic: str
    question_format: str
    marks: int
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    difficulty: str = "medium"
    bloom_level: str = "understand"
    nature: str = "NUMERICAL"
    has_diagram: bool = False
    diagram_type: Optional[str] = None
    diagram_svg_base64: Optional[str] = None
    diagram_description: Optional[str] = None
    diagram_elements: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None
    hints: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    quality_score: Optional[float] = None
    generation_metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
