#! /bin/sh
cd "${0%/*}/"
docker build -f Dockerfile -t namegen:latest .
docker run --rm -it -p '127.0.0.1:5604:80' namegen:latest