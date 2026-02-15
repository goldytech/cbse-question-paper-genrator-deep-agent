"""Qdrant client wrapper for CBSE Question Retriever."""

import logging
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import Distance, VectorParams

from cbse_question_retriever.settings import settings
from cbse_question_retriever.data_types import Chunk, ChunkType

logger = logging.getLogger(__name__)


class QdrantManager:
    """Manages Qdrant client connection and operations."""

    def __init__(self):
        self._client: Optional[QdrantClient] = None
        self._connected = False

    @property
    def client(self) -> QdrantClient:
        """Lazy initialization of Qdrant client."""
        if self._client is None:
            self._connect()
        return self._client

    def _connect(self) -> None:
        """Initialize Qdrant client connection."""
        try:
            self._client = QdrantClient(
                host=settings.qdrant.host,
                port=settings.qdrant.http_port,
                api_key=settings.qdrant.api_key,
                timeout=settings.qdrant.timeout,
            )
            self._connected = True
            logger.info(
                f"Connected to Qdrant at {settings.qdrant.host}:{settings.qdrant.http_port}"
            )
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise ConnectionError(f"Cannot connect to Qdrant: {e}")

    def check_collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists in Qdrant."""
        try:
            collections = self.client.get_collections()
            return any(col.name == collection_name for col in collections.collections)
        except Exception as e:
            logger.error(f"Error checking collection existence: {e}")
            return False

    def get_available_collections(self) -> List[str]:
        """Get list of all available collections."""
        try:
            collections = self.client.get_collections()
            return [col.name for col in collections.collections]
        except Exception as e:
            logger.error(f"Error getting collections: {e}")
            return []

    def search_by_vector(
        self,
        collection_name: str,
        query_vector: List[float],
        filter_conditions: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[Chunk]:
        """Search chunks by vector similarity with optional metadata filters.

        Args:
            collection_name: Name of the Qdrant collection
            query_vector: Embedding vector for similarity search
            filter_conditions: Optional metadata filters (e.g., {"chapter": "Polynomials"})
            limit: Maximum number of results

        Returns:
            List of Chunk objects
        """
        try:
            # Build query filter if conditions provided
            query_filter = None
            if filter_conditions:
                from qdrant_client.http.models import FieldCondition, MatchValue, Filter

                must_conditions = []
                for key, value in filter_conditions.items():
                    must_conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
                query_filter = Filter(must=must_conditions)

            # Perform vector search
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )

            # Convert to Chunk objects
            chunks = []
            for result in results:
                payload = result.payload
                chunks.append(
                    Chunk(
                        id=str(result.id),
                        text=payload.get("text", ""),
                        chapter=payload.get("chapter", ""),
                        section=payload.get("section", ""),
                        topic=payload.get("topic", ""),
                        chunk_type=ChunkType(payload.get("chunk_type", "THEORY")),
                        page_start=payload.get("page_start", 0),
                        page_end=payload.get("page_end", 0),
                        score=result.score,
                    )
                )

            return chunks

        except UnexpectedResponse as e:
            logger.error(f"Qdrant search error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            raise

    def get_distinct_topics(self, collection_name: str, chapter: Optional[str] = None) -> List[str]:
        """Get all distinct topics from a collection.

        Args:
            collection_name: Name of the collection
            chapter: Optional chapter filter

        Returns:
            List of unique topic names
        """
        try:
            # Use scroll to get all unique topics
            filter_conditions = {}
            if chapter:
                filter_conditions["chapter"] = chapter

            topics = set()
            offset = None

            while True:
                results, offset = self.client.scroll(
                    collection_name=collection_name,
                    offset=offset,
                    limit=100,
                    with_payload=True,
                )

                for result in results:
                    topic = result.payload.get("topic")
                    if topic:
                        topics.add(topic)

                if offset is None:
                    break

            return sorted(list(topics))

        except Exception as e:
            logger.error(f"Error getting distinct topics: {e}")
            return []


# Global Qdrant manager instance
qdrant_manager = QdrantManager()
