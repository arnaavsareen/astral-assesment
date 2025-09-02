# ==============================================================================
# test_profile_analyzer.py — LinkedIn profile analysis domain tests
# ==============================================================================
# Purpose: Test AI-powered LinkedIn profile analysis and intelligence extraction
# Sections: Imports, Test Data, Analysis Tests, AI Integration Tests, Fallback Tests
# ==============================================================================

# Standard Library --------------------------------------------------------------
import pytest
from unittest.mock import AsyncMock, patch
from typing import Dict, Any, List

# Third Party -------------------------------------------------------------------
# (none)

# Core (App-wide) ---------------------------------------------------------------
from domains.intelligence_collection.linkedin.profile_analyzer import LinkedInProfileAnalyzer


@pytest.fixture
def sample_profile_data() -> Dict[str, Any]:
    """Sample LinkedIn profile data for testing."""
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
        "profile_photo": "https://example.com/photo.jpg",
        "background_cover_image_url": "https://example.com/cover.jpg",
        "experience": [
            {
                "company_name": "Tech Company",
                "position": "Software Engineer",
                "starts_at": "2020-01",
                "ends_at": "Present",
                "industry": "Technology"
            }
        ],
        "education": [
            {
                "school": "University of California",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science"
            }
        ],
        "articles": [
            {
                "title": "The Future of AI in Software Development",
                "published_date": "Mar 15, 2023"
            }
        ],
        "activities": [
            {
                "activity": "Shared by John Doe",
                "title": "The Future of AI in Software Development",
                "published_date": "Mar 15, 2023"
            }
        ],
        "certification": [],
        "volunteering": []
    }


@pytest.fixture
def analyzer() -> LinkedInProfileAnalyzer:
    """Create a LinkedIn profile analyzer instance."""
    return LinkedInProfileAnalyzer()


