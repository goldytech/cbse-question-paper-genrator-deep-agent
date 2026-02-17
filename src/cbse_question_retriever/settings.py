"""Configuration settings for CBSE Question Retriever."""

from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class QdrantSettings(BaseModel):
    """Qdrant vector database settings."""

    host: str = Field(default="127.0.0.1", description="Qdrant server host")
    http_port: int = Field(default=6333, description="Qdrant HTTP port")
    api_key: Optional[str] = Field(default=None, description="Qdrant API key (optional)")
    timeout: int = Field(default=30, description="Connection timeout in seconds")


class OpenAISettings(BaseModel):
    """OpenAI API settings."""

    api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    embedding_model: str = Field(
        default="text-embedding-3-large", description="OpenAI embedding model"
    )
    embedding_dimensions: int = Field(default=3072, description="Embedding dimensions")


class RetrievalSettings(BaseModel):
    """Retrieval-specific settings."""

    max_chunks: int = Field(default=10, description="Maximum chunks to retrieve per query")
    similarity_threshold: float = Field(default=0.7, description="Minimum similarity score (0-1)")
    fuzzy_match_threshold: int = Field(default=80, description="Minimum fuzzy match score (0-100)")


class LLMSettings(BaseModel):
    """LLM question generation settings."""

    model: str = Field(default="gpt-5-mini", description="LLM model for question generation")
    temperature: float = Field(default=0.3, description="Temperature for generation (0.0-1.0)")
    max_tokens: int = Field(default=2000, description="Maximum tokens for generation")
    timeout: int = Field(default=30, description="LLM API timeout in seconds")
    quality_check_enabled: bool = Field(
        default=True, description="Enable quality self-assessment by LLM"
    )
    few_shot_examples_enabled: bool = Field(
        default=True, description="Include few-shot examples in prompts"
    )


class CBSEQuestionRetrieverSettings(BaseSettings):
    """Main settings class for CBSE Question Retriever."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__", extra="ignore"
    )

    qdrant: QdrantSettings = Field(default_factory=QdrantSettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)

    # Class-level configuration
    use_mock_data: bool = Field(default=False, description="Use mock data for testing")
    mock_data_path: str = Field(
        default="tests/fixtures/mock_qdrant_data.json", description="Path to mock data file"
    )
    use_real_openai: bool = Field(
        default=False, description="Use real OpenAI API for integration tests (false=use mocks)"
    )
    mock_llm_responses_path: str = Field(
        default="tests/fixtures/mock_llm_responses.json", description="Path to mock LLM responses"
    )


# Global settings instance
settings = CBSEQuestionRetrieverSettings()
