# ==============================================================================
# test_url_filtering.py — URL filtering and classification tests
# ==============================================================================
# Purpose: Test URL filtering logic and business intelligence classification
# Sections: Imports, Test Configuration, Filtering Tests, Mock Setup
# ==============================================================================

# Standard Library --------------------------------------------------------------
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from typing import List, Dict, Any

# Third Party -------------------------------------------------------------------
# (none)

# Core (App-wide) ---------------------------------------------------------------
from domains.intelligence_collection import filter_valuable_urls
from services.ai import ai_client, AIClient


@pytest.fixture
def sample_urls() -> List[str]:
    """Sample URLs for testing."""
    return [
        "https://example.com/about",
        "https://example.com/team",
        "https://example.com/services",
        "https://example.com/blog",
        "https://example.com/contact",
        "https://example.com/privacy",
        "https://example.com/terms"
    ]


@pytest.fixture
def sample_company_context() -> Dict[str, str]:
    """Sample company context for AI scoring."""
    return {
        "company_name": "Example Corp",
        "website": "https://example.com",
        "objective": "business intelligence gathering"
    }


@pytest.fixture
def mock_ai_response() -> List[Dict[str, Any]]:
    """Mock AI response for URL scoring."""
    return [
        {
            "url": "https://example.com/about",
            "score": 95,
            "reason": "Company mission and values page",
            "category": "leadership"
        },
        {
            "url": "https://example.com/team",
            "score": 90,
            "reason": "Leadership and team information",
            "category": "leadership"
        },
        {
            "url": "https://example.com/services",
            "score": 85,
            "reason": "Core business offerings",
            "category": "products"
        },
        {
            "url": "https://example.com/blog",
            "score": 70,
            "reason": "Company culture insights",
            "category": "culture"
        },
        {
            "url": "https://example.com/contact",
            "score": 20,
            "reason": "Utility page",
            "category": "other"
        },
        {
            "url": "https://example.com/privacy",
            "score": 10,
            "reason": "Legal/compliance page",
            "category": "other"
        },
        {
            "url": "https://example.com/terms",
            "score": 10,
            "reason": "Legal/compliance page",
            "category": "other"
        }
    ]


