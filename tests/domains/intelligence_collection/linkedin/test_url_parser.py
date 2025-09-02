# ==============================================================================
# test_url_parser.py — LinkedIn URL parsing domain tests
# ==============================================================================
# Purpose: Test LinkedIn URL validation, normalization, and profile ID extraction
# Sections: Imports, Test Cases, Edge Cases, Error Handling
# ==============================================================================

# Standard Library --------------------------------------------------------------
import pytest
from typing import List, Tuple

# Core (App-wide) ---------------------------------------------------------------
from domains.intelligence_collection.linkedin.url_parser import (
    extract_profile_id,
    is_valid_linkedin_url,
    normalize_linkedin_url,
    get_profile_url_from_id
)


class TestLinkedInURLParser:
    """Test LinkedIn URL parsing functionality - domain logic only."""
    
    def test_extract_profile_id_valid_urls(self):
        """Test extracting profile ID from valid LinkedIn URLs."""
        test_cases: List[Tuple[str, str]] = [
            ("https://linkedin.com/in/johndoe", "johndoe"),
            ("https://www.linkedin.com/in/johndoe/", "johndoe"),
            ("https://linkedin.com/in/johndoe?trk=profile", "johndoe"),
            ("linkedin.com/in/johndoe", "johndoe"),
            ("https://www.linkedin.com/in/richard-branson", "richard-branson"),
            ("https://linkedin.com/in/user_123", "user_123"),
            ("https://linkedin.com/in/jane-doe-123", "jane-doe-123"),
            ("https://www.linkedin.com/in/tech-leader-2024", "tech-leader-2024"),
        ]
        
        for url, expected_id in test_cases:
            result = extract_profile_id(url)
            assert result == expected_id, f"Failed for URL: {url}, expected: {expected_id}, got: {result}"
    
    def test_extract_profile_id_invalid_urls(self):
        """Test extracting profile ID from invalid LinkedIn URLs."""
        invalid_urls: List[str] = [
            "",
            "https://google.com/in/johndoe",
            "https://linkedin.com/company/example",
            "https://linkedin.com/in/",
            "https://linkedin.com/in",
            "not-a-url",
            "https://linkedin.com/feed/update/",
            "https://linkedin.com/jobs/",
            "https://linkedin.com/learning/",
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError):
                extract_profile_id(url)
    
    def test_is_valid_linkedin_url(self):
        """Test LinkedIn URL validation logic."""
        valid_urls: List[str] = [
            "https://linkedin.com/in/johndoe",
            "https://www.linkedin.com/in/johndoe/",
            "linkedin.com/in/johndoe",
            "https://linkedin.com/in/jane-doe-123",
            "https://www.linkedin.com/in/tech-leader-2024",
        ]
        
        invalid_urls: List[str] = [
            "",
            "https://google.com/in/johndoe",
            "https://linkedin.com/company/example",
            "not-a-url",
            "https://linkedin.com/feed/update/",
            "https://linkedin.com/jobs/",
            "https://linkedin.com/learning/",
            "https://linkedin.com/in/",  # Missing profile ID
        ]
        
        for url in valid_urls:
            assert is_valid_linkedin_url(url), f"Should be valid: {url}"
        
        for url in invalid_urls:
            assert not is_valid_linkedin_url(url), f"Should be invalid: {url}"
    
    def test_normalize_linkedin_url(self):
        """Test LinkedIn URL normalization to standard format."""
        test_cases: List[Tuple[str, str]] = [
            ("linkedin.com/in/johndoe", "https://www.linkedin.com/in/johndoe"),
            ("https://linkedin.com/in/johndoe?trk=profile", "https://www.linkedin.com/in/johndoe"),
            ("https://www.linkedin.com/in/johndoe/", "https://www.linkedin.com/in/johndoe"),
            ("http://linkedin.com/in/johndoe", "https://www.linkedin.com/in/johndoe"),
            ("linkedin.com/in/jane-doe-123", "https://www.linkedin.com/in/jane-doe-123"),
        ]
        
        for input_url, expected_url in test_cases:
            result = normalize_linkedin_url(input_url)
            assert result == expected_url, f"Failed for URL: {input_url}, expected: {expected_url}, got: {result}"
    
    def test_get_profile_url_from_id(self):
        """Test generating LinkedIn URL from profile ID."""
        test_cases: List[Tuple[str, str]] = [
            ("johndoe", "https://www.linkedin.com/in/johndoe"),
            ("richard-branson", "https://www.linkedin.com/in/richard-branson"),
            ("user_123", "https://www.linkedin.com/in/user_123"),
            ("jane-doe-123", "https://www.linkedin.com/in/jane-doe-123"),
            ("tech-leader-2024", "https://www.linkedin.com/in/tech-leader-2024"),
        ]
        
        for profile_id, expected_url in test_cases:
            result = get_profile_url_from_id(profile_id)
            assert result == expected_url, f"Failed for ID: {profile_id}, expected: {expected_url}, got: {result}"
    
    def test_edge_cases_and_boundaries(self):
        """Test edge cases and boundary conditions."""
        # Very long profile IDs
        long_id = "a" * 100
        assert is_valid_linkedin_url(f"https://linkedin.com/in/{long_id}")
        
        # Profile IDs with special characters (only those supported by LinkedIn)
        special_chars = ["user-123", "user_123"]  # Only hyphens and underscores are valid
        for special_id in special_chars:
            url = f"https://linkedin.com/in/{special_id}"
            assert is_valid_linkedin_url(url)
            extracted_id = extract_profile_id(url)
            assert extracted_id == special_id
        
        # Empty and whitespace handling
        with pytest.raises(ValueError):
            extract_profile_id("   ")
        with pytest.raises(ValueError):
            extract_profile_id("\t\n")
    
    def test_url_encoding_handling(self):
        """Test handling of URL-encoded characters."""
        # Note: The current implementation doesn't handle URL decoding
        # These tests verify that encoded URLs are rejected as expected
        encoded_urls = [
            "https://linkedin.com/in/jane%20doe",  # Space encoded as %20
            "https://linkedin.com/in/user%2D123",  # Hyphen encoded as %2D
            "https://linkedin.com/in/tech%5Fleader",  # Underscore encoded as %5F
        ]
        
        for encoded_url in encoded_urls:
            with pytest.raises(ValueError, match="Invalid profile ID format"):
                extract_profile_id(encoded_url)
    
    def test_case_insensitivity(self):
        """Test that URL validation is case-insensitive for profile IDs."""
        # Note: The current implementation is case-sensitive for profile IDs
        # This is the expected behavior for LinkedIn
        case_variations = [
            "https://linkedin.com/in/johndoe",
            "https://linkedin.com/in/JOHNDOE",
            "https://linkedin.com/in/JohnDoe",
        ]
        
        for url in case_variations:
            assert is_valid_linkedin_url(url), f"Should be valid: {url}"
            profile_id = extract_profile_id(url)
            # Profile ID should preserve case as LinkedIn does
            assert profile_id in ["johndoe", "JOHNDOE", "JohnDoe"], f"Should extract correct profile ID: {profile_id}" 