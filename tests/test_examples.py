# ==============================================================================
# test_examples.py — Example test cases and testing utilities
# ==============================================================================
# Purpose: Provide example test cases and testing patterns for the codebase
# Sections: Imports, Test Utilities, Example Test Cases, Mock Data
# ==============================================================================

# Standard Library --------------------------------------------------------------
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

# Third Party -------------------------------------------------------------------
import asyncio
import pytest

# Core (App-wide) ---------------------------------------------------------------
from core.types.models import AnalysisOutput, RegistrationRequest
from domains.intelligence_collection import process_registration


@pytest.fixture
def replicate_registration_data() -> Dict[str, Any]:
    """Sample registration data for Replicate (small startup)."""
    return {
        "first_name": "Demo",
        "last_name": "User",
        "company_website": "https://replicate.com",
        "linkedin": None
    }


@pytest.fixture
def airtable_registration_data() -> Dict[str, Any]:
    """Sample registration data for Airtable (mid-size company)."""
    return {
        "first_name": "Demo",
        "last_name": "User", 
        "company_website": "https://airtable.com",
        "linkedin": None
    }


@pytest.fixture
def mock_replicate_discovery() -> list:
    """Mock discovered URLs for Replicate (small startup)."""
    return [
        {"url": "https://replicate.com/about", "title": "About Replicate"},
        {"url": "https://replicate.com/blog", "title": "Blog"},
        {"url": "https://replicate.com/docs", "title": "Documentation"},
        {"url": "https://replicate.com/pricing", "title": "Pricing"},
        {"url": "https://replicate.com/contact", "title": "Contact"},
        {"url": "https://replicate.com/explore", "title": "Explore Models"},
        {"url": "https://replicate.com/account", "title": "Account"}
    ]


@pytest.fixture
def mock_airtable_discovery() -> list:
    """Mock discovered URLs for Airtable (mid-size company)."""
    return [
        {"url": "https://airtable.com/product", "title": "Product"},
        {"url": "https://airtable.com/customers", "title": "Customers"},
        {"url": "https://airtable.com/about", "title": "About Airtable"},
        {"url": "https://airtable.com/pricing", "title": "Pricing"},
        {"url": "https://airtable.com/contact", "title": "Contact"},
        {"url": "https://airtable.com/developers", "title": "Developers"},
        {"url": "https://airtable.com/help", "title": "Help Center"},
        {"url": "https://airtable.com/security", "title": "Security"},
        {"url": "https://airtable.com/privacy", "title": "Privacy"},
        {"url": "https://airtable.com/terms", "title": "Terms of Service"}
    ]


@pytest.fixture
def mock_replicate_filtered() -> list:
    """Mock filtered URLs for Replicate (high-value pages)."""
    return [
        {"url": "https://replicate.com/about", "reason": "Company information and mission"},
        {"url": "https://replicate.com/blog", "reason": "Latest company updates and insights"},
        {"url": "https://replicate.com/docs", "reason": "Technical documentation and API info"}
    ]


@pytest.fixture
def mock_airtable_filtered() -> list:
    """Mock filtered URLs for Airtable (high-value pages)."""
    return [
        {"url": "https://airtable.com/product", "reason": "Core product information"},
        {"url": "https://airtable.com/customers", "reason": "Customer success stories and use cases"},
        {"url": "https://airtable.com/about", "reason": "Company background and team information"}
    ]


