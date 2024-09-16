import base64
import datetime
import hashlib
import hmac
import http.cookies
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
    path = event.get("rawPath")
    if path == "/auth/login":
        return handler_login(event, context)
    if path == "/auth/session":
        return handler_session(event, context)

    return {
        "statusCode": 404,
    }


def handler_login(event, context):
    body = event.get("body")
    if not body:
        return {"statusCode": 400}
    if event["isBase64Encoded"]:
        body = base64.b64decode(body).decode("utf-8")

    s3_bucket = os.getenv("S3_BUCKET")
    user_pool_id = os.getenv("USER_POOL_ID")
    api_client_secret_id = os.getenv("API_CLIENT_SECRET_ID")

    s3 = boto3.client("s3")
    cognito_idp = boto3.client("cognito-idp")
    secretsmanager = boto3.client("secretsmanager")

    secret_response = secretsmanager.get_secret_value(
        SecretId=api_client_secret_id,
    )

    secret_value = json.loads(secret_response["SecretString"])
    client_id = secret_value["client_id"]
    client_secret = secret_value["client_secret"]

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
        session_id = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
        logger.info(
            "User %s logged in (session id: %s)",
            claims["sub"],
            session_id,
        )
        s3.put_object(
            Bucket=s3_bucket,
            Key=f"sessions/{session_id}/tokens.json",
            Body=json.dumps(
                {
                    "id_token": id_token,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expiration": (
                        datetime.datetime.now(datetime.timezone.utc)
                        + datetime.timedelta(seconds=expires_in)
                    ).isoformat(),
                }
            ).encode("utf-8"),
        )
        set_cookie = f"session_id={session_id}"
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Set-Cookie": set_cookie,
            },
            "body": json.dumps(
                {
                    "session": {
                        "access_token": access_token,
                        "id_token": id_token,
                    },
                    "claims": claims,
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


def handler_session(event, context):
    headers = event.get("headers", {})
    cookie = headers.get("cookie")
    sc = http.cookies.SimpleCookie(cookie)
    session_id = sc.get("session_id")
    if not session_id:
        return {"statusCode": 401}

    s3_bucket = os.getenv("S3_BUCKET")
    user_pool_id = os.getenv("USER_POOL_ID")
    api_client_secret_id = os.getenv("API_CLIENT_SECRET_ID")

    s3 = boto3.client("s3")
    cognito_idp = boto3.client("cognito-idp")
    secretsmanager = boto3.client("secretsmanager")

    try:
        tokens_response = s3.get_object(
            Bucket=s3_bucket, Key=f"sessions/{session_id.value}/tokens.json"
        )
        tokens = json.loads(tokens_response["Body"].read())
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return {"statusCode": 401}
        raise Exception(e) from e

    claims = jwt.get_unverified_claims(tokens["id_token"])

    if datetime.datetime.fromisoformat(
        tokens["expiration"],
    ) > datetime.datetime.now(
        datetime.timezone.utc
    ) + datetime.timedelta(minutes=20):
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps(
                {
                    "session": {
                        "access_token": tokens["access_token"],
                        "id_token": tokens["id_token"],
                    },
                    "claims": claims,
                }
            ),
        }

    secret_response = secretsmanager.get_secret_value(
        SecretId=api_client_secret_id,
    )
    secret_value = json.loads(secret_response["SecretString"])
    client_id = secret_value["client_id"]
    client_secret = secret_value["client_secret"]

    try:
        response = cognito_idp.admin_initiate_auth(
            UserPoolId=user_pool_id,
            ClientId=client_id,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={
                "REFRESH_TOKEN": tokens["refresh_token"],
                "SECRET_HASH": generate_secret_hash(
                    client_id,
                    client_secret,
                    claims["username"],
                ),
            },
        )

        result = response["AuthenticationResult"]
        id_token = result["IdToken"]
        access_token = result["AccessToken"]
        refresh_token = result.get("RefreshToken", tokens["refresh_token"])
        expires_in = result["ExpiresIn"]
        claims = jwt.get_unverified_claims(id_token)

        s3.put_object(
            Bucket=s3_bucket,
            Key=f"sessions/{session_id}/tokens.json",
            Body=json.dumps(
                {
                    "id_token": id_token,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expiration": (
                        datetime.datetime.now(datetime.timezone.utc)
                        + datetime.timedelta(seconds=expires_in)
                    ).isoformat(),
                }
            ).encode("utf-8"),
        )
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps(
                {
                    "session": {
                        "access_token": access_token,
                        "id_token": id_token,
                    },
                    "claims": claims,
                }
            ),
        }
    except Exception as e:
        print(e)
        return {"statusCode": 401}
