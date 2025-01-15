# docker build -t brian/sz_init_postgresql-v4 .
# docker run --user $UID -it -e SENZING_ENGINE_CONFIGURATION_JSON brian/sz_init_postgresql-v4

ARG BASE_IMAGE=senzing/senzingsdk-runtime:latest
FROM ${BASE_IMAGE}

LABEL Name="brian/sz_init_postgresql-v4" \
  Maintainer="brianmacy@gmail.com" \
  Version="DEV"

USER root

RUN apt-get update \
  && apt-get -y install senzingsdk-setup python3-uritools python3-psycopg2 \
  && apt-get -y autoremove \
  && apt-get -y clean

COPY ./init-postgresql.py /app/

ENV LD_LIBRARY_PATH=/opt/senzing/er/lib
ENV PYTHONPATH=/opt/senzing/er/sdk/python

USER 1001

WORKDIR /app
ENTRYPOINT ["/app/init-postgresql.py"]
