"""OpenAI embedding generator for CBSE Question Retriever."""

import logging
from typing import List

from openai import OpenAI

from cbse_question_retriever.settings import settings

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings using OpenAI API."""

    def __init__(self):
        self._client = None
        self._model = settings.openai.embedding_model
        self._dimensions = settings.openai.embedding_dimensions

    @property
    def client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            if not settings.openai.api_key:
                raise ValueError(
                    "OpenAI API key not set. Please set OPENAI__API_KEY in environment."
                )
            self._client = OpenAI(api_key=settings.openai.api_key)
        return self._client

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            Embedding vector as list of floats
        """
        try:
            response = self.client.embeddings.create(
                model=self._model,
                input=text,
                dimensions=self._dimensions,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch.

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                model=self._model,
                input=texts,
                dimensions=self._dimensions,
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise


# Global embedding generator instance
embedding_generator = EmbeddingGenerator()
