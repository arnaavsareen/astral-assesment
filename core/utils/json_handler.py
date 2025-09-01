"""Async JSON file handling utilities for analysis outputs."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import aiofiles


async def save_analysis(analysis_data: Dict[str, Any], request_id: str) -> str:
    """
    Save analysis data as JSON file to outputs directory.
    
    Args:
        analysis_data: Dictionary containing analysis results
        request_id: Unique identifier for the request
        
    Returns:
        Path to the saved JSON file
        
    Raises:
        OSError: If unable to create directory or write file
        TypeError: If analysis_data is not serializable
    """
    # 1️⃣ Create outputs directory if it doesn't exist ----
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    
    # 2️⃣ Generate filename with timestamp ----
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_{request_id}_{timestamp}.json"
    file_path = outputs_dir / filename
    
    # 3️⃣ Save JSON data asynchronously ----
    try:
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
            json_content = json.dumps(analysis_data, indent=2, default=str)
            await file.write(json_content)
    except (OSError, TypeError) as e:
        raise OSError(f"Failed to save analysis file {file_path}: {str(e)}")
    
    return str(file_path) 