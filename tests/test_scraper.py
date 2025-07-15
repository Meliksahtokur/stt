import unittest
from unittest.mock import patch, MagicMock
from src.scraper import fetch_and_parse_table, ScraperError
import requests
from bs4 import BeautifulSoup

class TestScraper(unittest.TestCase):

    def setUp(self):
        self.mock_url = "http://example.com"
        self.sample_html = """
        <table>
            <thead>
                <tr>
                    <th>Header1</th>
                    <th>Header2</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Data1A</td>
                    <td>Data1B</td>
                </tr>
                <tr>
                    <td>Data2A</td>
                    <td>Data2B</td>
                </tr>
            </tbody>
        </table>
        """
        self.expected_data = [
            {'Header1': 'Data1A', 'Header2': 'Data1B'},
            {'Header1': 'Data2A', 'Header2': 'Data2B'}
        ]

    @patch('src.scraper.requests.get')
    def test_fetch_and_parse_table_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = self.sample_html.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_and_parse_table(self.mock_url)
        self.assertEqual(result, self.expected_data)
        mock_get.assert_called_once_with(self.mock_url, timeout=15)
        mock_response.raise_for_status.assert_called_once()

    @patch('src.scraper.requests.get', side_effect=requests.exceptions.Timeout)
    def test_fetch_and_parse_table_timeout(self, mock_get):
        with self.assertRaisesRegex(ScraperError, "Web sitesine bağlanırken zaman aşımı yaşandı"):
            fetch_and_parse_table(self.mock_url)

    @patch('src.scraper.requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    def test_fetch_and_parse_table_request_error(self, mock_get):
        with self.assertRaisesRegex(ScraperError, "Web sitesine bağlanırken bir ağ hatası oluştu"):
            fetch_and_parse_table(self.mock_url)

    @patch('src.scraper.requests.get')
    def test_fetch_and_parse_table_no_table_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = "<html><body><p>No table here</p></body></html>".encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with self.assertRaisesRegex(ScraperError, "HTML içeriğinde beklenen '<table>' etiketi bulunamadı."):
            fetch_and_parse_table(self.mock_url)

    @patch('src.scraper.requests.get')
    def test_fetch_and_parse_table_empty_row_cells(self, mock_get):
        html_with_empty_row = """
        <table>
            <thead>
                <tr>
                    <th>Header1</th>
                    <th>Header2</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>Data1A</td><td>Data1B</td></tr>
                <tr></tr> <!-- This row will be skipped due to empty cells -->
                <tr><td>Data2A</td><td>Data2B</td></tr>
            </tbody>
        </table>
        """
        mock_response = MagicMock()
        mock_response.content = html_with_empty_row.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_and_parse_table(self.mock_url)
        self.assertEqual(result, self.expected_data)

    @patch('src.scraper.requests.get')
    def test_fetch_and_parse_table_missing_cells(self, mock_get):
        html_missing_cells = """
        <table>
            <thead>
                <tr>
                    <th>Header1</th>
                    <th>Header2</th>
                    <th>Header3</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Data1A</td>
                    <td>Data1B</td>
                </tr>
            </tbody>
        </table>
        """
        mock_response = MagicMock()
        mock_response.content = html_missing_cells.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_and_parse_table(self.mock_url)
        self.assertEqual(result, [{'Header1': 'Data1A', 'Header2': 'Data1B', 'Header3': ''}])
