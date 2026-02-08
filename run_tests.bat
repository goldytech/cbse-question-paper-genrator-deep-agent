@echo off
REM Run tests for specific domains
REM Usage: run_tests.bat [domain]
REM   where domain is one of: all, cache, question_generation, blueprint_validation, curriculum_search

if "%~1"=="" (
    echo Usage: run_tests.bat [domain]
    echo Domains: all, cache, question_generation, blueprint_validation, curriculum_search
    exit /b 1
)

if "%~1"=="all" (
    echo Running all tests...
    uv run pytest tests/ -v --tb=short
) else if "%~1"=="cache" (
    echo Running cache tests...
    uv run pytest tests/test_cache -v --tb=short
) else if "%~1"=="question_generation" (
    echo Running question generation tests...
    uv run pytest tests/test_question_generation -v --tb=short
) else if "%~1"=="blueprint_validation" (
    echo Running blueprint validation tests...
    uv run pytest tests/test_blueprint_validation -v --tb=short
) else if "%~1"=="curriculum_search" (
    echo Running curriculum search tests...
    uv run pytest tests/test_curriculum_search -v --tb=short
) else (
    echo Unknown domain: %~1
    echo Available domains: all, cache, question_generation, blueprint_validation, curriculum_search
    exit /b 1
)
