import unittest
import pandas as pd
from unittest.mock import patch
from src.data_loader import load_data_from_file
import os

class TestDataLoader(unittest.TestCase):
    def test_load_data_from_file_success(self):
        # Create a sample CSV file for testing
        sample_data = {'col1': [1, 2], 'col2': [3, 4]}
        df = pd.DataFrame(sample_data)
        csv_path = 'test_data.csv'
        df.to_csv(csv_path, index=False)

        try:
            data = load_data_from_file(csv_path)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]['col1'], 1)
            self.assertEqual(data[1]['col2'], 4)
        finally:
            os.remove(csv_path)  # Clean up the test file

    @patch('src.data_loader.os.path.exists', return_value=False)
    def test_load_data_from_file_file_not_found(self, mock_exists):
        with self.assertRaises(FileNotFoundError):
            load_data_from_file('nonexistent_file.csv')

    @patch('src.data_loader.os.path.exists', return_value=True) # Mock file existence
    @patch('src.data_loader.pd.read_csv', side_effect=pd.errors.EmptyDataError("Empty CSV"))
    def test_load_data_from_file_empty_csv(self, mock_read_csv, mock_exists):
        with self.assertRaises(ValueError) as context:
            load_data_from_file('empty_file.csv')
        self.assertEqual(str(context.exception), "The uploaded CSV file is empty.")

    @patch('src.data_loader.os.path.exists', return_value=True) # Mock file existence
    @patch('src.data_loader.pd.read_csv', side_effect=pd.errors.ParserError("Parse error"))
    def test_load_data_from_file_parse_error(self, mock_read_csv, mock_exists):
        with self.assertRaises(ValueError) as context:
            load_data_from_file('bad_file.csv')
        self.assertEqual(str(context.exception), "Error parsing the uploaded CSV file. Please check its format.")

if __name__ == '__main__':
    unittest.main()
