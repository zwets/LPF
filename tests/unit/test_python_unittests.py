from unittest import TestCase
import src.moss_functions as moss
import json
import os

class TestSqlCommands(TestCase):
    def setUp(self):
        with open('tests/resources/data_for_tests/json/assembly_test.json') as json_file:
            test_json = json.load(json_file)
        self.input_dict = moss.moss_init(test_json)
        self.input_dict['moss_db'] = 'tests/resources/data_for_tests/database/moss.db'
        moss.create_sql_db('tests/resources/data_for_tests/database/', 'datafiles/ena_list.json')

    def tearDown(self):
        os.system("rm -rf tests/resources/data_for_tests/database/moss.db")

    def test_completed_run_update_sql_database_assembly_sp(self):
        result = moss.completed_run_update_sql_database(None, self.input_dict)
        self.assertEqual(result, None)


    def test_completed_run_update_sql_database_assembly_hp(self):
        entry_id = moss.md5_of_file(self.input_dict['input_path'])
        moss.sql_execute_command(
            "INSERT INTO status_table(entry_id, sample_name, status,"
            " type, current_stage, final_stage, result, time_stamp)"
            " VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
                .format(entry_id, self.input_dict['sample_name'], "Queued", "Queued", "Queued",
                        "Queued", "Queued", ""), 'tests/resources/data_for_tests/database/moss.db')
        moss.completed_run_update_sql_database('assembly', self.input_dict)
        result = moss.sql_fetch_one("SELECT status FROM status_table WHERE entry_id = '{}'".format(entry_id), self.input_dict['moss_db'])[0]
        self.assertEqual(result, 'Completed')

    def test_completed_run_update_sql_database_alignment_hp(self):
        entry_id = moss.md5_of_file(self.input_dict['input_path'])
        moss.sql_execute_command(
            "INSERT INTO status_table(entry_id, sample_name, status,"
            " type, current_stage, final_stage, result, time_stamp)"
            " VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
                .format(entry_id, self.input_dict['sample_name'], "Queued", "Queued", "Queued",
                        "Queued", "Queued", ""), 'tests/resources/data_for_tests/database/moss.db')
        moss.completed_run_update_sql_database('alignment', self.input_dict)
        result = moss.sql_fetch_one("SELECT status FROM status_table WHERE entry_id = '{}'".format(entry_id), self.input_dict['moss_db'])[0]
        self.assertEqual(result, 'Completed')

    def test_clean_sql_for_moss_run(self):
        entry_id = moss.md5_of_file(self.input_dict['input_path'])
        moss.sql_execute_command(
            "INSERT INTO status_table(entry_id, sample_name, status,"
            " type, current_stage, final_stage, result, time_stamp)"
            " VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
                .format(entry_id, self.input_dict['sample_name'], "Queued", "Queued", "Queued",
                        "Queued", "Queued", ""), 'tests/resources/data_for_tests/database/moss.db')
        moss.sql_execute_command(moss.clean_sql_for_moss_run(self.input_dict), 'tests/resources/data_for_tests/database/moss.db')
        result = moss.sql_fetch_one("SELECT status FROM status_table WHERE entry_id = '{}'"
                      .format(entry_id), self.input_dict['moss_db'])[0]
        self.assertEqual(result, 'Run failed')

    def test_create_sql_db(self):
        self.assertTrue(os.path.exists('tests/resources/data_for_tests/database/moss.db'), 'create_sql_db did not create a database')

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
