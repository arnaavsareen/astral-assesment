"""Tests for intelligence collection domain process_registration function."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from typing import Dict, Any

# Domain imports
from domains.intelligence_collection import process_registration
from core.types.models import RegistrationRequest, AnalysisOutput


@pytest.fixture
def sample_website_data() -> Dict[str, Any]:
    """Sample registration data with website only."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "company_website": "https://example.com",
        "linkedin": None
    }


@pytest.fixture
def sample_linkedin_data() -> Dict[str, Any]:
    """Sample registration data with LinkedIn only."""
    return {
        "first_name": "Jane",
        "last_name": "Smith",
        "company_website": None,
        "linkedin": "https://linkedin.com/in/janesmith"
    }


@pytest.fixture
def sample_both_urls_data() -> Dict[str, Any]:
    """Sample registration data with both website and LinkedIn."""
    return {
        "first_name": "Bob",
        "last_name": "Johnson",
        "company_website": "https://company.com",
        "linkedin": "https://linkedin.com/in/bobjohnson"
    }


@pytest.fixture
def sample_no_urls_data() -> Dict[str, Any]:
    """Sample registration data with no URLs (should fail validation)."""
    return {
        "first_name": "Alice",
        "last_name": "Brown",
        "company_website": None,
        "linkedin": None
    }


@pytest.fixture
def mock_discovered_urls() -> list:
    """Mock discovered URLs from website crawling."""
    return [
        {"url": "https://example.com/about", "title": "About Us"},
        {"url": "https://example.com/services", "title": "Services"},
        {"url": "https://example.com/contact", "title": "Contact"},
        {"url": "https://example.com/blog", "title": "Blog"},
        {"url": "https://example.com/careers", "title": "Careers"},
        {"url": "https://example.com/pricing", "title": "Pricing"},
        {"url": "https://example.com/faq", "title": "FAQ"}
    ]


@pytest.fixture
def mock_filtered_urls() -> list:
    """Mock filtered URLs (subset of discovered URLs)."""
    return [
        {
            "url": "https://example.com/about", 
            "reason": "High value content",
            "score": 95,
            "category": "leadership"
        },
        {
            "url": "https://example.com/services", 
            "reason": "Core business info",
            "score": 85,
            "category": "products"
        },
        {
            "url": "https://example.com/contact", 
            "reason": "Contact information",
            "score": 20,
            "category": "other"
        }
    ]


@pytest.fixture
def mock_extracted_content() -> Dict[str, str]:
    """Mock extracted content from URLs."""
    return {
        "https://example.com/about": "# About Us\n\nWe are a leading technology company...",
        "https://example.com/services": "# Our Services\n\nWe provide innovative solutions...",
        "https://example.com/contact": "# Contact Us\n\nGet in touch with our team..."
    }


@pytest.fixture
def mock_linkedin_analysis() -> Dict[str, Any]:
    """Mock LinkedIn profile analysis results."""
    return {
        "profile_url": "https://linkedin.com/in/janesmith",
        "name": "Jane Smith",
        "title": "Senior Software Engineer",
        "company": "Tech Corp",
        "summary": "Experienced software engineer with 5+ years...",
        "skills": ["Python", "JavaScript", "React", "Node.js"],
        "experience": [
            {"title": "Senior Software Engineer", "company": "Tech Corp", "duration": "2 years"},
            {"title": "Software Engineer", "company": "Startup Inc", "duration": "3 years"}
        ]
    }


