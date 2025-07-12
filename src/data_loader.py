import logging
import os
import pandas as pd
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(filename='animal_tracker.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def load_data_from_file(file_path: str) -> List[Dict[str, Any]]:
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Load data using pandas, assuming it's a CSV file. Adapt as needed.
        df = pd.read_csv(file_path)

        # Convert the pandas DataFrame to a list of dictionaries
        data = df.to_dict(orient='records')

        logging.info(f"Data loaded successfully from {file_path}")
        return data
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise
    except pd.errors.EmptyDataError:
        logging.error(f"CSV file is empty: {file_path}")
        raise ValueError("The uploaded CSV file is empty.")
    except pd.errors.ParserError:
        logging.error(f"Error parsing CSV file: {file_path}")
        raise ValueError("Error parsing the uploaded CSV file. Please check its format.")
    except Exception as e:
        logging.exception(f"An error occurred while loading data from {file_path}: {e}")
        raise
