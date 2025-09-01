"""Pydantic models for data validation and serialization."""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator, Field


class RegistrationRequest(BaseModel):
    """Registration request model with URL validation."""
    
    first_name: str = Field(..., min_length=1, max_length=100, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="User's last name")
    company_website: Optional[HttpUrl] = Field(None, description="Company website URL")
    linkedin: Optional[HttpUrl] = Field(None, description="LinkedIn profile URL")
    
    def model_post_init(self, __context) -> None:
        """Validate that at least one URL is provided after model initialization."""
        if not self.company_website and not self.linkedin:
            raise ValueError("At least one URL (company_website or linkedin) must be provided")


class AnalysisOutput(BaseModel):
    """Analysis output model matching the JSON structure."""
    
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Analysis timestamp")
    input_data: RegistrationRequest = Field(..., description="Original registration request data")
    linkedin_analysis: Optional[dict] = Field(None, description="LinkedIn profile analysis results")
    website_analysis: Optional[dict] = Field(None, description="Company website analysis results") 