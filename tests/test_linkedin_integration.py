# ==============================================================================
# test_linkedin_integration.py — LinkedIn service integration tests
# ==============================================================================
# Purpose: Test LinkedIn profile analysis and scraping functionality
# Sections: Imports, Test Configuration, Integration Tests, Mock Data
# ==============================================================================

# Standard Library --------------------------------------------------------------
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from typing import Dict, Any

# Third Party -------------------------------------------------------------------
# (none)

# Core (App-wide) ---------------------------------------------------------------
from services.linkedin import (
    analyze_linkedin_profile,
    LinkedInProfileAnalyzer,
    ScrapingDogClient,
    extract_profile_id,
    is_valid_linkedin_url,
    normalize_linkedin_url,
    get_profile_url_from_id
)


class TestLinkedInURLParser:
    """Test LinkedIn URL parsing functionality."""
    
    def test_extract_profile_id_valid_urls(self):
        """Test extracting profile ID from valid LinkedIn URLs."""
        test_cases = [
            ("https://linkedin.com/in/johndoe", "johndoe"),
            ("https://www.linkedin.com/in/johndoe/", "johndoe"),
            ("https://linkedin.com/in/johndoe?trk=profile", "johndoe"),
            ("linkedin.com/in/johndoe", "johndoe"),
            ("https://www.linkedin.com/in/richard-branson", "richard-branson"),
            ("https://linkedin.com/in/user_123", "user_123"),
        ]
        
        for url, expected_id in test_cases:
            result = extract_profile_id(url)
            assert result == expected_id, f"Failed for URL: {url}"
    
    def test_extract_profile_id_invalid_urls(self):
        """Test extracting profile ID from invalid LinkedIn URLs."""
        invalid_urls = [
            "",
            "https://google.com/in/johndoe",
            "https://linkedin.com/company/example",
            "https://linkedin.com/in/",
            "https://linkedin.com/in",
            "not-a-url",
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError):
                extract_profile_id(url)
    
    def test_is_valid_linkedin_url(self):
        """Test LinkedIn URL validation."""
        valid_urls = [
            "https://linkedin.com/in/johndoe",
            "https://www.linkedin.com/in/johndoe/",
            "linkedin.com/in/johndoe",
        ]
        
        invalid_urls = [
            "",
            "https://google.com/in/johndoe",
            "https://linkedin.com/company/example",
            "not-a-url",
        ]
        
        for url in valid_urls:
            assert is_valid_linkedin_url(url), f"Should be valid: {url}"
        
        for url in invalid_urls:
            assert not is_valid_linkedin_url(url), f"Should be invalid: {url}"
    
    def test_normalize_linkedin_url(self):
        """Test LinkedIn URL normalization."""
        test_cases = [
            ("linkedin.com/in/johndoe", "https://www.linkedin.com/in/johndoe"),
            ("https://linkedin.com/in/johndoe?trk=profile", "https://www.linkedin.com/in/johndoe"),
            ("https://www.linkedin.com/in/johndoe/", "https://www.linkedin.com/in/johndoe"),
        ]
        
        for input_url, expected_url in test_cases:
            result = normalize_linkedin_url(input_url)
            assert result == expected_url, f"Failed for URL: {input_url}"
    
    def test_get_profile_url_from_id(self):
        """Test generating LinkedIn URL from profile ID."""
        test_cases = [
            ("johndoe", "https://www.linkedin.com/in/johndoe"),
            ("richard-branson", "https://www.linkedin.com/in/richard-branson"),
            ("user_123", "https://www.linkedin.com/in/user_123"),
        ]
        
        for profile_id, expected_url in test_cases:
            result = get_profile_url_from_id(profile_id)
            assert result == expected_url, f"Failed for profile ID: {profile_id}"
        
        # Test invalid profile ID
        with pytest.raises(ValueError):
            get_profile_url_from_id("")