@pytest.fixture
def mock_replicate_content() -> Dict[str, str]:
    """Mock extracted content for Replicate pages."""
    return {
        "https://replicate.com/about": """# About Replicate

Replicate is a platform for running machine learning models in the cloud. We make it easy to deploy and scale ML models without managing infrastructure.

## Our Mission

We're building the infrastructure for AI applications. Our platform enables developers to run open-source machine learning models with a simple API call.

## What We Do

- **Model Deployment**: Deploy ML models with one line of code
- **Scalable Infrastructure**: Automatic scaling and load balancing
- **Open Source**: Support for thousands of open-source models
- **Developer Experience**: Simple API and comprehensive documentation

## Team

Founded by engineers from Google, we're passionate about making AI accessible to everyone.""",
        
        "https://replicate.com/blog": """# Replicate Blog

Latest updates, tutorials, and insights from the Replicate team.

## Recent Posts

### How to Deploy Stable Diffusion with Replicate
Learn how to deploy and run Stable Diffusion models in production...

### Scaling ML Models: Best Practices
Tips and tricks for scaling machine learning models in the cloud...

### The Future of AI Infrastructure
Our vision for the future of AI development and deployment...""",
        
        "https://replicate.com/docs": """# Replicate Documentation

Welcome to the Replicate documentation. Learn how to deploy and run machine learning models.

## Quick Start

```python
import replicate

# Run a model
output = replicate.run(
    "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
    input={"prompt": "a photo of an astronaut riding a horse on mars"}
)
```

## API Reference

### Authentication
Set your API token as an environment variable:
```bash
export REPLICATE_API_TOKEN=your_token_here
```

### Model Deployment
Deploy your own models with our platform..."""
    }


@pytest.fixture
def mock_airtable_content() -> Dict[str, str]:
    """Mock extracted content for Airtable pages."""
    return {
        "https://airtable.com/product": """# Airtable Product

Airtable is a low-code platform for building collaborative apps. Transform how teams work with flexible databases, powerful automations, and intuitive interfaces.

## Key Features

### Flexible Databases
Create custom databases that adapt to your workflow. Link records, create relationships, and organize data exactly how you need it.

### Powerful Automations
Automate repetitive tasks with our visual automation builder. Connect apps, send notifications, and streamline your processes.

### Intuitive Interfaces
Build custom interfaces for your team. Create forms, dashboards, and apps without writing code.

## Use Cases

- **Project Management**: Track projects, assign tasks, and monitor progress
- **Customer Relationship Management**: Manage leads, track interactions, and analyze data
- **Content Management**: Organize content, manage workflows, and collaborate with teams
- **Inventory Management**: Track inventory, manage orders, and monitor stock levels""",
        
        "https://airtable.com/customers": """# Customer Success Stories

See how teams around the world use Airtable to transform their work.

## Featured Customers

### Netflix
Netflix uses Airtable to manage their content production pipeline, tracking thousands of shows and movies through development, production, and release.

### Shopify
Shopify leverages Airtable for their partner program management, organizing thousands of developers and agencies in their ecosystem.

### Airbnb
Airbnb uses Airtable to coordinate their global operations, managing everything from property listings to customer support workflows.

## Success Metrics

- **10M+ users** worldwide
- **300,000+ organizations** trust Airtable
- **99.9% uptime** reliability
- **24/7 support** for enterprise customers""",
        
        "https://airtable.com/about": """# About Airtable

Airtable is a low-code platform for building collaborative apps. We're on a mission to democratize software creation by enabling anyone to build the tools they need to run their business.

## Our Story

Founded in 2012, Airtable started with a simple idea: what if databases were as easy to use as spreadsheets? Today, we're helping millions of people and organizations build custom apps without writing code.

## Our Values

### Empowerment
We believe everyone should be able to create the tools they need to do their best work.

### Collaboration
We're building a platform that brings teams together, enabling seamless collaboration across organizations.

### Innovation
We're constantly pushing the boundaries of what's possible with no-code and low-code development.

## Leadership Team

- **Howie Liu** - Co-founder and CEO
- **Andrew Ofstad** - Co-founder and CTO
- **Emmanuel Schalit** - Co-founder and CPO

## Company Stats

- **Founded**: 2012
- **Headquarters**: San Francisco, CA
- **Employees**: 1,000+
- **Funding**: Series D, $735M raised"""
    }


