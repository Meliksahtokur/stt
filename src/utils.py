# src/utils.py

from datetime import datetime, timedelta
import re
from typing import Optional, Any, Dict, List

def parse_flexible_date_string(date_str):
    """
    Parses various date string formats, specifically handling "X gun once"
    relative to the CURRENT time of parsing.
    Returns a datetime object or None if parsing fails.
    """
    date_str = date_str.strip()
    if not date_str:
        return None

    # Handle "X gun once" format - IMPORTANT: this date is relative to NOW
    match = re.search(r'\((\d+)\s*gun\s*once\)', date_str)
    if match:
        days_ago = int(match.group(1))
        # The date is calculated from TODAY - (X days ago)
        return datetime.now() - timedelta(days=days_ago)
    
    # Handle standard DD.MM.YYYY format
    try:
        return datetime.strptime(date_str.split(' ')[0], '%d.%m.%Y')
    except ValueError:
        pass
    
    # Handle %Y-%m-%d format (often found in 'Gebe mi?' column)
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        pass
        
    return None # Could not parse

def safe_int(value, default=None):
    """Safely converts a value to int, returns default if conversion fails."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
