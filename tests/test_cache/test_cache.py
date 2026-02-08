"""Unit tests for question cache functionality."""

import json
import sqlite3
import pytest
from datetime import datetime, timedelta
from pathlib import Path


class TestQuestionCacheInitialization:
    """Tests for cache initialization."""

    def test_database_creation(self, question_cache):
        """Verify database file is created."""
        assert Path(question_cache.db_path).exists()

    def test_table_creation(self, question_cache):
        """Verify question_cache table is created."""
        with sqlite3.connect(question_cache.db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='question_cache'"
            )
            assert cursor.fetchone() is not None

    def test_index_creation(self, question_cache):
        """Verify index on blueprint_hash is created."""
        with sqlite3.connect(question_cache.db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_blueprint_hash'"
            )
            assert cursor.fetchone() is not None


class TestCacheKeyGeneration:
    """Tests for cache key generation."""

    def test_deterministic_key_generation(self, question_cache, sample_requirements_easy):
        """Verify same inputs produce same key."""
        key1 = question_cache.generate_key(sample_requirements_easy)
        key2 = question_cache.generate_key(sample_requirements_easy)
        assert key1 == key2
        assert len(key1) == 16

    def test_different_inputs_different_keys(
        self, question_cache, sample_requirements_easy, sample_requirements_medium
    ):
        """Verify different inputs produce different keys."""
        key1 = question_cache.generate_key(sample_requirements_easy)
        key2 = question_cache.generate_key(sample_requirements_medium)
        assert key1 != key2

    def test_key_components_included(self, question_cache, sample_requirements_easy):
        """Verify key includes all required components."""
        key = question_cache.generate_key(sample_requirements_easy)
        # Key should be hexadecimal
        assert all(c in "0123456789abcdef" for c in key)


class TestCacheStoreAndRetrieve:
    """Tests for cache storage and retrieval."""

    def test_store_and_retrieve(
        self, question_cache, sample_requirements_easy, sample_question_data
    ):
        """Verify question can be stored and retrieved."""
        cache_key = question_cache.generate_key(sample_requirements_easy)
        blueprint_hash = "test_hash_123"

        # Store
        question_cache.set(cache_key, sample_question_data, blueprint_hash)

        # Retrieve
        retrieved = question_cache.get(cache_key)
        assert retrieved is not None
        assert retrieved["question_id"] == sample_question_data["question_id"]
        assert retrieved["question_text"] == sample_question_data["question_text"]

    def test_cache_miss_returns_none(self, question_cache):
        """Verify None returned for non-existent key."""
        retrieved = question_cache.get("nonexistent_key")
        assert retrieved is None

    def test_cache_hit_increments_counter(
        self, question_cache, sample_requirements_easy, sample_question_data
    ):
        """Verify used_count increments on cache hit."""
        cache_key = question_cache.generate_key(sample_requirements_easy)
        question_cache.set(cache_key, sample_question_data, "hash")

        # First retrieval
        question_cache.get(cache_key)

        # Check counter in database
        with sqlite3.connect(question_cache.db_path) as conn:
            cursor = conn.execute(
                "SELECT used_count FROM question_cache WHERE cache_key = ?", (cache_key,)
            )
            count = cursor.fetchone()[0]
            assert count == 1

        # Second retrieval
        question_cache.get(cache_key)

        with sqlite3.connect(question_cache.db_path) as conn:
            cursor = conn.execute(
                "SELECT used_count FROM question_cache WHERE cache_key = ?", (cache_key,)
            )
            count = cursor.fetchone()[0]
            assert count == 2

    def test_overwrite_existing_key(
        self, question_cache, sample_requirements_easy, sample_question_data
    ):
        """Verify storing with same key overwrites existing data."""
        cache_key = question_cache.generate_key(sample_requirements_easy)

        # Store first version
        question_cache.set(cache_key, sample_question_data, "hash1")

        # Store second version
        new_data = sample_question_data.copy()
        new_data["question_text"] = "Modified question"
        question_cache.set(cache_key, new_data, "hash2")

        # Retrieve
        retrieved = question_cache.get(cache_key)
        assert retrieved["question_text"] == "Modified question"


class TestCacheWithBlueprintHash:
    """Tests for blueprint hash tracking."""

    def test_blueprint_hash_stored(
        self, question_cache, sample_requirements_easy, sample_question_data
    ):
        """Verify blueprint hash is stored with question."""
        cache_key = question_cache.generate_key(sample_requirements_easy)
        blueprint_hash = "blueprint_v1_hash"

        question_cache.set(cache_key, sample_question_data, blueprint_hash)

        with sqlite3.connect(question_cache.db_path) as conn:
            cursor = conn.execute(
                "SELECT blueprint_hash FROM question_cache WHERE cache_key = ?", (cache_key,)
            )
            stored_hash = cursor.fetchone()[0]
            assert stored_hash == blueprint_hash


class TestCacheExpirationLogic:
    """Tests for cache expiration (to be used with CLI)."""

    def test_old_entries_identified(
        self, question_cache, sample_requirements_easy, sample_question_data
    ):
        """Verify old entries can be identified for cleanup."""
        cache_key = question_cache.generate_key(sample_requirements_easy)
        question_cache.set(cache_key, sample_question_data, "hash")

        # Get entry timestamp
        with sqlite3.connect(question_cache.db_path) as conn:
            cursor = conn.execute(
                "SELECT created_at FROM question_cache WHERE cache_key = ?", (cache_key,)
            )
            created_at = cursor.fetchone()[0]

            # Verify it's a valid ISO timestamp
            created_datetime = datetime.fromisoformat(created_at)
            assert created_datetime.year == datetime.now().year
            assert created_datetime.month == datetime.now().month
            assert created_datetime.day == datetime.now().day