class TestProcessRegistration:
    """Test cases for process_registration function."""

    @pytest.mark.asyncio
    async def test_website_only_registration(
        self,
        sample_website_data: Dict[str, Any],
        mock_discovered_urls: list,
        mock_filtered_urls: list,
        mock_extracted_content: Dict[str, str]
    ):
        """Test registration with website URL only."""
        # Arrange
        registration_data = RegistrationRequest(**sample_website_data)
        
        # Mock all external dependencies
        with patch('domains.intelligence_collection.discover_company_urls', new_callable=AsyncMock) as mock_discover, \
             patch('domains.intelligence_collection.filter_valuable_urls', return_value=mock_filtered_urls) as mock_filter, \
             patch('domains.intelligence_collection.extract_content', new_callable=AsyncMock) as mock_extract, \
             patch('domains.intelligence_collection.analyze_linkedin_profile', return_value=None) as mock_linkedin, \
             patch('domains.intelligence_collection.save_analysis', new_callable=AsyncMock) as mock_save:
            
            mock_discover.return_value = mock_discovered_urls
            mock_extract.return_value = mock_extracted_content
            
            # Act
            result = await process_registration(registration_data)
            
            # Assert
            assert isinstance(result, AnalysisOutput)
            assert result.request_id is not None
            assert result.input_data == registration_data
            assert result.linkedin_analysis == {"status": "not_implemented"}
            assert result.website_analysis is not None

            # Verify website analysis structure
            website_analysis = result.website_analysis
            assert "discovered_urls" in website_analysis
            assert "filtered_urls" in website_analysis
            assert "scraped_content" in website_analysis
            
            # Verify filtered URLs structure
            filtered_urls = website_analysis["filtered_urls"]
            assert len(filtered_urls) > 0
            for url_data in filtered_urls:
                assert "url" in url_data
                assert "reason" in url_data
                assert "score" in url_data
                assert "category" in url_data
            
            # Verify scraped content structure
            scraped_content = website_analysis["scraped_content"]
            assert isinstance(scraped_content, dict)
            assert len(scraped_content) > 0
            
            # Verify function calls
            mock_discover.assert_called_once_with("https://example.com/")  # URL normalization adds trailing slash
            
            # Check filter call with flexible assertion for HttpUrl object
            filter_call_args = mock_filter.call_args
            assert filter_call_args is not None
            assert filter_call_args.kwargs["urls"] == mock_discovered_urls
            assert filter_call_args.kwargs["company_context"]["company_name"] == "John Doe's company"
            assert str(filter_call_args.kwargs["company_context"]["website"]) == "https://example.com/"
            assert filter_call_args.kwargs["company_context"]["objective"] == "business intelligence gathering"
            assert filter_call_args.kwargs["max_urls"] == 7
            mock_extract.assert_called_once_with(mock_filtered_urls)
            mock_linkedin.assert_not_called()
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_linkedin_only_registration(
        self,
        sample_linkedin_data: Dict[str, Any],
        mock_linkedin_analysis: Dict[str, Any]
    ):
        """Test registration with LinkedIn URL only."""
        # Arrange
        registration_data = RegistrationRequest(**sample_linkedin_data)
        
        # Mock external dependencies
        with patch('domains.intelligence_collection.discover_company_urls', new_callable=AsyncMock) as mock_discover, \
             patch('domains.intelligence_collection.filter_valuable_urls') as mock_filter, \
             patch('domains.intelligence_collection.extract_content', new_callable=AsyncMock) as mock_extract, \
             patch('domains.intelligence_collection.analyze_linkedin_profile', return_value=mock_linkedin_analysis) as mock_linkedin, \
             patch('domains.intelligence_collection.save_analysis', new_callable=AsyncMock) as mock_save:
            
            # Act
            result = await process_registration(registration_data)
            
            # Assert
            assert isinstance(result, AnalysisOutput)
            assert result.request_id is not None
            assert result.input_data == registration_data
            assert result.linkedin_analysis == mock_linkedin_analysis
            assert result.website_analysis is None  # No company website provided

            # Verify LinkedIn analysis is present
            assert result.linkedin_analysis is not None
            assert "profile_url" in result.linkedin_analysis
            assert "name" in result.linkedin_analysis

            # Verify function calls
            mock_linkedin.assert_called_once_with("https://linkedin.com/in/janesmith")
            mock_discover.assert_not_called()
            mock_filter.assert_not_called()
            mock_extract.assert_not_called()
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_both_urls_provided(
        self,
        sample_both_urls_data: Dict[str, Any],
        mock_discovered_urls: list,
        mock_filtered_urls: list,
        mock_extracted_content: Dict[str, str],
        mock_linkedin_analysis: Dict[str, Any]
    ):
        """Test registration with both website and LinkedIn URLs."""
        # Arrange
        registration_data = RegistrationRequest(**sample_both_urls_data)
        
        # Mock external dependencies
        with patch('domains.intelligence_collection.discover_company_urls', new_callable=AsyncMock) as mock_discover, \
             patch('domains.intelligence_collection.filter_valuable_urls', return_value=mock_filtered_urls) as mock_filter, \
             patch('domains.intelligence_collection.extract_content', new_callable=AsyncMock) as mock_extract, \
             patch('domains.intelligence_collection.analyze_linkedin_profile', return_value=mock_linkedin_analysis) as mock_linkedin, \
             patch('domains.intelligence_collection.save_analysis', new_callable=AsyncMock) as mock_save:
            
            mock_discover.return_value = mock_discovered_urls
            mock_extract.return_value = mock_extracted_content
            
            # Act
            result = await process_registration(registration_data)
            
            # Assert
            assert isinstance(result, AnalysisOutput)
            assert result.request_id is not None
            assert result.input_data == registration_data
            assert result.linkedin_analysis == mock_linkedin_analysis
            assert result.website_analysis is not None
            
            # Verify both analyses are present
            website_analysis = result.website_analysis
            assert "discovered_urls" in website_analysis
            assert "filtered_urls" in website_analysis
            assert "scraped_content" in website_analysis
            
            # Verify filtered URLs structure
            filtered_urls = website_analysis["filtered_urls"]
            assert len(filtered_urls) > 0
            for url_data in filtered_urls:
                assert "url" in url_data
                assert "reason" in url_data
                assert "score" in url_data
                assert "category" in url_data
            
            # Verify scraped content structure
            scraped_content = website_analysis["scraped_content"]
            assert isinstance(scraped_content, dict)
            assert len(scraped_content) > 0
            
            # Verify all function calls
            mock_linkedin.assert_called_once_with("https://linkedin.com/in/bobjohnson")
            mock_discover.assert_called_once_with("https://company.com/")  # URL normalization adds trailing slash
            
            # Check filter call with flexible assertion for HttpUrl object
            filter_call_args = mock_filter.call_args
            assert filter_call_args is not None
            assert filter_call_args.kwargs["urls"] == mock_discovered_urls
            assert filter_call_args.kwargs["company_context"]["company_name"] == "Bob Johnson's company"
            assert str(filter_call_args.kwargs["company_context"]["website"]) == "https://company.com/"
            assert filter_call_args.kwargs["company_context"]["objective"] == "business intelligence gathering"
            assert filter_call_args.kwargs["max_urls"] == 7
            mock_extract.assert_called_once_with(mock_filtered_urls)
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_missing_urls_raises_error(self, sample_no_urls_data: Dict[str, Any]):
        """Test that registration without URLs raises validation error."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="At least one URL.*must be provided"):
            registration_data = RegistrationRequest(**sample_no_urls_data)
            await process_registration(registration_data)

    @pytest.mark.asyncio
    async def test_save_analysis_failure_does_not_fail_process(
        self,
        sample_website_data: Dict[str, Any],
        mock_discovered_urls: list,
        mock_filtered_urls: list,
        mock_extracted_content: Dict[str, str]
    ):
        """Test that save_analysis failure doesn't fail the entire process."""
        # Arrange
        registration_data = RegistrationRequest(**sample_website_data)
        
        # Mock external dependencies with save_analysis failing
        with patch('domains.intelligence_collection.discover_company_urls', new_callable=AsyncMock) as mock_discover, \
             patch('domains.intelligence_collection.filter_valuable_urls', return_value=mock_filtered_urls) as mock_filter, \
             patch('domains.intelligence_collection.extract_content', new_callable=AsyncMock) as mock_extract, \
             patch('domains.intelligence_collection.analyze_linkedin_profile', return_value=None) as mock_linkedin, \
             patch('domains.intelligence_collection.save_analysis', new_callable=AsyncMock) as mock_save:
            
            mock_discover.return_value = mock_discovered_urls
            mock_extract.return_value = mock_extracted_content
            mock_save.side_effect = Exception("Save failed")
            
            # Act
            result = await process_registration(registration_data)
            
            # Assert
            assert isinstance(result, AnalysisOutput)
            assert result.request_id is not None
            assert result.website_analysis is not None
            # Process should complete successfully even if save fails

    @pytest.mark.asyncio
    async def test_discovery_failure_handled_gracefully(
        self,
        sample_website_data: Dict[str, Any]
    ):
        """Test that discovery failure is handled gracefully."""
        # Arrange
        registration_data = RegistrationRequest(**sample_website_data)
        
        # Mock discovery to fail
        with patch('domains.intelligence_collection.discover_company_urls', new_callable=AsyncMock) as mock_discover, \
             patch('domains.intelligence_collection.filter_valuable_urls', return_value=[]) as mock_filter, \
             patch('domains.intelligence_collection.extract_content', new_callable=AsyncMock) as mock_extract, \
             patch('domains.intelligence_collection.analyze_linkedin_profile', return_value=None) as mock_linkedin, \
             patch('domains.intelligence_collection.save_analysis', new_callable=AsyncMock) as mock_save:
            
            mock_discover.return_value = []  # Discovery returns empty list
            mock_extract.return_value = {}
            
            # Act
            result = await process_registration(registration_data)
            
            # Assert
            assert isinstance(result, AnalysisOutput)
            assert result.website_analysis is not None
            assert result.website_analysis["discovered_urls"] == []
            assert result.website_analysis["filtered_urls"] == []
            assert result.website_analysis["scraped_content"] == {}

    @pytest.mark.asyncio
    async def test_request_id_uniqueness(self, sample_website_data: Dict[str, Any]):
        """Test that each request gets a unique request_id."""
        # Arrange
        registration_data = RegistrationRequest(**sample_website_data)
        
        # Mock external dependencies
        with patch('domains.intelligence_collection.discover_company_urls', new_callable=AsyncMock) as mock_discover, \
             patch('domains.intelligence_collection.filter_valuable_urls', return_value=[]) as mock_filter, \
             patch('domains.intelligence_collection.extract_content', new_callable=AsyncMock) as mock_extract, \
             patch('domains.intelligence_collection.analyze_linkedin_profile', return_value=None) as mock_linkedin, \
             patch('domains.intelligence_collection.save_analysis', new_callable=AsyncMock) as mock_save:
            
            mock_discover.return_value = []
            mock_extract.return_value = {}
            
            # Act - process same data twice
            result1 = await process_registration(registration_data)
            result2 = await process_registration(registration_data)
            
            # Assert
            assert result1.request_id != result2.request_id
            assert isinstance(result1.request_id, str)
            assert isinstance(result2.request_id, str)

    @pytest.mark.asyncio
    async def test_timestamp_is_recent(self, sample_website_data: Dict[str, Any]):
        """Test that analysis timestamp is recent."""
        # Arrange
        registration_data = RegistrationRequest(**sample_website_data)
        start_time = datetime.now(timezone.utc)
        
        # Mock external dependencies
        with patch('domains.intelligence_collection.discover_company_urls', new_callable=AsyncMock) as mock_discover, \
             patch('domains.intelligence_collection.filter_valuable_urls', return_value=[]) as mock_filter, \
             patch('domains.intelligence_collection.extract_content', new_callable=AsyncMock) as mock_extract, \
             patch('domains.intelligence_collection.analyze_linkedin_profile', return_value=None) as mock_linkedin, \
             patch('domains.intelligence_collection.save_analysis', new_callable=AsyncMock) as mock_save:
            
            mock_discover.return_value = []
            mock_extract.return_value = {}
            
            # Act
            result = await process_registration(registration_data)
            end_time = datetime.now(timezone.utc)
            
            # Assert - convert result.timestamp to timezone-aware for comparison
            result_timestamp = result.timestamp.replace(tzinfo=timezone.utc) if result.timestamp.tzinfo is None else result.timestamp
            assert start_time <= result_timestamp <= end_time 