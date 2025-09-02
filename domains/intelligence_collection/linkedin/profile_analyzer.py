# ==============================================================================
# profile_analyzer.py — LinkedIn profile data processing and analysis
# ==============================================================================
# Purpose: Process and analyze LinkedIn profile data for business intelligence insights
# Sections: Imports, Profile Data Models, Analysis Functions, AI-Powered Intelligence
# ==============================================================================

# Standard Library --------------------------------------------------------------
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Third Party -------------------------------------------------------------------
from core.clients.openai import AIClient

# Configure logging
logger = logging.getLogger(__name__)


class LinkedInProfileAnalyzer:
    """Analyze and structure LinkedIn profile data using AI for intelligent insights."""
    
    def __init__(self):
        """Initialize the analyzer with AI client."""
        self.ai_client = AIClient()
    
    async def analyze_profile(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw ScrapingDog data into structured analysis using AI."""
        try:
            # Handle case where API returns array with single profile
            if isinstance(raw_data, list) and len(raw_data) > 0:
                profile_data = raw_data[0]
            else:
                profile_data = raw_data
            
            # Use AI to analyze the profile intelligently
            ai_analysis = await self._analyze_with_ai(profile_data)
            
            return {
                "profile_summary": self._extract_profile_summary(profile_data),
                "professional_info": self._extract_professional_info(profile_data),
                "experience": self._extract_experience(profile_data),
                "education": self._extract_education(profile_data),
                "ai_insights": ai_analysis,
                "raw_data": profile_data  # Include raw data for reference
            }
            
        except Exception as e:
            logger.error("Failed to analyze LinkedIn profile data", extra={"error": str(e)})
            return {
                "error": f"Profile analysis failed: {str(e)}",
                "raw_data": raw_data
            }
    
    async def _analyze_with_ai(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze profile data and extract intelligent insights."""
        try:
            # Check if AI client has API key
            if not self.ai_client._has_api_key():
                logger.info("No OpenAI API key available, using fallback analysis")
                return self._fallback_analysis(profile_data)
            
            # Prepare profile data for AI analysis
            profile_text = self._prepare_profile_for_ai(profile_data)
            
            # AI analysis prompt
            analysis_prompt = f"""
            Analyze this LinkedIn profile and provide business intelligence insights in JSON format:
            
            {profile_text}
            
            Return a JSON object with these fields:
            - skills_analysis: List of technical and soft skills with confidence scores
            - industry_expertise: Primary and secondary industries with reasoning
            - career_trajectory: Analysis of career progression and stability
            - business_network: Assessment of network strength and influence
            - thought_leadership: Evaluation of content quality and engagement
            - professional_gaps: Areas for potential development or improvement
            - market_positioning: How this person positions themselves professionally
            - competitive_advantages: Unique strengths and differentiators
            
            Focus on actionable business insights, not just descriptive information.
            """
            
            # Get AI analysis
            ai_response = await self.ai_client.analyze_text(analysis_prompt)
            
            # Parse and structure the AI response
            return self._parse_ai_analysis(ai_response)
            
        except Exception as e:
            logger.warning(f"AI analysis failed, falling back to basic analysis: {e}")
            return self._fallback_analysis(profile_data)
    
    def _prepare_profile_for_ai(self, profile_data: Dict[str, Any]) -> str:
        """Prepare profile data in a format suitable for AI analysis."""
        sections = []
        
        # Basic profile info
        if profile_data.get("fullName"):
            sections.append(f"Name: {profile_data['fullName']}")
        if profile_data.get("headline"):
            sections.append(f"Headline: {profile_data['headline']}")
        if profile_data.get("about"):
            sections.append(f"About: {profile_data['about']}")
        
        # Experience
        experience = profile_data.get("experience", [])
        if experience:
            sections.append("Work Experience:")
            for exp in experience:
                company = exp.get("company_name", "Unknown Company")
                position = exp.get("position", "Unknown Position")
                duration = f"{exp.get('starts_at', '')} - {exp.get('ends_at', 'Present')}"
                sections.append(f"  - {position} at {company} ({duration})")
        
        # Education
        education = profile_data.get("education", [])
        if education:
            sections.append("Education:")
            for edu in education:
                school = edu.get("school", "Unknown School")
                degree = edu.get("degree", "Unknown Degree")
                field = edu.get("field_of_study", "")
                sections.append(f"  - {degree} in {field} from {school}")
        
        # Content and activities
        if profile_data.get("articles"):
            sections.append(f"Articles: {len(profile_data['articles'])} published")
        if profile_data.get("activities"):
            sections.append(f"Activities: {len(profile_data['activities'])} recent activities")
        
        return "\n".join(sections)
    
    def _parse_ai_analysis(self, ai_response: str) -> Dict[str, Any]:
        """Parse and structure the AI response into usable insights."""
        try:
            # Try to extract JSON from the response
            import json
            import re
            
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return parsed
            else:
                # If no JSON found, return structured text
                return {
                    "raw_analysis": ai_response,
                    "parsing_status": "text_only"
                }
                
        except Exception as e:
            logger.warning(f"Failed to parse AI response as JSON: {e}")
            return {
                "raw_analysis": ai_response,
                "parsing_status": "parse_failed",
                "error": str(e)
            }
    
    def _fallback_analysis(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when AI fails - basic insights only."""
        experience = profile_data.get("experience", [])
        
        return {
            "skills_analysis": {
                "detected_skills": [],
                "confidence": "low",
                "method": "fallback"
            },
            "industry_expertise": {
                "primary_industry": "unknown",
                "reasoning": "AI analysis unavailable"
            },
            "career_trajectory": {
                "progression": "unknown",
                "stability": "unknown"
            },
            "business_network": {
                "strength": "unknown",
                "influence": "unknown"
            },
            "thought_leadership": {
                "content_quality": "unknown",
                "engagement_level": "unknown"
            },
            "analysis_quality": "fallback_basic"
        }
    
    def _extract_profile_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract basic profile summary information."""
        return {
            "full_name": data.get("fullName", ""),
            "first_name": data.get("first_name", ""),
            "last_name": data.get("last_name", ""),
            "headline": data.get("headline", ""),
            "location": data.get("location", ""),
            "profile_id": data.get("public_identifier", ""),
            "followers": data.get("followers", ""),
            "connections": data.get("connections", ""),
            "about": data.get("about", ""),
            "profile_photo": data.get("profile_photo", ""),
            "background_image": data.get("background_cover_image_url", "")
        }
    
    def _extract_professional_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract professional information and current position."""
        experience = data.get("experience", [])
        current_position = None
        
        if experience:
            # Find current position (most recent with no end date or "Present")
            for exp in experience:
                if not exp.get("ends_at") or exp.get("ends_at") == "Present":
                    current_position = exp
                    break
            
            # If no current position found, use the first one
            if not current_position and experience:
                current_position = experience[0]
        
        return {
            "current_position": current_position,
            "total_experience_years": self._calculate_total_experience(experience),
            "companies_worked_at": self._extract_companies(experience),
            "certifications": data.get("certification", []),
            "volunteering": data.get("volunteering", [])
        }
    
    def _extract_experience(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract detailed work experience information."""
        experience = data.get("experience", [])
        
        return {
            "total_positions": len(experience),
            "positions": experience,
            "recent_companies": self._get_recent_companies(experience, limit=5)
        }
    
    def _extract_education(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract education information."""
        education = data.get("education", [])
        
        return {
            "total_degrees": len(education),
            "degrees": education,
            "universities": [edu.get("school", "") for edu in education if edu.get("school")],
            "fields_of_study": [edu.get("field_of_study", "") for edu in education if edu.get("field_of_study")]
        }
    
    def _calculate_total_experience(self, experience: List[Dict[str, Any]]) -> int:
        """Calculate total years of experience."""
        if not experience:
            return 0
        
        total_years = 0
        for exp in experience:
            start_year = self._extract_year(exp.get("starts_at", ""))
            end_year = self._extract_year(exp.get("ends_at", ""))
            
            if start_year and end_year:
                total_years += end_year - start_year
            elif start_year:
                # Current position
                current_year = datetime.now().year
                total_years += current_year - start_year
        
        return total_years
    
    def _extract_year(self, date_str: str) -> Optional[int]:
        """Extract year from date string."""
        if not date_str or date_str == "Present":
            return None
        
        # Try to extract year from various formats
        import re
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            return int(year_match.group())
        
        return None
    
    def _extract_companies(self, experience: List[Dict[str, Any]]) -> List[str]:
        """Extract unique company names from experience."""
        companies = set()
        for exp in experience:
            company = exp.get("company_name", "")
            if company:
                companies.add(company)
        return list(companies)
    
    def _get_recent_companies(self, experience: List[Dict[str, Any]], limit: int = 5) -> List[str]:
        """Get most recent companies worked at."""
        companies = []
        for exp in experience[:limit]:
            company = exp.get("company_name", "")
            if company:
                companies.append(company)
        return companies 