class TestScrapingDogClient:
    """Test ScrapingDog API client functionality."""
    
    @pytest.fixture
    def client(self):
        """Create ScrapingDog client instance."""
        return ScrapingDogClient(api_key="test-api-key")
    
    @pytest.fixture
    def client_no_key(self):
        """Create ScrapingDog client without API key."""
        return ScrapingDogClient(api_key=None)
    
    def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.api_key == "test-api-key"
        assert client.base_url == "https://api.scrapingdog.com/linkedin/"
        assert client.timeout == 30
        assert client.max_retries == 3
    
    def test_has_api_key(self, client):
        """Test API key validation."""
        assert client._has_api_key() is True
        
        # Create a new client with no API key and patched settings
        with patch('services.linkedin.scrapingdog_client.settings') as mock_settings:
            mock_settings.scrapingdog_api_key = None
            client_no_key = ScrapingDogClient(api_key=None)
            assert client_no_key._has_api_key() is False
    
    @pytest.mark.asyncio
    async def test_scrape_profile_with_api_key(self, client):
        """Test profile scraping with valid API key."""
        with patch.object(client, '_make_request') as mock_request:
            mock_response = {
                "fullName": "John Doe",
                "headline": "Software Engineer",
                "experience": []
            }
            mock_request.return_value = mock_response
            
            result = await client.scrape_profile("https://linkedin.com/in/johndoe")
            
            assert result == mock_response
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_scrape_profile_without_api_key(self):
        """Test profile scraping without API key (returns mock data)."""
        # Create client with no API key and patched settings
        with patch('services.linkedin.scrapingdog_client.settings') as mock_settings:
            mock_settings.scrapingdog_api_key = None
            client_no_key = ScrapingDogClient(api_key=None)
            result = await client_no_key.scrape_profile("https://linkedin.com/in/johndoe")
            
            # The mock response structure has changed - check for the correct structure
            assert isinstance(result, dict)
            assert "fullName" in result
            assert "Mock User johndoe" in result["fullName"]
            assert result["headline"] == "Software Engineer at Mock Company"
    
    @pytest.mark.asyncio
    async def test_scrape_profile_invalid_url(self, client):
        """Test profile scraping with invalid URL."""
        with pytest.raises(ValueError, match="URL must be from linkedin.com domain"):
            await client.scrape_profile("https://google.com/in/johndoe")
    
    @pytest.mark.asyncio
    async def test_make_request_retry_logic(self, client):
        """Test retry logic for failed requests."""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock client to raise HTTPStatusError on first call, succeed on second
            mock_response = MagicMock()
            mock_response.json.return_value = {"success": True}
            
            mock_instance = AsyncMock()
            mock_instance.get.side_effect = [
                Exception("Network error"),  # First call fails
                mock_response  # Second call succeeds
            ]
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            result = await client._make_request({"api_key": "test", "linkId": "test"})
            
            assert result == {"success": True}
            assert mock_instance.get.call_count == 2
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, client):
        """Test API connection test with valid key."""
        with patch.object(client, 'scrape_profile') as mock_scrape:
            mock_scrape.side_effect = ValueError("Profile not found")  # Expected for test profile
            
            result = await client.test_connection()
            
            assert result is True
            mock_scrape.assert_called_once_with("https://linkedin.com/in/test-profile")
    
    @pytest.mark.asyncio
    async def test_test_connection_no_key(self):
        """Test API connection test without API key."""
        # Create client with no API key and patched settings
        with patch('services.linkedin.scrapingdog_client.settings') as mock_settings:
            mock_settings.scrapingdog_api_key = None
            client_no_key = ScrapingDogClient(api_key=None)
            result = await client_no_key.test_connection()
            assert result is False