class TestLinkedInProfileAnalyzer:
    """Test LinkedIn profile analysis functionality - domain logic only."""
    
    @pytest.mark.asyncio
    async def test_analyze_profile_success(self, analyzer: LinkedInProfileAnalyzer, sample_profile_data: Dict[str, Any]):
        """Test successful profile analysis with AI insights."""
        result = await analyzer.analyze_profile(sample_profile_data)
        
        # Check that all analysis sections are present
        assert "profile_summary" in result
        assert "professional_info" in result
        assert "experience" in result
        assert "education" in result
        assert "ai_insights" in result
        assert "raw_data" in result
        
        # Check profile summary
        summary = result["profile_summary"]
        assert summary["full_name"] == "John Doe"
        assert summary["headline"] == "Software Engineer at Tech Company"
        assert summary["location"] == "San Francisco, CA"
        assert summary["profile_id"] == "johndoe"
        assert summary["followers"] == "1,234 followers"
        assert summary["connections"] == "500+ connections"
        
        # Check professional info
        prof_info = result["professional_info"]
        assert prof_info["current_position"]["position"] == "Software Engineer"
        assert prof_info["current_position"]["company_name"] == "Tech Company"
        assert prof_info["companies_worked_at"] == ["Tech Company"]
        assert prof_info["total_experience_years"] >= 0
        
        # Check experience
        experience = result["experience"]
        assert experience["total_positions"] == 1
        assert experience["recent_companies"] == ["Tech Company"]
        
        # Check education
        education = result["education"]
        assert education["total_degrees"] == 1
        assert education["universities"] == ["University of California"]
        assert education["fields_of_study"] == ["Computer Science"]
    
    @pytest.mark.asyncio
    async def test_analyze_profile_with_list_data(self, analyzer: LinkedInProfileAnalyzer, sample_profile_data: Dict[str, Any]):
        """Test profile analysis with list data (API response format)."""
        list_data = [sample_profile_data]
        result = await analyzer.analyze_profile(list_data)
        
        # Should work the same as single profile data
        assert result["profile_summary"]["full_name"] == "John Doe"
        assert result["professional_info"]["current_position"]["position"] == "Software Engineer"
    
    @pytest.mark.asyncio
    async def test_analyze_profile_empty_data(self, analyzer: LinkedInProfileAnalyzer):
        """Test profile analysis with empty data."""
        result = await analyzer.analyze_profile({})
        
        # Should handle empty data gracefully
        assert "profile_summary" in result
        assert result["profile_summary"]["full_name"] == ""
        assert result["profile_summary"]["headline"] == ""
        assert result["profile_summary"]["location"] == ""
        
        # AI insights should still be present
        assert "ai_insights" in result
        # Check that AI analysis is present (even with empty data, AI can provide insights)
        assert "skills_analysis" in result["ai_insights"]
        # The AI provides structured skills analysis
        skills = result["ai_insights"]["skills_analysis"]
        assert "technical_skills" in skills or "soft_skills" in skills
    
    @pytest.mark.asyncio
    async def test_analyze_profile_error_handling(self, analyzer: LinkedInProfileAnalyzer):
        """Test profile analysis error handling."""
        # Pass invalid data that would cause an error
        invalid_data = {"experience": "not_a_list"}
        
        result = await analyzer.analyze_profile(invalid_data)
        
        # Should return error information
        assert "error" in result
        assert "Profile analysis failed" in result["error"]
    
    def test_extract_profile_summary(self, analyzer: LinkedInProfileAnalyzer, sample_profile_data: Dict[str, Any]):
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
        assert summary["about"] == "Experienced software engineer with expertise in Python and AI."
        assert summary["profile_photo"] == "https://example.com/photo.jpg"
        assert summary["background_image"] == "https://example.com/cover.jpg"
    
    def test_extract_professional_info(self, analyzer: LinkedInProfileAnalyzer, sample_profile_data: Dict[str, Any]):
        """Test professional information extraction."""
        prof_info = analyzer._extract_professional_info(sample_profile_data)
        
        assert prof_info["current_position"]["position"] == "Software Engineer"
        assert prof_info["current_position"]["company_name"] == "Tech Company"
        assert prof_info["companies_worked_at"] == ["Tech Company"]
        assert prof_info["total_experience_years"] >= 0
        assert prof_info["certifications"] == []
        assert prof_info["volunteering"] == []
    
    def test_extract_experience(self, analyzer: LinkedInProfileAnalyzer, sample_profile_data: Dict[str, Any]):
        """Test experience extraction."""
        experience = analyzer._extract_experience(sample_profile_data)
        
        assert experience["total_positions"] == 1
        assert experience["recent_companies"] == ["Tech Company"]
        assert len(experience["positions"]) == 1
        assert experience["positions"][0]["position"] == "Software Engineer"
    
    def test_extract_education(self, analyzer: LinkedInProfileAnalyzer, sample_profile_data: Dict[str, Any]):
        """Test education extraction."""
        education = analyzer._extract_education(sample_profile_data)
        
        assert education["total_degrees"] == 1
        assert education["universities"] == ["University of California"]
        assert education["fields_of_study"] == ["Computer Science"]
        assert len(education["degrees"]) == 1
        assert education["degrees"][0]["degree"] == "Bachelor of Science"
    
    def test_calculate_total_experience(self, analyzer: LinkedInProfileAnalyzer):
        """Test experience calculation logic."""
        # Test with current position
        current_position_exp = [
            {"starts_at": "2020-01", "ends_at": "Present"}
        ]
        years = analyzer._calculate_total_experience(current_position_exp)
        assert years >= 3  # Should be at least 3 years from 2020 to now
        
        # Test with completed positions
        completed_exp = [
            {"starts_at": "2018-01", "ends_at": "2020-01"},
            {"starts_at": "2020-01", "ends_at": "Present"}
        ]
        years = analyzer._calculate_total_experience(completed_exp)
        assert years >= 5  # Should be at least 5 years total
        
        # Test with empty experience
        years = analyzer._calculate_total_experience([])
        assert years == 0
    
    def test_extract_companies(self, analyzer: LinkedInProfileAnalyzer):
        """Test company extraction logic."""
        experience = [
            {"company_name": "Tech Company"},
            {"company_name": "Startup Inc"},
            {"company_name": "Big Corp"}
        ]
        
        companies = analyzer._extract_companies(experience)
        assert "Tech Company" in companies
        assert "Startup Inc" in companies
        assert "Big Corp" in companies
        assert len(companies) == 3
        
        # Test with empty experience
        companies = analyzer._extract_companies([])
        assert companies == []
        
        # Test with missing company names
        experience_with_missing = [
            {"company_name": "Tech Company"},
            {"position": "Engineer"},  # Missing company_name
            {"company_name": ""}  # Empty company_name
        ]
        companies = analyzer._extract_companies(experience_with_missing)
        assert companies == ["Tech Company"]
    
    def test_get_recent_companies(self, analyzer: LinkedInProfileAnalyzer):
        """Test recent companies extraction with limit."""
        experience = [
            {"company_name": "Current Company"},
            {"company_name": "Previous Company"},
            {"company_name": "Old Company"},
            {"company_name": "First Company"}
        ]
        
        # Test default limit (5)
        recent = analyzer._get_recent_companies(experience)
        assert len(recent) == 4
        assert recent[0] == "Current Company"
        
        # Test custom limit
        recent = analyzer._get_recent_companies(experience, limit=2)
        assert len(recent) == 2
        assert recent[0] == "Current Company"
        assert recent[1] == "Previous Company"
        
        # Test with empty experience
        recent = analyzer._get_recent_companies([])
        assert recent == []
    
    def test_extract_year(self, analyzer: LinkedInProfileAnalyzer):
        """Test year extraction from date strings."""
        # Test various date formats
        assert analyzer._extract_year("2020-01") == 2020
        assert analyzer._extract_year("2018-12") == 2018
        assert analyzer._extract_year("2024") == 2024
        assert analyzer._extract_year("Jan 2020") == 2020
        assert analyzer._extract_year("December 2018") == 2018
        
        # Test edge cases
        assert analyzer._extract_year("Present") is None
        assert analyzer._extract_year("") is None
        assert analyzer._extract_year("ongoing") is None
        assert analyzer._extract_year("not-a-date") is None


