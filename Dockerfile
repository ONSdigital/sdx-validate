FROM python:3.8-slim

RUN apt update && apt install -y build-essential curl gunicorn

WORKDIR /app

ENV PORT=5000
EXPOSE 5000

COPY . /app
RUN pip3 install --no-cache-dir -U -r /app/requirements.txt

CMD ["gunicorn", "server:app"]