class TestLinkedInProfileAnalyzer:
    """Test LinkedIn profile data analysis."""
    
    @pytest.fixture
    def analyzer(self):
        """Create profile analyzer instance."""
        return LinkedInProfileAnalyzer()
    
    @pytest.fixture
    def sample_profile_data(self):
        """Sample LinkedIn profile data from ScrapingDog API."""
        return {
            "fullName": "John Doe",
            "first_name": "John",
            "last_name": "Doe",
            "headline": "Software Engineer at Tech Company",
            "location": "San Francisco, CA",
            "public_identifier": "johndoe",
            "followers": "1,234 followers",
            "connections": "500+ connections",
            "about": "Experienced software engineer with expertise in Python and AI.",
            "experience": [
                {
                    "position": "Software Engineer",
                    "company_name": "Tech Company",
                    "location": "San Francisco, CA",
                    "summary": "Building amazing software solutions",
                    "starts_at": "Jan 2022",
                    "ends_at": "Present",
                    "duration": "2 years"
                }
            ],
            "education": [
                {
                    "school": "University of California",
                    "degree": "Bachelor of Science in Computer Science",
                    "field_of_study": "Computer Science",
                    "starts_at": "2018",
                    "ends_at": "2022"
                }
            ],
            "articles": [
                {
                    "title": "The Future of AI in Software Development",
                    "author": "By John Doe",
                    "published_date": "Mar 15, 2023"
                }
            ],
            "activities": [
                {
                    "title": "Shared an article about machine learning",
                    "activity": "Shared by John Doe"
                }
            ],
            "people_also_viewed": [
                {
                    "name": "Jane Smith",
                    "summary": "Senior Engineer at Another Company",
                    "location": "New York, NY"
                }
            ],
            "similar_profiles": [],
            "recommendations": [],
            "publications": [],
            "courses": [],
            "languages": [],
            "organizations": [],
            "projects": [],
            "awards": [],
            "score": []
        }
    
    def test_analyze_profile_success(self, analyzer, sample_profile_data):
        """Test successful profile analysis."""
        result = analyzer.analyze_profile(sample_profile_data)
        
        # Check that all analysis sections are present
        assert "profile_summary" in result
        assert "professional_info" in result
        assert "experience" in result
        assert "education" in result
        assert "content_analysis" in result
        assert "network_insights" in result
        assert "business_intelligence" in result
        assert "raw_data" in result
        
        # Check profile summary
        summary = result["profile_summary"]
        assert summary["full_name"] == "John Doe"
        assert summary["headline"] == "Software Engineer at Tech Company"
        assert summary["location"] == "San Francisco, CA"
        
        # Check professional info
        prof_info = result["professional_info"]
        assert prof_info["current_position"]["position"] == "Software Engineer"
        assert prof_info["current_position"]["company_name"] == "Tech Company"
        
        # Check experience
        experience = result["experience"]
        assert experience["total_positions"] == 1
        assert experience["seniority_level"] == "mid_level"
        
        # Check education
        education = result["education"]
        assert education["total_degrees"] == 1
        assert education["universities"] == ["University of California"]
        
        # Check content analysis
        content = result["content_analysis"]
        assert content["articles"]["total_articles"] == 1
        assert content["activities"]["total_activities"] == 1
        
        # Check network insights
        network = result["network_insights"]
        assert network["network_size"]["followers"] == 1234
        assert network["people_also_viewed"]["total"] == 1
        
        # Check business intelligence
        business = result["business_intelligence"]
        assert business["professional_trajectory"]["trajectory"] == "individual_contributor"
        assert "Technology" in business["industry_expertise"]  # From position analysis
    
    def test_analyze_profile_with_list_data(self, analyzer, sample_profile_data):
        """Test profile analysis with list data (API response format)."""
        list_data = [sample_profile_data]
        result = analyzer.analyze_profile(list_data)
        
        # Should work the same as single profile data
        assert result["profile_summary"]["full_name"] == "John Doe"
    
    def test_analyze_profile_empty_data(self, analyzer):
        """Test profile analysis with empty data."""
        result = analyzer.analyze_profile({})
        
        # Should handle empty data gracefully
        assert "profile_summary" in result
        assert result["profile_summary"]["full_name"] == ""
    
    def test_analyze_profile_error_handling(self, analyzer):
        """Test profile analysis error handling."""
        # Pass invalid data that would cause an error
        invalid_data = {"experience": "not_a_list"}
        
        result = analyzer.analyze_profile(invalid_data)
        
        # Should return error information
        assert "error" in result
        assert "Profile analysis failed" in result["error"]
    
    def test_extract_profile_summary(self, analyzer, sample_profile_data):
        """Test profile summary extraction."""
        summary = analyzer._extract_profile_summary(sample_profile_data)
        
        assert summary["full_name"] == "John Doe"
        assert summary["first_name"] == "John"
        assert summary["last_name"] == "Doe"
        assert summary["headline"] == "Software Engineer at Tech Company"
        assert summary["location"] == "San Francisco, CA"
        assert summary["profile_id"] == "johndoe"
        assert summary["followers"] == "1,234 followers"
        assert summary["connections"] == "500+ connections"
    
    def test_extract_professional_info(self, analyzer, sample_profile_data):
        """Test professional information extraction."""
        prof_info = analyzer._extract_professional_info(sample_profile_data)
        
        assert prof_info["current_position"]["position"] == "Software Engineer"
        assert prof_info["current_position"]["company_name"] == "Tech Company"
        assert prof_info["companies_worked_at"] == ["Tech Company"]
        assert "python" in prof_info["skills_mentioned"]
        assert "ai" in prof_info["skills_mentioned"]
    
    def test_extract_experience(self, analyzer, sample_profile_data):
        """Test experience extraction."""
        experience = analyzer._extract_experience(sample_profile_data)
        
        assert experience["total_positions"] == 1
        assert experience["seniority_level"] == "mid_level"
        assert experience["recent_companies"] == ["Tech Company"]
    
    def test_extract_education(self, analyzer, sample_profile_data):
        """Test education extraction."""
        education = analyzer._extract_education(sample_profile_data)
        
        assert education["total_degrees"] == 1
        assert education["universities"] == ["University of California"]
        assert education["fields_of_study"] == ["Computer Science"]
    
    def test_extract_content_analysis(self, analyzer, sample_profile_data):
        """Test content analysis extraction."""
        content = analyzer._extract_content_analysis(sample_profile_data)
        
        assert content["articles"]["total_articles"] == 1
        assert content["activities"]["total_activities"] == 1
        assert "Artificial Intelligence" in content["content_themes"]
    
    def test_extract_network_insights(self, analyzer, sample_profile_data):
        """Test network insights extraction."""
        network = analyzer._extract_network_insights(sample_profile_data)
        
        assert network["network_size"]["followers"] == 1234
        assert network["network_size"]["connections"] == 500
        assert network["people_also_viewed"]["total"] == 1
        assert network["influence_indicators"]["influence_score"] >= 0
    
    def test_extract_business_intelligence(self, analyzer, sample_profile_data):
        """Test business intelligence extraction."""
        business = analyzer._extract_business_intelligence(sample_profile_data)
        
        assert business["professional_trajectory"]["trajectory"] == "individual_contributor"
        assert "Technology" in business["industry_expertise"]
        assert business["thought_leadership"]["leadership_level"] in ["low", "medium", "high"]
        assert business["geographic_presence"]["current_location"] == "San Francisco, CA"


