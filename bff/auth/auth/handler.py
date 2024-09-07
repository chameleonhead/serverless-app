import base64
import hashlib
import hmac
import json
import logging
import os

import boto3
import botocore
import botocore.exceptions

logger = logging.Logger(name=__name__)
logging.basicConfig(handlers=[logging.StreamHandler()])


def generate_secret_hash(client_id, client_secret, username):
    digest = hmac.digest(
        client_secret.encode("utf-8"),
        (username + client_id).encode("utf-8"),
        hashlib.sha256,
    )
    return base64.b64encode(digest).decode()


def handler(event, context):
    user_pool_id = os.getenv("USER_POOL_ID")
    api_client_secret_id = os.getenv("API_CLIENT_SECRET_ID")

    cognito_idp = boto3.client("cognito-idp")
    secretsmanager = boto3.client("secretsmanager")

    secret_response = secretsmanager.get_secret_value(
        SecretId=api_client_secret_id,
    )

    secret_value = json.loads(secret_response["SecretString"])
    client_id = secret_value["client_id"]
    client_secret = secret_value["client_secret"]

    body = event["body"]
    if event["isBase64Encoded"]:
        body = base64.b64decode(body).decode("utf-8")

    body = json.loads(body)
    try:
        response = cognito_idp.admin_initiate_auth(
            UserPoolId=user_pool_id,
            ClientId=client_id,
            AuthFlow="ADMIN_USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": body["username"],
                "PASSWORD": body["password"],
                "SECRET_HASH": generate_secret_hash(
                    client_id,
                    client_secret,
                    body["username"],
                ),
            },
        )
        print(response)
        token = response["AuthenticationResult"]["RefreshToken"]
        maxage = response["AuthenticationResult"]["ExpiresIn"]
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Set-Cookie": f"session_id={token}; Max-Age={maxage}",
            },
            "body": json.dumps({"message": "hello, world."}),
        }
    except botocore.exceptions.ClientError as e:
        logger.exception(e)
        return {
            "statusCode": 403,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps({"message": "Failed to login."}),
        }
