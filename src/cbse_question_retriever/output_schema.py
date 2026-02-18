"""Pydantic models for structured LLM output.

These models define the schema for question generation responses,
enabling LangChain's structured output feature.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class QuestionOutput(BaseModel):
    """Schema for LLM question generation output.

    This model ensures the LLM returns properly structured JSON
    that can be directly parsed without manual repair.

    Optimized for CBSE exam paper generation - includes only fields
    necessary for teacher review and answer key verification.
    """

    question_text: str = Field(
        ...,
        description="The actual question text - clear, precise, and unambiguous",
        min_length=10,
    )

    options: Optional[List[str]] = Field(
        None,
        description="List of 4 options for MCQ (format: 'A) text', 'B) text', etc.), null for other formats",
    )

    correct_answer: Optional[str] = Field(
        None,
        description="Correct answer letter ('A', 'B', 'C', or 'D') for MCQ, null for other formats",
        pattern="^[A-D]$",
    )

    explanation: str = Field(
        ...,
        description="Step-by-step solution or detailed reasoning with all working shown. This helps teachers quickly verify answer correctness during review without manually solving each question.",
        min_length=10,
    )

    diagram_needed: bool = Field(
        ...,
        description="Whether a diagram is required to understand or solve the question",
    )

    diagram_description: Optional[str] = Field(
        None,
        description="Detailed description of what should be drawn if diagram is needed",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "question_text": "What is the zero of the polynomial p(x) = x - 3?",
                "options": ["A) 0", "B) 3", "C) -3", "D) 1"],
                "correct_answer": "B",
                "explanation": "To find the zero of a polynomial, set p(x) = 0. Therefore: x - 3 = 0 → x = 3. The zero is 3.",
                "diagram_needed": False,
                "diagram_description": None,
            }
        }
