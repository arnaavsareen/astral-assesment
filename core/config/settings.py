"""Application configuration settings using Pydantic v2."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application metadata
    app_name: str = Field(default="astral-assessment", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    environment: str = Field(default="development", description="Environment (development/production)")
    
    # Inngest configuration
    inngest_app_id: Optional[str] = Field(default=None, description="Inngest application ID")
    inngest_event_key: Optional[str] = Field(default=None, description="Inngest event key for authentication")
    inngest_signing_key: Optional[str] = Field(default=None, description="Inngest signing key for webhook verification")
    
    # ScrapingDog configuration
    scrapingdog_api_key: Optional[str] = Field(default=None, description="ScrapingDog API key for LinkedIn scraping")
    scrapingdog_premium_proxy: bool = Field(default=False, description="Use premium proxies for ScrapingDog")
    scrapingdog_max_retries: int = Field(default=3, description="Maximum retry attempts for ScrapingDog API")
    scrapingdog_timeout: int = Field(default=30, description="Request timeout in seconds for ScrapingDog API")
    
    # External API configuration
    firecrawl_api_key: str = Field(default="", description="Firecrawl API key for web scraping")
    proxycurl_api_key: str = Field(default="", description="Proxycurl API key for LinkedIn analysis")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key for AI processing")
    
    # Performance & Limits
    max_urls_per_website: int = Field(default=7, description="Maximum URLs to process per website")
    request_timeout: int = Field(default=30, description="Request timeout in seconds")
    max_concurrent_requests: int = Field(default=5, description="Maximum concurrent requests")
    
    # Logging & Debugging
    log_level: str = Field(default="INFO", description="Log level")
    debug: bool = Field(default=False, description="Enable debug logging")
    log_requests: bool = Field(default=True, description="Enable detailed request logging")
    
    # Development Server Settings
    host: str = Field(default="0.0.0.0", description="Development server host")
    port: int = Field(default=8000, description="Development server port")
    auto_reload: bool = Field(default=True, description="Enable auto-reload for development")
    
    # Output Configuration
    output_dir: str = Field(default="outputs", description="Directory for storing analysis output files")
    pretty_print_json: bool = Field(default=True, description="Enable JSON pretty printing in output files")
    
    # Security Settings
    enable_cors: bool = Field(default=True, description="Enable CORS for development")
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:8000", description="Allowed CORS origins")
    
    # Monitoring & Health Checks
    detailed_health_checks: bool = Field(default=True, description="Enable detailed health checks")
    health_check_timeout: int = Field(default=5, description="Health check timeout in seconds")
    
    # Testing Configuration
    test_mode: bool = Field(default=False, description="Enable test mode")
    test_firecrawl_api_key: str = Field(default="test-firecrawl-key", description="Test Firecrawl API key")
    test_proxycurl_api_key: str = Field(default="test-proxycurl-key", description="Test Proxycurl API key")


# Global settings instance
settings = Settings() 