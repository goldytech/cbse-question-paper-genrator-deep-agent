"""Unit tests for Tavily search configuration and behavior.

NOTE: All Tavily-related tests have been disabled pending Qdrant vector database integration.
The tests below are commented out but preserved for reference when implementing Qdrant.
"""

# =============================================================================
# TAVILY SEARCH TESTS - DISABLED
# =============================================================================
# These tests verified Tavily search functionality which is now disabled.
# They will be replaced with tests for Qdrant vector database search.
#
# import pytest
# from unittest.mock import Mock, patch
# from question_generation.orchestrator import TAVILY_CONFIG, _search_tavily
#
#
# class TestTavilyConfiguration:
#     """Tests for Tavily configuration constants."""
#
#     def test_max_results_is_15(self):
#         """Verify max_results is set to 15."""
#         assert TAVILY_CONFIG["max_results"] == 15
#
#     def test_search_depth_is_advanced(self):
#         """Verify search_depth is advanced."""
#         assert TAVILY_CONFIG["search_depth"] == "advanced"
#
#     def test_include_raw_content_is_true(self):
#         """Verify include_raw_content is True."""
#         assert TAVILY_CONFIG["include_raw_content"] is True
#
#     def test_only_operational_domains_included(self):
#         """Verify only operational domains are included."""
#         expected_domains = [
#             "cbseacademic.nic.in",
#             "byjus.com",
#             "vedantu.com",
#             "learn.careers360.com",
#         ]
#
#         actual_domains = TAVILY_CONFIG["include_domains"]
#
#         # Verify all expected domains are present
#         for domain in expected_domains:
#             assert domain in actual_domains, f"Missing domain: {domain}"
#
#         # Verify no unreachable domains
#         unreachable = ["ncert.nic.in", "toppr.com", "meritnation.com"]
#         for domain in unreachable:
#             assert domain not in actual_domains, (
#                 f"Unreachable domain should not be included: {domain}"
#             )
#
#     def test_no_untrusted_domains(self):
#         """Verify no untrusted domains in list."""
#         untrusted = ["wikipedia.org", "youtube.com", "facebook.com"]
#         for domain in untrusted:
#             assert domain not in TAVILY_CONFIG["include_domains"]
#
#
# class TestTavilyRateLimiting:
#     """Tests for rate limiting configuration."""
#
#     def test_max_concurrent_is_15(self):
#         """Verify MAX_CONCURRENT is 15."""
#         from question_generation.orchestrator import MAX_CONCURRENT
#
#         assert MAX_CONCURRENT == 15
#
#     def test_rate_limit_per_minute_is_100(self):
#         """Verify RATE_LIMIT_PER_MINUTE is 100."""
#         from question_generation.orchestrator import RATE_LIMIT_PER_MINUTE
#
#         assert RATE_LIMIT_PER_MINUTE == 100
#
#
# class TestTavilySearchFunction:
#     """Tests for Tavily search function."""
#
#     @pytest.mark.asyncio
#     async def test_search_uses_config(self, mock_tavily_client):
#         """Verify search uses configuration from TAVILY_CONFIG."""
#         results = await _search_tavily("test query")
#
#         # Verify client was called with correct parameters
#         mock_tavily_client.search.assert_called_once()
#         call_kwargs = mock_tavily_client.search.call_args[1]
#
#         assert call_kwargs["max_results"] == 15
#         assert call_kwargs["search_depth"] == "advanced"
#         assert call_kwargs["include_raw_content"] is True
#         assert call_kwargs["include_domains"] == TAVILY_CONFIG["include_domains"]
#
#     @pytest.mark.asyncio
#     async def test_search_returns_results(self, mock_tavily_client):
#         """Verify search returns results list."""
#         results = await _search_tavily("CBSE Class 10 Math")
#
#         assert isinstance(results, list)
#         assert len(results) == 15
#
#     @pytest.mark.asyncio
#     async def test_search_error_handling(self):
#         """Verify graceful handling of search errors."""
#         with patch("question_generation.orchestrator._get_tavily_client") as mock:
#             client = Mock()
#             client.search.side_effect = Exception("API Error")
#             mock.return_value = client
#
#             results = await _search_tavily("test query")
#
#             assert results == []
#
#     @pytest.mark.asyncio
#     async def test_search_empty_results(self, mock_tavily_client):
#         """Verify handling of empty results."""
#         mock_tavily_client.search.return_value = {"results": []}
#
#         results = await _search_tavily("test query")
#
#         assert results == []
#
#
# class TestTavilySearchQueryConstruction:
#     """Tests for search query construction."""
#
#     def test_query_includes_cbse(self):
#         """Verify query always includes CBSE."""
#         # This would be tested in integration with _optimize_query
#         # But we verify the pattern is expected
#         assert "CBSE" in "CBSE Class 10 Mathematics test"
#
#     def test_query_includes_class_level(self):
#         """Verify query includes class level."""
#         assert "Class 10" in "CBSE Class 10 Mathematics test"
#
#     def test_query_length_under_400(self):
#         """Verify query is under 400 characters."""
#         sample_query = "CBSE Class 10 Mathematics Polynomials Zeros easy MCQ practice questions"
#         assert len(sample_query) < 400
# =============================================================================
