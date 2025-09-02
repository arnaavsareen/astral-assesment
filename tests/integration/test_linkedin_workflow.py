# ==============================================================================
# test_linkedin_workflow.py — LinkedIn workflow integration tests
# ==============================================================================
# Purpose: Test complete LinkedIn analysis workflow across domains
# Sections: Imports, Test Configuration, Workflow Tests, Error Scenarios, Performance Tests
# ==============================================================================

# Standard Library --------------------------------------------------------------
import pytest
from unittest.mock import patch, AsyncMock
from typing import Dict, Any

# Third Party -------------------------------------------------------------------
# (none)

# Core (App-wide) ---------------------------------------------------------------
from domains.intelligence_collection.linkedin.analyzer import analyze_linkedin_profile
from domains.intelligence_collection.linkedin.url_parser import is_valid_linkedin_url, extract_profile_id
from core.clients.scrapingdog import ScrapingDogClient


@pytest.fixture
def sample_profile_data() -> Dict[str, Any]:
    """Sample LinkedIn profile data for integration testing."""
    return {
        "fullName": "Jane Smith",
        "first_name": "Jane",
        "last_name": "Smith",
        "headline": "Senior Product Manager at Innovation Corp",
        "location": "New York, NY",
        "public_identifier": "janesmith",
        "followers": "2,500+ followers",
        "connections": "1,000+ connections",
        "about": "Product leader with 8+ years experience in SaaS and mobile apps. Passionate about user experience and data-driven decision making.",
        "experience": [
            {
                "company_name": "Innovation Corp",
                "position": "Senior Product Manager",
                "starts_at": "2021-03",
                "ends_at": "Present",
                "industry": "Technology"
            },
            {
                "company_name": "StartupXYZ",
                "position": "Product Manager",
                "starts_at": "2019-01",
                "ends_at": "2021-02",
                "industry": "Technology"
            }
        ],
        "education": [
            {
                "school": "Stanford University",
                "degree": "Master of Business Administration",
                "field_of_study": "Business Administration"
            },
            {
                "school": "University of Michigan",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science"
            }
        ],
        "articles": [
            {
                "title": "Building Products Users Love",
                "published_date": "Jan 15, 2024"
            }
        ],
        "activities": [
            {
                "activity": "Shared by Jane Smith",
                "title": "Product Management Best Practices",
                "published_date": "Feb 1, 2024"
            }
        ]
    }


