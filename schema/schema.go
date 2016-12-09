// Package schema contains the schema definitions for valid survey data
package schema

const (
	V0_0_1 = `{
    "title": "Schema version 0.0.1",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "required": [ "type", "version", "origin", "survey_id", "submitted_at", "collection", "metadata", "data" ],
    "properties": {
      "type": {
        "type": "string",
        "enum": ["uk.gov.ons.edc.eq:surveyresponse"]
      },
      "version": {
        "type": "string",
        "enum": ["0.0.1"]
      },
      "origin": {
        "type": "string",
        "enum": ["uk.gov.ons.edc.eq"]
      },
      "tx_id": {
        "type": "string",
        "pattern": "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[8|9|aA|bB][a-fA-F0-9]{3}-[a-fA-F0-9]{12}$"
      },
      "survey_id": {
        "type": "string",
        "enum": ["0","023"]
      },
      "submitted_at": {
        "type": "string",
        "format": "date-time"
      },
      "metadata": {
        "type": "object",
        "required": [ "user_id", "ru_ref" ],
        "properties": {
          "user_id": {
            "type": "string"
          },
          "ru_ref": {
            "type": "string",
            "pattern": "^.{12}$"
          }
        }
      },
      "collection": {
        "type": "object",
        "required": [ "exercise_sid", "instrument_id", "period" ],
        "properties": {
          "exercised_sid": {
            "type": "string"
          },
          "instrument_id": {
            "type": "string",
            "enum": ["hh2016", "ce2016", "0203", "0213", "0205", "0215", "0102", "0112"]
          }
        }
      },
      "data": {
        "type": "object"
      }
    }
  }`

	V0_0_2 = `{
    "title": "Schema version 0.0.2"
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "required": [ "type", "version", "origin", "survey_sid", "submitted_at", "collection", "metadata", "data" ],
    "properties": {
      "type": {
        "type": "string",
        "enum": ["uk.gov.ons.edc.eq:surveyresponse"]
      },
      "version": {
        "type": "string",
        "enum": ["0.0.2"]
      },
      "origin": {
        "type": "string",
        "enum": ["uk.gov.ons.edc.eq"]
      },
      "tx_id": {
        "type": "string",
        "pattern": "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[8|9|aA|bB][a-fA-F0-9]{3}-[a-fA-F0-9]{12}$"
      },
      "survey_id": {
        "type": "string",
        "enum": ["census]
      }
      "submitted_at": {
        "type": "string",
        "format": "date-time"
      },
      "metadata": {
        "type": "object",
        "required": [ "user_id", "ru_ref" ],
        "properties: {
          "user_id": {
            "type": "string"
          },
          "ru_ref": {
            "type": "string"
          }
        }
      },
      "collection": {
        "type": "object",
        "required": [ "exercise_id", "instrument_id", "period" ],
        "properties": {
          "exercised_sid": {
            "type": "string"
          },
          "instrument_id": {
            "type": "string",
            "enum": ["household", "individual", "communal-establishment"]
          }
        }
      },
      "data": {
        "type": "array",
        "items": {
          "type": "object"
        }
      }
    }
  }`
)
