### Unreleased
### 2.14.1 2020-03-03
 - Amend vacancies formtypes to correct ones

### 2.14.0 2020-01-30
 - Add Vacancies formtypes (182, 183, 184, 185)

### 2.13.0 2020-01-27
 - Validate submission for null characters  (`\u0000`) and fail validation if present

### 2.12.0 2019-11-25
 - Add E-commerce formtypes 0001 and 0002

### 2.11.2 2019-11-08
 - Add python 3.8 to travis builds

### 2.11.1 2019-09-26
 - Update packages, including Werkzeug that had a security vulnerability

### 2.11.0 2019-05-31
 - Added support for QSI (Stocks)
 - Remove python 3.4 and 3.5 from travis builds
 - Add python 3.7 to travis builds

### 2.10.0 2019-02-19
 - Add support for QPSES

### 2.9.0 2019-02-08
 - Added support for UKIS
 - Add support for NI version of UKIS

### 2.8.0 2018-12-12
 - Added support for E-Commerce

### 2.7.0 2018-11-13
 - Added support for D-Trades

### 2.6.0 2018-10-22
 - Added support for LMS 2.
 - Made case_ref optional for version 0.0.2 surveys

### 2.5.0 2018-09-11
 - Add support for QCAS

### 2.4.0 2018-08-15
 - Update dependency versions
 - Add support for 'started_at' field in payload

### 2.3.0 2018-06-20
 - Support LMS survey

### 2.2.0 2018-05-21
 - Support MBS surveys

### 2.1.0 2018-03-06
 - Support case_id and case_ref fields

### 2.0.0 2017-01-04
  - Remove support for heartbeat survey
  - Add /info healthcheck endpoint

### 1.12.0 2017-11-21
  - Add all service specific config to config file
  - Change to use pytest to improve test output and also changes to improve code coverage stats
  - Add Cloudfoundry deployment files
  - Remove sdx-common logging and bring it back into the repo

### 1.11.0 2017-09-25
  - Permit reference period defaults in metadata

### 1.10.1 2017-09-11
  - Update version number in app

### 1.10.0 2017-09-11
  - Processing feedback surveys

### 1.9.1
  - Ensure integrity and version of library dependencies
  - Accept floats and ints in data key

### 1.8.0 2017-07-25
  - Change all instances of ADD to COPY in Dockerfile
  - Remove use of SDX_HOME variable in makefile
  - Missing or blank survey ids now return a 400 rather than 500
  - Add support for feedback survey responses

### 1.7.0 2017-07-10
  - Update and pin version of sdx-common to 0.7.0

### 1.6.0 2017-06-19
  - Add license
  - Add codacy badge
  - Adding sdx-common functionality
  - Updating logger format using sdx-common
  - Prepare for MCI refresh
  - Add support for codecov to see unit test coverage

### 1.5.0 2017-05-04
  - Support 'flushed' flag in schema definitions. Maintain backwards compatibility with older schema versions.
  - Validate ids based on schema
  - Validate data for different survey types
  - Support 'completed' flag in schema definitions. See the [schema definitions](https://github.com/ONSdigital/ons-schema-definitions/blob/master/docs/electronic_questionnaire_to_data_exchange.rst) for more information.

## 1.4.1 2017-03-15
  - Log version number on startup

### 1.4.0 2017-02-16
  - Add change log
  - Update known instruments to correlate to specific surveys
  - Add QBS details for validation
  - Add UKIS details for validation
  - Add MWSS details for validation

### 1.3.0 2016-12-13
  - Add support for validating version 0.0.2 schemas

### 1.2.1 2016-11-28
  - Remove sensitive data from logging

### 1.2.0 2016-10-19
  - Add new `/healthcheck` endpoint

### 1.1.0 2016-09-19
  - Add configurable log level

### 1.0.1 2016-08-19
  - Fix issue with paradata element

### 1.0.0 2016-08-05
  - Initial release
