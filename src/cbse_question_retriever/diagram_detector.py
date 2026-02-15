"""Diagram detector using LLM.

Uses gpt-5-mini to determine if a question requires a diagram.
"""

import logging
from typing import Any, Dict

from cbse_question_retriever.llm_client import llm_client
from cbse_question_retriever.prompt_templates import DIAGRAM_DETECTION_PROMPT

logger = logging.getLogger(__name__)


class DiagramDetector:
    """Detects if a question requires a diagram using LLM."""

    def detect_diagram_need(
        self,
        question_text: str,
        topic: str,
        chapter: str,
        question_format: str,
    ) -> Dict[str, Any]:
        """Detect if diagram is needed for a question.

        Args:
            question_text: The generated question text
            topic: Topic name
            chapter: Chapter name
            question_format: Question format

        Returns:
            Dictionary with diagram information:
            {
                "diagram_needed": bool,
                "diagram_description": str or None,
                "diagram_type": str (geometric/coordinate/construction/graphical/none),
                "reasoning": str
            }
        """
        try:
            # Build detection prompt
            prompt = DIAGRAM_DETECTION_PROMPT.format(
                question_text=question_text,
                topic=topic,
                chapter=chapter,
                format=question_format,
            )

            # Call LLM for detection
            result = llm_client.detect_diagram_need(prompt)

            # Ensure required fields
            return {
                "diagram_needed": result.get("diagram_needed", False),
                "diagram_description": result.get("diagram_description"),
                "diagram_type": result.get("diagram_type", "none"),
                "reasoning": result.get("reasoning", ""),
            }

        except Exception as e:
            logger.error(f"Error in diagram detection: {e}")
            # Return safe default
            return {
                "diagram_needed": False,
                "diagram_description": None,
                "diagram_type": "none",
                "reasoning": f"Error in detection: {str(e)}",
            }


# Global diagram detector instance
diagram_detector = DiagramDetector()
