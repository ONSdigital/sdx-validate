from server import app

import unittest
import json


class TestValidateService(unittest.TestCase):

    validate_endpoint = "/validate"
    message = '''{
       "tx_id": "0f534ffc-9442-414c-b39f-a756b4adc6cb",
       "type": "uk.gov.ons.edc.eq:surveyresponse",
       "origin": "uk.gov.ons.edc.eq",
       "survey_id": "023",
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
         "51": "84",
         "52": "10",
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
    }'''

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

    def assertValid(self, data):
        actual_response = self.validate_response(data)

        self.assertEqual(actual_response['valid'], True)

    def test_validate_fail_sends_500(self):
        r = self.app.post(self.validate_endpoint, data='rubbish')

        self.assertEqual(r.status_code, 500)

    def test_validates_json(self):
        expected_response = json.dumps({"valid": True})

        r = self.app.post(self.validate_endpoint, data=self.message)
        actual_response = json.dumps(json.loads(r.data.decode('UTF8')))

        self.assertEqual(actual_response, expected_response)

    def test_unknown_version_invalid(self):
        unknown_version = json.loads(self.message)
        unknown_version['version'] = "0.0.2"

        self.assertInvalid(unknown_version)

    def test_unknown_survey_invalid(self):
        unknown_survey = json.loads(self.message)
        unknown_survey['survey_id'] = "025"

        self.assertInvalid(unknown_survey)

    def test_unknown_instrument_invalid(self):
        unknown_instrument = json.loads(self.message)
        unknown_instrument['collection']['instrument_id'] = "999"

        self.assertInvalid(unknown_instrument)

    def test_empty_data_invalid(self):
        empty_data = json.loads(self.message)
        empty_data['data'] = ""

        self.assertInvalid(empty_data)

    def test_non_guid_tx_id_invalid(self):
        wrong_tx = json.loads(self.message)
        wrong_tx['tx_id'] = "999"

        self.assertInvalid(wrong_tx)

        # Last character missing
        wrong_tx['tx_id'] = "f81d4fae-7dec-11d0-a765-00a0c91e6bf"

        self.assertInvalid(wrong_tx)

        # Wrong character at 17th position
        wrong_tx['tx_id'] = "f81d4fae-7dec-11d0-z765-00a0c91e6bf6"

        self.assertInvalid(wrong_tx)

    def test_tx_id_optional(self):
        message = json.loads(self.message)
        del message['tx_id']

        self.assertValid(message)
