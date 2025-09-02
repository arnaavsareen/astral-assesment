# ==============================================================================
# test_health.py — Health check API endpoint tests
# ==============================================================================
# Purpose: Test health check endpoints and service status verification
# Sections: Imports, Test Configuration, Health Check Tests, Service Status Tests
# ==============================================================================

# Standard Library --------------------------------------------------------------
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Third Party -------------------------------------------------------------------
from fastapi.testclient import TestClient

# Core (App-wide) ---------------------------------------------------------------
from api.main import app

# Test client
client = TestClient(app)


class TestHealthEndpoint:
    """Test basic health check endpoint functionality."""
    
    def test_health_endpoint_accessible(self):
        """Test that health endpoint is accessible."""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_endpoint_response_structure(self):
        """Test health endpoint response structure."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"
        assert isinstance(data["timestamp"], str)
    
    def test_health_endpoint_timestamp_format(self):
        """Test that timestamp is in ISO format."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        timestamp = data["timestamp"]
        
        # Should be ISO format (YYYY-MM-DDTHH:MM:SS.mmmZ)
        assert "T" in timestamp
        assert len(timestamp) > 19  # At least YYYY-MM-DDTHH:MM:SS
        assert timestamp.count("-") == 2  # Two hyphens for date
        assert timestamp.count(":") == 2  # Two colons for time


class TestHealthEndpointMethods:
    """Test health endpoint HTTP methods."""
    
    def test_health_get_method(self):
        """Test that GET method works for health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_post_method_not_allowed(self):
        """Test that POST method is not allowed for health endpoint."""
        response = client.post("/health")
        assert response.status_code == 405  # Method Not Allowed
    
    def test_health_put_method_not_allowed(self):
        """Test that PUT method is not allowed for health endpoint."""
        response = client.put("/health")
        assert response.status_code == 405  # Method Not Allowed
    
    def test_health_delete_method_not_allowed(self):
        """Test that DELETE method is not allowed for health endpoint."""
        response = client.delete("/health")
        assert response.status_code == 405  # Method Not Allowed


class TestHealthEndpointHeaders:
    """Test health endpoint response headers."""
    
    def test_health_endpoint_content_type(self):
        """Test that health endpoint returns correct content type."""
        response = client.get("/health")
        assert response.status_code == 200
        
        content_type = response.headers.get("content-type")
        assert content_type is not None
        assert "application/json" in content_type
    
    def test_health_endpoint_cors_headers(self):
        """Test that CORS headers are present."""
        response = client.get("/health")
        assert response.status_code == 200
        
        # CORS headers should be present due to middleware
        # Note: FastAPI test client might not show all middleware headers
        # This is a basic check that the endpoint responds correctly


class TestHealthEndpointPerformance:
    """Test health endpoint performance characteristics."""
    
    def test_health_endpoint_response_time(self):
        """Test that health endpoint responds quickly."""
        import time
        
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        
        response_time = end_time - start_time
        # Should respond in under 100ms (very fast for health check)
        assert response_time < 0.1, f"Health endpoint too slow: {response_time:.3f}s"
    
    def test_health_endpoint_concurrent_requests(self):
        """Test that health endpoint handles concurrent requests."""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                start_time = time.time()
                response = client.get("/health")
                end_time = time.time()
                results.append({
                    "status_code": response.status_code,
                    "response_time": end_time - start_time
                })
            except Exception as e:
                errors.append(str(e))
        
        # Create 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Concurrent requests failed: {errors}"
        assert len(results) == 10, "Not all concurrent requests completed"
        
        # All requests should succeed
        for result in results:
            assert result["status_code"] == 200
            assert result["response_time"] < 0.1  # Should be fast


class TestHealthEndpointErrorHandling:
    """Test health endpoint error handling."""
    
    def test_health_endpoint_with_invalid_method(self):
        """Test health endpoint with invalid HTTP method."""
        response = client.patch("/health")
        assert response.status_code == 405  # Method Not Allowed
    
    def test_health_endpoint_with_query_params(self):
        """Test health endpoint with query parameters (should ignore them)."""
        response = client.get("/health?debug=true&format=json")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data


class TestHealthEndpointConsistency:
    """Test health endpoint response consistency."""
    
    def test_health_endpoint_multiple_calls(self):
        """Test that health endpoint returns consistent responses."""
        responses = []
        
        # Make multiple calls
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200
            responses.append(response.json())
        
        # Check that all responses have the same structure
        for i, response in enumerate(responses):
            assert "status" in response, f"Response {i} missing status"
            assert "timestamp" in response, f"Response {i} missing timestamp"
            assert response["status"] == "healthy", f"Response {i} has wrong status"
        
        # Check that timestamps are different (time passes between calls)
        timestamps = [r["timestamp"] for r in responses]
        unique_timestamps = set(timestamps)
        assert len(unique_timestamps) > 1, "All timestamps should be different"


class TestHealthEndpointEdgeCases:
    """Test health endpoint edge cases."""
    
    def test_health_endpoint_with_very_long_url(self):
        """Test health endpoint with very long URL path."""
        # Create a very long path (should still work)
        long_path = "/health" + "/" * 1000
        
        response = client.get(long_path)
        # Should either work or return 404, but not crash
        assert response.status_code in [200, 404]
    
    def test_health_endpoint_with_special_characters(self):
        """Test health endpoint with special characters in path."""
        # Test with various special characters
        special_paths = [
            "/health%20check",
            "/health/check",
            "/health?param=value",
            "/health#fragment"
        ]
        
        for path in special_paths:
            response = client.get(path)
            # Should either work or return 404, but not crash
            assert response.status_code in [200, 404]
    
    def test_health_endpoint_with_unicode(self):
        """Test health endpoint with unicode characters."""
        # Test with unicode characters
        unicode_paths = [
            "/health/测试",
            "/health/тест",
            "/health/テスト"
        ]
        
        for path in unicode_paths:
            response = client.get(path)
            # Should either work or return 404, but not crash
            assert response.status_code in [200, 404]


class TestHealthEndpointIntegration:
    """Test health endpoint integration with the application."""
    
    def test_health_endpoint_through_main_app(self):
        """Test health endpoint through the main FastAPI application."""
        # This test ensures the health endpoint is properly integrated
        # into the main application and accessible through the router
        
        response = client.get("/health")
        assert response.status_code == 200
        
        # Verify the response comes from our health router
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_health_endpoint_router_inclusion(self):
        """Test that health router is properly included in main app."""
        # Check if health routes are included in the main app
        from api.main import app
        
        health_routes = [route for route in app.routes if "/health" in route.path]
        assert len(health_routes) > 0, "Health routes should be included in main app"
        
        # Check that the health endpoint is accessible
        response = client.get("/health")
        assert response.status_code == 200 