from validate import app

import unittest
import json


class TestValidateService(unittest.TestCase):

    validate_endpoint = "/validate"

    def setUp(self):

        # creates a test client
        self.app = app.test_client()

        # propagate the exceptions to the test client
        self.app.testing = True

    def test_validate_fail_sends_500(self):

        # Ask posie to decode message
        r = self.app.post(self.validate_endpoint, data='rubbish')

        self.assertEqual(r.status_code, 500)

    def test_validates_json(self):
        # Encrypt a message with the key
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

        expected_response = json.dumps({"valid": True})

        r = self.app.post(self.validate_endpoint, data=message)
        actual_response = json.dumps(json.loads(r.data.decode('UTF8')))

        self.assertEqual(actual_response, expected_response)
