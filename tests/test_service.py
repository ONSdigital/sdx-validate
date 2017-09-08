from server import app

import unittest
import json


class TestValidateService(unittest.TestCase):

    validate_endpoint = "/validate"
    message = {
        '0.0.1': '''{
           "tx_id": "0f534ffc-9442-414c-b39f-a756b4adc6cb",
           "type": "uk.gov.ons.edc.eq:surveyresponse",
           "origin": "uk.gov.ons.edc.eq",
           "survey_id": "023",
           "completed": true,
           "flushed": false,
           "version": "0.0.1",
           "collection": {
             "exercise_sid": "hfjdskf",
             "instrument_id": "0203",
             "period": "0216"
           },
           "submitted_at": "2016-03-12T10:39:40Z",
           "metadata": {
             "user_id": "789473423",
             "ru_ref": "12345678901A"
           },
           "data": {
             "11": "01/04/2016",
             "12": "31/10/2016",
             "20": "1800000",
             "51": 84.00,
             "52": 10,
             "53": "73",
             "54": "24",
             "50": "205",
             "22": "705000",
             "23": "900",
             "24": "74",
             "25": "50",
             "26": "100",
             "21": "60000",
             "27": "7400",
             "146": "some comment"
           },
           "paradata": {}
        }''',

        '0.0.2': '''{
           "tx_id": "0f534ffc-9442-414c-b39f-a756b4adc6cb",
           "type": "uk.gov.ons.edc.eq:surveyresponse",
           "origin": "uk.gov.ons.edc.eq",
           "survey_id": "census",
           "completed": false,
           "flushed": true,
           "version": "0.0.2",
           "collection": {
             "exercise_sid": "hfjdskf",
             "instrument_id": "household",
             "period": "0216"
           },
           "submitted_at": "2016-03-12T10:39:40Z",
           "metadata": {
             "user_id": "789473423",
             "ru_ref": "12345"
           },
           "data": [{
             "value": "Joe Bloggs",
             "block_id": "household-composition",
             "answer_id": "household-full-name",
             "group_id": "multiple-questions-group",
             "group_instance": 0,
             "answer_instance": 0
            }]
        }''',

        'feedback': '''{
               "type" : "uk.gov.ons.edc.eq:feedback",
               "origin" : "uk.gov.ons.edc.eq",
               "metadata": {
                 "user_id": "789473423",
                 "ru_ref": "432423423423"
               },
               "data": {
                 "url": "https://eq.onsdigital.uk/feedback",
                 "name": "John Appleseed",
                 "email": "john.appleseed@ons.gov.uk",
                 "message": "Feedback message string"
               },
               "submitted_at": "2016-03-07T15:28:05Z",
               "collection": {
                 "instrument_id": "0203",
                 "exercise_sid": "739",
                 "period": "2016-02-01"
               },
               "survey_id": "023",
               "tx_id": "0f534ffc-9442-414c-b39f-a756b4adc6cb",
               "version" : "0.0.1"
            }'''
    }

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def validate_response(self, data):
        dumped_json = json.dumps(data)

        r = self.app.post(self.validate_endpoint, data=dumped_json)
        actual_response = json.loads(r.data.decode('UTF8'))

        return actual_response

    def assertInvalid(self, data):
        actual_response = self.validate_response(data)

        self.assertEqual(actual_response['valid'], False)
        self.assertEqual(actual_response['status'], 400)

    def assertValid(self, data):
        actual_response = self.validate_response(data)

        self.assertEqual(actual_response['valid'], True)

    def test_validate_fail_sends_500(self):
        r = self.app.post(self.validate_endpoint, data='rubbish')

        self.assertEqual(r.status_code, 500)

    def test_validates_json(self):
        expected_response = json.dumps({"valid": True})
        for v in ['0.0.1', '0.0.2', 'feedback']:
            m = self.message[v]
            r = self.app.post(self.validate_endpoint, data=m)
            actual_response = json.dumps(json.loads(r.data.decode('UTF8')))
            self.assertEqual(actual_response, expected_response)

    def test_mwss_valid(self):
        survey = json.loads(self.message['0.0.1'])
        survey['survey_id'] = "134"
        survey['collection']['instrument_id'] = "0005"
        self.assertValid(survey)

    def test_unknown_version_invalid(self):
        unknown_version = json.loads(self.message['0.0.1'])
        unknown_version['version'] = "0.0.3"

        self.assertInvalid(unknown_version)

    def test_unknown_survey_invalid(self):
        unknown_survey = json.loads(self.message['0.0.1'])
        unknown_survey['survey_id'] = "025"

        self.assertInvalid(unknown_survey)

    def test_blank_survey_invalid(self):
        unknown_survey = json.loads(self.message['0.0.1'])
        unknown_survey['survey_id'] = ""

        self.assertInvalid(unknown_survey)

    def test_missing_survey_invalid(self):
        unknown_survey = json.loads(self.message['0.0.1'])
        del unknown_survey['survey_id']

        self.assertInvalid(unknown_survey)

    def test_unknown_census_survey_invalid(self):
        unknown_survey = json.loads(self.message['0.0.2'])
        unknown_survey['survey_id'] = "025"

        self.assertInvalid(unknown_survey)

    def test_unknown_instrument_invalid(self):
        unknown_instrument = json.loads(self.message['0.0.1'])
        unknown_instrument['collection']['instrument_id'] = "999"

        self.assertInvalid(unknown_instrument)

    def test_unknown_census_instrument_invalid(self):
        unknown_instrument = json.loads(self.message['0.0.2'])
        unknown_instrument['collection']['instrument_id'] = "999"

        self.assertInvalid(unknown_instrument)

    def test_known_instrument_wrong_survey_invalid(self):
        # RSI survey_id with Census instrument_id
        known_instrument = json.loads(self.message['0.0.1'])
        known_instrument['collection']['instrument_id'] = "household"

        self.assertInvalid(known_instrument)

    def test_known_census_instrument_wrong_survey_invalid(self):
        # RSI survey_id with Census instrument_id
        known_instrument = json.loads(self.message['0.0.2'])
        known_instrument['collection']['instrument_id'] = "0203"

        self.assertInvalid(known_instrument)

    def test_known_instrument_correct_survey_valid(self):
        # RSI survey_id with RSI instrument_id
        known_instrument = json.loads(self.message['0.0.1'])
        known_instrument['collection']['instrument_id'] = "0213"

        self.assertValid(known_instrument)

    def test_known_census_instrument_correct_survey_valid(self):
        # RSI survey_id with RSI instrument_id
        known_instrument = json.loads(self.message['0.0.2'])
        known_instrument['collection']['instrument_id'] = "household"

        self.assertValid(known_instrument)

    def test_empty_data_invalid(self):
        empty_data = json.loads(self.message['0.0.1'])
        empty_data['data'] = ""

        self.assertInvalid(empty_data)

    def test_census_empty_data_invalid(self):
        empty_data = json.loads(self.message['0.0.2'])
        empty_data['data'] = ""

        self.assertInvalid(empty_data)

    def test_feedback_empty_data_invalid(self):
        empty_data = json.loads(self.message['feedback'])
        empty_data['data'] = ""

        self.assertInvalid(empty_data)

    def test_census_dict_data_invalid(self):
        dict_data = json.loads(self.message['0.0.2'])
        dict_data['data'] = {'key1': 'value1', 'key2': 'value2'}

        self.assertInvalid(dict_data)

    def test_census_list_dict_plain_data_invalid(self):
        data = json.loads(self.message['0.0.2'])
        data['data'] = ["a", "b", "c", {"Some": "Thing"}]

        self.assertInvalid(data)

    def test_string_data_invalid(self):
        data = "abcd"

        self.assertInvalid(data)

    def test_no_data(self):
        data = None

        self.assertInvalid(data)

    def test_server_error(self):
        r = self.app.post(self.validate_endpoint, data=None)
        actual_response = json.loads(r.data.decode('UTF8'))
        self.assertEqual(actual_response['valid'], False)
        self.assertEqual(actual_response['status'], 500)

    def test_census_binary_data_error(self):
        data = json.loads(self.message['0.0.2'])
        data['data'] = b'I am text.'

        with self.assertRaises(TypeError):
            self.validate_response(data)

    def test_non_guid_tx_id_invalid(self):
        wrong_tx = json.loads(self.message['0.0.1'])
        wrong_tx['tx_id'] = "999"

        self.assertInvalid(wrong_tx)

        # Last character missing
        wrong_tx['tx_id'] = "f81d4fae-7dec-11d0-a765-00a0c91e6bf"

        self.assertInvalid(wrong_tx)

        # Wrong character at 17th position
        wrong_tx['tx_id'] = "f81d4fae-7dec-11d0-z765-00a0c91e6bf6"

        self.assertInvalid(wrong_tx)

    def test_tx_id_optional(self):
        message = json.loads(self.message['0.0.1'])
        del message['tx_id']

        self.assertValid(message)

    def test_completed_not_boolean_fails(self):
        message = json.loads(self.message['0.0.1'])
        message['completed'] = ''

        self.assertInvalid(message)

    def test_flushed_not_boolean_fails(self):
        message = json.loads(self.message['0.0.1'])
        message['flushed'] = ''

        self.assertInvalid(message)

    def test_completed_key_missing_fails(self):
        message = json.loads(self.message['0.0.1'])
        message.pop('completed')

        self.assertRaises(KeyError, message.__getitem__, 'completed')
        self.assertValid(message)

    def test_flushed_key_missing_fails(self):
        message = json.loads(self.message['0.0.1'])
        message.pop('flushed')

        self.assertRaises(KeyError, message.__getitem__, 'flushed')
        self.assertValid(message)
