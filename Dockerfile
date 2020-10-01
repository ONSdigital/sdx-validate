FROM python:3.8-slim

RUN apt update && apt install -y build-essential curl gunicorn

WORKDIR /app

EXPOSE 5000

COPY . /app
RUN pip3 install --no-cache-dir -U -r /app/requirements.txt

CMD ["gunicorn", "-b", "0.0.0.0:5000", "--workers", "8", "--worker-class", "gevent", "--worker-connections" ,"1000", "--timeout", "30", "--keep-alive", "2", "app:server"]
