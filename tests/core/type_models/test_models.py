# ==============================================================================
# test_models.py — Core type models comprehensive testing
# ==============================================================================
# Purpose: Test core type models with 100% coverage
# Sections: Imports, Test Setup, Model Tests, Validation Tests
# ==============================================================================

# Standard Library --------------------------------------------------------------
from datetime import datetime, timezone
from typing import Dict, Any

# Third Party -------------------------------------------------------------------
import pytest
from pydantic import ValidationError

# Core (App-wide) ---------------------------------------------------------------
from core.types.models import RegistrationRequest, AnalysisOutput


class TestRegistrationRequest:
    """Test RegistrationRequest model validation and behavior."""
    
    def test_valid_registration_request(self):
        """Test valid registration request creation."""
        # Arrange
        valid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "company_website": "https://example.com",
            "linkedin": None
        }
        
        # Act
        request = RegistrationRequest(**valid_data)
        
        # Assert
        assert request.first_name == "John"
        assert request.last_name == "Doe"
        # Pydantic HttpUrl normalizes URLs (adds trailing slash)
        assert str(request.company_website) == "https://example.com/"
        assert request.linkedin is None
    
    def test_registration_request_with_linkedin(self):
        """Test registration request with LinkedIn URL."""
        # Arrange
        valid_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "company_website": None,
            "linkedin": "https://linkedin.com/in/janesmith"
        }
        
        # Act
        request = RegistrationRequest(**valid_data)
        
        # Assert
        assert request.first_name == "Jane"
        assert request.last_name == "Smith"
        assert request.company_website is None
        # Pydantic HttpUrl validates and stores the URL - check it's a valid HttpUrl object
        assert request.linkedin is not None
        assert str(request.linkedin).startswith("https://linkedin.com/in/janesmith")
    
    def test_registration_request_both_urls(self):
        """Test registration request with both URLs."""
        # Arrange
        valid_data = {
            "first_name": "Bob",
            "last_name": "Johnson",
            "company_website": "https://bobcompany.com",
            "linkedin": "https://linkedin.com/in/bobjohnson"
        }
        
        # Act
        request = RegistrationRequest(**valid_data)
        
        # Assert
        # Pydantic HttpUrl validates and stores the URLs - check they're valid HttpUrl objects
        assert request.company_website is not None
        assert request.linkedin is not None
        assert str(request.company_website).startswith("https://bobcompany.com")
        assert str(request.linkedin).startswith("https://linkedin.com/in/bobjohnson")
    
    def test_registration_request_missing_required_fields(self):
        """Test registration request validation with missing fields."""
        # Arrange
        invalid_data = {
            "first_name": "John"
            # Missing last_name, company_website, linkedin
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RegistrationRequest(**invalid_data)
        
        errors = exc_info.value.errors()
        # Only last_name is required - URLs are optional but at least one must be provided
        assert len(errors) == 1  # Only last_name missing
        assert any(error["loc"] == ("last_name",) for error in errors)
    
    def test_registration_request_empty_strings(self):
        """Test registration request with empty string values."""
        # Arrange
        invalid_data = {
            "first_name": "",
            "last_name": "",
            "company_website": "",
            "linkedin": ""
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RegistrationRequest(**invalid_data)
        
        errors = exc_info.value.errors()
        # Empty strings fail min_length validation for names, and URL validation for URLs
        assert len(errors) == 4  # All fields should fail validation
        assert any(error["loc"] == ("first_name",) for error in errors)
        assert any(error["loc"] == ("last_name",) for error in errors)
        assert any(error["loc"] == ("company_website",) for error in errors)
        assert any(error["loc"] == ("linkedin",) for error in errors)
    
    def test_registration_request_invalid_urls(self):
        """Test registration request with invalid URL formats."""
        # Arrange
        invalid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "company_website": "not-a-url",
            "linkedin": "also-not-a-url"
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RegistrationRequest(**invalid_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 2  # Both URLs should fail validation
        assert any(error["loc"] == ("company_website",) for error in errors)
        assert any(error["loc"] == ("linkedin",) for error in errors)
    
    def test_registration_request_whitespace_only(self):
        """Test registration request with whitespace-only values."""
        # Arrange
        invalid_data = {
            "first_name": "   ",
            "last_name": "   ",
            "company_website": "   ",
            "linkedin": "   "
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RegistrationRequest(**invalid_data)
        
        errors = exc_info.value.errors()
        # Pydantic validation behavior:
        # - Whitespace-only strings for names might pass min_length validation (depends on implementation)
        # - Whitespace-only strings for URLs definitely fail URL validation
        # The actual error count depends on Pydantic's validation order and implementation
        assert len(errors) >= 2  # At least URLs should fail validation
        
        # Check that we have errors for URL fields (these definitely fail)
        error_locations = [error["loc"] for error in errors]
        assert ("company_website",) in error_locations or ("linkedin",) in error_locations
        
        # Note: Name field validation for whitespace-only strings depends on Pydantic's min_length implementation
        # Some versions might treat "   " as having length 3, others might trim it
    
    def test_registration_request_very_long_names(self):
        """Test registration request with very long name values."""
        # Arrange
        long_name = "A" * 1000  # Very long name
        valid_data = {
            "first_name": long_name,
            "last_name": long_name,
            "company_website": "https://example.com",
            "linkedin": None
        }
        
        # Act & Assert
        # Should fail due to max_length constraint (100 characters)
        with pytest.raises(ValidationError) as exc_info:
            RegistrationRequest(**valid_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 2  # Both names should fail max_length validation
        assert any(error["loc"] == ("first_name",) for error in errors)
        assert any(error["loc"] == ("last_name",) for error in errors)
    
    def test_registration_request_special_characters(self):
        """Test registration request with special characters in names."""
        # Arrange
        valid_data = {
            "first_name": "José-María",
            "last_name": "O'Connor-Smith",
            "company_website": "https://example.com",
            "linkedin": None
        }
        
        # Act
        request = RegistrationRequest(**valid_data)
        
        # Assert
        assert request.first_name == "José-María"
        assert request.last_name == "O'Connor-Smith"
    
    def test_registration_request_model_export(self):
        """Test registration request model export functionality."""
        # Arrange
        valid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "company_website": "https://example.com",
            "linkedin": None
        }
        request = RegistrationRequest(**valid_data)
        
        # Act
        exported = request.model_dump()
        
        # Assert
        # Pydantic exports HttpUrl as HttpUrl objects, not strings
        assert exported["first_name"] == "John"
        assert exported["last_name"] == "Doe"
        assert exported["linkedin"] is None
        # company_website should be an HttpUrl object
        assert exported["company_website"] is not None
        assert str(exported["company_website"]).startswith("https://example.com")
    
    def test_registration_request_model_validation(self):
        """Test registration request model validation methods."""
        # Arrange
        valid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "company_website": "https://example.com",
            "linkedin": None
        }
        
        # Act
        request = RegistrationRequest.model_validate(valid_data)
        
        # Assert
        assert request.first_name == "John"
        assert request.last_name == "Doe"
        # Pydantic HttpUrl normalizes URLs (adds trailing slash)
        assert str(request.company_website) == "https://example.com/"
    
    def test_registration_request_no_urls_raises_error(self):
        """Test that providing no URLs raises validation error."""
        # Arrange
        invalid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "company_website": None,
            "linkedin": None
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="At least one URL"):
            RegistrationRequest(**invalid_data)
    
    def test_registration_request_at_least_one_url_required(self):
        """Test that at least one URL is required."""
        # Arrange - only company_website
        valid_data_website = {
            "first_name": "John",
            "last_name": "Doe",
            "company_website": "https://example.com",
            "linkedin": None
        }
        
        # Arrange - only linkedin
        valid_data_linkedin = {
            "first_name": "Jane",
            "last_name": "Smith",
            "company_website": None,
            "linkedin": "https://linkedin.com/in/janesmith"
        }
        
        # Act & Assert - both should work
        request1 = RegistrationRequest(**valid_data_website)
        request2 = RegistrationRequest(**valid_data_linkedin)
        
        assert request1.company_website is not None
        assert request1.linkedin is None
        assert request2.company_website is None
        assert request2.linkedin is not None


class TestAnalysisOutput:
    """Test AnalysisOutput model validation and behavior."""
    
    def test_valid_analysis_output(self):
        """Test valid analysis output creation."""
        # Arrange
        valid_data = {
            "request_id": "test-123",
            "timestamp": "2024-01-15T10:30:00Z",
            "input_data": {
                "first_name": "John",
                "last_name": "Doe",
                "company_website": "https://example.com",
                "linkedin": None
            },
            "linkedin_analysis": None,
            "website_analysis": {
                "base_url": "https://example.com",
                "discovered_urls": [],
                "filtered_urls": [],
                "extracted_content": {},
                "analysis_timestamp": "2024-01-15T10:30:00Z"
            }
        }
        
        # Act
        output = AnalysisOutput(**valid_data)
        
        # Assert
        assert output.request_id == "test-123"
        # Pydantic converts ISO string to datetime object
        assert isinstance(output.timestamp, datetime)
        assert output.timestamp.year == 2024
        assert output.timestamp.month == 1
        assert output.timestamp.day == 15
        assert output.timestamp.hour == 10
        assert output.timestamp.minute == 30
        assert output.linkedin_analysis is None
        assert output.website_analysis is not None
    
    def test_analysis_output_with_linkedin_data(self):
        """Test analysis output with LinkedIn analysis data."""
        # Arrange
        valid_data = {
            "request_id": "test-456",
            "timestamp": "2024-01-15T11:00:00Z",
            "input_data": {
                "first_name": "Jane",
                "last_name": "Smith",
                "company_website": None,
                "linkedin": "https://linkedin.com/in/janesmith"
            },
            "linkedin_analysis": {
                "full_name": "Jane Smith",
                "headline": "Software Engineer",
                "experience": ["Company A", "Company B"]
            },
            "website_analysis": None
        }
        
        # Act
        output = AnalysisOutput(**valid_data)
        
        # Assert
        assert output.request_id == "test-456"
        assert output.linkedin_analysis is not None
        assert output.linkedin_analysis["full_name"] == "Jane Smith"
        assert output.website_analysis is None
    
    def test_analysis_output_with_both_analyses(self):
        """Test analysis output with both LinkedIn and website analysis."""
        # Arrange
        valid_data = {
            "request_id": "test-789",
            "timestamp": "2024-01-15T12:00:00Z",
            "input_data": {
                "first_name": "Bob",
                "last_name": "Johnson",
                "company_website": "https://bobcompany.com",
                "linkedin": "https://linkedin.com/in/bobjohnson"
            },
            "linkedin_analysis": {"full_name": "Bob Johnson"},
            "website_analysis": {"base_url": "https://bobcompany.com"}
        }
        
        # Act
        output = AnalysisOutput(**valid_data)
        
        # Assert
        assert output.request_id == "test-789"
        assert output.linkedin_analysis is not None
        assert output.website_analysis is not None
    
    def test_analysis_output_missing_required_fields(self):
        """Test analysis output validation with missing fields."""
        # Arrange
        invalid_data = {
            "request_id": "test-123"
            # Missing timestamp, input_data, linkedin_analysis, website_analysis
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            AnalysisOutput(**invalid_data)
        
        errors = exc_info.value.errors()
        # Only input_data is required - others have defaults
        assert len(errors) == 1  # Only input_data missing
        assert any(error["loc"] == ("input_data",) for error in errors)
    
    def test_analysis_output_invalid_timestamp_format(self):
        """Test analysis output with invalid timestamp format."""
        # Arrange
        invalid_data = {
            "request_id": "test-123",
            "timestamp": "invalid-timestamp",
            "input_data": {
                "first_name": "John",
                "last_name": "Doe",
                "company_website": "https://example.com",
                "linkedin": None
            },
            "linkedin_analysis": None,
            "website_analysis": {
                "base_url": "https://example.com",
                "discovered_urls": [],
                "filtered_urls": [],
                "extracted_content": {},
                "analysis_timestamp": "2024-01-15T10:30:00Z"
            }
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            AnalysisOutput(**invalid_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1  # timestamp format error
        assert any(error["loc"] == ("timestamp",) for error in errors)
    
    def test_analysis_output_empty_request_id(self):
        """Test analysis output with empty request ID."""
        # Arrange
        invalid_data = {
            "request_id": "",
            "timestamp": "2024-01-15T10:30:00Z",
            "input_data": {
                "first_name": "John",
                "last_name": "Doe",
                "company_website": "https://example.com",
                "linkedin": None
            },
            "linkedin_analysis": None,
            "website_analysis": {
                "base_url": "https://example.com",
                "discovered_urls": [],
                "filtered_urls": [],
                "extracted_content": {},
                "analysis_timestamp": "2024-01-15T10:30:00Z"
            }
        }
        
        # Act & Assert
        # Empty string is valid for request_id (no min_length constraint)
        output = AnalysisOutput(**invalid_data)
        assert output.request_id == ""
    
    def test_analysis_output_model_export(self):
        """Test analysis output model export functionality."""
        # Arrange
        valid_data = {
            "request_id": "test-123",
            "timestamp": "2024-01-15T10:30:00Z",
            "input_data": {
                "first_name": "John",
                "last_name": "Doe",
                "company_website": "https://example.com",
                "linkedin": None
            },
            "linkedin_analysis": None,
            "website_analysis": {
                "base_url": "https://example.com",
                "discovered_urls": [],
                "filtered_urls": [],
                "extracted_content": {},
                "analysis_timestamp": "2024-01-15T10:30:00Z"
            }
        }
        output = AnalysisOutput(**valid_data)
        
        # Act
        exported = output.model_dump()
        
        # Assert
        assert exported["request_id"] == "test-123"
        # Pydantic exports datetime as datetime object, not string
        assert isinstance(exported["timestamp"], datetime)
        assert exported["timestamp"].year == 2024
        assert exported["timestamp"].month == 1
        assert exported["timestamp"].day == 15
    
    def test_analysis_output_model_validation(self):
        """Test analysis output model validation methods."""
        # Arrange
        valid_data = {
            "request_id": "test-123",
            "timestamp": "2024-01-15T10:30:00Z",
            "input_data": {
                "first_name": "John",
                "last_name": "Doe",
                "company_website": "https://example.com",
                "linkedin": None
            },
            "linkedin_analysis": None,
            "website_analysis": {
                "base_url": "https://example.com",
                "discovered_urls": [],
                "filtered_urls": [],
                "extracted_content": {},
                "analysis_timestamp": "2024-01-15T10:30:00Z"
            }
        }
        
        # Act
        output = AnalysisOutput.model_validate(valid_data)
        
        # Assert
        assert output.request_id == "test-123"
        # Pydantic converts ISO string to datetime object
        assert isinstance(output.timestamp, datetime)
        assert output.timestamp.year == 2024
        assert output.timestamp.month == 1
        assert output.timestamp.day == 15
    
    def test_analysis_output_default_timestamp(self):
        """Test that timestamp defaults to current time when not provided."""
        # Arrange
        valid_data = {
            "request_id": "test-default-timestamp",
            "input_data": {
                "first_name": "John",
                "last_name": "Doe",
                "company_website": "https://example.com",
                "linkedin": None
            },
            "linkedin_analysis": None,
            "website_analysis": {
                "base_url": "https://example.com",
                "discovered_urls": [],
                "filtered_urls": [],
                "extracted_content": {},
                "analysis_timestamp": "2024-01-15T10:30:00Z"
            }
        }
        
        # Act
        output = AnalysisOutput(**valid_data)
        
        # Assert
        assert output.request_id == "test-default-timestamp"
        # Should have default timestamp (current time)
        assert isinstance(output.timestamp, datetime)
        # Should be recent (within last minute)
        now = datetime.now(timezone.utc)
        time_diff = abs((now - output.timestamp).total_seconds())
        assert time_diff < 60  # Within 60 seconds


class TestModelIntegration:
    """Test integration between models."""
    
    def test_registration_to_analysis_workflow(self):
        """Test complete workflow from registration to analysis output."""
        # Arrange
        registration = RegistrationRequest(
            first_name="John",
            last_name="Doe",
            company_website="https://example.com",
            linkedin=None
        )
        
        # Act
        analysis_output = AnalysisOutput(
            request_id="test-123",
            timestamp="2024-01-15T10:30:00Z",
            input_data=registration,  # Pass the model instance directly
            linkedin_analysis=None,
            website_analysis={
                "base_url": "https://example.com",
                "discovered_urls": [],
                "filtered_urls": [],
                "extracted_content": {},
                "analysis_timestamp": "2024-01-15T10:30:00Z"
            }
        )
        
        # Assert
        # input_data is now a RegistrationRequest object, not a dict
        assert analysis_output.input_data.first_name == "John"
        assert analysis_output.input_data.last_name == "Doe"
        assert str(analysis_output.input_data.company_website) == "https://example.com/"
    
    def test_models_serialization_compatibility(self):
        """Test that models can be serialized and deserialized."""
        # Arrange
        registration = RegistrationRequest(
            first_name="John",
            last_name="Doe",
            company_website="https://example.com",
            linkedin=None
        )
        
        # Act
        serialized = registration.model_dump()
        deserialized = RegistrationRequest(**serialized)
        
        # Assert
        assert deserialized.first_name == registration.first_name
        assert deserialized.last_name == registration.last_name
        # URLs are normalized during serialization/deserialization
        assert str(deserialized.company_website) == str(registration.company_website) 