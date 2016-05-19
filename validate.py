from voluptuous import Schema, Required, Length, All, MultipleInvalid
from dateutil import parser
from flask import Flask, request, jsonify
import settings
import json
import logging
import logging.handlers
from logging import Formatter

app = Flask(__name__)


# Parses a timestamp, throwing a value error
# if unrecognised
def Timestamp(value):
    return parser.parse(value)


@app.errorhandler(500)
def unknown_error(error=None):
    app.logger.error("POSIE:DECRYPT:FAILURE '%s'", request.data.decode('UTF8'))
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
        Required('period'): str
    }, extra=True)

    metadata_s = Schema({
        Required('user_id'): str,
        Required('ru_ref'): All(str, Length(12))
    })

    s = Schema({
        Required('type'): "uk.gov.ons.edc.eq:surveyresponse",
        Required('version'): "0.0.1",
        Required('origin'): "uk.gov.ons.edc.eq",
        Required('survey_id'): str,
        Required('submitted_at'): Timestamp,
        Required('collection'): collection_s,
        Required('metadata'): metadata_s,
    }, extra=True)

    try:
        data = json.loads(request.data.decode('UTF8'))
        s(data)
    except MultipleInvalid as e:
        app.logger.debug("sdx-validate: FAILURE: '%s'" % str(e))

        return jsonify({
          'valid': False,
          'error': str(e)
        })
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
