"""Intelligence Collection domain - orchestrates business intelligence gathering."""

import uuid
from datetime import datetime, timezone
from typing import Optional

# Core imports
from core.types.models import RegistrationRequest, AnalysisOutput
from core.utils.json_handler import save_analysis
from core.utils.url_utils import normalize_url

# Internal domain modules
from domains.intelligence_collection.common.validators import validate_data_source
from domains.intelligence_collection.discovery.url_discoverer import discover_company_urls
from domains.intelligence_collection.filtering.url_filter import filter_valuable_urls
from domains.intelligence_collection.extraction.content_extractor import extract_content

# Service layer imports
from services.firecrawl.client import firecrawl_client
from services.linkedin.analyzer import analyze_linkedin_profile


async def process_registration(data: RegistrationRequest) -> AnalysisOutput:
    """
    Orchestrate the complete intelligence collection workflow.
    
    Workflow: Validate → Discover → Filter → Extract → Analyze → Save → Return
    
    Args:
        data: Registration request containing user data and URLs
        
    Returns:
        AnalysisOutput with structured results from all data sources
        
    Raises:
        ValueError: If data validation fails
    """
    # 1️⃣ Validate input has website or linkedin ----
    validate_data_source(data)
    
    # 2️⃣ Initialize analysis results ----
    request_id = str(uuid.uuid4())
    linkedin_analysis = {"status": "not_implemented"}
    website_analysis = None
    
    # 3️⃣ Process LinkedIn profile if provided ----
    if data.linkedin:
        linkedin_url = str(data.linkedin)
        try:
            linkedin_result = await analyze_linkedin_profile(linkedin_url)
            if linkedin_result:
                linkedin_analysis = linkedin_result
            else:
                linkedin_analysis = {"status": "failed_to_analyze"}
        except Exception as e:
            linkedin_analysis = {"status": "error", "message": str(e)}
    
    # 4️⃣ Process company website if provided ----
    if data.company_website:
        website_url = str(data.company_website)
        normalized_url = normalize_url(website_url)
        
        # Discover → Filter → Extract workflow
        discovered_urls = await discover_company_urls(normalized_url)
        
        # AI-powered intelligent filtering
        filtered_urls = await filter_valuable_urls(
            urls=discovered_urls,
            company_context={
                "company_name": f"{data.first_name} {data.last_name}'s company",
                "website": data.company_website,
                "objective": "business intelligence gathering"
            },
            max_urls=7
        )
        
        extracted_content = await extract_content(filtered_urls)
        
        website_analysis = {
            "discovered_urls": discovered_urls,
            "filtered_urls": [
                {
                    "url": u["url"], 
                    "reason": u["reason"],
                    "score": u.get("score", 0),
                    "category": u.get("category", "other")
                } for u in filtered_urls
            ],
            "scraped_content": {
                url: content for url, content in extracted_content.items()
            }
        }
    
    # 5️⃣ Create analysis output ----
    analysis_output = AnalysisOutput(
        request_id=request_id,
        timestamp=datetime.now(timezone.utc),
        input_data=data,
        linkedin_analysis=linkedin_analysis,
        website_analysis=website_analysis
    )
    
    # 6️⃣ Save analysis results ----
    try:
        await save_analysis(analysis_output.model_dump(), request_id)
    except Exception as e:
        # Log error but don't fail the entire process
        print(f"Warning: Failed to save analysis for {request_id}: {e}")
    
    return analysis_output 