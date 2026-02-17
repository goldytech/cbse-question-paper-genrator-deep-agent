"""Mock LLM response loader for integration tests.

This module loads mock LLM responses when USE_REAL_OPENAI is false.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Default mock responses for common question patterns
DEFAULT_MOCK_RESPONSES = {
    "MCQ": {
        "question_text": "What is the HCF of 12 and 18?",
        "options": ["A) 6", "B) 12", "C) 18", "D) 36"],
        "correct_answer": "A",
        "explanation": "The HCF (Highest Common Factor) of 12 and 18 is 6, as 6 is the largest number that divides both 12 and 18 exactly.",
        "diagram_needed": False,
        "diagram_description": None,
        "hints": ["Find the factors of both numbers", "Identify the largest common factor"],
        "prerequisites": ["Understanding of factors", "HCF concept"],
        "common_mistakes": ["Confusing HCF with LCM", "Missing common factors"],
        "quality_score": 0.92,
        "generation_metadata": {
            "model": "gpt-5-mini-mock",
            "temperature": 0.3,
            "chunks_used": 3,
            "few_shot_enabled": True,
            "quality_check_enabled": True,
        },
        "error": None,
    },
    "VERY_SHORT": {
        "question_text": "Find the zero of the polynomial p(x) = 2x - 6.",
        "options": None,
        "correct_answer": "3",
        "explanation": "To find the zero, set p(x) = 0: 2x - 6 = 0 → 2x = 6 → x = 3.",
        "diagram_needed": False,
        "diagram_description": None,
        "hints": ["Set the polynomial equal to zero", "Solve for x"],
        "prerequisites": ["Polynomial basics", "Linear equations"],
        "common_mistakes": ["Not setting to zero", "Sign errors"],
        "quality_score": 0.90,
        "generation_metadata": {
            "model": "gpt-5-mini-mock",
            "temperature": 0.3,
            "chunks_used": 3,
            "few_shot_enabled": True,
            "quality_check_enabled": True,
        },
        "error": None,
    },
    "SHORT": {
        "question_text": "Solve the pair of linear equations: 2x + 3y = 11 and x - y = 1 using substitution method.",
        "options": None,
        "correct_answer": "x = 2, y = 1",
        "explanation": "From equation 2: x = y + 1. Substitute into equation 1: 2(y + 1) + 3y = 11 → 2y + 2 + 3y = 11 → 5y = 9 → y = 9/5. Then x = 9/5 + 1 = 14/5.",
        "diagram_needed": False,
        "diagram_description": None,
        "hints": ["Express one variable in terms of the other", "Substitute and solve"],
        "prerequisites": ["Linear equations", "Substitution method"],
        "common_mistakes": ["Algebraic errors", "Incorrect substitution"],
        "quality_score": 0.88,
        "generation_metadata": {
            "model": "gpt-5-mini-mock",
            "temperature": 0.3,
            "chunks_used": 4,
            "few_shot_enabled": True,
            "quality_check_enabled": True,
        },
        "error": None,
    },
    "LONG": {
        "question_text": "Prove that √2 is an irrational number. Hence, show that 3 + 2√2 is also irrational.",
        "options": None,
        "correct_answer": "Proof completed",
        "explanation": "Assume √2 is rational: √2 = p/q where p, q are coprime. Then 2 = p²/q² → p² = 2q². Thus p² is even, so p is even. Let p = 2k. Then 4k² = 2q² → q² = 2k². Thus q is even. Contradiction! Hence √2 is irrational. For 3 + 2√2: if rational, then 2√2 = rational - 3 = rational, so √2 = rational/2 = rational. Contradiction!",
        "diagram_needed": False,
        "diagram_description": None,
        "hints": ["Use proof by contradiction", "Assume √2 is rational"],
        "prerequisites": ["Rational numbers", "Proof by contradiction", "Even/odd properties"],
        "common_mistakes": ["Not completing the contradiction", "Assuming without proof"],
        "quality_score": 0.94,
        "generation_metadata": {
            "model": "gpt-5-mini-mock",
            "temperature": 0.3,
            "chunks_used": 5,
            "few_shot_enabled": True,
            "quality_check_enabled": True,
        },
        "error": None,
    },
}

# Mock responses with diagrams
DIAGRAM_MOCK_RESPONSES = {
    "GRAPHICAL_METHOD": {
        "question_text": "Draw the graph of the linear equation 2x + y = 6. From the graph, find the value of y when x = 2.",
        "options": None,
        "correct_answer": "y = 2",
        "explanation": "To draw the graph: When x = 0, y = 6. When y = 0, x = 3. Plot points (0, 6) and (3, 0) and draw the line. From the graph, when x = 2, y = 2.",
        "diagram_needed": True,
        "diagram_description": "Coordinate plane showing line passing through (0, 6) and (3, 0). Point marked at x = 2 where y = 2.",
        "hints": ["Find two points on the line", "Plot and connect them"],
        "prerequisites": ["Coordinate geometry", "Graph plotting"],
        "common_mistakes": ["Incorrect plotting", "Wrong scale"],
        "quality_score": 0.91,
        "generation_metadata": {
            "model": "gpt-5-mini-mock",
            "temperature": 0.3,
            "chunks_used": 4,
            "few_shot_enabled": True,
            "quality_check_enabled": True,
        },
        "error": None,
    },
    "TRIANGLE": {
        "question_text": "In triangle ABC, angle A = 60°, angle B = 70°. Find angle C and classify the triangle.",
        "options": None,
        "correct_answer": "50°",
        "explanation": "Sum of angles in a triangle is 180°. So angle C = 180° - 60° - 70° = 50°. Since all angles are less than 90°, it's an acute-angled triangle.",
        "diagram_needed": True,
        "diagram_description": "Triangle ABC with angles labeled: A = 60°, B = 70°, C = 50°.",
        "hints": ["Use angle sum property", "Sum of angles = 180°"],
        "prerequisites": ["Triangle properties", "Angle sum"],
        "common_mistakes": ["Calculation errors", "Wrong classification"],
        "quality_score": 0.89,
        "generation_metadata": {
            "model": "gpt-5-mini-mock",
            "temperature": 0.3,
            "chunks_used": 4,
            "few_shot_enabled": True,
            "quality_check_enabled": True,
        },
        "error": None,
    },
}


class MockLLMLoader:
    """Loads mock LLM responses for integration testing."""

    def __init__(self, mock_responses_path: Optional[str] = None):
        """Initialize the mock loader.

        Args:
            mock_responses_path: Path to JSON file with mock responses
        """
        self.mock_responses_path = mock_responses_path
        self.custom_responses: Dict[str, Dict[str, Any]] = {}

        # Load custom responses if file exists
        if mock_responses_path and Path(mock_responses_path).exists():
            self._load_custom_responses()

    def _load_custom_responses(self) -> None:
        """Load custom responses from file."""
        try:
            with open(self.mock_responses_path, "r") as f:
                data = json.load(f)
                self.custom_responses = data.get("responses", {})
                logger.info(f"Loaded {len(self.custom_responses)} custom mock responses")
        except Exception as e:
            logger.error(f"Failed to load custom responses: {e}")
            self.custom_responses = {}

    def get_mock_response(
        self,
        question_id: str,
        question_format: str,
        topic: str,
        chapter: str,
    ) -> Dict[str, Any]:
        """Get a mock LLM response.

        Args:
            question_id: Question identifier
            question_format: MCQ, VERY_SHORT, SHORT, LONG
            topic: Topic name
            chapter: Chapter name

        Returns:
            Mock LLM response dictionary
        """
        # First check for custom response by question_id
        if question_id in self.custom_responses:
            logger.info(f"Using custom mock response for {question_id}")
            return self.custom_responses[question_id].copy()

        # Check if topic suggests a diagram
        topic_lower = topic.lower()
        chapter_lower = chapter.lower()

        if "graph" in topic_lower or "graphical" in topic_lower:
            logger.info(f"Using diagram mock response for graphical method: {question_id}")
            return DIAGRAM_MOCK_RESPONSES["GRAPHICAL_METHOD"].copy()

        if "triangle" in topic_lower or "geometry" in chapter_lower:
            logger.info(f"Using diagram mock response for geometry: {question_id}")
            return DIAGRAM_MOCK_RESPONSES["TRIANGLE"].copy()

        # Use default response based on format
        if question_format in DEFAULT_MOCK_RESPONSES:
            logger.info(f"Using default mock response for {question_format}: {question_id}")
            response = DEFAULT_MOCK_RESPONSES[question_format].copy()

            # Customize based on topic
            if question_format == "MCQ":
                if "polynomial" in topic_lower:
                    response["question_text"] = "If α and β are zeroes of x² - 5x + 6, find α + β."
                    response["options"] = ["A) 5", "B) 6", "C) -5", "D) -6"]
                    response["correct_answer"] = "A"
                    response["explanation"] = (
                        "For ax² + bx + c = 0, sum of zeroes = -b/a. Here, α + β = -(-5)/1 = 5."
                    )
                elif "euclid" in topic_lower or "division" in topic_lower:
                    response["question_text"] = (
                        "Using Euclid's division algorithm, find the HCF of 135 and 225."
                    )
                    response["options"] = ["A) 15", "B) 25", "C) 45", "D) 75"]
                    response["correct_answer"] = "C"
                    response["explanation"] = (
                        "225 = 135 × 1 + 90, 135 = 90 × 1 + 45, 90 = 45 × 2 + 0. HCF is 45."
                    )

            elif question_format == "VERY_SHORT":
                if "zero" in topic_lower and "polynomial" in topic_lower:
                    response["question_text"] = "Find the zero of the polynomial p(x) = 3x - 9."
                    response["correct_answer"] = "3"
                    response["explanation"] = "Set p(x) = 0: 3x - 9 = 0 → 3x = 9 → x = 3."

            return response

        # Fallback to SHORT format
        logger.warning(f"No mock response found for format {question_format}, using SHORT default")
        return DEFAULT_MOCK_RESPONSES["SHORT"].copy()

    def save_mock_responses(
        self,
        responses: Dict[str, Dict[str, Any]],
        output_path: str,
    ) -> bool:
        """Save generated mock responses to file.

        Args:
            responses: Dictionary of question_id -> response
            output_path: Path to save the file

        Returns:
            True if saved successfully
        """
        try:
            data = {
                "metadata": {
                    "total_responses": len(responses),
                    "format": "mock_llm_responses_v1",
                },
                "responses": responses,
            }

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {len(responses)} mock responses to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save mock responses: {e}")
            return False


# Global loader instance
_mock_loader: Optional[MockLLMLoader] = None


def get_mock_loader(mock_responses_path: Optional[str] = None) -> MockLLMLoader:
    """Get or create the global mock loader instance.

    Args:
        mock_responses_path: Path to mock responses file

    Returns:
        MockLLMLoader instance
    """
    global _mock_loader
    if _mock_loader is None or (_mock_loader.mock_responses_path != mock_responses_path):
        _mock_loader = MockLLMLoader(mock_responses_path)
    return _mock_loader
