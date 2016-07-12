from server import app

import unittest
import json


class TestValidateService(unittest.TestCase):

    validate_endpoint = "/validate"
    message = '''{
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
       }
    }'''

    def setUp(self):

        # creates a test client
        self.app = app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    def check_invalid(self, data):

        dumped_json = json.dumps(data)

        r = self.app.post(self.validate_endpoint, data=dumped_json)
        actual_response = json.loads(r.data.decode('UTF8'))

        self.assertEqual(actual_response['valid'], False)

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

        self.check_invalid(unknown_version)

    def test_unknown_survey_invalid(self):

        unknown_survey = json.loads(self.message)
        unknown_survey['survey_id'] = "025"

        self.check_invalid(unknown_survey)

    def test_unknown_instrument_invalid(self):

        unknown_instrument = json.loads(self.message)
        unknown_instrument['collection']['instrument_id'] = "999"

        self.check_invalid(unknown_instrument)

    def test_empty_data_invalid(self):

        empty_data = json.loads(self.message)
        empty_data['data'] = ""

        self.check_invalid(empty_data)