class TestLinkedInWorkflowIntegration:
    """Test complete LinkedIn analysis workflow integration."""
    
    @pytest.mark.asyncio
    async def test_full_linkedin_workflow_success(self, sample_profile_data: Dict[str, Any]):
        """Test the complete LinkedIn analysis workflow from URL to insights."""
        test_url = "https://linkedin.com/in/janesmith"
        
        # Test URL validation
        assert is_valid_linkedin_url(test_url) is True
        
        # Test profile ID extraction
        profile_id = extract_profile_id(test_url)
        assert profile_id == "janesmith"
        
        # Mock the entire workflow
        with patch('domains.intelligence_collection.linkedin.analyzer.ScrapingDogClient') as mock_client_class:
            with patch('domains.intelligence_collection.linkedin.analyzer.LinkedInProfileAnalyzer') as mock_analyzer_class:
                # Mock ScrapingDog client
                mock_client = AsyncMock()
                mock_client.scrape_profile.return_value = sample_profile_data
                mock_client_class.return_value = mock_client
                
                # Mock profile analyzer
                mock_analyzer = AsyncMock()
                mock_analyzer.analyze_profile.return_value = {
                    "profile_summary": {"full_name": "Jane Smith"},
                    "professional_info": {"current_position": {"position": "Senior Product Manager"}},
                    "experience": {"total_positions": 2},
                    "education": {"total_degrees": 2},
                    "ai_insights": {
                        "skills_analysis": {"detected_skills": ["Product Management", "SaaS"]},
                        "industry_expertise": {"primary_industry": "Technology"}
                    }
                }
                mock_analyzer_class.return_value = mock_analyzer
                
                # Execute the workflow
                result = await analyze_linkedin_profile(test_url)
                
                # Verify successful execution
                assert result["status"] == "success"
                assert result["url"] == test_url
                assert "analysis" in result
                assert "raw_data" in result
                assert "timestamp" in result
                
                # Verify the analysis structure
                analysis = result["analysis"]
                assert "profile_summary" in analysis
                assert "professional_info" in analysis
                assert "experience" in analysis
                assert "education" in analysis
                assert "ai_insights" in analysis
                
                # Verify AI insights
                ai_insights = analysis["ai_insights"]
                assert "skills_analysis" in ai_insights
                assert "industry_expertise" in ai_insights
                
                # Verify client and analyzer were called
                mock_client.scrape_profile.assert_called_once_with(test_url)
                mock_analyzer.analyze_profile.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_workflow_with_invalid_url(self):
        """Test workflow behavior with invalid LinkedIn URL."""
        invalid_urls = [
            "https://google.com/in/johndoe",
            "https://linkedin.com/company/example",
            "not-a-url",
            "",
            "https://linkedin.com/in/"  # Missing profile ID
        ]
        
        for url in invalid_urls:
            result = await analyze_linkedin_profile(url)
            
            assert result["status"] == "error"
            assert "Invalid LinkedIn URL format" in result["error"]
            assert result["url"] == url
            assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_workflow_with_scraping_failure(self):
        """Test workflow behavior when profile scraping fails."""
        test_url = "https://linkedin.com/in/johndoe"
        
        with patch('domains.intelligence_collection.linkedin.analyzer.ScrapingDogClient') as mock_client_class:
            # Mock client to raise exception
            mock_client = AsyncMock()
            mock_client.scrape_profile.side_effect = Exception("ScrapingDog API error")
            mock_client_class.return_value = mock_client
            
            result = await analyze_linkedin_profile(test_url)
            
            assert result["status"] == "error"
            assert "ScrapingDog API error" in result["error"]
            assert result["url"] == test_url
            assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_workflow_with_analysis_failure(self, sample_profile_data: Dict[str, Any]):
        """Test workflow behavior when profile analysis fails."""
        test_url = "https://linkedin.com/in/johndoe"
        
        with patch('domains.intelligence_collection.linkedin.analyzer.ScrapingDogClient') as mock_client_class:
            with patch('domains.intelligence_collection.linkedin.analyzer.LinkedInProfileAnalyzer') as mock_analyzer_class:
                # Mock client success
                mock_client = AsyncMock()
                mock_client.scrape_profile.return_value = sample_profile_data
                mock_client_class.return_value = mock_client
                
                # Mock analyzer failure
                mock_analyzer = AsyncMock()
                mock_analyzer.analyze_profile.return_value = {
                    "error": "Profile analysis failed due to invalid data"
                }
                mock_analyzer_class.return_value = mock_analyzer
                
                result = await analyze_linkedin_profile(test_url)
                
                assert result["status"] == "error"
                assert "Profile analysis failed due to invalid data" in result["error"]
                assert result["url"] == test_url
                assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_workflow_data_consistency(self, sample_profile_data: Dict[str, Any]):
        """Test that data flows consistently through the workflow."""
        test_url = "https://linkedin.com/in/janesmith"
        
        with patch('domains.intelligence_collection.linkedin.analyzer.ScrapingDogClient') as mock_client_class:
            with patch('domains.intelligence_collection.linkedin.analyzer.LinkedInProfileAnalyzer') as mock_analyzer_class:
                # Mock client
                mock_client = AsyncMock()
                mock_client.scrape_profile.return_value = sample_profile_data
                mock_client_class.return_value = mock_client
                
                # Mock analyzer to return the raw data in analysis
                mock_analyzer = AsyncMock()
                mock_analyzer.analyze_profile.return_value = {
                    "profile_summary": {"full_name": "Jane Smith"},
                    "professional_info": {},
                    "experience": {},
                    "education": {},
                    "ai_insights": {},
                    "raw_data": sample_profile_data
                }
                mock_analyzer_class.return_value = mock_analyzer
                
                result = await analyze_linkedin_profile(test_url)
                
                # Verify data consistency
                assert result["raw_data"] == sample_profile_data
                assert result["analysis"]["raw_data"] == sample_profile_data
                
                # Verify the profile name flows through
                assert result["analysis"]["profile_summary"]["full_name"] == "Jane Smith"
                assert result["raw_data"]["fullName"] == "Jane Smith"


