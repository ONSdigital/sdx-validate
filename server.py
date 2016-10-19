from voluptuous import Schema, Required, Length, All, MultipleInvalid, Optional
from dateutil import parser
from flask import Flask, request, jsonify
import settings
import logging
from structlog import wrap_logger
import os
from uuid import UUID

app = Flask(__name__)

logging.basicConfig(level=settings.LOGGING_LEVEL, format=settings.LOGGING_FORMAT)
logger = wrap_logger(logging.getLogger(__name__))
logger.debug("START")

KNOWN_SURVEYS = ['0', '023']
KNOWN_INSTRUMENTS = ['hh2016', 'ce2016', '0203', '0213', '0205', '0215', '0102', '0112']


# Parses a timestamp, throwing a value error
# if unrecognised
def Timestamp(value):
    return parser.parse(value)


def ValidSurveyId(value):
    if value not in KNOWN_SURVEYS:
        raise ValueError('Invalid survey id')


# Parses a UUID, throwing a value error
# if unrecognised
def ValidSurveyTxId(value):
    return UUID(value, version=4)


def ValidInstrumentId(value):
    if value not in KNOWN_INSTRUMENTS:
        raise ValueError('Invalid instrument id')


def ValidSurveyData(data):
    if isinstance(data, dict):
        for k, v in data.items():
            if not isinstance(k, str) or not (isinstance(v, str) or isinstance(v, list)):
                raise ValueError('Invalid survey data')
    else:
        raise ValueError('Invalid survey data')


@app.errorhandler(400)
def errorhandler_400(e):
    return client_error(repr(e))


def client_error(error=None):
    logger.error(error, request=request.data.decode('UTF8'))
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
    logger.error("Server Error", exception=repr(e), request=request.data.decode('UTF8'))
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
    request.get_data()

    if not request.data:
        return client_error("Request payload was empty")

    collection_s = Schema({
        Required('period'): str,
        Required('exercise_sid'): str,
        Required('instrument_id'): All(str, ValidInstrumentId)
    })

    metadata_s = Schema({
        Required('user_id'): str,
        Required('ru_ref'): All(str, Length(12))
    })

    schema = Schema({
        Optional('heartbeat'): bool,
        Required('type'): "uk.gov.ons.edc.eq:surveyresponse",
        Required('version'): "0.0.1",
        Optional('tx_id'): All(str, ValidSurveyTxId),
        Required('origin'): "uk.gov.ons.edc.eq",
        Required('survey_id'): All(str, ValidSurveyId),
        Required('submitted_at'): Timestamp,
        Required('collection'): collection_s,
        Required('metadata'): metadata_s,
        Required('data'): ValidSurveyData,
        Optional('paradata'): object
    })

    try:
        json_data = request.get_json(force=True)

        tx_id = None
        if 'tx_id' in json_data:
            tx_id = json_data['tx_id']

        bound_logger = logger.bind(tx_id=tx_id)
        bound_logger.debug("Validating json against schema")
        schema(json_data)

    except MultipleInvalid as e:
        return client_error(str(e))

    except Exception as e:
        return server_error(e)

    metadata = json_data['metadata']
    bound_logger.debug("Success", user_id=metadata['user_id'], ru_ref=metadata['ru_ref'])

    return jsonify({'valid': True})


@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({'status': 'OK'})


if __name__ == '__main__':
    port = int(os.getenv("PORT"))
    app.run(debug=True, host='0.0.0.0', port=port)
