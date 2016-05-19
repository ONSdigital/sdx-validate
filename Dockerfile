FROM onsdigital/flask-crypto

ADD validate.py /app/validate.py
ADD settings.py /app/settings.py
ADD requirements.txt /app/requirements.txt

RUN mkdir -p /app/logs

# set working directory to /app/
WORKDIR /app/

EXPOSE 5000

RUN pip3 install --no-cache-dir -U -I -r /app/requirements.txt

ENTRYPOINT python3 validate.py