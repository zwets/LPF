from unittest import TestCase
import src.moss_functions as moss
import json

#class TestMd5(TestCase):
#    def test_expected_hash(self):
#        self.assertEqual(moss.md5('test'), '098f6bcd4621d373cade4e832627b4f6')

class TestValidateInput(TestCase):
    def setUp(self):
        with open('tests/resources/input_json_file.json') as json_file:
            self.test_json = json.load(json_file)

    def test_bad_path_input_path(self):
        self.test_json['input_path'] = '/opt/moss_data/test_dir/file.fastq.gzsadgasd'
        with self.assertRaises(SystemExit) as cm:
            moss.validate_input(self.test_json)
        self.assertEqual(cm.exception.code, 'Input file is not a fastq.gz file. Only gzipped files are accepted.')

    def test_happy_path_input_path(self):
        self.assertEqual(moss.validate_input(self.test_json), True)

    def test_bad_path_collection_date(self):
        self.test_json['collection_date'] = '07/12/1984'
        with self.assertRaises(ValueError):
            moss.validate_input(self.test_json)

    def test_happy_path_collection_date(self):
        self.assertEqual(moss.validate_input(self.test_json), True)

class TestKmaFinders(TestCase):
    """
    Test KMA CGE Finders
    """
    #kma_finders("-ont -md 5", "resfinder", input_dict, "/opt/moss/resfinder_db/all")
    def setUp(self):
        with open('tests/resources/input_json_file.json') as json_file:
            self.test_json = json.load(json_file)

    def test_bad_path_input_path(self):
        self.test_json['input_path'] = '/opt/moss_data/test_dir/file.fastq.gzsadgasd' #Wrong ending
        with self.assertRaises(SystemExit) as cm:
            moss.validate_input(self.test_json)
        self.assertEqual(cm.exception.code, 'Input file is not a fastq.gz file. Only gzipped files are accepted.')

    def test_happy_path_input_path(self):
        self.assertEqual(moss.validate_input(self.test_json), True)

    def test_bad_path_collection_date(self):
        self.test_json['collection_date'] = '07/12/1984'
        with self.assertRaises(ValueError):
            moss.validate_input(self.test_json)

    def test_happy_path_collection_date(self):
        self.assertEqual(moss.validate_input(self.test_json), True)