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
        description="Step-by-step solution or detailed reasoning with all working shown",
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

    hints: List[str] = Field(
        ...,
        description="2-3 helpful hints for students to solve the question",
        min_length=1,
    )

    prerequisites: List[str] = Field(
        ...,
        description="2-3 required knowledge points students should know before attempting",
        min_length=1,
    )

    common_mistakes: List[str] = Field(
        ...,
        description="2-3 typical student errors or misconceptions for this question",
        min_length=1,
    )

    quality_score: Optional[float] = Field(
        None,
        description="Self-assessed quality score from 0.0 to 1.0 based on clarity, accuracy, and pedagogy",
        ge=0.0,
        le=1.0,
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
                "hints": ["Set the polynomial equal to zero", "Solve for x"],
                "prerequisites": ["Understanding polynomial zeros", "Basic equation solving"],
                "common_mistakes": ["Confusing zero with coefficient", "Sign errors"],
                "quality_score": 0.95,
            }
        }
