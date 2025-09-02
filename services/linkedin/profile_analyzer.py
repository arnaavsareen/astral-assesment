# ==============================================================================
# profile_analyzer.py — LinkedIn profile data processing and analysis
# ==============================================================================
# Purpose: Process and analyze LinkedIn profile data for business intelligence insights
# Sections: Imports, Profile Data Models, Analysis Functions, Intelligence Scoring
# ==============================================================================

# Standard Library --------------------------------------------------------------
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)


class LinkedInProfileAnalyzer:
    """Analyze and structure LinkedIn profile data from ScrapingDog API."""
    
    def analyze_profile(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw ScrapingDog data into structured analysis."""
        try:
            # Handle case where API returns array with single profile
            if isinstance(raw_data, list) and len(raw_data) > 0:
                profile_data = raw_data[0]
            else:
                profile_data = raw_data
            
            return {
                "profile_summary": self._extract_profile_summary(profile_data),
                "professional_info": self._extract_professional_info(profile_data),
                "experience": self._extract_experience(profile_data),
                "education": self._extract_education(profile_data),
                "content_analysis": self._extract_content_analysis(profile_data),
                "network_insights": self._extract_network_insights(profile_data),
                "business_intelligence": self._extract_business_intelligence(profile_data),
                "raw_data": profile_data  # Include raw data for reference
            }
            
        except Exception as e:
            logger.error("Failed to analyze LinkedIn profile data", extra={"error": str(e)})
            return {
                "error": f"Profile analysis failed: {str(e)}",
                "raw_data": raw_data
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
            "industries": self._extract_industries(experience),
            "skills_mentioned": self._extract_skills_from_text(data.get("about", "")),
            "certifications": data.get("certification", []),
            "volunteering": data.get("volunteering", [])
        }
    
    def _extract_experience(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract detailed work experience information."""
        experience = data.get("experience", [])
        
        return {
            "total_positions": len(experience),
            "positions": experience,
            "career_progression": self._analyze_career_progression(experience),
            "longest_position": self._find_longest_position(experience),
            "recent_companies": self._get_recent_companies(experience, limit=5),
            "seniority_level": self._determine_seniority_level(experience)
        }
    
    def _extract_education(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract education information."""
        education = data.get("education", [])
        
        return {
            "total_degrees": len(education),
            "degrees": education,
            "highest_degree": self._find_highest_degree(education),
            "universities": [edu.get("school", "") for edu in education if edu.get("school")],
            "fields_of_study": [edu.get("field_of_study", "") for edu in education if edu.get("field_of_study")]
        }
    
    def _extract_content_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract content and activity analysis."""
        articles = data.get("articles", [])
        activities = data.get("activities", [])
        
        return {
            "articles": {
                "total_articles": len(articles),
                "recent_articles": articles[:5],  # Last 5 articles
                "article_topics": self._extract_article_topics(articles)
            },
            "activities": {
                "total_activities": len(activities),
                "recent_activities": activities[:10],  # Last 10 activities
                "activity_types": self._categorize_activities(activities)
            },
            "content_themes": self._extract_content_themes(articles, activities),
            "engagement_patterns": self._analyze_engagement_patterns(activities)
        }
    
    def _extract_network_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract network and connection insights."""
        people_also_viewed = data.get("people_also_viewed", [])
        similar_profiles = data.get("similar_profiles", [])
        
        return {
            "network_size": {
                "followers": self._parse_count(data.get("followers", "")),
                "connections": self._parse_count(data.get("connections", ""))
            },
            "people_also_viewed": {
                "total": len(people_also_viewed),
                "profiles": people_also_viewed[:10]  # Top 10
            },
            "similar_profiles": {
                "total": len(similar_profiles),
                "profiles": similar_profiles[:10]  # Top 10
            },
            "network_quality": self._assess_network_quality(people_also_viewed, similar_profiles),
            "influence_indicators": self._calculate_influence_indicators(data)
        }
    
    def _extract_business_intelligence(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract business intelligence insights."""
        experience = data.get("experience", [])
        education = data.get("education", [])
        articles = data.get("articles", [])
        
        return {
            "professional_trajectory": self._analyze_professional_trajectory(experience),
            "industry_expertise": self._determine_industry_expertise(experience, articles),
            "thought_leadership": self._assess_thought_leadership(articles, data.get("about", "")),
            "company_affiliations": self._extract_company_affiliations(experience),
            "geographic_presence": self._analyze_geographic_presence(experience, data.get("location", "")),
            "professional_network": self._analyze_professional_network(data),
            "career_milestones": self._identify_career_milestones(experience),
            "business_opportunities": self._identify_business_opportunities(data)
        }
    
    # Helper methods for data extraction and analysis
    
    def _calculate_total_experience(self, experience: List[Dict[str, Any]]) -> int:
        """Calculate total years of experience."""
        total_years = 0
        for exp in experience:
            duration = exp.get("duration", "")
            if duration and "year" in duration.lower():
                # Extract years from duration string
                try:
                    years = int(''.join(filter(str.isdigit, duration)))
                    total_years += years
                except ValueError:
                    continue
        return total_years
    
    def _extract_companies(self, experience: List[Dict[str, Any]]) -> List[str]:
        """Extract unique company names from experience."""
        companies = []
        for exp in experience:
            company = exp.get("company_name", "")
            if company and company not in companies:
                companies.append(company)
        return companies
    
    def _extract_industries(self, experience: List[Dict[str, Any]]) -> List[str]:
        """Extract industries from experience (placeholder for future enhancement)."""
        # This would require additional data or AI analysis
        return []
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills mentioned in text (basic implementation)."""
        # This is a basic implementation - could be enhanced with NLP
        common_skills = [
            "python", "javascript", "java", "react", "node.js", "aws", "docker",
            "kubernetes", "machine learning", "ai", "data science", "sql",
            "project management", "leadership", "strategy", "marketing", "sales"
        ]
        
        found_skills = []
        text_lower = text.lower()
        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _analyze_career_progression(self, experience: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze career progression patterns."""
        if not experience:
            return {"pattern": "no_data", "progression": "unknown"}
        
        # Basic progression analysis
        positions = [exp.get("position", "").lower() for exp in experience]
        
        # Check for common progression patterns
        if any("senior" in pos for pos in positions):
            progression = "senior_level"
        elif any("manager" in pos or "director" in pos for pos in positions):
            progression = "management_level"
        elif any("founder" in pos or "ceo" in pos or "cto" in pos for pos in positions):
            progression = "executive_level"
        else:
            progression = "entry_mid_level"
        
        return {
            "pattern": "analyzed",
            "progression": progression,
            "total_positions": len(positions)
        }
    
    def _find_longest_position(self, experience: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the longest-held position."""
        if not experience:
            return None
        
        # This is a simplified implementation
        # In a real scenario, you'd parse dates and calculate actual durations
        return experience[0]  # Return first position as placeholder
    
    def _get_recent_companies(self, experience: List[Dict[str, Any]], limit: int = 5) -> List[str]:
        """Get most recent companies worked at."""
        companies = []
        for exp in experience[:limit]:
            company = exp.get("company_name", "")
            if company and company not in companies:
                companies.append(company)
        return companies
    
    def _determine_seniority_level(self, experience: List[Dict[str, Any]]) -> str:
        """Determine seniority level based on experience."""
        if not experience:
            return "unknown"
        
        positions = [exp.get("position", "").lower() for exp in experience]
        
        if any("ceo" in pos or "founder" in pos or "president" in pos for pos in positions):
            return "executive"
        elif any("director" in pos or "vp" in pos for pos in positions):
            return "senior_management"
        elif any("manager" in pos or "lead" in pos for pos in positions):
            return "management"
        elif any("senior" in pos for pos in positions):
            return "senior"
        else:
            return "mid_level"
    
    def _find_highest_degree(self, education: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the highest degree attained."""
        if not education:
            return None
        
        # Simple implementation - return first degree
        # In reality, you'd rank degrees by level (PhD > Masters > Bachelors)
        return education[0]
    
    def _extract_article_topics(self, articles: List[Dict[str, Any]]) -> List[str]:
        """Extract topics from articles."""
        topics = []
        for article in articles:
            title = article.get("title", "")
            if title:
                # Basic topic extraction - could be enhanced with NLP
                topics.append(title[:50] + "..." if len(title) > 50 else title)
        return topics[:5]  # Return top 5 topics
    
    def _categorize_activities(self, activities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize activities by type."""
        categories = {"shared": 0, "liked": 0, "commented": 0, "other": 0}
        
        for activity in activities:
            activity_text = activity.get("activity", "").lower()
            if "shared" in activity_text:
                categories["shared"] += 1
            elif "liked" in activity_text:
                categories["liked"] += 1
            elif "commented" in activity_text:
                categories["commented"] += 1
            else:
                categories["other"] += 1
        
        return categories
    
    def _extract_content_themes(self, articles: List[Dict[str, Any]], activities: List[Dict[str, Any]]) -> List[str]:
        """Extract content themes from articles and activities."""
        # Basic implementation - could be enhanced with NLP
        themes = []
        
        # Extract themes from article titles
        for article in articles:
            title = article.get("title", "").lower()
            if "ai" in title or "artificial intelligence" in title:
                themes.append("Artificial Intelligence")
            elif "leadership" in title:
                themes.append("Leadership")
            elif "technology" in title:
                themes.append("Technology")
        
        return list(set(themes))  # Remove duplicates
    
    def _analyze_engagement_patterns(self, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze engagement patterns."""
        if not activities:
            return {"engagement_level": "low", "activity_frequency": "unknown"}
        
        # Basic engagement analysis
        total_activities = len(activities)
        
        if total_activities > 50:
            engagement_level = "high"
        elif total_activities > 20:
            engagement_level = "medium"
        else:
            engagement_level = "low"
        
        return {
            "engagement_level": engagement_level,
            "activity_frequency": "analyzed",
            "total_activities": total_activities
        }
    
    def _parse_count(self, count_str: str) -> int:
        """Parse follower/connection count string to integer."""
        if not count_str:
            return 0
        
        # Remove non-numeric characters and parse
        import re
        numbers = re.findall(r'\d+', count_str.replace(',', ''))
        if numbers:
            return int(numbers[0])
        return 0
    
    def _assess_network_quality(self, people_also_viewed: List[Dict[str, Any]], similar_profiles: List[Dict[str, Any]]) -> str:
        """Assess the quality of the professional network."""
        total_connections = len(people_also_viewed) + len(similar_profiles)
        
        if total_connections > 20:
            return "high_quality"
        elif total_connections > 10:
            return "medium_quality"
        else:
            return "low_quality"
    
    def _calculate_influence_indicators(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate influence indicators."""
        followers = self._parse_count(data.get("followers", ""))
        articles = len(data.get("articles", []))
        
        influence_score = 0
        if followers > 10000:
            influence_score += 3
        elif followers > 1000:
            influence_score += 2
        elif followers > 100:
            influence_score += 1
        
        if articles > 10:
            influence_score += 2
        elif articles > 5:
            influence_score += 1
        
        return {
            "influence_score": influence_score,
            "follower_count": followers,
            "article_count": articles,
            "influence_level": "high" if influence_score >= 4 else "medium" if influence_score >= 2 else "low"
        }
    
    def _analyze_professional_trajectory(self, experience: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze professional trajectory and career path."""
        if not experience:
            return {"trajectory": "unknown", "career_path": "no_data"}
        
        # Basic trajectory analysis
        positions = [exp.get("position", "").lower() for exp in experience]
        
        if any("founder" in pos or "ceo" in pos for pos in positions):
            trajectory = "entrepreneurial"
        elif any("director" in pos or "vp" in pos for pos in positions):
            trajectory = "executive"
        elif any("manager" in pos for pos in positions):
            trajectory = "management"
        else:
            trajectory = "individual_contributor"
        
        return {
            "trajectory": trajectory,
            "career_path": "analyzed",
            "position_count": len(positions)
        }
    
    def _determine_industry_expertise(self, experience: List[Dict[str, Any]], articles: List[Dict[str, Any]]) -> List[str]:
        """Determine industry expertise areas."""
        # Basic implementation - could be enhanced with industry classification
        expertise_areas = []
        
        # Extract from experience
        for exp in experience:
            position = exp.get("position", "").lower()
            if "engineer" in position or "developer" in position:
                expertise_areas.append("Technology")
            elif "manager" in position or "director" in position:
                expertise_areas.append("Management")
            elif "founder" in position or "ceo" in position:
                expertise_areas.append("Entrepreneurship")
        
        return list(set(expertise_areas))  # Remove duplicates
    
    def _assess_thought_leadership(self, articles: List[Dict[str, Any]], about: str) -> Dict[str, Any]:
        """Assess thought leadership indicators."""
        article_count = len(articles)
        about_length = len(about)
        
        thought_leadership_score = 0
        if article_count > 10:
            thought_leadership_score += 3
        elif article_count > 5:
            thought_leadership_score += 2
        elif article_count > 0:
            thought_leadership_score += 1
        
        if about_length > 500:
            thought_leadership_score += 1
        
        return {
            "thought_leadership_score": thought_leadership_score,
            "article_count": article_count,
            "about_length": about_length,
            "leadership_level": "high" if thought_leadership_score >= 3 else "medium" if thought_leadership_score >= 1 else "low"
        }
    
    def _extract_company_affiliations(self, experience: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract company affiliations with details."""
        affiliations = []
        for exp in experience:
            affiliation = {
                "company": exp.get("company_name", ""),
                "position": exp.get("position", ""),
                "duration": exp.get("duration", ""),
                "current": exp.get("ends_at") == "Present" or not exp.get("ends_at")
            }
            affiliations.append(affiliation)
        return affiliations
    
    def _analyze_geographic_presence(self, experience: List[Dict[str, Any]], location: str) -> Dict[str, Any]:
        """Analyze geographic presence and mobility."""
        locations = []
        if location:
            locations.append(location)
        
        for exp in experience:
            exp_location = exp.get("location", "")
            if exp_location and exp_location not in locations:
                locations.append(exp_location)
        
        return {
            "current_location": location,
            "all_locations": locations,
            "location_count": len(locations),
            "mobility": "high" if len(locations) > 3 else "medium" if len(locations) > 1 else "low"
        }
    
    def _analyze_professional_network(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze professional network characteristics."""
        people_also_viewed = data.get("people_also_viewed", [])
        similar_profiles = data.get("similar_profiles", [])
        
        network_size = len(people_also_viewed) + len(similar_profiles)
        
        return {
            "network_size": network_size,
            "network_diversity": "high" if network_size > 15 else "medium" if network_size > 5 else "low",
            "connection_quality": "analyzed"
        }
    
    def _identify_career_milestones(self, experience: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify key career milestones."""
        milestones = []
        
        for exp in experience:
            position = exp.get("position", "").lower()
            if any(keyword in position for keyword in ["founder", "ceo", "cto", "president"]):
                milestones.append({
                    "type": "executive_position",
                    "position": exp.get("position", ""),
                    "company": exp.get("company_name", ""),
                    "year": exp.get("starts_at", "")
                })
            elif any(keyword in position for keyword in ["director", "vp", "head"]):
                milestones.append({
                    "type": "senior_management",
                    "position": exp.get("position", ""),
                    "company": exp.get("company_name", ""),
                    "year": exp.get("starts_at", "")
                })
        
        return milestones
    
    def _identify_business_opportunities(self, data: Dict[str, Any]) -> List[str]:
        """Identify potential business opportunities."""
        opportunities = []
        
        # Analyze based on various factors
        experience = data.get("experience", [])
        articles = data.get("articles", [])
        followers = self._parse_count(data.get("followers", ""))
        
        if any("founder" in exp.get("position", "").lower() for exp in experience):
            opportunities.append("Entrepreneurial collaboration")
        
        if len(articles) > 5:
            opportunities.append("Content partnership")
        
        if followers > 1000:
            opportunities.append("Influencer marketing")
        
        if any("manager" in exp.get("position", "").lower() for exp in experience):
            opportunities.append("Leadership consulting")
        
        return opportunities 