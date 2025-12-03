FROM python:3.7.0-alpine3.8
WORKDIR /usr/src/app

# Install build dependencies for psycopg2
RUN apk add --no-cache postgresql-libs gcc musl-dev postgresql-dev

COPY requirements.txt ./

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
CMD flask run --host=0.0.0.0
