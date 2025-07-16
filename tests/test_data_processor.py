import unittest
from datetime import datetime
from src.data_processor import process_animal_records, classify_animal, get_display_name

class TestDataProcessor(unittest.TestCase):

    def test_classify_animal_inek(self):
        # Two inseminations more than 180 days apart
        dates = [datetime(2022, 1, 1), datetime(2022, 8, 1)]
        self.assertEqual(classify_animal(dates), "İnek")

    def test_classify_animal_duve_single_insem(self):
        # Single insemination
        dates = [datetime(2023, 5, 10)]
        self.assertEqual(classify_animal(dates), "Düve")

    def test_classify_animal_duve_no_insem(self):
        # No inseminations
        dates = []
        self.assertEqual(classify_animal(dates), "Bilinmiyor") # Current logic returns Bilinmiyor for empty list

    def test_classify_animal_duve_close_insem(self):
        # Multiple inseminations but all within 180 days
        dates = [datetime(2023, 1, 1), datetime(2023, 2, 1), datetime(2023, 3, 1)]
        self.assertEqual(classify_animal(dates), "Düve")

    def test_get_display_name(self):
        self.assertEqual(get_display_name({"isletme_kupesi": "A123"}), "A123")
        self.assertEqual(get_display_name({"devlet_kupesi": "D456"}), "D456")
        self.assertEqual(get_display_name({"tasma_no": "T789"}), "T789")
        self.assertEqual(get_display_name({"isletme_kupesi": "A123", "devlet_kupesi": "D456"}), "A123")
        self.assertEqual(get_display_name({}), "Bilinmeyen Hayvan")

    def test_process_animal_records_date_conversion(self):
        mock_raw_animals = [
            {
                "uuid": "1",
                "isletme_kupesi": "A001",
                "dogum_tarihi": "2020-01-01T00:00:00",
                "tohumlamalar": [
                    {"tohumlama_tarihi": "2021-01-01T00:00:00"},
                    {"tohumlama_tarihi": "2022-08-01T00:00:00"}
                ]
            },
            {
                "uuid": "2",
                "isletme_kupesi": "A002",
                "dogum_tarihi": "invalid-date",
                "tohumlamalar": []
            }
        ]
        
        processed_animals = process_animal_records(mock_raw_animals)
        
        # Test animal 1
        self.assertIsInstance(processed_animals[0]['dogum_tarihi'], datetime)
        self.assertEqual(processed_animals[0]['dogum_tarihi'].year, 2020)
        self.assertEqual(processed_animals[0]['sinif'], 'İnek')
        self.assertIsInstance(processed_animals[0]['son_tohumlama'], datetime)
        self.assertEqual(processed_animals[0]['son_tohumlama'].year, 2022)
        
        # Test animal 2
        self.assertIsNone(processed_animals[1]['dogum_tarihi']) # Invalid date should be None
        self.assertEqual(processed_animals[1]['sinif'], 'Bilinmiyor')
        self.assertIsNone(processed_animals[1]['son_tohumlama'])

    def test_process_animal_records_empty_list(self):
        self.assertEqual(process_animal_records([]), [])

if __name__ == '__main__':
    unittest.main()
import unittest
from datetime import datetime
from src.data_processor import process_animal_records, classify_animal, get_display_name

class TestDataProcessor(unittest.TestCase):

    def test_classify_animal_inek(self):
        # Two inseminations more than 180 days apart
        dates = [datetime(2022, 1, 1), datetime(2022, 8, 1)]
        self.assertEqual(classify_animal(dates), "İnek")

    def test_classify_animal_duve_single_insem(self):
        # Single insemination
        dates = [datetime(2023, 5, 10)]
        self.assertEqual(classify_animal(dates), "Düve")

    def test_classify_animal_duve_no_insem(self):
        # No inseminations
        dates = []
        self.assertEqual(classify_animal(dates), "Bilinmiyor") # Current logic returns Bilinmiyor for empty list

    def test_classify_animal_duve_close_insem(self):
        # Multiple inseminations but all within 180 days
        dates = [datetime(2023, 1, 1), datetime(2023, 2, 1), datetime(2023, 3, 1)]
        self.assertEqual(classify_animal(dates), "Düve")

    def test_get_display_name(self):
        self.assertEqual(get_display_name({"isletme_kupesi": "A123"}), "A123")
        self.assertEqual(get_display_name({"devlet_kupesi": "D456"}), "D456")
        self.assertEqual(get_display_name({"tasma_no": "T789"}), "T789")
        self.assertEqual(get_display_name({"isletme_kupesi": "A123", "devlet_kupesi": "D456"}), "A123")
        self.assertEqual(get_display_name({}), "Bilinmeyen Hayvan")

    def test_process_animal_records_date_conversion(self):
        mock_raw_animals = [
            {
                "uuid": "1",
                "isletme_kupesi": "A001",
                "dogum_tarihi": "2020-01-01T00:00:00",
                "tohumlamalar": [
                    {"tohumlama_tarihi": "2021-01-01T00:00:00"},
                    {"tohumlama_tarihi": "2022-08-01T00:00:00"}
                ]
            },
            {
                "uuid": "2",
                "isletme_kupesi": "A002",
                "dogum_tarihi": "invalid-date",
                "tohumlamalar": []
            }
        ]
        
        processed_animals = process_animal_records(mock_raw_animals)
        
        # Test animal 1
        self.assertIsInstance(processed_animals[0]['dogum_tarihi'], datetime)
        self.assertEqual(processed_animals[0]['dogum_tarihi'].year, 2020)
        self.assertEqual(processed_animals[0]['sinif'], 'İnek')
        self.assertIsInstance(processed_animals[0]['son_tohumlama'], datetime)
        self.assertEqual(processed_animals[0]['son_tohumlama'].year, 2022)
        
        # Test animal 2
        self.assertIsNone(processed_animals[1]['dogum_tarihi']) # Invalid date should be None
        self.assertEqual(processed_animals[1]['sinif'], 'Bilinmiyor')
        self.assertIsNone(processed_animals[1]['son_tohumlama'])

    def test_process_animal_records_empty_list(self):
        self.assertEqual(process_animal_records([]), [])

if __name__ == '__main__':
    unittest.main()
