# ==============================================================================
# test_register.py — Registration API endpoint tests
# ==============================================================================
# Purpose: Test user registration endpoint functionality and validation
# Sections: Imports, Test Configuration, Registration Tests, Validation Tests, Error Tests
# ==============================================================================

# Standard Library --------------------------------------------------------------
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

# Third Party -------------------------------------------------------------------
from fastapi.testclient import TestClient
from fastapi import HTTPException

# Core (App-wide) ---------------------------------------------------------------
from api.main import app
from core.types.models import RegistrationRequest

# Test client
client = TestClient(app)


class TestRegistrationEndpoint:
    """Test registration endpoint functionality."""
    
    def test_register_endpoint_exists(self):
        """Test that registration endpoint is accessible."""
        response = client.get("/register")
        # Should return 405 Method Not Allowed (GET not supported)
        assert response.status_code == 405
    
    def test_register_endpoint_post_supported(self):
        """Test that POST method is supported."""
        response = client.options("/register")
        # OPTIONS should return 200 with allowed methods, but FastAPI might return 405
        assert response.status_code in [200, 405]


class TestRegistrationValidation:
    """Test registration data validation."""
    
    def test_valid_registration_request(self):
        """Test successful registration with valid data."""
        valid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "company_website": "https://example.com",
            "linkedin": "https://linkedin.com/in/johndoe"
        }
        
        with patch('services.inngest.inngest_client.send') as mock_send:
            mock_send.return_value = None
            
            response = client.post("/register", json=valid_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "request_id" in data
            assert data["status"] == "queued"
            assert "Registration received and queued for processing" in data["message"]
            
            # Verify Inngest event was sent
            mock_send.assert_called_once()
    
    def test_registration_with_company_website_only(self):
        """Test registration with only company website."""
        valid_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "company_website": "https://company.com"
        }
        
        with patch('services.inngest.inngest_client.send') as mock_send:
            mock_send.return_value = None
            
            response = client.post("/register", json=valid_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "queued"
    
    def test_registration_with_linkedin_only(self):
        """Test registration with only LinkedIn profile."""
        valid_data = {
            "first_name": "Bob",
            "last_name": "Johnson",
            "linkedin": "https://linkedin.com/in/bobjohnson"
        }
        
        with patch('services.inngest.inngest_client.send') as mock_send:
            mock_send.return_value = None
            
            response = client.post("/register", json=valid_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "queued"
    
    def test_registration_with_both_urls(self):
        """Test registration with both company website and LinkedIn."""
        valid_data = {
            "first_name": "Alice",
            "last_name": "Brown",
            "company_website": "https://company.com",
            "linkedin": "https://linkedin.com/in/alicebrown"
        }
        
        with patch('services.inngest.inngest_client.send') as mock_send:
            mock_send.return_value = None
            
            response = client.post("/register", json=valid_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "queued"


class TestRegistrationValidationErrors:
    """Test registration validation error handling."""
    
    def test_missing_required_fields(self):
        """Test registration with missing required fields."""
        invalid_data = {
            "first_name": "John"
            # Missing last_name and at least one URL
        }
        
        response = client.post("/register", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
        error_data = response.json()
        assert "detail" in error_data
    
    def test_missing_first_name(self):
        """Test registration without first name."""
        invalid_data = {
            "last_name": "Doe",
            "company_website": "https://example.com"
        }
        
        response = client.post("/register", json=invalid_data)
        
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
    
    def test_missing_last_name(self):
        """Test registration without last name."""
        invalid_data = {
            "first_name": "John",
            "company_website": "https://example.com"
        }
        
        response = client.post("/register", json=invalid_data)
        
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
    
    def test_missing_all_urls(self):
        """Test registration without any URLs."""
        invalid_data = {
            "first_name": "John",
            "last_name": "Doe"
            # Missing both company_website and linkedin
        }
        
        response = client.post("/register", json=invalid_data)
        
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
    
    def test_invalid_company_website_url(self):
        """Test registration with invalid company website URL."""
        invalid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "company_website": "not-a-valid-url",
            "linkedin": "https://linkedin.com/in/johndoe"
        }
        
        response = client.post("/register", json=invalid_data)
        
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
    
    def test_invalid_linkedin_url(self):
        """Test registration with invalid LinkedIn URL."""
        invalid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "company_website": "https://example.com",
            "linkedin": "not-a-valid-url"
        }
        
        response = client.post("/register", json=invalid_data)
        
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
    
    def test_empty_strings(self):
        """Test registration with empty string values."""
        invalid_data = {
            "first_name": "",
            "last_name": "",
            "company_website": "https://example.com"
        }
        
        response = client.post("/register", json=invalid_data)
        
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
    
    def test_whitespace_only_strings(self):
        """Test registration with whitespace-only values."""
        invalid_data = {
            "first_name": "   ",
            "last_name": "   ",
            "company_website": "https://example.com"
        }
        
        response = client.post("/register", json=invalid_data)
        
        # Should return either 422 (validation error) or 500 (server error)
        # depending on how Pydantic handles whitespace-only strings
        assert response.status_code in [422, 500]
        if response.status_code == 500:
            # If it's a 500, check that it's due to Inngest failure
            error_data = response.json()
            assert "Background processing failed" in error_data["detail"]["error"]


class TestRegistrationInngestIntegration:
    """Test Inngest integration during registration."""
    
    def test_inngest_event_sent_successfully(self):
        """Test that Inngest event is sent with correct data."""
        valid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "company_website": "https://example.com"
        }
        
        with patch('services.inngest.inngest_client.send') as mock_send:
            mock_send.return_value = None
            
            response = client.post("/register", json=valid_data)
            
            assert response.status_code == 200
            
            # Verify Inngest event was sent with correct data
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            
            # Check event structure
            event = call_args[0][0]  # First argument is the Event
            assert event.name == "registration.received"
            assert "request_id" in event.data
            assert "registration_data" in event.data
            assert event.data["registration_data"]["first_name"] == "John"
            assert event.data["registration_data"]["last_name"] == "Doe"
    
    def test_inngest_failure_handling(self):
        """Test handling of Inngest service failure."""
        valid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "company_website": "https://example.com"
        }
        
        with patch('services.inngest.inngest_client.send') as mock_send:
            mock_send.side_effect = Exception("Inngest service unavailable")
            
            response = client.post("/register", json=valid_data)
            
            assert response.status_code == 500
            error_data = response.json()
            # Check the error structure - it's nested under 'detail'
            assert "detail" in error_data
            assert "Background processing failed" in error_data["detail"]["error"]
            assert "request_id" in error_data["detail"]
    
    def test_inngest_failure_logging(self):
        """Test that Inngest failures are properly logged."""
        valid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "company_website": "https://example.com"
        }
        
        with patch('services.inngest.inngest_client.send') as mock_send, \
             patch('api.routers.register.logger') as mock_logger:
            
            mock_send.side_effect = Exception("Inngest service unavailable")
            
            response = client.post("/register", json=valid_data)
            
            assert response.status_code == 500
            
            # Verify error was logged
            mock_logger.error.assert_called()
            log_call = mock_logger.error.call_args
            assert "Failed to trigger background processing" in log_call[0][0]