class TestURLFiltering:
    """Test URL filtering functionality."""

    @pytest.mark.asyncio
    async def test_ai_powered_filtering_success(
        self,
        sample_urls: List[str],
        sample_company_context: Dict[str, str],
        mock_ai_response: List[Dict[str, Any]]
    ):
        """Test successful AI-powered URL filtering."""
        # Arrange
        with patch.object(ai_client, 'score_urls_for_business_intelligence', new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = mock_ai_response
            
            # Act
            result = await filter_valuable_urls(
                urls=sample_urls,
                company_context=sample_company_context,
                max_urls=5
            )
            
            # Assert
            assert len(result) == 5
            assert result[0]["url"] == "https://example.com/about"
            assert result[0]["score"] == 95
            assert result[0]["category"] == "leadership"
            
            # Verify AI client was called correctly
            mock_ai.assert_called_once_with(sample_urls, str(sample_company_context))

    @pytest.mark.asyncio
    async def test_ai_filtering_with_diversity_algorithm(
        self,
        sample_urls: List[str],
        sample_company_context: Dict[str, str]
    ):
        """Test that diversity algorithm ensures category variety."""
        # Arrange - Create response with multiple high-scoring URLs in same category
        diverse_ai_response = [
            {
                "url": "https://example.com/about",
                "score": 95,
                "reason": "Company mission",
                "category": "leadership"
            },
            {
                "url": "https://example.com/team",
                "score": 94,
                "reason": "Team info",
                "category": "leadership"
            },
            {
                "url": "https://example.com/ceo",
                "score": 93,
                "reason": "CEO profile",
                "category": "leadership"
            },
            {
                "url": "https://example.com/services",
                "score": 85,
                "reason": "Services",
                "category": "products"
            },
            {
                "url": "https://example.com/products",
                "score": 84,
                "reason": "Products",
                "category": "products"
            },
            {
                "url": "https://example.com/blog",
                "score": 70,
                "reason": "Blog",
                "category": "culture"
            },
            {
                "url": "https://example.com/culture",
                "score": 69,
                "reason": "Culture",
                "category": "culture"
            }
        ]
        
        with patch.object(ai_client, 'score_urls_for_business_intelligence', new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = diverse_ai_response
            
            # Act
            result = await filter_valuable_urls(
                urls=sample_urls,
                company_context=sample_company_context,
                max_urls=7
            )
            
            # Assert - Should have diversity across categories
            assert len(result) == 7
            
            # Count categories to ensure diversity
            categories = [item["category"] for item in result]
            category_counts = {}
            for category in categories:
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # The diversity algorithm allows max 2 URLs per category initially,
            # then fills remaining slots with highest scores regardless of category
            # So we should have at least 2 different categories
            assert len(category_counts) >= 2
            
            # Verify the diversity algorithm is working:
            # - First 4 URLs should be from different categories (max 2 per category)
            # - Then remaining slots filled with highest scores
            first_four_categories = categories[:4]
            first_four_category_counts = {}
            for category in first_four_categories:
                first_four_category_counts[category] = first_four_category_counts.get(category, 0) + 1
            
            # Should have max 2 URLs per category in first 4
            assert all(count <= 2 for count in first_four_category_counts.values())
            
            # Verify we get the highest scoring URLs overall
            scores = [item["score"] for item in result]
            # The algorithm should prioritize diversity first, then fill with highest scores
            # So the first few should be diverse, but overall we should get high-quality URLs
            assert max(scores) >= 90  # Should have high-scoring URLs

    @pytest.mark.asyncio
    async def test_ai_filtering_fallback_to_pattern_based(
        self,
        sample_urls: List[str],
        sample_company_context: Dict[str, str]
    ):
        """Test fallback to pattern-based filtering when AI fails."""
        # Arrange - Mock AI to fail
        with patch.object(ai_client, 'score_urls_for_business_intelligence', new_callable=AsyncMock) as mock_ai:
            mock_ai.side_effect = Exception("AI service unavailable")
            
            # Act
            result = await filter_valuable_urls(
                urls=sample_urls,
                company_context=sample_company_context,
                max_urls=5
            )
            
            # Assert - Should still return results using fallback
            assert len(result) == 5
            assert all("url" in item for item in result)
            assert all("score" in item for item in result)
            assert all("reason" in item for item in result)
            assert all("category" in item for item in result)
            
            # Verify fallback was used (pattern-based scoring)
            # About page should score high
            about_item = next(item for item in result if "/about" in item["url"])
            assert about_item["score"] >= 90
            
            # Privacy page should score low - check if it exists in results
            privacy_items = [item for item in result if "/privacy" in item["url"]]
            if privacy_items:  # Only check if privacy page is in top 5 results
                privacy_item = privacy_items[0]
                assert privacy_item["score"] <= 20
            
            # Verify scores are sorted (highest first)
            scores = [item["score"] for item in result]
            assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_empty_urls_returns_empty_list(
        self,
        sample_company_context: Dict[str, str]
    ):
        """Test that empty URL list returns empty result."""
        # Act
        result = await filter_valuable_urls(
            urls=[],
            company_context=sample_company_context,
            max_urls=5
        )
        
        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_max_urls_limit_respected(
        self,
        sample_urls: List[str],
        sample_company_context: Dict[str, str],
        mock_ai_response: List[Dict[str, Any]]
    ):
        """Test that max_urls limit is respected."""
        # Arrange
        with patch.object(ai_client, 'score_urls_for_business_intelligence', new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = mock_ai_response
            
            # Act
            result = await filter_valuable_urls(
                urls=sample_urls,
                company_context=sample_company_context,
                max_urls=3
            )
            
            # Assert
            assert len(result) == 3
            assert result[0]["score"] >= result[1]["score"] >= result[2]["score"]  # Sorted by score

    @pytest.mark.asyncio
    async def test_ai_client_initialization(self):
        """Test that AI client properly initializes with OpenAI key."""
        # This test verifies the AI client can access the OpenAI key
        assert ai_client._has_api_key() is True
        assert ai_client.api_key is not None
        assert len(ai_client.api_key.strip()) > 0

    @pytest.mark.asyncio
    async def test_ai_client_singleton_pattern(self):
        """Test that AI client follows singleton pattern."""
        # Create new instance
        new_instance = AIClient()
        
        # Should be the same instance
        assert new_instance is ai_client
        assert id(new_instance) == id(ai_client)


class TestAIClientIntegration:
    """Test AI client integration with OpenAI."""

    @pytest.mark.asyncio
    async def test_ai_client_can_build_prompt(
        self,
        sample_urls: List[str],
        sample_company_context: Dict[str, str]
    ):
        """Test that AI client can build proper prompts."""
        prompt = ai_client._build_scoring_prompt(sample_urls, str(sample_company_context))
        
        # Assert prompt contains expected elements
        assert "business intelligence analyst" in prompt
        assert "https://example.com/about" in prompt
        assert "Company Context:" in prompt
        assert "Scoring Guidelines:" in prompt
        assert "Return ONLY valid JSON" in prompt

    @pytest.mark.asyncio
    async def test_ai_client_response_parsing(self):
        """Test AI client response parsing."""
        # Mock OpenAI response
        mock_response = """[
  {
    "url": "https://example.com/about",
    "score": 95,
    "reason": "Company mission and values page",
    "category": "leadership"
  }
]"""
        
        # Test parsing
        parsed = ai_client._parse_ai_response(mock_response, ["https://example.com/about"])
        
        # Assert
        assert len(parsed) == 1
        assert parsed[0]["url"] == "https://example.com/about"
        assert parsed[0]["score"] == 95
        assert parsed[0]["category"] == "leadership"

    @pytest.mark.asyncio
    async def test_ai_client_handles_malformed_response(self):
        """Test AI client handles malformed responses gracefully."""
        # Mock malformed response
        malformed_response = "This is not valid JSON"
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="Invalid JSON response"):
            ai_client._parse_ai_response(malformed_response, ["https://example.com/about"]) 