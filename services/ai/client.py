"""AI service client for intelligent operations using OpenAI."""

import json
import logging
from typing import List, Dict, Any, Optional
import httpx
from core.config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)


class AIClient:
    """
    Singleton AI client for OpenAI operations.
    
    Responsibilities:
    - Score URLs for business intelligence value
    - Handle OpenAI API communication
    - Graceful error handling and fallbacks
    - Structured response parsing
    """
    
    _instance: Optional['AIClient'] = None
    _base_url = "https://api.openai.com/v1/chat/completions"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.api_key = settings.openai_api_key
            self._initialized = True
            
            if not self._has_api_key():
                logger.warning("No OpenAI API key provided - AI features will not function")
            else:
                logger.info("AI client initialized with OpenAI API key")
    
    def _has_api_key(self) -> bool:
        """Check if OpenAI API key is available and not empty."""
        return bool(self.api_key and self.api_key.strip())
    
    async def score_urls_for_business_intelligence(
        self,
        urls: List[str],
        context: str
    ) -> List[Dict[str, Any]]:
        """
        Call OpenAI to intelligently score URLs for business intelligence value.
        
        Args:
            urls: List of URLs to score
            context: Company context for intelligent scoring
            
        Returns:
            List of dictionaries with scoring results:
            {
                "url": "https://...",
                "score": 85,
                "reason": "Company mission and values page",
                "category": "leadership"
            }
            
        Raises:
            ValueError: If no API key is provided
            httpx.HTTPStatusError: If API call fails
        """
        if not self._has_api_key():
            raise ValueError("OpenAI API key required for AI-powered URL scoring")
        
        try:
            # Build the intelligent scoring prompt
            prompt = self._build_scoring_prompt(urls, context)
            
            # Make OpenAI API call
            response = await self._call_openai(prompt)
            
            # Parse and validate the response
            scored_urls = self._parse_ai_response(response, urls)
            
            logger.info(f"AI successfully scored {len(scored_urls)} URLs")
            return scored_urls
            
        except Exception as e:
            logger.error(f"AI scoring failed: {e}")
            raise
    
    def _build_scoring_prompt(self, urls: List[str], context: str) -> str:
        """
        Build the prompt for AI scoring.
        
        Args:
            urls: List of URLs to score
            context: Company context information
            
        Returns:
            Formatted prompt string for OpenAI
        """
        url_list = "\n".join([f"- {url}" for url in urls])
        
        prompt = f"""You are an expert business intelligence analyst. Score these URLs for their business intelligence value.

Company Context: {context}

URLs to analyze:
{url_list}

Instructions:
1. Score each URL from 0-100 for business intelligence value
2. Categorize into: leadership, products, culture, customers, financials, strategy, other
3. Provide one-sentence reasoning
4. Return valid JSON array

Scoring Guidelines:
- 90-100: Company mission, leadership, core strategy
- 80-89: Products/services, case studies, major announcements
- 70-79: Company culture, customer success, industry insights
- 60-69: Blog posts, news, partnerships
- 40-59: General company information
- 20-39: Contact, support, utility pages
- 0-19: Legal, privacy, login pages

Categories:
- leadership: About, team, executives, board
- products: Services, solutions, offerings, features
- culture: Values, mission, workplace, blog posts
- customers: Case studies, testimonials, success stories
- financials: Investors, press releases, earnings
- strategy: Vision, roadmap, partnerships, acquisitions
- other: Miscellaneous business-relevant content

Return ONLY valid JSON in this exact format:
[
  {{
    "url": "https://example.com/about",
    "score": 95,
    "reason": "Company mission and values page",
    "category": "leadership"
  }}
]"""
        
        return prompt
    
    async def _call_openai(self, prompt: str) -> str:
        """
        Make OpenAI API call with proper error handling.
        
        Args:
            prompt: The prompt to send to OpenAI
            
        Returns:
            Raw response text from OpenAI
            
        Raises:
            httpx.HTTPStatusError: If API call fails
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self._base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a business intelligence expert. Always respond with valid JSON."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.1,  # Low temperature for consistent scoring
                        "max_tokens": 2000
                    },
                    timeout=30.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Extract content from OpenAI response
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    logger.debug(f"OpenAI response: {content}")
                    return content
                else:
                    raise ValueError("Invalid OpenAI response format")
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAI API HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
    
    def _parse_ai_response(self, response: str, original_urls: List[str]) -> List[Dict[str, Any]]:
        """
        Parse and validate AI response.
        
        Args:
            response: Raw response from OpenAI
            original_urls: Original URLs to ensure we have results for all
            
        Returns:
            Parsed scoring results
            
        Raises:
            ValueError: If response cannot be parsed
        """
        try:
            # Clean the response and extract JSON
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            cleaned_response = cleaned_response.strip()
            
            # Parse JSON response
            parsed_data = json.loads(cleaned_response)
            
            if not isinstance(parsed_data, list):
                raise ValueError("AI response is not a list")
            
            # Validate and normalize the response
            validated_results = []
            for item in parsed_data:
                if not isinstance(item, dict):
                    continue
                    
                # Ensure required fields
                if "url" not in item or "score" not in item:
                    continue
                
                # Normalize and validate
                validated_item = {
                    "url": str(item["url"]),
                    "score": int(item.get("score", 0)),
                    "reason": str(item.get("reason", "No reason provided")),
                    "category": str(item.get("category", "other"))
                }
                
                # Ensure score is within valid range
                validated_item["score"] = max(0, min(100, validated_item["score"]))
                
                validated_results.append(validated_item)
            
            # Ensure we have results for all original URLs
            if len(validated_results) != len(original_urls):
                logger.warning(f"AI response incomplete: {len(validated_results)}/{len(original_urls)} URLs scored")
                
                # Add missing URLs with default scores
                scored_urls = {item["url"] for item in validated_results}
                for url in original_urls:
                    if url not in scored_urls:
                        validated_results.append({
                            "url": url,
                            "score": 40,  # Default medium score
                            "reason": "AI scoring incomplete - using fallback",
                            "category": "other"
                        })
            
            return validated_results
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            raise ValueError(f"Invalid JSON response from AI: {e}")
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            raise ValueError(f"Response parsing failed: {e}")


# Global singleton instance
ai_client = AIClient() 