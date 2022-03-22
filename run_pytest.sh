#! /bin/sh
cd "${0%/*}/"
docker build -f test.Dockerfile -t namegen-test:latest .
docker run --rm -it -v "$(pwd)/htmlcov/:/opt/namegen/htmlcov/" namegen-test:latest