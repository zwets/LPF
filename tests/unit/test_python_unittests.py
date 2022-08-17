from unittest import TestCase
import src.moss_functions as moss
import json

class TestValidateDateText(TestCase):
    def setUp(self):
        self.hp_date_time = '1996-06-01'
        self.sp_date_time = '01-06-1996'

    def test_hp_date_time(self):
        self.assertEqual(None, moss.validate_date_text(self.hp_date_time))

    def test_sp_date_time(self):
        self.assertRaises(ValueError, moss.validate_date_text, self.sp_date_time)


class TestValidateInput(TestCase):
    def setUp(self):
        with open('tests/resources/data_for_tests/json/assembly_test.json') as json_file:
            self.test_json = json.load(json_file)

    def test_sp_input_path(self):
        self.test_json['input_path'] = '/opt/moss_data/test_dir/file.fastq.gzsadgasd'
        self.assertRaises(SystemExit, moss.validate_input, self.test_json)

    def test_hp_all(self):
        self.assertEqual(None, moss.validate_input(self.test_json))

    def test_bad_path_collection_date(self):
        self.test_json['collection_date'] = '07/12/1984'
        with self.assertRaises(ValueError):
            moss.validate_input(self.test_json)