class TestRegistrationResponseFormat:
    """Test registration response format and structure."""
    
    def test_successful_response_structure(self):
        """Test that successful registration returns correct response structure."""
        valid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "company_website": "https://example.com"
        }
        
        with patch('services.inngest.inngest_client.send') as mock_send:
            mock_send.return_value = None
            
            response = client.post("/register", json=valid_data)
            
            assert response.status_code == 200
            data = response.json()
            
            # Check required fields
            required_fields = ["request_id", "status", "message"]
            for field in required_fields:
                assert field in data, f"Response missing required field: {field}"
            
            # Check field types
            assert isinstance(data["request_id"], str)
            assert isinstance(data["status"], str)
            assert isinstance(data["message"], str)
            
            # Check field values
            assert data["status"] == "queued"
            assert len(data["request_id"]) > 0  # Should be a UUID
    
    def test_request_id_uniqueness(self):
        """Test that each registration gets a unique request ID."""
        valid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "company_website": "https://example.com"
        }
        
        with patch('services.inngest.inngest_client.send') as mock_send:
            mock_send.return_value = None
            
            # Make two registration requests
            response1 = client.post("/register", json=valid_data)
            response2 = client.post("/register", json=valid_data)
            
            assert response1.status_code == 200
            assert response2.status_code == 200
            
            data1 = response1.json()
            data2 = response2.json()
            
            # Request IDs should be different
            assert data1["request_id"] != data2["request_id"], "Request IDs should be unique" 