class TestWorkflowErrorScenarios:
    """Test workflow behavior in various error scenarios."""
    
    @pytest.mark.asyncio
    async def test_workflow_network_timeout(self):
        """Test workflow behavior with network timeout."""
        test_url = "https://linkedin.com/in/johndoe"
        
        with patch('domains.intelligence_collection.linkedin.analyzer.ScrapingDogClient') as mock_client_class:
            # Mock client to simulate timeout
            mock_client = AsyncMock()
            mock_client.scrape_profile.side_effect = Exception("Request timeout")
            mock_client_class.return_value = mock_client
            
            result = await analyze_linkedin_profile(test_url)
            
            assert result["status"] == "error"
            assert "Request timeout" in result["error"]
    
    @pytest.mark.asyncio
    async def test_workflow_rate_limiting(self):
        """Test workflow behavior with rate limiting."""
        test_url = "https://linkedin.com/in/johndoe"
        
        with patch('domains.intelligence_collection.linkedin.analyzer.ScrapingDogClient') as mock_client_class:
            # Mock client to simulate rate limiting
            mock_client = AsyncMock()
            mock_client.scrape_profile.side_effect = Exception("Rate limit exceeded")
            mock_client_class.return_value = mock_client
            
            result = await analyze_linkedin_profile(test_url)
            
            assert result["status"] == "error"
            assert "Rate limit exceeded" in result["error"]
    
    @pytest.mark.asyncio
    async def test_workflow_malformed_data(self, sample_profile_data: Dict[str, Any]):
        """Test workflow behavior with malformed profile data."""
        test_url = "https://linkedin.com/in/johndoe"
        
        # Create malformed data
        malformed_data = sample_profile_data.copy()
        malformed_data["experience"] = "not_a_list"  # Should cause analysis error
        
        with patch('domains.intelligence_collection.linkedin.analyzer.ScrapingDogClient') as mock_client_class:
            with patch('domains.intelligence_collection.linkedin.analyzer.LinkedInProfileAnalyzer') as mock_analyzer_class:
                # Mock client returns malformed data
                mock_client = AsyncMock()
                mock_client.scrape_profile.return_value = malformed_data
                mock_client_class.return_value = mock_client
                
                # Mock analyzer to handle the error
                mock_analyzer = AsyncMock()
                mock_analyzer.analyze_profile.return_value = {
                    "error": "Profile analysis failed: 'str' object has no attribute 'get'"
                }
                mock_analyzer_class.return_value = mock_analyzer
                
                result = await analyze_linkedin_profile(test_url)
                
                assert result["status"] == "error"
                assert "Profile analysis failed" in result["error"]


class TestWorkflowPerformance:
    """Test workflow performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_workflow_response_time(self, sample_profile_data: Dict[str, Any]):
        """Test that workflow completes within reasonable time."""
        import time
        
        test_url = "https://linkedin.com/in/janesmith"
        
        with patch('domains.intelligence_collection.linkedin.analyzer.ScrapingDogClient') as mock_client_class:
            with patch('domains.intelligence_collection.linkedin.analyzer.LinkedInProfileAnalyzer') as mock_analyzer_class:
                # Mock fast responses
                mock_client = AsyncMock()
                mock_client.scrape_profile.return_value = sample_profile_data
                mock_client_class.return_value = mock_client
                
                mock_analyzer = AsyncMock()
                mock_analyzer.analyze_profile.return_value = {
                    "profile_summary": {"full_name": "Jane Smith"},
                    "professional_info": {},
                    "experience": {},
                    "education": {},
                    "ai_insights": {}
                }
                mock_analyzer_class.return_value = mock_analyzer
                
                start_time = time.time()
                result = await analyze_linkedin_profile(test_url)
                end_time = time.time()
                
                execution_time = end_time - start_time
                
                # Should complete within 1 second (with mocks)
                assert execution_time < 1.0
                assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_workflow_memory_usage(self, sample_profile_data: Dict[str, Any]):
        """Test that workflow doesn't consume excessive memory."""
        import sys
        
        test_url = "https://linkedin.com/in/janesmith"
        
        with patch('domains.intelligence_collection.linkedin.analyzer.ScrapingDogClient') as mock_client_class:
            with patch('domains.intelligence_collection.linkedin.analyzer.LinkedInProfileAnalyzer') as mock_analyzer_class:
                # Mock responses
                mock_client = AsyncMock()
                mock_client.scrape_profile.return_value = sample_profile_data
                mock_client_class.return_value = mock_client
                
                mock_analyzer = AsyncMock()
                mock_analyzer.analyze_profile.return_value = {
                    "profile_summary": {"full_name": "Jane Smith"},
                    "professional_info": {},
                    "experience": {},
                    "education": {},
                    "ai_insights": {}
                }
                mock_analyzer_class.return_value = mock_analyzer
                
                # Execute workflow
                result = await analyze_linkedin_profile(test_url)
                
                # Verify result is reasonable size
                result_size = sys.getsizeof(str(result))
                assert result_size < 10000  # Should be less than 10KB
                
                assert result["status"] == "success" 