class TestLinkedInAnalyzerIntegration:
    """Test the main LinkedIn analyzer integration."""
    
    @pytest.mark.asyncio
    async def test_analyze_linkedin_profile_success(self):
        """Test successful LinkedIn profile analysis."""
        with patch('services.linkedin.analyzer.ScrapingDogClient') as mock_client_class:
            with patch('services.linkedin.analyzer.LinkedInProfileAnalyzer') as mock_analyzer_class:
                # Mock client
                mock_client = AsyncMock()
                mock_client.scrape_profile.return_value = {
                    "fullName": "John Doe",
                    "headline": "Software Engineer"
                }
                mock_client_class.return_value = mock_client
                
                # Mock analyzer
                mock_analyzer = MagicMock()
                mock_analyzer.analyze_profile.return_value = {
                    "profile_summary": {"full_name": "John Doe"},
                    "professional_info": {},
                    "experience": {},
                    "education": {},
                    "content_analysis": {},
                    "network_insights": {},
                    "business_intelligence": {}
                }
                mock_analyzer_class.return_value = mock_analyzer
                
                result = await analyze_linkedin_profile("https://linkedin.com/in/johndoe")
                
                assert result["status"] == "success"
                assert result["url"] == "https://linkedin.com/in/johndoe"
                assert "analysis" in result
                assert "raw_data" in result
                assert "timestamp" in result
                
                # Verify client and analyzer were called
                mock_client.scrape_profile.assert_called_once_with("https://linkedin.com/in/johndoe")
                mock_analyzer.analyze_profile.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_linkedin_profile_invalid_url(self):
        """Test LinkedIn profile analysis with invalid URL."""
        result = await analyze_linkedin_profile("https://google.com/in/johndoe")
        
        assert result["status"] == "error"
        assert "Invalid LinkedIn URL format" in result["error"]
    
    @pytest.mark.asyncio
    async def test_analyze_linkedin_profile_client_error(self):
        """Test LinkedIn profile analysis when client fails."""
        with patch('services.linkedin.analyzer.ScrapingDogClient') as mock_client_class:
            # Mock client to raise exception
            mock_client = AsyncMock()
            mock_client.scrape_profile.side_effect = Exception("API error")
            mock_client_class.return_value = mock_client
            
            result = await analyze_linkedin_profile("https://linkedin.com/in/johndoe")
            
            assert result["status"] == "error"
            assert "API error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_analyze_linkedin_profile_analyzer_error(self):
        """Test LinkedIn profile analysis when analyzer fails."""
        with patch('services.linkedin.analyzer.ScrapingDogClient') as mock_client_class:
            with patch('services.linkedin.analyzer.LinkedInProfileAnalyzer') as mock_analyzer_class:
                # Mock client
                mock_client = AsyncMock()
                mock_client.scrape_profile.return_value = {"fullName": "John Doe"}
                mock_client_class.return_value = mock_client
                
                # Mock analyzer to return error
                mock_analyzer = MagicMock()
                mock_analyzer.analyze_profile.return_value = {
                    "error": "Analysis failed"
                }
                mock_analyzer_class.return_value = mock_analyzer
                
                result = await analyze_linkedin_profile("https://linkedin.com/in/johndoe")
                
                assert result["status"] == "error"
                assert "Analysis failed" in result["error"]


