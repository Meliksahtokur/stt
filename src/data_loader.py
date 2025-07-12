import logging
import os
import json
from typing import List, Dict, Any

# ... other imports ...

# Configure logging
logging.basicConfig(filename='animal_tracker.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def load_data_from_file(file_path: str) -> List[Dict[str, Any]]:
    try:
        # ... existing code ...
        logging.info(f"Data loaded successfully from {file_path}")
        return data
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logging.exception(f"An error occurred while loading data from {file_path}: {e}")
        raise
