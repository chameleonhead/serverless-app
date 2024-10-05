import os

import boto3
import psycopg2


def handler(event, context):
    aws_region = os.getenv("AWS_REGION")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_POST", "5432")
    db_user = os.getenv("DB_USER", "contacts_api")
    db_name = os.getenv("DB_NAME", "apidb")

    rds = boto3.client("rds")

    token = rds.generate_db_auth_token(
        DBHostname=db_host,
        Port=db_port,
        DBUsername=db_user,
        Region=aws_region,
    )

    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            apidb=db_user,
            password=token,
            sslrootcert="SSLCERTIFICATE",
        )
        cur = conn.cursor()
        cur.execute("""SELECT now()""")
        query_results = cur.fetchall()
        print(query_results)
    except Exception as e:
        print("Database connection failed due to {}".format(e))
