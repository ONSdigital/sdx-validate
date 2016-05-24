# sdx-validate

The sde-validate app is used within the Office National of Statistics (ONS) for validating Survey Data Exchange (SDX) Surveys.

## Installation

Using virtualenv and pip, create a new environment and install within using:

    $ pip install -r requirements.txt

It's also possible to install within a container using docker. From the sdx-validate directory:

    $ docker build -t sdx-validate .

## Usage

Start sdx-validate service using the following command:

    python validate.py

sdx-validate exposes a single endpoint '/validate' and by default binds to port 5000 on localhost.

### Example

The example below uses the Python library [requests](https://github.com/kennethreitz/requests) to validate some data using sdx-validate.

```python
import requests

r = requests.post('http://127.0.0.1:5000/validate', data={"type": "uk.gov.ons.edc.eq:surveyresponse", ...})

decrypted_data = r.text
```