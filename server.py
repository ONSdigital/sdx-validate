from functools import partial
from voluptuous import Schema, Required, Length, All, MultipleInvalid, Optional
from dateutil import parser
from flask import Flask, request, jsonify
import logging
from structlog import wrap_logger
import os
from uuid import UUID

from sdx.common.logger_config import logger_initial_config

__version__ = "1.10.1"

app = Flask(__name__)

logger_initial_config(service_name='sdx-validate')

logger = wrap_logger(logging.getLogger(__name__))
logger.debug("START", version=__version__)

KNOWN_SURVEYS = {
    '0.0.1': {
        '023': ['0203', '0213', '0205', '0215', '0102', '0112'],
        '134': ['0005'],
        '139': ['0001'],
        '144': ['0001'],
    },
    '0.0.2': {
        'census': ['household', 'individual', 'communal']
    }
}


# Parses a timestamp, throwing a value error
# if unrecognised
def Timestamp(value):
    return parser.parse(value)


def ValidSurveyId(value, version=None):
    if not version:
        raise AttributeError('No version number')
    if value not in KNOWN_SURVEYS[version]:
        raise ValueError('Invalid survey id')


# Parses a UUID, throwing a value error
# if unrecognised
def ValidSurveyTxId(value):
    return UUID(value, version=4)


def ValidSurveyData(data):
    if isinstance(data, dict):
        for k, v in data.items():
            if not isinstance(k, str) or not isinstance(v, (str, list, int, float)):
                raise ValueError('Invalid survey data')
    else:
        raise ValueError('Invalid survey data')


def ValidateListSurveyData(data):
    if not isinstance(data, list):
        raise ValueError('Invalid surey data')

    for x in data:
        if isinstance(x, dict):
            for k, v in x.items():
                if not isinstance(k, str) or not isinstance(v, (str, list, int, float)):
                    raise ValueError('Invalid survey data')
        else:
            raise ValueError('Invalid survey data')


@app.errorhandler(400)
def errorhandler_400(e):
    return client_error(repr(e))


def client_error(error=None):
    logger.error("Validation error", exception=error)
    message = {
        'valid': False,
        'status': 400,
        'message': error,
        'uri': request.url
    }
    resp = jsonify(message)
    resp.status_code = 400

    return resp


@app.errorhandler(500)
def server_error(e):
    logger.error("Server Error", exception=repr(e))
    message = {
        'valid': False,
        'status': 500,
        'message': "Internal server error: " + repr(e)
    }
    resp = jsonify(message)
    resp.status_code = 500

    return resp


@app.route('/validate', methods=['POST'])
def validate():
    try:
        json_data = request.get_json(force=True)

        response_type = str(json_data['type'])

        if response_type.find("feedback") == -1:
            version = json_data['version']

            schema = get_schema(version)

            if schema is None:
                return client_error("Unsupported schema version '%s'" % version)

            bound_logger = logger.bind(survey_id=json_data.get(
                'survey_id'), tx_id=json_data.get('tx_id'))

            bound_logger.debug("Validating json against schema")
            schema(json_data)

            survey_id = json_data.get('survey_id')
            if survey_id not in KNOWN_SURVEYS.get(version, {}):
                bound_logger.debug("Survey id is not known", survey_id=survey_id)
                return client_error("Unsupported survey '%s'" % survey_id)

            instrument_id = json_data.get('collection', {}).get('instrument_id')
            if instrument_id not in KNOWN_SURVEYS.get(version, {}).get(survey_id, []):
                bound_logger.debug("Instrument ID is not known", survey_id=survey_id)
                return client_error("Unsupported instrument '%s'" % instrument_id)

            metadata = json_data.get('metadata')
            bound_logger.debug("Success", user_id=metadata.get('user_id'), ru_ref=metadata.get('ru_ref'))

        else:

            schema = get_schema("feedback")

            bound_logger = logger.bind(response_type="feedback", tx_id=json_data.get('tx_id'))

            bound_logger.debug("Validating json against schema")
            schema(json_data)

            bound_logger.debug("Success")

    except (MultipleInvalid, KeyError, TypeError) as e:
        logger.error("Client error", error=e)
        return client_error(str(e))
    except Exception as e:
        logger.error("Server error", error=e)
        return server_error(e)

    return jsonify({'valid': True})


@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({'status': 'OK'})


def get_schema(version):

    if version == "0.0.1":
        valid_survey_id = partial(ValidSurveyId, version='0.0.1')

        collection_s = Schema({
            Required('period'): str,
            Required('exercise_sid'): str,
            Required('instrument_id'): All(str, Length(max=4))
        })

        metadata_s = Schema({
            Required('user_id'): str,
            Required('ru_ref'): All(str, Length(12)),
            Optional('ref_period_start_date'): Timestamp,
            Optional('ref_period_end_date'): Timestamp
        })

        schema = Schema({
            Optional('heartbeat'): bool,
            Required('type'): "uk.gov.ons.edc.eq:surveyresponse",
            Required('version'): "0.0.1",
            Optional('tx_id'): All(str, ValidSurveyTxId),
            Required('origin'): "uk.gov.ons.edc.eq",
            Required('survey_id'): All(str, valid_survey_id),
            Optional('completed'): bool,
            Optional('flushed'): bool,
            Required('submitted_at'): Timestamp,
            Required('collection'): collection_s,
            Required('metadata'): metadata_s,
            Required('data'): ValidSurveyData,
            Optional('paradata'): object
        })
        return schema

    elif version == "0.0.2":
        valid_survey_id = partial(ValidSurveyId, version='0.0.2')

        collection_s = Schema({
            Required('period'): str,
            Required('exercise_sid'): str,
            Required('instrument_id'): All(str, Length(max=10))
        })

        metadata_s = Schema({
            Required('user_id'): str,
            Required('ru_ref'): str
        })

        schema = Schema({
            Optional('heartbeat'): bool,
            Required('type'): "uk.gov.ons.edc.eq:surveyresponse",
            Required('version'): "0.0.2",
            Optional('tx_id'): All(str, ValidSurveyTxId),
            Required('origin'): "uk.gov.ons.edc.eq",
            Required('survey_id'): All(str, valid_survey_id),
            Optional('completed'): bool,
            Optional('flushed'): bool,
            Required('submitted_at'): Timestamp,
            Required('collection'): collection_s,
            Required('metadata'): metadata_s,
            Required('data'): ValidateListSurveyData,
            Optional('paradata'): object
        })
        return schema

    elif version == "feedback":

        collection_s = Schema({
            Required('period'): str,
            Required('exercise_sid'): str,
            Required('instrument_id'): All(str, Length(max=10))
        })

        schema = Schema({
            Optional('heartbeat'): bool,
            Required('type'): "uk.gov.ons.edc.eq:feedback",
            Optional('tx_id'): All(str, ValidSurveyTxId),
            Required('origin'): "uk.gov.ons.edc.eq",
            Required('survey_id'): str,
            Required('version'): str,
            Optional('completed'): bool,
            Optional('flushed'): bool,
            Required('submitted_at'): Timestamp,
            Required('collection'): collection_s,
            Required('data'): ValidSurveyData,
            Optional('metadata'): object,
            Optional('paradata'): object
        })
        return schema

    else:
        return None


if __name__ == '__main__':
    port = int(os.getenv("PORT"))
    app.run(debug=True, host='0.0.0.0', port=port)
