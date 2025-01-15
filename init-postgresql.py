#! /usr/bin/env python3

import argparse
import json
import os
import sys

import uritools

import psycopg2

import senzing_core


def add_default_config(factory):
    config_mgr = factory.create_configmanager()

    if config_mgr.get_default_config_id():
        print("It appears a configuration is already installed. Skipping.")
        return

    er_config = factory.create_config()
    default_er_config = er_config.export_config(er_config.create_config())

    config_mgr.set_default_config_id(
        config_mgr.add_config(default_er_config, "Initial configuration.")
    )


def get_postgresql_url(engine_config):
    # BEMIMP currently doesn't support database clustering
    config = json.loads(engine_config)
    senzing_database_url = config["SQL"]["CONNECTION"]

    parsed = uritools.urisplit(senzing_database_url)
    if "schema" in parsed.getquerydict():
        # BEMIMP
        print("Non-default schema not currently supported.")
        sys.exit(-1)

    if not parsed.port and len(parsed.path) <= 1:
        # print("URI with DBi, reparsing modified URI")
        # historically, postgresql URIs allow the DB to be after after a colon
        # or part of the path
        # actual PostgreSQL URIs aren't standard either though the python interface
        # attempts to normalize it so we convert here
        values = parsed.host.split(":")
        host = values[0]
        port = None
        path = None
        if len(values) > 2:
            port = values[1]
            path = "/" + values[2]
        else:
            path = "/" + values[1]

        mod_uri = uritools.uricompose(
            scheme=parsed.scheme,
            userinfo=parsed.userinfo,
            host=host,
            path=path,
            port=port,
            query=parsed.query,
            fragment=parsed.fragment,
        )
        return mod_uri

    return senzing_database_url


def schema_creation(engine_config):
    url = get_postgresql_url(engine_config)
    print(f"Connecting with {url}")
    conn = psycopg2.connect(url)
    conn.autocommit = True
    cur = conn.cursor()

    config = json.loads(engine_config)
    schema_creation_file = os.path.join(
        config["PIPELINE"]["RESOURCEPATH"],
        "schema",
        "szcore-schema-postgresql-create.sql",
    )

    try:
        cur.execute(
            "select var_value from sys_vars where var_group = 'VERSION' and var_code = 'SCHEMA'"
        )
        row = cur.fetchall()
        if not row:
            print("Database appears to contain a partial schema.  Contact support.")
            sys.exit(-1)
        if len(row) == 1 and row[0][0] != "4.0":
            print(
                f"Database appears to contain an old schema [{row[0][0]}].  Refer to Senzing documentation for upgrade instructions."
            )
            sys.exit(-1)

        print(
            "It appears that the Senzing 4.0 schema already exists in the database.  Skipping creation."
        )
        return
    except Exception:
        pass

    with open(schema_creation_file, "r", encoding="utf-8") as input_file:
        for line in input_file:
            line_string = line.strip()
            if line_string:
                cur.execute(line_string)

    cur.close()
    conn.close()


parser = argparse.ArgumentParser()
parser.add_argument(
    "-t",
    "--debugTrace",
    dest="debugTrace",
    action="store_true",
    default=False,
    help="output debug trace information",
)
parser.add_argument(
    "-x",
    "--skipEnginePrime",
    dest="skipEnginePrime",
    action="store_true",
    default=False,
    help="skip the engine prime_engine to speed up execution"
)
args = parser.parse_args()

engine_config = os.getenv("SENZING_ENGINE_CONFIGURATION_JSON")
if not engine_config:
    print(
        "The environment variable SENZING_ENGINE_CONFIGURATION_JSON must be set with a proper JSON configuration.",
        file=sys.stderr,
    )
    print(
        "Please see https://senzing.zendesk.com/hc/en-us/articles/360038774134-G2Module-Configuration-and-the-Senzing-API",
        file=sys.stderr,
    )
    sys.exit(-1)

# Initialize the G2Engine
factory = senzing_core.SzAbstractFactory(
    "sz_init_postgresql", engine_config, verbose_logging=args.debugTrace
)

schema_creation(engine_config)
add_default_config(factory)

try:
    engine = factory.create_engine()
    if not args.skipEnginePrime:
        engine.prime_engine()
    print(factory.create_product().get_version())
    print("Successful Senzing initialization test.")
except Exception as ex:
    print("FAILED Senzing initialization test.")
    print(ex)
    sys.exit(-1)
