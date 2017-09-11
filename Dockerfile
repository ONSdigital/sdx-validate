FROM onsdigital/flask-crypto

COPY requirements.txt /app/requirements.txt
COPY server.py /app/server.py
COPY settings.py /app/settings.pys
COPY startup.sh /app/startup.sh

# set working directory to /app/
WORKDIR /app/

EXPOSE 5000

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -yq git gcc make build-essential python3-dev python3-reportlab
RUN pip3 install --no-cache-dir -U -r /app/requirements.txt

ENTRYPOINT ./startup.sh