class TestRealCompanyExamples:
    """Integration tests with real companies for demonstration."""

    @pytest.mark.asyncio
    async def test_replicate_small_startup(
        self,
        replicate_registration_data: Dict[str, Any],
        mock_replicate_discovery: list,
        mock_replicate_filtered: list,
        mock_replicate_content: Dict[str, str]
    ):
        """Test intelligence collection for Replicate (small startup)."""
        # Arrange
        registration_data = RegistrationRequest(**replicate_registration_data)
    
        # Mock external dependencies
        with patch('domains.intelligence_collection.discover_company_urls', new_callable=AsyncMock) as mock_discover, \
             patch('domains.intelligence_collection.filter_valuable_urls', return_value=mock_replicate_filtered) as mock_filter, \
             patch('domains.intelligence_collection.extract_content', new_callable=AsyncMock) as mock_extract, \
             patch('domains.intelligence_collection.analyze_linkedin_profile', return_value=None) as mock_linkedin, \
             patch('domains.intelligence_collection.save_analysis', new_callable=AsyncMock) as mock_save:
    
            mock_discover.return_value = mock_replicate_discovery
            mock_extract.return_value = mock_replicate_content
    
            # Act
            result = await process_registration(registration_data)
    
            # Assert
            assert isinstance(result, AnalysisOutput)
            assert result.request_id is not None
            assert result.input_data == registration_data
            # LinkedIn analysis should be "not_implemented" when no LinkedIn URL provided
            assert result.linkedin_analysis == {"status": "not_implemented"}
            assert result.website_analysis is not None
    
            # Verify website analysis structure
            website_analysis = result.website_analysis
            assert "discovered_urls" in website_analysis
            assert "filtered_urls" in website_analysis
            assert "scraped_content" in website_analysis
    
            # Verify the content matches our mock data
            assert len(website_analysis["discovered_urls"]) == len(mock_replicate_discovery)
            assert len(website_analysis["filtered_urls"]) == len(mock_replicate_filtered)
            assert len(website_analysis["scraped_content"]) == len(mock_replicate_content)

    @pytest.mark.asyncio
    async def test_airtable_mid_size_company(
        self,
        airtable_registration_data: Dict[str, Any],
        mock_airtable_discovery: list,
        mock_airtable_filtered: list,
        mock_airtable_content: Dict[str, str]
    ):
        """
        Test intelligence collection for Airtable (mid-size company).
    
        Verifies that the system can discover and analyze key pages
        typically found on established company websites: Product, Customers, About.
        """
        # Arrange
        registration_data = RegistrationRequest(**airtable_registration_data)
    
        # Mock external dependencies
        with patch('domains.intelligence_collection.discover_company_urls', new_callable=AsyncMock) as mock_discover, \
             patch('domains.intelligence_collection.filter_valuable_urls', return_value=mock_airtable_filtered) as mock_filter, \
             patch('domains.intelligence_collection.extract_content', new_callable=AsyncMock) as mock_extract, \
             patch('domains.intelligence_collection.analyze_linkedin_profile', return_value=None) as mock_linkedin, \
             patch('domains.intelligence_collection.save_analysis', new_callable=AsyncMock) as mock_save:
    
            mock_discover.return_value = mock_airtable_discovery
            mock_extract.return_value = mock_airtable_content
    
            # Act
            result = await process_registration(registration_data)
    
            # Assert
            assert isinstance(result, AnalysisOutput)
            assert result.request_id is not None
            assert result.input_data == registration_data
            # LinkedIn analysis should be "not_implemented" when no LinkedIn URL provided
            assert result.linkedin_analysis == {"status": "not_implemented"}
            assert result.website_analysis is not None
    
            # Verify website analysis structure
            website_analysis = result.website_analysis
            assert "discovered_urls" in website_analysis
            assert "filtered_urls" in website_analysis
            assert "scraped_content" in website_analysis
    
            # Verify the content matches our mock data
            assert len(website_analysis["discovered_urls"]) == len(mock_airtable_discovery)
            assert len(website_analysis["filtered_urls"]) == len(mock_airtable_filtered)
            assert len(website_analysis["scraped_content"]) == len(mock_airtable_content)

    @pytest.mark.asyncio
    async def test_company_comparison_analysis(
        self,
        replicate_registration_data: Dict[str, Any],
        airtable_registration_data: Dict[str, Any],
        mock_replicate_discovery: list,
        mock_airtable_discovery: list,
        mock_replicate_filtered: list,
        mock_airtable_filtered: list,
        mock_replicate_content: Dict[str, str],
        mock_airtable_content: Dict[str, str]
    ):
        """
        Test comparison analysis between different company types.
    
        Demonstrates how the system can analyze different types of companies
        and extract relevant business intelligence for comparison.
        """
        # Arrange
        replicate_data = RegistrationRequest(**replicate_registration_data)
        airtable_data = RegistrationRequest(**airtable_registration_data)
    
        # Mock external dependencies for both companies
        with patch('domains.intelligence_collection.discover_company_urls', new_callable=AsyncMock) as mock_discover, \
             patch('domains.intelligence_collection.filter_valuable_urls') as mock_filter, \
             patch('domains.intelligence_collection.extract_content', new_callable=AsyncMock) as mock_extract, \
             patch('domains.intelligence_collection.analyze_linkedin_profile', return_value=None) as mock_linkedin, \
             patch('domains.intelligence_collection.save_analysis', new_callable=AsyncMock) as mock_save:
    
            # Configure mocks to return different data for each company
            def mock_discover_side_effect(url):
                if "replicate.com" in url:
                    return mock_replicate_discovery
                elif "airtable.com" in url:
                    return mock_airtable_discovery
                return []
    
            def mock_filter_side_effect(urls, company_context=None, max_urls=7):
                if any("replicate.com" in url["url"] for url in urls):
                    return mock_replicate_filtered
                elif any("airtable.com" in url["url"] for url in urls):
                    return mock_airtable_filtered
                return []
    
            def mock_extract_side_effect(urls):
                if any("replicate.com" in url["url"] for url in urls):
                    return mock_replicate_content
                elif any("airtable.com" in url["url"] for url in urls):
                    return mock_airtable_content
                return {}
    
            mock_discover.side_effect = mock_discover_side_effect
            mock_filter.side_effect = mock_filter_side_effect
            mock_extract.side_effect = mock_extract_side_effect
    
            # Act - Process both companies
            replicate_result = await process_registration(replicate_data)
            airtable_result = await process_registration(airtable_data)
    
            # Assert - Both should succeed
            assert isinstance(replicate_result, AnalysisOutput)
            assert isinstance(airtable_result, AnalysisOutput)
    
            # Verify different company data produces different results
            assert replicate_result.website_analysis is not None
            assert airtable_result.website_analysis is not None
    
            # Verify company-specific content
            replicate_content = replicate_result.website_analysis["scraped_content"]
            airtable_content = airtable_result.website_analysis["scraped_content"]
    
            # Should have different content for different companies
            assert "replicate.com" in str(replicate_content)
            assert "airtable.com" in str(airtable_content)
    
            # Verify LinkedIn analysis is consistent (not_implemented for both)
            assert replicate_result.linkedin_analysis == {"status": "not_implemented"}
            assert airtable_result.linkedin_analysis == {"status": "not_implemented"}

    @pytest.mark.asyncio
    async def test_real_api_integration_demo(
        self,
        replicate_registration_data: Dict[str, Any]
    ):
        """
        Demo test that can optionally run against real APIs.
    
        This test demonstrates how the system would work with real APIs.
        It can be run with real Firecrawl API calls for demonstration purposes.
        """
        # Arrange
        registration_data = RegistrationRequest(**replicate_registration_data)
    
        # Note: This test can be run with real APIs by removing the mocks
        # For demo purposes, we'll use mocks but show the structure
    
        # Mock external dependencies (remove these for real API demo)
        with patch('domains.intelligence_collection.discover_company_urls', new_callable=AsyncMock) as mock_discover, \
             patch('domains.intelligence_collection.filter_valuable_urls', return_value=[]) as mock_filter, \
             patch('domains.intelligence_collection.extract_content', new_callable=AsyncMock) as mock_extract, \
             patch('domains.intelligence_collection.analyze_linkedin_profile', return_value=None) as mock_linkedin, \
             patch('domains.intelligence_collection.save_analysis', new_callable=AsyncMock) as mock_save:
    
            mock_discover.return_value = [
                {"url": "https://replicate.com/about", "title": "About Replicate"},
                {"url": "https://replicate.com/blog", "title": "Blog"}
            ]
            mock_filter.return_value = [
                {"url": "https://replicate.com/about", "reason": "Company information"}
            ]
            mock_extract.return_value = {
                "https://replicate.com/about": "# About Replicate\n\nReplicate is a platform for running machine learning models in the cloud."
            }
    
            # Act
            result = await process_registration(registration_data)
    
            # Assert
            assert isinstance(result, AnalysisOutput)
            assert result.website_analysis is not None
    
            # Verify the analysis structure is ready for real API integration
            website_analysis = result.website_analysis
            assert "discovered_urls" in website_analysis
            assert "filtered_urls" in website_analysis
            assert "scraped_content" in website_analysis
    
            # Verify the content structure matches expected format
            assert len(website_analysis["discovered_urls"]) == 2
            assert len(website_analysis["filtered_urls"]) == 1
            assert len(website_analysis["scraped_content"]) == 1
    
            # Verify specific content
            about_content = website_analysis["scraped_content"]["https://replicate.com/about"]
            assert "Replicate is a platform" in about_content


