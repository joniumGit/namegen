FROM python:3.9-alpine
RUN apk add sqlite
WORKDIR /opt/namegen

COPY ./setup.py .
COPY ./README.md .
COPY ./src ./src
COPY ./wordlist.txt .
RUN pip install .[dev]

COPY ./db.sql .
RUN sqlite3 namegen.db < ./db.sql

COPY ./test ./test
CMD pytest --cov=namegen --cov-report=html --cov-report=term && echo 'Tests Done'