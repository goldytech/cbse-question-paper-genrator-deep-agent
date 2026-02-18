"""LangChain-based LLM client for question generation.

Uses ChatOpenAI from langchain_openai for gpt-5-mini integration.
"""

import json
import logging
from typing import Any, Dict, Optional, Union

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .output_schema import QuestionOutput
from .settings import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Manages LLM interactions using LangChain for question generation."""

    def __init__(self):
        """Initialize LangChain ChatOpenAI client."""
        self._llm: Optional[ChatOpenAI] = None
        self._model = settings.llm.model
        self._temperature = settings.llm.temperature
        self._max_tokens = settings.llm.max_tokens
        self._timeout = settings.llm.timeout

    @property
    def llm(self) -> ChatOpenAI:
        """Lazy initialization of LangChain LLM."""
        if self._llm is None:
            if not settings.openai.api_key:
                raise ValueError(
                    "OpenAI API key not set. Please set OPENAI__API_KEY in environment."
                )

            self._llm = ChatOpenAI(
                model=self._model,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
                timeout=self._timeout,
                api_key=settings.openai.api_key,
            )
            logger.info(f"Initialized LangChain ChatOpenAI with model: {self._model}")

        return self._llm

    def generate_question(self, prompt: str) -> Dict[str, Any]:
        """Generate question using LLM with structured output.

        Args:
            prompt: Complete prompt with context and instructions

        Returns:
            Parsed question dictionary from structured output
        """
        try:
            messages = [
                SystemMessage(
                    content="You are an expert CBSE question paper setter with deep knowledge of Indian secondary education curriculum and NCERT textbooks. Generate high-quality, pedagogically sound questions that strictly follow CBSE standards."
                ),
                HumanMessage(content=prompt),
            ]

            logger.info(
                f"Calling LLM ({self._model}) for question generation with structured output..."
            )

            # Use structured output to ensure valid JSON
            structured_llm = self.llm.with_structured_output(QuestionOutput)
            response = structured_llm.invoke(messages)

            logger.info("LLM question generation completed with structured output")

            # Convert Pydantic model to dictionary
            if hasattr(response, "model_dump"):
                return response.model_dump()
            elif hasattr(response, "dict"):
                return response.dict()
            else:
                return dict(response)

        except Exception as e:
            logger.error(f"Error generating question with LLM: {e}")
            raise

    def detect_diagram_need(self, prompt: str) -> Dict[str, Any]:
        """Detect if diagram is needed using LLM.

        Args:
            prompt: Diagram detection prompt

        Returns:
            Parsed diagram detection result
        """
        try:
            messages = [
                SystemMessage(
                    content="You are an expert at analyzing educational content to determine visual aid requirements."
                ),
                HumanMessage(content=prompt),
            ]

            logger.info("Calling LLM for diagram detection...")
            response = self.llm.invoke(messages)
            logger.info("Diagram detection completed")

            # Parse JSON response
            content = response.content.strip()
            # Extract JSON if wrapped in markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            return json.loads(content)

        except Exception as e:
            logger.error(f"Error detecting diagram need: {e}")
            return {
                "diagram_needed": False,
                "diagram_description": None,
                "diagram_type": "none",
                "reasoning": f"Error in detection: {str(e)}",
            }


# Global LLM client instance
llm_client = LLMClient()