# Helper function to create sample outputs for demonstration
async def create_sample_outputs():
    """Create sample analysis outputs in the outputs/ directory for demonstration."""
    
    # Sample Replicate analysis
    replicate_analysis = {
        "request_id": "demo-replicate-2024-01-15",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_data": {
            "first_name": "Demo",
            "last_name": "User",
            "company_website": "https://replicate.com",
            "linkedin": None
        },
        "linkedin_analysis": None,
        "website_analysis": {
            "base_url": "https://replicate.com/",
            "discovered_urls": [
                {"url": "https://replicate.com/about", "title": "About Replicate"},
                {"url": "https://replicate.com/blog", "title": "Blog"},
                {"url": "https://replicate.com/docs", "title": "Documentation"}
            ],
            "filtered_urls": [
                {"url": "https://replicate.com/about", "reason": "Company information and mission"},
                {"url": "https://replicate.com/blog", "reason": "Latest company updates and insights"},
                {"url": "https://replicate.com/docs", "reason": "Technical documentation and API info"}
            ],
            "extracted_content": {
                "https://replicate.com/about": "# About Replicate\n\nReplicate is a platform for running machine learning models in the cloud...",
                "https://replicate.com/blog": "# Replicate Blog\n\nLatest updates, tutorials, and insights from the Replicate team...",
                "https://replicate.com/docs": "# Replicate Documentation\n\nWelcome to the Replicate documentation..."
            },
            "analysis_timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
    
    # Sample Airtable analysis
    airtable_analysis = {
        "request_id": "demo-airtable-2024-01-15",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_data": {
            "first_name": "Demo",
            "last_name": "User",
            "company_website": "https://airtable.com",
            "linkedin": None
        },
        "linkedin_analysis": None,
        "website_analysis": {
            "base_url": "https://airtable.com/",
            "discovered_urls": [
                {"url": "https://airtable.com/product", "title": "Product"},
                {"url": "https://airtable.com/customers", "title": "Customers"},
                {"url": "https://airtable.com/about", "title": "About Airtable"}
            ],
            "filtered_urls": [
                {"url": "https://airtable.com/product", "reason": "Core product information"},
                {"url": "https://airtable.com/customers", "reason": "Customer success stories and use cases"},
                {"url": "https://airtable.com/about", "reason": "Company background and team information"}
            ],
            "extracted_content": {
                "https://airtable.com/product": "# Airtable Product\n\nAirtable is a low-code platform for building collaborative apps...",
                "https://airtable.com/customers": "# Customer Success Stories\n\nSee how teams around the world use Airtable...",
                "https://airtable.com/about": "# About Airtable\n\nAirtable is a low-code platform for building collaborative apps..."
            },
            "analysis_timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
    
    # Save sample outputs
    from core.utils.json_handler import save_analysis
    
    try:
        await save_analysis(replicate_analysis, "demo-replicate-2024-01-15")
        await save_analysis(airtable_analysis, "demo-airtable-2024-01-15")
        print("✅ Sample outputs created successfully")
        print("📁 Check outputs/ directory for demo files")
    except Exception as e:
        print(f"⚠️ Could not create sample outputs: {e}")


if __name__ == "__main__":
    # Create sample outputs when run directly
    asyncio.run(create_sample_outputs()) 