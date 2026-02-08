#!/bin/bash
# Run tests for specific domains
# Usage: ./run_tests.sh [domain]
#   where domain is one of: all, cache, question_generation, blueprint_validation, curriculum_search

if [ -z "$1" ]; then
    echo "Usage: ./run_tests.sh [domain]"
    echo "Domains: all, cache, question_generation, blueprint_validation, curriculum_search"
    exit 1
fi

case "$1" in
    all)
        echo "Running all tests..."
        uv run pytest tests/ -v --tb=short
        ;;
    cache)
        echo "Running cache tests..."
        uv run pytest tests/test_cache -v --tb=short
        ;;
    question_generation)
        echo "Running question generation tests..."
        uv run pytest tests/test_question_generation -v --tb=short
        ;;
    blueprint_validation)
        echo "Running blueprint validation tests..."
        uv run pytest tests/test_blueprint_validation -v --tb=short
        ;;
    curriculum_search)
        echo "Running curriculum search tests..."
        uv run pytest tests/test_curriculum_search -v --tb=short
        ;;
    *)
        echo "Unknown domain: $1"
        echo "Available domains: all, cache, question_generation, blueprint_validation, curriculum_search"
        exit 1
        ;;
esac
