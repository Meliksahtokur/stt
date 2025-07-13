import unittest
from datetime import datetime, date
from unittest.mock import patch, MagicMock
from src.statistics import (
    calculate_statistics,
    calculate_breed_distribution,
    generate_pie_chart_base64,
    calculate_births_per_month,
    generate_bar_chart_base64,
    get_animal_specific_stats
)
import base64 # To check if output is valid base64

class TestStatistics(unittest.TestCase):

    def setUp(self):
        self.mock_animals = [
            {'uuid': '1', 'isletme_kupesi': 'A001', 'devlet_kupesi': 'D001', 'tasma_no': 'T001', 'irk': 'Holstein', 'sinif': 'İnek',
             'dogum_tarihi': datetime(2020, 1, 1), 'tohumlamalar': [{'tohumlama_tarihi': datetime(2022, 5, 1)}]},
            {'uuid': '2', 'isletme_kupesi': 'A002', 'devlet_kupesi': 'D002', 'tasma_no': 'T002', 'irk': 'Jersey', 'sinif': 'Düve',
             'dogum_tarihi': datetime(2023, 3, 15), 'tohumlamalar': []},
            {'uuid': '3', 'isletme_kupesi': 'A003', 'devlet_kupesi': 'D003', 'tasma_no': 'T003', 'irk': 'Holstein', 'sinif': 'İnek',
             'dogum_tarihi': datetime(2021, 7, 20), 'tohumlamalar': [{'tohumlama_tarihi': datetime(2023, 1, 1)}, {'tohumlama_tarihi': datetime(2022, 1, 1)}]},
            {'uuid': '4', 'isletme_kupesi': 'A004', 'devlet_kupesi': 'D004', 'tasma_no': 'T004', 'irk': 'Angus', 'sinif': 'Düve',
             'dogum_tarihi': datetime(2024, 2, 10), 'tohumlamalar': [{'tohumlama_tarihi': datetime(2024, 5, 15)}]},
        ]

    def test_calculate_statistics_empty_list(self):
        self.assertEqual(calculate_statistics([]), {})

    @patch('src.statistics.date')
    def test_calculate_statistics(self, mock_date):
        mock_date.today.return_value = date(2024, 7, 13) # Fix current date for consistent age calculation

        stats = calculate_statistics(self.mock_animals)
        self.assertAlmostEqual(stats["toplam_hayvan_sayisi"], 4)
        self.assertAlmostEqual(stats["inek_sayisi"], 2)
        self.assertAlmostEqual(stats["duve_sayisi"], 2)
        self.assertAlmostEqual(stats["ortalama_tohumlama_sayisi"], (1 + 0 + 2 + 1) / 4) # (total inseminations / total animals)
        
        # Age calculation:
        # Animal 1: 2024-07-13 - 2020-01-01 = 1656 days
        # Animal 2: 2024-07-13 - 2023-03-15 = 486 days
        # Animal 3: 2024-07-13 - 2021-07-20 = 1089 days
        # Animal 4: 2024-07-13 - 2024-02-10 = 154 days
        # Total days: 1656 + 486 + 1089 + 154 = 3385
        # Average days: 3385 / 4 = 846.25
        # Average years: 846.25 / 365.25 = ~2.316 years
        self.assertAlmostEqual(stats["ortalama_yas_gun"], 846.25, places=2)
        self.assertAlmostEqual(stats["ortalama_yas_yil"], 2.3, places=1)


    def test_calculate_breed_distribution(self):
        breed_dist = calculate_breed_distribution(self.mock_animals)
        self.assertEqual(breed_dist, {'Holstein': 2, 'Jersey': 1, 'Angus': 1})

    def test_generate_pie_chart_base64_valid_data(self):
        data = {'BreedA': 10, 'BreedB': 5}
        chart_base64 = generate_pie_chart_base64(data, "Test Pie Chart")
        self.assertIsNotNone(chart_base64)
        self.assertIsInstance(chart_base64, str)
        # Check if it's a valid base64 string
        self.assertGreater(len(chart_base64), 0)
        try:
            base64.b64decode(chart_base64)
        except Exception:
            self.fail("Generated string is not valid base64")

    def test_generate_pie_chart_base64_empty_data(self):
        chart_base64 = generate_pie_chart_base64({}, "Empty Chart")
        self.assertIsNone(chart_base64) # Should return None as per implementation

    def test_calculate_births_per_month(self):
        births = calculate_births_per_month(self.mock_animals)
        self.assertEqual(births, {'2020-01': 1, '2021-07': 1, '2023-03': 1, '2024-02': 1})

    def test_generate_bar_chart_base64_valid_data(self):
        data = {'2023-01': 2, '2023-02': 5}
        chart_base64 = generate_bar_chart_base64(data, "Test Bar Chart", "Month", "Count")
        self.assertIsNotNone(chart_base64)
        self.assertIsInstance(chart_base64, str)
        self.assertGreater(len(chart_base64), 0)
        try:
            base64.b64decode(chart_base64)
        except Exception:
            self.fail("Generated string is not valid base64")

    def test_generate_bar_chart_base64_empty_data(self):
        chart_base64 = generate_bar_chart_base64({}, "Empty Bar Chart", "X", "Y")
        self.assertIsNone(chart_base64) # Should return None as per implementation

    def test_get_animal_specific_stats_found(self):
        stats = get_animal_specific_stats('1', self.mock_animals)
        self.assertEqual(stats['toplam_tohumlama_sayisi'], 1)
        self.assertEqual(stats['sinif_tahmini'], 'İnek')
        self.assertIsInstance(stats['son_tohumlama'], datetime)
        self.assertEqual(stats['dogum_tarihi'], '2020-01-01')

    def test_get_animal_specific_stats_not_found(self):
        stats = get_animal_specific_stats('999', self.mock_animals)
        self.assertEqual(stats, {"hata": "Hayvan bulunamadı."})

if __name__ == '__main__':
    unittest.main()
