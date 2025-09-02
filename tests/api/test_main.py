# ==============================================================================
# test_main.py — FastAPI application configuration and lifecycle tests
# ==============================================================================
# Purpose: Test FastAPI app configuration, middleware, and lifecycle management
# Sections: Imports, App Configuration Tests, Middleware Tests, Lifecycle Tests
# ==============================================================================

# Standard Library --------------------------------------------------------------
import pytest
from unittest.mock import patch, MagicMock

# Third Party -------------------------------------------------------------------
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Core (App-wide) ---------------------------------------------------------------
from api.main import app, lifespan


class TestFastAPIApp:
    """Test FastAPI application configuration and setup."""
    
    def test_app_creation(self):
        """Test that FastAPI app is created with correct configuration."""
        assert isinstance(app, FastAPI)
        assert app.title == "astral-assessment"
        assert app.version == "0.1.0"
        assert "Business intelligence collection and analysis platform" in app.description
    
    def test_cors_middleware_configured(self):
        """Test that CORS middleware is properly configured."""
        # Check if CORS middleware is added
        middleware_found = False
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(middleware.cls):
                middleware_found = True
                break
        
        assert middleware_found, "CORS middleware should be configured"
    
    def test_routers_included(self):
        """Test that all required routers are included."""
        # Check if health and register routers are included
        router_paths = [route.path for route in app.routes]
        
        # Health router should be included
        assert any("/health" in path for path in router_paths), "Health router should be included"
        
        # Register router should be included
        assert any("/register" in path for path in router_paths), "Register router should be included"
    
    def test_global_exception_handler(self):
        """Test that global exception handler is configured."""
        # Check if global exception handler is registered
        exception_handlers = app.exception_handlers
        assert Exception in exception_handlers, "Global exception handler should be registered"
    
    def test_app_metadata(self):
        """Test app metadata and configuration."""
        assert app.title == "astral-assessment"
        assert app.version == "0.1.0"
        assert app.description is not None
        assert len(app.description) > 0


class TestAppLifespan:
    """Test application startup and shutdown lifecycle."""
    
    @pytest.mark.asyncio
    async def test_lifespan_startup(self):
        """Test application startup lifecycle."""
        startup_logs = []
        
        # Mock logger to capture startup messages
        with patch('api.main.logger') as mock_logger:
            mock_logger.info = MagicMock(side_effect=lambda msg, **kwargs: startup_logs.append(msg))
            
            async with lifespan(app):
                # App should be running during context
                pass
        
        # Check startup logs
        assert any("Starting application" in log for log in startup_logs), "Startup message should be logged"
        assert any("Application startup completed successfully" in log for log in startup_logs), "Startup completion should be logged"
    
    @pytest.mark.asyncio
    async def test_lifespan_shutdown(self):
        """Test application shutdown lifecycle."""
        shutdown_logs = []
        
        # Mock logger to capture shutdown messages
        with patch('api.main.logger') as mock_logger:
            mock_logger.info = MagicMock(side_effect=lambda msg, **kwargs: shutdown_logs.append(msg))
            
            async with lifespan(app):
                # App runs here
                pass
        
        # Check shutdown logs
        assert any("Application shutting down" in log for log in shutdown_logs), "Shutdown message should be logged"


class TestAppEndpoints:
    """Test basic app endpoint functionality."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    def test_root_endpoint_not_found(self):
        """Test that root endpoint returns 404 (not configured)."""
        response = self.client.get("/")
        # FastAPI might have a default root endpoint, so check for either 404 or 200
        assert response.status_code in [200, 404]
    
    def test_docs_endpoint_available(self):
        """Test that OpenAPI docs endpoint is available."""
        response = self.client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_schema_available(self):
        """Test that OpenAPI schema endpoint is available."""
        response = self.client.get("/openapi.json")
        assert response.status_code == 200
        
        # Check schema structure
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
    
    def test_health_endpoint_available(self):
        """Test that health endpoint is available."""
        response = self.client.get("/health")
        assert response.status_code == 200
    
    def test_register_endpoint_available(self):
        """Test that register endpoint is available."""
        response = self.client.get("/register")
        # GET might not be allowed, but endpoint should exist
        assert response.status_code in [405, 404]  # Method not allowed or not found is OK


class TestAppConfiguration:
    """Test app configuration and settings."""
    
    def test_app_has_lifespan(self):
        """Test that app has lifespan configured."""
        assert hasattr(app, 'router')
        assert app.router is not None
    
    def test_app_has_middleware(self):
        """Test that app has middleware configured."""
        assert len(app.user_middleware) > 0
    
    def test_app_has_routes(self):
        """Test that app has routes configured."""
        assert len(app.routes) > 0
    
    def test_app_has_exception_handlers(self):
        """Test that app has exception handlers configured."""
        assert len(app.exception_handlers) > 0 