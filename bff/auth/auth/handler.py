import base64
import hashlib
import hmac
import json
import logging
import os

import boto3
import botocore
import botocore.exceptions
from jose import jwt

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="{asctime} [{levelname:.4}] {name}: {message}",
    style="{",
)


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

        result = response["AuthenticationResult"]
        id_token = result["IdToken"]
        access_token = result["AccessToken"]
        refresh_token = result["RefreshToken"]
        expires_in = result["ExpiresIn"]
        claims = jwt.get_unverified_claims(id_token)
        logger.info("User %s logged in", claims["sub"])
        set_cookie = f"session_id={refresh_token}; Max-Age={expires_in}"
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Set-Cookie": set_cookie,
            },
            "body": json.dumps(
                {
                    "access_token": access_token,
                    "id_token": id_token,
                }
            ),
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