class TestLinkedInIntegrationEndToEnd:
    """Test end-to-end LinkedIn integration workflow."""
    
    @pytest.mark.asyncio
    async def test_full_linkedin_workflow(self):
        """Test the complete LinkedIn analysis workflow."""
        # This test simulates the full workflow without making actual API calls
        test_url = "https://linkedin.com/in/testuser"
    
        # Test URL parsing
        profile_id = extract_profile_id(test_url)
        assert profile_id == "testuser"
    
        # Test URL validation
        assert is_valid_linkedin_url(test_url) is True
    
        # Test client creation (without API key for mock data)
        with patch('services.linkedin.scrapingdog_client.settings') as mock_settings:
            mock_settings.scrapingdog_api_key = None
            client = ScrapingDogClient(api_key=None)
            assert client._has_api_key() is False
    
            # Test profile scraping (will return mock data)
            raw_data = await client.scrape_profile(test_url)
            assert "fullName" in raw_data
            assert "Mock User testuser" in raw_data["fullName"]
    
            # Test profile analysis
            analyzer = LinkedInProfileAnalyzer()
            analysis = analyzer.analyze_profile(raw_data)
    
            assert "profile_summary" in analysis
            assert "professional_info" in analysis
            assert "experience" in analysis
            assert "education" in analysis
            assert "content_analysis" in analysis
            assert "network_insights" in analysis
            assert "business_intelligence" in analysis
    
            # Test main analyzer function with mocked dependencies
            with patch('services.linkedin.scrapingdog_client.ScrapingDogClient.scrape_profile') as mock_scrape:
                mock_scrape.return_value = raw_data
                
                result = await analyze_linkedin_profile(test_url)
                assert result["status"] == "success"
                assert "analysis" in result
                assert "raw_data" in result
                assert "timestamp" in result
                
                # Check the analysis structure
                analysis = result["analysis"]
                assert "profile_summary" in analysis
                assert "professional_info" in analysis
                assert "experience" in analysis
                assert "education" in analysis
                assert "content_analysis" in analysis
                assert "network_insights" in analysis
                assert "business_intelligence" in analysis 