class TestAIIntegration:
    """Test AI integration functionality."""
    
    @pytest.mark.asyncio
    async def test_ai_analysis_with_api_key(self, analyzer: LinkedInProfileAnalyzer, sample_profile_data: Dict[str, Any]):
        """Test AI analysis when API key is available."""
        with patch.object(analyzer.ai_client, '_has_api_key', return_value=True):
            with patch.object(analyzer.ai_client, 'analyze_text', new_callable=AsyncMock) as mock_ai:
                mock_ai.return_value = '{"skills_analysis": {"detected_skills": ["Python", "AI"]}}'
                
                result = await analyzer.analyze_profile(sample_profile_data)
                
                # Should have AI insights
                assert "ai_insights" in result
                # The AI response gets parsed and merged into ai_insights
                assert "skills_analysis" in result["ai_insights"]
                
                # AI should have been called
                mock_ai.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ai_analysis_without_api_key(self, analyzer: LinkedInProfileAnalyzer, sample_profile_data: Dict[str, Any]):
        """Test fallback analysis when no API key is available."""
        with patch.object(analyzer.ai_client, '_has_api_key', return_value=False):
            result = await analyzer.analyze_profile(sample_profile_data)
            
            # Should use fallback analysis
            assert "ai_insights" in result
            assert result["ai_insights"]["analysis_quality"] == "fallback_basic"
            assert result["ai_insights"]["skills_analysis"]["method"] == "fallback"
    
    @pytest.mark.asyncio
    async def test_ai_analysis_failure_fallback(self, analyzer: LinkedInProfileAnalyzer, sample_profile_data: Dict[str, Any]):
        """Test fallback when AI analysis fails."""
        with patch.object(analyzer.ai_client, '_has_api_key', return_value=True):
            with patch.object(analyzer.ai_client, 'analyze_text', side_effect=Exception("AI service down")):
                result = await analyzer.analyze_profile(sample_profile_data)
                
                # Should fall back to basic analysis
                assert "ai_insights" in result
                assert result["ai_insights"]["analysis_quality"] == "fallback_basic"
    
    def test_prepare_profile_for_ai(self, analyzer: LinkedInProfileAnalyzer, sample_profile_data: Dict[str, Any]):
        """Test profile data preparation for AI analysis."""
        profile_text = analyzer._prepare_profile_for_ai(sample_profile_data)
        
        # Should contain key profile information
        assert "Name: John Doe" in profile_text
        assert "Headline: Software Engineer at Tech Company" in profile_text
        assert "About: Experienced software engineer with expertise in Python and AI." in profile_text
        assert "Work Experience:" in profile_text
        assert "Software Engineer at Tech Company" in profile_text
        assert "Education:" in profile_text
        assert "Bachelor of Science in Computer Science from University of California" in profile_text
        assert "Articles: 1 published" in profile_text
        assert "Activities: 1 recent activities" in profile_text
    
    def test_parse_ai_analysis_valid_json(self, analyzer: LinkedInProfileAnalyzer):
        """Test parsing of valid AI response."""
        valid_response = '{"skills_analysis": {"detected_skills": ["Python"]}}'
        result = analyzer._parse_ai_analysis(valid_response)
        
        assert result["skills_analysis"]["detected_skills"] == ["Python"]
    
    def test_parse_ai_analysis_invalid_json(self, analyzer: LinkedInProfileAnalyzer):
        """Test parsing of invalid AI response."""
        invalid_response = "This is not JSON"
        result = analyzer._parse_ai_analysis(invalid_response)
        
        assert result["parsing_status"] == "text_only"
        assert result["raw_analysis"] == invalid_response
    
    def test_parse_ai_analysis_malformed_json(self, analyzer: LinkedInProfileAnalyzer):
        """Test parsing of malformed JSON response."""
        malformed_response = '{"skills_analysis": {"detected_skills": ["Python"]'  # Missing closing brace
        result = analyzer._parse_ai_analysis(malformed_response)
        
        # The current implementation returns "text_only" for malformed JSON
        assert result["parsing_status"] == "text_only"
        assert "raw_analysis" in result


class TestFallbackAnalysis:
    """Test fallback analysis functionality."""
    
    def test_fallback_analysis_structure(self, analyzer: LinkedInProfileAnalyzer, sample_profile_data: Dict[str, Any]):
        """Test that fallback analysis provides consistent structure."""
        fallback = analyzer._fallback_analysis(sample_profile_data)
        
        # Should have all required fields
        assert "skills_analysis" in fallback
        assert "industry_expertise" in fallback
        assert "career_trajectory" in fallback
        assert "business_network" in fallback
        assert "thought_leadership" in fallback
        assert "analysis_quality" in fallback
        
        # Should indicate fallback status
        assert fallback["analysis_quality"] == "fallback_basic"
        assert fallback["skills_analysis"]["method"] == "fallback"
        assert fallback["skills_analysis"]["confidence"] == "low" 