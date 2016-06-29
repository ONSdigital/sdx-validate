from voluptuous import Schema, Required, Length, All, MultipleInvalid
from dateutil import parser
from flask import Flask, request, jsonify
import settings
import logging
import logging.handlers
from logging import Formatter

app = Flask(__name__)

KNOWN_SURVEYS = ['023']
KNOWN_INSTRUMENTS = ['0203', '0213', '0205', '0215', '0102', '0112']


# Parses a timestamp, throwing a value error
# if unrecognised
def Timestamp(value):
    return parser.parse(value)


def ValidSurveyId(value):
    if value not in KNOWN_SURVEYS:
        raise ValueError('Invalid survey id')


def ValidInstrumentId(value):
    if value not in KNOWN_INSTRUMENTS:
        raise ValueError('Invalid instrument id')


@app.errorhandler(500)
def unknown_error(error=None):
    app.logger.error("sdx-validate:FAILURE '%s'", request.data.decode('UTF8'))
    message = {
        'status': 500,
        'message': "Internal server error: " + repr(error),
    }
    resp = jsonify(message)
    resp.status_code = 500

    return resp


@app.route('/validate', methods=['POST'])
def validate():
    request.get_data()

    if not request.data:
        app.logger.debug("sdx-validate: FAILURE: Received no data")

    collection_s = Schema({
        Required('period'): str,
        Required('exercise_sid'): str,
        Required('instrument_id'): All(str, ValidInstrumentId)
    })

    metadata_s = Schema({
        Required('user_id'): str,
        Required('ru_ref'): All(str, Length(12))
    })

    s = Schema({
        Required('type'): "uk.gov.ons.edc.eq:surveyresponse",
        Required('version'): "0.0.1",
        Required('origin'): "uk.gov.ons.edc.eq",
        Required('survey_id'): All(str, ValidSurveyId),
        Required('submitted_at'): Timestamp,
        Required('collection'): collection_s,
        Required('metadata'): metadata_s,
        Required('data'): All({}, extra=True),
    })

    try:
        json_data = request.get_json(force=True)
        s(json_data)

    except MultipleInvalid as e:

        app.logger.debug("sdx-validate: FAILURE: '%s'" % str(e))

        return jsonify({
          'valid': False,
          'error': str(e)
        }), 400
    except Exception as e:
        return unknown_error(e)

    app.logger.debug("sdx-validate: SUCCESS")

    return jsonify({'valid': True})

if __name__ == '__main__':
    # Startup
    logging.basicConfig(level=settings.LOGGING_LEVEL, format=settings.LOGGING_FORMAT)
    handler = logging.handlers.RotatingFileHandler(settings.LOGGING_LOCATION, maxBytes=20000, backupCount=5)
    handler.setFormatter(Formatter(settings.LOGGING_FORMAT))
    app.logger.addHandler(handler)
    app.run(debug=True, host='0.0.0.0')
