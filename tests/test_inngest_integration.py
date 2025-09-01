"""Test Inngest integration and event triggering."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from api.main import app
from services.inngest.client import inngest_client
from core.types.models import RegistrationRequest

# Create test client
client = TestClient(app)


class TestInngestIntegration:
    """Test Inngest event triggering and background processing."""

    def test_register_endpoint_triggers_inngest_event(self):
        """Test that /register endpoint properly triggers Inngest event."""
        # Arrange
        test_data = {
            "first_name": "John",
            "last_name": "Doe",
            "company_website": "https://example.com"
        }
        
        # Mock the Inngest client send method
        with patch.object(inngest_client, 'send', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = None
            
            # Act
            response = client.post("/register", json=test_data)
            
            # Assert
            assert response.status_code == 200
            response_data = response.json()
            assert "request_id" in response_data
            assert response_data["status"] == "queued"
            assert response_data["message"] == "Registration received and queued for processing"
            
            # Verify Inngest event was sent
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            event = call_args[0][0]  # First argument is the Event object
            
            assert event.name == "registration.received"
            assert "request_id" in event.data
            assert "registration_data" in event.data
            assert event.data["registration_data"]["first_name"] == "John"
            assert event.data["registration_data"]["last_name"] == "Doe"
            # Pydantic HttpUrl normalizes URLs (adds trailing slash)
            assert str(event.data["registration_data"]["company_website"]) == "https://example.com/"

    def test_register_endpoint_handles_inngest_failure(self):
        """Test that /register endpoint handles Inngest send failures gracefully."""
        # Arrange
        test_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "linkedin": "https://linkedin.com/in/janesmith"
        }
        
        # Mock the Inngest client send method to raise an exception
        with patch.object(inngest_client, 'send', new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = Exception("Inngest connection failed")
            
            # Act
            response = client.post("/register", json=test_data)
            
            # Assert
            assert response.status_code == 500
            response_data = response.json()
            assert response_data["detail"]["error"] == "Background processing failed"
            assert "Failed to queue registration for processing" in response_data["detail"]["message"]

    def test_register_endpoint_validation_failure(self):
        """Test that /register endpoint fails early on validation errors."""
        # Arrange - Missing required URLs
        test_data = {
            "first_name": "John",
            "last_name": "Doe"
            # Missing both company_website and linkedin
        }
        
        # Act
        response = client.post("/register", json=test_data)
        
        # Assert
        assert response.status_code == 422  # Pydantic validation error
        response_data = response.json()
        assert "value error" in response_data["detail"][0]["msg"].lower()

    def test_register_endpoint_with_linkedin_only(self):
        """Test that /register endpoint works with LinkedIn URL only."""
        # Arrange
        test_data = {
            "first_name": "Alice",
            "last_name": "Johnson",
            "linkedin": "https://linkedin.com/in/alicejohnson"
        }
        
        # Mock the Inngest client send method
        with patch.object(inngest_client, 'send', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = None
            
            # Act
            response = client.post("/register", json=test_data)
            
            # Assert
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["status"] == "queued"
            
            # Verify event data contains LinkedIn URL
            call_args = mock_send.call_args
            event = call_args[0][0]
            assert str(event.data["registration_data"]["linkedin"]) == "https://linkedin.com/in/alicejohnson"
            assert event.data["registration_data"]["company_website"] is None

    def test_register_endpoint_with_both_urls(self):
        """Test that /register endpoint works with both URLs provided."""
        # Arrange
        test_data = {
            "first_name": "Bob",
            "last_name": "Wilson",
            "company_website": "https://bobsworld.com",
            "linkedin": "https://linkedin.com/in/bobwilson"
        }
        
        # Mock the Inngest client send method
        with patch.object(inngest_client, 'send', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = None
            
            # Act
            response = client.post("/register", json=test_data)
            
            # Assert
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["status"] == "queued"
            
            # Verify event data contains both URLs
            call_args = mock_send.call_args
            event = call_args[0][0]
            assert str(event.data["registration_data"]["company_website"]) == "https://bobsworld.com/"
            assert str(event.data["registration_data"]["linkedin"]) == "https://linkedin.com/in/bobwilson"


# Note: Inngest function testing is complex due to the wrapper nature of the functions.
# The important integration tests above verify that:
# 1. Events are properly triggered from the API endpoint
# 2. Error handling works correctly
# 3. Validation is enforced
# 4. Different URL combinations work as expected
#
# The actual Inngest function logic is tested through the domain tests
# in tests/domains/intelligence_collection/test_process.py


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 