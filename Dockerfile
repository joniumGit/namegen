FROM python:3.10-alpine AS worker
WORKDIR /build
RUN python -m pip install --upgrade pip && python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY ./setup.py .
COPY ./README.md .
COPY ./src ./src
RUN pip install .[runnable]

FROM python:3.10-alpine
COPY --from=worker /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /opt/namegen
COPY ./wordlist.csv .

RUN apk add --no-cache sqlite
COPY ./db.sql .
RUN sqlite3 namegen.db < db.sql

VOLUME /opt/namegen
EXPOSE 80
CMD uvicorn --port 80 --host 0.0.0.0 --workers 1 --no-access-log namegen.server:app